from testflows.core import *
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *


@TestScenario
def basic_concurrent_export(self, threads):
    """Check concurrent exports from different sources to the same S3 table."""

    with Given(f"I create {threads} populated source tables and an empty S3 table"):
        for i in range(threads):
            partitioned_merge_tree_table(
                table_name=f"source{i}",
                partition_by="p",
                columns=default_columns(),
                stop_merges=True,
            )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export parts from all sources concurrently to the S3 table"):
        for i in range(threads):
            Step(test=export_parts, parallel=True)(
                source_table=f"source{i}",
                destination_table=s3_table_name,
                node=self.context.node,
            )
        join()

    with And("I read data from all tables"):
        source_data = []
        for i in range(threads):
            data = select_all_ordered(table_name=f"source{i}", node=self.context.node)
            source_data.extend(data)
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with Then("All data should be present in the S3 table"):
        assert set(source_data) == set(destination_data), error()


@TestFeature
@Requirements(RQ_ClickHouse_ExportPart_Concurrency("1.0"))
@Name("concurrency and networks")
def feature(self):
    """Check that exports work correctly with concurrency and various network conditions."""

    Scenario(test=basic_concurrent_export)(threads=5)
    # Scenario(test=network_packet_delay)(delay_ms=100)
    # Scenario(test=network_packet_loss)(percent_loss=50)
    # Scenario(test=network_packet_loss_gemodel)(interruption_probability=10, recovery_probability=90)
    # Scenario(test=network_packet_corruption)(percent_corrupt=20)
    # Scenario(test=network_packet_duplication)(percent_duplicated=10)
    # Scenario(test=network_packet_reordering)(delay_ms=100, percent_reordered=90)
    # Scenario(test=network_packet_rate_limit)(rate_mbit=10)