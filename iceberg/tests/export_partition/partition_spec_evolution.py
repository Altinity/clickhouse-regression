"""Partition spec changes between (or during) exports.

Planned scenarios:

    * Export with spec v1, then evolve the Iceberg partition spec (e.g. add
      a bucket field) externally, then export again - the two snapshots
      must remain individually readable and stats must reflect each spec.
    * Attempt to export into a table whose partition spec was changed after
      ClickHouse attached - must still map the MergeTree PARTITION BY to
      the current spec or reject synchronously.
    * Evolving from an identity transform to a higher-order transform
      (e.g. ``region`` -> ``truncate[2](region)``) between exports.
"""

from testflows.core import *


@TestScenario
def placeholder(self, minio_root_user, minio_root_password):
    """Placeholder; partition spec evolution scenarios pending implementation."""
    skip("partition spec evolution scenarios pending implementation")


@TestFeature
@Name("partition spec evolution")
def feature(self, minio_root_user, minio_root_password):
    """Partition spec changes during and between exports."""
    Scenario(test=placeholder)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
