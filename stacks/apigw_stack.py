from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
)
from constructs import Construct
from models.post_truck_model import post_truck_schema

with open("./templates/get_all_trucks.txt", "r", encoding="utf-8") as f:
    get_all_trucks_template= f.read()

with open("./templates/get_all_records.txt", "r", encoding="utf-8") as f:
    get_all_records_template= f.read()

class RestApiGWStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, 
                user_pool: cognito.UserPool, 
                add_truck_lambda: _lambda.Function, 
                trucks_table: dynamodb.Table, 
                records_table: dynamodb.Table, 
                **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        rest_api = apigw.RestApi(
            self,
            "RunlogRestApi",
            deploy_options=apigw.StageOptions(
                throttling_rate_limit=10,
                throttling_burst_limit=2
            )
        )

        rest_api.add_gateway_response("BadRequestBody",
            type=apigw.ResponseType.BAD_REQUEST_BODY,
            status_code="400",
            templates={
                "application/json": "{ \
                    \"message\": $context.error.message, \
                    \"statusCode\": \"400\", \
                    \"validationErrorString\": \"$context.error.validationErrorString\"\
                    }"
            }
        )

        rest_auth = apigw.CognitoUserPoolsAuthorizer(self, "RunlogCognitoAuthorizer",
            cognito_user_pools=[user_pool]
        )

        post_truck_model = rest_api.add_model("AddTruckModel",
            content_type="application/json",
            model_name="PostTruckRequestModel",
            schema=post_truck_schema
        )

        add_truck = rest_api.root.add_resource("addtruck")

        add_truck.add_method(
            "POST",
            apigw.LambdaIntegration(add_truck_lambda),
            authorizer=rest_auth,
            authorization_type=apigw.AuthorizationType.COGNITO,
            request_models={
                "application/json": post_truck_model
            },
            request_validator_options=apigw.RequestValidatorOptions(
                request_validator_name="PostTruckRequestModelValidator",
                validate_request_body=True,
                validate_request_parameters=False
            ),
        )

        ddb_scan_policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    actions=["dynamodb:Scan"],
                    resources=[f"{trucks_table.table_arn}", f"{records_table.table_arn}"],
                    effect=iam.Effect.ALLOW
                )
            ]
        )

        # create the IAM role for APIGW to call dynamodb
        ddb_scan_role = iam.Role(self, "DynamoDBScanRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            inline_policies={
                "DynamoDBScanPolicy": ddb_scan_policy
            }
        )

        get_all_trucks = apigw.AwsIntegration(
            service="dynamodb",
            action="Scan",
            integration_http_method="POST",
            options=apigw.IntegrationOptions(
                credentials_role=ddb_scan_role,
                request_templates={
                    "application/json": repr({"TableName": trucks_table.table_name}).replace("'", '"')
                },
                integration_responses=[
                    apigw.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": get_all_trucks_template
                        }
                    )
                ],
                passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_TEMPLATES,
            )
        )

        all_trucks = rest_api.root.add_resource("alltrucks")

        all_trucks.add_method("GET",
            get_all_trucks,
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=rest_auth,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                )
            ]
        )

        get_all_records = apigw.AwsIntegration(
            service="dynamodb",
            action="Scan",
            integration_http_method="POST",
            options=apigw.IntegrationOptions(
                credentials_role=ddb_scan_role,
                request_templates={
                    "application/json": repr({"TableName": records_table.table_name}).replace("'", '"')
                },
                integration_responses=[
                    apigw.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": get_all_records_template
                        }
                    )
                ],
                passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_TEMPLATES,
            )
        )

        all_records = rest_api.root.add_resource("allrecords")

        all_records.add_method("GET",
            get_all_records,
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=rest_auth,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                )
            ]
        )

        # create DELETE method for a specific record
        delete_record = rest_api.root.add_resource("{filename}")

        delete_record.add_method("DELETE",
            apigw.AwsIntegration(
                service="dynamodb",
                action="DeleteItem",
                integration_http_method="DELETE",
                options=apigw.IntegrationOptions(
                    credentials_role=ddb_scan_role,
                    request_templates={
                        "application/json": repr({
                            "TableName": records_table.table_name,
                            "Key": {
                                "filename": {
                                    "S": "$input.params('filename')"
                                }
                            }
                        }).replace("'", '"')
                    },
                    integration_responses=[
                        apigw.IntegrationResponse(
                            status_code="200",
                            response_templates={
                                "application/json": ""
                            }
                        )
                    ],
                    passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_TEMPLATES,
                )
            ),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=rest_auth,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                )
            ]
        )
