import boto3
import requests
import json

import variables as vr

from authenticate import authenticate_user

# def authenticate_user(username, password, user_pool_id, app_client_id):
#     client = boto3.client('cognito-idp')

#     response = client.initiate_auth(
#         ClientId=app_client_id,
#         AuthFlow='USER_PASSWORD_AUTH',
#         AuthParameters={
#             'USERNAME': username,
#             'PASSWORD': password
#         }
#     )

#     return response['AuthenticationResult']['IdToken']

def make_api_request(url, token, payload):
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

# User credentials
username = vr.username
password = vr.password

# Cognito user pool and app client details
user_pool_id = vr.user_pool_id
app_client_id = vr.user_pool_client_id

# API Gateway endpoint
api_url = f"{vr.api_url}/addtruck"

# Item payload
item_payload = {
    "originalVin": "E94820",
    "currentVin": "E94822",
    "par": "42Q",
    "engine": "DD15",
    "ats": "GATS2.0",
    "cab": "Sleeper",
    "chassis": "OTR",
    "axleRatio": "2.7",
    "powerRating": "400/1850",
    "fuelmap": "15.1.1.0",
    "transmission": "DT320",
    "fanClutchCooler": "Oil",
    "fanModel": "B52",
    "fanClutch": "U642",
    "trailerNumber": "T14"
}

# Authenticate user and get the JWT token
token = authenticate_user(username, password, user_pool_id=user_pool_id, app_client_id=app_client_id)

# Make the API request
response = make_api_request(api_url, token, item_payload)

# Print the response
print(response)
