from testflows.core import *


@TestFeature
@Name("native create")
def feature(self, minio_root_user, minio_root_password):
    """Run native create test for Iceberg table engine, database engine and table functions."""
    with Feature("rest catalog"):
        self.context.catalog = "rest"
        Feature(
            test=load(
                "iceberg.tests.iceberg_engine.native_create.datatypes", "feature"
            ),
        )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
