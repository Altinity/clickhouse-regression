#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster, create_cluster
from helpers.common import experimental_analyzer
from helpers.argparser import argparser_s3, CaptureClusterArgs, CaptureS3Args
from s3.tests.common import *
from helpers.create_clusters import add_clusters_for_nodes, get_clusters_for_nodes

from s3.requirements import SRS_015_ClickHouse_S3_External_Storage

xfails = {
    ":/:/disk/generic url": [(Fail, "not yet supported")],
    ":/:/remote host filter": [
        (Fail, "remote host filter does not work with disk storage")
    ],
    "gcs/:/disk invalid/:": [
        (Fail, "Google Cloud Storage does not work with disk storage")
    ],
    ":/:/zero copy replication/alter/count=10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22516")
    ],
    ":/:/zero copy replication/ttl move": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22679")
    ],
    ":/:/zero copy replication/ttl delete": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/22679")
    ],
    ":/:/zero copy replication/delete": [
        (Fail, "test is slow to clean up, needs investigation")
    ],
    ":/:/zero copy replication/:mutation/:/the size of the s3 bucket:": [
        (Fail, "test doesn't clean up, needs investigation")
    ],
    "minio/:/backup/:/alter freeze": [(Fail, "External disks do not create backups")],
    "minio/:/disk/environment credentials/:": [
        (Fail, "AWS S3 credentials not set for minio tests.")
    ],
    "minio/:/disk/log/:": [
        (Fail, "Not working 22.X", check_clickhouse_version("<=23"))
    ],
    "aws s3/:/disk/:/:/:the size of the s3 bucket*": [(Fail, "fails on runners")],
    "aws s3/:/disk/:/:the size of the s3 bucket*": [(Fail, "fails on runners")],
    "aws s3/:/backup/:/:/:/the size of the s3 bucket*": [(Fail, "needs review")],
    "gcs/:/disk/environment credentials/:": [
        (Fail, "AWS S3 credentials not set for gcs tests.")
    ],
    ":/:/backup/:/metadata non restorable schema": [
        (Fail, "send_metadata is deprecated")
    ],
    ":/:/zero copy replication/the size of the s3 bucket should be the same as before": [
        (Fail, "Data cleanup needs investigation")
    ],
    "aws s3/:/backup/:/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/30510")
    ],
    "minio/:/zero copy replication/performance alter": [
        (Error, "Unstable test"),
        (Fail, "Unstable test"),
    ],
    "minio/:/zero copy replication/performance select": [
        (Error, "Unstable test"),
        (Fail, "Unstable test"),
    ],
    "aws s3/:/zero copy replication/stale alter replica": [
        (Error, "Timeout on 22.x", check_clickhouse_version("<=23"))
    ],
    "gcs/:/table function/wildcard/:": [
        (Fail, "Fixed by https://github.com/ClickHouse/ClickHouse/pull/37344")
    ],
    ":/:/disk/delete/delete one row": [(Fail, "Bug that needs to be investigated")],
    "gcs/:/disk/delete/gcs truncate err log": [
        (Fail, "Exception appears in error log but not in ClickHouse.")
    ],
    "aws s3/:/table function/ssec/:": [
        (Fail, "https://altinity.atlassian.net/browse/CH-241")
    ],
    "aws s3/:/table function/ssec/:/:": [
        (Fail, "https://altinity.atlassian.net/browse/CH-241")
    ],
    "aws s3/:/table function/ssec encryption check": [
        (Fail, "https://altinity.atlassian.net/browse/CH-242")
    ],
    ":/:/table function performance/wildcard/:": [
        (
            Error,
            "https://github.com/ClickHouse/ClickHouse/pull/62120",
            check_clickhouse_version("<24.5"),
        )
    ],
    ":/:/table function performance/wildcard/one folder/*": [
        (
            Fail,
            "Need investigation, fails on 25.6 Antalya",
        )
    ],
    ":/:/table function performance/wildcard/nums/*": [
        (
            Fail,
            "Need investigation, fails on 25.6 Antalya",
        )
    ],
    ":/:/table function performance/wildcard/nums one invalid*": [
        (
            Fail,
            "Need investigation, fails on 25.6 Antalya",
        )
    ],
    ":/:/table function performance/wildcard/star/*": [
        (
            Fail,
            "Need investigation",
        )
    ],
    ":/:/table function performance/wildcard/question encoded/*": [
        (
            Fail,
            "Need investigation",
        )
    ],
    ":/:/table function performance/wildcard/question/*": [
        (
            Fail,
            "Need investigation",
        )
    ],
    ":/:/table function performance/wildcard/range/*": [
        (
            Fail,
            "Need investigation",
        )
    ],
    ":/:/table function performance/setup/*": [
        (Fail, "Need investigation, fails on 25.6 Antalya"),
    ],
    ":/:/disk/low cardinality offset": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/pull/44875")
    ],
    ":/:/zero copy replication/bad detached part": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/pull/58333",
            check_clickhouse_version("<23.11"),
        )
    ],
    ":/:/alter/:/projection": [
        (Fail, "Wrong error message 22.3", check_clickhouse_version("<22.8")),
    ],
    ":/:/alter/zero copy encrypted/:": [
        (
            Fail,
            "Bug in 23.3 https://github.com/ClickHouse/ClickHouse/pull/68821",
            check_clickhouse_version("<23.8"),
        ),
    ],
    ":/:/table function/measure file size": [
        (Fail, "Not implemented <24", check_clickhouse_version("<24"))
    ],
    ":/:/table function/measure file size s3Cluster": [
        (Fail, "Not implemented <24", check_clickhouse_version("<24"))
    ],
    ":/:/combinatoric table/:n_cols=2000:part_type=compact": [
        (
            Fail,
            "Compact parts require too much memory with 2000 columns",
            always,
            ".*MEMORY_LIMIT_EXCEEDED.*",
        )
    ],
    ":/:/combinatoric table/engine=VersionedCollapsingMergeTree,replicated=True,n_cols=2000,n_tables=3,part_type=wide": [
        (
            Fail,
            "Needs investigation, MEMORY_LIMIT_EXCEEDED",
            always,
            ".*MEMORY_LIMIT_EXCEEDED.*",
        )
    ],
    ":/:/combinatoric table/engine=:,replicated=True,n_cols=2000,n_tables=3,part_type=:": [
        (
            Fail,
            "Needs investigation, rows not appearing",
            always,
            ".*assert rows == actual_count.*",
        )
    ],
    "gcs/:/combinatoric table": [
        (Fail, "Time outs need investigation"),
    ],
    "gcs/:/combinatoric table/:": [
        (
            Error,
            "Times out, needs investigation",
            always,
            ".*testflows.uexpect.uexpect.ExpectTimeoutError.*",
        ),
    ],
    "azure/:/combinatoric table/:": [
        (
            Fail,
            "Times out, needs investigation",
            always,
            ".*TIMEOUT_EXCEEDED.*",
        ),
    ],
    "azure/:/combinatoric table/:": [
        (
            Error,
            "Times out, needs investigation",
            always,
            ".*testflows.uexpect.uexpect.ExpectTimeoutError.*",
        ),
    ],
    ":/:/invalid table function/invalid region": [
        (Error, "https://github.com/ClickHouse/ClickHouse/issues/59084")
    ],
    ":/:/invalid table function/invalid path": [
        (
            Error,
            "https://github.com/ClickHouse/ClickHouse/issues/59084",
            check_clickhouse_version(">=24.9"),
        )
    ],
    ":/:/invalid table function/invalid wildcard": [
        (
            Fail,
            "doesn't work <25.1 https://github.com/ClickHouse/ClickHouse/issues/75492",
            check_clickhouse_version("<25.1"),
        )
    ],
    ":/:/alter/:/columns/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/83388",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/:/compression_method = :, cluster_name = :/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/credentials s3Cluster/cluster_name = cluster_3shards_2replicas_0/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/credentials s3Cluster/cluster_name = cluster_3shards_1replicas_0/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/credentials s3Cluster/cluster_name = cluster_2shards_1replicas_0/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/data format/fmt = *, cluster_name = cluster_2shards_1replicas_0/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/data format/fmt = *, cluster_name = cluster_3shards_1replicas_0/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/data format/fmt = *, cluster_name = cluster_3shards_2replicas_0/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/wildcard/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/syntax s3Cluster/cluster_name = cluster_3shards_2replicas_0/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/syntax s3Cluster/cluster_name = cluster_3shards_1replicas_0/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    "minio/part 1/table function/syntax s3Cluster/cluster_name = cluster_2shards_1replicas_0/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/84713",
            check_clickhouse_version(">=25.7"),
        )
    ],
    ":/part 1/table function/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/88699",
            check_clickhouse_version(">=25.8"),
        )
    ],
}

