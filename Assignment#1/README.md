# Assignment 1: Automated Instance Management Using AWS Lambda and Boto3

## Objective

The goal of this assignment is to automate the start and stop functionality of
EC2 instances based on tags using AWS Boto3 and Lambda function.

------------------------------------------------------------------------

# Step 1: Create EC2 Instances

1.  Open theAWS Console → EC2 Dashboard
2.  Launch two instances (t2.micro).

### Instance #1

Name: `instance-stop`

| Key    | Value      |
|--------|------------|
| Action | Auto-Stop |

Screenshot: EC2 instance with Auto-Stop tag



------------------------------------------------------------------------

### Instance #2

Name: `instance-start`

| Key    | Value      |
|--------|------------|
| Action | Auto-Start |

Screenshot: EC2 instance with Auto-Start tag


------------------------------------------------------------------------

# Step 2: Create IAM Role for Lambda

1.  Open IAM Dashboard
2.  Click Roles → Create Role
3.  Choose Lambda
4.  Add Permissions: `AmazonEC2FullAccess`

Role Name: `LambdaEC2ManagerRole`

Screenshot: IAM role with EC2 permissions

------------------------------------------------------------------------

# Step 3: Create Lambda Function

1.  Open AWS Lambda Console
2.  Click Create Function
3.  Choose Author From Scratch

Settings:

Function Name: ec2-auto-manager\
Runtime: Python 3.x\
Execution Role: LambdaEC2ManagerRole

Screenshot: Lambda function creation page

------------------------------------------------------------------------

# Step 4: Lambda Function Code

``` python
import boto3

# Initialize EC2 client 
ec2 = boto3.client('ec2' , region_name='ap-south-1')

# Lambda handler function

def lambda_handler(event, context):
    # -------------------------
    # Stop instances with Auto-Stop tag
    # -------------------------
    stop_response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Action', 'Values': ['Auto-Stop']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    stop_ids = [
        instance['InstanceId']
        for reservation in stop_response['Reservations']
        for instance in reservation['Instances']
    ]

    print("Instances found to stop (Auto-Stop & running):", stop_ids)

    if stop_ids:
        ec2.stop_instances(InstanceIds=stop_ids)
        print("Stopping instances:", stop_ids)
    else:
        print("No instances to stop.")

    # -------------------------
    # Start instances with Auto-Start tag
    # -------------------------
    start_response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Action', 'Values': ['Auto-Start']},
            {'Name': 'instance-state-name', 'Values': ['stopped']}
        ]
    )

    start_ids = [
        instance['InstanceId']
        for reservation in start_response['Reservations']
        for instance in reservation['Instances']
    ]

    print("Instances found to start (Auto-Start & stopped):", start_ids)

    if start_ids:
        ec2.start_instances(InstanceIds=start_ids)
        print("Starting instances:", start_ids)
    else:
        print("No instances to start.")

    return {
        'statusCode': 200,
        'stopped_instances': stop_ids,
        'started_instances': start_ids
    }
```

Screenshot: Lambda Code Editor

------------------------------------------------------------------------

# Step 5: Deploy and Test Lambda

1.  Click Deploy
2.  Click Test
3.  Create test event
4. Invoke

Event Name: `test`

Screenshot: Lambda test execution

------------------------------------------------------------------------

# Step 6: Verify EC2 Results

Open EC2 Dashboard and check instance states.

Expected results:

  Instance         Tag          Result
  ---------------- ------------ ---------
  instance-stop    Auto-Stop    Stopped
  instance-start   Auto-Start   Running

Screenshot: EC2 instances state after Lambda execution

------------------------------------------------------------------------

# Case Testing

## Case 1
**Scenario:**

Initial state:

instance-stop = Stopped
instance-start = Stopped

**Result:**

instance-stop = Stopped
instance-start = Running

Screenshot: EC2 instances state before & after Lambda execution

------------------------------------------------------------------------

## Case 2
**Scenario:**

Initial state:

instance-stop = Running
instance-start = Running

Result:

instance-stop = Stopped
instance-start = Running

Screenshot: EC2 instances state before & after Lambda execution

------------------------------------------------------------------------

## Case 3
**Scenario:**

Initial state:

instance-stop = Running
instance-start = Stopped

Result:

instance-stop = Stopped
instance-start = Running

Screenshot: EC2 instances state before & after Lambda execution

------------------------------------------------------------------------

# Conclusion

This project demonstrates how AWS Lambda and Boto3 can automatically
manage EC2 instances based on tags.

This is an automation approach helps automate infrastructure management and reduce manual
work in aws cloud environment.

------------------------------------------------------------------------