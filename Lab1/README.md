# S3 Step Function Lock Processor

A generic distributed workflow lock processor that implements pessimistic locking using AWS S3 and Step Functions. This solution ensures only one process can run at any given time by using S3 as a distributed lock mechanism, with built-in stale lock detection and timeout management.

<img width="330" height="356" alt="S3 Step Function Lock Processor Architecture" src="https://github.com/user-attachments/assets/a1520b31-69f1-4524-a779-3ec4fc41779a" />

## 🔧 Features

- **Pessimistic Locking**: Ensures mutual exclusion using S3-based distributed locks
- **Stale Lock Detection**: Automatically detects and handles stale locks from aborted Step Function executions
- **Configurable Timeout**: Customizable lock timeout to prevent indefinite locking
- **Concurrency Control**: Configurable concurrency limits for controlled parallel execution
- **Serverless Architecture**: Built with AWS Lambda and Step Functions for scalability
- **Lock Counter Management**: Tracks active locks using JSON-based counters

## 🏗️ Architecture

The lock processor uses the following components:

1. **S3 Bucket**: Acts as the distributed lock store
2. **Step Functions**: Orchestrates the locking workflow
3. **Lambda Functions**: Handles lock acquisition, release, and validation
4. **Lock Files**: JSON-based lock files stored in S3
5. **Counter Files**: Track active lock counts

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Node.js 14.x or higher
- Serverless Framework installed

### Installation

```bash
# Clone the repository
git clone https://github.com/soumilshah1995/s3-step-fn-lock-processor.git
cd s3-step-fn-lock-processor

# Install dependencies
npm install

# Install serverless step functions plugin
npm install --save-dev serverless-step-functions
```

### Deployment

```bash
# Deploy the stack
sls deploy

# Deploy to specific stage
sls deploy --stage prod
```

## 📋 Usage

### Sample Execution Payload

```json
{
  "bucket_name": "my-lock-bucket",
  "concurrency_limit": 1,
  "counter_name": "active_locks.json",
  "lock_timeout_minutes": 15
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `bucket_name` | String | Yes | S3 bucket name for storing lock files |
| `concurrency_limit` | Integer | Yes | Maximum number of concurrent processes allowed |
| `counter_name` | String | Yes | Name of the lock counter file (e.g., "active_locks.json") |
| `lock_timeout_minutes` | Integer | Yes | Lock timeout duration in minutes |

### Example Usage

```python
import boto3
import json

# Initialize Step Functions client
stepfunctions = boto3.client('stepfunctions')

# Define the execution payload
payload = {
    "bucket_name": "my-distributed-locks",
    "concurrency_limit": 1,
    "counter_name": "workflow_locks.json",
    "lock_timeout_minutes": 30
}

# Start execution
response = stepfunctions.start_execution(
    stateMachineArn='arn:aws:states:region:account:stateMachine:LockProcessor',
    input=json.dumps(payload)
)
```

## 🔒 Lock Mechanism

### How It Works

1. **Lock Acquisition**: Process attempts to create a lock file in S3
2. **Concurrency Check**: Validates against the configured concurrency limit
3. **Lock Validation**: Checks for existing locks and their timestamps
4. **Stale Lock Detection**: Identifies and removes expired locks
5. **Process Execution**: Runs the protected workflow
6. **Lock Release**: Removes the lock file upon completion or timeout

### Lock File Structure

```json
{
  "lock_id": "unique-lock-identifier",
  "timestamp": "2024-01-15T10:30:00Z",
  "process_id": "step-function-execution-arn",
  "timeout_minutes": 15,
  "status": "active"
}
```

### Counter File Structure

```json
{
  "active_locks": 1,
  "max_concurrency": 1,
  "last_updated": "2024-01-15T10:30:00Z",
  "locks": [
    {
      "lock_id": "unique-lock-identifier",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## 🛡️ Stale Lock Handling

The system automatically handles stale locks through:

- **Timeout Detection**: Locks exceeding the configured timeout are marked as stale
- **Cleanup Process**: Stale locks are automatically removed during lock acquisition attempts
- **Health Checks**: Periodic validation of active locks against running Step Function executions

### Stale Lock Scenarios

- Step Function execution is aborted or fails
- Lambda function timeout or error
- Manual termination of processes
- AWS service interruptions

## ⚙️ Configuration

### Environment Variables

```yaml
# serverless.yml
environment:
  LOCK_BUCKET: ${self:custom.lockBucket}
  DEFAULT_TIMEOUT: 15
  MAX_RETRIES: 3
  CLEANUP_INTERVAL: 300
```

### Custom Configuration

```yaml
# serverless.yml
custom:
  lockBucket: my-distributed-locks-${self:provider.stage}
  concurrencyLimits:
    dev: 2
    prod: 1
  timeoutMinutes:
    dev: 10
    prod: 30
```

## 🔍 Monitoring and Logging

### CloudWatch Metrics

- Lock acquisition success/failure rates
- Lock timeout occurrences
- Stale lock cleanup events
- Concurrency violations

### Log Groups

- `/aws/lambda/lock-processor-acquire`
- `/aws/lambda/lock-processor-release`
- `/aws/lambda/lock-processor-cleanup`
- `/aws/stepfunctions/lock-processor-workflow`

### Sample CloudWatch Query

```sql
fields @timestamp, @message
| filter @message like /LOCK_ACQUIRED/
| stats count() by bin(5m)
```

## 🚨 Error Handling

### Common Error Scenarios

| Error | Description | Resolution |
|-------|-------------|------------|
| `LockAcquisitionFailed` | Unable to acquire lock due to concurrency limit | Retry with exponential backoff |
| `StaleLockDetected` | Found expired locks during acquisition | Automatic cleanup triggered |
| `S3AccessDenied` | Insufficient permissions for S3 operations | Verify IAM permissions |
| `LockTimeoutExceeded` | Lock held longer than configured timeout | Automatic lock release |

### Retry Strategy

```json
{
  "Retry": [
    {
      "ErrorEquals": ["LockAcquisitionFailed"],
      "IntervalSeconds": 2,
      "MaxAttempts": 3,
      "BackoffRate": 2.0
    }
  ]
}
```

## 🔐 Security Considerations

### IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-lock-bucket/*",
        "arn:aws:s3:::my-lock-bucket"
      ]
    }
  ]
}
```

### Best Practices

- Use dedicated S3 bucket for locks
- Enable S3 versioning for lock files
- Implement S3 bucket encryption
- Set up S3 lifecycle policies for cleanup
- Monitor S3 access patterns

## 🧪 Testing

### Unit Tests

```bash
npm test
```

### Integration Tests

```bash
npm run test:integration
```

### Load Testing

```bash
# Test concurrent lock acquisition
npm run test:load
```

## 📊 Performance Considerations

- **S3 Consistency**: Utilizes S3 strong consistency for reliable locking
- **Lock Granularity**: Fine-g
