"""Multi-replica EXPORT PARTITION scenarios.

The scenarios in :mod:`iceberg.tests.export_partition.concurrent_writes`
exercise concurrency through a single replica — they deliberately avoid
running two ALTERs in parallel against the same ClickHouse container
because TestFlows' pty management segfaults when two bash sessions share
one node. That coverage gap matters because in practice users run
``EXPORT PARTITION`` from whichever replica happens to hold the
requested parts, and the ZooKeeper-backed idempotency / snapshot-commit
protocol is meant to hold up across replicas.

This module covers that missing surface along two axes — concurrency
across replicas and recoverability under ZooKeeper disturbance:

* Two replicas concurrently exporting *different* partitions of the
  same source table into one shared catalog-backed Iceberg destination.
  The destination must end up with one linearised append-snapshot per
  partition, and every replica must see the final state.
* Two replicas concurrently exporting the *same* partition. The
  ZooKeeper-backed idempotency key rejects every caller after the
  first with ``BAD_ARGUMENTS`` ("Export with key ..."); the
  destination's snapshot log must gain exactly one snapshot, matching
  the guarantee :mod:`iceberg.tests.export_partition.transactions`
  already validates in the single-replica case
  (``duplicate_export_within_ttl_rejected``).
* A single-replica export that starts normally, then gets interrupted
  by ZooKeeper bouncing mid-flight. CH's export scheduler must
  reconnect its ZK session, retry from whatever step it was on
  (manifest install / snapshot commit / COMPLETED publish), and end
  with exactly one Iceberg snapshot holding the partition's rows.
  Covered for two disturbance modes: graceful ``zkServer.sh restart``
  and harsh ``docker kill -s SIGKILL`` + ``docker start``.
* The multi-replica version: two replicas concurrently export two
  different partitions and ZooKeeper bounces while both exports are
  in flight. Both exports must converge to COMPLETED and the
  destination must end up with two linearised append snapshots. Same
  two disturbance modes as the single-replica variant.

Each disturbance mode exercises a different failure surface: the
graceful restart is a clean session expiry ClickHouse should always
shake off, while the SIGKILL + ``docker start`` path gives the ZK
process no chance to checkpoint state or send disconnects, leaving
mid-commit operations to the ZK transaction log replay on restart. The
graceful and SIGKILL variants share assertion bodies
(:func:`_run_single_replica_zk_recovery` and
:func:`_run_multi_replica_zk_recovery`) so the two modes cannot drift
apart.

## Scope: catalog-only for the multi-replica scenarios

Under ``no_catalog`` mode each CH node owns its own ``IcebergS3(...)``
table; there is no cheap way to make two replicas write to the *same*
Iceberg destination without open-coding a shared metadata.json
handshake and ``CREATE TABLE`` race. Under ``rest`` / ``glue`` the
``DataLakeCatalog`` database is propagated via
``CREATE DATABASE ... ON CLUSTER`` so every replica resolves the
same ``<database>.`<namespace.table>``` identifier against a shared
registered table — the production-realistic multi-writer surface.
The multi-replica scenarios therefore skip under ``no_catalog``. The
single-replica ZK-restart scenario runs in every catalog mode.

## ZooKeeper disturbance helpers

Both disturbance modes drive the ZooKeeper container lifecycle through
``cluster.docker_compose`` — the graceful path via ``docker compose
restart`` (SIGTERM → clean stop → start) and the harsh path via
``docker compose kill -s SIGKILL`` + ``docker compose start``. Going
through docker-compose inherits the project-directory wiring
``helpers.cluster`` already sets up (no need to hardcode container
names like ``iceberg_env-zookeeper1-1``) and keeps the two modes from
disagreeing over who owns the pid file on the ZK data volume — see
:func:`_disturb_zookeeper_graceful` for the full rationale.

``_zk_wait_healthy`` still uses ``zkServer.sh status`` from inside the
container to confirm ZK is accepting client connections again, since
the health probe is orthogonal to how the container was restarted.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import RQ_Iceberg_ExportPartition_MultiReplicaRecovery

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
    """Invoke ``zkServer.sh <subcommand>`` on the ZooKeeper container.

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

    ``docker compose restart`` sends SIGTERM, waits for the ZK process
    to checkpoint state and respond to close frames, then calls
    ``start`` — semantically identical to what
    ``ZooKeeperNode.restart_zookeeper()`` (``zkServer.sh restart``)
    gives us, with one important difference: the lifecycle is driven
    from outside the container, so it cannot disagree with the harsh
    :func:`_disturb_zookeeper_docker_kill` path over who owns the
    ``/data/zookeeper_server.pid`` file.

    Why that matters: ``zkServer.sh start`` runs ZK as a daemon and
    writes ``/data/zookeeper_server.pid``; the official zookeeper
    image's entrypoint runs ``zkServer.sh start-foreground`` which
    does not. If the graceful path used ``zkServer.sh restart`` and
    was sequenced after a docker-kill scenario in the same run, the
    next ``zkServer.sh stop`` would try to ``kill`` the stale daemon
    PID from before the container crash, succeed trivially
    ("No such process"), then ``zkServer.sh start`` would race the
    still-live foreground ZK for port 2181 and fail with
    "FAILED TO START". Routing both disturbance modes through
    docker-compose eliminates that cross-scenario pid-file drift.
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
@Name("concurrent exports from different replicas on different partitions")
def concurrent_cross_replica_different_partitions(
    self, minio_root_user, minio_root_password
):
    """Two replicas race to export two different partitions of the same table.

    The Iceberg commit protocol must linearise both commits through
    ZooKeeper: the destination ends with exactly two ``append``
    snapshots chained head-to-tail (newer ``parent_snapshot_id`` ==
    older ``snapshot_id``) and both partitions' rows are reachable from
    the latest snapshot. Either scheduling order is acceptable as long
    as the chain is linear.
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
@Name("concurrent exports of the same partition from different replicas are idempotent")
def concurrent_cross_replica_same_partition_idempotent(
    self, minio_root_user, minio_root_password
):
    """Two replicas try to export the same partition; only one commits.

    The first ALTER installs a ZK idempotency entry keyed on
    ``(source_table, destination, partition_id)`` and schedules the
    background export. The second ALTER — landing on a different
    replica — observes the existing key and is rejected synchronously
    with ``BAD_ARGUMENTS`` ("Export with key ..."), exactly like the
    single-replica ``duplicate_export_within_ttl_rejected`` scenario in
    :mod:`iceberg.tests.export_partition.transactions`. The shared
    destination must end up with exactly one append snapshot and no
    double-commit of the partition's rows.

    The second ALTER is fired *after* the first returns control to the
    client, so the ZK key is already installed when replica2 evaluates
    the ALTER — the rejection is deterministic. The asynchronous race
    we're actually stressing is between replica1's background commit
    task and replica2's synchronous ALTER rejection path.
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
    """Shared body for the single-replica ZK-disturbance scenarios.

    ``disturb`` is a callable taking ``self`` that inflicts whatever
    kind of ZooKeeper bounce the calling scenario wants to exercise
    (graceful ``zkServer.sh restart`` or harsh ``docker kill``).
    Everything else — setup, schedule, post-bounce assertions — is
    identical so the graceful and crash paths cannot drift apart.
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
    """Shared body for the multi-replica ZK-disturbance scenarios.

    Two replicas schedule ``EXPORT PARTITION`` on different partitions
    against the same shared catalog-backed destination; ``disturb`` is
    applied while both background tasks are in flight. Both must
    reconnect their ZK sessions and drive their commits to completion,
    and the destination must end up with exactly two linearised append
    snapshots (one per partition) with no duplicates and no lost rows.
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
@Name("export recovers after a ZooKeeper restart mid-flight")
def export_recovers_after_zookeeper_restart(
    self, minio_root_user, minio_root_password
):
    """Single-replica export must survive a graceful ``zkServer.sh restart``.

    See :func:`_run_single_replica_zk_recovery` for the shared body.
    The graceful-restart branch is the baseline recoverability claim:
    in-flight export tasks observe a clean session expiry, reconnect,
    and drive their commits to COMPLETED.
    """
    _run_single_replica_zk_recovery(
        self,
        disturb=_disturb_zookeeper_graceful,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


@TestScenario
@Name("export recovers after a ZooKeeper SIGKILL + docker start")
def export_recovers_after_zookeeper_docker_kill(
    self, minio_root_user, minio_root_password
):
    """Single-replica export must survive a ``docker kill -s SIGKILL`` crash.

    Harsher variant of :func:`export_recovers_after_zookeeper_restart`:
    the ZK process dies without checkpointing state or sending a
    disconnect, so in-flight export tasks observe an abrupt
    ``ConnectionLoss`` and any mid-commit operation is left to the ZK
    transaction log to replay on restart. All other invariants (row
    count, single append snapshot, no double-commit) are identical to
    the graceful path — see :func:`_run_single_replica_zk_recovery`.
    """
    _run_single_replica_zk_recovery(
        self,
        disturb=_disturb_zookeeper_docker_kill,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


@TestScenario
@Name("concurrent cross-replica exports survive a ZooKeeper restart")
def cross_replica_exports_survive_zookeeper_restart(
    self, minio_root_user, minio_root_password
):
    """Multi-replica version of ``export_recovers_after_zookeeper_restart``.

    See :func:`_run_multi_replica_zk_recovery` for the shared body.
    The graceful-restart branch validates that two concurrent
    cross-replica commits both reconnect cleanly and preserve the
    linear snapshot chain.
    """
    _run_multi_replica_zk_recovery(
        self,
        disturb=_disturb_zookeeper_graceful,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


@TestScenario
@Name("concurrent cross-replica exports survive a ZooKeeper SIGKILL + docker start")
def cross_replica_exports_survive_zookeeper_docker_kill(
    self, minio_root_user, minio_root_password
):
    """Multi-replica version of ``export_recovers_after_zookeeper_docker_kill``.

    Harsher variant of
    :func:`cross_replica_exports_survive_zookeeper_restart`: both
    replicas' in-flight export tasks observe an abrupt
    ``ConnectionLoss`` when zookeeper1 is SIGKILL'd mid-flight, and
    must still converge to COMPLETED with a single linearised append
    chain after the container comes back up. Shared invariants live in
    :func:`_run_multi_replica_zk_recovery`.
    """
    _run_multi_replica_zk_recovery(
        self,
        disturb=_disturb_zookeeper_docker_kill,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )


SCENARIOS = (
    concurrent_cross_replica_different_partitions,
    concurrent_cross_replica_same_partition_idempotent,
    export_recovers_after_zookeeper_restart,
    export_recovers_after_zookeeper_docker_kill,
    cross_replica_exports_survive_zookeeper_restart,
    cross_replica_exports_survive_zookeeper_docker_kill,
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
