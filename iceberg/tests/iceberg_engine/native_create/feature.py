import os

from testflows.core import *

from iceberg.tests.iceberg_engine.native_create.steps import feature_available

MODULES = [
    # "sanity",
    "datatypes",
    "schema",
    "location",
    "namespaces",
    "explicit_engine",
    "metadata",
    "idempotency",
    "drop",
    "on_cluster",
    "lifecycle",
    "rbac",
]


@TestFeature
@Name("native create")
def feature(self, minio_root_user, minio_root_password):
    """Native CREATE TABLE / DROP TABLE for DataLakeCatalog (SRS-049)."""
    # Host-side storage observers (iceberg.tests.steps.s3_objects) read the
    # MinIO credentials from the context.
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    if not feature_available(self.context.node):
        skip(
            "build has no native CREATE/DROP for DataLakeCatalog "
            "(system.settings lacks data_lake_delete_data_on_drop)"
        )

    catalogs = ["rest"]
    if os.getenv("LOCALSTACK_AUTH_TOKEN"):
        catalogs.append("glue")

    for catalog in catalogs:
        with Feature(f"{catalog} catalog"):
            self.context.catalog = catalog
            for module in MODULES:
                Feature(
                    test=load(
                        f"iceberg.tests.iceberg_engine.native_create.{module}",
                        "feature",
                    )
                )(
                    minio_root_user=minio_root_user,
                    minio_root_password=minio_root_password,
                )
