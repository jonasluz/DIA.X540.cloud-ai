"""
Speech module for various cloud providers.
@author: Jonas de Araújo Luz Jr.
@date: 2025-11-02
"""
import os

# Load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

# Configuration for cloud speech services
config = {
    "AZURE_SPEECH_KEY": os.getenv("AZURE_SPEECH_KEY"),
    "AZURE_SPEECH_ENDPOINT": os.getenv("AZURE_SPEECH_ENDPOINT"),
    "GOOGLE_SPEECH_KEY": os.getenv("GOOGLE_SPEECH_KEY"),
    "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT"),
}

def play_audio(filepath: str):
    """Play audio file using the default system player."""
    import sys
    import subprocess

    if sys.platform == "win32":
        os.startfile(filepath)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filepath])


# Import speech synthesizer classes
from ._azure import AzureSpeech
from ._google import GoogleSpeech
from ._aws import AWSSpeech

# Define the public API of the speech module
__all__ = [
    "play_audio",
    "AzureSpeech",
    "GoogleSpeech",
    "AWSSpeech",
]