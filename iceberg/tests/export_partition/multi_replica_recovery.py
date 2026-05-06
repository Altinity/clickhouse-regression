"""Multi-replica EXPORT PARTITION scenarios.

Covers two surfaces that the single-replica modules cannot exercise:
concurrent exports from different replicas (same source, same
destination) and recoverability when ZooKeeper bounces mid-flight
(graceful ``zkServer.sh restart`` and harsh SIGKILL + ``docker start``).
A small ``stress``-only sub-suite layers randomised replica kill / restart
loops on top of the same setup primitives to exercise timing-dependent
recovery paths beyond the single-shot scenarios.

The multi-replica scenarios skip under ``no_catalog`` because that mode
does not give two replicas a shared Iceberg destination; the
single-replica ZK-restart scenarios run in every catalog mode.
"""

import random
import time

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_MultiReplicaRecovery,
    RQ_Iceberg_ExportPartition_MultiReplicaRecovery_CrossReplicaConcurrency,
    RQ_Iceberg_ExportPartition_MultiReplicaRecovery_InitiatorFailover,
    RQ_Iceberg_ExportPartition_MultiReplicaRecovery_ZooKeeperBounce,
    RQ_Iceberg_ExportPartition_MultiReplicaRecovery_RandomisedChaos,
)

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
    sync_replica,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.export_status import (
    wait_for_export_status,
    wait_for_exports_to_settle,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    get_current_snapshot_summary,
    get_snapshots,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"

BAD_ARGUMENTS = 36

# Named cluster from iceberg/configs/clickhouse/config.d/remote.xml;
# every clickhouseN is listed as a replica of the same shard, so
# ``ON CLUSTER replicated_cluster`` fans DDL out to every replica
# the suite ever sees.
REPLICATED_CLUSTER = "replicated_cluster"

# Single zookeeper service name in iceberg/iceberg_env/docker-compose.yml.
ZOOKEEPER_SERVICE = "zookeeper1"


def _zk_server_command(zk_node, subcommand, **kwargs):
    """Run ``zkServer.sh <subcommand>`` inside the ZooKeeper container.

    Mirrors ``ZooKeeperNode.zk_server_command`` (``steps=False`` so the
    call does not spam the report with a nested By(...) per subcommand
    on top of the outer step we already wrap it in). Using ``command``
    directly instead of the ``ZooKeeperNode`` helper keeps us decoupled
    from ``use_zookeeper_nodes=True`` at the regression entrypoint.
    """
    return zk_node.command(
        f"zkServer.sh {subcommand}", steps=False, **kwargs
    )


def _zk_wait_healthy(zk_node, timeout=60):
    """Poll ``zkServer.sh status`` until ZooKeeper answers successfully.

    ``zkServer.sh restart`` returns before the new process has finished
    initialising and accepting client connections, so any export task
    that reconnects in that window will re-fail. Waiting for ``status``
    to report ``0`` matches ``ZooKeeperNode.wait_zookeeper_healthy`` and
    makes the retry window deterministic.
    """
    with By(f"waiting for {zk_node.name} to report healthy"):
        for attempt in retries(timeout=timeout, delay=1):
            with attempt:
                result = _zk_server_command(zk_node, "status", no_checks=True)
                assert result.exitcode == 0, error(
                    f"ZooKeeper is not healthy yet: {result.output}"
                )


def _zookeeper_node(self):
    """Return the single ``zookeeper1`` Node handle from the cluster.

    See the module docstring for why this is a plain ``Node`` rather
    than a ``ZooKeeperNode``.
    """
    return self.context.cluster.node(ZOOKEEPER_SERVICE)


def _zk_docker_kill(self, signal="SIGKILL"):
    """Forcefully kill the ZooKeeper container.

    Uses ``docker compose kill -s <signal>`` so we inherit the
    project-directory / project-file wiring ``helpers.cluster`` already
    sets up — no need to hardcode ``iceberg_env-zookeeper1-1``.
    ``SIGKILL`` gives the ZK process no chance to checkpoint state or
    send a disconnect to its clients, which is the real-crash
    disturbance we want to layer on top of the graceful-restart path.
    """
    cluster = self.context.cluster
    with By(f"sending {signal} to {ZOOKEEPER_SERVICE} via docker compose"):
        cluster.command(
            None,
            f"{cluster.docker_compose} kill -s {signal} {ZOOKEEPER_SERVICE}",
            exitcode=0,
            steps=False,
        )


def _zk_docker_start(self):
    """Start the ZooKeeper container after a ``_zk_docker_kill``.

    ``docker compose start`` re-launches the container through the same
    compose project, so the ZK image's own entrypoint brings the server
    back up under its normal init script rather than the ``zkServer.sh
    start`` path our graceful helpers use. Paired with
    :func:`_zk_wait_healthy`, this gives us the "crash and recover"
    semantics the s3 ``export_partition`` suite gets from its
    ``containers.kill_zookeeper`` / ``containers.start_zookeeper``
    steps.
    """
    cluster = self.context.cluster
    with By(f"starting {ZOOKEEPER_SERVICE} via docker compose"):
        cluster.command(
            None,
            f"{cluster.docker_compose} start {ZOOKEEPER_SERVICE}",
            exitcode=0,
            steps=False,
        )


def _disturb_zookeeper_graceful(self):
    """Graceful bounce: ``docker compose restart`` + health probe.

    Driven from docker-compose (not ``zkServer.sh restart``) so the
    graceful and harsh paths share the same lifecycle owner and cannot
    disagree over the ``/data/zookeeper_server.pid`` file.
    """
    cluster = self.context.cluster
    with By(f"gracefully bouncing {ZOOKEEPER_SERVICE} via docker compose"):
        cluster.command(
            None,
            f"{cluster.docker_compose} restart {ZOOKEEPER_SERVICE}",
            exitcode=0,
            steps=False,
        )
    zk = _zookeeper_node(self)
    # Matches the timeout we use after the harsh disturbance: docker
    # compose restart re-runs the container entrypoint, which
    # re-forms the single-node quorum before answering ``zkServer.sh
    # status`` — the first few probes legitimately fail.
    _zk_wait_healthy(zk, timeout=120)


def _disturb_zookeeper_docker_kill(self):
    """Harsh bounce: ``docker compose kill -s SIGKILL`` + ``start``.

    The ZK process dies instantly with no on-disk checkpoint flush and
    no TCP FIN to its clients, so in-flight export tasks observe an
    abrupt ``ConnectionLoss`` and any operation that was mid-commit on
    the server side is left to the ZK transaction log to replay on
    restart. After the container comes back up we wait until
    ``zkServer.sh status`` reports healthy; the first health probe
    after ``docker start`` frequently needs several seconds because
    the image's entrypoint re-forms the quorum before answering, so
    the wait timeout is bumped to 120s.
    """
    _zk_docker_kill(self)
    _zk_docker_start(self)
    zk = _zookeeper_node(self)
    _zk_wait_healthy(zk, timeout=120)


def _require_multi_replica_catalog_mode(self):
    """Gate scenarios that need >=2 CH replicas + a catalog-mode destination.

    See the module docstring for why ``no_catalog`` is out of scope.
    """
    if not hasattr(self.context, "nodes") or len(self.context.nodes) < 2:
        skip("need at least two ClickHouse replicas")
    if self.context.catalog == "no":
        skip(
            "multi-replica EXPORT PARTITION needs a catalog-registered "
            "destination shared across nodes; no_catalog mode has each "
            "replica managing its own IcebergS3 table"
        )


def _setup_replicated_source(table_name, nodes):
    """Create a ReplicatedMergeTree on every replica, sharing one zk_path.

    The per-replica ``replica_name`` is the standard ``r1`` / ``r2`` /
    ... pattern used by :mod:`iceberg.tests.export_partition.sanity`
    (``cross_replica_export``) so the replicas negotiate a real
    multi-writer setup via ZooKeeper rather than accidentally colliding
    on ``replica_name``.
    """
    for i, node in enumerate(nodes, start=1):
        create_replicated_mergetree(
            table_name=table_name,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            zk_path=f"/clickhouse/tables/{table_name}",
            replica_name=f"r{i}",
            node=node,
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_MultiReplicaRecovery_CrossReplicaConcurrency("1.0"))
@Name("concurrent exports from different replicas on different partitions")
def concurrent_cross_replica_different_partitions(
    self, minio_root_user, minio_root_password
):
    """Two replicas race to export two different partitions of the same
    table; the destination ends with two append snapshots chained
    head-to-tail and both partitions' rows reachable.
    """
    _require_multi_replica_catalog_mode(self)

    replica1 = self.context.nodes[0]
    replica2 = self.context.nodes[1]
    table_name = f"mt_{getuid()}"

    with Given("create the replicated source on every replica"):
        _setup_replicated_source(table_name, [replica1, replica2])

    with And("insert two partitions' worth of rows on replica1"):
        insert_data(
            table_name=table_name,
            values="(1, 2020), (2, 2020), (3, 2021), (4, 2021)",
            node=replica1,
        )

    with And("wait for replica2 to pick up the new parts"):
        sync_replica(table_name=table_name, node=replica2)

    with Given("create a catalog-backed destination wired up on every replica"):
        # cluster_name fans the DataLakeCatalog CREATE DATABASE out via
        # ON CLUSTER so both replica1 and replica2 resolve the same
        # <database>.`ns.tbl` identifier.
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=replica1,
            cluster_name=REPLICATED_CLUSTER,
        )

    with When("schedule EXPORT of partition 2020 on replica1 without waiting"):
        export_partition(
            source_table=table_name,
            destination=destination,
            partition_id="2020",
            node=replica1,
            wait_for_completion=False,
        )

    with And("schedule EXPORT of partition 2021 on replica2 without waiting"):
        # The two ALTERs install independent ZK idempotency keys (the
        # key is per-partition), so both schedule successfully and the
        # background tasks race for the Iceberg snapshot commit lock.
        export_partition(
            source_table=table_name,
            destination=destination,
            partition_id="2021",
            node=replica2,
            wait_for_completion=False,
        )

    with Then("both export rows reach COMPLETED (observed from their own replica)"):
        wait_for_export_status(
            source_table=table_name,
            destination=destination,
            partition_id="2020",
            expected_status="COMPLETED",
            node=replica1,
        )
        wait_for_export_status(
            source_table=table_name,
            destination=destination,
            partition_id="2021",
            expected_status="COMPLETED",
            node=replica2,
        )

    with And("snapshot log has exactly two linearised append snapshots"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == 2, error(
            f"Expected 2 snapshots (one per partition), got "
            f"{len(snapshots)}: {[s.snapshot_id for s in snapshots]!r}"
        )
        for snap in snapshots:
            operation = getattr(snap.summary, "operation", None)
            op_str = str(getattr(operation, "value", operation))
            assert op_str == "append", error(
                f"Expected append snapshot, got {op_str!r} for "
                f"snapshot_id={snap.snapshot_id}"
            )
        # Linearity is the property we care about: the younger snapshot
        # must chain to the older one regardless of which replica
        # happened to commit first.
        assert snapshots[1].parent_snapshot_id == snapshots[0].snapshot_id, error(
            "Concurrent cross-replica commits must form a single linear chain; "
            f"got parent={snapshots[1].parent_snapshot_id} "
            f"for snapshot={snapshots[1].snapshot_id}"
        )

    with And("destination holds both partitions' rows (4 rows total)"):
        assert_destination_row_count(
            destination=destination,
            expected=4,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_MultiReplicaRecovery_CrossReplicaConcurrency("1.0"))
@Name("concurrent exports of the same partition from different replicas are idempotent")
def concurrent_cross_replica_same_partition_idempotent(
    self, minio_root_user, minio_root_password
):
    """Two replicas try to export the same partition; the second is
    rejected synchronously by the shared ZK idempotency key
    (``BAD_ARGUMENTS`` / "Export with key ..."), and the destination
    ends with exactly one append snapshot.
    """
    _require_multi_replica_catalog_mode(self)

    replica1 = self.context.nodes[0]
    replica2 = self.context.nodes[1]
    table_name = f"mt_{getuid()}"

    with Given("create the replicated source on every replica"):
        _setup_replicated_source(table_name, [replica1, replica2])

    with And("insert one partition's worth of rows on replica1"):
        insert_data(
            table_name=table_name,
            values="(1, 2020), (2, 2020), (3, 2020)",
            node=replica1,
        )

    with And("wait for replica2 to pick up the parts"):
        sync_replica(table_name=table_name, node=replica2)

    with Given("create a catalog-backed destination wired up on every replica"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=replica1,
            cluster_name=REPLICATED_CLUSTER,
        )

    with When("schedule EXPORT of partition 2020 on replica1 without waiting"):
        export_partition(
            source_table=table_name,
            destination=destination,
            partition_id="2020",
            node=replica1,
            wait_for_completion=False,
        )

    with And("duplicate ALTER on replica2 is rejected by the shared ZK lock"):
        # The ZK idempotency key is visible to every replica; replica2's
        # ALTER sees the entry replica1 just installed and fails with
        # BAD_ARGUMENTS / "Export with key ...". This is the
        # multi-writer equivalent of
        # ``transactions.duplicate_export_within_ttl_rejected``.
        export_partition(
            source_table=table_name,
            destination=destination,
            partition_id="2020",
            node=replica2,
            exitcode=BAD_ARGUMENTS,
            message="Export with key",
            wait_for_completion=False,
        )

    with And("wait for replica1's in-flight export to settle on both nodes"):
        # Drain from both replicas so we don't race PyIceberg's
        # metadata.json read against the snapshot commit (same reason
        # ``duplicate_export_inside_one_alter`` calls settle).
        for node in (replica1, replica2):
            wait_for_exports_to_settle(
                source_table=table_name,
                destination=destination,
                partition_id="2020",
                node=node,
            )

    with Then("exactly one snapshot exists — the duplicate never committed"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == 1, error(
            f"ZK idempotency must reject the duplicate cross-replica "
            f"export; got {len(snapshots)} snapshots: "
            f"{[s.snapshot_id for s in snapshots]!r}"
        )
        operation = getattr(snapshots[0].summary, "operation", None)
        op_str = str(getattr(operation, "value", operation))
        assert op_str == "append", error(
            f"Expected append snapshot, got {op_str!r}"
        )

    with And("destination row count matches the partition exactly once"):
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


def _run_single_replica_zk_recovery(
    self, disturb, minio_root_user, minio_root_password
):
    """Shared body: schedule a single-replica export, apply ``disturb``
    while it is in flight, then assert it converges to ``COMPLETED``
    with exactly one append snapshot and no row loss. ``disturb`` selects
    the bounce mode (graceful restart or SIGKILL).
    """
    if not hasattr(self.context, "nodes") or len(self.context.nodes) < 1:
        skip("need at least one ClickHouse replica")

    node = self.context.node
    table_name = f"mt_{getuid()}"

    with Given("create a ReplicatedMergeTree source"):
        create_replicated_mergetree(
            table_name=table_name,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            zk_path=f"/clickhouse/tables/{table_name}",
            replica_name="r1",
            node=node,
        )

    with And("insert one partition's worth of rows"):
        insert_data(
            table_name=table_name,
            values="(1, 2020), (2, 2020), (3, 2020)",
            node=node,
        )

    with Given("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    with When("schedule EXPORT PARTITION 2020 without waiting"):
        export_partition(
            source_table=table_name,
            destination=destination,
            partition_id="2020",
            node=node,
            wait_for_completion=False,
        )

    with And("disturb zookeeper1 while the export is in flight"):
        # Whichever stage the background commit task is on when the ZK
        # session dies (manifest install / snapshot commit / COMPLETED
        # publish), CH must reconnect and drive the work forward. This
        # scenario intentionally does not pin a specific race — the
        # assertion is simply that every path is recoverable end-to-end.
        disturb(self)

    with Then("the export eventually reaches COMPLETED despite the ZK bounce"):
        # Bumped timeout: the first reconnect attempt can land just
        # after the bounce and the retry backoff adds a few seconds on
        # top of the usual commit window.
        wait_for_export_status(
            source_table=table_name,
            destination=destination,
            partition_id="2020",
            expected_status="COMPLETED",
            node=node,
            timeout=180,
        )

    with And("exactly one snapshot exists — retry never double-commits"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == 1, error(
            f"ZK-disturbance retry must not produce a duplicate snapshot; "
            f"got {len(snapshots)}: {[s.snapshot_id for s in snapshots]!r}"
        )
        operation = getattr(snapshots[0].summary, "operation", None)
        op_str = str(getattr(operation, "value", operation))
        assert op_str == "append", error(
            f"Expected append snapshot, got {op_str!r}"
        )

    with And("destination holds the partition's rows intact"):
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


def _run_multi_replica_zk_recovery(
    self, disturb, minio_root_user, minio_root_password
):
    """Shared body: two replicas export different partitions, ``disturb``
    is applied mid-flight, and both commits must converge with the
    destination ending in two linearised append snapshots and no row loss.
    """
    _require_multi_replica_catalog_mode(self)

    replica1 = self.context.nodes[0]
    replica2 = self.context.nodes[1]
    table_name = f"mt_{getuid()}"

    with Given("create the replicated source on every replica"):
        _setup_replicated_source(table_name, [replica1, replica2])

    with And("insert two partitions' worth of rows on replica1"):
        insert_data(
            table_name=table_name,
            values="(1, 2020), (2, 2020), (3, 2021), (4, 2021)",
            node=replica1,
        )

    with And("wait for replica2 to pick up the new parts"):
        sync_replica(table_name=table_name, node=replica2)

    with Given("create a catalog-backed destination wired up on every replica"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=replica1,
            cluster_name=REPLICATED_CLUSTER,
        )

    with When("schedule EXPORT of partition 2020 on replica1 without waiting"):
        export_partition(
            source_table=table_name,
            destination=destination,
            partition_id="2020",
            node=replica1,
            wait_for_completion=False,
        )

    with And("schedule EXPORT of partition 2021 on replica2 without waiting"):
        export_partition(
            source_table=table_name,
            destination=destination,
            partition_id="2021",
            node=replica2,
            wait_for_completion=False,
        )

    with And("disturb zookeeper1 while both exports are in flight"):
        # Both replicas share the single zookeeper1 instance, so one
        # disturbance severs every open session at once. Each replica
        # must reconnect and retry independently.
        disturb(self)

    with Then("both exports converge to COMPLETED on their respective replicas"):
        wait_for_export_status(
            source_table=table_name,
            destination=destination,
            partition_id="2020",
            expected_status="COMPLETED",
            node=replica1,
            timeout=180,
        )
        wait_for_export_status(
            source_table=table_name,
            destination=destination,
            partition_id="2021",
            expected_status="COMPLETED",
            node=replica2,
            timeout=180,
        )

    with And("snapshot log has exactly two linearised append snapshots"):
        snapshots = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots) == 2, error(
            f"Expected 2 snapshots (one per partition), got "
            f"{len(snapshots)}: {[s.snapshot_id for s in snapshots]!r}"
        )
        for snap in snapshots:
            operation = getattr(snap.summary, "operation", None)
            op_str = str(getattr(operation, "value", operation))
            assert op_str == "append", error(
                f"Expected append snapshot, got {op_str!r} for "
                f"snapshot_id={snap.snapshot_id}"
            )
        assert snapshots[1].parent_snapshot_id == snapshots[0].snapshot_id, error(
            "Post-ZK-disturbance commits must still form a single linear chain; "
            f"got parent={snapshots[1].parent_snapshot_id} "
            f"for snapshot={snapshots[1].snapshot_id}"
        )

    with And("destination holds both partitions' rows (4 rows total)"):
        assert_destination_row_count(
            destination=destination,
            expected=4,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_MultiReplicaRecovery_InitiatorFailover("1.0"))
@Name("initiator dies mid-commit and peer replica finalizes exactly once")
def initiator_dies_mid_commit_peer_finalizes_exactly_once(
    self, minio_root_user, minio_root_password
):
    """``replica1`` is stopped mid-export; ``replica2`` must finish the
    work via the Keeper-stashed metadata, and the
    ``clickhouse.export-partition-transaction-id`` idempotency check
    must prevent a double-commit. The destination ends with exactly one
    append snapshot carrying the transaction-id marker.
    """
    _require_multi_replica_catalog_mode(self)

    replica1 = self.context.nodes[0]
    replica2 = self.context.nodes[1]
    table_name = f"mt_{getuid()}"

    with Given("create the replicated source on every replica"):
        _setup_replicated_source(table_name, [replica1, replica2])

    with And("insert one partition's worth of rows on replica1"):
        insert_data(
            table_name=table_name,
            values="(1, 2020), (2, 2020), (3, 2020)",
            node=replica1,
        )

    with And("wait for replica2 to pick up the parts"):
        sync_replica(table_name=table_name, node=replica2)

    with Given("create a catalog-backed destination wired up on every replica"):
        # cluster_name fans the DataLakeCatalog CREATE DATABASE out via
        # ON CLUSTER so both replica1 and replica2 resolve the same
        # <database>.`ns.tbl` identifier even after replica1 disappears.
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=replica1,
            cluster_name=REPLICATED_CLUSTER,
        )

    initiator_started = True
    try:
        with When("schedule EXPORT PARTITION on replica1 without waiting"):
            export_partition(
                source_table=table_name,
                destination=destination,
                partition_id="2020",
                node=replica1,
                wait_for_completion=False,
            )

        with And("stop replica1 mid-flight via docker compose"):
            # ``docker compose stop`` sends SIGTERM and waits for a
            # graceful shutdown, so the container exits without
            # writing the COMPLETED status to Keeper. The Keeper
            # session times out, the task drops back to PENDING from
            # the surviving replicas' perspective, and replica2's
            # manifest-updating task picks the work up.
            replica1.stop()
            initiator_started = False

        with Then(
            "replica2 drives the export to COMPLETED on its own "
            "(timeout bumped to allow Keeper session expiry + retry)"
        ):
            wait_for_export_status(
                source_table=table_name,
                destination=destination,
                partition_id="2020",
                expected_status="COMPLETED",
                node=replica2,
                timeout=180,
            )

        with And(
            "exactly one snapshot exists - the survivor must not "
            "double-commit the partition"
        ):
            snapshots = get_snapshots(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert len(snapshots) == 1, error(
                f"Initiator-death recovery must not double-commit; "
                f"got {len(snapshots)} snapshots: "
                f"{[s.snapshot_id for s in snapshots]!r}"
            )
            operation = getattr(snapshots[0].summary, "operation", None)
            op_str = str(getattr(operation, "value", operation))
            assert op_str == "append", error(
                f"Expected append snapshot, got {op_str!r}"
            )

        with And(
            "snapshot summary carries the export-partition-transaction-id "
            "(the idempotency marker the survivor uses on retry)"
        ):
            summary = get_current_snapshot_summary(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            txn_id_key = "clickhouse.export-partition-transaction-id"
            assert txn_id_key in summary, error(
                f"Expected {txn_id_key!r} in snapshot summary so the "
                f"survivor can detect any prior commit by the dead "
                f"initiator; got keys {sorted(summary.keys())!r}"
            )

        with And("destination holds the partition's rows intact"):
            assert_destination_row_count(
                destination=destination,
                expected=3,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                node=replica2,
            )
    finally:
        if not initiator_started:
            with Finally("restart replica1 so the rest of the suite has all nodes"):
                replica1.start()


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_MultiReplicaRecovery("1.0"),
    RQ_Iceberg_ExportPartition_MultiReplicaRecovery_ZooKeeperBounce("1.0"),
)
@Name("export recovers after a ZooKeeper restart mid-flight")
def export_recovers_after_zookeeper_restart(
    self, minio_root_user, minio_root_password
):
    """Single-replica export survives a graceful ZooKeeper restart
    (clean session expiry, reconnect, commit to ``COMPLETED``).
    """
    _run_single_replica_zk_recovery(
        self,
        disturb=_disturb_zookeeper_graceful,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_MultiReplicaRecovery_ZooKeeperBounce("1.0"))
@Name("export recovers after a ZooKeeper SIGKILL + docker start")
def export_recovers_after_zookeeper_docker_kill(
    self, minio_root_user, minio_root_password
):
    """Single-replica export survives a SIGKILL'd ZooKeeper (abrupt
    ``ConnectionLoss``, transaction-log replay on restart). Same
    invariants as the graceful variant.
    """
    _run_single_replica_zk_recovery(
        self,
        disturb=_disturb_zookeeper_docker_kill,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_MultiReplicaRecovery_ZooKeeperBounce("1.0"))
@Name("concurrent cross-replica exports survive a ZooKeeper restart")
def cross_replica_exports_survive_zookeeper_restart(
    self, minio_root_user, minio_root_password
):
    """Two concurrent cross-replica exports survive a graceful ZooKeeper
    restart and preserve the linear snapshot chain.
    """
    _run_multi_replica_zk_recovery(
        self,
        disturb=_disturb_zookeeper_graceful,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_MultiReplicaRecovery_ZooKeeperBounce("1.0"))
@Name("concurrent cross-replica exports survive a ZooKeeper SIGKILL + docker start")
def cross_replica_exports_survive_zookeeper_docker_kill(
    self, minio_root_user, minio_root_password
):
    """Two concurrent cross-replica exports survive a SIGKILL'd
    ZooKeeper and preserve the linear snapshot chain.
    """
    _run_multi_replica_zk_recovery(
        self,
        disturb=_disturb_zookeeper_docker_kill,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


# =============================================================================
# Stress-only randomised replica chaos
# =============================================================================
#
# The scenarios below are gated by ``self.context.stress`` (set via the
# ``--stress`` regression flag) because every iteration costs at least one
# ClickHouse restart (~10-30s) and the randomised loops compound that.
# Each iteration seeds its PRNG from :func:`getuid` so a failure is
# reproducible: rerun against the same getuid-derived value to replay the
# exact phase / kill mode / restart-policy choices.

# Iterations per stress scenario. Bumped via the constant rather than via a
# CLI flag so callers can ratchet pressure up without changing infra.
STRESS_ITERATIONS = 3

# Wall-clock budget for the multi-partition chaos loop. Calibrated so most
# scheduled exports get at least one disruption but the scenario still
# settles within :data:`wait_for_exports_to_settle`'s timeout afterwards.
STRESS_CHAOS_DURATION_S = 30.0


def _kill_clickhouse_sigkill(victim):
    """SIGKILL ClickHouse inside the (still-running) container.

    Fastest disruption mode: skips the ``SYSTEM STOP MOVES`` /
    ``SYSTEM FLUSH LOGS`` / ``sync`` quiesce dance ``stop_clickhouse(safe=True)``
    runs, so any in-flight export task observes an instantaneous process
    death and the surviving replica must drive the work forward without
    on-disk hand-off from the victim.
    """
    victim.stop_clickhouse(safe=False, signal="KILL")


def _kill_container_stop(victim):
    """Stop the entire docker container.

    Mirrors a host-level outage: the CH process AND the userspace it ran
    in disappear together. Slower to recover than :func:`_kill_clickhouse_sigkill`
    because :func:`_ensure_alive` has to wait for the container to come
    back up before CH can boot.
    """
    victim.stop()


# (label, kill_fn) pairs the stress scenarios pick from at random. Revival
# is uniformly handled by :func:`_ensure_alive` regardless of which kill
# mode was used, so the pair only carries the kill side.
_KILL_MODES = (
    ("sigkill", _kill_clickhouse_sigkill),
    ("container_stop", _kill_container_stop),
)


def _ensure_alive(victim):
    """Bring ``victim`` back online if it is currently down. Idempotent.

    Probes the container before deciding which startup path to take so the
    helper handles every kill mode uniformly:

    * If the container is up but CH is dead, ``start_clickhouse()`` boots
      the CH process directly (matches :func:`_kill_clickhouse_sigkill`).
    * If the container itself is down, ``start()`` brings it back up; the
      ClickHouseNode entrypoint then starts CH on its own (matches
      :func:`_kill_container_stop`).

    Wrapping both probes in ``try/except`` keeps the helper safe to call
    from a Finally even when the container is in an awkward intermediate
    state (e.g. mid-stop), at the cost of an extra start attempt the
    follow-up call will short-circuit on.
    """
    try:
        if victim.clickhouse_pid() is not None:
            return
    except Exception:
        # ``clickhouse_pid`` shells into the container; if the container
        # is currently down the call raises, which we treat as "not alive".
        pass

    container_running = False
    try:
        result = victim.command("true", no_checks=True, steps=False)
        container_running = (result.exitcode == 0)
    except Exception:
        container_running = False

    if container_running:
        victim.start_clickhouse()
    else:
        victim.start()


def _assert_snapshot_chain_valid(snapshots, *, where):
    """Assert that ``snapshots`` (in metadata order) form a single linear
    chain of EXPORT PARTITION append commits.

    Mirrors the per-scenario checks already inlined in
    :func:`concurrent_cross_replica_different_partitions` /
    :func:`initiator_dies_mid_commit_peer_finalizes_exactly_once` and adds
    the txn-id-marker check that
    :func:`initiator_dies_mid_commit_peer_finalizes_exactly_once` runs
    (every snapshot must carry
    ``clickhouse.export-partition-transaction-id`` so a survivor's retry
    can detect a prior commit by the dead initiator). Empty input is
    vacuously valid — destinations where every export was killed before
    landing a snapshot are an expected outcome under chaos.
    """
    txn_id_key = "clickhouse.export-partition-transaction-id"

    for snap in snapshots:
        operation = getattr(snap.summary, "operation", None)
        op_str = str(getattr(operation, "value", operation))
        assert op_str == "append", error(
            f"{where}: expected append snapshot, got {op_str!r} for "
            f"snapshot_id={snap.snapshot_id}"
        )
        props = dict(snap.summary.additional_properties or {})
        assert txn_id_key in props, error(
            f"{where}: expected {txn_id_key!r} in snapshot summary so "
            f"survivor retries are idempotent; got keys "
            f"{sorted(props.keys())!r}"
        )

    for prev, curr in zip(snapshots, snapshots[1:]):
        assert curr.parent_snapshot_id == prev.snapshot_id, error(
            f"{where}: snapshot chain must be linear; "
            f"snapshot_id={curr.snapshot_id} parent={curr.parent_snapshot_id}, "
            f"expected parent={prev.snapshot_id}"
        )


def _require_stress(self):
    """Skip the scenario unless the regression was launched with ``--stress``.

    Stress scenarios run randomised disruption loops that cost minutes
    each; defaulting them off keeps every other CI run fast. Pair this
    with :func:`_require_multi_replica_catalog_mode` for chaos scenarios
    that also need a shared Iceberg destination.
    """
    if not getattr(self.context, "stress", False):
        skip("stress-only scenario; pass --stress to enable")


def _setup_chaos_table_with_destination(
    self,
    replicas,
    rows,
    minio_root_user,
    minio_root_password,
):
    """Shared setup for the stress scenarios: replicated source on every
    ``replicas`` node populated with ``rows`` (a SQL VALUES tail), and a
    catalog-backed Iceberg destination wired up via ``ON CLUSTER`` so any
    replica can resolve the same identifier.

    Returns ``(table_name, destination)``.
    """
    table_name = f"mt_{getuid()}"

    with Given("create the replicated source on every replica"):
        _setup_replicated_source(table_name, replicas)

    with And("seed the source with the chaos workload"):
        insert_data(
            table_name=table_name,
            values=rows,
            node=replicas[0],
        )

    with And("wait for peer replicas to pick up the parts"):
        for peer in replicas[1:]:
            sync_replica(table_name=table_name, node=peer)

    with Given("create a catalog-backed destination wired up on every replica"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=replicas[0],
            cluster_name=REPLICATED_CLUSTER,
        )

    return table_name, destination


@TestStep(When)
def _run_chaos_loop(self, kill_candidates, duration_s, rng):
    """Pick random victims from ``kill_candidates`` and bounce each once
    with random kill mode + downtime, looping until ``duration_s`` has
    elapsed.

    The caller is responsible for excluding the survivor it intends to
    use for observation queries from ``kill_candidates`` — this step does
    not enforce a "leave one alive" rule itself, so the contract is
    simpler and the caller can opt into more aggressive policies.
    """
    deadline = time.monotonic() + duration_s
    while time.monotonic() < deadline:
        kill_label, kill_fn = rng.choice(_KILL_MODES)
        victim = rng.choice(kill_candidates)
        sleep_before = rng.uniform(0.0, 2.0)
        sleep_down = rng.uniform(0.5, 3.0)

        with By(
            f"chaos: sleep {sleep_before:.2f}s, then {kill_label} on "
            f"{victim.name}, leave down for {sleep_down:.2f}s"
        ):
            time.sleep(sleep_before)
            kill_fn(victim)
            time.sleep(sleep_down)
            _ensure_alive(victim)


def _phased_kill_iteration(
    self,
    iteration,
    phase,
    victim,
    survivor,
    kill_label,
    kill_fn,
    restart_policy,
    rng,
    minio_root_user,
    minio_root_password,
):
    """One iteration of :func:`stress_replica_kill_at_random_phase`.

    ``phase`` selects when the kill fires relative to the export:

    * ``"post_schedule_pre_commit"`` — schedule, sleep [0, 1)s, kill.
      Targets the brief window between the synchronous ALTER returning
      and the background commit task starting work.
    * ``"during_commit_phase"`` — schedule, sleep [1, 5)s, kill. Targets
      the manifest-install / snapshot-commit window.
    * ``"post_complete"`` — schedule, wait for ``COMPLETED``, kill. Tests
      no-op invariance: the surviving replica must not double-commit
      after seeing the dead initiator's stash, and the destination state
      must remain unchanged.

    ``restart_policy`` decides when the victim comes back:

    * ``"immediate"`` — revive right after the kill.
    * ``"delayed_short"`` — revive after 1s.
    * ``"delayed_long"`` — revive after 5s.
    * ``"end_of_iteration"`` — leave down until the iteration's Finally
      so :func:`wait_for_exports_to_settle` exercises the survivor-only
      recovery path end-to-end.
    """
    rows = "(1, 2020), (2, 2020), (3, 2020)"
    _ensure_alive(victim)
    _ensure_alive(survivor)

    table_name, destination = _setup_chaos_table_with_destination(
        self,
        replicas=[victim, survivor],
        rows=rows,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    pre_kill_snapshot_id = None
    revived_inline = False

    try:
        if phase == "post_complete":
            with When("schedule EXPORT and wait for COMPLETED"):
                export_partition(
                    source_table=table_name,
                    destination=destination,
                    partition_id="2020",
                    node=victim,
                    wait_timeout=180,
                )
            with And("capture the pre-kill snapshot id"):
                snapshots = get_snapshots(
                    destination=destination,
                    minio_root_user=minio_root_user,
                    minio_root_password=minio_root_password,
                )
                assert len(snapshots) == 1, error(
                    f"iter {iteration} {phase}: expected 1 snapshot before "
                    f"kill, got {len(snapshots)}: "
                    f"{[s.snapshot_id for s in snapshots]!r}"
                )
                pre_kill_snapshot_id = snapshots[0].snapshot_id
        else:
            sleep_for = (
                rng.uniform(0.0, 1.0)
                if phase == "post_schedule_pre_commit"
                else rng.uniform(1.0, 5.0)
            )
            with When("schedule EXPORT PARTITION without waiting"):
                export_partition(
                    source_table=table_name,
                    destination=destination,
                    partition_id="2020",
                    node=victim,
                    wait_for_completion=False,
                )
            with And(f"sleep {sleep_for:.2f}s to advance into phase {phase!r}"):
                time.sleep(sleep_for)

        with When(f"kill {victim.name} via {kill_label}"):
            kill_fn(victim)

        if restart_policy == "immediate":
            with And(f"revive {victim.name} immediately"):
                _ensure_alive(victim)
                revived_inline = True
        elif restart_policy == "delayed_short":
            with And(f"revive {victim.name} after 1s"):
                time.sleep(1.0)
                _ensure_alive(victim)
                revived_inline = True
        elif restart_policy == "delayed_long":
            with And(f"revive {victim.name} after 5s"):
                time.sleep(5.0)
                _ensure_alive(victim)
                revived_inline = True
        # else: end_of_iteration — the Finally below revives the victim
        # after the survivor has had a chance to drive the export to
        # terminal status on its own.

        with Then("export reaches terminal status (observed from survivor)"):
            wait_for_exports_to_settle(
                source_table=table_name,
                destination=destination,
                partition_id="2020",
                node=survivor,
                timeout=300,
            )

        with And("destination snapshot state is consistent with the kill"):
            snapshots = get_snapshots(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )

            if phase == "post_complete":
                assert len(snapshots) == 1, error(
                    f"iter {iteration} {phase}: kill+revive after success "
                    f"must not change snapshot count; got {len(snapshots)}: "
                    f"{[s.snapshot_id for s in snapshots]!r}"
                )
                assert snapshots[0].snapshot_id == pre_kill_snapshot_id, error(
                    f"iter {iteration} {phase}: kill+revive after success "
                    f"must not replace the snapshot; pre={pre_kill_snapshot_id} "
                    f"post={snapshots[0].snapshot_id}"
                )
            else:
                assert len(snapshots) <= 1, error(
                    f"iter {iteration} {phase}: kill recovery must not "
                    f"produce duplicate snapshots; got {len(snapshots)}: "
                    f"{[s.snapshot_id for s in snapshots]!r}"
                )

            _assert_snapshot_chain_valid(
                snapshots, where=f"iter {iteration} {phase}"
            )

    finally:
        if not revived_inline:
            with Finally(f"revive {victim.name} before the next iteration"):
                _ensure_alive(victim)


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_MultiReplicaRecovery_RandomisedChaos("1.0"))
@Name("randomised replica kill at varied export-lifecycle phases")
def stress_replica_kill_at_random_phase(
    self, minio_root_user, minio_root_password
):
    """Repeat ``STRESS_ITERATIONS`` rounds of "schedule, kill, settle"
    with random phase, kill mode, and restart policy. Each iteration must
    converge to a terminal status with snapshot integrity preserved.
    """
    _require_stress(self)
    _require_multi_replica_catalog_mode(self)

    rng = random.Random(getuid())

    initiator = self.context.nodes[0]
    survivor = self.context.nodes[1]

    phases = (
        "post_schedule_pre_commit",
        "during_commit_phase",
        "post_complete",
    )
    restart_policies = (
        "immediate",
        "delayed_short",
        "delayed_long",
        "end_of_iteration",
    )

    for iteration in range(1, STRESS_ITERATIONS + 1):
        phase = rng.choice(phases)
        kill_label, kill_fn = rng.choice(_KILL_MODES)
        restart_policy = rng.choice(restart_policies)

        with When(
            f"iteration {iteration}: phase={phase} kill={kill_label} "
            f"restart={restart_policy}"
        ):
            _phased_kill_iteration(
                self,
                iteration=iteration,
                phase=phase,
                victim=initiator,
                survivor=survivor,
                kill_label=kill_label,
                kill_fn=kill_fn,
                restart_policy=restart_policy,
                rng=rng,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_MultiReplicaRecovery_RandomisedChaos("1.0"))
@Name("repeated initiator bounce during a single export")
def stress_initiator_repeated_bounce(
    self, minio_root_user, minio_root_password
):
    """Repeatedly stop+start the initiating replica during one export.

    The export must converge to a terminal status from the survivor's
    perspective, and the destination must hold at most one append
    snapshot for the partition (no double-commit across bounce cycles).
    """
    _require_stress(self)
    _require_multi_replica_catalog_mode(self)

    rng = random.Random(getuid())

    initiator = self.context.nodes[0]
    survivor = self.context.nodes[1]

    _ensure_alive(initiator)
    _ensure_alive(survivor)

    table_name, destination = _setup_chaos_table_with_destination(
        self,
        replicas=[initiator, survivor],
        rows="(1, 2020), (2, 2020), (3, 2020)",
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    bounce_count = rng.randint(3, 8)

    try:
        with When("schedule EXPORT PARTITION on the initiator without waiting"):
            export_partition(
                source_table=table_name,
                destination=destination,
                partition_id="2020",
                node=initiator,
                wait_for_completion=False,
            )

        with And(f"bounce the initiator {bounce_count} times with random gaps"):
            for i in range(1, bounce_count + 1):
                kill_label, kill_fn = rng.choice(_KILL_MODES)
                pre_kill_sleep = rng.uniform(0.0, 3.0)
                post_kill_sleep = rng.uniform(0.5, 3.0)

                with By(
                    f"bounce {i}: sleep {pre_kill_sleep:.2f}s, "
                    f"kill={kill_label}, down for {post_kill_sleep:.2f}s"
                ):
                    time.sleep(pre_kill_sleep)
                    kill_fn(initiator)
                    time.sleep(post_kill_sleep)
                    _ensure_alive(initiator)

        with Then("export reaches a terminal status (observed from survivor)"):
            wait_for_exports_to_settle(
                source_table=table_name,
                destination=destination,
                partition_id="2020",
                node=survivor,
                timeout=300,
            )

        with And("destination has at most one append snapshot for the partition"):
            snapshots = get_snapshots(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert len(snapshots) <= 1, error(
                f"Repeated bounce must not produce duplicate snapshots; "
                f"got {len(snapshots)}: {[s.snapshot_id for s in snapshots]!r}"
            )
            _assert_snapshot_chain_valid(
                snapshots, where="repeated initiator bounce"
            )

    finally:
        with Finally("ensure the initiator is online before the suite continues"):
            _ensure_alive(initiator)


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_MultiReplicaRecovery_RandomisedChaos("1.0"))
@Name("multi-partition fleet under randomised replica chaos")
def stress_multi_partition_chaos(
    self, minio_root_user, minio_root_password
):
    """Schedule N partition exports concurrently from alternating replicas
    and run a chaos thread that randomly bounces a victim replica for
    :data:`STRESS_CHAOS_DURATION_S` seconds. After chaos exits, every
    export must settle to a terminal status, the destination's snapshot
    chain must be linear and txn-id-tagged, and the snapshot count must
    not exceed the partition count (no double-commits).
    """
    _require_stress(self)
    _require_multi_replica_catalog_mode(self)

    rng = random.Random(getuid())

    # Two replicas: one initiates exports + acts as chaos victim, the
    # other is reserved as the survivor we observe through. The chaos
    # loop only knows about ``victim`` so it can never accidentally take
    # both nodes down at once. Bumping to 3 victims would require the
    # caller to ensure the survivor is excluded from kill_candidates.
    victim = self.context.nodes[0]
    survivor = self.context.nodes[1]

    _ensure_alive(victim)
    _ensure_alive(survivor)

    partitions = [2020, 2021, 2022, 2023, 2024]
    rows = ", ".join(f"({i + 1}, {p})" for i, p in enumerate(partitions))

    table_name, destination = _setup_chaos_table_with_destination(
        self,
        replicas=[victim, survivor],
        rows=rows,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

    try:
        with When("schedule each partition's export from alternating replicas"):
            initiators = [victim, survivor]
            for i, partition_id in enumerate(partitions):
                export_partition(
                    source_table=table_name,
                    destination=destination,
                    partition_id=str(partition_id),
                    node=initiators[i % len(initiators)],
                    wait_for_completion=False,
                )

        with And(
            f"bounce {victim.name} randomly for {STRESS_CHAOS_DURATION_S}s "
            f"in parallel with the export fleet"
        ):
            with Pool(1) as pool:
                Step(
                    "chaos loop",
                    test=_run_chaos_loop,
                    parallel=True,
                    executor=pool,
                )(
                    kill_candidates=[victim],
                    duration_s=STRESS_CHAOS_DURATION_S,
                    rng=rng,
                )
                join()

        with Then("every export converges to a terminal status"):
            for partition_id in partitions:
                wait_for_exports_to_settle(
                    source_table=table_name,
                    destination=destination,
                    partition_id=str(partition_id),
                    node=survivor,
                    timeout=300,
                )

        with And(
            "destination snapshot chain is linear, txn-id-tagged, and bounded "
            "by the partition count"
        ):
            snapshots = get_snapshots(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert len(snapshots) <= len(partitions), error(
                f"Snapshot count must not exceed partition count under chaos; "
                f"got {len(snapshots)} snapshots for {len(partitions)} "
                f"partitions: {[s.snapshot_id for s in snapshots]!r}"
            )
            _assert_snapshot_chain_valid(
                snapshots, where="multi-partition chaos"
            )

    finally:
        with Finally(f"ensure {victim.name} is online before the suite continues"):
            _ensure_alive(victim)


SCENARIOS = (
    concurrent_cross_replica_different_partitions,
    concurrent_cross_replica_same_partition_idempotent,
    initiator_dies_mid_commit_peer_finalizes_exactly_once,
    export_recovers_after_zookeeper_restart,
    export_recovers_after_zookeeper_docker_kill,
    cross_replica_exports_survive_zookeeper_restart,
    cross_replica_exports_survive_zookeeper_docker_kill,
    stress_replica_kill_at_random_phase,
    stress_initiator_repeated_bounce,
    stress_multi_partition_chaos,
)


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_MultiReplicaRecovery("1.0"))
@Name("multi replica recovery")
def feature(self, minio_root_user, minio_root_password):
    """Multi-replica EXPORT PARTITION concurrency and ZooKeeper recovery."""
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
