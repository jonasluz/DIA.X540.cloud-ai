##
# transcribe.py
# ----------------------------------
# Utility functions for AWS Transcribe operations.
##
import json
from urllib import request

import boto3

import chalicelib.config as config


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
        raise RuntimeError(f"Failed to start transcription job: {str(e)}") from e

    return response['TranscriptionJob']['TranscriptionJobId']


def get_transcription_result(job_id: str) -> tuple[str, str]:
    """
    Retrieve the transcription result text for a completed job.
    """
    try:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_id)
        status = result['TranscriptionJob']['TranscriptionJobStatus']
        match status:
            case 'FAILED':
                raise RuntimeError("Transcription job failed.")
            case 'COMPLETED':
                transcript = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
                with request.urlopen(transcript) as f:
                    transcript_json = json.loads(f.read().decode('utf-8'))
                response = transcript_json['results']['transcripts'][0]['transcript']
                return (status, response)
            case _:
                return (status, "")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve transcription result: {str(e)}") from e


__all__ = [
    'start_transcription_job', 
    'get_transcription_job_status', 
    'get_transcription_result'
]