ffails = {
    "minio/:/hive partitioning": (
        Skip,
        "implemented on antalya build with clickhouse version 24.12",
        check_clickhouse_version("<24.12"),
    ),
    "minio/:/remote s3 function call": (
        Skip,
        "implemented on antalya build with clickhouse version 24.12",
        check_clickhouse_version("<24.12"),
    ),
    "minio/:/table function performance/wildcard": (
        Skip,
        "needs investigation",
    ),
    ":/:/hive partitioning": (
        Skip,
        "implemented on antalya build with clickhouse version 24.12",
        check_if_not_antalya_build,
    ),
    ":/:/remote s3 function call": (
        Skip,
        "implemented on antalya build with clickhouse version 24.12",
        check_if_not_antalya_build,
    ),
    "minio/:/table function/measure file size s3Cluster": (
        Skip,
        "S3Cluster table function correctly handles arguments since 23.8",
        check_clickhouse_version("<23.8"),
    ),
    "minio/:/disk/environment credentials": (
        Skip,
        "AWS S3 credentials not set for minio tests.",
    ),
    "gcs/:/disk/environment credentials": (
        Skip,
        "AWS S3 credentials not set for gcs tests.",
    ),
    "gcs/:/zero copy replication": (
        Skip,
        "GCS is not supported for zero copy replication",
    ),
    "gcs/:/:/:/:/:the size of the s3 bucket*": (
        Skip,
        "needs investigation",
    ),
    "gcs/:/:/:/:the size of the s3 bucket*": (
        Skip,
        "needs investigation",
    ),
    "gcs/:/table function/measure file size": (
        Skip,
        "needs investigation",
    ),
    "gcs/:/table function/measure file size s3Cluster": (
        Skip,
        "needs investigation",
    ),
    "gcs/:/table function performance/wildcard/nums no match": (
        Skip,
        "needs investigation",
    ),
    "gcs/:/table function performance/wildcard/range no match": (
        Skip,
        "needs investigation",
    ),
    "gcs/:/orphans": (
        Skip,
        "AWS S3 credentials not set for gcs tests.",
    ),
    "azure/:/:/:/:/:he size of the s3 bucket*": (
        Skip,
        "azure not s3 compatible",
    ),
    "azure/:/:/:/:he size of the s3 bucket*": (
        Skip,
        "azure not s3 compatible",
    ),
    "azure/:/:/:he size of the s3 bucket*": (
        Skip,
        "azure not s3 compatible",
    ),
    "azure/:/disk/environment credentials": (
        Skip,
        "azure not s3 compatible",
    ),
    "azure/:/disk/:ports": (
        Skip,
        "azure not s3 compatible",
    ),
    "azure/:/invalid disk/access failed skip check": (
        XFail,
        "Not working, needs investigation",
    ),
    "azure/:/combinatoric table": (Skip, "Time outs need investigation"),
    "azure/:/zero copy replication/metadata": (Skip, "azure not s3 compatible"),
    "azure/:/zero copy replication/alter": (Skip, "investigate"),
    "aws s3/:/invalid table function/invalid wildcard": (Skip, "needs investigation"),
    "aws s3/:/disk/ssec": (Skip, "SSEC option with disk not working"),
    "aws s3/:/table function/ssec encryption check": (
        Skip,
        "SSEC currently not working. Timeout",
    ),
    ":/:/disk/cache*": (
        XFail,
        "Under development for 22.8 and newer.",
        check_clickhouse_version(">=22.8"),
    ),
    ":/:/invalid disk/cache*": (
        XFail,
        "Under development for 22.8 and newer.",
        check_clickhouse_version(">=22.8"),
    ),
    ":/:/disk/no restart": (
        XFail,
        "https://github.com/ClickHouse/ClickHouse/issues/58924",
        check_clickhouse_version(">=23.12"),
    ),
    ":/:/table function performance": (
        Skip,
        "not supported <23.8",
        check_clickhouse_version("<23.8"),
    ),
    ":/:/settings/setting combinations": (
        Skip,
        "Many settings not supported <23.8",
        check_clickhouse_version("<23.8"),
    ),
    ":/:/orphans": (
        Skip,
        "not supported <24",
        check_clickhouse_version("<24"),
    ),
    ":/:/orphans/zero copy replication/:etach:": (
        Skip,
        "detach not enabled with zero copy replication",
    ),
    ":/:/orphans/zero copy replication/:reeze:": (
        Skip,
        "freeze not enabled with zero copy replication <24.10",
        check_clickhouse_version("<24.10"),
    ),
    ":/:/alter/:/update delete": (
        Skip,
        "Not supported <22.8",
        check_clickhouse_version("<23"),
    ),
    ":/:/alter/zero copy encrypted/update delete": (
        XError,
        "Timeout 23.3",
        check_clickhouse_version("<23.8"),
    ),
    ":/:/alter/zero cop:/projection": (
        Skip,
        "Not supported <23",
        check_clickhouse_version("<23"),
    ),
    ":/:/alter/zero cop:/freeze": (
        Skip,
        "not supported <24.10",
        check_clickhouse_version("<24.10"),
    ),
    ":/:/alter/zero cop:/d:": (
        Skip,
        "not supported",
    ),
    ":/:/alter/zero cop:/fetch": (
        Skip,
        "not supported",
    ),
    ":/:/backup/:/metadata:": (XFail, "SYSTEM RESTART DISK is not implemented"),
    ":/:/backup/:/system unfreeze": (
        XFail,
        "doesn't work <22.8",
        check_clickhouse_version("<22.8"),
    ),
    "/:/:/part 3/export part/*": (
        Skip,
        "Export part introduced in Antalya build",
        check_if_not_antalya_build,
    ),
    "/:/:/part 3/export part/*": (
        Skip,
        "Export part tests not supported for Antalya version <25.8",
        check_clickhouse_version("<25.8"),
    ),
    "/:/:/part 3/export partition/*": (
        Skip,
        "Export partition introduced in Antalya build",
        check_if_not_antalya_build,
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

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            environ={
                "MINIO_ROOT_PASSWORD": root_password,
                "MINIO_ROOT_USER": root_user,
            },
            configs_dir=current_dir(),
        )

    self.context.cluster = cluster
    self.context.node = cluster.node("clickhouse1")
    self.context.node2 = cluster.node("clickhouse2")
    self.context.node3 = cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node2, self.context.node3]

    with And("I have a minio client"):
        start_minio(access_key=root_user, secret_key=root_password)
        uri_bucket_file = uri + f"/{self.context.cluster.minio_bucket}/{bucket_prefix}/"
        self.context.bucket_name = self.context.cluster.minio_bucket

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    with And("allow higher cpu_wait_ratio "):
        if check_clickhouse_version(">=25.4")(self):
            allow_higher_cpu_wait_ratio(
                min_os_cpu_wait_time_ratio_to_throw=15,
                max_os_cpu_wait_time_ratio_to_throw=25,
            )

    with And("I add all possible clusters for nodes"):
        add_clusters_for_nodes(nodes=nodes["clickhouse"], modify=True)

    with And("I get all possible clusters for nodes"):
        self.context.clusters = get_clusters_for_nodes(nodes=nodes["clickhouse"])

    with Feature("part 1"):
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
    with Feature("part 2"):
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
    with Feature("part 3"):
        Feature(test=load("s3.tests.table_function_performance", "minio"))(
            uri=uri_bucket_file
        )
        Feature(test=load("s3.tests.hive_partitioning", "minio"))(
            uri=uri_bucket_file, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.remote_s3_function", "minio"))(
            uri=uri_bucket_file, bucket_prefix=bucket_prefix
        )
    with Feature("export tests"):    
        Feature(test=load("s3.tests.export_part.feature", "minio"))(
            uri=uri_bucket_file, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.export_partition.feature", "minio"))(
            uri=uri_bucket_file, bucket_prefix=bucket_prefix
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

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            environ={
                "S3_AMAZON_ACCESS_KEY": access_key,
                "S3_AMAZON_KEY_ID": key_id,
                "AWS_ACCESS_KEY_ID": key_id,
                "AWS_SECRET_ACCESS_KEY": access_key,
                "AWS_DEFAULT_REGION": region,
            },
            configs_dir=current_dir(),
        )

        self.context.cluster = cluster
        self.context.cluster.bucket = bucket
        self.context.node = cluster.node("clickhouse1")

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    with And("allow higher cpu_wait_ratio "):
        if check_clickhouse_version(">=25.4")(self):
            allow_higher_cpu_wait_ratio(
                min_os_cpu_wait_time_ratio_to_throw=15,
                max_os_cpu_wait_time_ratio_to_throw=25,
            )

    with And("I add all possible clusters for nodes"):
        add_clusters_for_nodes(nodes=nodes["clickhouse"], modify=True)

    with And("I get all possible clusters for nodes"):
        self.context.clusters = get_clusters_for_nodes(nodes=nodes["clickhouse"])

    with Feature("part 1"):
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
    with Feature("part 2"):
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
@Name("azure")
def azure_regression(
    self,
    account_name,
    storage_key,
    container_name,
    cluster_args,
    with_analyzer=False,
):
    """Setup and run aws s3 tests."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    if account_name == None:
        fail("Azure account name needs to be set")
    account_name = account_name.value

    if storage_key == None:
        fail("Azure storage key needs to be set")
    storage_key = storage_key.value

    if container_name == None:
        fail("Azure container name needs to be set")
    container_name = container_name.value

    azure_storage_account_url = f"https://{account_name}.blob.core.windows.net/"
    uri = None
    bucket_prefix = None

    self.context.storage = "azure"
    self.context.azure_storage_account_url = azure_storage_account_url
    self.context.uri = uri
    self.context.azure_account_name = account_name
    self.context.azure_account_key = storage_key
    self.context.azure_container_name = container_name

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            # environ={
            #     "AZURE_CLIENT_ID": client_id,
            #     "AZURE_CLIENT_SECRET": client_secret,
            #     "AZURE_STORAGE_KEY": storage_key,
            #     "AZURE_TENANT_ID": tenant_id,
            # },
            configs_dir=current_dir(),
        )

        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    with And("allow higher cpu_wait_ratio "):
        if check_clickhouse_version(">=25.4")(self):
            allow_higher_cpu_wait_ratio(
                min_os_cpu_wait_time_ratio_to_throw=15,
                max_os_cpu_wait_time_ratio_to_throw=25,
            )

    with Feature("part 1"):
        Feature(test=load("s3.tests.sanity", "azure"))()
        Feature(test=load("s3.tests.alter", "feature"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.disk", "azure"))()
        Feature(test=load("s3.tests.disk_invalid", "azure"))()
        Feature(test=load("s3.tests.combinatoric_table", "feature"))(uri=uri)
    with Feature("part 2"):
        Feature(test=load("s3.tests.zero_copy_replication", "azure"))()
        Feature(test=load("s3.tests.reconnect", "azure"))()
        Feature(test=load("s3.tests.backup", "azure"))()
        # Feature(test=load("s3.tests.orphans", "feature"))(
        #     uri=uri, bucket_prefix=bucket_prefix
        # )
        Feature(test=load("s3.tests.settings", "feature"))(uri=uri)


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

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            environ={"GCS_KEY_SECRET": access_key, "GCS_KEY_ID": key_id},
            configs_dir=current_dir(),
        )

        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    with And("allow higher cpu_wait_ratio "):
        if check_clickhouse_version(">=25.4")(self):
            allow_higher_cpu_wait_ratio(
                min_os_cpu_wait_time_ratio_to_throw=15,
                max_os_cpu_wait_time_ratio_to_throw=25,
            )

    with And("I add all possible clusters for nodes"):
        add_clusters_for_nodes(nodes=nodes["clickhouse"], modify=True)

    with And("I get all possible clusters for nodes"):
        self.context.clusters = get_clusters_for_nodes(nodes=nodes["clickhouse"])

    with Feature("part 1"):
        Feature(test=load("s3.tests.sanity", "gcs"))(uri=uri)
        Feature(test=load("s3.tests.table_function", "gcs"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
        Feature(test=load("s3.tests.table_function_invalid", "gcs"))(uri=uri)
        Feature(test=load("s3.tests.disk", "gcs"))(uri=uri, bucket_prefix=bucket_prefix)
        Feature(test=load("s3.tests.disk_invalid", "gcs"))(uri=uri)
        Feature(test=load("s3.tests.alter", "feature"))(
            uri=uri, bucket_prefix=bucket_prefix
        )
    with Feature("part 2"):
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
@ArgumentParser(argparser_s3)
@Specifications(SRS_015_ClickHouse_S3_External_Storage)
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
@CaptureS3Args
def regression(
    self,
    cluster_args: dict,
    s3_args: dict,
    clickhouse_version: str,
    stress=False,
    with_analyzer=False,
):
    """S3 Storage regression."""

    self.context.clickhouse_version = clickhouse_version
    self.context.stress = stress

    storages = s3_args.pop("storages", None)
    if storages is None:
        storages = ["minio"]

    if "aws_s3" in storages:
        Feature(test=aws_s3_regression)(
            cluster_args=cluster_args,
            bucket=s3_args["aws_s3_bucket"],
            region=s3_args["aws_s3_region"],
            key_id=s3_args["aws_s3_key_id"],
            access_key=s3_args["aws_s3_access_key"],
            with_analyzer=with_analyzer,
        )

    if "gcs" in storages:
        Feature(test=gcs_regression)(
            cluster_args=cluster_args,
            uri=s3_args["gcs_uri"],
            key_id=s3_args["gcs_key_id"],
            access_key=s3_args["gcs_key_secret"],
            with_analyzer=with_analyzer,
        )

    if "azure" in storages:
        Feature(test=azure_regression)(
            cluster_args=cluster_args,
            account_name=s3_args["azure_account_name"],
            storage_key=s3_args["azure_storage_key"],
            container_name=s3_args["azure_container"],
            with_analyzer=with_analyzer,
        )

    if "minio" in storages:
        Feature(test=minio_regression)(
            cluster_args=cluster_args,
            uri=s3_args["minio_uri"],
            root_user=s3_args["minio_root_user"],
            root_password=s3_args["minio_root_password"],
            with_analyzer=with_analyzer,
        )


if main():
    regression()
