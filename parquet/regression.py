#!/usr/bin/env python3
import os
import sys
import boto3

from minio import Minio
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from s3.regression import argparser
from parquet.requirements import *
from helpers.tables import Column, generate_all_column_types
from helpers.datatypes import *
from helpers.common import experimental_analyzer
from parquet.tests.common import start_minio, parquet_test_columns


xfails = {
    "chunked array": [(Fail, "Not supported")],
    "gcs": [(Fail, "Not implemented")],
    "/parquet/encoding/dictionary/*": [
        (Fail, "datetime different on export and import, that needs to be investigated")
    ],
    "/parquet/encoding/plain/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/complex/nestedstruct/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/complex/largestruct3/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/compression/snappyplain/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/datatypes/manydatatypes/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/datatypes/timestamp?/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/datatypes/json/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/datatypes/arrowtimestamp/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/datatypes/arrowtimestampms/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/datatypes/stringtypes/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/encoding/plainrlesnappy/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/datatypes/negativeint64/*": [
        (Fail, "datetime different on export and import, needs to be investigated")
    ],
    "/parquet/datatypes/nameswithemoji/*": [
        (
            Fail,
            "DB::Exception: Expected not empty name: While processing ``: While processing SELECT `önë`, ``, `🦆` FROM file",
        )
    ],
    "/parquet/compression/snappyrle/*": [
        (
            Fail,
            "Getting an error that encoding is not supported. Probably error "
            "occurs because of Delta Encoding (DELTA_BINARY_PACKED)",
        )
    ],
    "/parquet/complex/largestruct/*": [
        (
            Fail,
            "Getting an error that encoding is not supported. Probably error "
            "occurs because of Delta Encoding (DELTA_BINARY_PACKED)",
        )
    ],
    "/parquet/datatypes/decimalwithfilter2/*": [
        (
            Fail,
            "Getting an error that encoding is not supported. error "
            "occurs because of Delta Encoding (DELTA_BINARY_PACKED)",
        )
    ],
    "/parquet/datatypes/sparkv2?/*": [
        (
            Fail,
            "Getting an error that encoding is not supported. error "
            "occurs because of Delta Encoding (DELTA_BINARY_PACKED)",
        )
    ],
    "/parquet/datatypes/h2oai/*": [
        (
            Fail,
            "Nullable(String) turns into LowCardinality(Nullable(String)) after import -> export process",
        )
    ],
    "/parquet/complex/tuplewithdatetime/*": [
        (
            Fail,
            "Getting an error that encoding is not supported. error "
            "occurs because of Delta Encoding (DELTA_BINARY_PACKED)",
        )
    ],
    "/parquet/encoding/deltabytearray?/*": [
        (
            Fail,
            "Getting an error that encoding is not supported. error "
            "occurs because of DELTA_BYTE_ARRAY encoding",
        )
    ],
    "/parquet/encoding/deltalengthbytearray/*": [
        (
            Fail,
            "Getting an error that encoding is not supported. error "
            "occurs because of DELTA_LENGTH_BYTE_ARRAY encoding",
        )
    ],
    "/parquet/encoding/rleboolean/*": [
        (
            Fail,
            "Getting an error that encoding is not supported.",
        )
    ],
    "/parquet/datatypes/large string map": [
        (
            Fail,
            "Will fail until the, https://github.com/apache/arrow/pull/35825, gets merged.",
        )
    ],
    "/parquet/rowgroups/*": [
        (
            Fail,
            "Needs Investigation. The issue seems to be from the tests side, not a bug.",
        )
    ],
    "/parquet/fastparquet/*": [
        (
            Fail,
            "Needs Investigation. The issue seems to be from the tests side, not a bug.",
        )
    ],
    "/parquet/postgresql/compression type/*/postgresql engine to parquet file to postgresql engine": [
        (
            Fail,
            "This fails because of the difference in snapshot values. We used to capture the datetime value `0` be "
            "converted as 2106-02-07 06:28:16 instead of the correct 1970-01-01 01:00:00. But when steps are "
            "repeated manually, we can not reproduce it",
        )
    ],
    "/parquet/*/s3/compression type/*/outline/engine/*": [
        (
            Fail,
            "Fails with the error `could not be decoded`, we will attach the ticket to the xfail",
        )
    ],
    "/parquet/read and write/read and write parquet file/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/59330",
        )
    ],
}
xflags = {}

