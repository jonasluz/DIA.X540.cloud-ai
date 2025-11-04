from . import config, play_audio

import azure.cognitiveservices.speech as speechsdk


class AzureSpeech:
    """
    Azure Speech Synthesizer class.
    """
    # List of known voices
    known_voices = [
        'en-US-Ava:DragonHDLatestNeural',
        'pt-BR-FranciscaNeural'
    ]

    def __init__(self, voice_name: str = 'pt-BR-FranciscaNeural'):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=config["AZURE_SPEECH_KEY"], 
            endpoint=config["AZURE_SPEECH_ENDPOINT"])

        self.audio_config = speechsdk.audio.AudioOutputConfig(
            use_default_speaker=True)

        # The neural multilingual voice can speak different languages based on the input text.
        self.speech_config.speech_synthesis_voice_name = voice_name

        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=self.audio_config)


    def speak(self, text: str):
        """
        Synthesize speech from text.
        """
        try:
            result = self.speech_synthesizer.speak_text_async(text).get()

            if not result:
                print("No result returned from synthesizer")
                return None

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"Speech synthesized for text [{text}]")

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = getattr(result, 'cancellation_details', None)
                reason = getattr(cancellation_details, 'reason', 'Unknown') if cancellation_details else 'Unknown'
                print(f"Speech synthesis canceled: {reason}")

                if (
                    cancellation_details is not None and
                    reason == speechsdk.CancellationReason.Error and
                    getattr(cancellation_details, 'error_details', None)
                ):
                    print(f"Error details: {cancellation_details.error_details}")
                    print("Did you set the speech resource key and endpoint values?")
            
            return result
        
        except Exception as e:
            print(f"Error occurred: {e}")    


    def synthesize(self, text: str,
                          output_filepath: str = "output.mp3",
                          play: bool = False) -> bool | str:
        """Synthesize speech to an MP3 file.

        Args:
            text: The text to synthesize.
            output_filepath: Destination path for the MP3 file.
            play: If True, plays the generated audio after saving.

        Returns:
            False on success, or an error string on failure (aligns with AWS provider pattern).
        """
        try:
            # Ensure MP3 output format
            self.speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
            )

            # Use a file-based audio output for this synthesis
            file_audio_config = speechsdk.audio.AudioOutputConfig(
                filename=output_filepath
            )

            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=file_audio_config
            )

            result = synthesizer.speak_text_async(text).get()
            if not result:
                return "No result returned from synthesizer"

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                if play:
                    play_audio(output_filepath)
                return False

            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = getattr(result, 'cancellation_details', None)
                reason = getattr(cancellation_details, 'reason', 'Unknown') if cancellation_details else 'Unknown'
                msg = f"Speech synthesis canceled: {reason}"
                if (
                    cancellation_details is not None and
                    reason == speechsdk.CancellationReason.Error and
                    getattr(cancellation_details, 'error_details', None)
                ):
                    msg += f" | Error details: {cancellation_details.error_details}"
                return msg

            # Fallback unexpected branch
            return f"Unexpected synthesis result: {result.reason}"

        except Exception as e:
            return str(e)