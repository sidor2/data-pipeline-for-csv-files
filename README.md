# Data Pipeline for CSV Files

A serverless data pipeline that processes CSV files containing coordinates to generate maps and manages truck test records using AWS services.

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![AWS CDK](https://img.shields.io/badge/AWS_CDK-v2-orange)](https://aws.amazon.com/cdk/)

## Overview

This project implements a serverless data pipeline to process CSV files containing coordinates, generate maps, and store truck test records. It leverages AWS services such as S3, DynamoDB, Lambda, API Gateway, and Cognito for secure and scalable data processing and user authentication.

### Workflow
- **CSV Upload**: When a CSV file is uploaded to the `IncomingCsv` S3 bucket, a Lambda function is triggered.
- **Record Creation**: The first Lambda function creates a test record in the `RecordsTable` DynamoDB table.
- **Map Generation**: A second Lambda function generates a map from the CSV coordinates, saves it to the `Maps` S3 bucket, and updates the `RecordsTable` with the map file name.
- **Authentication**: User authentication is managed via a Cognito User Pool.

<img src="./workflow.png" alt="Workflow Diagram" width="600">

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
- **Serverless Processing**: Uses AWS Lambda for event-driven CSV processing and map generation.
- **Secure Authentication**: Integrates Cognito User Pool for user registration and authentication.
- **Scalable Storage**: Stores truck configurations and test records in DynamoDB tables.
- **RESTful API**: Provides API endpoints via API Gateway to manage truck records and retrieve data.
- **Map Visualization**: Generates maps from coordinates using Pandas and Folium libraries.

## Architecture

The application is built using the AWS Cloud Development Kit (CDK) and consists of several stacks:

### CognitoStack (`cognito_stack.py`)
Manages user authentication and authorization.
- **Cognito User Pool**: Supports self-sign-up, email verification, and user alias (email/username).
- **Cognito User Pool Client**: Facilitates authentication flows, including user-password and Secure Remote Password (SRP).
- **Cognito Identity Pool**: Grants authenticated users read-only access to S3 buckets via an IAM role.
- **Outputs**:
  - `UserPoolId`
  - `UserPoolClientId`
  - `IdentityPoolId`

### TrucksDdbStack (`truck_ddb_stack.py`)
Handles truck configuration storage.
- **DynamoDB Table**: `TrucksTable` with `currentVin` as the partition key.
- **Lambda Function**: `EnterTruckLambda`, triggered by API Gateway to insert truck records.
- **IAM Role**: Grants the Lambda function write access to `TrucksTable`.
- **Outputs**:
  - `TrucksTableARN`
  - `AddTruckLambdaARN`

### RecordsDdbStack (`records_ddb_stack.py`)
Processes CSV files and stores test records.
- **DynamoDB Table**: `RecordsTable` with `filename` as the partition key.
- **Lambda Function**: `CsvLambda`, triggered by S3 to process CSV files and insert data into `RecordsTable`.
- **S3 Buckets**:
  - `incomingcsvs-`: Stores uploaded CSV files and triggers `CsvLambda`.
  - `maps-`: Stores generated maps.
- **Lambda Layer**: Includes Pandas and Folium for map generation.
- **Outputs**:
  - `CsvBucketName`
  - `MapsBucketName`

### RestApiGWStack (`apigw_stack.py`)
Provides RESTful API endpoints.
- **API Gateway**: `RunlogRestApi` serves as the entry point for API requests.
- **Cognito Authorizer**: Secures API endpoints using Cognito User Pool.
- **API Methods**:
  - `POST /addtruck`: Adds truck records to `TrucksTable`.
  - `GET /alltrucks`: Retrieves all truck records.
  - `GET /allrecords`: Retrieves all test records.
- **IAM Role**: Grants read access to `TrucksTable` and `RecordsTable`.

### Application (`app.py`)
Orchestrates stack deployment and manages dependencies using AWS CDK.

### Additional Files
- Lambda functions: `csv_lambda.py`, `maps_lambda.py`, `trucksdb_lambda.py`.
- Utility scripts: `createuser.py`, `addtruck.py`, `alltrucks.py`, `allrecords.py`, `getmap.py`.
- Templates for data processing.

<img src="./diagram.png" alt="CDK App Architecture Diagram" width="600">

## Prerequisites
- **AWS CLI**: Installed and configured with appropriate credentials.
- **Node.js**: Required for AWS CDK (version 14 or higher recommended).
- **Python**: Version 3.8 or higher.
- **AWS CDK**: Install via `npm install -g aws-cdk`.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/username/repo.git
   cd runlog
   ```
2. Create and activate a virtual environment:
   - **MacOS/Linux**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows**:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate.bat
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Synthesize the CloudFormation template:
   ```bash
   cdk synth
   ```
5. Deploy the stacks:
   ```bash
   cdk deploy --all
   ```
   To skip manual approvals:
   ```bash
   cdk deploy --all --require-approval=never
   ```

## Usage
1. Populate the `variables.py` file with required values (e.g., bucket names, API endpoints).
2. Create a user in the Cognito User Pool:
   ```bash
   python createuser.py
   ```
   Note: All API calls require a JWT token from an authenticated Cognito user.
3. Add a truck configuration:
   ```bash
   python addtruck.py
   ```
4. List all truck configurations:
   ```bash
   python alltrucks.py
   ```
5. Upload CSV files to the `incomingcsvs-` S3 bucket to trigger processing.
6. Retrieve test records:
   ```bash
   python allrecords.py
   ```
7. Retrieve generated maps:
   ```bash
   python getmap.py
   ```