from . import config

# google-cloud-texttospeech minimum version 2.29.0 is required.
from google.cloud import texttospeech


PROJECT_ID = config["GOOGLE_CLOUD_PROJECT"]


class GoogleSpeech:
    """
    Google Speech Synthesizer class.
    """
    known_voices = [
        'Achernar',
        'Charon',
    ]

    def __init__(self, model: str = 'gemini-2.5-pro-tts', 
                 voice_name: str = 'Charon', 
                 language_code: str = 'en-US'):
        self._client = texttospeech.TextToSpeechClient()

        # Select the voice you want to use.
        self._voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            model_name=model
        )


    def synthesize(self, prompt: str, text: str, 
                   output_filepath: str = "output.mp3"):
        """Synthesizes speech from the input text and saves it to an MP3 file.

        Args:
            prompt: Styling instructions on how to synthesize the content in
            the text field.
            text: The text to synthesize.
            output_filepath: The path to save the generated audio file.
            Defaults to "output.mp3".
        """
        synthesis_input = texttospeech.SynthesisInput(text=text, prompt=prompt)

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type.
        response = self._client.synthesize_speech(
            input=synthesis_input, voice=self._voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        with open(output_filepath, "wb") as out:
            out.write(response.audio_content)
            print(f"Audio content written to file: {output_filepath}")