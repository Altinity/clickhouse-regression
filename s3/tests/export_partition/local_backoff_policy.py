from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.create import partitioned_replicated_merge_tree_table
from helpers.queries import select_all_ordered
from s3.requirements.export_partition import *
from s3.tests.export_partition.steps import (
    get_partitions,
    create_s3_table,
    default_columns,
    source_matches_destination,
    wait_for_export_to_complete,
    get_exception_count,
    RETRYABLE_FAILPOINT,
    NON_RETRYABLE_FAILPOINT,
    INITIAL_BACKOFF_SECONDS,
    MAX_BACKOFF_SECONDS,
    TASK_TIMEOUT_SECONDS,
    enable_failpoint,
    disable_failpoint,
    stop_moves,
    start_moves,
    start_export,
    wait_for_export_status,
    get_export_status,
    get_local_backoff_count,
    wait_for_local_backoff,
    get_local_backoff_column_type,
    export_partitions,
)


@TestStep(Given)
def populated_source_and_s3_table(
    self, number_of_partitions=1, number_of_parts=3, destination_cluster=None
):
    """Create a populated replicated source table and an empty S3 destination table.

    ``destination_cluster`` controls where the S3 destination table is created. It
    defaults to ``None`` (only the initiating node). Scenarios that expect a
    replica other than the initiator to complete the export must pass the cluster
    name so every replica has a destination table to write to — otherwise a
    healthy replica has nothing to export into and the task can only ever be
    finished by the initiating node.
    """
    source_table = f"source_{getuid()}"
    partitioned_replicated_merge_tree_table(
        table_name=source_table,
        partition_by="p",
        columns=default_columns(),
        stop_merges=True,
        number_of_partitions=number_of_partitions,
        number_of_parts=number_of_parts,
        cluster="replicated_cluster",
    )
    s3_table_name = create_s3_table(
        table_name="s3", create_new_bucket=True, cluster=destination_cluster
    )
    return source_table, s3_table_name


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_RetryMechanism("1.1"))
def backoff_settings_accepted(self):
    """Check that the new per-part back-off settings are accepted and the export succeeds."""

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table(
            number_of_partitions=2, number_of_parts=2
        )

    with When("I export partitions with the new back-off settings"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            settings=[
                (INITIAL_BACKOFF_SECONDS, "1"),
                (MAX_BACKOFF_SECONDS, "5"),
            ],
        )

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def local_backoff_per_part_column(self):
    """Check that system.replicated_partition_exports exposes the local_backoff_per_part column."""

    with When("I read the local_backoff_per_part column type"):
        column_type = get_local_backoff_column_type()

    with Then("its nested type should expose part, attempts and next_retry_time"):
        assert "part" in column_type, error()
        assert "attempts" in column_type, error()
        assert "next_retry_time" in column_type, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_RetryMechanism("1.1"))
def non_retryable_error_fails_task(self):
    """Check that a non-retryable part-export error fails the whole task immediately."""

    node = self.context.node

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table()
        partition = get_partitions(table_name=source_table, node=node)[0]

    with When("I enable the non-retryable failpoint on all nodes"):
        enable_failpoint(failpoint=NON_RETRYABLE_FAILPOINT)

    try:
        with And("I start exporting the partition"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=node,
            )

        with Then("the export task transitions to FAILED"):
            wait_for_export_status(
                source_table=source_table,
                partition=partition,
                status="FAILED",
                timeout=60,
            )

        with And("an exception is recorded for the failed export"):
            assert (
                int(get_exception_count(source_table=source_table).output.strip()) > 0
            ), error()

        with And("no rows reach the destination"):
            destination_data = select_all_ordered(table_name=s3_table_name, node=node)
            assert len(destination_data) == 0, error()
    finally:
        with Finally("I disable the non-retryable failpoint on all nodes"):
            disable_failpoint(failpoint=NON_RETRYABLE_FAILPOINT)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_RetryMechanism("1.1"))
