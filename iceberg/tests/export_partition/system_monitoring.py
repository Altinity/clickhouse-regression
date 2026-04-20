"""``system.replicated_partition_exports`` / profile event monitoring.

Planned scenarios:

    * Every required column of ``system.replicated_partition_exports`` is
      populated correctly for every status transition
      (PENDING -> RUNNING -> COMPLETED / FAILED / KILLED).
    * ``parts_count`` and ``parts_to_do`` converge to zero at COMPLETED and
      match the actual number of parts exported.
    * ``ExportPartitionZooKeeper*`` profile events increase by the expected
      amount per export.
    * ``system.part_log`` gets one ``ExportPart`` entry per exported part.
    * ``KILL EXPORT PARTITION`` reflects in the system table with status
      KILLED and preserves the original ``source_replica`` / ``create_time``.
    * ``export_merge_tree_partition_system_table_prefer_remote_information``
      flips reported status between "local-only" and "whole-cluster" views.
"""

from testflows.core import *


@TestScenario
def placeholder(self, minio_root_user, minio_root_password):
    """Placeholder; monitoring scenarios pending implementation."""
    skip("monitoring scenarios pending implementation")


@TestFeature
@Name("system monitoring")
def feature(self, minio_root_user, minio_root_password):
    """System-table and profile-event visibility of EXPORT PARTITION."""
    Scenario(test=placeholder)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
