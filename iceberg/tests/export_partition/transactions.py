"""Atomicity and idempotency of EXPORT PARTITION commits.

Planned scenarios:

    * Commit atomicity: a ClickHouse kill between ``append`` and commit must
      either leave the Iceberg table unchanged (no new snapshot) or advance
      the snapshot exactly once - never both.
    * Idempotency: re-running EXPORT PARTITION for an already-committed
      partition while the manifest TTL is active must be rejected with
      ``Export with key`` (see the PR's ``test_export_ttl``).
    * TTL expiry: after ``export_merge_tree_partition_manifest_ttl`` elapses
      the same partition can be re-exported.
    * Failure points (via failpoints):
        - failpoint_export_before_write
        - failpoint_export_before_commit
        - failpoint_export_after_commit (must be a no-op on retry)
"""

from testflows.core import *


@TestScenario
def placeholder(self, minio_root_user, minio_root_password):
    """Placeholder; transaction / atomicity scenarios pending implementation."""
    skip("transaction scenarios pending implementation")


@TestFeature
@Name("transactions")
def feature(self, minio_root_user, minio_root_password):
    """Transaction, idempotency, and failpoint scenarios."""
    Scenario(test=placeholder)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
