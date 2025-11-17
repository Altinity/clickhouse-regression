from time import sleep
from testflows.core import *
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *
from alter.stress.tests.tc_netem import *


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Concurrency("1.0"))
def parallel_insert(self):
    """Check that exports work correctly with concurrent inserts of source data."""

    with Given("I create an empty source and S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            populate=False,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When(
        "I insert data and export it in parallel",
        description="""
        5 partitions with 1 part each are inserted.
        The export is queued in parallel and usually behaves by exporting
        a snapshot of the source data, often getting just the first partition
        which means the export happens right after the first INSERT query completes.
    """,
    ):
        Step(test=create_partitions_with_random_uint64, parallel=True)(
            table_name=source_table,
            number_of_partitions=5,
            number_of_parts=1,
        )
        Step(test=export_parts, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )
        join()

    with Then("Destination data should be a subset of source data"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )
        assert set(source_data) >= set(destination_data), error()

    with And("Inserts should have completed successfully"):
        assert len(source_data) == 15, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Concurrency("1.0"))
def multiple_sources_same_destination(self, num_tables):
    """Check concurrent exports from different sources to the same S3 table."""

    with Given(f"I create {num_tables} populated source tables and an empty S3 table"):
        source_tables, destination_tables = concurrent_export_tables(
            num_tables=num_tables
        )

    with And("I read data from all tables"):
        source_data = []
        destination_data = []
        for i in range(num_tables):
            data = select_all_ordered(
                table_name=source_tables[i], node=self.context.node
            )
            source_data.extend(data)
            data = select_all_ordered(
                table_name=destination_tables[i], node=self.context.node
            )
            destination_data.extend(data)

    with Then("All data should be present in the S3 table"):
        assert set(source_data) == set(destination_data), error()

    with And("Exports should have run concurrently"):
        verify_export_concurrency(node=self.context.node, source_tables=source_tables)


@TestScenario
def select_parts(self):
    """Test selecting from the source table before, during, and after exports."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(simple=False),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False),
        )

    with And("I select data from the source table before exporting parts"):
        before_export_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )

    with When("I slow the network"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with And("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I select data from the source table during exporting parts"):
        during_export_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )

    with And("I select data from the source and destination after exporting parts"):
        sleep(5)
        after_export_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with Then("Check data is consistent before, during, and after exports"):
        assert before_export_data == during_export_data, error()
        assert during_export_data == after_export_data, error()
        assert before_export_data == after_export_data, error()
        assert before_export_data == destination_data, error()


@TestScenario
def merge_parts(self):
    """Test merging parts from the source table before, during, and after exporting parts."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            number_of_parts=2,
            columns=default_columns(simple=False),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False),
        )

    with And("I optimize partition 1 before export"):
        optimize_partition(
            table_name=source_table,
            partition="1",
        )

    with And("I read source parts before export"):
        source_parts_before_export = get_parts_per_partition(table_name=source_table)

    with When("I slow the network to make export take longer"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with And("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I optimize partition 2 during export"):
        optimize_partition(
            table_name=source_table,
            partition="2",
        )

    with And("I optimize partition 3 after export"):
        sleep(5)
        optimize_partition(
            table_name=source_table,
            partition="3",
        )

    with Then("I verify destination partition structure is correct"):
        destination_parts_after_export = get_s3_parts_per_partition(
            table_name=s3_table_name
        )
        assert destination_parts_after_export == source_parts_before_export, error()

    with And("Source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("Final partition structure is correct"):
        source_parts_after_export = get_parts_per_partition(table_name=source_table)
        assert source_parts_after_export == {
            "1": 1,
            "2": 1,
            "3": 1,
            "4": 2,
            "5": 2,
        }, error()
        assert destination_parts_after_export == {
            "1": 1,
            "2": 2,
            "3": 2,
            "4": 2,
            "5": 2,
        }, error()


@TestFeature
@Name("concurrent other")
def feature(self):
    """Check that exports work correctly with explicitly parallel tests."""

    Scenario(test=multiple_sources_same_destination)(num_tables=5)
    Scenario(run=parallel_insert)
    Scenario(run=select_parts)
    Scenario(run=merge_parts)
