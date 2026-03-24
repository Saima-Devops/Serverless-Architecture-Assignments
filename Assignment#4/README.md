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

Created a New EBS volume

1. Opened **EC2** Dashboard
2. Elastic Block Store → **Volumes**
3. Created **Volume**
4. Configured Volume
    - ✔️ Volume Type
         Chosen:
         gp3 (General Purpose SSD) → recommended

    - ✔️ Size
         Chosen: 100 GiB (as eg.)

    - ✔️ Availability Zone
         Must match the EC2 instance's availability zone.

    - ✔️ Snapshot (Optional)
        Left empty (for fresh volume)   

    - ✔️ Encryption
         Left default (or enable if required)  

5. Added Tag
    - Before creation, expanded **Tags**:
    - Clicked `Add tag` and entered:
    ```bash
    Key: Backup 
    Value: True
    ```

> This is what my Lambda function will use!

<br>

6. Clicked `Create volume`

<br>

**Screenshots:**
<br>
**EBS Volume Created**

<img width="1917" height="867" alt="image" src="https://github.com/user-attachments/assets/039050a1-ca90-46a5-a6d6-740b1e116ec1" />


<img width="1905" height="373" alt="image" src="https://github.com/user-attachments/assets/3652d51a-4e79-4050-b631-70bd18a133bf" />


<img width="1918" height="977" alt="image" src="https://github.com/user-attachments/assets/bffda256-1fe8-449c-9fcf-164e9f36961a" />

---

## Step 2: IAM Role
- Created IAM Role for Lambda
- Attached policy: `AmazonEC2FullAccess`
- Attached policy: `CloudWatchFullAccess`

**Screenshot:**

<img width="1895" height="872" alt="image" src="https://github.com/user-attachments/assets/7b3a70e9-3804-4a7e-8b5e-46a1e9dfab76" />

---

## Step 3: Lambda Function Code

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

**Screenshots:**

<img width="1900" height="708" alt="image" src="https://github.com/user-attachments/assets/30b8d051-0b97-404a-b26e-e84cd5597faf" />

<img width="1918" height="860" alt="image" src="https://github.com/user-attachments/assets/bf395598-241e-4792-9add-ed85ed1095a6" />


---

## Step 4: EventBridge Scheduling

Created **EventBridge Schedule**

    - opened EventBridge
    - Clicked Scheduler - `Scheduler → Schedules`
    - Configured Basic Details
        - ✔️ Name: `EBS-Backup-Schedule`
        - ✔️ Schedule Pattern = `rate(7 days)` 
        - ✔️ Flexible Time Window = `OFF` (Ensures exact execution time)
        - ✔️ Select Target: `Lambda function`
        - ✔️ Permissions: `Create new role` (AWS will automatically create the correct permissions)
        - ✔️ Click `Create Schedule`

> Lambda will now run automatically.

<br>

**Screenshots:**

<img width="1906" height="848" alt="image" src="https://github.com/user-attachments/assets/486edfd6-4fa7-40d8-8556-bac33ea9c62b" />

<img width="1915" height="871" alt="image" src="https://github.com/user-attachments/assets/444c5d47-a9dd-4f01-ae53-7f06bab7fe4f" />

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

> Ran the Lambda function and checked the logs.

<br>

### Note: 

After testing, I reverted the final changes back:

`RETENTION_DAYS = 30`

Schedule is set to `rate(7 days)`

<br>

### Result:

- Snapshot created automatically
- Snapshot deleted within a minute


<br>

**Screenshots:**

<img width="1907" height="982" alt="image" src="https://github.com/user-attachments/assets/756a709e-e0b6-4da5-9534-ccd72fe3f612" />

<img width="1912" height="983" alt="image" src="https://github.com/user-attachments/assets/b85a42a1-bbec-4941-89bf-5e2653336d39" />

<img width="1913" height="620" alt="image" src="https://github.com/user-attachments/assets/6c408ca1-770b-4299-9138-de16f8db0562" />

---

## Step 5: EventBridge Trigger (Final Setup)

Created rule using schedule:
```bash
rate(7 days)
```

**Screenshot:**

<img width="1915" height="871" alt="image" src="https://github.com/user-attachments/assets/ef622d4c-1b3f-4206-bd98-667a1004daf7" />

---

## Step 6: Monitoring CloudWatch Logs

1.  Opened **Lambda → Monitor**
2.  Clicked **View CloudWatch Logs**
3.  Opened the latest **log stream**

**Expected Logs:**

<img width="1887" height="867" alt="log stream" src="https://github.com/user-attachments/assets/7d2a8817-1735-43f3-9e2f-f3de933e44a0" />

<img width="1917" height="911" alt="image" src="https://github.com/user-attachments/assets/7eb790ed-3feb-4e7e-820a-62de6c768b0c" />

<img width="1918" height="880" alt="image" src="https://github.com/user-attachments/assets/621e3a3a-2dd4-414f-9c12-1a2293d879ce" />

---

## Step 7: Snapshot Verification

Checked `EC2 → Snapshots`


<img width="1918" height="973" alt="image" src="https://github.com/user-attachments/assets/b8db837f-356c-4f23-8e87-401a905f26bd" />

<br>


### Confirmed:

- New snapshots are being created after 7 days (Weekly Backup)
- Old snapshots will be deleted after 30 days (Monthly Cleanup)

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
