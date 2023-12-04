#!/usr/bin/env python3
import os
import sys
import boto3

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from s3.regression import argparser
from alter.requirements.requirements import *
from helpers.datatypes import *

xfails = {
    "/alter/replace partition/concurrent merges and mutations/mutations on unrelated partition": [
        (
            Fail,
            "The pr is not done yet: https://github.com/ClickHouse/ClickHouse/pull/54272",
        )
    ],
    "/alter/replace partition/concurrent merges and mutations/merges on unrelated partition/that the merge was finished": [
        (
            Fail,
            "The pr is not done yet: https://github.com/ClickHouse/ClickHouse/pull/54272",
        )
    ],
    "/alter/replace partition/concurrent actions/one replace partition/fetch partition from * table": [
        (
            Fail,
            "Sometimes fails with the reason that the partition already fetched",
        )
    ],
    "/alter/replace partition/concurrent actions/one replace partition/freeze * partition with name": [
        (
            Fail,
            "Sometimes fails with the reason that the partition already frozen",
        )
    ],
    "/alter/replace partition/storage/replace partition on minio and default disks/pattern #1": [
        (
            Fail,
            "Replacing partition when two tables have different structures is expected to fail",
        )
    ],
    "/alter/replace partition/storage/replace partition on minio and default disks/pattern #2": [
        (
            Fail,
            "Replacing partition when two tables have different structures is expected to fail",
        )
    ],
    "/alter/replace partition/storage/replace partition on tiered and default storages/pattern #1": [
        (
            Fail,
            "Replacing partition when two tables have different structures is expected to fail",
        )
    ],
    "/alter/replace partition/storage/replace partition on tiered and default storages/pattern #2": [
        (
            Fail,
            "Replacing partition when two tables have different structures is expected to fail",
        )
    ],
}

xflags = {}

ffails = {
    "/alter/replace partition/temporary table": (
        Skip,
        "Not implemented before 23.5",
        check_clickhouse_version("<23.5"),
    ),
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Specifications(SRS032_ClickHouse_Alter)
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
    self.context.storage = "minio"
    self.context.uri = "http://minio:9001/root/data/alter"
    self.context.access_key_id = "minio"
    self.context.secret_access_key = "minio123"

    with Cluster(
        local,
        clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        nodes=nodes,
    ) as cluster:
        self.context.cluster = cluster

        Feature(run=load("alter.table.replace_partition.feature", "feature"))


if main():
    regression()
