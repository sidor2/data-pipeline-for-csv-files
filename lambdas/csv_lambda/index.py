from datetime import datetime
import json
import urllib.parse
import re
import os
import boto3


def lambda_handler(event, context):
    # Get the bucket and key from the S3 event notification
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    # Validate the filename for potential XSS attack
    xss_pattern = re.compile('[<>\"\'&]')
    if xss_pattern.search(key):
        print(f"Invalid filename: {key}")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid filename')
        }

    # Validate the filename for alphanumeric characters
    alphanumeric_pattern = re.compile('^[a-zA-Z0-9_\-\.]+$')
    if not alphanumeric_pattern.match(key):
        print(f"Invalid filename: {key}")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid filename')
        }

    # Extract the VIN and date from the filename
    vin = key[0:6]
    date = key[7:17] 

    # Validate the VIN
    vin_pattern = re.compile('^E9\d{4}$')
    if not vin_pattern.match(vin):
        print(f"Invalid VIN: {vin}")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid VIN')
        }

    # Validate the date
    date_pattern = re.compile('^\d{4}_\d{2}_\d{2}$')
    if not date_pattern.match(date):
        print(f"Invalid date: {date}")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid date')
        }
    
    date_obj = datetime.strptime(date, '%Y_%m_%d').date()
    mf4_filename = key.replace('_PQR.csv', '.MF4')

    # Log the extracted VIN and date
    print(f"Extracted VIN: {vin}")
    print(f"Extracted date: {date_obj}")
    print(f"Data file name: {mf4_filename}")
    print(f"CSV file name: {key}")

    TRUCKS_TABLE_NAME = os.environ.get('TRUCKS_TABLE_NAME')
    RECORDS_TABLE_NAME = os.environ.get('RECORDS_TABLE_NAME')

    dynamodb = boto3.resource('dynamodb')

    # Retrieve the table
    trucks_table = dynamodb.Table(TRUCKS_TABLE_NAME)
    records_table = dynamodb.Table(RECORDS_TABLE_NAME)

    try:
        # Retrieve the item from the table
        truck_key = {'currentVin': vin}
        response = trucks_table.get_item(Key=truck_key)
        truck_item = response.get('Item')

        if not truck_item:
            print(f"No record for {vin} in the {trucks_table.table_name}, creating.")

            trucks_table.put_item(
                Item={
                    "currentVin": vin
                }
            )
        
        # check if record exists
        record_key = {'filename': key}
        record = records_table.get_item(Key=record_key)
        record = record.get('Item')

        if not record:
            # creat test record
            print(f"No record found for filename: {key}, creating.")

            test_data = {
                "date": date_obj.isoformat(),
                "filename": key,
                "data_filename": mf4_filename
            }

            if not truck_item:
                truck_item = {
                    "currentVin": vin
                }
            
            record_item = {**truck_item, **test_data}

            records_table.put_item(
                Item=record_item
            )

        else:
            print(f"Record found for filename: {key}, skipping.")

    except Exception as e:
        print(e)
        raise e
