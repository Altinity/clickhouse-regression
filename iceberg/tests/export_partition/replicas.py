"""Replicated-cluster EXPORT PARTITION scenarios.

Covers behaviour that only applies when multiple ClickHouse replicas share a
single catalog-backed Iceberg destination (``ice`` / ``glue`` catalog modes).
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_MultiReplicaRecovery_SettingDisabledFailover,
)

from helpers.common import getuid
from helpers.config import users_d

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
    sync_replica,
)
from iceberg.tests.export_partition.steps.export_operations import (
    prepare_export_partition_settings,
)
from iceberg.tests.export_partition.steps.export_status import (
    get_export_row,
    wait_for_export_status,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
)


REPLICATED_CLUSTER = "replicated_cluster"

CATALOG_MODES_FOR_REPLICAS = ("ice", "glue")

SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"

_EXPORT_GATE_OFF_PROFILE = "export_partition_no_iceberg_gate"
_EXPORT_GATE_OFF_USER = "export_partition_gate_off"


def _setup_simple_replicated_source(table_name, nodes):
    """Two-replica RMT shaped like :mod:`multi_replica_recovery`'s SIMPLE schema."""
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
@Requirements(
    RQ_Iceberg_ExportPartition_MultiReplicaRecovery_SettingDisabledFailover("1.0")
)
@Name(
    "peer replica completes export when initiator has allow_experimental_insert_into_iceberg disabled"
)
def peer_completes_export_when_initiator_setting_disabled(
    self, minio_root_user, minio_root_password
):
    """Register a restrictive **profile** in shared ``users.d``, then create an
    auxiliary login with ``CREATE USER … SETTINGS PROFILE …`` so RBAC
    ``GRANT`` statements apply (they cannot target identities that exist only
    in ``users_xml`` — ``ACCESS_STORAGE_READONLY``).

    Submit ``ALTER … EXPORT`` from the initiating replica as that user so the
    session's merged defaults lack ``allow_experimental_insert_into_iceberg``
    while ``default`` keeps the suite-wide ``1``. The peer is expected to
    finalize the export.

    Verifies that:

    * The export reaches ``COMPLETED`` despite the initiator identity lacking
      the gate in profile defaults (while ``SETTINGS … = 1`` still parses).
    * The destination ends up with every source row.
    * ``system.replicated_partition_exports.source_replica`` stays the
      initiating replica's name (manifest provenance) while completion still
      proves the peer path worked with gate-enabled defaults.

    Why not tweak ``profiles/default`` on one replica only? Every iceberg CH
    container mounts the same host ``configs/clickhouse/users.d`` volume — any
    file dropped via ``docker compose exec clickhouse1`` is visible to
    ``clickhouse2`` as well.
    """
    disabled_replica = self.context.nodes[0]
    enabled_replica = self.context.nodes[1]
    replicas = [disabled_replica, enabled_replica]
    table_name = f"replicas_failover_{getuid()}"
    partition_id = "2020"
    gate_off_users_xml = f"export_partition_gate_off_{getuid()}.xml"

    with Given(
        f"add {_EXPORT_GATE_OFF_PROFILE!r} to users.d "
        f"(allow_experimental_insert_into_iceberg = 0)"
    ):
        users_d.create_and_add(
            entries={
                "profiles": {
                    _EXPORT_GATE_OFF_PROFILE: {
                        "allow_experimental_insert_into_iceberg": "0",
                    },
                },
            },
            config_file=gate_off_users_xml,
            node=disabled_replica,
            modify=False,
        )

    # SQL ``GRANT`` cannot attach privileges to users defined only in
    # ``users_xml`` (ACCESS_STORAGE_READONLY). Drop an SQL shadow of the
    # auxiliary user on teardown before removing the profile XML.
    with Finally(
        f"drop SQL user {_EXPORT_GATE_OFF_USER} on both replicas "
        f"(keep users_xml profile removable)"
    ):
        for replica in replicas:
            replica.query(
                f"DROP USER IF EXISTS {_EXPORT_GATE_OFF_USER}",
                steps=False,
                no_checks=True,
            )

    with And(
        f"create SQL user {_EXPORT_GATE_OFF_USER} bound to "
        f"{_EXPORT_GATE_OFF_PROFILE!r}, then grant default.*"
    ):
        for replica in replicas:
            replica.query(f"DROP USER IF EXISTS {_EXPORT_GATE_OFF_USER}")
            replica.query(
                f"CREATE USER {_EXPORT_GATE_OFF_USER} "
                f"IDENTIFIED WITH plaintext_password BY '' "
                f"SETTINGS PROFILE {_EXPORT_GATE_OFF_PROFILE}"
            )
            replica.query(f"GRANT ALL ON default.* TO {_EXPORT_GATE_OFF_USER}")

    def _iceberg_gate_session_value(node, user=None):
        settings = []
        if user is not None:
            settings.append(("user", user))
            settings.append(("password", ""))
        return node.query(
            "SELECT value FROM system.settings "
            "WHERE name = 'allow_experimental_insert_into_iceberg'",
            settings=settings,
        ).output.strip()

    with And(
        f"sanity-check {_EXPORT_GATE_OFF_USER} resolves "
        f"allow_experimental_insert_into_iceberg = 0"
    ):
        gate_off_value = _iceberg_gate_session_value(
            disabled_replica, user=_EXPORT_GATE_OFF_USER
        )
        assert gate_off_value == "0", error(
            f"auxiliary user {_EXPORT_GATE_OFF_USER!r} should observe gate off; "
            f"got {gate_off_value!r}"
        )

    with And(
        f"sanity-check default sessions still observe gate enabled " f"on both replicas"
    ):
        for replica in replicas:
            v = _iceberg_gate_session_value(replica, user=None)
            assert v == "1", error(
                f"{replica.name} default profile unexpectedly has "
                f"allow_experimental_insert_into_iceberg = {v!r}"
            )

    with Given("create the replicated source on both replicas"):
        _setup_simple_replicated_source(table_name, replicas)

    with And(f"insert one partition's worth of rows on {disabled_replica.name}"):
        insert_data(
            table_name=table_name,
            values="(1, 2020), (2, 2020), (3, 2020)",
            node=disabled_replica,
        )

    with And(f"wait for {enabled_replica.name} to pick up the parts"):
        sync_replica(table_name=table_name, node=enabled_replica)

    with Given("create a catalog-backed iceberg destination wired up on every replica"):
        # Use ``default`` so CREATE DATABASE is not gated on the auxiliary user.
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=enabled_replica,
            cluster_name=REPLICATED_CLUSTER,
        )

    dest_db = destination["database_name"]
    with And(
        f"grant {_EXPORT_GATE_OFF_USER!r} access to {dest_db!r} "
        f"(default.* already granted at user creation)"
    ):
        for replica in replicas:
            replica.query(f"GRANT ALL ON {dest_db}.* TO {_EXPORT_GATE_OFF_USER}")

    with When(
        f"submit ALTER ... EXPORT PARTITION from {disabled_replica.name} "
        f"as {_EXPORT_GATE_OFF_USER!r} (profile defaults gate off; per-query "
        f"SETTINGS allow_experimental_insert_into_iceberg = 1 still attached)"
    ):
        dest_sql_name = as_destination_name(destination)
        alter_settings = list(
            prepare_export_partition_settings(self.context.catalog, [])
        )
        alter_settings.extend(
            [
                ("user", _EXPORT_GATE_OFF_USER),
                ("password", ""),
            ]
        )
        disabled_replica.query(
            f"ALTER TABLE {table_name} "
            f"EXPORT PARTITION ID '{partition_id}' "
            f"TO TABLE {dest_sql_name}",
            settings=alter_settings,
        )

    with Then(
        f"the export reaches COMPLETED even though {disabled_replica.name} "
        f"cannot commit; the peer finalizes via the Keeper-stashed manifest"
    ):
        wait_for_export_status(
            source_table=table_name,
            destination=destination,
            partition_id=partition_id,
            expected_status="COMPLETED",
            node=enabled_replica,
            timeout=180,
        )

    with And("destination holds the partition's rows intact"):
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=enabled_replica,
        )

    with And(
        "system.replicated_partition_exports.source_replica names the "
        "initiating replica (manifest field), not the peer that may finalize "
        "the Iceberg commit"
    ):
        source_replica = get_export_row(
            source_table=table_name,
            destination=destination,
            partition_id=partition_id,
            columns="source_replica",
            node=enabled_replica,
        )
        assert source_replica is not None, error(
            "export row missing source_replica column"
        )
        disabled_index = replicas.index(disabled_replica) + 1
        expected_replica_name = f"r{disabled_index}"
        assert source_replica == expected_replica_name, error(
            f"Expected source_replica = {expected_replica_name!r} "
            f"(initiator {disabled_replica.name}); got {source_replica!r}. "
            f"If this drifts, manifest provenance for EXPORT PARTITION may have "
            f"changed upstream."
        )


SCENARIOS = (peer_completes_export_when_initiator_setting_disabled,)


@TestFeature
@Name("replicas")
def feature(self, minio_root_user, minio_root_password):
    """EXPORT PARTITION scenarios that need a multi-replica catalog-backed cluster."""

    if not hasattr(self.context, "nodes") or len(self.context.nodes) < 2:
        skip("need at least two ClickHouse replicas")
    if self.context.catalog not in CATALOG_MODES_FOR_REPLICAS:
        skip(
            "replicas scenarios need a catalog-registered destination shared "
            "across nodes; no_catalog mode has each replica managing its own "
            "IcebergS3 table"
        )

    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
