#!/usr/bin/env python3
import os
import sys
import boto3

from minio import Minio
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from s3.regression import argparser
from parquet.requirements import *
from helpers.tables import Column, generate_all_column_types
from helpers.datatypes import *
from parquet.tests.common import start_minio, parquet_test_columns

xfails = {
    "chunked array": [(Fail, "Not supported")],
    "gcs": [(Fail, "Not implemented")]
}

xflags = {}

ffails = {
    "/parquet/compression/brotli": (
        Skip,
        "Not implemented before 23.3",
        check_clickhouse_version("<23.3"),
    ),
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("parquet")
@Specifications(SRS032_ClickHouse_Parquet_Data_Format)
@Requirements(RQ_SRS_032_ClickHouse_Parquet("1.0"))
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
        collect_service_logs=collect_service_logs,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:

        with Given("I have a Parquet table definition"):
            self.context.cluster = cluster
            columns = (
                cluster.node("clickhouse1")
                .command("cat /var/lib/test_files/clickhouse_table_def.txt")
                .output.strip()
                .split(".")
            )
            self.context.parquet_table_columns = []
            for column in columns:
                name, datatype = column.split(" ", 1)
                self.context.parquet_table_columns.append(
                    Column(datatype=eval(datatype), name=name)
                )

        with And("I check that common code provides all necessary data types"):
            columns = generate_all_column_types(include=parquet_test_columns())
            datatypes = [type(column.datatype) for column in columns]
            for datatype in [
                UInt8,
                Int8,
                UInt16,
                UInt32,
                UInt64,
                Int16,
                Int32,
                Int64,
                Float32,
                Float64,
                Date,
                DateTime,
                String,
                Decimal128,
                Array,
                Tuple,
                Map,
                Nullable,
                LowCardinality,
            ]:
                assert datatype in datatypes, fail(
                    f"Common code did not provide {datatype}"
                )

        with Pool(2) as executor:
            Feature(
                run=load("parquet.tests.file", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.query", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.int_list_multiple_chunks", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.url", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.mysql", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.postgresql", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.remote", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.chunked_array", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.broken", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.encoding", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.compression", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.datatypes", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.complex_datatypes", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.indexing", "feature"),
                parallel=True,
                executor=executor,
            )
            Feature(
                run=load("parquet.tests.cache", "feature"),
                parallel=True,
                executor=executor,
            )
            join()

        if storages is None:
            pass

        else:
            if "aws_s3" in storages:
                with Given("I make sure the S3 credentials are set"):

                    if aws_s3_access_key == None:
                        fail("AWS S3 access key needs to be set")

                    if aws_s3_key_id == None:
                        fail("AWS S3 key id needs to be set")

                    if aws_s3_bucket == None:
                        fail("AWS S3 bucket needs to be set")

                    if aws_s3_region == None:
                        fail("AWS S3 region needs to be set")

                self.context.storage = "aws_s3"
                self.context.aws_s3_bucket = aws_s3_bucket.value
                self.context.uri = f"https://s3.{aws_s3_region.value}.amazonaws.com/{aws_s3_bucket.value}/data/parquet/"
                self.context.access_key_id = aws_s3_key_id.value
                self.context.secret_access_key = aws_s3_access_key.value
                self.context.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=self.context.access_key_id,
                    aws_secret_access_key=self.context.secret_access_key,
                )
                with Feature("aws s3"):
                    Feature(run=load("parquet.tests.s3", "feature"))

            if "minio" in storages:

                self.context.storage = "minio"
                self.context.uri = "http://minio:9001/root/data/parquet/"
                self.context.access_key_id = "minio"
                self.context.secret_access_key = "minio123"

                with Given("I have a minio client"):
                    start_minio(access_key="minio", secret_key="minio123")

                with Feature("minio"):
                    Feature(run=load("parquet.tests.s3", "feature"))

            if "gcs" in storages:
                with Feature("gcs"):
                    fail("GCS not implemented")    


if main():
    regression()
