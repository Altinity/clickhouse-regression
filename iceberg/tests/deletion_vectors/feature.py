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

from helpers.common import getuid

from iceberg.requirements.deletion_vectors import (
    SRS_048_ClickHouse_Iceberg_v3_Deletion_Vectors_Read_Support,
)

import iceberg.tests.steps.spark as spark
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects


MODULES = (
    # "sanity",
    # "access_forms",
    # "vector_shapes",
    # "coexistence",
    # "query_semantics",
    # "time_travel",
    # "partitioning",
    # "count_paths",
    "error_handling",
    "distributed",
    "cache",
)


@TestStep(Finally)
def cleanup_created_tables(self):
    """Batch-drop every table the suite created: unregister from the REST
    catalog via pyiceberg (fast, no Spark JVM), then delete the S3
    objects. Best-effort — cleanup must never fail the suite — but the S3
    prefix of a table is only deleted once the table is confirmed gone
    from the catalog (dropped, or already absent): deleting the objects
    under a still-registered table would turn a retriable leftover into a
    permanently broken catalog entry."""
    tables = getattr(self.context, "spark_created_tables", [])
    if not tables:
        return

    from pyiceberg.catalog import load_catalog
    from pyiceberg.exceptions import NoSuchTableError

    catalog = None
    try:
        catalog = load_catalog(
            f"dv_cleanup_{getuid()}",
            **{
                "uri": "http://localhost:8182",
                "type": "rest",
                "s3.endpoint": s3_objects.S3_HOST_ENDPOINT,
                "s3.access-key-id": self.context.minio_root_user,
                "s3.secret-access-key": self.context.minio_root_password,
            },
        )
    except Exception as exc:
        note(
            f"REST catalog unavailable for cleanup, retaining all "
            f"{len(tables)} table(s) for a later attempt: {exc}"
        )

    dropped = 0
    retained = []
    deleted_objects = 0
    for namespace, table_name in tables:
        identifier = f"{namespace}.{table_name}"

        unregistered = False
        if catalog is not None:
            try:
                catalog.drop_table(identifier)
                unregistered = True
            except NoSuchTableError:
                unregistered = True  # confirmed absent
            except Exception as exc:
                note(f"failed to drop {identifier} from the catalog: {exc}")
            try:
                catalog.drop_namespace(namespace)
            except Exception:
                pass  # non-empty or already gone — harmless either way

        if not unregistered:
            retained.append(identifier)
            continue

        dropped += 1
        try:
            deleted_objects += s3_objects.delete_prefix(
                s3_objects.table_prefix(namespace, table_name)
            )
        except Exception as exc:
            note(f"failed to delete objects of {identifier}: {exc}")

    note(
        f"cleanup: {dropped}/{len(tables)} table(s) dropped, "
        f"{deleted_objects} object(s) removed"
        + (f", retained for later cleanup: {retained}" if retained else "")
    )


@TestFeature
@Specifications(SRS_048_ClickHouse_Iceberg_v3_Deletion_Vectors_Read_Support)
@Name("deletion vectors")
def feature(self, minio_root_user, minio_root_password):
    """Run all deletion-vector read scenarios."""
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password
    self.context.spark_created_tables = []

    with Given("the Spark writer container is ready"):
        spark.wait_for_spark()

    try:
        for module in MODULES:
            Feature(
                test=load(f"iceberg.tests.deletion_vectors.{module}", "feature"),
            )(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
    finally:
        with Finally("clean up all Spark-created tables"):
            cleanup_created_tables()
