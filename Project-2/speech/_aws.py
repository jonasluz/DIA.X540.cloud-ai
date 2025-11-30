from . import config, play_audio

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError

from contextlib import closing

class AWSSpeech:
    """
    AWS Speech Synthesis
    """
    def __init__(self, aws_profile: str = 'default', 
                 voice_name: str = "Camila"):
        # Create a client using the credentials and region defined in the [default]
        # section of the AWS credentials file (~/.aws/credentials).
        session = Session(profile_name=aws_profile)
        self._polly = session.client("polly")
        self._voice_name = voice_name


    def synthesize(self, text: str, 
                          output_filepath: str = "output.mp3", 
                          play: bool = False) -> bool | str:
        try:
            # Request speech synthesis
            response = self._polly.synthesize_speech(
                Text=text, OutputFormat="mp3",
                VoiceId=self._voice_name
            )
            audio_stream = response.get("AudioStream", None)
            if audio_stream is None:
                return "Could not stream audio"

            # Note: Closing the stream is important because the service throttles on the
            # number of parallel connections. Here we are using contextlib.closing to
            # ensure the close method of the stream object will be called automatically
            # at the end of the with statement's scope.
            with closing(audio_stream) as stream:
                try:
                    # Open a file for writing the output as a binary stream
                    with open(output_filepath, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    # Could not write to file
                    return str(error)

            # Play the audio using the platform's default player
            if play:
                play_audio(output_filepath)
        
        except (BotoCoreError, ClientError) as error:
            # The service returned an error
            return str(error)

        return False