# Task#4: Automatic EBS Snapshot and Cleanup Using AWS Lambda


## Objective
Automate EBS snapshot creation and deletion of snapshots older than 30 days using AWS Lambda and Boto3.

---

## Overview

The Lambda function should be able to perform the following tasks:

- Take a snapshot of a specific EBS volume
- Tag-Based Automation instead of hardcoding the volume ID
- Find old snapshots (older than 30 days)
- Delete those old snapshots
- Log everything

---

## Step 1: EBS Volume Setup

Create a New EBS volume

1. Open EC2 Dashboard
2. Elastic Block Store → Volumes
3. Create Volume
4. Configure Volume
    - ✔️ Volume Type
         Choose:
         gp3 (General Purpose SSD) → recommended

    - ✔️ Size
         Choose: 10 GiB (eg.)

    - ✔️ Availability Zone
         Must match your EC2 instance's availability zone.

    - ✔️ Snapshot (Optional)
        Leave empty (for fresh volume)   

    - ✔️ Encryption
         Leave default (or enable if required)  

5. Add Tag

Before creating, expand Tags:

Click `Add tag` and enter:

```bash
Key: Backup 
Value: True
```

> This is what the Lambda function will use!

6. Click `Create volume`

<br>

Screenshot:

---

## Step 2: IAM Role
- Created IAM Role for Lambda
- Attached policy: `AmazonEC2FullAccess`
- Attached policy: `CloudWatchFullAccess`

Screenshot:

---

## Step 3: Lambda Function

```python
import boto3
from datetime import datetime, timezone, timedelta

ec2 = boto3.client('ec2')

RETENTION_DAYS = 30
TAG_KEY = "Backup"
TAG_VALUE = "True"

def lambda_handler(event, context):
    
    # Step 1: Get volumes with Backup=True tag
    volumes = ec2.describe_volumes(
        Filters=[
            {'Name': f'tag:{TAG_KEY}', 'Values': [TAG_VALUE]}
        ]
    )
    
    volume_ids = [v['VolumeId'] for v in volumes['Volumes']]
    
    print(f"Volumes to back up: {volume_ids}")
    
    created_snapshots = []
    deleted_snapshots = []
    
    now = datetime.now(timezone.utc)
    # Format current date as YYYY-MM-DD for snapshot name
    current_date_str = now.strftime("%Y-%m-%d")
    
    # Step 2: Loop through volumes
    for volume_id in volume_ids:
        
        # Create snapshot with date in description
        description = f"Backup-{volume_id}-{current_date_str}"
        
        snapshot = ec2.create_snapshot(
            VolumeId=volume_id,
            Description=description
        )
        
        snapshot_id = snapshot['SnapshotId']
        created_snapshots.append(snapshot_id)
        print(f"Created Snapshot: {snapshot_id} ({description})")
        
        # Step 3: Get snapshots for this volume
        snapshots = ec2.describe_snapshots(
            Filters=[
                {'Name': 'volume-id', 'Values': [volume_id]}
            ],
            OwnerIds=['self']
        )
        
        # Step 4: Delete old snapshots
        for snap in snapshots['Snapshots']:
            start_time = snap['StartTime']
            age = now - start_time
            
            if age > timedelta(days=RETENTION_DAYS):
                ec2.delete_snapshot(SnapshotId=snap['SnapshotId'])
                deleted_snapshots.append(snap['SnapshotId'])
                print(f"Deleted Snapshot: {snap['SnapshotId']}")
    
    return {
        "created_snapshots": created_snapshots,
        "deleted_snapshots": deleted_snapshots
    }
```

<br>

Screenshot:

---

## Step 4: EventBridge Scheduling

Create EventBridge Schedule

    - open EventBridge
    - Go to Scheduler - `Scheduler → Schedules`
    - Configure Basic Details
        - ✔️ Name: `EBS-Backup-Schedule`
        - ✔️ Schedule Pattern = `rate(7 days)` 
        - ✔️ Flexible Time Window = `OFF` (Ensures exact execution time)
        - ✔️ Select Target: `Lambda function`
        - ✔️ Permissions: `Create new role` (AWS will automatically create the correct permissions)
        - ✔️ Click `Create schedule`

> Lambda will now run automatically.

---

## Step 5: Testing 

### Temporary Changes for Testing:

To verify snapshot deletion quickly, the following changes were made:

```python
RETENTION_DAYS = 0
```

OR

```python
if age > timedelta(minutes=2):
```


### EventBridge Schedule for Testing:
```
rate(5 minutes)
```

> Run the Lambda function and check the logs.

### Note: 

After testing, ensure:

`RETENTION_DAYS = 30`

Schedule is set to `rate(7 days)`



### Result:

- Snapshot created automatically
- Snapshot deleted within 2 minutes

Screenshot:

---

## Step 5: EventBridge Trigger (Final Setup)

Created rule using schedule:
```bash
rate(7 days)
```

Screenshot:

---

## Step 6: Monitoring CloudWatch Logs

1.  Go to Lambda → Monitor
2.  Click **View CloudWatch Logs**
3.  Open latest log stream

Expected Logs:

---

## Step 7: Snapshot Verification

Checked EC2 → Snapshots


Confirmed:

- New snapshot created
- Old snapshots deleted

---

## Final Summary

I created an AWS Lambda function using Python and Boto3 to automate EBS snapshot management. The function performs the following tasks:

- Creates a snapshot of a specified EBS volume.
- Retrieves all snapshots associated with the volume.
- Deletes snapshots older than 30 days based on a retention policy.
- Logs, including the created and deleted snapshot IDs.

Note: An `IAM` role was configured with `EC2` permissions to allow `snapshot` creation and deletion. Additionally, an `EventBridge rule` was set up to trigger the `Lambda function` weekly/monthly, ensuring automated backups.

---

## Conclusion & Outcomes

- Automated backup process implemented
- Storage costs optimized by deleting old snapshots
- Fully serverless and scalable solution

---