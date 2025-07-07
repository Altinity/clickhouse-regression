from testflows.core import *


@TestFeature
@Name("iceberg engine")
def feature(self, minio_root_user, minio_root_password):
    """Run iceberg engine test."""
    self.context.catalog = "rest"
    Feature(
        test=load("iceberg.tests.catalogs.nessie_sanity", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.catalogs.tabulario", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("iceberg.tests.catalogs.ice", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
