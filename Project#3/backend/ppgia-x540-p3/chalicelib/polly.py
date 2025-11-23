## 
# polly.py
# -----------------------------
# Module to the AWS TTS service.
#
## 
import boto3

import chalicelib.config as config


_polly = boto3.client('polly', region_name=config.REGION)

class PollyException(Exception):
    """
    Custom exception class to manage the possible errors while using Polly.
    """
    def __init__(self, message: str):
        super().__init__(f"Error on Polly TTS service: {message}")


def synthetize(
    text: str, 
    language: str = config.LANGUAGE, 
    output_format: str = "ogg_vorbis", 
    use_ssml: bool = False) -> bytes:
    """
    Synthetize the text using the given Polly voice in pt-BR.
    """
    #TODO: Add check of text size (max 3000 chars for standard voices, 6000 for neural)
    try:
        synth = _polly.synthesize_speech(
            Engine=config.POLLY_ENGINE,
            LanguageCode=language,
            VoiceId=config.POLLY_VOICE_ID,
            OutputFormat=output_format,
            Text=text,
            TextType=('ssml' if use_ssml else "text")
        )
    except Exception as e:
        raise PollyException(str(e))

    stream = synth.get('AudioStream')
    if stream is None:
        raise PollyException("No audio stream returned.")

    audio = stream.read()
    return audio

__all__ = [
    "synthetize",
    "PollyException",
]
