import boto3

def authenticate_user(username, password, user_pool_id=None, app_client_id=None):
    client = boto3.client('cognito-idp')

    response = client.initiate_auth(
        ClientId=app_client_id,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    )

    return response['AuthenticationResult']['IdToken']