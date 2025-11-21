##
# dynamodb.py
# ----------------------------------
# Module for DynamoDB interactions.
#
##
import boto3
from boto3.dynamodb.conditions import Key, Attr

import chalicelib.config as config


_dynamodb = boto3.resource('dynamodb', region_name=config.REGION)
sessions_table = _dynamodb.Table(config.DYNAMODB_TABLE_NAME)


__all__ = [
    "sessions_table",
]
