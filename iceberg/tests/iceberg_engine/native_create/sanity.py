"""Happy paths for the three creation forms and both drop modes (plan §3.1).

Every scenario brackets the statement under test with ``snapshot_state`` and
ends with ``check_state_invariants`` so the catalog, object storage and every
ClickHouse node are judged the same way (see ``invariants.md``).
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_CreateTable("1.0"))
def engine_less_create(self):
    """Engine-less CREATE TABLE registers an empty table that ClickHouse lists,
    PyIceberg loads, and that accepts INSERT then SELECT."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
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

    with When("snapshot before"):
        before = snapshot_state(**args)

    with And("CREATE TABLE without ENGINE"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=ENGINE_LESS,
            columns=["id Int64", "name String", "value Float64"],
            partition_by="id",
            order_by="name",
        )

    with Then("B1: exactly one table, one metadata file, empty everywhere"):
        after = snapshot_state(**args)
        assert_table_created(before=before, after=after)

    with And("ClickHouse lists it in SHOW TABLES and system.tables"):
        shown = self.context.node.query(f"SHOW TABLES FROM {database_name}").output
        assert f"{namespace}.{table_name}" in shown, error(shown)
        # DataLakeCatalog databases are hidden from system.tables unless
        # show_data_lake_catalogs_in_system_tables is on (SHOW TABLES enables it
        # internally); the catalog is queried for every table when they are shown.
        engine = self.context.node.query(
            f"SELECT engine FROM system.tables WHERE database = '{database_name}' "
            f"AND name = '{namespace}.{table_name}'",
            settings=[("show_data_lake_catalogs_in_system_tables", 1)],
        ).output.strip()
        assert engine.startswith("Iceberg"), error(f"engine={engine!r}")

    with And("PyIceberg loads it with the declared schema and no snapshots"):
        table = catalog.load_table(f"{namespace}.{table_name}")
        assert pyiceberg_schema_shape(table) == [
            ("id", "long", True),
            ("name", "string", True),
            ("value", "double", True),
        ], error(pyiceberg_schema_shape(table))
        assert table.current_snapshot() is None, error("new table has a snapshot")

    with When("INSERT a row"):
        insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a', 1.5)")

    with Then("SELECT returns it on every node"):
        for node in nodes_with_database(database_name, self):
            check_column_value(table_name=ch_name, expected="1\ta\t1.5", node=node)

    with And("A: state invariants hold"):
        check_state_invariants(**args, expected=PRESENT)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_CreateTable_ExplicitEngine("1.0"))
def explicit_engine_create(self):
    """CREATE TABLE ... ENGINE = IcebergS3(...) inside the catalog database
    yields the same table shape as the engine-less form."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    columns = ["id Int64", "name Nullable(String)", "d Date"]
    shapes = {}

    for path in (ENGINE_LESS, EXPLICIT_ENGINE):
        namespace = f"ns_{getuid()}"  # own namespace per table: a CREATE into an existing namespace costs ~33 s (findings.md #3)
        table_name = f"t_{path}_{getuid()}"
        args = dict(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            database_name=database_name,
        )

        with When(f"snapshot before {path}"):
            before = snapshot_state(**args)

        with And(f"CREATE TABLE via {path}"):
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                path=path,
                columns=columns,
                partition_by="toRelativeDayNum(d)",
                order_by="id",
            )

        with Then(f"B1 and A hold for {path}"):
            after = snapshot_state(**args)
            assert_table_created(before=before, after=after)
            check_state_invariants(**args, expected=PRESENT, state=after)

        with And(f"record what PyIceberg sees for {path}"):
            table = catalog.load_table(f"{namespace}.{table_name}")
            shapes[path] = (
                pyiceberg_schema_shape(table),
                [(f.source_id, str(f.transform)) for f in table.spec().fields],
                [
                    (f.source_id, str(f.transform), str(f.direction))
                    for f in table.sort_order().fields
                ],
            )

        with And(f"INSERT and SELECT work for {path}"):
            ch_name = clickhouse_table_name(database_name, namespace, table_name)
            insert_into_native_iceberg_table(
                table_name=ch_name, values_sql="(7, 'x', '2024-01-02')"
            )
            check_column_value(table_name=ch_name, expected="7\tx\t2024-01-02")

    with Then("C1/C2: both paths registered an identical schema, spec and sort order"):
        assert shapes[ENGINE_LESS] == shapes[EXPLICIT_ENGINE], error(
            f"engine_less={shapes[ENGINE_LESS]}\nexplicit_engine={shapes[EXPLICIT_ENGINE]}"
        )


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_CreateTable_AsSource("1.0"))
def create_as_source_copies_keys(self):
    """CREATE TABLE ... AS a MergeTree source copies columns, an
    Iceberg-expressible PARTITION BY, and ORDER BY; INSERT ... SELECT then
    moves the data."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
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

    with Given(
        "a MergeTree source with a day partition key and a two-column sorting key"
    ):
        source = mergetree_source_table(
            columns=["a Int64", "b String", "d Date"],
            partition_by="toRelativeDayNum(d)",
            order_by="(a, b)",
            rows="(1, 'x', '2024-01-01'), (2, 'y', '2024-01-02'), (3, 'z', '2024-01-02')",
        )

    with When("snapshot before"):
        before = snapshot_state(**args)

    with And("CREATE TABLE ... AS source"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=AS_SOURCE,
            source=source,
        )

    with Then("B1 and A hold"):
        after = snapshot_state(**args)
        assert_table_created(before=before, after=after)
        check_state_invariants(**args, expected=PRESENT, state=after)

    with And("PyIceberg shows the copied columns, day transform and sort order"):
        table = catalog.load_table(f"{namespace}.{table_name}")
        assert [f.name for f in table.schema().fields] == ["a", "b", "d"], error()
        assert [(f.source_id, str(f.transform)) for f in table.spec().fields] == [
            (3, "day")
        ], error(str(table.spec()))
        assert [f.source_id for f in table.sort_order().fields] == [1, 2], error(
            str(table.sort_order())
        )

    with When("INSERT ... SELECT from the source"):
        self.context.node.query(
            f"INSERT INTO {ch_name} SELECT * FROM {source}",
            inline_settings=[("allow_insert_into_iceberg", 1)],
        )

    with Then("row counts match"):
        got = self.context.node.query(f"SELECT count() FROM {ch_name}").output.strip()
        assert got == "3", error(got)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_CreateTable_AsSource("1.0"))
