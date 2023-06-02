#!/usr/bin/env python3

import aws_cdk as cdk
from stacks.records_ddb_stack import RecordsDdbStack
from stacks.trucks_ddb_stack import TrucksDdbStack
from stacks.cognito_stack  import CognitoStack
from stacks.apigw_stack import RestApiGWStack


app = cdk.App()

cognito_stack = CognitoStack(app, "CognitoStack")

trucks_ddb_stack = TrucksDdbStack(app, "TrucksDdbStack")

records_ddb_stack = RecordsDdbStack(app, "RecordsDdbStack", 
                                    trucks_table=trucks_ddb_stack.trucks_table,
                                    )

rest_api_stack = RestApiGWStack(app, "RestApiGWStack", 
                                user_pool=cognito_stack.runlog_user_pool,
                                add_truck_lambda=trucks_ddb_stack.add_truck_lambda,
                                trucks_table=trucks_ddb_stack.trucks_table,
                                records_table=records_ddb_stack.records_table
                                )

rest_api_stack.add_dependency(cognito_stack)
records_ddb_stack.add_dependency(trucks_ddb_stack)

app.synth()
