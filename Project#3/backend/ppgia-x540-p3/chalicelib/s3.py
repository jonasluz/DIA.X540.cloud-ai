##
# s3.py @ Project#3/backend/ppgia-x540-p3/chalicelib
# ----------------------------------
# S3 utility functions for audio file storage.
##
import boto3
from botocore.exceptions import ClientError

import chalicelib.config as config


# S3 client for audio storage (requires IAM: s3:PutObject, s3:GetObject on bucket ARN)
s3_client = boto3.client('s3', region_name=config.REGION)

def upload_audio_file(file_name: str, data: bytes, content_type: str, 
                      expires_in: int = 300) -> str:
    """Upload an audio file to S3 and return a presigned HTTPS URL.

    Parameters
    ----------
    file_name : str
        Key to store in S3 (e.g., 'sessions/<session_id>/<uuid>.ogg').
    data : bytes
        Binary audio data.
    content_type : str
        MIME type (e.g., 'audio/ogg', 'audio/mpeg').
    expires_in : int, default 300
        Expiration time in seconds for the presigned URL.

    Returns
    -------
    str
        Presigned URL to download the uploaded object via HTTP.
    """
    try:
        s3_client.put_object(
            Bucket=config.S3_AUDIO_BUCKET,
            Key=file_name,
            Body=data,
            ContentType=content_type
        )
    except ClientError as e:
        raise RuntimeError(
            f"Failed to upload audio file to S3: {e.response['Error'].get('Message', str(e))}") from e
    except Exception as e:
        raise RuntimeError(
            f"Failed to upload audio file to S3: {str(e)}") from e

    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.S3_AUDIO_BUCKET, 'Key': file_name},
            ExpiresIn=expires_in
        )
    except ClientError as e:
        raise RuntimeError(
            f"Failed to generate presigned URL: {e.response['Error'].get('Message', str(e))}") from e
    except Exception as e:
        raise RuntimeError(
            f"Failed to generate presigned URL: {str(e)}") from e

    return presigned_url