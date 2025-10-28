from testflows.core import *
from testflows.asserts import error
from s3.tests.export_part.steps import *
from s3.requirements.export_part import *
from helpers.queries import *


# TODO replicated merge tree tables (all types)


@TestCheck
def configured_table(self, table_engine, number_of_partitions, number_of_parts):
    """Test a specific combination of table engine, number of partitions, and number of parts."""

    with Given("I create a populated source table and empty S3 table"):
        table_engine(
            table_name="source",
            partition_by="p",
            stop_merges=True,
            populate=True,
            number_of_partitions=number_of_partitions,
            number_of_parts=number_of_parts,
            columns=default_columns(simple=False),
        )
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, columns=default_columns(simple=False)
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


@TestSketch(Scenario)
@Flags(TE)
@Requirements(RQ_ClickHouse_ExportPart_SourceEngines("1.0"))
def table_combos(self):
    """Test various combinations of table engines, number of partitions, and number of parts."""

    tables = [
        partitioned_merge_tree_table,
        partitioned_replacing_merge_tree_table,
        partitioned_summing_merge_tree_table,
        partitioned_collapsing_merge_tree_table,
        partitioned_versioned_collapsing_merge_tree_table,
        partitioned_aggregating_merge_tree_table,
        partitioned_graphite_merge_tree_table,
    ]
    # TODO expand combos
    number_of_partitions = [5]
    number_of_parts = [1]

    configured_table(
        table_engine=either(*tables),
        number_of_partitions=either(*number_of_partitions),
        number_of_parts=either(*number_of_parts),
    )


@TestFeature
@Name("engines")
def feature(self):
    """Check exporting parts to S3 storage with different table engines."""

    Scenario(run=table_combos)
