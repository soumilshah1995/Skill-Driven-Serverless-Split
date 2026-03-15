## Lab 1 – S3 Step Function Lock Processor

### Overview

This lab walks you through building a **distributed lock processor** using **AWS Step Functions**, **AWS Lambda (Python)**, and **Amazon S3**.  
The goal is to enforce **pessimistic locking** around a “worker” job so that only a safe number of concurrent workflows can run at once, while automatically cleaning up **stale locks** that exceed a configurable timeout.

At the end of the lab you will:

- Understand how to model a locking workflow in Step Functions.
- Use S3 objects as lock records and a simple JSON counter to track active locks.
- Implement Lambda handlers that **check**, **acquire**, and **release** locks safely.

---

### High‑Level Architecture

- **Step Functions state machine (`s3LockedProcessorWorkflow`)**
  - Orchestrates the locking lifecycle.
  - States:
    - `CheckIfLockExists` → Lambda `checkIfLockExists`
    - `CanAcquireLock` → choice on `canAcquireLock`
    - `AcquireLock` → Lambda `acquireLock`
    - `SubmitEMRStep` / `SimulateWorker` (placeholder “work”)
    - `ReleaseLock` → Lambda `releaseLock`
    - `LockFailed` (Fail state if lock cannot be acquired)

- **Lambda functions (Python, in `handlers/`)**
  - `check_lock.py` (`checkIfLockExists`):
    - Lists current S3 lock objects under `locks/`.
    - Removes **stale** locks based on `lock_timeout_minutes`.
    - Maintains an `active_locks.json` counter and decides if a new lock can be acquired (`canAcquireLock`).
  - `acquire_lock.py` (`acquireLock`):
    - Creates a new lock object in S3 with a unique `lockId` and timestamp.
    - Increments the `active_locks.json` counter.
  - `release_lock.py` (`releaseLock`):
    - Deletes the lock object.
    - Decrements the `active_locks.json` counter.

- **S3 bucket (`custom.bucketName` in `serverless.yml`)**
  - Stores:
    - `locks/<uuid>` JSON documents representing active locks.
    - `active_locks.json` containing a simple `{"count": <int>}` counter.

- **IAM role**
  - Grants Lambdas permission to read/write/delete S3 lock objects and to interact with EMR/Step Functions as needed.

This lab uses a **Serverless Framework** service defined in `serverless.yml` (`service: s3-locked-processor`) and deploys to AWS as a fully managed, event‑driven workflow.

---

### Input Contract and Lock Behaviour

Step Function executions expect an input payload similar to:

```json
{
  "bucket_name": "my-lock-bucket",
  "concurrency_limit": 1,
  "counter_name": "active_locks.json",
  "lock_timeout_minutes": 15
}
```

- **`bucket_name`**: S3 bucket where locks and the counter file live (must exist before running the lab).
- **`concurrency_limit`**: Maximum allowed concurrent locks; if `active_locks >= concurrency_limit`, the workflow fails with `LockAcquisitionFailed`.
- **`counter_name`**: Name of the JSON file that tracks the number of active locks.
- **`lock_timeout_minutes`**: Threshold after which an existing lock is treated as **stale** and removed during the `check_lock` step.

Lock lifecycle:

1. **Check** – `check_lock` removes stale locks and updates `active_locks.json`.
2. **Decision** – If `currentLocks < concurrency_limit`, `canAcquireLock = true`.
3. **Acquire** – `acquire_lock` creates a new lock object and increments the counter.
4. **Work** – A simulated worker step runs (placeholder for EMR or other workloads).
5. **Release** – `release_lock` deletes the lock and decrements the counter.

---

### Local Setup

#### Prerequisites

- **AWS account** with permissions to deploy Lambda, Step Functions, and S3.
- **AWS CLI** configured (`aws configure`) for the target account/region.
- **Node.js 14.x or higher** (for the Serverless Framework CLI).
- **npm** (bundled with Node.js).
- **Python 3.9** (matches `runtime: python3.9` in `serverless.yml`).

