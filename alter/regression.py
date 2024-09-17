#!/usr/bin/env python3
import sys

from testflows.core import *

append_path(sys.path, "..")

from alter.requirements.requirements import *

from helpers.cluster import create_cluster
from helpers.common import experimental_analyzer
from helpers.argparser import argparser as base_argparser, CaptureClusterArgs
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
    "/alter/attach partition/conditions/projections/*": [
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
    "/alter/attach partition/part level/too high level/:/I check that part was not attached by checking the parts state": [
        (
            Fail,
            "Need to investigate why part name stays the same",
            check_clickhouse_version("<22.12"),
        )
    ],
    "/alter/attach partition/operations on attached partitions/multiple operations/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/pull/68052",
            check_clickhouse_version("<24.3.6"),
        )
    ],
    "/alter/attach partition/partition key/attach partition from with id/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/pull/68052",
            check_clickhouse_version("<24.3.6"),
        )
    ],
    "/alter/attach partition/part level/reset when equal to legacy max level/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/69001",
            check_clickhouse_version(">24.8"),
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
        check_clickhouse_version("<24.4"),
    ),
}


@TestModule
@ArgumentParser(base_argparser)
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
