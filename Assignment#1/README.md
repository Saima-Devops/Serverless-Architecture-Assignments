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

<br>

**Screenshot: EC2 instance with `Auto-Stop` tag**

<img width="1897" height="385" alt="image" src="https://github.com/user-attachments/assets/72fe3bdc-93bf-4c6b-8937-8927af72497a" />


------------------------------------------------------------------------

### Instance #2

Name: `instance-start`

| Key    | Value      |
|--------|------------|
| Action | Auto-Start |

<br>

**Screenshot: EC2 instance with` Auto-Start` tag**

<img width="1895" height="431" alt="image" src="https://github.com/user-attachments/assets/88f1907b-5a42-4f31-b273-2519c9c9f7e6" />

<img width="1892" height="606" alt="image" src="https://github.com/user-attachments/assets/1a490893-b605-4ee0-91c1-6bb8890dcb79" />


------------------------------------------------------------------------

# Step 2: Create IAM Role for Lambda

1.  Open `IAM` Dashboard
2.  Click Roles → Create Role
3.  Choose Lambda
4.  Add Permissions: `AmazonEC2FullAccess`

Role Name: `LambdaEC2ManagerRole`

<br>

**Screenshot: IAM role with EC2 permissions**

<img width="1890" height="797" alt="image" src="https://github.com/user-attachments/assets/a1193c21-7da7-43ef-9063-a7841a7eb4a9" />

<img width="1906" height="826" alt="image" src="https://github.com/user-attachments/assets/1fe7f3c1-0696-4cbe-b1c7-f063e285ebcf" />

<img width="1906" height="806" alt="image" src="https://github.com/user-attachments/assets/c1085c7a-92af-4418-a7d0-2b0868f64fc7" />

------------------------------------------------------------------------

# Step 3: Create Lambda Function

1.  Open AWS Lambda Console
2.  Click Create Function
3.  Choose Author From Scratch

**Settings:**

Function Name: `ec2-auto-manager`\
Runtime: `Python 3.x`\
Execution Role: `LambdaEC2ManagerRole`

<br>

**Screenshot: Lambda function creation page**

<img width="1797" height="776" alt="image" src="https://github.com/user-attachments/assets/bceac791-d561-4294-af2f-ab02395eadbb" />

<img width="1888" height="713" alt="image" src="https://github.com/user-attachments/assets/a131686b-035f-4061-b902-f6bf7d50c97a" />

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
<br>

**Screenshot: Lambda Code Editor**

<img width="1617" height="910" alt="image" src="https://github.com/user-attachments/assets/cd38dccc-272a-49c9-ad80-153b047c0758" />


------------------------------------------------------------------------

# Step 5: Deploy and Test Lambda

1.  Click Deploy
2.  Click Test
3.  Create test event
4. Invoke

Event Name: `test`
<br>

**Screenshot: Lambda test execution**

<img width="1887" height="762" alt="image" src="https://github.com/user-attachments/assets/4936dabb-4d0c-4656-b579-6aeba9b4e6c4" />


------------------------------------------------------------------------

# Step 6: Verify EC2 Results

Open EC2 Dashboard and check instance states.

Expected Results:

| Instance       |  Tag       |  Result   |
|----------------|------------|-----------|
| instance-stop  | Auto-Stop  | Stopped   |
| instance-start | Auto-Start | Running   |

<br>

**Screenshot: EC2 instances state after Lambda execution**

<img width="1912" height="625" alt="image" src="https://github.com/user-attachments/assets/eed9572f-cbbf-4832-ab0f-85576f8ed822" />

------------------------------------------------------------------------

# Case Testing

## Case 1
**Scenario:**

**Initial state:**

instance-stop = Stopped <br>
instance-start = Stopped

**Result:**

instance-stop = Stopped <br>
instance-start = Running

**Screenshot: EC2 instances state before & after Lambda execution**

<img width="1896" height="502" alt="image" src="https://github.com/user-attachments/assets/220b87f3-c78c-4753-95f1-61b4735031f4" />

<img width="1913" height="842" alt="image" src="https://github.com/user-attachments/assets/d356024b-19b1-488e-a7d7-29e30de01897" />

<img width="1912" height="625" alt="image" src="https://github.com/user-attachments/assets/c4e8351b-0e7f-4934-9077-21d60dae615f" />

------------------------------------------------------------------------

## Case 2
**Scenario:**

**Initial state:**

instance-stop = Running <br>
instance-start = Running

**Result:**

instance-stop = Stopped <br>
instance-start = Running

**Screenshot: EC2 instances state before & after Lambda execution**

<img width="1918" height="632" alt="image" src="https://github.com/user-attachments/assets/b8e86b51-57ad-45b4-a181-7d8bdb4b326a" />
<img width="1847" height="801" alt="image" src="https://github.com/user-attachments/assets/fdb2c690-c97f-43ae-99a1-9a7b84305f6c" />
<img width="1913" height="617" alt="image" src="https://github.com/user-attachments/assets/5b824b57-e9e7-4cf8-ab00-ec62762327fe" />


------------------------------------------------------------------------

## Case 3
**Scenario:**

**Initial state:**

instance-stop = Running
instance-start = Stopped

**Result:**

instance-stop = Stopped
instance-start = Running

**Screenshot: EC2 instances state before & after Lambda execution**

<img width="1918" height="592" alt="image" src="https://github.com/user-attachments/assets/61a9f4f9-b16c-429a-9a7a-bc8fea50489f" />

<img width="1886" height="852" alt="image" src="https://github.com/user-attachments/assets/a02a8d5c-ceec-412c-8d76-fd55e45bcdea" />

<img width="1918" height="707" alt="image" src="https://github.com/user-attachments/assets/d200d089-294d-4019-b0fd-2cea9b1d7f04" />


------------------------------------------------------------------------

# Conclusion

This project demonstrates how AWS Lambda and Boto3 can automatically
manage EC2 instances based on tags.

This is an automation approach that helps us to automate infrastructure management and reduce manual
work in AWS cloud architecture.

------------------------------------------------------------------------
