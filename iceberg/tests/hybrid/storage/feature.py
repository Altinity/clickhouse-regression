from testflows.core import *


@TestFeature
@Name("storage")
def feature(self, minio_root_user, minio_root_password):
    """Catalog Iceberg / icebergCluster / S3 Parquet segments, type auto-cast, schema refresh."""
    Feature(
        test=load("iceberg.tests.hybrid.storage.mergetree_iceberg_catalog", "feature")
    )(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Feature(
        test=load("iceberg.tests.hybrid.storage.mergetree_iceberg_cluster", "feature")
    )(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Feature(test=load("iceberg.tests.hybrid.storage.mergetree_s3", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Feature(test=load("iceberg.tests.hybrid.storage.type_autocast_iceberg", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Feature(test=load("iceberg.tests.hybrid.storage.schema_refresh", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
