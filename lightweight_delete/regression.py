#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as argparser_base
from helpers.common import check_clickhouse_version
from lightweight_delete.requirements import *
from lightweight_delete.tests.steps import allow_experimental_lightweight_delete

xfails = {
    "views/materialized view": [(Fail, "not implemented")],
    "views/live view": [(Fail, "not implemented")],
    "views/window view": [(Fail, "not implemented")],
    "efficient physical data removal/delete and check size of the table": [
        (Fail, "Does not match space requirements.")
    ],
    "s3/s3": [(Fail, "not implemented")],
    "projections/simple projection": [(Fail, "engine type not supported.")],
    "replicated tables concurrent deletes/:/:": [(Fail, "engine type not supported.")],
    "replicated table with concurrent alter and delete/:": [
        (Fail, "engine type not supported")
    ],
    "replicated table with alter after delete on single node/:/:": [
        (Fail, "engine type not supported.")
    ],
    "distributed tables/:": [(Fail, "engine type not supported.")],
    "replication queue/:/replication queue": [(Fail, "engine type not supported.")],
    "replicated tables/:/:": [(Fail, "engine type not supported.")],
    "performance/performance large number of partitions": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/39870")
    ],
    "zookeeper load/load zookeeper": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/39870")
    ],
    "load/:": [(Fail, "https://github.com/ClickHouse/ClickHouse/issues/39870")],
    "drop empty part/drop empty part/": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/49909")
    ],
    "concurrent alter and delete/:/concurrent delete attach detach partition/": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/50922")
    ],
}

xflags = {}

ffails = {}


def argparser(parser):
    argparser_base(parser)
    parser.add_argument(
        "--use-alter-delete",
        action="store_true",
        help="Use alter delete instead of lightweight delete.",
    )

    parser.add_argument(
        "--force-run",
        action="store_true",
        help="Force running of lightweight delete suite on any ClickHouse version.",
    )


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("lightweight delete")
@Specifications(SRS023_ClickHouse_Lightweight_Delete)
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_DeleteStatement("1.0"),
    RQ_SRS_023_ClickHouse_LightweightDelete_SupportedTableEngines("1.0"),
)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    use_alter_delete=False,
    force_run=False,
    stress=None,
    parallel=None,
):
    """Lightweight Delete regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version
    self.context.use_alter_delete = use_alter_delete

    with Cluster(
        local,
        clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        nodes=nodes,
    ) as cluster:
        self.context.cluster = cluster
        self.context.stress = stress

        if parallel is not None:
            self.context.parallel = parallel

        if not force_run:
            if not use_alter_delete:
                if check_clickhouse_version("<22.8")(self):
                    skip(reason="only supported on ClickHouse version >= 22.8")

        if not use_alter_delete:
            with Given("I enable lightweight delete"):
                allow_experimental_lightweight_delete()

        Feature(
            run=load(
                "lightweight_delete.tests.acceptance_concurrent_alter_and_delete",
                "feature",
            )
        )
        Feature(run=load("lightweight_delete.tests.acceptance_column_ttl", "feature"))
        Feature(run=load("lightweight_delete.tests.backup", "feature"))
        Feature(run=load("lightweight_delete.tests.disk_space", "feature"))
        Feature(run=load("lightweight_delete.tests.zookeeper_load", "feature"))
        Feature(run=load("lightweight_delete.tests.load", "feature"))
        Feature(run=load("lightweight_delete.tests.acceptance", "feature"))
        Feature(
            run=load(
                "lightweight_delete.tests.acceptance_tiered_storage_ttl", "feature"
            )
        )
        Feature(
            run=load(
                "lightweight_delete.tests.efficient_physical_data_removal", "feature"
            )
        )
        Feature(
            run=load("lightweight_delete.tests.multiple_delete_limitations", "feature")
        )
        Feature(run=load("lightweight_delete.tests.hard_restart", "feature"))
        Feature(run=load("lightweight_delete.tests.s3", "feature"))
        Feature(run=load("lightweight_delete.tests.lack_of_disk_space", "feature"))
        Feature(run=load("lightweight_delete.tests.multi_disk", "feature"))
        Feature(run=load("lightweight_delete.tests.projections", "feature"))
        Feature(run=load("lightweight_delete.tests.drop_empty_part", "feature"))
        Feature(run=load("lightweight_delete.tests.views", "feature"))
        Feature(run=load("lightweight_delete.tests.compatibility", "feature"))
        Feature(run=load("lightweight_delete.tests.ontime_tests", "feature"))
        Feature(
            run=load(
                "lightweight_delete.tests.replicated_tables_concurrent_deletes",
                "feature",
            )
        )
        Feature(
            run=load(
                "lightweight_delete.tests.replicated_table_with_concurrent_alter_and_delete",
                "feature",
            )
        )
        Feature(
            run=load(
                "lightweight_delete.tests.replicated_table_with_alter_after_delete_on_single_node",
                "feature",
            )
        )
        Feature(
            run=load("lightweight_delete.tests.nondeterministic_functions", "feature")
        )
        Feature(run=load("lightweight_delete.tests.performance", "feature"))
        Feature(run=load("lightweight_delete.tests.distributed_tables", "feature"))
        Feature(run=load("lightweight_delete.tests.replication_queue", "feature"))
        Feature(run=load("lightweight_delete.tests.replicated_tables", "feature"))
        Feature(
            run=load(
                "lightweight_delete.tests.delete_and_tiered_storage_ttl", "feature"
            )
        )
        Feature(run=load("lightweight_delete.tests.encrypted_disk", "feature"))
        Feature(run=load("lightweight_delete.tests.delete_and_column_ttl", "feature"))
        Feature(run=load("lightweight_delete.tests.alter_after_delete", "feature"))
        Feature(run=load("lightweight_delete.tests.random_concurrent_alter", "feature"))
        Feature(
            run=load("lightweight_delete.tests.concurrent_alter_and_delete", "feature")
        )
        Feature(run=load("lightweight_delete.tests.concurrent_delete", "feature"))
        Feature(run=load("lightweight_delete.tests.invalid_where_clause", "feature"))
        Feature(run=load("lightweight_delete.tests.immediate_removal", "feature"))
        Feature(run=load("lightweight_delete.tests.basic_checks", "feature"))
        Feature(run=load("lightweight_delete.tests.specific_deletes", "feature"))


if main():
    regression()
