#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.common import experimental_analyzer
from helpers.argparser import argparser as argparser_base, CaptureClusterArgs
from s3.tests.common import *

from s3.requirements import SRS_015_ClickHouse_S3_External_Storage


def argparser(parser):
    """Default argument for regressions."""
    argparser_base(parser)

    parser.add_argument(
        "--storage",
        action="append",
        help="select which storage types to run tests with",
        choices=["minio", "aws_s3", "gcs", "local"],
        default=None,
        dest="storages",
    )

    parser.add_argument(
        "--minio-uri",
        action="store",
        help="set url for the minio connection",
        type=Secret(name="minio_uri"),
        default="http://minio1:9001",
    )

    parser.add_argument(
        "--minio-root-user",
        action="store",
        help="minio root user name (access key id)",
        type=Secret(name="minio_root_user"),
        default="minio_user",
    )

    parser.add_argument(
        "--minio-root-password",
        action="store",
        help="minio root user password (secret access key)",
        type=Secret(name="minio_root_password"),
        default="minio123",
    )

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

    parser.add_argument(
        "--gcs-uri",
        action="store",
        help="set url for the gcs connection",
        type=Secret(name="gcs_uri"),
        default=os.getenv("GCS_URI"),
    )

    parser.add_argument(
        "--gcs-key-id",
        action="store",
        help="gcs key id",
        type=Secret(name="gcs_key_id"),
        default=os.getenv("GCS_KEY_ID"),
    )

    parser.add_argument(
        "--gcs-key-secret",
        action="store",
        help="gcs key secret",
        type=Secret(name="gcs_key_secret"),
        default=os.getenv("GCS_KEY_SECRET"),
    )


xfails = {
    ":/disk/generic url": [(Fail, "not yet supported")],
    ":/:/remote host filter": [
        (Fail, "remote host filter does not work with disk storage")
    ],
    "gcs/disk invalid/:": [
        (Fail, "Google Cloud Storage does not work with disk storage")
    ],
    ":/zero copy replication/alter/count=10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22516")
    ],
    ":/zero copy replication/ttl move": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22679")
    ],
    ":/zero copy replication/ttl delete": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22679")
    ],
    ":/zero copy replication/delete": [
        (Fail, "test is slow to clean up, needs investigation")
    ],
    ":/zero copy replication/:mutation/:/the size of the s3 bucket:": [
        (Fail, "test doesn't clean up, needs investigation")
    ],
    "minio/backup/:/alter freeze": [(Fail, "External disks do not create backups")],
    "minio/disk/environment credentials/:": [
        (Fail, "AWS S3 credentials not set for minio tests.")
    ],
    "minio/disk/log/:": [(Fail, "Not working 22.X", check_clickhouse_version("<=23"))],
    "aws s3/disk/:/:/:the size of the s3 bucket*": [(Fail, "fails on runners")],
    "aws s3/disk/:/:the size of the s3 bucket*": [(Fail, "fails on runners")],
    "aws s3/backup/:/:/:/the size of the s3 bucket*": [(Fail, "needs review")],
    "gcs/disk/environment credentials/:": [
        (Fail, "AWS S3 credentials not set for gcs tests.")
    ],
    ":/backup/:/metadata non restorable schema": [
        (Fail, "send_metadata is deprecated")
    ],
    ":/zero copy replication/the bucket should be cleaned up": [
        (Fail, "Data cleanup needs investigation")
    ],
    "aws s3/backup/:/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/30510")
    ],
    "minio/zero copy replication/performance alter": [
        (Error, "Unstable test"),
        (Fail, "Unstable test"),
    ],
    "minio/zero copy replication/performance select": [
        (Error, "Unstable test"),
        (Fail, "Unstable test"),
    ],
    "aws s3/zero copy replication/stale alter replica": [
        (Error, "Timeout on 22.x", check_clickhouse_version("<=23"))
    ],
    "gcs/table function/wildcard/:": [
        (Fail, "Fixed by https://github.com/ClickHouse/ClickHouse/pull/37344")
    ],
    ":/disk/delete/delete one row": [(Fail, "Bug that needs to be investigated")],
    "gcs/disk/delete/gcs truncate err log": [
        (Fail, "Exception appears in error log but not in ClickHouse.")
    ],
    "aws s3/table function/ssec/:": [
        (Fail, "https://altinity.atlassian.net/browse/CH-241")
    ],
    "aws s3/table function/ssec/:/:": [
        (Fail, "https://altinity.atlassian.net/browse/CH-241")
    ],
    "aws s3/table function/ssec encryption check": [
        (Fail, "https://altinity.atlassian.net/browse/CH-242")
    ],
    ":/table function performance/wildcard/:": [
        (
            Error,
            "https://github.com/ClickHouse/ClickHouse/pull/62120",
            check_clickhouse_version("<24.5"),
        )
    ],
    ":/disk/low cardinality offset": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/pull/44875")
    ],
    ":/zero copy replication/bad detached part": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/pull/58333",
            check_clickhouse_version("<23.11"),
        )
    ],
    ":/alter/:/projection": [
        (Fail, "Wrong error message 22.3", check_clickhouse_version("<22.8")),
    ],
    ":/alter/zero copy encrypted/:": [
        (
            Fail,
            "Bug in 23.3 https://github.com/ClickHouse/ClickHouse/pull/68821",
            check_clickhouse_version("<23.8"),
        ),
    ],
    ":/table function/measure file size": [
        (Fail, "Not implemented <24", check_clickhouse_version("<24"))
    ],
    ":/combinatoric table/:": [(Fail, "Unstable test")],
    ":/invalid table function/invalid region": [
        (Error, "https://github.com/ClickHouse/ClickHouse/issues/59084")
    ],
    ":/invalid table function/invalid path": [
        (
            Error,
            "https://github.com/ClickHouse/ClickHouse/issues/59084",
            check_clickhouse_version(">=24.9"),
        )
    ],
}

