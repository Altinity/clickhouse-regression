"""Entry point for the ``deletion_vectors`` suite (SRS-048).

ClickHouse read support for Iceberg format version 3 deletion vectors:
row-level deletes stored as ``deletion-vector-v1`` blobs in ``Puffin``
files. The external writer is the ``iceberg_spark`` container
(``tabulario/spark-iceberg``), whose ``demo`` catalog is wired to the
``rest`` Iceberg REST catalog and the MinIO ``warehouse`` bucket — Spark
commits ``DELETE`` / ``UPDATE`` / ``MERGE`` on v3 merge-on-read tables and
ClickHouse must return exactly the rows Spark itself would return.

Corruption-based scenarios (error handling, some vector shapes) rewrite the
Spark-written Puffin files and Avro manifests in place through the local
steps harness (``steps/puffin.py``, ``steps/manifest.py``).

Environment gaps (skipped scenarios, not silent omissions):

* ``icebergAzure`` — no Azure (azurite) service in ``iceberg_env``;
* ``Distributed.ProtocolFailClosed`` — needs a worker on an older protocol
  version, while all nodes here run the same build.
"""

from testflows.core import *

from iceberg.requirements.deletion_vectors import (
    SRS_048_ClickHouse_Iceberg_v3_Deletion_Vectors_Read_Support,
)

import iceberg.tests.steps.spark as spark


MODULES = (
    "sanity",
    "access_forms",
    "vector_shapes",
    "coexistence",
    "query_semantics",
    "time_travel",
    "partitioning",
    "count_paths",
    "error_handling",
    "distributed",
    "cache",
)


@TestFeature
@Specifications(SRS_048_ClickHouse_Iceberg_v3_Deletion_Vectors_Read_Support)
@Name("deletion vectors")
def feature(self, minio_root_user, minio_root_password):
    """Run all deletion-vector read scenarios."""
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    with Given("the Spark writer container is ready"):
        spark.wait_for_spark()

    for module in MODULES:
        Feature(
            test=load(f"iceberg.tests.deletion_vectors.{module}", "feature"),
            flags=TE,
        )(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
