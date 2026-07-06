from testflows.core import *
from testflows.asserts import error

import helpers.config.users_d as users_d
from helpers.common import getuid
from helpers.create import partitioned_replicated_merge_tree_table
from helpers.queries import select_all_ordered
from s3.requirements.export_partition import *
from s3.tests.export_partition.steps import *


@TestStep(Given)
def populated_source_and_s3_table(
    self,
    number_of_partitions=1,
    number_of_parts=3,
    destination_cluster=None,
    destination_columns=None,
):
    """Create a populated replicated source table and an empty S3 destination table.

    ``destination_cluster`` controls where the S3 destination table is created. It
    defaults to ``None`` (only the initiating node). Scenarios that expect a
    replica other than the initiator to complete the export must pass the cluster
    name so every replica has a destination table to write to — otherwise a
    healthy replica has nothing to export into and the task can only ever be
    finished by the initiating node.

    ``destination_columns`` overrides the S3 table columns (used by the
    non-retryable schema-mismatch scenarios).
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
        table_name="s3",
        create_new_bucket=True,
        cluster=destination_cluster,
        columns=destination_columns,
    )
    return source_table, s3_table_name


# ---------------------------------------------------------------------------
# Phase 1 — Happy path
# ---------------------------------------------------------------------------


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
            settings=short_backoff_settings(initial=1, max_backoff=5),
        )

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_RetryMechanism("1.1"))
def happy_default_settings(self):
    """Check that an export succeeds with the default back-off settings (no overrides)."""

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table(
            number_of_partitions=2, number_of_parts=2
        )

    with When("I export partitions with default settings"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_LocalBackoffPolicy_State("1.0"))
def no_backoff_on_clean_export(self):
    """Check that a successful export never records any local back-off entry."""

    node = self.context.node

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table()
        partition = get_partitions(table_name=source_table, node=node)[0]

    with When("I export the partition"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=node,
            partitions=[partition],
        )

    with Then("no replica ever reported a back-off entry"):
        for n in self.context.nodes:
            count = get_local_backoff_count(
                source_table=source_table, partition=partition, node=n
            )
            assert count == 0, error(f"unexpected back-off entries on {n.name}")


@TestOutline(Scenario)
@Examples(
    "initial, max_backoff",
    [
        (10, 5),
        (3, 3),
        (0, 5),
        (1_000_000_000, 2_000_000_000),
    ],
)
@Requirements(
    RQ_ClickHouse_ExportPartition_LocalBackoffPolicy("1.1"),
    RQ_ClickHouse_ExportPartition_Settings_RetryInitialBackoff("1.1"),
    RQ_ClickHouse_ExportPartition_Settings_RetryMaxBackoff("1.1"),
)
def settings_boundaries(self, initial, max_backoff):
    """Check that boundary back-off settings still produce a successful export:
    initial > max (clamped), initial == max, initial = 0, and very large values."""

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table()

    with When(f"I export with back-off initial={initial}, max={max_backoff}"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            settings=short_backoff_settings(initial=initial, max_backoff=max_backoff),
        )

    with Then("source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_Settings_RetryInitialBackoff("1.1"),
    RQ_ClickHouse_ExportPartition_Settings_RetryMaxBackoff("1.1"),
)
def invalid_settings_rejected(self):
    """Check that invalid back-off setting values are rejected with a query error."""

    node = self.context.node

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table()
        partition = get_partitions(table_name=source_table, node=node)[0]

    for setting in (INITIAL_BACKOFF_SECONDS, MAX_BACKOFF_SECONDS):
        for value in ("-1", "abc"):
            with Then(f"{setting}={value} is rejected"):
                assert_setting_rejected(
                    source_table=source_table,
                    destination_table=s3_table_name,
                    partition=partition,
                    setting=setting,
                    value=value,
                    node=node,
                )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Settings_TaskTimeout("1.1"))
def task_timeout_zero_disables(self):
    """Check that task_timeout_seconds = 0 disables the timeout: a continuously failing
    retryable export stays PENDING and is never auto-killed."""

    node = self.context.node

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table()
        partition = get_partitions(table_name=source_table, node=node)[0]

    with When("I enable the retryable failpoint on all nodes"):
        enable_failpoint(failpoint=RETRYABLE_FAILPOINT)

    try:
        with And("I start an export with the task timeout disabled"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=node,
                settings=[(TASK_TIMEOUT_SECONDS, "0")] + short_backoff_settings(),
            )

        with Then("the task keeps retrying and is never killed"):
            assert_task_stays_pending(
                source_table=source_table, partition=partition, node=node, duration=20
            )
    finally:
        with Finally("I disable the retryable failpoint on all nodes"):
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT)


# ---------------------------------------------------------------------------
# Phase 2 — Error classification and observability
# ---------------------------------------------------------------------------


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
@Requirements(RQ_ClickHouse_ExportPartition_ErrorClassification_NonRetryable("1.1"))
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
            assert_destination_empty(destination_table=s3_table_name, node=node)
    finally:
        with Finally("I disable the non-retryable failpoint on all nodes"):
            disable_failpoint(failpoint=NON_RETRYABLE_FAILPOINT)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_ErrorClassification_NonRetryable("1.1"))
def non_retryable_column_count_mismatch(self):
    """Check that a real deterministic error (destination has an extra column) fails
    fast and writes no data, instead of retrying until the timeout."""

    node = self.context.node

    with Given("I create a source table and a destination with an extra column"):
        source_table, s3_table_name = populated_source_and_s3_table(
            destination_columns=default_columns() + [{"name": "extra", "type": "Int64"}]
        )
        partition = get_partitions(table_name=source_table, node=node)[0]

    with Then("the export fails fast with no rows written"):
        assert_export_fails_fast(
            source_table=source_table,
            destination_table=s3_table_name,
            partition=partition,
            node=node,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_ErrorClassification_NonRetryable("1.1"))
def non_retryable_lossy_cast(self):
    """Check that a lossy cast (UInt64 -> Int32) with allow_lossy_cast disabled fails
    fast instead of retrying until the timeout."""

    node = self.context.node

    with Given("I create a source table and a destination requiring a lossy cast"):
        source_table, s3_table_name = populated_source_and_s3_table(
            destination_columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "i", "type": "Int32"},
            ]
        )
        partition = get_partitions(table_name=source_table, node=node)[0]

    with Then("the export fails fast with no rows written"):
        assert_export_fails_fast(
            source_table=source_table,
            destination_table=s3_table_name,
            partition=partition,
            node=node,
            settings=[("export_merge_tree_part_allow_lossy_cast", "0")],
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_ErrorClassification_NonRetryable("1.1"))
def non_retryable_file_already_exists(self):
    """Check that re-exporting with file_already_exists_policy='error' fails fast
    (FILE_ALREADY_EXISTS is non-retryable)."""

    node = self.context.node

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table()
        partition = get_partitions(table_name=source_table, node=node)[0]

    with When("I export the partition successfully once"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=node,
            partitions=[partition],
        )
        exported_rows = select_all_ordered(table_name=s3_table_name, node=node)

    with Then("re-exporting over the existing files with policy='error' fails fast"):
        assert_export_fails_fast(
            source_table=source_table,
            destination_table=s3_table_name,
            partition=partition,
            node=node,
            settings=[
                ("export_merge_tree_partition_force_export", "1"),
                ("export_merge_tree_part_file_already_exists_policy", "error"),
            ],
            expected_rows=exported_rows,
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_ErrorClassification_Retryable("1.1"),
    RQ_ClickHouse_ExportPartition_NetworkResilience_DestinationInterruption("1.0"),
)
def retryable_minio_outage_recovers(self):
    """Check that a real object-storage outage is retried (task stays PENDING and backs
    off) and the export completes once MinIO returns."""

    node = self.context.node

    with Given("I create a populated source table and empty S3 table"):
        source_table, s3_table_name = populated_source_and_s3_table()
        partition = get_partitions(table_name=source_table, node=node)[0]

    with When("I take MinIO down"):
        kill_minio()

    try:
        with And("I start exporting the partition with a short back-off"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=node,
                settings=short_backoff_settings(),
            )

        with Then("a local back-off entry appears and the task stays PENDING"):
            # A real MinIO outage first spins inside the AWS SDK's own retry loop
            # (query-level s3_retry_* settings do not reach the background export
            # worker), so the first ClickHouse-level part failure — and therefore the
            # first local back-off entry — only appears after ~60-70s. Wait longer than
            # that window so the retryable failure registers before the test gives up.
            wait_for_local_backoff(
                source_table=source_table, partition=partition, timeout=120
            )
            status = get_export_status(source_table=source_table, partition=partition)
            assert status == "PENDING", error(f"expected PENDING, got {status!r}")
    finally:
        with Finally("I bring MinIO back"):
            start_minio()

    with Then("the export completes once storage returns"):
        wait_for_export_to_complete(
            source_table=source_table, partition_id=partition, node=node
        )

    with And("source matches destination"):
        source_matches_destination(
            source_table=source_table, destination_table=s3_table_name
        )


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
                settings=short_backoff_settings(),
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
@Requirements(RQ_ClickHouse_ExportPartition_LocalBackoffPolicy_State("1.0"))
def backoff_attempts_increment(self):
    """Check the observable back-off state: attempts grows across retries and
    next_retry_time is always in the future while the task stays PENDING."""

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
                settings=short_backoff_settings(),
            )

        with Then("the attempt count grows past one"):
            wait_for_backoff_attempts(
                source_table=source_table, partition=partition, min_attempts=2
            )

        with And("the next retry time is in the future"):
            wait_for_backoff_next_retry_in_future(
                source_table=source_table, partition=partition, node=node
            )

        with And("the task is still PENDING"):
            status = get_export_status(source_table=source_table, partition=partition)
            assert status == "PENDING", error(f"expected PENDING, got {status!r}")
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
                settings=short_backoff_settings(),
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
                settings=[(TASK_TIMEOUT_SECONDS, "5")] + short_backoff_settings(),
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
            assert_destination_empty(destination_table=s3_table_name, node=node)
    finally:
        with Finally("I disable the retryable failpoint on all nodes"):
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_ErrorClassification_PermanentDestinationErrors("1.0")
)
def s3_permanent_error_retries_until_timeout(self):
    """Document current behavior: a permanent destination error (wrong credentials,
    surfaced as S3_ERROR) is treated as retryable, so the task only stops at the task
    timeout as KILLED instead of failing fast."""

    node = self.context.node

    with Given("I create a source table and a destination with wrong credentials"):
        source_table = f"source_{getuid()}"
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table_wrong_credentials()
        partition = get_partitions(table_name=source_table, node=node)[0]

    with When("I start the export with a short task timeout"):
        start_export(
            source_table=source_table,
            destination_table=s3_table_name,
            partition=partition,
            node=node,
            settings=[(TASK_TIMEOUT_SECONDS, "10")] + short_backoff_settings(),
        )

    with Then("the permanent error is retried until the timeout, ending in KILLED"):
        wait_for_export_status(
            source_table=source_table,
            partition=partition,
            status="KILLED",
            timeout=120,
        )

    # No destination-emptiness check here: the destination is deliberately
    # configured with wrong credentials, so a SELECT against it fails with the
    # same S3_ERROR (SignatureDoesNotMatch) as the writes. Reaching KILLED (every
    # write attempt failed before committing) is the documented behavior.


# ---------------------------------------------------------------------------
# Phase 3 — Multi-replica choreography
# ---------------------------------------------------------------------------


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

    with And(
        "I stop moves on the healthy replicas so the failing replica exports first"
    ):
        stop_moves(source_table=source_table, nodes=healthy_nodes)

    with And("I enable the retryable failpoint on the failing replica only"):
        enable_failpoint(failpoint=RETRYABLE_FAILPOINT, nodes=[failing_node])

    try:
        with When(
            "I start exporting the partition with a short back-off on the failing replica"
        ):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=failing_node,
                settings=short_backoff_settings(),
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
            source_matches_destination(
                source_table=source_table,
                destination_table=s3_table_name,
            )
    finally:
        with Finally("I disable the retryable failpoint on the affected replica"):
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT, nodes=[failing_node])

        with Finally("I resume moves on all replicas"):
            start_moves(source_table=source_table, nodes=self.context.nodes)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_LocalBackoffPolicy("1.1"))
def all_replicas_backoff_independently(self):
    """Check that when every replica fails a retryable error, each arms its own back-off
    entry, the task stays PENDING, and it completes once the failure clears."""

    source_table = None
    try:
        with Given("I create a source table and an S3 table on every replica"):
            source_table, s3_table_name = populated_source_and_s3_table(
                destination_cluster="replicated_cluster"
            )
            partition = get_partitions(table_name=source_table, node=self.context.node)[
                0
            ]

        with When("I enable the retryable failpoint on all nodes"):
            enable_failpoint(failpoint=RETRYABLE_FAILPOINT)

        with And("I start the export with a short back-off"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=self.context.node,
                settings=short_backoff_settings(),
            )

        with Then("every replica reports its own back-off entry"):
            wait_for_local_backoff_on_all(
                source_table=source_table, partition=partition
            )

        with And("the task stays PENDING"):
            status = get_export_status(source_table=source_table, partition=partition)
            assert status == "PENDING", error(f"expected PENDING, got {status!r}")

        with When("I clear the failure on all nodes"):
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT)

        with Then("the export completes and matches source"):
            wait_for_export_to_complete(
                source_table=source_table,
                partition_id=partition,
                node=self.context.node,
            )
            source_matches_destination(
                source_table=source_table, destination_table=s3_table_name
            )
    finally:
        with Finally("I reset cluster state"):
            reset_backoff_test_state(source_table=source_table)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_LocalBackoffPolicy_NotPersistedAcrossRestart("1.0")
)
def backoff_resets_on_restart(self):
    """Check that the in-memory back-off does not survive a replica restart: after the
    backing-off replica restarts, its attempt count resets.

    The failure source is a wrong-credentials S3 destination (a persistent
    ``S3_ERROR``) rather than an in-memory failpoint. A failpoint is wiped when the
    replica is killed, leaving a window in which the restarted replica exports the
    part successfully (task ``COMPLETED``, back-off entries pruned) before the
    failpoint can be re-armed — so a fresh back-off never reappears and the reset
    is unobservable. A permanent credential error keeps failing across the restart,
    so the replica deterministically re-registers a back-off that starts over from
    a low attempt count.
    """

    failing_node = self.context.nodes[0]
    healthy_nodes = [n for n in self.context.nodes if n is not failing_node]
    source_table = None

    try:
        with Given(
            "I create a source table and a wrong-credentials S3 table on every replica"
        ):
            source_table = f"source_{getuid()}"
            partitioned_replicated_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                columns=default_columns(),
                stop_merges=True,
                cluster="replicated_cluster",
            )
            s3_table_name = create_s3_table_wrong_credentials(
                cluster="replicated_cluster"
            )
            partition = get_partitions(table_name=source_table, node=failing_node)[0]

        with And(
            "I stop moves on the healthy replicas so only the first replica exports"
        ):
            stop_moves(source_table=source_table, nodes=healthy_nodes)

        with When("I start the export and let the attempt count grow"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=failing_node,
                settings=short_backoff_settings(),
            )
            wait_for_backoff_attempts(
                source_table=source_table,
                partition=partition,
                min_attempts=4,
                nodes=[failing_node],
            )
            before = get_backoff_attempts(
                source_table=source_table, partition=partition, node=failing_node
            )

        with And("I restart the failing replica"):
            kill_node(node=failing_node)
            start_node(node=failing_node)
            wait_for_nodes_ready(nodes=[failing_node])

        with Then("the attempt count starts over (in-memory state was lost)"):
            wait_for_backoff_attempts(
                source_table=source_table,
                partition=partition,
                min_attempts=1,
                nodes=[failing_node],
                delay=1,
            )
            after = get_backoff_attempts(
                source_table=source_table, partition=partition, node=failing_node
            )
            assert after < before, error(
                f"attempts should reset after restart, got before={before} after={after}"
            )
    finally:
        with Finally("I reset cluster state"):
            reset_backoff_test_state(source_table=source_table)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_RetryMechanism("1.1"))
def timeout_survives_handoffs(self):
    """Check that the absolute task timeout (measured from manifest create_time) still
    fires even as the part is handed off between replicas, ending in KILLED."""

    source_table = None
    try:
        with Given("I create a source table and an S3 table on every replica"):
            source_table, s3_table_name = populated_source_and_s3_table(
                destination_cluster="replicated_cluster"
            )
            partition = get_partitions(table_name=source_table, node=self.context.node)[
                0
            ]

        with When("I enable the retryable failpoint on all nodes"):
            enable_failpoint(failpoint=RETRYABLE_FAILPOINT)

        with And("I start the export with a short task timeout"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=self.context.nodes[0],
                settings=[(TASK_TIMEOUT_SECONDS, "20")] + short_backoff_settings(),
            )
            wait_for_local_backoff(source_table=source_table, partition=partition)

        with And("I kill the initiating replica to force a hand-off"):
            kill_node(node=self.context.nodes[0])

        with Then("the task is still KILLED once the absolute timeout elapses"):
            wait_for_export_status(
                source_table=source_table,
                partition=partition,
                status="KILLED",
                node=self.context.nodes[1],
                timeout=120,
            )
    finally:
        with Finally("I reset cluster state"):
            reset_backoff_test_state(source_table=source_table)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_LocalBackoffPolicy("1.1"),
    RQ_ClickHouse_ExportPartition_NetworkResilience_NodeInterruption("1.0"),
)
def killed_backing_off_replica_does_not_block(self):
    """Check that killing a replica while it is backing off does not block the export:
    a healthy replica completes it."""

    failing_node = self.context.nodes[0]
    healthy_nodes = [n for n in self.context.nodes if n is not failing_node]
    source_table = None

    try:
        with Given("I create a source table and an S3 table on every replica"):
            source_table, s3_table_name = populated_source_and_s3_table(
                destination_cluster="replicated_cluster"
            )
            partition = get_partitions(table_name=source_table, node=failing_node)[0]

        with And(
            "I stop moves on the healthy replicas so the first replica fails first"
        ):
            stop_moves(source_table=source_table, nodes=healthy_nodes)

        with And("I enable the retryable failpoint on the failing replica only"):
            enable_failpoint(failpoint=RETRYABLE_FAILPOINT, nodes=[failing_node])

        with When("I start the export and wait for it to back off"):
            start_export(
                source_table=source_table,
                destination_table=s3_table_name,
                partition=partition,
                node=failing_node,
                settings=short_backoff_settings(),
            )
            wait_for_local_backoff(
                source_table=source_table, partition=partition, nodes=[failing_node]
            )

        with And("I kill the backing-off replica and resume moves on the healthy ones"):
            kill_node(node=failing_node)
            start_moves(source_table=source_table, nodes=healthy_nodes)

        with Then("a healthy replica completes the export and matches source"):
            wait_for_export_to_complete(
                source_table=source_table,
                partition_id=partition,
                node=healthy_nodes[0],
            )
            source_matches_destination(
                source_table=source_table,
                destination_table=s3_table_name,
                source_node=healthy_nodes[0],
                destination_node=healthy_nodes[0],
            )
    finally:
        with Finally("I reset cluster state"):
            reset_backoff_test_state(source_table=source_table)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_LocalBackoffPolicy("1.1"),
    RQ_ClickHouse_ExportPartition_Idempotency("1.0"),
    RQ_ClickHouse_ExportPartition_NetworkResilience_NodeInterruption("1.0"),
)
def relay_failover_failpoint(self):
    """Scripted relay with a per-replica retryable failpoint: replicas fail and are
    killed one by one, the export survives the hand-offs and completes exactly once."""

    source_table = None
    try:
        with Given("I create a source table and an S3 table on every replica"):
            source_table, s3_table_name = populated_source_and_s3_table(
                destination_cluster="replicated_cluster"
            )
            partition = get_partitions(table_name=source_table, node=self.context.node)[
                0
            ]

        run_relay_failover(
            source_table=source_table,
            destination_table=s3_table_name,
            partition=partition,
            nodes=list(self.context.nodes),
            mode=FAILPOINT_MODE,
        )
    finally:
        with Finally("I reset cluster state"):
            reset_backoff_test_state(source_table=source_table)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_LocalBackoffPolicy("1.1"),
    RQ_ClickHouse_ExportPartition_Idempotency("1.0"),
    RQ_ClickHouse_ExportPartition_NetworkResilience_DestinationInterruption("1.0"),
)
def relay_failover_minio(self):
    """Scripted relay driven by a real MinIO outage: replicas fail and are killed one by
    one, and the export completes exactly once after storage returns."""

    source_table = None
    try:
        with Given("I create a source table and an S3 table on every replica"):
            source_table, s3_table_name = populated_source_and_s3_table(
                destination_cluster="replicated_cluster"
            )
            partition = get_partitions(table_name=source_table, node=self.context.node)[
                0
            ]

        run_relay_failover(
            source_table=source_table,
            destination_table=s3_table_name,
            partition=partition,
            nodes=list(self.context.nodes),
            mode=MINIO_MODE,
        )
    finally:
        with Finally("I reset cluster state"):
            reset_backoff_test_state(source_table=source_table)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_LocalBackoffPolicy("1.1"),
    RQ_ClickHouse_ExportPartition_Idempotency("1.0"),
    RQ_ClickHouse_ExportPartition_NetworkResilience_NodeInterruption("1.0"),
)
def chaos_failover_failpoint(self):
    """Randomized chaos with a per-replica retryable failpoint: random kills/restarts,
    then restore everything and assert the export completes exactly once."""

    source_table = None
    try:
        with Given("I create a source table and an S3 table on every replica"):
            source_table, s3_table_name = populated_source_and_s3_table(
                destination_cluster="replicated_cluster"
            )
            partition = get_partitions(table_name=source_table, node=self.context.node)[
                0
            ]

        run_chaos_failover(
            source_table=source_table,
            destination_table=s3_table_name,
            partition=partition,
            nodes=list(self.context.nodes),
            mode=FAILPOINT_MODE,
        )
    finally:
        with Finally("I reset cluster state"):
            reset_backoff_test_state(source_table=source_table)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_LocalBackoffPolicy("1.1"),
    RQ_ClickHouse_ExportPartition_Idempotency("1.0"),
    RQ_ClickHouse_ExportPartition_NetworkResilience_DestinationInterruption("1.0"),
)
def chaos_failover_minio(self):
    """Randomized chaos driven by a real MinIO outage plus random kills/restarts, then
    restore everything and assert the export completes exactly once."""

    source_table = None
    try:
        with Given("I create a source table and an S3 table on every replica"):
            source_table, s3_table_name = populated_source_and_s3_table(
                destination_cluster="replicated_cluster"
            )
            partition = get_partitions(table_name=source_table, node=self.context.node)[
                0
            ]

        run_chaos_failover(
            source_table=source_table,
            destination_table=s3_table_name,
            partition=partition,
            nodes=list(self.context.nodes),
            mode=MINIO_MODE,
        )
    finally:
        with Finally("I reset cluster state"):
            reset_backoff_test_state(source_table=source_table)


@TestFeature
def happy_path(self):
    Scenario(run=backoff_settings_accepted)
    Scenario(run=happy_default_settings)
    Scenario(run=no_backoff_on_clean_export)
    Scenario(run=settings_boundaries)
    Scenario(run=invalid_settings_rejected)
    Scenario(run=task_timeout_zero_disables)


@TestFeature
def error_classification_and_observability(self):
    Scenario(run=local_backoff_per_part_column)
    Scenario(run=non_retryable_error_fails_task)
    Scenario(run=non_retryable_column_count_mismatch)
    Scenario(run=non_retryable_lossy_cast)
    Scenario(run=non_retryable_file_already_exists)
    Scenario(run=retryable_minio_outage_recovers)
    Scenario(run=retryable_error_stays_pending_and_backs_off)
    Scenario(run=backoff_attempts_increment)
    Scenario(run=retryable_error_recovers_after_failpoint_cleared)
    Scenario(run=retryable_error_killed_on_timeout)
    Scenario(run=s3_permanent_error_retries_until_timeout)


@TestFeature
def multi_replica_choreography(self):
    Scenario(run=local_backoff_is_replica_local)
    Scenario(run=all_replicas_backoff_independently)
    Scenario(run=backoff_resets_on_restart)
    Scenario(run=timeout_survives_handoffs)
    Scenario(run=killed_backing_off_replica_does_not_block)
    Scenario(run=relay_failover_failpoint)
    Scenario(run=relay_failover_minio)
    Scenario(run=chaos_failover_failpoint)
    Scenario(run=chaos_failover_minio)


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

    with Given(
        "I lower s3_retry_attempts so background exports surface object-storage "
        "failures quickly during MinIO-outage scenarios"
    ):
        # The background export worker's S3 client retries each operation up to
        # ``s3_retry_attempts`` (default 500) times. Once earlier scenarios have
        # warmed the S3 connection pool, a killed MinIO leaves dead keep-alive
        # sockets whose reads block per retry, so the first ClickHouse-level failure
        # (and therefore the first local back-off entry) can take minutes to appear
        # -> the MinIO-outage scenarios time out even though the export is behaving
        # correctly. In isolation (cold pool) a fresh connect() is refused instantly
        # and the same scenario passes in seconds. Lowering the profile default
        # makes failures surface fast regardless of pool state. It must live in
        # users.d (25.8+ rejects the setting in config.d) and it reaches the
        # background worker (unlike query-level s3_retry_* settings).
        for node in self.context.nodes:
            users_d.create_and_add(
                entries={"profiles": {"default": {"s3_retry_attempts": "3"}}},
                config_file="s3_retry_attempts.xml",
                node=node,
            )

    Feature(run=happy_path)
    Feature(run=error_classification_and_observability)
    Feature(run=multi_replica_choreography)
