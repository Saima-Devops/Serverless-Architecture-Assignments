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