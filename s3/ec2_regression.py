#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as argparser_base

from s3.requirements import *


def argparser(parser):
    """Default argument for ec2 regressions."""
    argparser_base(parser)

    parser.add_argument(
        "--uri",
        type=str,
        action="store",
        help="set url for the aws connection",
        default=None,
    )

    parser.add_argument(
        "--region",
        type=str,
        action="store",
        help="set region for the aws connection",
        default=None,
    )

    parser.add_argument(
        "--session-token",
        type=str,
        action="store",
        help="set session token for the aws connection",
        default=None,
    )

    parser.add_argument(
        "--key-id",
        type=str,
        action="store",
        help="aws s3 key id",
        default=None,
    )

    parser.add_argument(
        "--access-key",
        type=str,
        action="store",
        help="aws s3 access key",
        default=None,
    )


xfails = {}


@TestModule
@ArgumentParser(argparser)
@Name("ec2")
@Requirements(RQ_SRS_015_S3("1.0"))
@XFails(xfails)
def regression(
    self, local, clickhouse_path, uri, access_key, key_id, session_token, region
):
    """S3 Storage regression."""
    if aws_s3_access_key == None:
        fail("AWS S3 access key needs to be set")
    if aws_s3_key_id == None:
        fail("AWS S3 key id needs to be set")

    with Cluster(
        local,
        clickhouse_path,
        nodes=nodes,
        environ={
            "S3_AMAZON_ACCESS_KEY": access_key,
            "S3_AMAZON_KEY_ID": key_id,
            "AWS_REGION": region,
            "AWS_SESSION_TOKEN": session_token,
        },
    ) as cluster:
        self.context.cluster = cluster

        with Given("I make sure the AWS credentials are set"):
            assert os.getenv(
                "AWS_ACCESS_KEY_ID", None
            ), "AWS_ACCESS_KEY_ID env variable must be defined"
            assert os.getenv(
                "AWS_SECRET_ACCESS_KEY", None
            ), "AWS_SECRET_ACCESS_KEY env variable must be defined"
            assert os.getenv(
                "AWS_SESSION_TOKEN", None
            ), "AWS_SESSION_TOKEN env variable must be defined"
            assert os.getenv(
                "AWS_REGION", None
            ), "AWS_REGION env variable must be defined"

        Feature(run=load("s3.tests.ec2", "feature"))


if main():
    regression()
