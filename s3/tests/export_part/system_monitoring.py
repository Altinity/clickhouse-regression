from testflows.core import *
from testflows.asserts import error
from s3.tests.export_part.steps import *
from s3.requirements.export_part import *
from time import sleep


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Logging("1.0"))
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

    with And("I read the initial logged export events"):
        initial_events = get_export_events(node=self.context.node)

    with When("I export parts to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I read the final logged export events and part log"):
        final_events = get_export_events(node=self.context.node)
        part_log = get_part_log(node=self.context.node)

    with Then("I check that the number of part exports is correct"):
        assert (
            final_events["PartsExports"] - initial_events["PartsExports"] == 5
        ), error()

    with And("I check that the part log contains the correct parts"):
        parts = get_parts(table_name="source", node=self.context.node)
        for part in parts:
            assert part in part_log, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Idempotency("1.0"))
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


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_SystemTables_Exports("1.0"))
def system_exports_logging(self):
    """Check that system.exports table tracks export operations before they complete."""

    with Given(
        "I create a populated source table with large enough parts and empty S3 table"
    ):
        source_table = partitioned_merge_tree_table(
            table_name=f"source_{getuid()}",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_values=1000000,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("I check that system.exports contains some relevant parts"):
        exports = get_system_exports(node=self.context.node)
        assert len(exports) > 0, error()
        assert [source_table, s3_table_name] in exports, error()

    with And("I verify that system.exports empties after exports complete"):
        sleep(5)
        assert len(get_system_exports(node=self.context.node)) == 0, error()


@TestScenario
def background_move_pool_size(self):
    pass


@TestFeature
@Name("system monitoring")
@Requirements(RQ_ClickHouse_ExportPart_Logging("1.0"))
def feature(self):
    """Check system monitoring of export events."""

    Scenario(run=part_logging)
    Scenario(run=duplicate_logging)
    Scenario(run=system_exports_logging)
