from aws_cdk import (
    CfnOutput,
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_logs as logs
)

from constructs import Construct

class TrucksDdbStack(Stack):
    """
    This stack creates Trucks DDB table and 
    a Lambda function to put truck records in the table.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a DynamoDB table
        self.trucks_table = dynamodb.Table(
            self,
            'TrucksTable',
            partition_key=dynamodb.Attribute(
                name='currentVin',
                type=dynamodb.AttributeType.STRING
            )
        )

        lambda_role = iam.Role(
            self,
            'EnterTruckLambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    'service-role/AWSLambdaBasicExecutionRole'
                )
            ]
        )

        # Create a Lambda function to put records in the DynamoDB table
        self.add_truck_lambda = _lambda.Function(
            self,
            'EnterTruckLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='index.lambda_handler',
            code=_lambda.Code.from_asset('./lambdas/trucksdb_lambda'),
            role=lambda_role,
            # reserved_concurrent_executions=1,
            environment={
                'TRUCKS_TABLE_NAME': self.trucks_table.table_name,
                'LOG_LEVEL': 'INFO'
            }
        )

        # Grant write access to the DynamoDB table to the Lambda function
        self.trucks_table.grant_write_data(lambda_role)

        logs.LogGroup(
            self,
            'EnterTruckLambdaLogGroup',
            log_group_name=f'/aws/lambda/{self.add_truck_lambda.function_name}',
            retention=logs.RetentionDays.ONE_DAY
        )

        CfnOutput(self, "TrucksTableARN",
            value=self.trucks_table.table_arn,
            export_name="TrucksTableArn"
        )

        CfnOutput(self, "AddTruckLambdaARN",
            value=self.trucks_table.table_arn,
            export_name="AddTruckLambdaARN"
        )
