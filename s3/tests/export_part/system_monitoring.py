from testflows.core import *
from testflows.asserts import error
from s3.tests.export_part.steps import *
from s3.requirements.export_part import *


@TestScenario
def part_logging(self):
    """Check part exports are logged correctly in both system.events and system.part_log."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I read the initial logged number of part exports"):
        initial_events = get_export_events(node=self.context.node)
        initial_part_log = get_part_log(node=self.context.node)
        note(f"Initial events: {initial_events}")
        note(f"Initial part log: {initial_part_log}")

    # with When("I export parts to the S3 table"):
    #     export_parts(
    #         source_table="source",
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
def duplicate_logging(self):
    """Check duplicate exports are logged correctly in system.events."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I read the initial export events"):
        initial_events = get_export_events(node=self.context.node)

    with When("I try to export the parts twice"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table="source",
            destination_table=s3_table_name,
        )

    with And("Check logs for correct number of duplicate exports"):
        final_events = get_export_events(node=self.context.node)
        assert (
            final_events["PartsExportDuplicated"]
            - initial_events["PartsExportDuplicated"]
            == 5
        ), error()


@TestFeature
@Name("system monitoring")
@Requirements(RQ_ClickHouse_ExportPart_Logging("1.0"))
def feature(self):
    """Check system monitoring of export events."""

    # TODO
    # part_log is where to look
    # overwrite file
    # max bandwidth
    # some of system.events stuff wont appear unless i set this maybe? just a guess
    # system.events
    # Export row in system.metrics??
    # partsexports incrementing correctly
    # duplicates incrementing correctly

    Scenario(run=part_logging)
    # Scenario(run=duplicate_logging)
