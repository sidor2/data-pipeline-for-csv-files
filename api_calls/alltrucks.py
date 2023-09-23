import boto3
import requests

import variables as vr

from authenticate  import authenticate_user

def make_api_request(url, token):
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    return response.json()

# User credentials
username = vr.username
password = vr.password

# Cognito user pool and app client details
user_pool_id = vr.user_pool_id
app_client_id = vr.user_pool_client_id

# API Gateway endpoint
api_url = f"{vr.api_url}/alltrucks"

# Authenticate user and get the JWT token
token = authenticate_user(username, password, user_pool_id=user_pool_id, app_client_id=app_client_id)

# Make the API request
response = make_api_request(api_url, token)

# Print the response
print(response)
