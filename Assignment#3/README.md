# Assignment 2: Automated S3 Bucket Cleanup Using AWS Lambda and Boto3

## Objective

Automate deletion of files older than **30 days** from an S3 bucket
using AWS Lambda and Boto3.

------------------------------------------------------------------------

## Mental Map

S3 Bucket (Files Stored) ↓ AWS Lambda (Python + Boto3) ↓ Delete Files
Older Than 30 Days

------------------------------------------------------------------------

## Step 1: S3 Setup

1.  Go to **AWS Console → S3**
2.  Click **Create Bucket**
3.  Example bucket name: `s3-cleanup-demo-saima`

4.  Upload multiple files.

> Here Some files are **older than 30 days** - Some files are **recent**

Screenshot:


------------------------------------------------------------------------

## Step 2: Create Lambda IAM Role

1.  Open **IAM → Roles**
2.  Click **Create Role**
3.  Select **Lambda**
4.  Attach policy: `AmazonS3FullAccess`

5.  Role Name: `LambdaS3CleanupRole`

Screenshot:


------------------------------------------------------------------------

## Step 3: Create Lambda Function

Configuration:

Function Name: `s3-cleanup-function`\
Runtime: `Python 3.x`\
Execution Role: `LambdaS3CleanupRole`

Screenshot:

------------------------------------------------------------------------

## Step 4: Lambda Code

``` python
import boto3
from datetime import datetime, timezone, timedelta

s3 = boto3.client('s3')

BUCKET_NAME = "s3-cleanup-demo-saima"
DAYS = 30

def lambda_handler(event, context):

    deleted_files = []

    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    if 'Contents' not in response:
        print("Bucket is empty")
        return

    for obj in response['Contents']:

        file_name = obj['Key']
        last_modified = obj['LastModified']

        file_age = datetime.now(timezone.utc) - last_modified

        if file_age > timedelta(days=DAYS):

            s3.delete_object(
                Bucket=BUCKET_NAME,
                Key=file_name
            )

            deleted_files.append(file_name)
            print(f"Deleted: {file_name}")

    if not deleted_files:
        print("No old files found")

    return {
        'statusCode': 200,
        'deleted_files': deleted_files
    }

print("Cleanup complete.")
```

Screenshot:

------------------------------------------------------------------------

## Step 5: Test Lambda

1.  Click **Deploy**
2.  Click **Test**
3.  Create **test event**

Event Name: `test`

Screenshot:


------------------------------------------------------------------------

## Step 6: Verify Results

After running Lambda:

| File Age           | Result     |
|--------------------|------------|
| Older than 30 days | Deleted    |
| Newer than 30 days | Remains    |


Screenshot:



------------------------------------------------------------------------

## Temporarily Reduce the Age Threshold just for Demo Purpose

Change: 

``` python
DAYS = 30
```
to

``` python
DAYS = 0
```

> Any file older than a few seconds/minutes will be deleted.

Screenshot:


------------------------------------------------------------------------