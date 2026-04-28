"""Backward-compatibility: ReplicatedMergeTree without the ``/exports`` znode.

The EXPORT PARTITION feature added a new persistent znode,
``/clickhouse/tables/<table>/exports``, under every RMT table's ZK
path. Tables created on CH builds that predate the feature do not
have that node, and neither do replicas whose ZK state was restored
from a pre-feature backup.

``StorageReplicatedMergeTree`` heals this on *every* replica attach,
not just on CREATE TABLE:

* ``createNewZooKeeperNodesAttempt()`` asynchronously creates
  ``zookeeper_path + "/exports"`` alongside ``/quorum``, ``/mutations``,
  and the rest of the legacy back-compat bag
  (``StorageReplicatedMergeTree.cpp`` line 968).
* ``ReplicatedMergeTreeAttachThread::runImpl`` at line 199 calls
  ``storage.createNewZooKeeperNodes(...)`` as part of the normal
  replica-attach flow — so a cold server start, a ``DETACH``+``ATTACH``,
  or ``SYSTEM RESTART REPLICA`` all re-create the missing znode before
  the replica is promoted out of readonly mode.

That means the realistic upgrade / restore-from-backup path — boot
the server against the old ZK state — is self-healing: by the time
any user query can reach the replica, ``/exports`` is back. The
EXPORT PARTITION code itself does *not* issue a ``CreateIfNotExists``
for the parent as part of its commit multi-op (it only creates
``/exports/<key>``), so deleting ``/exports`` under a running table
without a subsequent attach does block EXPORT — but that is an
operator-foot-gun scenario, not an upgrade scenario, and it too is
cleared by ``SYSTEM RESTART REPLICA``.

Scenarios here exercise the real contract: legacy or missing
``/exports`` plus a replica attach recovers EXPORT. Both scenarios
explicitly use ``SYSTEM RESTART REPLICA`` to force the attach-thread
to run; that matches what a CH server restart would do without
having to cycle the container.

Scope:
This module is ``no_catalog``-only. The legacy-ZK question is about
RMT itself (the source side of EXPORT), which is identical across
catalog modes — running this scenario once per destination catalog
would just multiply the same ZooKeeper assertions by three without
exercising any new code paths.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import RQ_Iceberg_ExportPartition_ZooKeeperCompat

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    _require_no_catalog,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    assert_source_and_destination_match,
)
from iceberg.tests.export_partition.steps.zookeeper import (
    ensure_zk_path_absent,
    zk_node_exists,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"


@TestStep(When)
def restart_replica(self, table_name, node=None):
    """Run ``SYSTEM RESTART REPLICA`` against ``table_name``.

    This re-enters the table through ``LoadingStrictnessLevel::ATTACH``
    and therefore triggers ``ReplicatedMergeTreeAttachThread::runImpl``
    → ``storage.createNewZooKeeperNodes(...)``, which is what re-creates
    the ``/exports`` znode on upgraded / restored ZK state.
    Used here instead of a full server restart so the test stays quick
    while exercising the same recovery code path.
    """
    if node is None:
        node = self.context.node
    node.query(f"SYSTEM RESTART REPLICA {table_name}")


@TestScenario
@Name("export after restart recreates missing exports znode")
def export_after_restart_recreates_exports_znode(
    self, minio_root_user, minio_root_password
):
    """Pre-feature / restored-from-backup layout: ``/exports`` absent
    at session start. ``SYSTEM RESTART REPLICA`` must recreate it via
    the attach thread, and the subsequent EXPORT must succeed.

    This is the realistic upgrade path — on a real server restart the
    attach thread runs before any user query can reach the replica,
    so ``/exports`` is always back by the time EXPORT is issued.
    """
    _require_no_catalog(
        "legacy ZK layout is a ReplicatedMergeTree concern, not a "
        "destination concern; run it once via the no_catalog path"
    )

    source_table = f"mt_{getuid()}"
    zk_path = f"/clickhouse/tables/{source_table}"
    exports_path = f"{zk_path}/exports"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            zk_path=zk_path,
        )

    with And("insert data into two partitions"):
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020), (3, 2021)",
        )

    with And(f"force the legacy layout — ensure {exports_path!r} is absent"):
        # No-op when the build under test has not yet auto-created the
        # znode (so we already have the pre-feature layout); deletes it
        # when a newer build did create it on CREATE TABLE. Either way
        # the replica enters the restart step without /exports.
        ensure_zk_path_absent(path=exports_path)

    with When(
        "SYSTEM RESTART REPLICA — attach thread should re-create /exports"
    ):
        restart_replica(table_name=source_table)

    with Then("/exports is back after the replica attach"):
        assert zk_node_exists(path=exports_path), error(
            f"{exports_path!r} was not re-created by the replica attach; "
            "ReplicatedMergeTreeAttachThread::runImpl is expected to call "
            "storage.createNewZooKeeperNodes which asyncTryCreateNoThrow's "
            "the /exports node. If this assertion fires, the heal path "
            "moved and upgrade-from-pre-feature RMT is no longer "
            "self-healing."
        )

    with And("create the Iceberg destination and run EXPORT"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with And("destination matches the exported partition"):
        assert_destination_row_count(
            destination=destination,
            expected=2,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert_source_and_destination_match(
            source_table=source_table,
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            partition_where="year = 2020",
            order_by="id",
        )


@TestScenario
@Name("restart heals operator-deleted exports znode mid-session")
def restart_heals_operator_deletion(
    self, minio_root_user, minio_root_password
):
    """Operator-foot-gun path: ``/exports`` is deleted out from under
    a live, already-exported RMT. A subsequent ``SYSTEM RESTART REPLICA``
    must bring EXPORT back online. Unlike scenario 1, the znode had
    per-export children before deletion, so this also confirms the
    recovery is idempotent with respect to prior EXPORT history stored
    elsewhere in the replica state (the EXPORT completion records live
    under the replica path, not under ``/exports``).
    """
    _require_no_catalog(
        "legacy ZK layout is a ReplicatedMergeTree concern, not a "
        "destination concern; run it once via the no_catalog path"
    )

    source_table = f"mt_{getuid()}"
    zk_path = f"/clickhouse/tables/{source_table}"
    exports_path = f"{zk_path}/exports"

    with Given("create the RMT source, insert data, create destination"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            zk_path=zk_path,
        )
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2021), (3, 2022)",
        )
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("first EXPORT populates /exports with a real child node"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )
        assert zk_node_exists(path=exports_path), error(
            f"{exports_path!r} should exist after a successful EXPORT; "
            "the rest of the scenario depends on deleting a populated "
            "parent, not an already-missing one."
        )

    with When(
        f"delete {exports_path!r} out from under the live table "
        "(simulating an operator mistake or external ZK wipe)"
    ):
        ensure_zk_path_absent(path=exports_path)

    with And("SYSTEM RESTART REPLICA to trigger the attach-thread heal"):
        restart_replica(table_name=source_table)

    with Then("/exports is back after the replica attach"):
        assert zk_node_exists(path=exports_path), error(
            f"{exports_path!r} was not re-created by the replica "
            "attach after mid-session deletion; the attach-thread "
            "heal path is the only supported recovery, so regressions "
            "here turn operator foot-guns into permanent bricks."
        )

    with And("a fresh EXPORT against a new partition still works"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2022",
        )
        assert_destination_row_count(
            destination=destination,
            expected=2,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_ZooKeeperCompat("1.0"))
@Name("zk compat")
def feature(self, minio_root_user, minio_root_password):
    """Backward compatibility with pre-EXPORT-feature ZooKeeper layouts
    and operator-deletion recovery via replica attach."""
    Scenario(test=export_after_restart_recreates_exports_znode, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=restart_heals_operator_deletion, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
