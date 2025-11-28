from time import sleep
import random
from testflows.core import *
from testflows.combinatorics import product
from helpers.common import getuid
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *
from alter.stress.tests.tc_netem import *


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_NetworkResilience_PacketIssues("1.0"))
def packet_delay(self, delay_ms):
    """Check that exports work correctly with packet delay."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I apply a packet delay"):
        network_packet_delay(node=self.context.node, delay_ms=delay_ms)

    with And("I export parts from the source table to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table=source_table,
                    destination_table=s3_table_name,
                )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_NetworkResilience_PacketIssues("1.0"))
def packet_loss(self, percent_loss):
    """Check that exports work correctly with packet loss."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I apply packet loss"):
        network_packet_loss(node=self.context.node, percent_loss=percent_loss)

    with And("I export parts from the source table to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table=source_table,
                    destination_table=s3_table_name,
                )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_NetworkResilience_PacketIssues("1.0"))
def packet_loss_gemodel(self, interruption_probability, recovery_probability):
    """Check that exports work correctly with packet loss using the GE model."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
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
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table=source_table,
                    destination_table=s3_table_name,
                )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_NetworkResilience_PacketIssues("1.0"))
def packet_corruption(self, percent_corrupt):
    """Check that exports work correctly with packet corruption."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
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
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table=source_table,
                    destination_table=s3_table_name,
                )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_NetworkResilience_PacketIssues("1.0"))
def packet_duplication(self, percent_duplicated):
    """Check that exports work correctly with packet corruption."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
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
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table=source_table,
                    destination_table=s3_table_name,
                )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_NetworkResilience_PacketIssues("1.0"))
def packet_reordering(self, delay_ms, percent_reordered):
    """Check that exports work correctly with packet corruption."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
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
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table=source_table,
                    destination_table=s3_table_name,
                )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_NetworkResilience_PacketIssues("1.0"))
def packet_rate_limit(self, rate_mbit):
    """Check that exports work correctly with packet corruption."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I apply packet rate limit"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=rate_mbit)

    with And("I export parts from the source table to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    for retry in retries(timeout=30, delay=1):
        with retry:
            with Then("Check source matches destination"):
                source_matches_destination(
                    source_table=source_table,
                    destination_table=s3_table_name,
                )


def get_minio_interruption_strategies():
    strategies = ["before", "during", "after", "random"]
    signals = ["KILL", "TERM", "SEGV"]
    return product(strategies, signals)


@TestOutline(Scenario)
@Examples(
    "strategy, signal",
    get_minio_interruption_strategies(),
)
@Requirements(RQ_ClickHouse_ExportPart_NetworkResilience_DestinationInterruption("1.0"))
def minio_interruption(self, strategy, signal):
    """Check that MinIO outages at different times during exports work correctly."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I slow the network to make export take longer"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    if strategy == "before":
        with When("I kill MinIO before export"):
            kill_minio(signal=signal)
            export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
            )

    elif strategy == "during":
        with When("I kill MinIO during export"):
            export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
            )
            kill_minio(signal=signal)

    elif strategy == "after":
        with When("I export data"):
            export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
            )

        with And("I kill MinIO after export"):
            wait_for_all_exports_to_complete()
            kill_minio(signal=signal)

    elif strategy == "random":
        with When("I kill MinIO at a random time during export"):
            export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
            )
            sleep(random.uniform(0, 3))
            kill_minio(signal=signal)

    with Then("I start MinIO"):
        start_minio()

    if strategy == "after":
        with And("Check source matches destination"):
            source_matches_destination(
                source_table=source_table,
                destination_table=s3_table_name,
            )
    else:
        with And("Destination data should be a subset of source data"):
            source_data = select_all_ordered(
                table_name=source_table, node=self.context.node
            )
            destination_data = select_all_ordered(
                table_name=s3_table_name, node=self.context.node
            )
            assert set(source_data) >= set(destination_data), error()


def get_clickhouse_interruption_strategies():
    strategies = ["before", "during", "after", "random"]
    signals = ["KILL", "TERM", "SEGV"]
    safe_values = [True, False]
    return product(strategies, signals, safe_values)


@TestOutline(Scenario)
@Examples(
    "strategy, signal, safe",
    get_clickhouse_interruption_strategies(),
)
@Requirements(RQ_ClickHouse_ExportPart_NetworkResilience_NodeInterruption("1.0"))
def clickhouse_interruption(self, strategy, signal, safe):
    """Check that exports work correctly with ClickHouse outages."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get parts before the interruption"):
        parts = get_parts(table_name=source_table, node=self.context.node)

    with And("I slow the network to make export take longer"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    if strategy == "before":
        with When("I stop ClickHouse before export"):
            self.context.node.stop_clickhouse(safe=safe, signal=signal)
            export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
                parts=parts,
                exitcode=1,
            )

    elif strategy == "during":
        with When("I stop ClickHouse during export"):
            export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
                parts=parts,
            )
            self.context.node.stop_clickhouse(safe=safe, signal=signal)

    elif strategy == "after":
        with When("I export data"):
            export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
                parts=parts,
            )

        with And("I stop ClickHouse after export"):
            wait_for_all_exports_to_complete()
            self.context.node.stop_clickhouse(safe=safe, signal=signal)

    elif strategy == "random":
        with When("I kill ClickHouse at a random time during export"):
            export_parts(
                source_table=source_table,
                destination_table=s3_table_name,
                node=self.context.node,
                parts=parts,
            )
            sleep(random.uniform(0, 3))
            self.context.node.stop_clickhouse(safe=safe, signal=signal)

    with Then("I start ClickHouse"):
        self.context.node.start_clickhouse(thread_fuzzer=True)

    with And("I get data from both tables"):
        wait_for_all_exports_to_complete()
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    if strategy == "before":
        with And("Destination should be empty"):
            assert len(destination_data) == 0, error()
    elif strategy == "after" or safe == True:
        with And("Destination matches source"):
            assert source_data == destination_data, error()
    else:
        with And("Destination data should be a subset of source data"):
            assert set(source_data) >= set(destination_data), error()


@TestFeature
@Name("network")
def feature(self):
    """Check that exports work correctly with various network conditions."""

    Scenario(test=packet_delay)(delay_ms=100)
    Scenario(test=packet_loss)(percent_loss=50)
    Scenario(test=packet_loss_gemodel)(
        interruption_probability=40, recovery_probability=70
    )
    Scenario(test=packet_corruption)(percent_corrupt=50)
    Scenario(test=packet_duplication)(percent_duplicated=50)
    Scenario(test=packet_reordering)(delay_ms=100, percent_reordered=90)
    Scenario(test=packet_rate_limit)(rate_mbit=0.05)
    Scenario(run=minio_interruption)
    Scenario(run=clickhouse_interruption)
