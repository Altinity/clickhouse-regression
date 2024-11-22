#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.tables import *
from helpers.argparser import argparser as argparser_base, CaptureClusterArgs
from helpers.cluster import create_cluster, Cluster
from helpers.common import experimental_analyzer


def argparser(parser):
    """Default argument for regressions."""
    argparser_base(parser)

    parser.add_argument(
        "--aws-s3-bucket",
        action="store",
        help="set bucket for the aws connection",
        type=Secret(name="aws_s3_bucket"),
        default=os.getenv("S3_AMAZON_BUCKET"),
    )

    parser.add_argument(
        "--aws-s3-region",
        action="store",
        help="set aws region for the aws connection",
        type=Secret(name="aws_s3_region"),
        default=os.getenv("AWS_DEFAULT_REGION"),
    )

    parser.add_argument(
        "--aws-s3-key-id",
        action="store",
        help="aws s3 key id",
        type=Secret(name="aws_s3_key_id"),
        default=os.getenv("AWS_ACCESS_KEY_ID"),
    )

    parser.add_argument(
        "--aws-s3-access-key",
        action="store",
        help="aws s3 access key",
        type=Secret(name="aws_s3_access_key"),
        default=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


xfails = {}
ffails = {
    "/data lakes": (
        Skip,
        "Under development",
    ),
}


@TestModule
@Name("datalakes")
@ArgumentParser(argparser)
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    aws_s3_bucket=None,
    aws_s3_region=None,
    aws_s3_key_id=None,
    aws_s3_access_key=None,
    with_analyzer=False,
):
    """Pass."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version
    self.context.stress = stress

    # if aws_s3_access_key == None:
    #     fail("AWS S3 access key needs to be set")
    # aws_s3_access_key = aws_s3_access_key.value

    # if aws_s3_key_id == None:
    #     fail("AWS S3 key id needs to be set")
    # aws_s3_key_id = aws_s3_key_id.value

    # if aws_s3_bucket == None:
    #     fail("AWS S3 bucket needs to be set")
    # aws_s3_bucket = aws_s3_bucket.value

    # if aws_s3_region == None:
    #     fail("AWS S3 region needs to be set")
    # aws_s3_region = aws_s3_region.value

    bucket_prefix = "data"

    # uri = f"https://s3.{aws_s3_region}.amazonaws.com/{aws_s3_bucket}/{bucket_prefix}/"

    # self.context.storage = "aws_s3"
    # self.context.access_key_id = aws_s3_key_id
    # self.context.secret_access_key = aws_s3_access_key
    # self.context.bucket_name = aws_s3_bucket
    # self.context.region = aws_s3_region

    with Cluster(
        **cluster_args,
        nodes=nodes,
    ) as cluster:
        self.context.cluster = cluster
        # self.context.cluster.bucket = aws_s3_bucket
        self.context.node = cluster.node("clickhouse1")

        with Given("I enable or disable experimental analyzer if needed"):
            for node in nodes["clickhouse"]:
                experimental_analyzer(
                    node=cluster.node(node), with_analyzer=with_analyzer
                )

        # Feature(run=load("datalakes.tests.check_healthy", "feature"))
        # Feature(run=load("datalakes.tests.delta_lake", "feature"))
        Feature(run=load("datalakes.tests.iceberg", "feature"))


if main():
    regression()
