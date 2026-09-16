"""DROP TABLE: keep vs purge, the setting and its alias, every route the
setting can take, IF EXISTS, and the per-catalog refusals (plan §3.9)."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.config import users_d

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *


@TestStep(Given)
def table_with_a_row(self, catalog, database_name, namespace, table_name, node=None):
    """An engine-less table with one committed row; returns the pre-drop
    ``State`` (catalog entry present, metadata plus data objects)."""
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        columns=["id Int64"],
        node=node,
        purge_on_exit=False,
    )
    insert_into_native_iceberg_table(
        table_name=clickhouse_table_name(database_name, namespace, table_name),
        values_sql="(1)",
        node=node,
    )
    with When("snapshot state"):
        state = snapshot_state(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            database_name=database_name,
        )
    assert state.catalog_table, error("table not registered")
    assert any(k.endswith(".parquet") for k in state.objects), error(
        f"no data file after INSERT: {sorted(state.objects)}"
    )
    return state


@TestOutline(Scenario)
@Requirements(
    RQ_Iceberg_NativeCreateDrop_Drop_KeepData("1.0"),
    RQ_Iceberg_NativeCreateDrop_Drop_Purge("1.0"),
    RQ_Iceberg_NativeCreateDrop_Drop_QueryLevelSetting("1.0"),
)
@Examples(
    "purge inline alias",
    [
        (None, False, False),  # server default: keep
        (0, False, False),  # explicit keep via client flag
        (1, False, False),  # purge via client flag
        (1, True, False),  # purge via SET in the session
        (0, True, False),  # keep via SET in the session
        (1, False, True),  # purge via the alias iceberg_delete_data_on_drop
    ],
)
def drop_routes(self, purge, inline, alias):
    """Every way of passing the purge flag to DROP TABLE reaches the drop:
    the catalog entry goes, and the objects go if and only if purge is on."""
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

    with Given("a table with a committed row"):
        before = table_with_a_row(
            catalog=catalog,
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
        )

    with When(f"DROP TABLE purge={purge} inline={inline} alias={alias}"):
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            purge=purge,
            inline=inline,
            alias=alias,
        )

    with Then("B5 / B6"):
        after = snapshot_state(**args)
        purged = bool(purge)
        assert_table_dropped(before=before, after=after, purged=purged)
        check_state_invariants(
            **args,
            expected=ABSENT_PURGED if purged else ABSENT_DATA_KEPT,
            before=before,
            state=after,
        )

    with Finally("clear kept objects"):
        s3.delete_prefix(after.prefix)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Drop_Setting("1.0"))
def setting_and_alias_are_one(self):
    """E1: system.settings shows the alias, the changes history has the new
    name, and both names read the same value."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    node = self.context.node

    with Then("system.settings lists data_lake_delete_data_on_drop with default 0"):
        row = node.query(
            f"SELECT value, alias_for FROM system.settings WHERE name = '{PURGE_SETTING}' FORMAT TSV"
        ).output.strip()
        assert row.split("\t")[0] == "0", error(row)

    with And("the old name is an alias for the new one"):
        alias_for = node.query(
            f"SELECT alias_for FROM system.settings WHERE name = '{PURGE_SETTING_ALIAS}' FORMAT TSV"
        ).output.strip()
        assert alias_for == PURGE_SETTING, error(f"alias_for={alias_for!r}")

    with And("setting one name changes the value read through the other"):
        value = node.query(
            f"SELECT getSetting('{PURGE_SETTING}')",
            inline_settings=[(PURGE_SETTING_ALIAS, 1)],
        ).output.strip()
        assert value == "1", error(value)
        value = node.query(
            f"SELECT getSetting('{PURGE_SETTING_ALIAS}')",
            inline_settings=[(PURGE_SETTING, 1)],
        ).output.strip()
        assert value == "1", error(value)

    with And("system.settings_changes records the new setting"):
        count = node.query(
            f"SELECT count() FROM system.settings_changes "
            f"WHERE arrayExists(x -> tupleElement(x, 1) = '{PURGE_SETTING}', changes)"
        ).output.strip()
        assert count != "0", error("no settings_changes entry")


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_Drop_QueryLevelSetting("1.0"))
@Examples(
    "storage purge",
    [("IcebergS3", 0), ("IcebergS3", 1), ("IcebergLocal", 0), ("IcebergLocal", 1)],
)
def path_based_table_drop(self, storage, purge):
    """B8 outside a catalog: a path-based Iceberg table honours the query-level
    setting through the background drop (``DROP TABLE ... SYNC``)."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    node = self.context.node
    table_name = f"default.pb_{getuid()}"
    key = f"pathbased_{getuid()}"

    if storage == "IcebergS3":
        engine = f"IcebergS3('http://minio:9000/warehouse/{key}/', '{minio_root_user}', '{minio_root_password}')"
        prefix = f"{key}/"
        inventory = lambda: s3.object_inventory(prefix)
    else:
        local_path = f"/var/lib/clickhouse/user_files/{key}/"
        engine = f"IcebergLocal('{local_path}')"
        node.command(f"mkdir -p {local_path}", exitcode=0)
        inventory = lambda: {
            line: None
            for line in node.command(f"find {local_path} -type f 2>/dev/null").output.split()
        }

    try:
        with Given(f"a {storage} table with one row"):
            node.query(
                f"CREATE TABLE {table_name} (id Int64) ENGINE = {engine}",
                settings=[("write_full_path_in_iceberg_metadata", 1)],
            )
            node.query(
                f"INSERT INTO {table_name} VALUES (1)",
                inline_settings=[("allow_insert_into_iceberg", 1)],
            )
            before = inventory()
            assert before, error("no files written")

        with When(f"DROP TABLE SYNC with purge={purge}"):
            drop_table(
                database_name=None,
                namespace=None,
                table_name=None,
                name=table_name,
                purge=purge,
                sync=True,
            )

        with Then("files are gone or unchanged"):
            after = inventory()
            if purge:
                assert after == {}, error(f"files remain: {sorted(after)}")
            else:
                assert after == before, error(
                    f"files changed:\nbefore={sorted(before)}\nafter={sorted(after)}"
                )
    finally:
        with Finally("cleanup"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC", no_checks=True)
            if storage == "IcebergS3":
                s3.delete_prefix(prefix)
            else:
                node.command(f"rm -rf {local_path}", no_checks=True)


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_Drop_QueryLevelSetting("1.0"))
@Examples("query_override expect_purged", [(0, False), (None, True)])
def server_wide_default(self, query_override, expect_purged):
    """B8: with data_lake_delete_data_on_drop = 1 in the default profile, a
    query-level 0 keeps the data and no override deletes it."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    node = self.context.node

    with Given("the default profile enables purge on drop on every node"):
        for n in all_nodes(self):
            users_d.create_and_add(
                entries={"profiles": {"default": {PURGE_SETTING: "1"}}},
                config_file="native_create_purge_default.xml",
                node=n,
                modify=True,
            )

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

    with And("a table with a committed row, read once so its storage is loaded"):
        before = table_with_a_row(
            catalog=catalog,
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
        )
        node.query(
            f"SELECT count() FROM {clickhouse_table_name(database_name, namespace, table_name)}"
        )

    with When(f"DROP TABLE with query-level override {query_override}"):
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            purge=query_override,
        )

    with Then("the query-level value wins; the profile applies only without it"):
        after = snapshot_state(**args)
        assert_table_dropped(before=before, after=after, purged=expect_purged)

    with Finally("clear kept objects"):
        s3.delete_prefix(after.prefix)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Drop_IfExists("1.0"))
