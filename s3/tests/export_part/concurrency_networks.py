from testflows.core import *
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *
from alter.stress.tests.tc_netem import *


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


@TestScenario
def packet_delay(self, delay_ms):
    """Check that exports work correctly with packet delay."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I apply a packet delay"):
        network_packet_delay(node=self.context.node, delay_ms=delay_ms)

    with And("I export parts from the source table to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table="source",
                    destination_table=s3_table_name,
                )


@TestScenario
def packet_loss(self, percent_loss):
    """Check that exports work correctly with packet loss."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I apply packet loss"):
        network_packet_loss(node=self.context.node, percent_loss=percent_loss)

    with And("I export parts from the source table to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table="source",
                    destination_table=s3_table_name,
                )


@TestScenario
def packet_loss_gemodel(self, interruption_probability, recovery_probability):
    """Check that exports work correctly with packet loss using the GE model."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I apply packet loss using the GE model"):
        network_packet_loss_gemodel(
            node=self.context.node,
            interruption_probability=interruption_probability,
            recovery_probability=recovery_probability,
        )

    with And("I export parts from the source table to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table="source",
                    destination_table=s3_table_name,
                )


@TestScenario
def packet_corruption(self, percent_corrupt):
    """Check that exports work correctly with packet corruption."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I apply packet corruption"):
        network_packet_corruption(
            node=self.context.node, percent_corrupt=percent_corrupt
        )

    with And("I export parts from the source table to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table="source",
                    destination_table=s3_table_name,
                )


@TestScenario
def packet_duplication(self, percent_duplicated):
    """Check that exports work correctly with packet corruption."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I apply packet duplication"):
        network_packet_duplication(
            node=self.context.node, percent_duplicated=percent_duplicated
        )

    with And("I export parts from the source table to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table="source",
                    destination_table=s3_table_name,
                )


@TestScenario
def packet_reordering(self, delay_ms, percent_reordered):
    """Check that exports work correctly with packet corruption."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I apply packet reordering"):
        network_packet_reordering(
            node=self.context.node,
            delay_ms=delay_ms,
            percent_reordered=percent_reordered,
        )

    with And("I export parts from the source table to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table="source",
                    destination_table=s3_table_name,
                )


@TestScenario
def packet_rate_limit(self, rate_mbit):
    """Check that exports work correctly with packet corruption."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I apply packet rate limit"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=rate_mbit)

    with And("I export parts from the source table to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table="source",
                    destination_table=s3_table_name,
                )


@TestFeature
@Requirements(RQ_ClickHouse_ExportPart_Concurrency("1.0"))
@Name("concurrency and networks")
def feature(self):
    """Check that exports work correctly with concurrency and various network conditions."""

    Scenario(test=basic_concurrent_export)(threads=5)
    Scenario(test=packet_delay)(delay_ms=100)
    Scenario(test=packet_loss)(percent_loss=50)
    Scenario(test=packet_loss_gemodel)(
        interruption_probability=40, recovery_probability=70
    )
    Scenario(test=packet_corruption)(percent_corrupt=50)
    Scenario(test=packet_duplication)(percent_duplicated=50)  # How do I make this fail?
    Scenario(test=packet_reordering)(delay_ms=100, percent_reordered=90)  # And this?
    Scenario(test=packet_rate_limit)(rate_mbit=0.05)  # Am I using this right lol
