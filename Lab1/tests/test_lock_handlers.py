import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

import pytest

# Ensure project root is on sys.path so Lab1 can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Lab1.handlers.acquire_lock import handler as acquire_lock_handler
from Lab1.handlers.check_lock import handler as check_lock_handler
from Lab1.handlers.release_lock import handler as release_lock_handler


class DummyS3ObjectBody:
    def __init__(self, data: str):
        self._data = data

    def read(self):
        return self._data.encode("utf-8")


@pytest.fixture
def dummy_context():
    return object()


def test_acquire_lock_happy_path(monkeypatch):
    captured_put_objects = []

    class DummyS3Client:
        class exceptions:
            class NoSuchKey(Exception):
                pass

        def put_object(self, Bucket, Key, Body):
            captured_put_objects.append({"Bucket": Bucket, "Key": Key, "Body": Body})

        def get_object(self, Bucket, Key):
            # Start with zero active locks
            return {"Body": DummyS3ObjectBody(json.dumps({"count": 0}))}

    dummy_s3 = DummyS3Client()

    # Monkeypatch boto3 client used inside the handler
    import Lab1.handlers.acquire_lock as acquire_mod

    monkeypatch.setattr(acquire_mod.boto3, "client", lambda service: dummy_s3)

    event = {"bucket_name": "test-bucket"}
    result = acquire_lock_handler(event, None)

    assert result["lockAcquired"] is True
    assert result["bucket_name"] == "test-bucket"
    assert "lockId" in result
    assert "lockPath" in result
    assert result["lockPath"].startswith("locks/")

    # Ensure lock object and counter were written
    assert any(obj["Key"].startswith("locks/") for obj in captured_put_objects)
    assert any(obj["Key"] == "active_locks.json" for obj in captured_put_objects)


def test_acquire_lock_failure_propagates_error(monkeypatch):
    class FailingS3Client:
        def put_object(self, Bucket, Key, Body):
            raise RuntimeError("boom")

    import Lab1.handlers.acquire_lock as acquire_mod

    monkeypatch.setattr(acquire_mod.boto3, "client", lambda service: FailingS3Client())

    event = {"bucket_name": "test-bucket"}
    result = acquire_lock_handler(event, None)

    assert result["lockAcquired"] is False
    assert "error" in result


def test_check_lock_missing_bucket_returns_400(dummy_context):
    event = {}
    result = check_lock_handler(event, dummy_context)

    assert result["statusCode"] == 400
    assert result["canAcquireLock"] is False
    assert "bucket_name" in result["error"]


def test_check_lock_all_active_within_limit(monkeypatch, dummy_context):
    # Create a recent timestamp so no locks are stale
    now = datetime.now().isoformat()
    lock_body = json.dumps({"timestamp": now})

    class DummyS3Client:
        class exceptions:
            class NoSuchKey(Exception):
                pass

        def list_objects_v2(self, Bucket, Prefix):
            return {
                "Contents": [
                    {"Key": "locks/lock-1"},
                    {"Key": "locks/lock-2"},
                ]
            }

        def get_object(self, Bucket, Key):
            if Key.startswith("locks/"):
                return {"Body": DummyS3ObjectBody(lock_body)}
            if Key == "active_locks.json":
                return {"Body": DummyS3ObjectBody(json.dumps({"count": 2}))}
            raise self.exceptions.NoSuchKey()

        def put_object(self, Bucket, Key, Body):
            # Accept updates to counter without side effects for this test
            pass

        def delete_object(self, Bucket, Key):
            # No stale locks in this test
            raise AssertionError("delete_object should not be called for active locks")

    import Lab1.handlers.check_lock as check_mod

    monkeypatch.setattr(check_mod, "s3", DummyS3Client())

    event = {"bucket_name": "test-bucket", "concurrency_limit": 3}
    result = check_lock_handler(event, dummy_context)

    assert result["canAcquireLock"] is True
    assert result["currentLocks"] == 2


def test_check_lock_stale_locks_cleaned_and_count_updated(monkeypatch, dummy_context):
    stale_time = (datetime.now() - timedelta(minutes=30)).isoformat()
    fresh_time = datetime.now().isoformat()

    lock_bodies = {
        "locks/stale-lock": json.dumps({"timestamp": stale_time}),
        "locks/active-lock": json.dumps({"timestamp": fresh_time}),
    }

    deleted_keys = []
    put_payloads = []

    class DummyS3Client:
        class exceptions:
            class NoSuchKey(Exception):
                pass

        def list_objects_v2(self, Bucket, Prefix):
            return {
                "Contents": [
                    {"Key": "locks/stale-lock"},
                    {"Key": "locks/active-lock"},
                ]
            }

        def get_object(self, Bucket, Key):
            if Key in lock_bodies:
                return {"Body": DummyS3ObjectBody(lock_bodies[Key])}
            if Key == "active_locks.json":
                # Pretend we had 2 locks recorded
                return {"Body": DummyS3ObjectBody(json.dumps({"count": 2}))}
            raise self.exceptions.NoSuchKey()

        def put_object(self, Bucket, Key, Body):
            put_payloads.append({"Bucket": Bucket, "Key": Key, "Body": Body})

        def delete_object(self, Bucket, Key):
            deleted_keys.append(Key)

    import Lab1.handlers.check_lock as check_mod

    monkeypatch.setattr(check_mod, "s3", DummyS3Client())

    event = {
        "bucket_name": "test-bucket",
        "concurrency_limit": 5,
        "lock_timeout_minutes": 15,
    }
    result = check_lock_handler(event, dummy_context)

    # One stale lock should have been removed
    assert "locks/stale-lock" in deleted_keys

    # The counter should have been updated from 2 down to 1
    assert any(
        p["Key"] == "active_locks.json"
        and json.loads(p["Body"])["count"] == 1
        for p in put_payloads
    )

    assert result["canAcquireLock"] is True
    assert result["currentLocks"] == 1


def test_release_lock_no_lock_info_returns_message(monkeypatch, dummy_context):
    event = {"bucket_name": "test-bucket"}
    result = release_lock_handler(event, dummy_context)

    assert result["lockReleased"] is False
    assert "No lock information" in result["message"]


def test_release_lock_happy_path(monkeypatch, dummy_context):
    deleted_keys = []
    put_payloads = []

    class DummyS3Client:
        def delete_object(self, Bucket, Key):
            deleted_keys.append(Key)

        def get_object(self, Bucket, Key):
            # Start from count 1
            return {"Body": DummyS3ObjectBody(json.dumps({"count": 1}))}

        def put_object(self, Bucket, Key, Body):
            put_payloads.append({"Bucket": Bucket, "Key": Key, "Body": Body})

    import Lab1.handlers.release_lock as release_mod

    monkeypatch.setattr(release_mod.boto3, "client", lambda service: DummyS3Client())

    event = {
        "bucket_name": "test-bucket",
        "lockId": "abc",
        "lockPath": "locks/abc",
    }
    result = release_lock_handler(event, dummy_context)

    assert result["lockReleased"] is True
    assert "releaseTimestamp" in result
    assert "locks/abc" in deleted_keys

    # Counter should have been decremented from 1 to 0
    assert any(
        p["Key"] == "active_locks.json"
        and json.loads(p["Body"])["count"] == 0
        for p in put_payloads
    )


