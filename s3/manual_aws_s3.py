#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as base_argparser

from s3.requirements import *


def argparser(parser):
    """Default argument for manual AWS S3 storage regression."""
    base_argparser(parser)

    parser.add_argument(
        "--aws-s3-bucket",
        type=str,
        action="store",
        help="set AWS S3 bucket name",
        default="altinity-qa-test",
    )

    parser.add_argument(
        "--aws-s3-region",
        type=str,
        action="store",
        help="set aws region for the aws connection",
        default="us-west-2",
    )

    parser.add_argument(
        "--aws-s3-default-region",
        type=str,
        action="store",
        help="set AWS default region for S3 bucket",
        default="us-west-2",
    )

    parser.add_argument(
        "--aws-s3-arn",
        type=str,
        action="store",
        help="set AWS S3 ARN",
        default="arn:aws:iam::407099639081:role/qa-test",
    )


xfails = {}


@TestModule
@ArgumentParser(argparser)
@Name("manual aws s3")
@Requirements()
@XFails(xfails)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    stress,
    aws_s3_bucket,
    aws_s3_region,
    aws_s3_default_region,
    aws_s3_arn,
):
    """Manual tests for AWS S3 Storage regression."""

    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    with Given("I obtain web identity token"):
        with By(
            "obtaining dex password from 1password",
            description="""
                PASSWORD_FROM_1PASSWORD= from https://altinity.1password.com/vaults/bb6ymhqucqxmqrendlfdabwqwa/allitems/ids64yb7viyxsw6jgw3bkar4ui
                """,
        ):
            pass

        with And(
            "installing smallstep", description="""from https://smallstep.com/cli/"""
        ):
            pass

        with And(
            "obtaining web identity token",
            description="""
                 Using the following command:

                 step oauth --client-id qa-test --client-secret $PASSWORD_FROM_1PASSWORD --provider https://dex.dev.altinity.cloud --listen localhost:8000 --oidc --bare --scope=openid --scope=profile --scope=email > token
                 """,
        ):
            aws_s3_web_identity_token = input("enter AWS S3 web identity token")

    with Cluster(
        local,
        clickhouse_binary_path,
        nodes=nodes,
    ) as cluster:
        self.context.cluster = cluster
        self.context.aws_s3_bucket = aws_s3_bucket
        self.context.aws_s3_region = aws_s3_region
        self.context.aws_s3_default_region = aws_s3_default_region
        self.context.aws_s3_arn = aws_s3_arn
        self.context.aws_s3_web_identity_token = aws_s3_web_identity_token

        Feature(run=load("s3.tests.iam_auth", "feature"))


if main():
    regression()
