import boto3    
import variables as vr

# Usage example
user_pool_id = vr.user_pool_id
username = vr.username
password = vr.password

def create_user(username, password, user_pool_id):
    client = boto3.client('cognito-idp')

    try:
        response = client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            TemporaryPassword=password,
            UserAttributes=[
                {
                    'Name': 'email_verified',
                    'Value': 'True'
                },
                {
                    'Name': 'email',
                    'Value': 'ilsoldier1984@gmail.com'
                }
            ]
        )
    except client.exceptions.UsernameExistsException:
        print('User already exists.')
        quit()


    try:
        # Check user status
        user_status = client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=username
        )['UserStatus']

        if user_status == 'CONFIRMED':
            print('User is already confirmed.')
            return

    except client.exceptions.UserNotFoundException:
        print('User not found.')

    try:
        client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=password,
            Permanent=True
        )

        print('User created and approved successfully.')

    except client.exceptions.NotAuthorizedException as e:
        if e.response['Error']['Code'] == 'NotAuthorizedException' and 'FORCE_CHANGE_PASSWORD' in e.response['Error']['Message']:
            # User needs to change the temporary password
            client.admin_set_user_password(
                UserPoolId=user_pool_id,
                Username=username,
                Password=password,
                Permanent=True
            )
            # client.admin_confirm_sign_up(
            #     UserPoolId=user_pool_id,
            #     Username=username
            # )
            print('User created, password changed, and approved successfully.')
        else:
            raise e



create_user(username, password, user_pool_id)