def drop_if_exists(self):
    """B7: IF EXISTS on an absent table is a no-op that returns OK; without
    it the server reports UNKNOWN_TABLE; a table an external writer dropped
    a moment ago counts as absent."""
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

    with When("DROP TABLE IF EXISTS on a table that never existed"):
        before = snapshot_state(**args)
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            if_exists=True,
        )

    with Then("OK and nothing changed"):
        after = snapshot_state(**args)
        assert_state_unchanged(before=before, after=after)

    with When("DROP TABLE without IF EXISTS"):
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            exitcode=UNKNOWN_TABLE,
            message="UNKNOWN_TABLE",
        )

    with Given("a table PyIceberg created and then dropped, leaving its files"):
        pyiceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            rows=[{"id": 1, "name": "a"}],
        )
        catalog.drop_table(table_identifier(namespace, table_name))
        before = snapshot_state(**args)
        assert not before.catalog_table and before.objects, error(before.describe())

    with When("DROP TABLE IF EXISTS on it, with purge requested"):
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            if_exists=True,
            purge=1,
        )

    with Then("OK, and the leftover files were not touched"):
        after = snapshot_state(**args)
        assert_state_unchanged(before=before, after=after)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Drop_Glue("1.0"))
def glue_drop(self):
    """G2: Glue keep-drop removes the entry and keeps files; a purge drop is
    refused with NOT_IMPLEMENTED and the table stays; IF EXISTS plus purge
    on a missing table is a no-op."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    if self.context.catalog != "glue":
        skip("Glue-only scenario")

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

    with Given("a table with a committed row"):
        before = table_with_a_row(
            catalog=catalog,
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
        )

    with When("DROP TABLE with purge"):
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            purge=1,
            exitcode=NOT_IMPLEMENTED,
            message="not supported for the Glue catalog",
        )

    with Then("the table is still registered and readable"):
        after = snapshot_state(**args)
        assert_state_unchanged(before=before, after=after)
        check_column_value(table_name=ch_name, expected="1")

    with When("DROP TABLE without purge"):
        drop_table(database_name=database_name, namespace=namespace, table_name=table_name)

    with Then("entry gone, files kept"):
        after = snapshot_state(**args)
        assert_table_dropped(before=before, after=after, purged=False)

    with When("DROP TABLE IF EXISTS with purge on the now-missing table"):
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            if_exists=True,
            purge=1,
        )

    with Then("no-op"):
        final = snapshot_state(**args)
        assert_state_unchanged(before=after, after=final)

    with Finally("clear kept objects"):
        s3.delete_prefix(after.prefix)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Drop_S3Tables("1.0"))
def s3_tables_drop(self):
    """G3: S3 Tables refuses a keep-drop and honours a purge drop."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    skip("no S3 Tables service in iceberg_env; covered by RQ only")


@TestFeature
@Name("drop")
def feature(self, minio_root_user, minio_root_password):
    """DROP TABLE behaviour and the purge setting."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
