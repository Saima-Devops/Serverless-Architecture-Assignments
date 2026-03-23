# Assignment #5: Auto-Tagging EC2 Instances on Launch, Using AWS Boto3 & Lambda function

## Objective

Automatically tag EC2 instances at launch using AWS Lambda.

------------------------------------------------------------------------

## Mental Map

EC2 Launch → EventBridge → Lambda fn → Auto Tagging

------------------------------------------------------------------------

## How it Works?

1. When we launch an EC2 instance
2. AWS CloudWatch detects the launch event
3. It triggers the Lambda function
4. Lambda uses Boto3 to tag the instance


------------------------------------------------------------------------

## Step 1: IAM Role for Lambda

Policy#1: `AmazonEC2FullAccess`
Policy#2: `CloudWatchFullAccess`
Policy#3: `AWSLambdaBasicExecutionRole`

Trusted entity: `Lambda`

Role Name: `LambdaEC2AutoTagRole`

Screenshot:

------------------------------------------------------------------------

## Step 2: Create Lambda Function

Function Name: `auto-tagging-function`\
Runtime: `Python 3.x`

Screenshot:

------------------------------------------------------------------------

## Step 3: Lambda function Code

``` python
import boto3
import json
from datetime import datetime

# Initialize the EC2 client outside the handler for better performance (TCP Warm Start)
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # 1. Log the incoming event for debugging
    print("Received event:", json.dumps(event))

    try:
        # 2. Extract Instance ID from the EventBridge structure
        # Matches the 'EC2 Instance State-change Notification' format
        instance_id = event.get('detail', {}).get('instance-id')

        if not instance_id:
            print("No Instance ID found in event. Exiting.")
            return {
                'statusCode': 400,
                'body': 'Missing instance-id'
            }

        # 3. Define the Tags
        today = datetime.utcnow().strftime('%Y-%m-%d')
        tags = [
            {'Key': 'LaunchDate', 'Value': today},
            {'Key': 'HeroVired', 'Value': 'DevOps-Saima'},
            {'Key': 'ManagedBy', 'Value': 'Lambda-Automation'}
        ]

        # 4. Apply Tags to the EC2 Instance
        ec2.create_tags(
            Resources=[instance_id],
            Tags=tags
        )

        success_msg = f"Successfully tagged instance {instance_id}"
        print(success_msg)
        
        return {
            'statusCode': 200,
            'body': json.dumps(success_msg)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal Error: {str(e)}")
        }
```

Screenshot:

------------------------------------------------------------------------

## Step 4: Create EventBridge Rule

### Step 1: Open EventBridge

1. Go to AWS Console
2. In the search bar, type EventBridge
3. Click Amazon EventBridge

------------------------------------------------------------------------

### Step 2: Go to Rules

1. On the left sidebar → click Rules
2. Click Create rule

------------------------------------------------------------------------

### Step 3: Configure & Define Rule Details

Fill in:

- Rule Name: `EC2-Auto-Tagging-Rule`
- Description: `Trigger Lambda when EC2 starts`
- Event bus: `Default` (leave as is)

- Rule type:
Select `Rule with an event pattern` > `Next`

------------------------------------------------------------------------

### Step 4: Build Event Pattern

Now choose:

- Event source: `AWS events`
- Service provider: `AWS`
- Service name: `EC2`
- Event type: `EC2 Instance State-change Notification`

<br>
Now Choose Pattern Method

Select:

- Use custom pattern (JSON editor)

{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["running"]
  }
}
 
------------------------------------------------------------------------

### Step 5: Select Target

Now you connect it to the Lambda function:

- Target type: `AWS service`
- Select target: `Lambda function`
- Target Location: `Target in this account`
- Function: `auto-tagging-function` (the lambda function which I have created earlier)

> This links AWS Lambda to the rule

`Next`

------------------------------------------------------------------------

### Step 6: Review & Create

- Check everything
- Click Create rule

Screenshots:


------------------------------------------------------------------------

## How It Works After Setup

1. You launch instance in Amazon EC2
2. EC2 sends event → EventBridge
3. EventBridge matches your rule
4. It triggers Lambda
5. Lambda tags the instance

Event: `EC2 → State change → running`

Screenshot:

------------------------------------------------------------------------

## Step 5: Add Target

Lambda: ec2-auto-tag

Screenshot:

------------------------------------------------------------------------

## Step 6: Testing

Launch EC2 instance

Screenshot:

------------------------------------------------------------------------

## Step 7: Verify

Check Tags:

LaunchDate → Date\
HeroVired → DevOps-Saima\
ManagedBy → Lambda-Automation

Screenshot:

------------------------------------------------------------------------

## Step 8: Monitoring CloudWatch Logs

1.  Go to Lambda → Monitor
2.  Click **View CloudWatch Logs**
3.  Open latest log stream

Expected Logs:

    START RequestId: xxxx
    Tagged instance i-1234567890
    END RequestId: xxxx
    REPORT RequestId: xxxx Duration: 120 ms

Screenshots:



------------------------------------------------------------------------

## Conclusion

With the help of Lambda function, I have built an automated system using:

- Amazon EC2 → launches instances
- Amazon CloudWatch → detects launch
- AWS Lambda → runs code
- Boto3 → applies tags


------------------------------------------------------------------------