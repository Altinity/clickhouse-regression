#!/usr/bin/env python3
import os
import sys

from testflows.core import *
from testflows.connect import Shell

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as argparser_base, CaptureClusterArgs
from helpers.common import check_clickhouse_version, experimental_analyzer
from s3.tests.common import temporary_bucket_path
from tiered_storage.requirements import *
from tiered_storage.tests.common import add_storage_config


def argparser(parser):
    """Custom argument parser."""
    argparser_base(parser)

    parser.add_argument(
        "--with-minio",
        action="store_true",
        help="use minio storage for external disk",
        default=False,
    )

    parser.add_argument(
        "--with-s3amazon",
        action="store_true",
        help="use S3 Amazon Cloud storage for external disk",
        default=False,
    )

    parser.add_argument(
        "--with-s3gcs",
        action="store_true",
        help="use S3 Google Cloud storage for external disk",
        default=False,
    )

    parser.add_argument(
        "--aws-s3-access-key",
        action="store",
        help="S3 Amazon access key",
        type=Secret(name="aws_s3_access_key"),
        default=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    parser.add_argument(
        "--aws-s3-key-id",
        action="store",
        help="S3 Amazon key id",
        type=Secret(name="aws_s3_key_id"),
        default=os.getenv("AWS_ACCESS_KEY_ID"),
    )

    parser.add_argument(
        "--aws-s3-uri",
        action="store",
        help="S3 Amazon uri",
        type=Secret(name="aws_s3_uri"),
        default=os.getenv("S3_AMAZON_URI"),
    )

    parser.add_argument(
        "--gcs-uri",
        action="store",
        help="S3 gcs uri",
        type=Secret(name="gcs_uri"),
        default=os.getenv("GCS_URI"),
    )

    parser.add_argument(
        "--gcs-key-id",
        action="store",
        help="S3 gcs key id",
        type=Secret(name="gcs_key_id"),
        default=os.getenv("GCS_KEY_ID"),
    )

    parser.add_argument(
        "--gcs-key-secret",
        action="store",
        help="S3 gcs key secret",
        type=Secret(name="gcs_key_secret"),
        default=os.getenv("GCS_KEY_SECRET"),
    )

    return parser


xfails = {
    ":/manual move with downtime": [
        (Fail, "https://altinity.atlassian.net/browse/CH-124")
    ],
    ":/ttl moves/alter with existing parts/:/inserted parts should:": [
        (Fail, "not yet supported")
    ],
    ":/ttl moves/alter policy and ttl with existing parts": [
        (Fail, "not yet supported")
    ],
    ":/ttl moves/alter with merge": [(Fail, "not yet supported")],
    ":/ttl moves/materialize ttl": [(Error, "not yet supported")],
    ":/ttl moves/mutation update column in ttl": [(Error, "not yet supported")],
    ":/double move while select": [(Fail, "not yet supported")],
    ":/background move/concurrent read/:": [(Fail, "known issue")],
    ":/disk space bytes": [(Fail, "not yet supported")],
    ":/attach or replace partition different policies": [(Fail, "known issue")],
    ":/ttl moves/alter column in ttl/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/39808")
    ],
    ":/ttl moves/delete/:/parts should be deleted": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/50060")
    ],
    ":/ttl moves/defaults to delete/:/parts should be deleted": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/50060")
    ],
    ":/query parser": [
        (
            Fail,
            "Incorrect message https://github.com/ClickHouse/ClickHouse/pull/51854",
            check_clickhouse_version("<23.8"),
        )
    ],
    ":/alter move/concurrent/:/:": [
        (Error, "Unstable test", always, ".*Failed to find a part to move.*"),
        (Fail, "Unstable test", always, ".*NOT_ENOUGH_SPACE.*"),
    ],
    ":/system tables": [
        (Fail, "Not configured for 22.3", check_clickhouse_version("<22.8"))
    ],
    ":/freeze": [(Fail, "Not working 22.3", check_clickhouse_version("<22.8"))],
    ":/alter move/alter move/:": [
        (Fail, "Not working 22.3", check_clickhouse_version("<22.8"))
    ],
    ":/background move/:/:": [
        (Fail, "Not working 22.3", check_clickhouse_version("<22.8"))
    ],
}

