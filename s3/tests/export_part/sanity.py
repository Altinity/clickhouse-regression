from testflows.core import *
from testflows.asserts import error
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *
from alter.table.replace_partition.partition_types import *


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Settings_AllowExperimental("1.0"))
def export_setting(self):
    """Check that the export setting is settable in 2 ways when exporting parts."""

    with Given("I create a populated source table and 2 empty S3 tables"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name1 = create_s3_table(table_name="s3_1", create_new_bucket=True)
        s3_table_name2 = create_s3_table(table_name="s3_2")

    with When("I export parts to the first S3 table using the SET query"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name1,
            node=self.context.node,
            explicit_set=1,
        )

    with And("I export parts to the second S3 table using the settings argument"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name2,
            node=self.context.node,
            explicit_set=0,
        )

    with And("I read data from all tables"):
        source_data = select_all_ordered(table_name="source", node=self.context.node)
        destination_data1 = select_all_ordered(
            table_name=s3_table_name1, node=self.context.node
        )
        destination_data2 = select_all_ordered(
            table_name=s3_table_name2, node=self.context.node
        )

    with Then("All tables should have the same data"):
        assert source_data == destination_data1, error()
        assert source_data == destination_data2, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_SchemaCompatibility("1.0"))
def mismatched_columns(self):
    """Test exporting parts when source and destination tables have mismatched columns."""

    with Given("I create a source table and S3 table with different columns"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False),
        )

    with When("I export parts to the S3 table"):
        results = export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
            exitcode=1,
        )

    with Then("I should see an error related to mismatched columns"):
        assert results[0].exitcode == 122, error()
        assert "Tables have different structure" in results[0].output, error()


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPart_S3("1.0"),
    RQ_ClickHouse_ExportPart_SQLCommand("1.0"),
)
def basic_table(self):
    """Test exporting parts of a basic table."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export parts to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I read data from both tables"):
        source_data = select_all_ordered(table_name="source", node=self.context.node)
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with Then("They should be the same"):
        assert source_data == destination_data, error()


@TestScenario
def empty_table(self):
    """Test exporting parts from an empty table."""

    with Given("I create empty source and S3 tables"):
        partitioned_merge_tree_table(
            table_name="empty_source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            populate=False,
        )
        s3_table_name = create_s3_table(table_name="empty_s3", create_new_bucket=True)

    with When("I export parts to the S3 table"):
        export_parts(
            source_table="empty_source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I read data from both tables"):
        source_data = select_all_ordered(
            table_name="empty_source", node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with Then("They should be empty"):
        assert source_data == [], error()
        assert destination_data == [], error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_PartitionKeyTypes("1.0"))
def no_partition_by(self):
    """Test exporting parts when the source table has no PARTITION BY type."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="tuple()",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, partition_by="tuple()"
        )

    with When("I export parts to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I read data from both tables"):
        source_data = select_all_ordered(table_name="source", node=self.context.node)
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with Then("They should be the same"):
        assert source_data == destination_data, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_PartTypes("1.0"))
def wide_and_compact_parts(self):
    """Check that exporting with both wide and compact parts is supported."""

    with Given("I create a source table with wide and compact parts"):
        table_with_compact_and_wide_parts(table_name="source")
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export parts to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I read data from both tables"):
        source_data = select_all_ordered(table_name="source", node=self.context.node)
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with Then("They should be the same"):
        assert source_data == destination_data, error()


@TestFeature
@Name("sanity")
def feature(self):
    """Check basic functionality of exporting data parts to S3 storage."""

    Scenario(run=empty_table)
    Scenario(run=basic_table)
    Scenario(run=no_partition_by)
    Scenario(run=mismatched_columns)
    Scenario(run=wide_and_compact_parts)
    # Scenario(run=export_setting) # This test fails because of an actual bug in the export setting
