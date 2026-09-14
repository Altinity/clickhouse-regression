#!/usr/bin/env python3
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
)
from cas.cas_mode import CAS_DISK, enable_cas_s3_cache, reset_cas_s3_cache_config


xfails = {}
ffails = {}


def argparser(parser):
    base_argparser_minio(parser)
    parser.add_argument(
        "--cas-s3-cache",
        action="store_true",
        default=False,
        dest="use_cas_s3_cache",
        help="layer a type=cache disk in front of cas_disk; cas_policy and "
        "default use the cache disk (production-shaped S3 cache; tests need "
        "no storage_policy change)",
    )


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

    if use_cas_s3_cache:
        with Given("S3 cache disk in front of the CAS disk"):
            enable_cas_s3_cache()
    else:
        with Given("no S3 cache in front of the CAS disk"):
            reset_cas_s3_cache_config()

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
            environ={
                "MINIO_ROOT_USER": minio_root_user,
                "MINIO_ROOT_PASSWORD": minio_root_password,
            },
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

    with And("enable or disable experimental analyzer if needed"):
        for node in self.context.nodes:
            experimental_analyzer(node=node, with_analyzer=with_analyzer)

    Feature(run=load("cas.tests.feature", "feature"))


if main():
    regression()
