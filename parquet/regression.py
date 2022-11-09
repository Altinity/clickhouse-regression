#!/usr/bin/env python3
import os
import sys
import boto3

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from s3.regression import argparser
from parquet.requirements import SRS032_ClickHouse_Parquet_Data_Format
from helpers.common import check_clickhouse_version
from parquet.tests.common import start_minio

xfails = {}

xflags = {}

ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("parquet")
@Specifications(SRS032_ClickHouse_Parquet_Data_Format)
def regression(
    self,
    local,
    clickhouse_version,
    clickhouse_binary_path,
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
    """Parquet regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    from platform import processor as current_cpu

    folder_name = os.path.basename(current_dir())
    if current_cpu() == "aarch64":
        env = f"{folder_name}_env_arm64"
    else:
        env = f"{folder_name}_env"

    with Cluster(
        local,
        clickhouse_binary_path,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:
        self.context.cluster = cluster
        nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}
        self.context.parquet_table_def = cluster.node("clickhouse1").command(
            "cat /var/lib/clickhouse/user_files/clickhouse_table_def.txt"
        ).output.strip()
        pause()

        Feature(run=load("parquet.tests.file", "feature"))
        Feature(run=load("parquet.tests.query", "feature"))

        if storages is None:
            pass

        else:
            for storage in storages:
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

                    self.context.aws_s3_bucket = aws_s3_bucket.value
                    self.context.uri = f"https://s3.{aws_s3_region.value}.amazonaws.com/{aws_s3_bucket.value}/data/parquet/"
                    self.context.access_key_id = aws_s3_key_id.value
                    self.context.secret_access_key = aws_s3_access_key.value
                    self.context.client = boto3.client(
                        "s3",
                        aws_access_key_id=self.context.access_key_id,
                        aws_secret_access_key=self.context.secret_access_key,
                    )

                elif "minio" == storage.lower():

                    self.context.uri = "http://minio1:9001/root/data/"
                    self.context.access_key_id = "minio"
                    self.context.secret_access_key = "minio123"

                    self.context.client = start_minio()

                elif "gcs" == storage.lower():
                    xfail("GCS not implemented")

                self.context.storage = storage

            Feature(run=load("parquet.tests.s3", "feature"))


if main():
    regression()