def retryable_error_stays_pending_and_backs_off(self):
    """Check that a retryable part-export error keeps the task PENDING and records a local back-off."""

    node = self.context.node

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table()
        partition = get_partitions(table_name=source_table, node=node)[0]

    with When("I enable the retryable failpoint on all nodes"):
        enable_failpoint(failpoint=RETRYABLE_FAILPOINT)

    try:
        with And("I start exporting the partition with a short back-off"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=node,
                settings=[
                    (INITIAL_BACKOFF_SECONDS, "1"),
                    (MAX_BACKOFF_SECONDS, "2"),
                ],
            )

        with Then("a local back-off entry appears on the failing replica"):
            wait_for_local_backoff(source_table=source_table, partition=partition)

        with And("the task stays PENDING instead of failing on a retry budget"):
            status = get_export_status(source_table=source_table, partition=partition)
            assert status == "PENDING", error(
                f"Retryable failures must keep the task PENDING, got {status!r}"
            )
    finally:
        with Finally("I disable the retryable failpoint on all nodes"):
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_RetryMechanism("1.1"),
    RQ_ClickHouse_ExportPartition_ResumeAfterFailure("1.0"),
)
def retryable_error_recovers_after_failpoint_cleared(self):
    """Check that a retryable export recovers and completes once the transient failure clears."""

    node = self.context.node

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table()
        partition = get_partitions(table_name=source_table, node=node)[0]

    with When("I enable the retryable failpoint on all nodes"):
        enable_failpoint(failpoint=RETRYABLE_FAILPOINT)

    try:
        with And("I start exporting the partition with a short back-off"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=node,
                settings=[
                    (INITIAL_BACKOFF_SECONDS, "1"),
                    (MAX_BACKOFF_SECONDS, "2"),
                ],
            )

        with And("I wait until the retryable failure is recorded"):
            wait_for_local_backoff(source_table=source_table, partition=partition)
    finally:
        with When("I disable the retryable failpoint on all nodes"):
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT)

    with Then("the export completes once the failure clears"):
        wait_for_export_to_complete(
            source_table=source_table, partition_id=partition, node=node
        )

    with And("source matches destination"):
        for retry in retries(timeout=30, delay=1):
            with retry:
                source_matches_destination(
                    source_table=source_table,
                    destination_table=s3_table_name,
                )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_RetryMechanism("1.1"))
