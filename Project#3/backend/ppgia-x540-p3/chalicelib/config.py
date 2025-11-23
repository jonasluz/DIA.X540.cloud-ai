##
# Chalice config file for ppgia-x540-p3 project.
#
##
import os


# Chalice app configuration
APP_NAME = 'ppgia-x540-p3'

# AWS region (default: us-east-1)
REGION = os.environ.get("AWS_REGION", "us-east-1")

# Environment variables for Bedrock Agent configuration
AGENT_ID = os.environ.get("BEDROCK_AGENT_ID")
AGENT_ALIAS_ID = os.environ.get("BEDROCK_AGENT_ALIAS_ID")

# DynamoDB table name for session management
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME")

# Polly voice
POLLY_VOICE_ID = os.environ.get("POLLY_VOICE_ID", "Camila")
POLLY_ENGINE = os.environ.get("POLLY_ENGINE", "neural")
LANGUAGE = os.environ.get("LANGUAGE", "pt-BR")

# S3 bucket to store generated audio files
S3_AUDIO_BUCKET = os.environ.get("S3_AUDIO_BUCKET")


# Validate required configurations
# Early check for required env.vars to avoid runtime errors.
if not AGENT_ID or not AGENT_ALIAS_ID:
    raise RuntimeError(
        "The env.vars to make BedRock Agent calls are not set."
    )
elif not DYNAMODB_TABLE_NAME:
    raise RuntimeError(
        "The env.var DYNAMODB_TABLE_NAME is not set."
    )
elif not S3_AUDIO_BUCKET:
    raise RuntimeError(
        "The env.var S3_AUDIO_BUCKET is not set."
    )


__all__ = [
    "APP_NAME",
    "REGION",
    "AGENT_ID",
    "AGENT_ALIAS_ID",
    "DYNAMODB_TABLE_NAME",
    "POLLY_VOICE_ID",
    "POLLY_ENGINE",
    "LANGUAGE",
    "S3_AUDIO_BUCKET"
]