ffails = {
    ":/ttl moves/alter with merge": (XFail, "bug, test gets stuck"),
    "with s3amazon/alter table policy": (XFail, "Investigating"),
}


@TestOutline(Feature)
@Requirements(
    RQ_SRS_004_MultipleStorageDevices("1.0"),
    RQ_SRS_004_TableDefinition_ChangesForStoragePolicyOrTTLExpressions("1.0"),
)
def feature(
    self,
    cluster,
    with_minio=False,
    with_s3amazon=False,
    with_s3gcs=False,
    environ=None,
    base_uri=None,
):
    """Execute tests for tiered storage feature."""

    args = {"cluster": cluster}
    common_args = dict(args=args, flags=TE)

    if with_s3amazon:
        with Given("a temporary S3 path"):
            bucket_name, bucket_prefix = (
                base_uri.split(".amazonaws.com/")[-1].strip("/").split("/", maxsplit=1)
            )
            temp_s3_path = temporary_bucket_path(
                bucket_name=bucket_name,
                bucket_prefix=f"{bucket_prefix}/tiered_storage",
                secret_access_key=environ["S3_AMAZON_ACCESS_KEY"],
                access_key_id=environ["S3_AMAZON_KEY_ID"],
                storage="aws_s3",
            )
            environ["S3_AMAZON_URI"] = f"{base_uri}/tiered_storage/{temp_s3_path}/"

    if with_s3gcs:
        with Given("a temporary GCS path"):
            bucket_name, bucket_prefix = (
                base_uri.split("https://storage.googleapis.com/")[-1]
                .strip("/")
                .split("/", maxsplit=1)
            )
            temp_s3_path = temporary_bucket_path(
                bucket_name=bucket_name,
                bucket_prefix=f"{bucket_prefix}/tiered_storage",
                access_key_id=environ["GCS_KEY_ID"],
                secret_access_key=environ["GCS_KEY_SECRET"],
                storage="gcs",
            )
            environ["GCS_URI"] = f"{base_uri}/tiered_storage/{temp_s3_path}"

    with add_storage_config(with_minio, with_s3amazon, with_s3gcs, environ):
        Scenario(
            run=load("tiered_storage.tests.startup_and_queries", "scenario"),
            **common_args,
        )
        Scenario(run=load("tiered_storage.tests.metadata", "scenario"), **common_args)
        Scenario(
            run=load("tiered_storage.tests.no_changes_to_queries", "scenario"),
            **common_args,
        )
        # Scenario(run=load("tiered_storage.tests.disk_config_either_keep_free_space_bytes_or_ratio", "scenario"), **common_args)
        Scenario(
            run=load(
                "tiered_storage.tests.volume_config_either_max_data_part_size_bytes_or_ratio",
                "scenario",
            ),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.system_tables", "scenario"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.system_detached_parts", "scenario"),
            **common_args,
        )
        Scenario(
            run=load(
                "tiered_storage.tests.attach_or_replace_partition_different_policies",
                "scenario",
            ),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.query_parser", "scenario"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.keep_free_space", "scenario"),
            **common_args,
        )
        Scenario(
            run=load(
                "tiered_storage.tests.no_warning_about_zero_max_data_part_size",
                "scenario",
            ),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.round_robin", "scenario"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.max_data_part_size", "scenario"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.jbod_overflow", "scenario"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.start_stop_moves", "scenario"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.mutate_to_another_disk", "scenario"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.alter_table_policy", "scenario"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.simple_replication_and_moves", "scenario"),
            **common_args,
        )
        # Scenario(run=load("tiered_storage.tests.simple_replication_and_moves_no_space", "scenario"), **common_args)
        Scenario(
            run=load("tiered_storage.tests.download_appropriate_disk", "scenario"),
            **common_args,
        )
        Scenario(
            run=load(
                "tiered_storage.tests.download_appropriate_disk_advanced",
                "scenario",
            ),
            **common_args,
        )
        Scenario(
            run=load(
                "tiered_storage.tests.download_appropriate_disk_max_data_part_size",
                "scenario",
            ),
            **common_args,
        )
        Scenario(run=load("tiered_storage.tests.rename", "scenario"), **common_args)
        Scenario(run=load("tiered_storage.tests.freeze", "scenario"), **common_args)
        Scenario(
            run=load("tiered_storage.tests.double_move_while_select", "scenario"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.background_move.feature", "feature"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.alter_move.feature", "feature"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.manual_move_with_downtime", "scenario"),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.merge_parts_different_volumes", "scenario"),
            **common_args,
        )
        Scenario(
            run=load(
                "tiered_storage.tests.merge_parts_different_volumes_no_space",
                "scenario",
            ),
            **common_args,
        )
        Scenario(
            run=load("tiered_storage.tests.ttl_moves.feature", "feature"),
            **common_args,
        )
        Scenario(
            run=load(
                "tiered_storage.tests.change_config_norestart.feature",
                "feature",
            ),
            **common_args,
        )


