#!/usr/bin/env python3
import sys

from testflows.core import *

append_path(sys.path, "..")

from alter.requirements.requirements import *

from helpers.cluster import create_cluster
from helpers.common import experimental_analyzer
from helpers.argparser import argparser as base_argparser, CaptureClusterArgs
from helpers.datatypes import *


def argparser(parser):
    """Custom argparser that adds a --use-specific-clickhouse-version option."""
    base_argparser(parser)

    parser.add_argument(
        "--use-specific-clickhouse-version",
        type=str,
        dest="use_specific_version",
        help="used for the tests that use different versions of clickhouse, there is a main version used for all "
        "tests which is set by --clickhouse-binary-path variable, this argument fetches additional clickhouse "
        "binary and stores it inside a container along the main version",
        metavar="path",
        default="docker://altinity/clickhouse-server:23.3.13.7.altinitytest",
    )


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
    "/alter/attach partition/temporary table/*": [
        (
            Error,
            "Temporary tables can only be created with ENGINE = Memory, not MergeTree before 23.3.",
            check_clickhouse_version("<23.3"),
        )
    ],
    "/alter/attach partition/partition key datetime/*": [
        (Fail, "Need to investigate", check_clickhouse_version("<=24.2"))
    ],
    "/alter/attach partition/storage/attach partition on tiered and default storages/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/62764",
            check_clickhouse_version(">=24.3"),
        )
    ],
    "/alter/attach partition/storage/attach partition on minio and default disks/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/62764",
            check_clickhouse_version(">=24.3"),
        )
    ],
    "/alter/replace partition/prohibited actions/conditions/storage policy/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/62764",
            check_clickhouse_version(">=24.3"),
        )
    ],
    "/alter/replace partition/storage/different disks/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/62764",
            check_clickhouse_version(">=24.3"),
        )
    ],
    "/alter/attach partition/part level/merge increment/*": [
        (
            Fail,
            "Need to investigate",
        )
    ],
    "/alter/attach partition/part level/part level reset/*": [  # ReplicatedReplacingMergeTree
        (
            Fail,
            "Need to investigate",
        )
    ],
    "/alter/replace partition/concurrent replace partitions/concurrent replace/*": [
        (
            Fail,
            "Bug when replacing partitions concurrently",
        )
    ],
    "/alter/attach partition/conditions/indices/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/54896",
            check_clickhouse_version("<23.3"),
        )
    ],
    "attach partition/conditions/primary key/:": [
        (
            Fail,
            "Bug fixed in 23 https://github.com/ClickHouse/ClickHouse/issues/41783",
            check_clickhouse_version("<23"),
        )
    ],
}

xflags = {}

ffails = {
    "/alter/:/temporary table": (
        Skip,
        "Not implemented before 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/alter/attach partition/part level/part levels user example/*": (
        Skip,
        "Crashes before 24.3",
        check_clickhouse_version("<24.3"),
    ),
    "/alter/move partition/move to self": (
        XFail,
        "https://github.com/ClickHouse/ClickHouse/issues/62459",
    ),
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Specifications(SRS032_ClickHouse_Alter)
@Name("alter")
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    use_specific_version,
    stress=None,
    with_analyzer=False,
):
    """Alter regression."""
    nodes = {
        "clickhouse": (
            "clickhouse1",
            "clickhouse2",
            "clickhouse3",
            "clickhouse-different-versions",
        )
    }

    self.context.clickhouse_version = clickhouse_version
    self.context.storage = "minio"
    self.context.uri = "http://minio:9001/root/data/alter"
    self.context.access_key_id = "minio"
    self.context.secret_access_key = "minio123"

    self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
            use_specific_version=use_specific_version,
        )
        self.context.cluster = cluster

    with And("I enable or disable experimental analyzer if needed"):
        for node in cluster.nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Feature(run=load("alter.table.replace_partition.feature", "feature"))
    Feature(run=load("alter.table.attach_partition.feature", "feature"))
    Feature(run=load("alter.table.move_partition.feature", "feature"))


if main():
    regression()
