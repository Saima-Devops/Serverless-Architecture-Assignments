# Task#2: Automated S3 Bucket Cleanup Using AWS Lambda and Boto3

## Objective

Automate deletion of files older than **30 days** from an S3 bucket
using AWS Lambda and Boto3.

------------------------------------------------------------------------

## Mental Map

**S3 Bucket** (Files Stored)  →  **AWS Lambda** (Python + Boto3)  →  **Delete Files** (Older Than 30 Days)

------------------------------------------------------------------------

## Step 1: S3 Setup

1.  Go to **AWS Console → S3**
2.  Click **Create Bucket**
3.  Example bucket name: `s3-cleanup-demo-saima`

4.  Upload multiple files.

> Here Some files are **older than 30 days** - Some files are **recent**

**Screenshot:**

<img width="1915" height="782" alt="image" src="https://github.com/user-attachments/assets/47917d74-e70a-41fb-9360-affd1b05b275" />

<img width="1917" height="851" alt="image" src="https://github.com/user-attachments/assets/218bdb94-4c35-40d9-80ed-b759e140737b" />

------------------------------------------------------------------------

## Step 2: Create Lambda IAM Role

1.  Open **IAM → Roles**
2.  Click **Create Role**
3.  Select **Lambda**
4.  Attach policy: `AmazonS3FullAccess`

5.  Role Name: `LambdaS3CleanupRole`

**Screenshot:**

<img width="1896" height="790" alt="image" src="https://github.com/user-attachments/assets/3ebc5c48-ba04-4b38-b033-3d7b414344f0" />

------------------------------------------------------------------------

## Step 3: Create Lambda Function

Configuration:

Function Name: `s3-cleanup-function`\
Runtime: `Python 3.x`\
Execution Role: `LambdaS3CleanupRole`

**Screenshot:**

<img width="1897" height="865" alt="image" src="https://github.com/user-attachments/assets/a48b89ba-6aff-4790-9243-60f6604c82a1" />

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

print("Cleanup Complete.")
```

**Screenshot:**

<img width="1902" height="860" alt="image" src="https://github.com/user-attachments/assets/aa78a35c-3157-4e93-95ad-167f996ec7b3" />

------------------------------------------------------------------------

## Step 5: Test Lambda

1.  Click **Deploy**
2.  Click **Test**
3.  Create **test event**

Event Name: `test`

**Screenshot:**

<img width="1867" height="711" alt="image" src="https://github.com/user-attachments/assets/c36059e1-4ce4-4829-9d4e-83bba30c7b7c" />

------------------------------------------------------------------------

## Step 6: Verify Results

After running Lambda:

| File Age           | Result     |
|--------------------|------------|
| Older than 30 days | Deleted    |
| Newer than 30 days | Remains    |


------------------------------------------------------------------------

## Step 6: Verify Logs

<img width="1917" height="728" alt="image" src="https://github.com/user-attachments/assets/7de68209-2816-47d4-8130-f101bd1c0c5d" />

<img width="1918" height="747" alt="image" src="https://github.com/user-attachments/assets/778f298f-ef4e-42b0-81e2-5fe4e5b9f1d1" />

------------------------------------------------------------------------

## Step 7: Temporarily Reduce the Age Threshold (just for Demo Purpose)

Change: 

``` python
DAYS = 30
```
to

``` python
DAYS = 0
```

<img width="1872" height="440" alt="image" src="https://github.com/user-attachments/assets/7ffaaadf-75d1-4943-b6c9-ebb8fd58a0e5" />

<br>

> Any file older than a few seconds/minutes will be deleted.

------------------------------------------------------------------------

### Screenshots:


**Before:**

<img width="1917" height="972" alt="image" src="https://github.com/user-attachments/assets/8cf95e1f-279e-44c1-b562-279df2b2231c" />

<br>
<br>

**After Running Lambda Function:**

<img width="1913" height="973" alt="image" src="https://github.com/user-attachments/assets/43587df8-c96a-43c5-a028-16f0214d6eb0" />

<img width="1917" height="981" alt="image" src="https://github.com/user-attachments/assets/c1e99279-3ede-4567-84b4-a78787e292b8" />

------------------------------------------------------------------------