def retryable_error_killed_on_timeout(self):
    """Check that a retryable export is KILLED once the task timeout elapses."""

    node = self.context.node

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table()
        partition = get_partitions(table_name=source_table, node=node)[0]

    with When("I enable the retryable failpoint on all nodes"):
        enable_failpoint(failpoint=RETRYABLE_FAILPOINT)

    try:
        with And("I start exporting the partition with a short task timeout"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=node,
                settings=[
                    (TASK_TIMEOUT_SECONDS, "5"),
                    (INITIAL_BACKOFF_SECONDS, "1"),
                    (MAX_BACKOFF_SECONDS, "2"),
                ],
            )

        with Then("the export is not failed on a retry budget but KILLED on timeout"):
            wait_for_export_status(
                source_table=source_table,
                partition=partition,
                status="KILLED",
                timeout=120,
            )

        with And("an exception is recorded for the killed export"):
            assert (
                int(get_exception_count(source_table=source_table).output.strip()) > 0
            ), error()

        with And("no rows reach the destination"):
            destination_data = select_all_ordered(table_name=s3_table_name, node=node)
            assert len(destination_data) == 0, error()
    finally:
        with Finally("I disable the retryable failpoint on all nodes"):
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_RetryMechanism("1.1"),
    RQ_ClickHouse_ExportPartition_ResumeAfterFailure("1.0"),
)
def local_backoff_is_replica_local(self):
    """Check that the local back-off is replica-local: a replica that backs off must
    not block another replica from completing the same part, and the back-off state
    must only appear on the affected replica.

    The hand-off is orchestrated deterministically with SYSTEM STOP/START MOVES,
    mirroring the upstream integration test
    ``test_export_partition_local_backoff_does_not_block_other_replica``. Without
    this two-phase control the failing replica wakes on its own back-off expiry
    (~1-2s) and re-locks the freed part before the healthy replicas' coarser
    (~5s) scheduler tick, starving them and stalling the export until the task
    timeout. See ``export_partition_local_backoff_policy.md`` for details.
    """

    failing_node = self.context.nodes[0]
    healthy_nodes = [n for n in self.context.nodes if n is not failing_node]

    with Given("I create a populated source table and an S3 table on every replica"):
        source_table, s3_table_name = populated_source_and_s3_table(
            destination_cluster="replicated_cluster"
        )
        partition = get_partitions(table_name=source_table, node=failing_node)[0]

    with And("I stop moves on the healthy replicas so the failing replica exports first"):
        stop_moves(source_table=source_table, nodes=healthy_nodes)

    with And("I enable the retryable failpoint on the failing replica only"):
        enable_failpoint(failpoint=RETRYABLE_FAILPOINT, nodes=[failing_node])

    try:
        with When("I start exporting the partition with a short back-off on the failing replica"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=failing_node,
                settings=[
                    (INITIAL_BACKOFF_SECONDS, "1"),
                    (MAX_BACKOFF_SECONDS, "2"),
                ],
            )

        with Then("a local back-off entry appears on the failing replica"):
            wait_for_local_backoff(
                source_table=source_table,
                partition=partition,
                nodes=[failing_node],
            )

        with And("the task stays PENDING instead of failing on a retry budget"):
            status = get_export_status(
                source_table=source_table, partition=partition, node=failing_node
            )
            assert status == "PENDING", error(
                f"Retryable failures must keep the task PENDING, got {status!r}"
            )

        with And("the back-off state has not leaked to the healthy replicas"):
            for healthy in healthy_nodes:
                count = get_local_backoff_count(
                    source_table=source_table,
                    partition=partition,
                    node=healthy,
                )
                assert count == 0, error(
                    f"Local back-off must be replica-local, healthy replica reported {count} entries"
                )

        with When("I resume moves on the healthy replicas"):
            start_moves(source_table=source_table, nodes=healthy_nodes)

        with Then("the export completes because a healthy replica exports the part"):
            wait_for_export_to_complete(
                source_table=source_table,
                partition_id=partition,
                node=healthy_nodes[0],
            )

        with And("source matches destination"):
            for retry in retries(timeout=30, delay=1):
                with retry:
                    source_matches_destination(
                        source_table=source_table,
                        destination_table=s3_table_name,
                    )
    finally:
        with Finally("I disable the retryable failpoint on the affected replica"):
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT, nodes=[failing_node])

        with Finally("I resume moves on all replicas"):
            start_moves(source_table=source_table, nodes=self.context.nodes)


@TestFeature
@Name("local backoff policy")
@Requirements(
    RQ_ClickHouse_ExportPartition_RetryMechanism("1.1"),
    RQ_ClickHouse_ExportPartition_ResumeAfterFailure("1.0"),
)
def feature(self):
    """Check the per-part local back-off policy for export partition (Altinity/ClickHouse#1984).

    Failures are split into two kinds:
    * Non-retryable errors (schema/type incompatibilities) fail the whole task
      immediately as FAILED.
    * Retryable errors (transient network/object-storage/Keeper/memory failures)
      are retried with a per-replica in-memory exponential back-off until the
      export succeeds or the absolute task timeout elapses (task becomes KILLED).
    """

    Scenario(run=backoff_settings_accepted)
    Scenario(run=local_backoff_per_part_column)
    Scenario(run=non_retryable_error_fails_task)
    Scenario(run=retryable_error_stays_pending_and_backs_off)
    Scenario(run=retryable_error_recovers_after_failpoint_cleared)
    Scenario(run=retryable_error_killed_on_timeout)
    Scenario(run=local_backoff_is_replica_local)
