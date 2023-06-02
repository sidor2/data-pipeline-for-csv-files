import boto3
import variables as vr

from authenticate  import authenticate_user


# Set up AWS region
region = vr.region

# Step 1: Authenticate into the user pool with username and password
username = vr.username
password = vr.password
user_pool_id = vr.user_pool_id
user_pool_client_id = vr.user_pool_client_id
identity_pool_id = vr.identity_pool_id
bucket_name = vr.bucket_name
object_key = vr.object_key

cognito_client = boto3.client('cognito-idp', region_name=region)

try:
    jwt_token = authenticate_user(username, password, user_pool_id=user_pool_id, app_client_id=user_pool_client_id)
    # response = cognito_client.initiate_auth(
    #     ClientId=user_pool_client_id,
    #     AuthFlow='USER_PASSWORD_AUTH',
    #     AuthParameters={
    #         'USERNAME': username,
    #         'PASSWORD': password
    #     }
    # )
    # jwt_token = response['AuthenticationResult']['IdToken']

except cognito_client.exceptions.NotAuthorizedException as e:
    print('Failed to authenticate:', e.response['Error']['Message'])
    quit()

# Step 2: Exchange the JWT token for credentials from the identity pool
identity_client = boto3.client('cognito-identity', region_name=region)
try:
    response = identity_client.get_id(
        IdentityPoolId=identity_pool_id,
        Logins={
            f'cognito-idp.us-east-1.amazonaws.com/{user_pool_id}': jwt_token
        }
    )
    identity_id = response['IdentityId']
    print('Identity ID:', identity_id)

except identity_client.exceptions.NotAuthorizedException as e:
    print('Failed to get identity ID:', e.response['Error']['Message'])
    # Additional error handling if needed

try:
    res = identity_client.get_credentials_for_identity(
        IdentityId=identity_id,
        Logins={
            f'cognito-idp.us-east-1.amazonaws.com/{user_pool_id}': jwt_token
        }
    )
    identity_credentials = res['Credentials']
    # print('Identity credentials:', identity_credentials)

except identity_client.exceptions.NotAuthorizedException as e:
    print('Failed to get credentials for identity:', e.response['Error']['Message'])
    # Additional error handling if needed

# Step 3: Retrieve an object from S3 using the temporary credentials
s3_client = boto3.client(
    's3',
    region_name=region,
    aws_access_key_id=identity_credentials['AccessKeyId'],
    aws_secret_access_key=identity_credentials['SecretKey'],
    aws_session_token=identity_credentials['SessionToken']
)

try:
    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=object_key
    )
    data = response['Body'].read()
    print('Object data:', data.decode('utf-8'))

except Exception as e:
    print('Error retrieving object from S3:', str(e))