def create_as_source_explicit_keys_win(self):
    """Explicit PARTITION BY / ORDER BY on the AS statement take precedence
    over the source's keys."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with Given("a source partitioned by day and ordered by a"):
        source = mergetree_source_table(
            columns=["a Int64", "b String", "d Date"],
            partition_by="toRelativeDayNum(d)",
            order_by="a",
        )

    with When("CREATE TABLE ... AS source with its own keys"):
        before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=AS_SOURCE,
            source=source,
            partition_by="icebergBucket(4, a)",
            order_by="b",
        )

    with Then("the explicit keys are the ones registered"):
        after = snapshot_state(**args)
        assert_table_created(before=before, after=after)
        table = catalog.load_table(f"{namespace}.{table_name}")
        assert [(f.source_id, str(f.transform)) for f in table.spec().fields] == [
            (1, "bucket[4]")
        ], error(str(table.spec()))
        assert [f.source_id for f in table.sort_order().fields] == [2], error(
            str(table.sort_order())
        )
        check_state_invariants(**args, expected=PRESENT, state=after)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_CreateTable_AsSource("1.0"))
def create_as_source_with_unrepresentable_keys(self):
    """A source whose PARTITION BY uses a function Iceberg cannot express
    (toYYYYMM) is rejected with BAD_ARGUMENTS and leaves no trace.

    Note: plan §3.1 #5 expected silent creation without keys; the server
    copies the source key unconditionally and ``getPartitionField`` rejects
    it, so rejection is the behaviour under test.
    """
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with Given("a source partitioned by toYYYYMM"):
        source = mergetree_source_table(
            columns=["a Int64", "d Date"], partition_by="toYYYYMM(d)", order_by="a"
        )

    with When("CREATE TABLE ... AS source"):
        before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=AS_SOURCE,
            source=source,
            exitcode=BAD_ARGUMENTS,
            message="Unsupported function for iceberg partitioning",
        )

    with Then("B2: nothing changed"):
        after = snapshot_state(**args)
        assert_state_unchanged(before=before, after=after)
        check_state_invariants(**args, expected=ABSENT_PURGED, state=after)


@TestScenario
@Requirements(
    RQ_Iceberg_NativeCreateDrop_Drop("1.0"),
    RQ_Iceberg_NativeCreateDrop_Drop_KeepData("1.0"),
)
def drop_keeps_data_by_default(self):
    """DROP TABLE without the setting removes the catalog entry and leaves
    every object in place."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
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

    with Given("a table with one committed row"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=["id Int64"],
        )
        insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1)")

    with When("snapshot, then DROP TABLE"):
        before = snapshot_state(**args)
        assert before.catalog_table and len(before.objects) > 1, error(
            before.describe()
        )
        drop_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )

    with Then("B5: entry gone, objects untouched"):
        after = snapshot_state(**args)
        assert_table_dropped(before=before, after=after, purged=False)
        assert not catalog_has_table(catalog, namespace, table_name), error()
        check_state_invariants(
            **args, expected=ABSENT_DATA_KEPT, before=before, state=after
        )

    with Finally("clean the kept objects so the bucket is left as found"):
        s3.delete_prefix(after.prefix)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Drop_Purge("1.0"))
def drop_with_purge(self):
    """DROP TABLE with data_lake_delete_data_on_drop = 1 removes the entry
    and every object under the table location."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
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

    with Given("a table with one committed row"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=["id Int64"],
        )
        insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1)")

    with When("snapshot, then DROP TABLE with purge"):
        before = snapshot_state(**args)
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            purge=1,
        )

    with Then("B6: entry gone, location empty"):
        after = snapshot_state(**args)
        assert_table_dropped(before=before, after=after, purged=True)
        check_state_invariants(**args, expected=ABSENT_PURGED, state=after)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Drop("1.0"))
def drop_table_never_loaded(self):
    """A table created by PyIceberg is dropped through a fresh database that
    never read it: the drop goes to the catalog, not to a cached storage."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with Given("a namespace and a table created by PyIceberg"):
        pyiceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            rows=[{"id": 1, "name": "a"}],
        )

    with When("DROP TABLE as the first statement touching it"):
        before = snapshot_state(**args)
        assert before.catalog_table, error("PyIceberg table not registered")
        drop_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )

    with Then("B5: unregistered, objects kept"):
        after = snapshot_state(**args)
        assert_table_dropped(before=before, after=after, purged=False)
        check_state_invariants(
            **args, expected=ABSENT_DATA_KEPT, before=before, state=after
        )

    with Finally("clean the kept objects"):
        s3.delete_prefix(after.prefix)


@TestFeature
@Name("sanity")
def feature(self, minio_root_user, minio_root_password):
    """Happy paths for all three creation forms and both drop modes."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