ffails = {
    "/parquet/compression/brotli": (
        Skip,
        "Not implemented before 23.3",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/*/*/insert into function auto cast types/*": (
        Skip,
        "Datatype issues before 23.3",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/*/*/select from function auto cast types/*": (
        Skip,
        "Datatype issues before 23.3",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/*/*/select from function manual cast types/*": (
        Skip,
        "Datatype issues before 23.3",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/aws s3/s3/*/function/select from function manual cast types/*": (
        Skip,
        "Datatype issues before 23.3",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/broken/*": (
        Skip,
        "Different error messages on 23.6 and above",
        check_clickhouse_version(">=23.6"),
    ),
    "/parquet/encrypted/": (
        Skip,
        "Different error message on 23.8 and above",
        check_clickhouse_version("<=24.3"),
    ),
    "/parquet/compression/*": (
        Skip,
        "Different on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/boolean": (
        Skip,
        "Different on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/columnwithnull2": (
        Skip,
        "Different on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/enum*": (
        Skip,
        "Different on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/nameswithemoji": (
        Skip,
        "Different on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/nandouble": (
        Skip,
        "Different on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/manydatatypes*": (
        Skip,
        "Different on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/fixedstring": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/supporteduuid": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/int32": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/struct": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/complex/tupleofnulls": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/complex/nestedstruct*": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/complex/nestedallcomplex": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/complex/nested map": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/complex/largestruct2": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/complex/complex null": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/complex/big tuple with nulls": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/complex/arraystring": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/complex/bytearraydictionary": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/*/s3/compression type/*/engine/engine to file to engine/": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/*/s3/compression type/*/function/insert into function/": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/datatypes/string int list inconsistent offset multiple batches": (
        Skip,
        "The fix not implemented yet",
        check_clickhouse_version("<23.13"),
    ),
    "/parquet/aws s3/s3/compression type/=NONE /engine/insert into engine": (
        Skip,
        "Unsupported on 22.8",
        check_clickhouse_version("<23.3"),
    ),
    "/parquet/glob/glob with multiple elements": (
        Skip,
        "Multi directory globs are not introduced for these versions",
        check_clickhouse_version("<23.8"),
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
    allow_vfs=False,
    with_analyzer=False,
):
    """Parquet regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if check_clickhouse_version("<23.3")(self):
        pool = 2
        parallel = NO_PARALLEL
    else:
        pool = 4
        parallel = PARALLEL

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(
                node=cluster.node(node), with_analyzer=with_analyzer
            )

    with And("I have a Parquet table definition"):
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

        check_datatypes = [
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
            Array,
            Tuple,
            Map,
            Nullable,
            LowCardinality,
            Decimal128,
        ]

        for datatype in check_datatypes:
            assert datatype in datatypes, fail(
                f"Common code did not provide {datatype}"
            )

    with Pool(pool) as executor:
        Feature(
            run=load("parquet.tests.file", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.query", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.int_list_multiple_chunks", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.url", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.mysql", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.postgresql", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.remote", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.chunked_array", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.broken", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.encoding", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.compression", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.datatypes", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.complex_datatypes", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.indexing", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.cache", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.glob", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.rowgroups", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.encrypted", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.fastparquet", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
        )
        Feature(
            run=load("parquet.tests.read_and_write", "feature"),
            parallel=True,
            executor=executor,
            flags=parallel,
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
