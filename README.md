
# Welcome to the Runlog3.o CDK Python project!

This app tracks test records for a fleet of trucks based on incoming CSV files. 
Trucks configurations and test records are stored in DDB tables. 
As soon as a CSV file is uploaded into the IncomingCsv S3 bucket, Lambda function is invoked. 
The first Lambda function creates a test record in Records DDB table. 
As soon as the record is created, the second Lambda generates a map from coordinates 
in the CSV file and adds the file name into the records table.

## Install the CDK

```
$ curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
$ sudo apt install nodejs
```

```
$ npm install -g aws-cdk
```

## Setup
To manually create a virtualenv on MacOS and Linux:

### inside the Runlog30 directory
```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

Configure the AWS credentials for the profile you want to use and run

```
$ cdk deploy --all
```

to skip approvals for each stack run

```
$ cdk deploy --all --require-approval=never
```

## Usage

Once the app is deployed, populate all the values in the ```variables.py``` file

1. Run ```createuser.py``` to create a user in the Cognito User Pool
 - all API calls require a JWT of the user authenticated with CUP
2. Run ```addtruck.py``` to create a truck configuration entry
3. Run ```alltrucks.py``` to list all truck configurations
4. Upload the CSV files into the IncomingCsvs bucket
5. Run ```allrecords.py``` to retrieve the created records
6. Run ```getmap.py``` to retreive maps