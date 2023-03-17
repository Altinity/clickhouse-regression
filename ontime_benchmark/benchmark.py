#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from s3.regression import argparser as argparser_base

from s3.tests.common import *

xfails = {}


def argparser(parser):
    """Default argument for regressions."""
    argparser_base(parser)

    parser.add_argument(
        "--format",
        help="storage type",
        dest="format",
        type=str,
        required=False,
        default=None,
    )


@TestModule
@ArgumentParser(argparser)
@Name("benchmark")
@XFails(xfails)
def regression(
    self,
    local,
    clickhouse_version,
    clickhouse_binary_path,
    collect_service_logs,
    storages,
    stress,
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
    format,
    node="clickhouse1",
):
    """Storage Benchmark."""

    uri = None
    access_key_id = None
    secret_access_key = None
    disks = None
    policies = None
    bucket_path = "data/benchmark"

    self.context.clickhouse_version = clickhouse_version

    if storages is None:
        storages = ["minio"]

    for storage in storages:
        nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}
        with Feature(f"{storage.lower()}"):
            if "aws_s3" == storage.lower():
                with Given("I make sure the S3 credentials are set"):
                    if aws_s3_access_key == None:
                        fail("AWS S3 access key needs to be set")

                    if aws_s3_key_id == None:
                        fail("AWS S3 key id needs to be set")

                    if aws_s3_bucket == None:
                        fail("AWS S3 bucket needs to be set")

                    if aws_s3_region == None:
                        fail("AWS S3 region needs to be set")

                uri = f"https://s3.{aws_s3_region.value}.amazonaws.com/{aws_s3_bucket.value}/data/benchmark/"
                access_key_id = aws_s3_key_id.value
                secret_access_key = aws_s3_access_key.value

            elif "minio" == storage.lower():
                uri = "http://minio1:9001/root/data/benchmark/"
                access_key_id = "minio"
                secret_access_key = "minio123"
                environ = {
                    "MINIO_ROOT_PASSWORD": "minio123",
                    "MINIO_ROOT_USER": "minio",
                }

            elif "s3_gcs" == storage.lower():
                uri = gcs_uri.value
                access_key_id = gcs_key_id.value
                secret_access_key = gcs_key_secret.value

            self.context.uri = uri
            self.context.access_key_id = access_key_id
            self.context.secret_access_key = secret_access_key
            self.context.storage = storage

            from platform import processor as current_cpu

            folder_name = os.path.basename(current_dir())
            if current_cpu() == "aarch64":
                env = f"{folder_name}_env_arm64"
            else:
                env = f"{folder_name}_env"

            with Cluster(
                local,
                clickhouse_binary_path,
                collect_service_logs=collect_service_logs,
                nodes=nodes,
                docker_compose_project_dir=os.path.join(current_dir(), env),
                environ=environ,
            ) as cluster:
                self.context.cluster = cluster
                self.context.node = self.context.cluster.node(node)
                self.context.clickhouse_version = current().context.clickhouse_version

                with And("I set the nodes to use with replicated tables"):
                    nodes = cluster.nodes["clickhouse"][:2]

                with And(f"cluster nodes {nodes}"):
                    nodes = [cluster.node(name) for name in nodes]
                    self.context.nodes = nodes

                with And("I have two S3 disks configured"):
                    uri_tiered = self.context.uri + "tiered/"
                    disks = {
                        "default": {"keep_free_space_bytes": "1024"},
                        "external": {
                            "type": "s3",
                            "endpoint": f"{self.context.uri}",
                            "access_key_id": f"{self.context.access_key_id}",
                            "secret_access_key": f"{self.context.secret_access_key}",
                        },
                    }

                with And(
                    """I have a storage policy configured to use the S3 disk and a tiered
                         storage policy using both S3 disks"""
                ):
                    policies = {
                        "default": {"volumes": {"default": {"disk": "default"}}},
                        "external": {"volumes": {"external": {"disk": "external"}}},
                        "tiered": {
                            "volumes": {
                                "default": {"disk": "default"},
                                "external": {"disk": "external"},
                            }
                        },
                    }

                with s3_storage(disks, policies):
                    Feature(test=load("ontime_benchmark.tests.benchmark", "feature"))(
                        format=format
                    )


if main():
    regression()
