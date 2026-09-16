"""Where a new table is placed: base-location precedence, derivation from
storage_endpoint, URI style, and backend consistency (plan §3.4)."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *

COLUMNS = ["id Int64", "name String"]


def catalog_reported_base(catalog):
    """The `default-base-location` the REST catalog advertises in its config,
    or None. Decides whether a database-level base is honoured (E2)."""
    return getattr(catalog, "properties", {}).get("default-base-location")


@TestOutline(Scenario)
@Requirements(
    RQ_Iceberg_NativeCreateDrop_Location_DefaultBaseLocation("1.0"),
    RQ_Iceberg_NativeCreateDrop_Location_Resolution("1.0"),
)
@Examples("base", [("s3://warehouse/custom",), ("s3://warehouse/custom/",)])
def default_base_location(self, base):
    """E2 / A5: with `default_base_location` on the database the table lands
    at <base>/<ns>/<t> unless the catalog advertises its own base, which then
    wins."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            default_base_location=base,
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)
    reported = catalog_reported_base(catalog)
    effective = reported or base
    note(f"catalog reports base={reported!r}; effective base={effective!r}")
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
        base_location=effective,
    )

    with Then("SHOW CREATE DATABASE shows the setting"):
        shown = self.context.node.query(f"SHOW CREATE DATABASE {database_name}").output
        assert "default_base_location" in shown, error(shown)

    with When("CREATE TABLE and INSERT"):
        before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
        )
        insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a')")

    with Then("location, metadata/ and data/ are under the effective base"):
        after = snapshot_state(**args)
        expected = expected_table_location(namespace, table_name, effective)
        assert after.table_location == expected, error(f"{after.table_location} != {expected}")
        prefix = s3.prefix_from_uri(expected)
        assert any(k.startswith(prefix + "metadata/") for k in after.objects), error(
            sorted(after.objects)
        )
        assert any(k.startswith(prefix + "data/") for k in after.objects), error(
            sorted(after.objects)
        )
        check_state_invariants(**args, expected=PRESENT, state=after)


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_Location_DerivedFromStorageEndpoint("1.0"))
@Examples(
    "storage_endpoint base",
    [
        ("http://minio:9000/warehouse", "s3://warehouse"),
        ("http://minio:9000/warehouse/prefix", "s3://warehouse/prefix"),
    ],
)
def derived_from_storage_endpoint(
    self, minio_root_user, minio_root_password, storage_endpoint, base
):
    """A5 on a catalog with no base: the bucket path of storage_endpoint is
    the base."""
    if self.context.catalog != "glue":
        skip("derivation is observable only on a catalog that reports no base (Glue)")

    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            storage_endpoint=storage_endpoint,
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
        base_location=base,
    )
    with When("snapshot state"):
        before = snapshot_state(**args)
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        columns=COLUMNS,
    )
    with When("snapshot state"):
        after = snapshot_state(**args)
    assert_table_created(before=before, after=after)
    check_state_invariants(**args, expected=PRESENT, state=after)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Location_DerivedFromStorageEndpoint("1.0"))
def storage_endpoint_without_bucket(self):
    """storage_endpoint with no bucket path cannot derive a location."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    if self.context.catalog != "glue":
        skip("Glue only")
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            storage_endpoint="http://minio:9000/",
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )
    with When("snapshot state"):
        before = snapshot_state(**args)
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        columns=COLUMNS,
        exitcode=BAD_ARGUMENTS,
        message="does not contain a bucket",
    )
    assert_rejected_no_trace(before=before, after=snapshot_state(**args), namespace_expected=False)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Location_Resolution("1.0"))
def no_base_and_no_endpoint(self):
    """E2: on a catalog that advertises no base, a database without
    `default_base_location` cannot create a table: with `storage_endpoint`
    alone a REST catalog refuses to guess the scheme, and with neither
    setting the error names both. Nothing is written either way."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("a database with storage_endpoint but no base"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            default_base_location=None,
        )
    if catalog_reported_base(catalog):
        skip("catalog advertises default-base-location; the database needs no setting")

    with Check("storage_endpoint only", flags=TE):
        namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
        args = dict(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            database_name=database_name,
        )
        with When("snapshot state"):
            before = snapshot_state(**args)
        if self.context.catalog == "glue":
            note(
                "Glue derives the location from storage_endpoint; see derived_from_storage_endpoint"
            )
        else:
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                columns=COLUMNS,
                exitcode=BAD_ARGUMENTS,
                message="Cannot determine storage scheme for CREATE TABLE",
            )
            with Then("no trace"):
                after = snapshot_state(**args)
                assert_rejected_no_trace(before=before, after=after, namespace_expected=False)

    with Check("neither setting", flags=TE):
        with Given("a database with neither setting"):
            bare_database = datalake_database(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                default_base_location=None,
                storage_endpoint=None,
            )
        namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
        args = dict(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            database_name=bare_database,
        )
        with When("snapshot state"):
            before = snapshot_state(**args)
        create_table(
            database_name=bare_database,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
            exitcode=BAD_ARGUMENTS,
            message="requires `default_base_location` or `storage_endpoint`",
        )
        with Then("no trace"):
            after = snapshot_state(**args)
            assert_rejected_no_trace(before=before, after=after, namespace_expected=False)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Location_VirtualHostedStyle("1.0"))
def virtual_hosted_requires_base(self):
    """E3: virtual-hosted URI style cannot derive the bucket; with a base the
    table is registered at the expected location."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Check("without base", flags=TE):
        with By("catalog and database"):
            catalog, database_name = catalog_and_database(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                storage_uri_style="virtual_hosted",
                default_base_location=None,
            )
        namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
        args = dict(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            database_name=database_name,
        )
        if catalog_reported_base(catalog):
            note("catalog advertises a base, so derivation is not attempted; expecting success")
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                columns=COLUMNS,
            )
            assert catalog_has_table(catalog, namespace, table_name), error()
        else:
            with By("snapshot state"):
                before = snapshot_state(**args)
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                columns=COLUMNS,
                exitcode=BAD_ARGUMENTS,
                message="default_base_location",
            )
            assert_rejected_no_trace(
                before=before, after=snapshot_state(**args), namespace_expected=False
            )

    with Check("with base", flags=TE):
        base = "s3://warehouse/vh"
        with By("catalog and database"):
            catalog, database_name = catalog_and_database(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                storage_uri_style="virtual_hosted",
                default_base_location=base,
            )
        effective = catalog_reported_base(catalog) or base
        namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
        )
        _, location = catalog_table_info(catalog, namespace, table_name)
        assert location == expected_table_location(namespace, table_name, effective), error(
            location
        )


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Location_BackendConsistency("1.0"))
def base_on_a_different_backend(self):
    """A6: a base on another backend than the catalog's fixed one is refused
    with no trace."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    if self.context.catalog != "glue":
        skip("needs a fixed-backend catalog (Glue)")
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            default_base_location="abfss://c@h.dfs.core.windows.net/x",
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )
    with When("snapshot state"):
        before = snapshot_state(**args)
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        columns=COLUMNS,
        exitcode=BAD_ARGUMENTS,
        message="stores tables on",
    )
    assert_rejected_no_trace(before=before, after=snapshot_state(**args), namespace_expected=False)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Location_Azure("1.0"))
def azure_location(self):
    """abfss location derivation."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    skip("no Azure service in iceberg_env; covered by the unit test in the PR")


@TestFeature
@Name("location")
def feature(self, minio_root_user, minio_root_password):
    """Table location resolution."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
