# Assignment#5: Auto-Tagging EC2 Instances on Launch, Using AWS Boto3 & Lambda function

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

**Screenshot:**

<img width="1897" height="865" alt="image" src="https://github.com/user-attachments/assets/ef89f444-36c9-4449-a68c-64577b5b7b2b" />

------------------------------------------------------------------------

## Step 2: Create Lambda Function

Function Name: `auto-tagging-function`\
Runtime: `Python 3.x`

**Screenshot:**

<img width="1883" height="860" alt="image" src="https://github.com/user-attachments/assets/d035db87-4757-4916-9ffe-304352b2c1fc" />

<img width="1912" height="876" alt="image" src="https://github.com/user-attachments/assets/8559efff-20f8-4b12-bf80-005b380c02c6" />

------------------------------------------------------------------------

## Step 3: Create a Lambda function

``` python
import boto3                     # AWS SDK for Python to interact with AWS services
import json                      # Used for formatting logs
from datetime import datetime    # Used to get current date

# Create EC2 client (initialized outside handler for better performance)
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    """
    This function is triggered by Amazon EventBridge when an EC2 instance changes state.
    It tags the EC2 instance when it reaches the 'running' state.
    """

    # Log the full event for debugging (visible in CloudWatch Logs)
    print("Received Event:")
    print(json.dumps(event))

    try:
        # Extract 'detail' section from the event
        detail = event.get('detail', {})

        # Get the instance ID (e.g., i-1234567890abcdef0)
        instance_id = detail.get('instance-id')

        # Get the current state of the instance (pending, running, stopping, etc.)
        state = detail.get('state')

        # Check if instance ID exists
        if not instance_id:
            print("Error: No instance-id found in event")
            return "Missing instance-id"

        # Only proceed if instance is in 'running' state
        # This avoids tagging during other states like 'pending' or 'stopping'
        if state != 'running':
            print(f"Ignoring instance {instance_id} because state is '{state}'")
            return f"Ignored state: {state}"

        # Get current date in YYYY-MM-DD format
        today = datetime.utcnow().strftime('%Y-%m-%d')

        # Define tags to apply
        tags = [
            {
                'Key': 'LaunchDate',   # Tag key
                'Value': today         # Current date as value
            },
            {
                'Key': 'HeroVired',
                'Value': 'DevOps-Saima'   # Custom tag (you can change this)
            },
            {
                'Key': 'ManagedBy',
                'Value': 'Lambda-Automation'  # Indicates automation
            }
        ]

        # Apply tags to the EC2 instance
        ec2.create_tags(
            Resources=[instance_id],   # List of instance IDs
            Tags=tags                  # Tags to apply
        )

        # Success log message
        print(f"Successfully tagged EC2 instance: {instance_id}")

        return f"Success: Instance {instance_id} tagged"

    except Exception as e:
        # Catch any unexpected errors
        print(f"Error occurred: {str(e)}")
        
        # Raise error so it appears properly in CloudWatch Logs
        raise
```

**Screenshot:**

<img width="1898" height="866" alt="image" src="https://github.com/user-attachments/assets/aeb1db04-6a1d-4998-a655-05a606493fd1" />

------------------------------------------------------------------------

## Step 4: Create EventBridge Rule

### 1: Open EventBridge

1. Go to AWS Console
2. In the search bar, type EventBridge
3. Click Amazon EventBridge

**Screenshot:**

<img width="517" height="523" alt="image" src="https://github.com/user-attachments/assets/9617a7a4-d862-4f68-8e55-f72ca375007f" />

------------------------------------------------------------------------

### 2: Go to Rules

1. On the left sidebar → click Rules
2. Click Create rule

------------------------------------------------------------------------

### 3: Configure & Define Rule Details

Fill in:

- Rule Name: `EC2AutoTaggingRule`
- Description: `Trigger Lambda when EC2 starts`
- Event bus: `Default` (leave as is)

- Rule type:
Select `Rule with an event pattern` > `Next`

**Screenshot:**

<img width="1897" height="870" alt="image" src="https://github.com/user-attachments/assets/0170b8f3-f0d9-4e11-a866-c6bd3f383dc0" />

------------------------------------------------------------------------

### 4: Build Event Pattern

**Now choose:**

- Event source: `AWS events`
- Service provider: `AWS`
- Service name: `EC2`
- Event type: `EC2 Instance State-change Notification`

<br>
**Now Choose Pattern Method**

Select:

- Use custom pattern (JSON editor)
``` json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["running"]
  }
}
```

**Screenshot:**

<img width="1898" height="850" alt="image" src="https://github.com/user-attachments/assets/4dedc133-6cc3-4cfe-a1d4-f186093312b0" />
 
------------------------------------------------------------------------

### 5: Select Target

Now you connect it to the Lambda function:

- Target type: `AWS service`
- Select target: `Lambda function`
- Target Location: `Target in this account`
- Function: `auto-tagging-function` (the lambda function which I have created earlier)

> This links AWS Lambda to the rule

`Next`

**Screenshots:**

<img width="1888" height="852" alt="image" src="https://github.com/user-attachments/assets/a3c8294e-81a8-46e0-b68a-67e0affadde1" />

<img width="1186" height="502" alt="image" src="https://github.com/user-attachments/assets/55dab72f-d17f-458c-8274-4128791242e4" />

------------------------------------------------------------------------

### 6: Review & Create

- Check everything
- Click Create rule

**Screenshot:**

<img width="1917" height="877" alt="image" src="https://github.com/user-attachments/assets/5c9128ae-0264-4c61-b4c1-d2cf04dec22d" />

------------------------------------------------------------------------

## How It Works After Setup

1. You launch instance in Amazon EC2
2. EC2 sends event → EventBridge
3. EventBridge matches your rule
4. It triggers Lambda
5. Lambda tags the instance

**Event: `EC2 → State change → running`**

------------------------------------------------------------------------

## Step 6: Testing

Launch EC2 instance

**Screenshot:**

<img width="1892" height="867" alt="image" src="https://github.com/user-attachments/assets/0b5d6a9a-85ba-4ca8-a3ba-726a11deded5" />

<img width="1886" height="820" alt="image" src="https://github.com/user-attachments/assets/986ac180-ef4e-41fe-82ed-483f4204b7d0" />

------------------------------------------------------------------------

## Step 7: Verify

Check Tags:

LaunchDate → Date\
HeroVired → DevOps-Saima\
ManagedBy → Lambda-Automation

**Screenshot:**

<img width="841" height="337" alt="image" src="https://github.com/user-attachments/assets/136181ec-6a3f-4afa-b88c-62c76109d500" />


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

**Screenshot:**

<img width="1896" height="863" alt="image" src="https://github.com/user-attachments/assets/981b6d02-d9e4-4460-ac75-9c027f526187" />

------------------------------------------------------------------------

## Conclusion

With the help of Lambda function, I have built an automated system using:

- Amazon EC2 → launches instance
- Amazon CloudWatch → detects launch
- AWS Lambda → runs code
- Boto3 → applies tags

------------------------------------------------------------------------
