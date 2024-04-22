#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.common import check_clickhouse_version
from s3.regression import argparser
from s3.tests.common import start_minio

from vfs.requirements import *

xfails = {
    ":/settings/incompatible with zero copy": [(Fail, "not implemented yet")],
    ":/replica/command combinations/*": [(Error, "some combos time out")],
    ":/alter/move/:": [(Fail, "Fix pending")],
    ":/system/vfs events/VFSGcRunsException": [
        (Fail, "TODO: find method to generate this")
    ],
}

ffails = {
    "*": (
        Skip,
        "vfs not supported on < 24.2 and requires --allow-vfs flag",
        lambda test: not test.context.allow_vfs
        or check_clickhouse_version("<24.2")(test),
    ),
    ":/parallel replica": (Skip, "WIP"),
    ":/system/zookeeper timeout": (XFail, "unstable"),
}

# RQ_SRS038_DiskObjectStorageVFS_Providers_Configuration


@TestModule
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Providers_MinIO("1.0"))
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
    nodes = {
        "zookeeper": ("zookeeper1", "zookeeper2", "zookeeper3"),
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
    }

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            use_zookeeper_nodes=True,
            configs_dir=current_dir(),
            environ={
                "MINIO_ROOT_PASSWORD": root_password,
                "MINIO_ROOT_USER": root_user,
            },
        )
        self.context.cluster = cluster
        self.context.node = self.context.cluster.node("clickhouse1")
        self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]
        self.context.zk_nodes = [cluster.node(n) for n in cluster.nodes["zookeeper"]]
        self.context.access_key_id = root_user
        self.context.secret_access_key = root_password
        self.context.bucket_name = "root"
        self.context.bucket_path = "data/object-storage"

        self.context.minio_enabled = True

    with And("I have a minio client"):
        start_minio(access_key=root_user, secret_key=root_password)
        uri_bucket_file = uri + f"/{self.context.cluster.minio_bucket}" + "/data/"
        self.context.uri = uri_bucket_file

    Feature(run=load("vfs.tests.settings", "feature"))
    Feature(run=load("vfs.tests.table", "feature"))
    Feature(run=load("vfs.tests.ttl", "feature"))
    Feature(run=load("vfs.tests.system", "feature"))
    Feature(run=load("vfs.tests.migration", "feature"))

    Feature(run=load("vfs.tests.alter", "feature"))
    Feature(run=load("vfs.tests.replica", "feature"))
    # Feature(run=load("vfs.tests.parallel_replica", "feature"))
    Feature(run=load("vfs.tests.create_insert", "feature"))
    Feature(run=load("vfs.tests.performance", "feature"))

    if self.context.stress:
        Feature(run=load("vfs.tests.stress_insert", "feature"))


@TestModule
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Providers_AWS("1.0"))
def aws_s3(
    self,
    key_id,
    access_key,
    bucket,
    region,
    local,
    clickhouse_binary_path,
    collect_service_logs,
):
    """Setup and run aws s3 tests."""
    nodes = {
        "zookeeper": ("zookeeper1", "zookeeper2", "zookeeper3"),
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
    }

    if access_key == None:
        fail("AWS S3 access key needs to be set")
    access_key = access_key.value

    if key_id == None:
        fail("AWS S3 key id needs to be set")
    key_id = key_id.value

    if bucket == None:
        fail("AWS S3 bucket needs to be set")
    bucket = bucket.value

    if region == None:
        fail("AWS S3 region needs to be set")
    region = region.value

    uri = f"https://s3.{region}.amazonaws.com/{bucket}/data/"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key
    self.context.bucket_name = "altinity-qa-test"
    self.context.bucket_path = "data/object-storage"
    self.context.minio_enabled = False

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            use_zookeeper_nodes=True,
            configs_dir=current_dir(),
            environ={
                "S3_AMAZON_ACCESS_KEY": access_key,
                "S3_AMAZON_KEY_ID": key_id,
                "AWS_ACCESS_KEY_ID": key_id,
                "AWS_SECRET_ACCESS_KEY": access_key,
                "AWS_DEFAULT_REGION": region,
            },
        )
        self.context.cluster = cluster
        self.context.node = self.context.cluster.node("clickhouse1")
        self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]
        self.context.zk_nodes = [cluster.node(n) for n in cluster.nodes["zookeeper"]]

    Feature(run=load("vfs.tests.settings", "feature"))
    Feature(run=load("vfs.tests.table", "feature"))
    Feature(run=load("vfs.tests.ttl", "feature"))
    Feature(run=load("vfs.tests.system", "feature"))
    Feature(run=load("vfs.tests.migration", "feature"))

    Feature(run=load("vfs.tests.alter", "feature"))
    Feature(run=load("vfs.tests.replica", "feature"))
    # Feature(run=load("vfs.tests.parallel_replica", "feature"))
    Feature(run=load("vfs.tests.create_insert", "feature"))
    Feature(run=load("vfs.tests.performance", "feature"))

    if self.context.stress:
        Feature(run=load("vfs.tests.stress_insert", "feature"))


