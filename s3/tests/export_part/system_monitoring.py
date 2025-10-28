from testflows.core import *
from testflows.asserts import error

from s3.tests.export_part.steps import *


# TODO checks on export_events should go here, not in sanity.py
# partsexports incrementing correctly
# duplicates incrementing correctly


@TestScenario
def part_exports(self):
    """Check part exports are properly tracked in system.events."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True
        )

    with And("I read the initial logged number of part exports"):
        initial_exports = get_export_events(node=self.context.node)#.get("PartsExports", 0)
        note(f"Initial exports: {initial_exports}")
    
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


@TestFeature
@Name("system monitoring")
def feature(self):
    """Check system monitoring of export events."""

    Scenario(run=part_exports)