#### Install the Serverless Framework and plugins

From the docs worktree root:

```bash
cd Lab1

# Install the Serverless Framework CLI (if not already installed)
npm install -g serverless

# Install local dependencies (primarily plugins such as serverless-step-functions)
npm install
```

> The `serverless.yml` in this lab already references the `serverless-step-functions` plugin via the `plugins` section.

#### Python dependencies

The Lambda handlers in `handlers/` use only the **AWS SDK for Python (`boto3`)** and the Python standard library:

- On AWS, `boto3` is available in the managed Lambda runtime.
- If you want to run or unit‑test locally, create and activate a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install boto3
```

---

### Deployment

All deployment is driven by the **Serverless Framework** configuration in `Lab1/serverless.yml`.

#### 1. Prepare the S3 bucket

In `serverless.yml`, the bucket is configured as:

```yaml
custom:
  bucketName: soumil-dev-bucket-1995
```

- Create this bucket (or adjust the name and create your own):

```bash
aws s3 mb s3://soumil-dev-bucket-1995 --region us-east-1
```

#### 2. Deploy the stack

From `Lab1/`:

```bash
# Deploy to the default stage (usually "dev")
sls deploy

# Or deploy explicitly to a stage
sls deploy --stage dev
sls deploy --stage prod
```

Deployment creates:

- The three Lambda functions (`checkIfLockExists`, `acquireLock`, `releaseLock`).
- The Step Functions state machine (`s3-locked-processor-workflow`).
- IAM roles and permissions defined in `serverless.yml`.

---

### Running the Workflow

After deployment:

1. Open the **AWS Step Functions** console.
2. Locate the state machine named **`s3-locked-processor-workflow`**.
3. Choose **Start execution** and provide an input payload:

```json
{
  "bucket_name": "soumil-dev-bucket-1995",
  "concurrency_limit": 1,
  "counter_name": "active_locks.json",
  "lock_timeout_minutes": 15
}
```

4. Start multiple executions to observe how:
   - Only up to `concurrency_limit` executions are allowed concurrently.
   - Stale locks are removed once `lock_timeout_minutes` is exceeded.

You can inspect the S3 bucket to see:

- Lock objects under `locks/`.
- The `active_locks.json` counter being incremented/decremented.

---

### Testing and Validation

This lab does not include a dedicated automated test suite, but you can validate behaviour using:

- **Step Functions execution history**:
  - Confirm transitions through `CheckIfLockExists`, `AcquireLock`, and `ReleaseLock`.
  - Observe failures to `LockFailed` when `concurrency_limit` is exceeded.
- **CloudWatch Logs**:
  - Each Lambda logs messages (e.g., “Incremented active locks”, “Stale lock detected”).
- **S3 inspection**:
  - Verify creation, expiration, and deletion of `locks/*` objects.
  - Verify that `active_locks.json` count matches expectations.

If you want more formal tests, you can:

- Write unit tests for the handlers in `handlers/` using `pytest` and mocked `boto3` clients.
- Use Step Functions local or integration tests to simulate concurrent executions.

---

### Operational and Security Notes

- **IAM permissions** (from `serverless.yml`):
  - Lambdas can `GetObject`, `PutObject`, `DeleteObject`, and `ListBucket` on the configured lock bucket.
  - Additional permissions allow EMR and Step Functions interactions if you extend the lab.
- **Best practices** when turning this lab into production code:
  - Use a dedicated S3 bucket for locks and enable encryption and versioning.
  - Apply lifecycle policies to clean up old lock files.
  - Add alarms/metrics on:
    - Lock acquisition failures.
    - Stale lock cleanup events.
    - Concurrency limit violations.

This lab README is intentionally concise and focused on **what the lab is**, **how it is wired**, and **how to deploy and exercise the workflow**. For deeper exploration, inspect `serverless.yml` and the Lambda handlers in `handlers/`.
