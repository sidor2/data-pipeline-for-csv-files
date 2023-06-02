import boto3
import os
import io
import folium
import pandas as pd

CSV_BUCKET = os.environ.get('CSV_BUCKET')
MAPS_BUCKET = os.environ.get('MAPS_BUCKET')
RECORDS_TABLE = os.environ.get('RECORDS_TABLE')

def lambda_handler(event, context):
    
    try:
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                
                filename = record['dynamodb']['NewImage']['filename']['S']
                print(f"Processing file {filename}")
        
        X = 'X'
        Y  = 'Y'

        try:
            # Read the CSV file containing the coordinates
            s3 = boto3.client("s3")
            obj = s3.get_object(Bucket=CSV_BUCKET, Key=filename)
            body = obj['Body'].read()
            df = pd.read_csv(io.BytesIO(body))


            # Create a map centered on the first coordinate in the CSV file
            m = folium.Map(location=[df[X][0], df[Y][0]], zoom_start=6, tiles="Stamen Terrain")

            # Add a line connecting the markers in the CSV file
            route = folium.PolyLine(locations=df[[Y, X]].values.tolist(), color='red')
            route.add_to(m)
            bounds = route.get_bounds()
            m.fit_bounds(bounds)

        except Exception as e:
            print("Error reading the CSV files.")
            print(e)
            raise

        try:
            # Save the map as an HTML file
            map_filename = filename.replace("_PQR.csv", "_Map.html")
            map_holder = f"/tmp/{map_filename}"
            m.save(map_holder)
            print(f"Generated the map {map_holder}.")
            
        except Exception as e:
            print("Error saving the map file")
            print(e)
            raise

        try:
            # s3.put_object(Bucket=MAPS_BUCKET, Key=f"{map_filename}", body=m)
            s3.upload_file(map_holder, MAPS_BUCKET, map_filename)
            print("Uploaded the map to destionation S3 bucket.")

        except Exception as e:
            print("Error uploading the map to S3 bucket.")
            print(e)
            raise

        try:
            # Update the record in the DynamoDB table
            # existing_attributes = record['dynamodb']['NewImage']
            
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(RECORDS_TABLE)

            # Create an update expression to add a new attribute to the record
            update_expression = 'SET #new_attr_name = :new_attr_value'
            expression_attribute_names = {'#new_attr_name': 'map'}
            expression_attribute_values = {':new_attr_value': map_filename}
            
            
            # Update the record in DynamoDB
            response = table.update_item(
                Key={'filename': filename},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values
            )

            # Log the response from the update operation
            print(f"Updated record {filename}: {response}")

        except Exception as e:
            print("Could not update the test record.")
            print(e)
            raise
            

    except Exception as e:
        print(e)
        raise

    return 0