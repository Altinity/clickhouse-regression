"""Catalog-specific happy paths and edge cases.

Because the outer feature loops over ``no_catalog``, ``rest`` and ``glue``,
most catalog-specific scenarios here only run for a subset of modes; the
others are skipped at runtime based on ``self.context.catalog``.

Planned scenarios:

    no_catalog (IcebergS3):
        * Export to a table at a custom MinIO path.
        * Export when the target prefix already contains (stale) metadata.
        * Two EXPORT PARTITION statements writing to the same URL from
          different replicas.

    rest (ice-rest-catalog):
        * Export to a table discovered via REST catalog namespace listing.
        * Export when the REST catalog returns 409 during the commit
          (simulated via network blip).

    glue (LocalStack):
        * Export through the Glue catalog and verify that a Glue
          ``GetTable`` call reflects the new snapshot.
        * Catalog-side UpdateTable concurrency handling.
"""

from testflows.core import *


@TestScenario
def placeholder(self, minio_root_user, minio_root_password):
    """Placeholder; catalog-specific scenarios pending implementation."""
    skip(f"catalog scenarios pending implementation (mode: {self.context.catalog})")


@TestFeature
@Name("catalogs")
def feature(self, minio_root_user, minio_root_password):
    """Catalog-specific export paths."""
    Scenario(test=placeholder)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