ffails = {
    "minio/disk/environment credentials": (
        Skip,
        "AWS S3 credentials not set for minio tests.",
    ),
    "gcs/disk/environment credentials": (
        Skip,
        "AWS S3 credentials not set for gcs tests.",
    ),
    "gcs/zero copy replication": (
        Skip,
        "GCS is not supported for zero copy replication",
    ),
    "gcs/:/:/:/:the size of the s3 bucket*": (
        Skip,
        "needs investigation",
    ),
    "gcs/:/:/:the size of the s3 bucket*": (
        Skip,
        "needs investigation",
    ),
    "gcs/table function/measure file size": (
        Skip,
        "needs investigation",
    ),
    "gcs/orphans": (
        Skip,
        "AWS S3 credentials not set for gcs tests.",
    ),
    "aws s3/disk/ssec": (Skip, "SSEC option with disk not working"),
    "aws s3/table function/ssec encryption check": (
        Skip,
        "SSEC currently not working. Timeout",
    ),
    ":/disk/cache*": (
        XFail,
        "Under development for 22.8 and newer.",
        check_clickhouse_version(">=22.8"),
    ),
    ":/invalid disk/cache*": (
        XFail,
        "Under development for 22.8 and newer.",
        check_clickhouse_version(">=22.8"),
    ),
    ":/disk/no restart": (
        XFail,
        "https://github.com/ClickHouse/ClickHouse/issues/58924",
        check_clickhouse_version(">=23.12"),
    ),
    ":/table function performance": (
        Skip,
        "not supported <23.8",
        check_clickhouse_version("<23.8"),
    ),
    ":/settings/setting combinations": (
        Skip,
        "Many settings not supported <23.8",
        check_clickhouse_version("<23.8"),
    ),
    ":/orphans": (
        Skip,
        "not supported <24",
        check_clickhouse_version("<24"),
    ),
    ":/orphans/zero copy replication/:etach:": (
        Skip,
        "detach not enabled with zero copy replication",
    ),
    ":/orphans/zero copy replication/:reeze:": (
        Skip,
        "freeze not enabled with zero copy replication",
    ),
    ":/alter/:/update delete": (
        Skip,
        "Not supported <22.8",
        check_clickhouse_version("<23"),
    ),
    ":/alter/zero copy encrypted/update delete": (
        XError,
        "Timeout 23.3",
        check_clickhouse_version("<23.8"),
    ),
    ":/alter/zero cop:/projection": (
        Skip,
        "Not supported <23",
        check_clickhouse_version("<23"),
    ),
    ":/alter/zero cop:/freeze": (
        Skip,
        "not supported <24",
        check_clickhouse_version("<24"),
    ),
    ":/alter/zero cop:/d:": (
        Skip,
        "not supported",
    ),
    ":/alter/zero cop:/fetch": (
        Skip,
        "not supported",
    ),
    ":/backup/:/metadata:": (XFail, "SYSTEM RESTART DISK is not implemented"),
    ":/backup/:/system unfreeze": (
        XFail,
        "doesn't work <22.8",
        check_clickhouse_version("<22.8"),
    ),
}


