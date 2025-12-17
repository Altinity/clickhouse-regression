import time
import uuid

from testflows.core import *
from testflows.asserts import error
from s3.tests.export_partition.steps import (
    export_partitions,
    kill_export_partition,
    get_partitions,
    create_s3_table,
    default_columns,
    check_killed_export_status,
    check_export_status,
)
from helpers.create import partitioned_replicated_merge_tree_table
from helpers.common import getuid
from helpers.kill import kill_query_by_id
from helpers.queries import select_all_ordered
from alter.stress.tests.tc_netem import network_packet_rate_limit
from s3.requirements.export_partition import *


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_QueryCancellation_KillExportPartition("1.0")
)
def kill_export_partition_command(self):
    """Check that KILL EXPORT PARTITION command can cancel in-progress partition exports."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            cluster="replicated_cluster",
            number_of_partitions=5,
            number_of_parts=10,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get partitions to export"):
        partitions = get_partitions(table_name=source_table, node=self.context.node)
        partition_to_export = partitions[0]

    with And("I slow the network to make export take longer"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with When("I start exporting a partition"):
        Step(test=export_partitions, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            partitions=[partition_to_export],
            check_export=False,
        )

        time.sleep(0.001)

        Step(test=kill_export_partition, parallel=True)(
            partition_id=partition_to_export,
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

        join()

    with Then("I verify the export was killed"):
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                check_killed_export_status(
                    source_table=source_table, partition_id=partition_to_export
                )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_QueryCancellation_KillQuery("1.0"))
def kill_export_partition_with_kill_query(self):
    """Check if KILL QUERY command can cancel in-progress partition exports."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            cluster="replicated_cluster",
            number_of_partitions=5,
            number_of_parts=10,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get partitions to export"):
        partitions = get_partitions(table_name=source_table, node=self.context.node)
        partition_to_export = partitions[0]

    with And("I save the source table data before export"):
        source_data_before = select_all_ordered(
            table_name=source_table, node=self.context.node
        )

    with And("I slow the network to make export take longer"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with When("I start exporting a partition with a known query_id"):
        query_id = str(uuid.uuid4())
        settings = list(self.context.default_settings) + [("query_id", query_id)]

        Step(test=export_partitions, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            partitions=[partition_to_export],
            check_export=False,
            settings=settings,
        )

        time.sleep(0.5)

        Step(test=kill_query_by_id, parallel=True)(
            query_id=query_id,
            node=self.context.node,
            sync=True,
        )

        join()

    with Then(
        "I verify the export entry does not exist in system.replicated_partition_exports"
    ):
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                check_export_status(
                    status="COMPLETED",
                    source_table=source_table,
                    partition_id=partition_to_export,
                    node=self.context.node,
                )

                check_killed_export_status(
                    source_table=source_table,
                    partition_id=partition_to_export,
                    populated=False,
                )

    with And("I verify the source table is still populated"):
        source_data_after = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        assert source_data_before == source_data_after, error(
            "Source table data should remain unchanged after KILL QUERY"
        )


@TestFeature
@Name("kill")
@Requirements(RQ_ClickHouse_ExportPartition_QueryCancellation("1.0"))
def feature(self):
    """Check that KILL commands can cancel in-progress partition exports."""

    Scenario(run=kill_export_partition_command)
    Scenario(run=kill_export_partition_with_kill_query)
