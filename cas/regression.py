#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import (
    argparser_minio as base_argparser_minio,
    CaptureClusterArgs,
    CaptureMinioArgs,
)
from helpers.common import (
    experimental_analyzer,
    getuid,
)
from cas.cas_mode import (
    CAS_DISK,
    enable_cas_aws_storage,
    enable_cas_minio_disk,
)
from cas.tests.steps.disk import AWS_S3_DISK_PREFIX, CAS_POLICY_POOL, cas_endpoint
from cas.tests.steps.pool import cleanup_cas_storage, configure_cas_mc_alias


xfails = {}
ffails = {}


def argparser(parser):
    base_argparser_minio(parser)
    parser.add_argument(
        "--cas-s3-cache",
        action="store_true",
        default=False,
        dest="use_cas_s3_cache",
        help="layer a type=cache disk in front of cas_disk; cas_policy uses "
        "the cache disk (production-shaped S3 cache; tests keep "
        "storage_policy = 'cas_policy'). The default policy stays local.",
    )
    parser.add_argument(
        "--storage",
        choices=["minio", "aws_s3"],
        default="minio",
        dest="storage",
        help="object store for CAS disks (default: minio)",
    )
    parser.add_argument(
        "--aws-s3-bucket",
        type=Secret(name="aws_s3_bucket"),
        default=os.getenv("S3_AMAZON_BUCKET") or os.getenv("AWS_S3_BUCKET"),
        dest="aws_s3_bucket",
        help="AWS S3 bucket for --storage aws_s3",
    )
    parser.add_argument(
        "--aws-s3-region",
        type=Secret(name="aws_s3_region"),
        default=os.getenv("AWS_DEFAULT_REGION"),
        dest="aws_s3_region",
        help="AWS region for --storage aws_s3",
    )
    parser.add_argument(
        "--aws-s3-key-id",
        type=Secret(name="aws_s3_key_id"),
        default=os.getenv("AWS_ACCESS_KEY_ID"),
        dest="aws_s3_key_id",
        help="AWS access key id for --storage aws_s3",
    )
    parser.add_argument(
        "--aws-s3-access-key",
        type=Secret(name="aws_s3_access_key"),
        default=os.getenv("AWS_SECRET_ACCESS_KEY"),
        dest="aws_s3_access_key",
        help="AWS secret access key for --storage aws_s3",
    )


def _secret_value(value):
    if value is None:
        return None
    return value.value if hasattr(value, "value") else value


@TestModule
@Name("cas")
@FFails(ffails)
@XFails(xfails)
@ArgumentParser(argparser)
@CaptureClusterArgs
@CaptureMinioArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
    minio_args=None,
    use_cas_s3_cache=False,
    storage="minio",
    aws_s3_bucket=None,
    aws_s3_region=None,
    aws_s3_key_id=None,
    aws_s3_access_key=None,
):
    """Run tests for content-addressed storage."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    minio_root_user = minio_args["minio_root_user"].value
    minio_root_password = minio_args["minio_root_password"].value
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password
    self.context.use_cas_s3_cache = False
    self.context.cas_disk_name = CAS_DISK
    self.context.storage = storage
    self.context.cas_access_key = minio_root_user
    self.context.cas_secret_key = minio_root_password
    self.context.cas_endpoint_host = "http://minio:9000"
    self.context.cas_bucket = "warehouse"
    self.context.cas_root_prefix = "cas"
    self.context.cas_region = None
    self.context.cas_mc_alias = "minio"

    if storage == "aws_s3":
        bucket = _secret_value(aws_s3_bucket)
        region = _secret_value(aws_s3_region)
        key_id = _secret_value(aws_s3_key_id)
        access_key = _secret_value(aws_s3_access_key)
        if not all((bucket, region, key_id, access_key)):
            fail(
                "--storage aws_s3 needs --aws-s3-bucket, --aws-s3-region, "
                "--aws-s3-key-id and --aws-s3-access-key"
            )

        self.context.cas_access_key = key_id
        self.context.cas_secret_key = access_key
        self.context.cas_endpoint_host = f"https://s3.{region}.amazonaws.com"
        self.context.cas_bucket = bucket
        self.context.cas_root_prefix = f"cas_reg_{getuid()}"
        self.context.cas_region = region
        self.context.cas_mc_alias = "aws"

        with Given("CAS disks on AWS S3"):
            enable_cas_aws_storage(
                s3_endpoint=cas_endpoint(self, AWS_S3_DISK_PREFIX),
                cas_endpoint=cas_endpoint(self, CAS_POLICY_POOL),
                region=region,
                with_cache=use_cas_s3_cache,
            )
    else:
        with Given("named CAS disk endpoint"):
            enable_cas_minio_disk(
                endpoint=cas_endpoint(self, CAS_POLICY_POOL),
                with_cache=use_cas_s3_cache,
            )

    cluster_environ = {
        "MINIO_ROOT_USER": minio_root_user,
        "MINIO_ROOT_PASSWORD": minio_root_password,
    }
    if storage == "aws_s3":
        cluster_environ["CAS_ACCESS_KEY_ID"] = self.context.cas_access_key
        cluster_environ["CAS_SECRET_ACCESS_KEY"] = self.context.cas_secret_key

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
            environ=cluster_environ,
        )
        self.context.cluster = cluster

    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node2 = self.context.cluster.node("clickhouse2")
    self.context.node3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.node,
        self.context.node2,
        self.context.node3,
    ]

    if storage == "aws_s3":
        with And("mc alias for the AWS bucket"):
            configure_cas_mc_alias(
                cluster=cluster,
                alias="aws",
                endpoint=self.context.cas_endpoint_host,
                access_key=self.context.cas_access_key,
                secret_key=self.context.cas_secret_key,
            )

    with And("enable or disable experimental analyzer if needed"):
        for node in self.context.nodes:
            experimental_analyzer(node=node, with_analyzer=with_analyzer)

    Feature(run=load("cas.tests.feature", "feature"))

    with Finally("clean up CAS pool data from object storage"):
        cleanup_cas_storage()


if main():
    regression()
