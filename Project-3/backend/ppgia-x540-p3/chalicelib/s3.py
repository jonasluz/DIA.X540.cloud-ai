##
# s3.py @ Project#3/backend/ppgia-x540-p3/chalicelib
# ----------------------------------
# S3 utility functions for audio file storage.
# Author: Jonas de Araújo Luz Jr.
# Last Update: 2025-11-27
##
import boto3
from botocore.exceptions import ClientError

import chalicelib.config as config


# S3 client for audio storage (requires IAM: s3:PutObject, s3:GetObject on bucket ARN)
_s3_client = boto3.client('s3', region_name=config.REGION)


def create_presigned_upload_url(
    object_name: str,
    content_type: str,
    expiration: int = 300) -> str:
    """
    Generate a presigned URL to share an S3 object (PUT).
    """
    try:
        response = _s3_client.generate_presigned_url(
            'put_object', 
            Params={
                'Bucket': config.S3_AUDIO_BUCKET,
                'Key': object_name,
                'ContentType': content_type
            },
            ExpiresIn=expiration)
    
    except ClientError as e:
        raise RuntimeError(
            f"Failed to generate presigned upload URL: {e.response['Error'].get('Message', str(e))}") \
            from e
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to generate presigned upload URL: {str(e)}") from e
    
    return response


def upload_audio_file(file_name: str, data: bytes, content_type: str, 
                      expires_in: int = 300, presign: bool = True) -> str:
    """
    Upload an audio file to S3 and return a presigned HTTPS URL if required.
    """
    try:
        _s3_client.put_object(
            Bucket=config.S3_AUDIO_BUCKET,
            Key=file_name,
            Body=data,
            ContentType=content_type
        )

    except ClientError as e:
        raise RuntimeError(
            f"Failed to upload audio file to S3: {e.response['Error'].get('Message', str(e))}") \
            from e
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to upload audio file to S3: {str(e)}") from e

    if not presign:
        return f"s3://{config.S3_AUDIO_BUCKET}/{file_name}"
    
    try:
        presigned_url = _s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': config.S3_AUDIO_BUCKET, 
                'Key': file_name
            },
            ExpiresIn=expires_in
        )
    
    except ClientError as e:
        raise RuntimeError(
            f"Failed to generate presigned URL: {e.response['Error'].get('Message', str(e))}") from e
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to generate presigned URL: {str(e)}") from e

    return presigned_url



def read_s3_file(s3_uri: str, text: bool = False) -> bytes | str:
    """
    Read a file from S3 given its S3 URI (s3://bucket/key).
    """
    try:
        parts = s3_uri.replace("s3://", "").split("/", 1)
        bucket, key = parts[0], parts[1]
        
        response = _s3_client.get_object(Bucket=bucket, Key=key)
        body = response['Body'].read()
        
        # Treat the response as text if text=True
        return body.decode('utf-8') if text else body
    
    except ClientError as e:
        raise RuntimeError(
            f"Failed to read file from S3: {e.response['Error'].get('Message', str(e))}") from e
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to read file from S3: {str(e)}") from e


__all__ = [
    'create_presigned_upload_url',
    'upload_audio_file',
    'read_s3_file'
]