"""What happens to a natively created table afterwards (plan §3.11)."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *

COLUMNS = ["id Int64", "name String", "d Date"]


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_Lifecycle_InsertAlterSelect("1.0"))
@Examples("path", [(ENGINE_LESS,), (EXPLICIT_ENGINE,)])
def insert_alter_select(self, path):
    """C4: the table takes INSERT, schema ALTERs, partition-pruned SELECT,
    ALTER DELETE and TRUNCATE; the catalog's metadata-location advances after
    each mutation and PyIceberg observes the result."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    node = self.context.node
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with Given("a partitioned table"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=path,
            columns=COLUMNS,
            partition_by="toRelativeDayNum(d)",
            engine_settings=({"iceberg_format_version": 2} if path == EXPLICIT_ENGINE else None),
        )

    def metadata_location():
        return catalog_table_info(catalog, namespace, table_name)[0]

    steps = [
        (
            "INSERT",
            f"INSERT INTO {ch_name} VALUES (1, 'a', '2024-01-01'), (2, 'b', '2024-01-02')",
        ),
        ("ADD COLUMN", f"ALTER TABLE {ch_name} ADD COLUMN extra Int32"),
        ("RENAME COLUMN", f"ALTER TABLE {ch_name} RENAME COLUMN extra TO renamed"),
        ("MODIFY COLUMN", f"ALTER TABLE {ch_name} MODIFY COLUMN renamed Int64"),
        ("DROP COLUMN", f"ALTER TABLE {ch_name} DROP COLUMN renamed"),
        ("ALTER DELETE", f"ALTER TABLE {ch_name} DELETE WHERE id = 2"),
    ]
    for label, query in steps:
        with Check(label, flags=TE):
            previous = metadata_location()
            node.query(
                query,
                inline_settings=[
                    ("allow_insert_into_iceberg", 1),
                    ("allow_experimental_iceberg_compaction", 0),
                ],
            )
            assert metadata_location() != previous, error("metadata-location did not advance")

    with Check("SELECT with a partition predicate", flags=TE):
        got = node.query(f"SELECT id FROM {ch_name} WHERE d = '2024-01-01'").output.strip()
        assert got == "1", error(got)

    with Check("PyIceberg sees the final schema and rows", flags=TE):
        table = catalog.load_table(f"{namespace}.{table_name}")
        assert [f.name for f in table.schema().fields] == ["id", "name", "d"], error(
            pyiceberg_schema_shape(table)
        )
        rows = table.scan().to_arrow().to_pylist()
        assert [r["id"] for r in rows] == [1], error(rows)

    with Check("TRUNCATE", flags=TE):
        previous = metadata_location()
        node.query(
            f"TRUNCATE TABLE {ch_name}",
            inline_settings=[("allow_insert_into_iceberg", 1)],
        )
        assert metadata_location() != previous, error("metadata-location did not advance")
        assert node.query(f"SELECT count() FROM {ch_name}").output.strip() == "0", error()

    with Then("invariants hold"):
        check_state_invariants(**args, expected=PRESENT)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Lifecycle_Recreate("1.0"))
def recreate_after_purge_drop(self):
    """B9: after a purge-drop the same name can be created again and is empty."""
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

    with Given("a table with a row, purge-dropped"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
            purge_on_exit=False,
        )
        insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a', '2024-01-01')")
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            purge=1,
        )

    for path in (ENGINE_LESS, EXPLICIT_ENGINE):
        with When(f"recreate via {path}"):
            before = snapshot_state(**args)
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                path=path,
                columns=COLUMNS,
                purge_on_exit=False,
            )

        with Then("B1: fresh and empty"):
            after = snapshot_state(**args)
            assert_table_created(before=before, after=after)
            check_state_invariants(**args, expected=PRESENT, state=after)

        with And("purge-drop again"):
            drop_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                purge=1,
            )


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Lifecycle_Recreate("1.0"))
def recreate_after_keep_drop(self):
    """B9: after a keep-drop the explicit-engine recreate is refused; under a
    database with another base the same name succeeds and the old files are
    untouched."""
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

    with Given("a table with a row, keep-dropped"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
            purge_on_exit=False,
        )
        insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a', '2024-01-01')")
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            purge=0,
        )
        leftover = snapshot_state(**args)

    with When("recreate at the same location with an explicit engine"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=EXPLICIT_ENGINE,
            columns=COLUMNS,
            exitcode=TABLE_ALREADY_EXISTS,
            message=PURGE_SETTING,
            purge_on_exit=False,
        )
        assert_state_unchanged(before=leftover, after=snapshot_state(**args))

    with And("recreate under a database with a different base"):
        base = f"s3://warehouse/alt_{getuid()}"
        other_db = datalake_database(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            default_base_location=base,
        )
        reported = getattr(catalog, "properties", {}).get("default-base-location")
        if reported:
            skip("catalog advertises its own base; a database-level base cannot move the table")
        try:
            create_table(
                database_name=other_db,
                namespace=namespace,
                table_name=table_name,
                columns=COLUMNS,
                purge_on_exit=False,
            )
            state = snapshot_state(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                database_name=other_db,
                base_location=base,
            )
            check_state_invariants(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                database_name=other_db,
                base_location=base,
                expected=PRESENT,
                state=state,
            )
        finally:
            drop_table(
                database_name=other_db,
                namespace=namespace,
                table_name=table_name,
                purge=1,
                if_exists=True,
            )

    with Then("the old files are untouched"):
        assert s3.object_inventory(leftover.prefix) == leftover.objects, error()

    with Finally("clear leftovers"):
        s3.delete_prefix(leftover.prefix)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Lifecycle_ExportPartitionDestination("1.0"))
def export_partition_destination(self):
    """An engine-less table as EXPORT PARTITION destination."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    skip(
        "deferred: reuse s3/tests/export_partition steps once the Antalya build under test is fixed"
    )


@TestFeature
@Name("lifecycle")
def feature(self, minio_root_user, minio_root_password):
    """Life of a natively created table."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
