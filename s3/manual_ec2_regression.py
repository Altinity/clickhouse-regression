#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser

from s3.requirements import *

xfails = {}


@TestModule
@ArgumentParser(argparser)
@Name("s3")
@Requirements(RQ_SRS_015_S3("1.0"))
@XFails(xfails)
def regression(self, local, clickhouse_binary_path, aws_s3_access_key, aws_s3_key_id):
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    with Cluster(
        local,
        clickhouse_binary_path,
        nodes=nodes,
        environ={
            "S3_AMAZON_ACCESS_KEY": aws_s3_access_key,
            "S3_AMAZON_KEY_ID": aws_s3_key_id,
        },
    ) as cluster:
        self.context.cluster = cluster
        Scenario(run=load("s3.tests.manual_ec2", "feature"), flags=TE)


if main():
    regression()
