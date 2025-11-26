from testflows.core import *
from testflows.asserts import error
from s3.tests.export_partition.steps import (
    export_partitions,
    source_matches_destination,
)
from s3.tests.export_part.steps import *
from helpers.common import getuid
from s3.requirements.export_partition import *


# TODO
# part_log is where to look
# overwrite file
# max bandwidth
# some of system.events stuff wont appear unless i set this maybe? just a guess
# system.events
# Export row in system.metrics??
# partsexports incrementing correctly
# duplicates incrementing correctly


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Logging("1.0"))
def part_exports(self):
    """Check part exports are properly tracked in system.part_log."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I read the initial logged number of part exports"):
        initial_exports = get_export_events(
            node=self.context.node
        )  # .get("PartsExports", 0)
        note(f"Initial exports: {initial_exports}")

    # with When("I export partitions to the S3 table"):
    #     export_partitions(
    #         source_table=source_table,
    #         destination_table=s3_table_name,
    #         node=self.context.node,
    #     )

    # with And("I read the final logged number of part exports"):
    #     final_exports = get_export_events(node=self.context.node).get("PartsExports", 0)

    # with Then("I check that the number of part exports is correct"):

    #     with By("Reading the number of parts for the source table"):
    #         num_parts = len(get_parts(table_name="source", node=self.context.node))

    #     with And("Checking that the before and after difference is correct"):
    #         assert final_exports - initial_exports == num_parts, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Idempotency("1.0"))
def duplicate_exports(self):
    """Check duplicate exports are ignored and not exported again."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I try to export the partitions twice"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    # with And("I read the initial export events"):

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("Check logs for duplicate exports"):
        export_events = get_export_events(node=self.context.node)
        note(export_events["PartsExports"])


@TestFeature
@Name("system monitoring")
@Requirements(
    RQ_ClickHouse_ExportPartition_Logging("1.0"),
    RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"),
    RQ_ClickHouse_ExportPartition_Idempotency("1.0"),
)
def feature(self):
    """Check system monitoring of export events."""

    # Scenario(run=part_exports)
    Scenario(run=duplicate_exports)
