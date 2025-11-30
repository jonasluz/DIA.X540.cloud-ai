##
# dynamodb.py
# ----------------------------------
# Module for DynamoDB interactions.
#
##
import time
import uuid

import boto3
from boto3.dynamodb.conditions import Key, Attr

import chalicelib.config as config


_dynamodb = boto3.resource('dynamodb', region_name=config.REGION)
sessions_table = _dynamodb.Table(config.DYNAMODB_TABLE_NAME)

def create_session(user_id: str) -> tuple[str, int]:
    """
    Create a new session entry in the DynamoDB table.
    Returns the session ID and timestamp.
    """
    session_id = str(uuid.uuid4())
    timestamp = int(time.time())

    sessions_table.put_item(
        Item={
            'conversation_id': session_id,
            'user_id': user_id,
            'created_at': timestamp,
            'status': 'active',
        }
    )

    return session_id, timestamp

def close_session(session_id: str) -> int:
    """
    Close an existing session by updating its status in the DynamoDB table.
    Returns the timestamp of closure.
    """
    timestamp = int(time.time())

    sessions_table.update_item(
        Key={'conversation_id': session_id},
        UpdateExpression="SET #s = :s, closed_at = :c",
        ExpressionAttributeNames={
            '#s': 'status',
        },
        ExpressionAttributeValues={
            ':s': 'closed',
            ':c': timestamp,
        }
    )

    return timestamp


__all__ = [
    "create_session",
    "close_session",
]