@TestModule
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Providers_GCS("1.0"))
def gcs(
    self,
    uri,
    key_id,
    access_key,
    local,
    clickhouse_binary_path,
    collect_service_logs,
):
    """Setup and run gcs tests."""
    nodes = {
        "zookeeper": ("zookeeper1", "zookeeper2", "zookeeper3"),
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
    }

    if uri == None:
        fail("GCS uri needs to be set")
    uri = uri.value
    if access_key == None:
        fail("GCS access key needs to be set")
    access_key = access_key.value
    if key_id == None:
        fail("GCS key id needs to be set")
    key_id = key_id.value

    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key
    self.context.bucket_name = "altinity-qa-test"
    self.context.bucket_path = "data/object-storage"
    self.context.minio_enabled = False

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            use_zookeeper_nodes=True,
            configs_dir=current_dir(),
            environ={"GCS_KEY_SECRET": access_key, "GCS_KEY_ID": key_id},
        )
        self.context.cluster = cluster
        self.context.node = self.context.cluster.node("clickhouse1")
        self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]
        self.context.zk_nodes = [cluster.node(n) for n in cluster.nodes["zookeeper"]]

    Feature(run=load("vfs.tests.settings", "feature"))
    Feature(run=load("vfs.tests.table", "feature"))
    Feature(run=load("vfs.tests.ttl", "feature"))
    Feature(run=load("vfs.tests.system", "feature"))
    Feature(run=load("vfs.tests.migration", "feature"))

    Feature(run=load("vfs.tests.alter", "feature"))
    Feature(run=load("vfs.tests.replica", "feature"))
    # Feature(run=load("vfs.tests.parallel_replica", "feature"))
    Feature(run=load("vfs.tests.create_insert", "feature"))
    Feature(run=load("vfs.tests.performance", "feature"))

    if self.context.stress:
        Feature(run=load("vfs.tests.stress_insert", "feature"))


@TestModule
@Name("vfs")
@ArgumentParser(argparser)
@Specifications(SRS038_ClickHouse_Disk_Object_Storage_VFS)
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
    allow_experimental_analyzer=False,
):
    """Disk Object Storage VFS regression."""

    self.context.clickhouse_version = clickhouse_version
    note(f"Clickhouse version {clickhouse_version}")
    if not allow_vfs or check_clickhouse_version("<24.2")(self):
        skip("vfs not supported on < 24.2 and requires --allow-vfs flag")
        return

    self.context.stress = stress
    self.context.allow_vfs = allow_vfs

    if storages is None:
        storages = ["minio"]

    with Given("I disable experimental analyzer if needed"):
        if check_clickhouse_version(">=24.3")(self):
            if not allow_experimental_analyzer:
                default_query_settings = getsattr(
                    current().context, "default_query_settings", []
                )
                default_query_settings.append(("allow_experimental_analyzer", 0))
        else:
            if allow_experimental_analyzer:
                default_query_settings = getsattr(
                    current().context, "default_query_settings", []
                )
                default_query_settings.append(("allow_experimental_analyzer", 1))

    if "aws_s3" in storages:
        Module(test=aws_s3)(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            bucket=aws_s3_bucket,
            region=aws_s3_region,
            key_id=aws_s3_key_id,
            access_key=aws_s3_access_key,
        )

    if "gcs" in storages:
        Module(test=gcs)(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            uri=gcs_uri,
            key_id=gcs_key_id,
            access_key=gcs_key_secret,
        )

    if "minio" in storages:
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
