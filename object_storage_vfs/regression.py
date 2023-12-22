#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.common import check_clickhouse_version
from s3.regression import argparser
from s3.tests.common import start_minio

from object_storage_vfs.requirements import *

xfails = {}

ffails = {}

# RQ_SRS_038_DiskObjectStorageVFS_Providers_Configuration
# RQ_SRS_038_DiskObjectStorageVFS_Providers_AWS,
# RQ_SRS_038_DiskObjectStorageVFS_Providers_GCS,


@TestModule
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Providers_MinIO("1.0"))
def minio(
    self,
    uri,
    root_user,
    root_password,
    local,
    clickhouse_binary_path,
    collect_service_logs,
):
    """Setup and run minio tests."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            configs_dir=current_dir(),
            environ={
                "MINIO_ROOT_PASSWORD": root_password,
                "MINIO_ROOT_USER": root_user,
            },
        )
        self.context.cluster = cluster

    with And("I have a minio client"):
        start_minio(access_key=root_user, secret_key=root_password)
        uri_bucket_file = uri + f"/{self.context.cluster.minio_bucket}" + "/data/"

    Feature(test=load("object_storage_vfs.tests.core", "feature"))(
        uri=uri_bucket_file, key=root_user, secret=root_password
    )
    Feature(test=load("object_storage_vfs.tests.settings", "feature"))(
        uri=uri_bucket_file, key=root_user, secret=root_password
    )
    Feature(test=load("object_storage_vfs.tests.integrity", "feature"))(
        uri=uri_bucket_file, key=root_user, secret=root_password
    )

    if self.context.stress:
        Feature(test=load("object_storage_vfs.tests.stress", "feature"))(
            uri=uri_bucket_file, key=root_user, secret=root_password
        )


@TestModule
@Name("vfs")
@ArgumentParser(argparser)
@Specifications(SRS_038_ClickHouse_Disk_Object_Storage_VFS)
@XFails(xfails)
@FFails(ffails)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    storages,
    minio_uri,
    gcs_uri,
    aws_s3_region,
    aws_s3_bucket,
    minio_root_user,
    minio_root_password,
    aws_s3_access_key,
    aws_s3_key_id,
    gcs_key_secret,
    gcs_key_id,
    stress,
    allow_vfs,
):
    """Disk Object Storage VFS regression."""

    if not allow_vfs:
        skip("VFS is not enabled")

    self.context.clickhouse_version = clickhouse_version
    self.context.stress = stress

    if check_clickhouse_version("<23.11")(self):
        skip("vfs not supported on < 23.11")

    Module(test=minio)(
        local=local,
        clickhouse_binary_path=clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        uri=minio_uri,
        root_user=minio_root_user,
        root_password=minio_root_password,
    )


if main():
    regression()
