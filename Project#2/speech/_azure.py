from . import config

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

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"Speech synthesized for text [{text}]")

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"Speech synthesis canceled: {cancellation_details.reason}")

                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    if cancellation_details.error_details:
                        print(f"Error details: {cancellation_details.error_details}")
                        print("Did you set the speech resource key and endpoint values?")
            
            return result
        
        except Exception as e:
            print(f"Error occurred: {e}")    