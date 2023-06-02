from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    CfnOutput,
    aws_apigatewayv2_authorizers_alpha as auth,
    aws_iam as iam,
)

from constructs import Construct

class CognitoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.runlog_user_pool = cognito.UserPool(self, "runlog_user_pool", 
            user_pool_name="RunlogUserPool",
            self_sign_up_enabled=True,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            sign_in_aliases=cognito.SignInAliases(email=True, username=True),
            standard_attributes=cognito.StandardAttributes(
                preferred_username=cognito.StandardAttribute(
                    required=True
                ),
                email=cognito.StandardAttribute(
                    required=True
                )
            )
        )

        self.runlog_client = self.runlog_user_pool.add_client(
            "runlog_client",
            generate_secret=False,
            user_pool_client_name="RunlogClient",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            )
        )
        
        # Create the Identity Pool
        self.identity_pool = cognito.CfnIdentityPool(self, "RunlogIdentityPool",
            identity_pool_name="runlog-identity-pool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=self.runlog_client.user_pool_client_id,
                    provider_name=self.runlog_user_pool.user_pool_provider_name
                )
            ]
        )

        # Create the IAM role for S3 access
        s3_access_role = iam.Role(self, "MapsS3AccessRole",
            assumed_by=iam.FederatedPrincipal(
                federated="cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": self.identity_pool.ref
                    }
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity"
            )
        )
        s3_access_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
        )

        # Attach the role to the Identity Pool
        cognito.CfnIdentityPoolRoleAttachment(self, "IdentityPoolRoleAttachment",
            identity_pool_id=self.identity_pool.ref,
            roles={"authenticated": s3_access_role.role_arn}
        )

# TODO: Create an IAM role for the identity pool allowing access to the Maps S3 bucket

        self.authorizer = auth.HttpUserPoolAuthorizer(
            'user_pool_authorizer',
            self.runlog_user_pool,
            authorizer_name='SourceDbLambdaAuthorizer',
            user_pool_clients=[self.runlog_client]
        )

        CfnOutput(self, "UserPoolId", value=self.runlog_user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=self.runlog_client.user_pool_client_id)
        CfnOutput(self, "IdentityPoolId", value=self.identity_pool.ref)