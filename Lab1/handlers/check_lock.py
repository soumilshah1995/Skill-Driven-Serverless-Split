import boto3
import json
from datetime import datetime, timedelta

# Initialize the S3 client
s3 = boto3.client('s3')

def handler(event, context):
    """
    AWS Lambda function to check if a processing lock can be acquired.
    This function also handles cleaning up of stale locks and updates the active lock count.

    Args:
        event (dict): Input event containing:
            - bucket_name (str): Name of the S3 bucket containing locks
            - concurrency_limit (int, optional): Maximum number of allowed concurrent locks (default: 1)
            - counter_name (str, optional): Name of the JSON file storing the active lock count (default: 'active_locks.json')
            - lock_timeout_minutes (int, optional): Timeout for considering a lock as stale (default: 15 minutes)

    Returns:
        dict: A response indicating whether the lock can be acquired:
            - canAcquireLock (bool): True if the lock can be acquired, False otherwise
            - currentLocks (int): The number of currently active locks
            - statusCode (int, optional): 400 if input validation fails
            - error (str, optional): Error message if validation fails
    """
    # Extract parameters from the event
    bucket_name = event.get('bucket_name')
    concurrency_limit = event.get('concurrency_limit', 1)
    counter_name = event.get('counter_name', 'active_locks.json')
    lock_timeout_minutes = event.get('lock_timeout_minutes', 15)

    # Validate required parameters
    if not bucket_name:
        print("Error: Missing required parameter 'bucket_name'")
        return {
            'statusCode': 400,
            'canAcquireLock': False,
            'error': 'Missing required parameter: bucket_name'
        }

    print(f"Checking if lock can be acquired in bucket: {bucket_name}")
    print(f"Concurrency limit: {concurrency_limit}")
    print(f"Lock timeout: {lock_timeout_minutes} minutes")

    try:
        # Attempt to retrieve all locks from S3
        print("Retrieving existing locks from S3...")
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix='locks/')

        stale_locks_removed = 0
        if 'Contents' in response:
            print("Checking for stale locks...")
            for obj in response['Contents']:
                lock_key = obj['Key']
                lock_data_response = s3.get_object(Bucket=bucket_name, Key=lock_key)
                lock_data = json.loads(lock_data_response['Body'].read().decode('utf-8'))

                # Check if the lock is stale
                lock_timestamp = datetime.fromisoformat(lock_data['timestamp'])
                current_time = datetime.now()
                if current_time - lock_timestamp > timedelta(minutes=lock_timeout_minutes):
                    print(f"Stale lock detected: {lock_key}. Removing...")
                    s3.delete_object(Bucket=bucket_name, Key=lock_key)
                    stale_locks_removed += 1
                else:
                    print(f"Active lock found: {lock_key}")

        # Update the active locks count after cleaning stale locks
        print(f"Retrieving and updating active lock count in {counter_name}...")
        try:
            response = s3.get_object(Bucket=bucket_name, Key=counter_name)
            content = response['Body'].read().decode('utf-8')
            active_locks = int(json.loads(content)['count'])

            # Decrement the active locks count by the number of stale locks removed
            active_locks = max(0, active_locks - stale_locks_removed)

            # Update the counter file
            s3.put_object(
                Bucket=bucket_name,
                Key=counter_name,
                Body=json.dumps({'count': active_locks})
            )
        except s3.exceptions.NoSuchKey:
            print("Lock counter file does not exist. Initializing with zero active locks.")
            active_locks = 0
            s3.put_object(
                Bucket=bucket_name,
                Key=counter_name,
                Body=json.dumps({'count': active_locks})
            )

        can_acquire = active_locks < concurrency_limit

        print(f"Current active locks: {active_locks}")
        print(f"Can acquire lock: {can_acquire}")

        return {
            "canAcquireLock": can_acquire,
            "currentLocks": active_locks
        }

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'canAcquireLock': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }
