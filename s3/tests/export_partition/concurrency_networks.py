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


@TestScenario
def concurrent_insert(self):
    """Check that exports work correctly with concurrent inserts of source data."""

    with Given("I create an empty source and S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
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
            table_name="source",
            number_of_partitions=5,
            number_of_parts=1,
        )
        Step(test=export_parts, parallel=True)(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )
        join()

    with Then("Destination data should be a subset of source data"):
        source_data = select_all_ordered(table_name="source", node=self.context.node)
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )
        assert set(source_data) >= set(destination_data), error()

    with And("Inserts should have completed successfully"):
        assert len(source_data) == 15, error()


@TestScenario
def export_and_drop(self):
    """Check that dropping a column immediately after export works correctly."""
    pause()
    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        # s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)
        # drop_column(
        #     node=self.context.node,
        #     table_name="source",
        #     column_name="i",
        # )

    # with When("I export data then drop a column"):
    #     export_parts(
    #         source_table="source",
    #         destination_table=s3_table_name,
    #         node=self.context.node,
    #     )
    #     drop_column(
    #         node=self.context.node,
    #         table_name="source",
    #         column_name="i",
    #     )
    # This drop freezes the test ☠️☠️☠️


@TestStep(When)
def kill_minio(self, cluster=None, container_name="s3_env-minio1-1", signal="KILL"):
    """Forcefully kill MinIO container to simulate network crash."""

    if cluster is None:
        cluster = self.context.cluster

    retry(cluster.command, 5)(
        None,
        f"docker kill --signal={signal} {container_name}",
        timeout=60,
        exitcode=0,
        steps=False,
    )


@TestStep(When)
def start_minio(self, cluster=None, container_name="s3_env-minio1-1", timeout=300):
    """Start MinIO container and wait for it to be ready."""

    if cluster is None:
        cluster = self.context.cluster

    with By("starting MinIO container"):
        retry(cluster.command, 5)(
            None,
            f"docker start {container_name}",
            timeout=timeout,
            exitcode=0,
            steps=True,
        )

    with And("waiting for MinIO to be ready"):
        for attempt in retries(timeout=timeout, delay=1):
            with attempt:
                result = cluster.command(
                    None,
                    f"docker exec {container_name} curl -f http://localhost:9001/minio/health/live",
                    timeout=10,
                    steps=False,
                    no_checks=True,
                )
                if result.exitcode != 0:
                    fail("MinIO health check failed")


@TestScenario
def restart_minio(self):
    """Check that restarting MinIO after exporting data works correctly."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I kill MinIO"):
        kill_minio()

    with When("I export data"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I restart MinIO"):
        start_minio()

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

    # TODO corruption (bit flipping)

    Scenario(test=basic_concurrent_export)(threads=5)
    Scenario(test=packet_delay)(delay_ms=100)
    Scenario(test=packet_loss)(percent_loss=50)
    Scenario(test=packet_loss_gemodel)(
        interruption_probability=40, recovery_probability=70
    )
    Scenario(test=packet_corruption)(percent_corrupt=50)
    Scenario(test=packet_duplication)(percent_duplicated=50)
    Scenario(test=packet_reordering)(delay_ms=100, percent_reordered=90)
    Scenario(test=packet_rate_limit)(rate_mbit=0.05)
    Scenario(run=concurrent_insert)
    Scenario(run=restart_minio)

    # Scenario(run=export_and_drop)
