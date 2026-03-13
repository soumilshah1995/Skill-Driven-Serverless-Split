import boto3
import json
from datetime import datetime

def handler(event, context):
    """
    Lambda function to release a lock after processing is complete.

    Returns:
        dict: Contains lock release information and original event data
    """
    s3 = boto3.client('s3')

    # Extract parameters from the event
    bucket_name = event.get('bucket_name')
    counter_name = event.get('counter_name', 'active_locks.json')

    # Extract lock information
    lock_id = event.get('lockAcquisition', {}).get('lockId') if 'lockAcquisition' in event else event.get('lockId')
    lock_path = event.get('lockAcquisition', {}).get('lockPath') if 'lockAcquisition' in event else event.get('lockPath')

    # Check if we have lock information
    if not lock_id or not lock_path:
        print("No lock information found. Nothing to release.")
        return {
            **event,
            "lockReleased": False,
            "message": "No lock information found"
        }

    print(f"Attempting to release lock '{lock_id}' from bucket {bucket_name}")

    try:
        # Delete the lock file
        s3.delete_object(Bucket=bucket_name, Key=lock_path)

        # Decrement the active locks counter
        _decrement_active_locks(s3, bucket_name, counter_name)

        print(f"Lock '{lock_id}' released at {datetime.now().isoformat()}")

        # Return the original event with lock release information
        return {
            **event,
            "lockReleased": True,
            "releaseTimestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error releasing lock: {str(e)}")

        # If we fail to release the lock, return the error
        return {
            **event,
            "lockReleased": False,
            "error": str(e)
        }

def _decrement_active_locks(s3_client, bucket_name, counter_name):
    """
    Decrement the active locks counter.

    Args:
        s3_client: Boto3 S3 client
        bucket_name: Name of the S3 bucket
        counter_name: Name of the counter file
    """
    try:
        # Get current count
        response = s3_client.get_object(Bucket=bucket_name, Key=counter_name)
        content = response['Body'].read().decode('utf-8')
        active_locks = int(json.loads(content)['count'])

        # Decrement and update (ensure we don't go below 0)
        new_count = max(0, active_locks - 1)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=counter_name,
            Body=json.dumps({'count': new_count})
        )
        print(f"Decremented active locks from {active_locks} to {new_count}")

    except Exception as e:
        print(f"Error decrementing active locks: {str(e)}")
        raise