@TestFeature
@Name("minio")
def minio_regression(
    self,
    uri,
    root_user,
    root_password,
    cluster_args,
    with_analyzer=False,
):
    """Setup and run minio tests."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    root_user = root_user.value
    root_password = root_password.value
    uri = uri.value

    self.context.storage = "minio"
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
            uri_bucket_file = (
                uri + f"/{self.context.cluster.minio_bucket}/{bucket_prefix}/"
            )
            self.context.bucket_name = self.context.cluster.minio_bucket

        with And("I enable or disable experimental analyzer if needed"):
            for node in nodes["clickhouse"]:
                experimental_analyzer(
                    node=cluster.node(node), with_analyzer=with_analyzer
                )

        Feature(test=load("s3.tests.sanity", "minio"))(uri=uri_bucket_file)
        Feature(test=load("s3.tests.table_function", "minio"))(
            uri=uri_bucket_file, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.backup", "minio"))(
            uri=uri_bucket_file, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.table_function_invalid", "minio"))(
            uri=uri_bucket_file
        )
        Feature(test=load("s3.tests.disk", "minio"))(
            uri=uri_bucket_file, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.disk_invalid", "minio"))(uri=uri_bucket_file)
        Feature(test=load("s3.tests.alter", "feature"))(
            uri=uri_bucket_file, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.combinatoric_table", "feature"))(
            uri=uri_bucket_file
        )
        Feature(test=load("s3.tests.reconnect", "minio"))(uri=uri_bucket_file)
        Feature(test=load("s3.tests.zero_copy_replication", "minio"))(
            uri=uri_bucket_file, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.orphans", "feature"))(
            uri=uri_bucket_file, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.cit", "feature"))(uri=uri)
        Feature(test=load("s3.tests.settings", "feature"))(uri=uri_bucket_file)
        Feature(test=load("s3.tests.table_function_performance", "minio"))(
            uri=uri_bucket_file
        )


@TestFeature
@Name("aws s3")
def aws_s3_regression(
    self,
    key_id,
    access_key,
    bucket,
    region,
    cluster_args,
    with_analyzer=False,
):
    """Setup and run aws s3 tests."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    if access_key == None:
        fail("AWS S3 access key needs to be set")
    access_key = access_key.value

    if key_id == None:
        fail("AWS S3 key id needs to be set")
    key_id = key_id.value

    if bucket == None:
        fail("AWS S3 bucket needs to be set")
    bucket = bucket.value

    if region == None:
        fail("AWS S3 region needs to be set")
    region = region.value

    bucket_prefix = "data"

    uri = f"https://s3.{region}.amazonaws.com/{bucket}/{bucket_prefix}/"

    self.context.storage = "aws_s3"
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key
    self.context.bucket_name = bucket
    self.context.region = region

    with Cluster(
        **cluster_args,
        nodes=nodes,
        environ={
            "S3_AMAZON_ACCESS_KEY": access_key,
            "S3_AMAZON_KEY_ID": key_id,
            "AWS_ACCESS_KEY_ID": key_id,
            "AWS_SECRET_ACCESS_KEY": access_key,
            "AWS_DEFAULT_REGION": region,
        },
    ) as cluster:

        self.context.cluster = cluster
        self.context.cluster.bucket = bucket
        self.context.node = cluster.node("clickhouse1")

        with Given("I enable or disable experimental analyzer if needed"):
            for node in nodes["clickhouse"]:
                experimental_analyzer(
                    node=cluster.node(node), with_analyzer=with_analyzer
                )

        Feature(test=load("s3.tests.sanity", "aws_s3"))(uri=uri)
        Feature(test=load("s3.tests.table_function", "aws_s3"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.table_function_invalid", "aws_s3"))(uri=uri)
        Feature(test=load("s3.tests.disk", "aws_s3"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.disk_invalid", "aws_s3"))(uri=uri)
        Feature(test=load("s3.tests.alter", "feature"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.combinatoric_table", "feature"))(uri=uri)
        Feature(test=load("s3.tests.zero_copy_replication", "aws_s3"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.reconnect", "aws_s3"))(uri=uri)
        Feature(test=load("s3.tests.backup", "aws_s3"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.orphans", "feature"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.settings", "feature"))(uri=uri)
        Feature(test=load("s3.tests.table_function_performance", "aws_s3"))(uri=uri)


@TestFeature
@Name("gcs")
def gcs_regression(
    self,
    uri,
    key_id,
    access_key,
    cluster_args,
    with_analyzer=False,
):
    """Setup and run gcs tests."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    if uri == None:
        fail("GCS uri needs to be set")
    uri = uri.value
    if access_key == None:
        fail("GCS access key needs to be set")
    access_key = access_key.value
    if key_id == None:
        fail("GCS key id needs to be set")
    key_id = key_id.value

    bucket_name, bucket_prefix = uri.split("https://storage.googleapis.com/")[-1].split(
        "/", maxsplit=1
    )
    self.context.storage = "gcs"
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key
    self.context.bucket_name = Secret(name="gcs_bucket")(bucket_name).value

    with Cluster(
        **cluster_args,
        nodes=nodes,
        environ={"GCS_KEY_SECRET": access_key, "GCS_KEY_ID": key_id},
    ) as cluster:
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

        with Given("I enable or disable experimental analyzer if needed"):
            for node in nodes["clickhouse"]:
                experimental_analyzer(
                    node=cluster.node(node), with_analyzer=with_analyzer
                )

        Feature(test=load("s3.tests.table_function", "gcs"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.table_function_invalid", "gcs"))(uri=uri)
        Feature(test=load("s3.tests.disk", "gcs"))(uri=uri, bucket_prefix=bucket_prefix)
        Feature(test=load("s3.tests.disk_invalid", "gcs"))(uri=uri)
        Feature(test=load("s3.tests.alter", "feature"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.combinatoric_table", "feature"))(uri=uri)
        Feature(test=load("s3.tests.zero_copy_replication", "gcs"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.backup", "gcs"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.orphans", "feature"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.settings", "feature"))(uri=uri)
        Feature(test=load("s3.tests.table_function_performance", "gcs"))(uri=uri)


@TestModule
@Name("s3")
@ArgumentParser(argparser)
@Specifications(SRS_015_ClickHouse_S3_External_Storage)
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    storages,
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
    stress=False,
    with_analyzer=False,
):
    """S3 Storage regression."""

    self.context.clickhouse_version = clickhouse_version
    self.context.stress = stress

    if storages is None:
        storages = ["minio"]

    if "aws_s3" in storages:
        Feature(test=aws_s3_regression)(
            cluster_args=cluster_args,
            bucket=aws_s3_bucket,
            region=aws_s3_region,
            key_id=aws_s3_key_id,
            access_key=aws_s3_access_key,
            with_analyzer=with_analyzer,
        )

    if "gcs" in storages:
        Feature(test=gcs_regression)(
            cluster_args=cluster_args,
            uri=gcs_uri,
            key_id=gcs_key_id,
            access_key=gcs_key_secret,
            with_analyzer=with_analyzer,
        )

    if "minio" in storages:
        Feature(test=minio_regression)(
            cluster_args=cluster_args,
            uri=minio_uri,
            root_user=minio_root_user,
            root_password=minio_root_password,
            with_analyzer=with_analyzer,
        )


if main():
    regression()
