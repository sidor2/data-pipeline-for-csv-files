from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_logs as logs,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_iam as iam
)
import uuid
from constructs import Construct

with open("./templates/get_all_records.txt", "r", encoding="utf-8") as f:
    get_all_records_template= f.read()


class RecordsDdbStack(Stack):
    """
    This stack creates Records DDB table and 
    a Lambda function to put test records in the table.
    """
    
    def __init__(self, scope: Construct, id: str, trucks_table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)


# TODO : maybe add a parameter to pass the bucket name

        # Define the S3 bucket
        csv_bucket = s3.Bucket(
            self, "CsvBucket",
            # removal_policy=RemovalPolicy.RETAIN,
            bucket_name=f"incomingcsvs-{uuid.uuid4()}",
            enforce_ssl=True
        )

        csv_upload_statement = iam.PolicyStatement(
            actions=["s3:PutObject"],
            not_resources=[csv_bucket.arn_for_objects("*.csv")],
            effect=iam.Effect.DENY,
            principals=[iam.AnyPrincipal()]
        )

        csv_bucket.add_to_resource_policy(csv_upload_statement)

        maps_bucket = s3.Bucket(
            self, "MapsBucket",
            # removal_policy=RemovalPolicy.RETAIN,
            bucket_name=f"maps-{uuid.uuid4()}",
            public_read_access=False,
            enforce_ssl=True,
        )

        self.records_table = dynamodb.Table(
            self,
            'RecordsTable',
            partition_key=dynamodb.Attribute(
                name='filename',
                type=dynamodb.AttributeType.STRING
            ), 
            stream=dynamodb.StreamViewType.NEW_IMAGE
        )

        # Define the Lambda function
        self.csv_lambda = _lambda.Function(
            self, "CsvLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("./lambdas/csv_lambda"),
            environment={
                'TRUCKS_TABLE_NAME': trucks_table.table_name,
                'RECORDS_TABLE_NAME': self.records_table.table_name
            }
        )

        logs.LogGroup(
            self,
            'CsvLambdaLogGroup',
            log_group_name=f'/aws/lambda/{self.csv_lambda.function_name}',
            retention=logs.RetentionDays.ONE_DAY
        )

        trucks_table.grant_read_write_data(self.csv_lambda)
        self.records_table.grant_read_write_data(self.csv_lambda)

        # Define the S3 bucket notification configuration
        notification = s3n.LambdaDestination(self.csv_lambda)

        csv_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            notification,
            s3.NotificationKeyFilter(suffix="_PQR.csv")
        )

        # create lambd layer with Pandas and Folium
        maps_lambda_layer = _lambda.LayerVersion(
            self, "MapsLambdaLayer",
            code=_lambda.Code.from_asset("./lambda_layers/maps_layer.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
        )

        dlq = sqs.Queue(self, "MapsLambdaDlq", queue_name="MapsLambdaDlq")

        # Create a Lambda function for generating maps
        maps_lambda = _lambda.Function(
            self, "MapsLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("./lambdas/maps_lambda"),
            layers=[maps_lambda_layer],
            environment={
                'CSV_BUCKET': csv_bucket.bucket_name,
                'MAPS_BUCKET': maps_bucket.bucket_name,
                'RECORDS_TABLE': self.records_table.table_name
            },
            timeout=Duration.minutes(2),
            retry_attempts=0,
            dead_letter_queue_enabled=True,
            dead_letter_queue=dlq
        )

#TODO Add dead letter queue for the Maps Lambda

        logs.LogGroup(
            self,
            'MapsLambdaLogGroup',
            log_group_name=f'/aws/lambda/{maps_lambda.function_name}',
            retention=logs.RetentionDays.ONE_DAY
        )

        self.records_table.grant_stream_read(maps_lambda)
        self.records_table.grant_write_data(maps_lambda)
        csv_bucket.grant_read(maps_lambda)
        maps_bucket.grant_write(maps_lambda)

        # Add a stream event source mapping to the Lambda function
        maps_lambda.add_event_source_mapping(
            "MapsLambdaEventSourceMapping",
            event_source_arn=self.records_table.table_stream_arn,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=1,
            filters=[_lambda.FilterCriteria.filter(
                {
                    "eventName": _lambda.FilterRule.is_equal("INSERT")
                 }
                )
            ]
        )

        # create output of bucket name
        CfnOutput(self, "CsvBucketName", value=csv_bucket.bucket_name)
        CfnOutput(self, "MapsBucketName", value=maps_bucket.bucket_name)
