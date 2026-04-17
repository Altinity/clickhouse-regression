"""Schema evolution while EXPORT PARTITION runs / between exports.

Planned scenarios:

    * Add a nullable column to the source between two exports - the Iceberg
      table must gain the column with correct field-id and reader can still
      read the older snapshot.
    * Drop a column between exports - existing snapshots remain valid,
      subsequent export writes without that column.
    * Rename a column - Iceberg field IDs must be preserved (otherwise old
      data becomes unreadable).
    * Long-running export (large partition) while the source is ALTERed;
      the in-flight export must not observe a partial schema mid-way.
    * Column type widening (Int32 -> Int64).
"""

from testflows.core import *


@TestScenario
def placeholder(self, minio_root_user, minio_root_password):
    """Placeholder; schema evolution scenarios pending implementation."""
    skip("schema evolution scenarios pending implementation")


@TestFeature
@Name("schema evolution")
def feature(self, minio_root_user, minio_root_password):
    """Schema changes during and between exports."""
    Scenario(test=placeholder)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
