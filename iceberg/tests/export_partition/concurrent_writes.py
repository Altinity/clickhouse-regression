"""Concurrent EXPORT PARTITION scenarios.

Planned scenarios:

    * Multiple replicas attempting to export the same partition: exactly one
      wins; the others report KILLED / FAILED gracefully via ZK coordination.
    * Multiple partitions exported in parallel from the same node - verify
      final row counts and that no partition's data leaks into another.
    * EXPORT PARTITION concurrent with INSERT into the same source table:
      the new parts must not be silently pulled into the running export but
      should surface in a subsequent export.
    * EXPORT PARTITION concurrent with ALTER TABLE ... MOVE PARTITION.
"""

from testflows.core import *


@TestScenario
def placeholder(self, minio_root_user, minio_root_password):
    """Placeholder; concurrent scenarios pending implementation."""
    skip("concurrent export scenarios pending implementation")


@TestFeature
@Name("concurrent writes")
def feature(self, minio_root_user, minio_root_password):
    """Concurrent exports across replicas and partitions."""
    Scenario(test=placeholder)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
