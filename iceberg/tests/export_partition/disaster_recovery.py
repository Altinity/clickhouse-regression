"""Disaster-recovery / failure-injection scenarios.

Planned scenarios (adapted from the PR integration tests and expanded):

    * MinIO reachable -> unreachable during an export: the scheduler retries
      up to ``export_merge_tree_partition_max_retries`` and ultimately
      either succeeds (when network is restored) or lands in FAILED with a
      non-zero ``exception_count``.
    * Keeper session loss mid-export: the export re-acquires the lock after
      reconnect and resumes or restarts cleanly.
    * Killing the ClickHouse process between ``PENDING`` and ``COMPLETED``
      leaves the destination in a consistent state; restart picks up and
      finishes the export.
    * ``SYSTEM STOP MOVES`` before/during export: existing PR tests cover
      this; we replicate them here so regression catches removals of the
      moves_blocker guard.
    * ``KILL EXPORT PARTITION`` from another node.
"""

from testflows.core import *


@TestScenario
def placeholder(self, minio_root_user, minio_root_password):
    """Placeholder; disaster recovery scenarios pending implementation."""
    skip("disaster recovery scenarios pending implementation")


@TestFeature
@Name("disaster recovery")
def feature(self, minio_root_user, minio_root_password):
    """Failure injection and recovery scenarios."""
    Scenario(test=placeholder)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
