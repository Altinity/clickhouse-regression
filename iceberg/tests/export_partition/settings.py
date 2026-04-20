"""Per-setting behaviour tests for EXPORT PARTITION.

Planned scenarios, one per setting:

    * ``enable_experimental_export_merge_tree_partition_feature = 0`` (server
      setting, requires restart): EXPORT PARTITION must be rejected with
      ``SUPPORT_IS_DISABLED``.
    * ``allow_experimental_export_merge_tree_part = 0`` (query setting,
      default ``true``): related EXPORT PART form must be rejected when
      disabled.
    * ``export_merge_tree_partition_max_retries``: exercise 0, 1, and large
      values against a blocked MinIO.
    * ``export_merge_tree_partition_manifest_ttl``: verify TTL gating of
      retries (see the PR's ``test_export_ttl``).
    * ``export_merge_tree_partition_force_export``: force a re-export after
      a successful commit within the TTL window.
    * ``export_merge_tree_partition_lock_inside_task``: round-trip behaviour
      under contention.
    * ``write_full_path_in_iceberg_metadata``: covered functionally in
      ``storage_paths`` but also asserted here at the metadata level.
    * Parquet-writer settings (compression, row-group size) relayed via the
      output writer - verify the destination Parquet files respect them.
"""

from testflows.core import *


@TestScenario
def placeholder(self, minio_root_user, minio_root_password):
    """Placeholder; settings scenarios pending implementation."""
    skip("settings scenarios pending implementation")


@TestFeature
@Name("settings")
def feature(self, minio_root_user, minio_root_password):
    """Behaviour of each export_merge_tree_partition_* setting."""
    Scenario(test=placeholder)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
