##
# transcribe.py
# ----------------------------------
# Utility functions for AWS Transcribe operations.
##
import json

import boto3

import chalicelib.config as config
from chalicelib.s3 import read_s3_file


transcribe = boto3.client('transcribe')

def start_transcription_job(s3_audio_file: str, 
                            job_name: str,
                            media_format: str = "wav", 
                            language_code: str = config.LANGUAGE) -> str:
    """
    Start a transcription job for the given audio file.
    """
    try:
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_audio_file},
            MediaFormat=media_format,
            LanguageCode=language_code,
            OutputBucketName=config.S3_AUDIO_BUCKET,
            OutputKey=f"transcripts/{job_name}.json"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to start transcription job: {str(e)}")

    return response['TranscriptionJob']['TranscriptionJobName']


def get_transcription_result(job_name: str) -> tuple[str, str]:
    """
    Retrieve the transcription result text for a completed job.
    """
    try:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        status = result['TranscriptionJob']['TranscriptionJobStatus']
        match status:
            case 'FAILED':
                raise RuntimeError("Transcription job failed.")
            case 'COMPLETED':
                transcript_uri = f"s3://{config.S3_AUDIO_BUCKET}/transcripts/{job_name}.json"
                print(f"Transcript URI: {transcript_uri}")
                transcript_json = json.loads(read_s3_file(transcript_uri, text=True))

                response = transcript_json['results']['transcripts'][0]['transcript']
                return (status, response)
            case _:
                return (status, "")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve transcription result: {str(e)}") from e


__all__ = [
    'start_transcription_job', 
    'get_transcription_result'
]