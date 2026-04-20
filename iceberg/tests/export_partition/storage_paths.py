"""Storage path / location-related behaviour.

Planned scenarios:

    * ``write_full_path_in_iceberg_metadata = 1`` writes absolute URIs that
      tools like Athena / Trino accept.
    * ``write_full_path_in_iceberg_metadata = 0`` (default) keeps
      relative paths; moving the table directory does not break reads.
    * Mixed locations: the table directory lives at one S3 prefix while
      data files live at another - both ClickHouse and PyIceberg must
      resolve them correctly.
    * Tables with deep prefix hierarchies (e.g. ``s3://bucket/a/b/c/d/e``).
"""

from testflows.core import *


@TestScenario
def placeholder(self, minio_root_user, minio_root_password):
    """Placeholder; storage path scenarios pending implementation."""
    skip("storage path scenarios pending implementation")


@TestFeature
@Name("storage paths")
def feature(self, minio_root_user, minio_root_password):
    """Storage location and path-writing behaviour."""
    Scenario(test=placeholder)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
