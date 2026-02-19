import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("MERCHANT_TABLE", "Merchant")
table = dynamodb.Table(TABLE_NAME)

def _resp(msg: str):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": msg
    }

def lambda_handler(event, context):
    # 1) Parse JSON body
    try:
        body = event.get("body")
        if body is None:
            payload = {}
        elif isinstance(body, str):
            payload = json.loads(body)
        elif isinstance(body, dict):
            payload = body
        else:
            payload = {}
    except Exception:
        payload = {}

    merchant_name = payload.get("merchant_name")
    merchant_token = payload.get("merchant_token")

    if not merchant_name or not merchant_token:
        return _resp("Merchant Not Authorized.")

    # 2) DynamoDB lookup by Name (partition key)
    try:
        result = table.get_item(Key={"Name": merchant_name})
        item = result.get("Item")
        if not item:
            return _resp("Merchant Not Authorized.")

        expected_token = item.get("Token")
        if expected_token == merchant_token:
            return _resp("Merchant Authorized.")
        return _resp("Merchant Not Authorized.")

    except Exception:
        # permission errors, wrong region, wrong table name, etc.
        return _resp("Merchant Not Authorized.")
