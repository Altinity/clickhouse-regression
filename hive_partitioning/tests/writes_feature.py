from testflows.core import *


@TestFeature
@Name("writes")
def feature(self, uri, minio_root_user, minio_root_password):
    """Run writes test."""

    Feature(test=load("hive_partitioning.tests.writes.generic", "feature"))(
        uri=uri, 
        minio_root_user=minio_root_user, 
        minio_root_password=minio_root_password
    )