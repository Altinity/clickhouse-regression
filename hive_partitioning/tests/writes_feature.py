from testflows.core import *


@TestFeature
@Name("writes")
def feature(self, uri, minio_root_user, minio_root_password, uri_readonly):
    """Run writes test."""

    Feature(test=load("hive_partitioning.tests.writes.generic", "feature"))(
        uri=uri,
        uri_readonly=uri_readonly,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password
    )
    Feature(test=load("hive_partitioning.tests.writes.partition_by", "feature"))(
        uri=uri,
        uri_readonly=uri_readonly,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password
    )
    Feature(test=load("hive_partitioning.tests.writes.stratagy_parameter", "feature"))(
        uri=uri,
        uri_readonly=uri_readonly,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password
    )
    Feature(test=load("hive_partitioning.tests.writes.path_parameter", "feature"))(
        uri=uri,
        uri_readonly=uri_readonly,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password
    )
    Feature(
        test=load("hive_partitioning.tests.writes.s3_engine_parameters", "feature")
    )(
        uri=uri,
        uri_readonly=uri_readonly,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Feature(test=load("hive_partitioning.tests.writes.filename_parameter", "feature"))(
        uri=uri,
        uri_readonly=uri_readonly,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password
    )
