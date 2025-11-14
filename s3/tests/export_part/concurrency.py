from testflows.core import *
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Concurrency("1.0"))
def concurrent_insert(self):
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
def concurrent_export(self, num_tables):
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


@TestFeature
@Name("concurrency")
def feature(self):
    """Check that exports work correctly with concurrency."""

    Scenario(test=concurrent_export)(num_tables=5)
    Scenario(test=concurrent_insert)
