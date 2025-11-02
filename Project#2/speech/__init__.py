import os

from dotenv import load_dotenv
load_dotenv()

config = {
    "AZURE_SPEECH_KEY": os.getenv("AZURE_SPEECH_KEY"),
    "AZURE_SPEECH_ENDPOINT": os.getenv("AZURE_SPEECH_ENDPOINT"),
    "GOOGLE_SPEECH_KEY": os.getenv("GOOGLE_SPEECH_KEY"),
    "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT"),
}

from ._azure import AzureSpeech
from ._google import GoogleSpeech
from ._aws import AWSSpeech

__all__ = [
    "AzureSpeech",
    "GoogleSpeech",
    "AWSSpeech",
]