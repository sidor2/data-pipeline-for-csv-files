import json
import os
import re
import boto3

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TRUCKS_TABLE_NAME')

def lambda_handler(event, context):
    try:
        payload = json.loads(event['body'])
        print(f'Received payload: {payload}')

        # Get the DynamoDB table and put the item in the table
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item=payload)

        # Return a success response
        response = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Record saved successfully'})
        }

    except Exception as e:
        # Return an error response
        response = {
            'statusCode': 400,
            'body': json.dumps(event)
        }
        raise e

    return response
