#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from s3.regression import argparser
from s3.tests.common import enable_vfs

from object_storage_vfs.requirements import SRS_038_ClickHouse_Disk_Object_Storage_VFS

xfails = {}

ffails = {}


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
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    if not allow_vfs:
        skip("VFS is not enabled")

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with Given("I enable allow_object_storage_vfs"):
        enable_vfs()

    Feature(run=load("object_storage_vfs.tests.outline", "feature"))


if main():
    regression()
