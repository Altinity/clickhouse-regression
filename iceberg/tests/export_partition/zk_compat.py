"""Backward-compatibility: ReplicatedMergeTree without the ``/exports`` znode.

Verifies the self-healing contract: a missing or deleted
``/clickhouse/tables/<table>/exports`` znode is recreated on replica
attach (``SYSTEM RESTART REPLICA``) and EXPORT works again. ``no_catalog``
only — this is a ReplicatedMergeTree concern, not a destination concern.
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
    """``SYSTEM RESTART REPLICA``: re-enters the attach thread so
    ``createNewZooKeeperNodes`` runs (same recovery path as a server
    restart, without cycling the container).
    """
    if node is None:
        node = self.context.node
    node.query(f"SYSTEM RESTART REPLICA {table_name}")


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_ZooKeeperCompat("1.0"))
@Name("export after restart recreates missing exports znode")
def export_after_restart_recreates_exports_znode(
    self, minio_root_user, minio_root_password
):
    """Pre-feature / restored-from-backup layout (``/exports`` absent):
    ``SYSTEM RESTART REPLICA`` recreates it via the attach thread and
    the subsequent EXPORT succeeds.
    """
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
@Requirements(RQ_Iceberg_ExportPartition_ZooKeeperCompat("1.0"))
@Name("restart heals operator-deleted exports znode mid-session")
def restart_heals_operator_deletion(
    self, minio_root_user, minio_root_password
):
    """Deleting ``/exports`` mid-session (operator foot-gun) is healed
    by ``SYSTEM RESTART REPLICA`` and a fresh EXPORT against a new
    partition still works.
    """
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
@Name("zk compat")
def feature(self, minio_root_user, minio_root_password):
    """Backward compatibility with pre-EXPORT-feature ZooKeeper layouts
    and operator-deletion recovery via replica attach.

    ``no_catalog`` only — the ``/exports`` znode lives under the
    ``ReplicatedMergeTree`` source path, so the destination's catalog
    flavour is irrelevant. Filter at load time to avoid penalising the
    requirement count with not-applicable runtime ``skip()``s.
    """
    _require_no_catalog(
        "legacy ZK layout is a ReplicatedMergeTree concern, not a "
        "destination concern; run it once via the no_catalog path"
    )
    Scenario(test=export_after_restart_recreates_exports_znode, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=restart_heals_operator_deletion, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
