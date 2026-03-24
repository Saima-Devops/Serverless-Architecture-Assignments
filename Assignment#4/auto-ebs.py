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