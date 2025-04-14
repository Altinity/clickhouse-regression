#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.common import *

from selects.requirements import *

xfails = {
    "final/force/general/without experimental analyzer/select join clause/*": [
        (
            Fail,
            "doesn't work in clickhouse"
            " https://github.com/ClickHouse/ClickHouse/issues/8655",
        )
    ],
    "final/force/general/with experimental analyzer/simple select group by/*": [
        (Fail, "group by conflict analyzer")
    ],
    "final/force/general/with experimental analyzer/simple select count/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/simple select as/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/simple select limit/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/simple select limit by/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/simple select distinct/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/simple select where/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/select multiple join clause select/AggregatingMergeTree*": [
        (Fail, "AggregatingFunction problem with analyzer")
    ],
    "final/force/general/with experimental analyzer/select nested join clause select/AggregatingMergeTree*": [
        (Fail, "AggregatingFunction problem with analyzer")
    ],
    "final/force/general/with experimental analyzer/select nested subquery/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/select where subquery/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/select subquery/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/alias/as with alias/*": [(Fail, "fails for ARM")],
    "final/force/general/with experimental analyzer/simple select count/*_wview*": [
        (
            Fail,
            "Experimental WINDOW VIEW feature is not supported in the current infrastructure for query analysis. PR#62367",
            check_clickhouse_version(">=24.4"),
        )
    ],
    "final/force/alias/count with alias/distr_Log_:/*": [
        (Fail, "Storage Log doesn't support FINAL. Issue 63960.", check_analyzer())
    ],
    "final/force/alias/count with alias/distr_MergeTree_:/*": [
        (Fail, "Storage MergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/count with alias/distr_StripeLog_:/*": [
        (Fail, "Storage StripeLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/count with alias/distr_TinyLog_:/*": [
        (Fail, "Storage TinyLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/count with alias/distr_ReplicatedMergeTree_table:/*": [
        (Fail, "Storage ReplicatedMergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/distinct with alias/distr_Log_:/*": [
        (Fail, "Storage Log doesn't support FINAL. Issue 63960.", check_analyzer())
    ],
    "final/force/alias/distinct with alias/distr_MergeTree_:/*": [
        (Fail, "Storage MergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/distinct with alias/distr_StripeLog_:/*": [
        (Fail, "Storage StripeLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/distinct with alias/distr_TinyLog_:/*": [
        (Fail, "Storage TinyLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/distinct with alias/distr_ReplicatedMergeTree_table:/*": [
        (Fail, "Storage ReplicatedMergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/group by with :/distr_Log_:/*": [
        (Fail, "Storage Log doesn't support FINAL. Issue 63960.", check_analyzer())
    ],
    "final/force/alias/group by with :/distr_MergeTree_:/*": [
        (Fail, "Storage MergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/group by with :/distr_StripeLog_:/*": [
        (Fail, "Storage StripeLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/group by with :/distr_TinyLog_:/*": [
        (Fail, "Storage TinyLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/group by with :/distr_ReplicatedMergeTree_table:/*": [
        (Fail, "Storage ReplicatedMergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/order by :/distr_Log_:/*": [
        (Fail, "Storage Log doesn't support FINAL. Issue 63960.", check_analyzer())
    ],
    "final/force/alias/order by :/distr_MergeTree_:/*": [
        (Fail, "Storage MergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/order by :/distr_StripeLog_:/*": [
        (Fail, "Storage StripeLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/order by :/distr_TinyLog_:/*": [
        (Fail, "Storage TinyLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/order by :/distr_ReplicatedMergeTree_table:/*": [
        (Fail, "Storage ReplicatedMergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/limit :/distr_Log_:/*": [
        (Fail, "Storage Log doesn't support FINAL. Issue 63960.", check_analyzer())
    ],
    "final/force/alias/limit :/distr_MergeTree_:/*": [
        (Fail, "Storage MergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/limit :/distr_StripeLog_:/*": [
        (Fail, "Storage StripeLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/limit :/distr_TinyLog_:/*": [
        (Fail, "Storage TinyLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/limit :/distr_ReplicatedMergeTree_table:/*": [
        (Fail, "Storage ReplicatedMergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/select nested subquery with alias/distr_Log_:/*": [
        (Fail, "Storage Log doesn't support FINAL. Issue 63960.", check_analyzer())
    ],
    "final/force/alias/select nested subquery with alias/distr_MergeTree_:/*": [
        (Fail, "Storage MergeTree doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/select nested subquery with alias/distr_StripeLog_:/*": [
        (Fail, "Storage StripeLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/select nested subquery with alias/distr_TinyLog_:/*": [
        (Fail, "Storage TinyLog doesn't support FINAL.", check_analyzer())
    ],
    "final/force/alias/select nested subquery with alias/distr_ReplicatedMergeTree_table:/*": [
        (Fail, "Storage ReplicatedMergeTree doesn't support FINAL.", check_analyzer())
    ],
}

xflags = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@Name("selects")
@Specifications()
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """ClickHouse SELECT query regression suite."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("I have a clickhouse cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            docker_compose_project_dir=os.path.join(
                current_dir(), os.path.basename(current_dir()) + "_env"
            ),
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
                min_os_cpu_wait_time_ratio_to_throw=10,
                max_os_cpu_wait_time_ratio_to_throw=20,
            )

    Feature(run=load("selects.tests.final.feature", "module"))


if main():
    regression()
