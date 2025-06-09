#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.common import experimental_analyzer
from helpers.argparser import argparser_minio, CaptureClusterArgs, CaptureMinioArgs
from helpers.create_clusters import add_clusters_for_nodes, get_clusters_for_nodes
from s3.tests.common import start_minio

from requirements.requirements import *


xfails = {}
ffails = {}


@TestFeature
@Name("S3 Table Engine")
def s3_table_engine(
    self,
    uri,
    root_user,
    root_password,
    cluster_args,
    with_analyzer=False,
):
    """Setup and run S3 Table Engine tests."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    root_user = root_user.value
    root_password = root_password.value
    uri = uri.value

    self.context.access_key_id = root_user
    self.context.secret_access_key = root_password
    bucket_prefix = "data"

    with Cluster(
        **cluster_args,
        nodes=nodes,
        environ={"MINIO_ROOT_PASSWORD": root_password, "MINIO_ROOT_USER": root_user},
    ) as cluster:
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

        with Given("I have a minio client"):
            start_minio(access_key=root_user, secret_key=root_password)
            start_minio(
                access_key=root_user, secret_key=root_password, uri="localhost:9002"
            )
            uri_bucket_file = (
                uri + f"/{self.context.cluster.minio_bucket}/{bucket_prefix}/"
            )
            uri_bucket_file_readonly = (
                "http://minio_readonly:9002"
                + f"/{self.context.cluster.minio_bucket}/{bucket_prefix}/"
            )
            self.context.bucket_name = self.context.cluster.minio_bucket

        Feature(test=load("hive_partitioning.tests.writes_feature", "feature"))(
            uri=uri_bucket_file,
            uri_readonly=uri_bucket_file_readonly,
            minio_root_user=root_user,
            minio_root_password=root_password,
        )


@TestModule
@Name("hive partitioning")
@ArgumentParser(argparser_minio)
@Specifications(SRS_045_Hive_Partitioning)
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
@CaptureMinioArgs
def regression(
    self,
    cluster_args: dict,
    minio_args: dict,
    clickhouse_version: str,
    stress=False,
    with_analyzer=False,
):
    """Hive Partitioning regression."""

    self.context.clickhouse_version = clickhouse_version
    self.context.stress = stress
    self.context.with_analyzer = with_analyzer
    Feature(test=s3_table_engine)(
        cluster_args=cluster_args,
        uri=minio_args["minio_uri"],
        root_user=minio_args["minio_root_user"],
        root_password=minio_args["minio_root_password"],
        with_analyzer=with_analyzer,
    )


if main():
    regression()
