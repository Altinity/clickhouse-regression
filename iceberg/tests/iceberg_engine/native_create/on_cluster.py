"""Distributed DDL against a catalog database and shared-catalog visibility
(plan §3.10, invariants F)."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *

CLUSTER = "all"
COLUMNS = ["id Int64", "name String"]


def ddl_queue_entries(node, needle):
    return node.query(
        f"SELECT count() FROM system.distributed_ddl_queue WHERE query LIKE '%{needle}%'"
    ).output.strip()


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_OnCluster_Rejected("1.0"))
def on_cluster_rejected_on_initiator(self):
    """F1: CREATE, DROP and ALTER with ON CLUSTER fail on the initiator with
    NOT_IMPLEMENTED, enqueue nothing, and leave the catalog unchanged.
    RENAME has no initiator check and is stopped by the worker guard."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    node = self.context.node
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with Check("CREATE TABLE ON CLUSTER", flags=TE):
        with By("snapshot state"):
            before = snapshot_state(**args)
        queued = ddl_queue_entries(node, table_name)
        node.query(
            f"CREATE TABLE {ch_name} ON CLUSTER {CLUSTER} (id Int64)",
            exitcode=NOT_IMPLEMENTED,
            message="ON CLUSTER is not supported for DataLakeCatalog",
            ignore_exception=True,
        )
        assert ddl_queue_entries(node, table_name) == queued, error(
            "a DDL task was enqueued"
        )
        with When("snapshot state"):
            after = snapshot_state(**args)
        assert_rejected_no_trace(before=before, after=after, namespace_expected=False)

    with Given("an existing table"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
        )
        before = snapshot_state(**args)

    for label, query in {
        "ALTER TABLE ON CLUSTER": f"ALTER TABLE {ch_name} ON CLUSTER {CLUSTER} ADD COLUMN extra Int32",
        "DROP TABLE ON CLUSTER": f"DROP TABLE {ch_name} ON CLUSTER {CLUSTER}",
    }.items():
        with Check(label, flags=TE):
            queued = ddl_queue_entries(node, table_name)
            node.query(
                query,
                exitcode=NOT_IMPLEMENTED,
                message="ON CLUSTER is not supported for DataLakeCatalog",
                ignore_exception=True,
                inline_settings=[("allow_insert_into_iceberg", 1)],
            )
            assert ddl_queue_entries(node, table_name) == queued, error(
                "a DDL task was enqueued"
            )
            with When("snapshot state"):
                after = snapshot_state(**args)
            assert_state_unchanged(before=before, after=after)

    with Check("RENAME TABLE ON CLUSTER (worker guard)", flags=TE):
        node.query(
            f"RENAME TABLE {ch_name} TO {clickhouse_table_name(database_name, namespace, table_name + '_r')} ON CLUSTER {CLUSTER}",
            exitcode=NOT_IMPLEMENTED,
            message="ON CLUSTER is not supported for DataLakeCatalog",
            ignore_exception=True,
        )
        with When("snapshot state"):
            after = snapshot_state(**args)
        assert_state_unchanged(before=before, after=after)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_OnCluster_WorkerGuard("1.0"))
def worker_guard(self):
    """F2: a task that reaches the DDL queue from a node without the database
    is rejected by the worker that has it; a control query in `default`
    with ON CLUSTER still works."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    nodes = all_nodes(self)
    if len(nodes) < 2:
        skip("needs two nodes")
    node1, node2 = nodes[0], nodes[1]

    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node1,
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with When("node2, which has no such database, issues CREATE ... ON CLUSTER"):
        before = snapshot_state(**args)
        result = node2.query(
            f"CREATE TABLE {ch_name} ON CLUSTER {CLUSTER} (id Int64)", no_checks=True
        )
        assert result.exitcode != 0, error("query succeeded")

    with Then(
        "node1's worker rejected it with NOT_IMPLEMENTED and the catalog has no table"
    ):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                code = node1.query(
                    f"SELECT exception_code FROM system.distributed_ddl_queue "
                    f"WHERE query LIKE '%{table_name}%' AND host = '{node1.name}' LIMIT 1"
                ).output.strip()
                assert code == str(NOT_IMPLEMENTED), error(f"exception_code={code!r}")
        with When("snapshot state"):
            after = snapshot_state(**args)
        assert_rejected_no_trace(before=before, after=after, namespace_expected=False)

    with And("control: ON CLUSTER in default works from node2"):
        control = f"default.ctl_{getuid()}"
        try:
            node2.query(
                f"CREATE TABLE {control} ON CLUSTER {CLUSTER} (id Int64) ENGINE = MergeTree ORDER BY id"
            )
            for node in nodes:
                assert (
                    node.query(f"EXISTS TABLE {control}").output.strip() == "1"
                ), error(node.name)
        finally:
            node2.query(
                f"DROP TABLE IF EXISTS {control} ON CLUSTER {CLUSTER} SYNC",
                no_checks=True,
            )


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_SharedCatalogVisibility("1.0"))
def shared_catalog_visibility(self):
    """A7: a table created on one node is visible, readable, and
    cluster-readable from every node with a database over the same catalog,
    and its drop is visible everywhere."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    nodes = all_nodes(self)
    if len(nodes) < 2:
        skip("needs several nodes")

    with Given("a database on every node over one catalog"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=nodes[0],
        )
        databases = {nodes[0].name: database_name}
        for node in nodes[1:]:
            databases[node.name] = datalake_database(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                node=node,
            )

    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"

    with When("create and insert on the first node"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
            node=nodes[0],
        )
        insert_into_native_iceberg_table(
            table_name=clickhouse_table_name(database_name, namespace, table_name),
            values_sql="(1, 'a')",
            node=nodes[0],
        )

    with Then("every other node lists and reads it"):
        for node in nodes[1:]:
            name = clickhouse_table_name(databases[node.name], namespace, table_name)
            shown = node.query(f"SHOW TABLES FROM {databases[node.name]}").output
            assert f"{namespace}.{table_name}" in shown, error(f"{node.name}: {shown}")
            check_column_value(table_name=name, expected="1\ta", node=node)

    with And("cluster reads work"):
        name = clickhouse_table_name(database_name, namespace, table_name)
        for label, settings in {
            "object_storage_cluster": [("object_storage_cluster", CLUSTER)],
            "parallel replicas": [
                ("parallel_replicas_for_cluster_engines", 1),
                ("cluster_for_parallel_replicas", CLUSTER),
            ],
        }.items():
            with Check(label, flags=TE):
                got = (
                    nodes[0]
                    .query(f"SELECT count() FROM {name}", settings=settings)
                    .output.strip()
                )
                assert got == "1", error(got)

    with When("drop on the first node"):
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            purge=1,
            node=nodes[0],
        )

    with Then("absent everywhere"):
        for node in nodes:
            assert not clickhouse_table_visible(
                databases[node.name], namespace, table_name, node
            ), error(node.name)


@TestFeature
@Name("on cluster")
def feature(self, minio_root_user, minio_root_password):
    """Distributed DDL and shared-catalog visibility."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
