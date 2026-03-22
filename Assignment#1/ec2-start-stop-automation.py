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