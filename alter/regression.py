#!/usr/bin/env python3
import os
import sys
import boto3


from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from s3.regression import argparser
from alter.table.requirements.replace_partition import *
from helpers.datatypes import *


xfails = {
    "/alter/replace partition/between temporary and regular tables": [
        (
            Fail,
            "Temporary table gets deleted before we can insert data, needs to be fixed in tests",
        )
    ],
    "/alter/replace partition/between temporary tables": [
        (
            Fail,
            "Temporary table gets deleted before we can insert data, needs to be fixed in tests",
        )
    ],
}

xflags = {}

ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition("1.0"))
@Name("alter")
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
    node="clickhouse1",
):
    """Alter regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    with Cluster(
        local,
        clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        nodes=nodes,
    ) as cluster:
        self.context.cluster = cluster

        Feature(run=load("alter.table.tests.replace_partition.feature", "feature"))


if main():
    regression()