@TestModule
@ArgumentParser(argparser)
@Name("tiered storage")
@Specifications(QA_SRS004_ClickHouse_Tiered_Storage)
@Requirements(RQ_SRS_004_TieredStorage("1.0"))
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_minio=False,
    with_s3amazon=False,
    with_s3gcs=False,
    aws_s3_access_key=None,
    aws_s3_key_id=None,
    aws_s3_uri=None,
    gcs_key_secret=None,
    gcs_key_id=None,
    gcs_uri=None,
    with_analyzer=False,
):
    """Tiered Storage regression."""
    environ = {}

    self.context.clickhouse_version = clickhouse_version

    if with_minio or with_s3amazon or with_s3gcs:
        if not self.skip:
            self.skip = []
        self.skip.append(The("/tiered storage/:/:/manual move with downtime"))

    with Shell() as bash:
        base_uri = None
        aws_region = None
        if with_s3amazon:
            assert (
                aws_s3_key_id.value is not None
            ), "AWS_ACCESS_KEY_ID env variable must be defined or passed through the command line"
            assert (
                aws_s3_access_key.value is not None
            ), "AWS_SECRET_ACCESS_KEY env variable must be defined or passed through the command line"
            assert (
                aws_s3_uri.value is not None
            ), "S3_AMAZON_URI env variable must be defined"
            environ["S3_AMAZON_KEY_ID"] = aws_s3_key_id.value
            environ["S3_AMAZON_ACCESS_KEY"] = aws_s3_access_key.value
            base_uri = aws_s3_uri.value
            aws_region = base_uri.split(".")[1]

        if with_s3gcs:
            assert (
                gcs_key_id.value is not None
            ), "GCS_KEY_ID env variable must be defined or passed through the command line"
            assert (
                gcs_key_secret.value is not None
            ), "GCS_KEY_SECRET env variable must be defined or passed through the command line"
            assert gcs_uri.value is not None, "GCS_URI env variable must be defined"
            environ["GCS_KEY_ID"] = gcs_key_id.value
            environ["GCS_KEY_SECRET"] = gcs_key_secret.value
            base_uri = gcs_uri.value

        nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    with Cluster(
        **cluster_args,
        nodes=nodes,
        environ={"AWS_DEFAULT_REGION": aws_region},
    ) as cluster:
        cluster.with_minio = with_minio
        cluster.with_s3amazon = with_s3amazon
        cluster.with_s3gcs = with_s3gcs
        self.context.cluster = cluster

        with Given("I enable or disable experimental analyzer if needed"):
            for node in nodes["clickhouse"]:
                experimental_analyzer(
                    node=cluster.node(node), with_analyzer=with_analyzer
                )

        name = "normal"
        if with_minio:
            name = "with minio"
        elif with_s3amazon:
            name = "with s3amazon"
        elif with_s3gcs:
            name = "with s3gcs"

        Feature(name, test=feature)(
            cluster=cluster,
            with_minio=with_minio,
            with_s3amazon=with_s3amazon,
            with_s3gcs=with_s3gcs,
            environ=environ,
            base_uri=base_uri,
        )


if main():
    regression()
