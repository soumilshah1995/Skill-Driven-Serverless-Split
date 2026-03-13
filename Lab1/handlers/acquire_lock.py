import boto3
import json
import uuid
from datetime import datetime


def handler(event, context):
    """
    Lambda function to acquire a lock for the processing job.

    Returns:
        dict: Contains lock information and original event data
    """
    s3 = boto3.client('s3')

    # Extract parameters from the event
    bucket_name = event.get('bucket_name')
    counter_name = event.get('counter_name', 'active_locks.json')

    # Generate a unique lock ID
    lock_id = str(uuid.uuid4())
    lock_path = f"locks/{lock_id}"

    print(f"Attempting to acquire lock '{lock_id}' in bucket {bucket_name}")

    try:
        lock_timestamp = datetime.now().isoformat()
        lock_data = {
            "lockId": lock_id,
            "timestamp": lock_timestamp
        }

        s3.put_object(Bucket=bucket_name, Key=lock_path, Body=json.dumps(lock_data))

        # Increment the active locks counter
        _increment_active_locks(s3, bucket_name, counter_name)

        print(f"Lock '{lock_id}' acquired at {datetime.now().isoformat()}")

        # Return the original event with lock information added
        return {
            **event,
            "lockId": lock_id,
            "lockPath": lock_path,
            "lockAcquired": True,
            "lockTimestamp": lock_timestamp
        }

    except Exception as e:
        print(f"Error acquiring lock: {str(e)}")

        # If we fail to acquire the lock, return failure info
        return {
            **event,
            "lockAcquired": False,
            "error": str(e)
        }


def _increment_active_locks(s3_client, bucket_name, counter_name):
    """
    Increment the active locks counter.

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

        # Increment and update
        new_count = active_locks + 1
        s3_client.put_object(
            Bucket=bucket_name,
            Key=counter_name,
            Body=json.dumps({'count': new_count})
        )
        print(f"Incremented active locks from {active_locks} to {new_count}")

    except s3_client.exceptions.NoSuchKey:
        # If counter doesn't exist, initialize it with 1
        s3_client.put_object(
            Bucket=bucket_name,
            Key=counter_name,
            Body=json.dumps({'count': 1})
        )
        print("Initialized active locks counter to 1")

    except Exception as e:
        print(f"Error incrementing active locks: {str(e)}")
        raise
