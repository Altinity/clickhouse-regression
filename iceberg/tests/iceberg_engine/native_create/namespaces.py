"""Namespace auto-creation, default location placement, nested and filtered
namespaces (plan §3.5)."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *

COLUMNS = ["id Int64", "name String"]


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Namespace_AutoCreate("1.0"))
def namespace_auto_created(self):
    """An absent namespace is created by the first CREATE TABLE."""
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

    with When("CREATE TABLE in a namespace the catalog has never seen"):
        before = snapshot_state(**args)
        assert not before.catalog_namespace, error()
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
        )

    with Then("the namespace now exists and PyIceberg lists it"):
        after = snapshot_state(**args)
        assert_table_created(before=before, after=after)
        assert (namespace,) in catalog.list_namespaces(), error(catalog.list_namespaces())
        check_state_invariants(**args, expected=PRESENT, state=after)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Namespace_AutoCreate("1.0"))
def existing_namespace_reused(self):
    """A namespace pre-created with custom properties is reused, and its
    properties survive the CREATE."""
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

    with Given("a namespace with a custom property"):
        catalog.create_namespace(namespace, properties={"owner": "regression"})
        props_before = catalog.load_namespace_properties(namespace)

    with When("CREATE TABLE in it"):
        before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
        )

    with Then("table created, properties unchanged"):
        after = snapshot_state(**args)
        assert_table_created(before=before, after=after)
        assert catalog.load_namespace_properties(namespace) == props_before, error(
            f"{props_before} -> {catalog.load_namespace_properties(namespace)}"
        )


@TestScenario
@Requirements(
    RQ_Iceberg_NativeCreateDrop_Namespace_AutoCreate("1.0"),
    RQ_Iceberg_NativeCreateDrop_FailedCreateLeavesNoTrace("1.0"),
)
def rejected_create_leaves_no_namespace(self):
    """A rejected CREATE in a fresh namespace does not create the namespace."""
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
    with When("snapshot state"):
        before = snapshot_state(**args)
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        columns=["id Int64", "d Date"],
        partition_by="toYYYYMM(d)",
        exitcode=BAD_ARGUMENTS,
    )
    with When("snapshot state"):
        after = snapshot_state(**args)
    assert_rejected_no_trace(before=before, after=after, namespace_expected=False)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Namespace_DefaultLocation("1.0"))
def second_table_lands_beside_the_first(self):
    """A4: the namespace location is the namespace base; a second table is
    placed beside the first, never under it."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, t1, t2 = f"ns_{getuid()}", f"t1_{getuid()}", f"t2_{getuid()}"

    with When("create the first table engine-less"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=t1,
            columns=COLUMNS,
        )

    with Then("the namespace location, if reported, is <base>/<namespace>"):
        ns_location = catalog_namespace_location(catalog, namespace)
        if ns_location is None:
            note("catalog reports no namespace location")
        else:
            assert ns_location.rstrip("/") == f"{DEFAULT_BASE_LOCATION}/{namespace}", error(
                ns_location
            )

    with When("create a second table"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=t2,
            columns=COLUMNS,
        )

    with Then("it lives at <base>/<namespace>/<t2>, not under <t1>"):
        _, location = catalog_table_info(catalog, namespace, t2)
        assert location == expected_table_location(namespace, t2), error(location)
        assert f"/{t1}/" not in location, error(location)
        for table_name in (t1, t2):
            check_state_invariants(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                database_name=database_name,
                expected=PRESENT,
            )


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Namespace_DefaultLocation("1.0"))
def explicit_engine_namespace_location(self):
    """An explicit engine whose URL follows <base>/<ns>/<t>/ registers the
    namespace base; one that does not registers no namespace location, and
    a later engine-less table does not nest inside it."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )

    with Check("conventional URL", flags=TE):
        namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=EXPLICIT_ENGINE,
            columns=COLUMNS,
        )
        ns_location = catalog_namespace_location(catalog, namespace)
        if ns_location is None:
            note("catalog reports no namespace location")
        else:
            assert ns_location.rstrip("/") == f"{DEFAULT_BASE_LOCATION}/{namespace}", error(
                ns_location
            )
        check_state_invariants(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            database_name=database_name,
            expected=PRESENT,
        )

    with Check("custom URL", flags=TE):
        namespace, t1, t2 = f"ns_{getuid()}", f"t1_{getuid()}", f"t2_{getuid()}"
        custom = f"custom_{t1}"
        engine = f"IcebergS3('http://minio:9000/warehouse/{custom}/', '{minio_root_user}', '{minio_root_password}')"
        try:
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=t1,
                path=EXPLICIT_ENGINE,
                columns=COLUMNS,
                engine=engine,
            )
            _, location = catalog_table_info(catalog, namespace, t1)
            assert location.rstrip("/") == f"s3://warehouse/{custom}", error(location)
            ns_location = catalog_namespace_location(catalog, namespace)
            assert ns_location is None or not ns_location.rstrip("/").endswith(custom), error(
                ns_location
            )

            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=t2,
                columns=COLUMNS,
            )
            _, location2 = catalog_table_info(catalog, namespace, t2)
            assert custom not in location2, error(
                f"second table nested under the custom table: {location2}"
            )
        finally:
            s3.delete_prefix(f"{custom}/")


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Namespace_Nested("1.0"))
def nested_namespace(self):
    """A dotted namespace is sent as segments: create, insert, alter, select,
    and PyIceberg lists the table under the nested identifier."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    if self.context.catalog == "glue":
        skip("Glue databases are flat")

    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    uid = getuid()
    namespace, table_name = f"a_{uid}.b.c", f"t_{uid}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with When("CREATE TABLE in a.b.c"):
        before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
        )

    with Then("registered under the nested identifier"):
        after = snapshot_state(**args)
        assert_table_created(before=before, after=after)
        tables = catalog.list_tables(tuple(namespace.split(".")))
        assert (*namespace.split("."), table_name) in tables, error(tables)

    with When("INSERT, ALTER ADD COLUMN, SELECT"):
        insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a')")
        self.context.node.query(f"ALTER TABLE {ch_name} ADD COLUMN extra Int32")
        check_column_value(table_name=ch_name, expected="1\ta")

    with Then("invariants hold"):
        check_state_invariants(**args, expected=PRESENT)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Namespace_Filtered("1.0"))
def filtered_namespaces(self):
    """A database restricted with `namespaces` refuses CREATE and DROP
    outside the allowed set and leaves the catalog untouched."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    uid = getuid()
    allowed, other = f"allowed_{uid}", f"other_{uid}"
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            namespaces=allowed,
        )
    table_name = f"t_{uid}"

    with When("CREATE TABLE in a namespace outside the filter"):
        args = dict(
            catalog=catalog,
            namespace=other,
            table_name=table_name,
            database_name=database_name,
        )
        before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=other,
            table_name=table_name,
            columns=COLUMNS,
            exitcode=CATALOG_NAMESPACE_DISABLED,
            message="Namespace",
        )

    with Then("nothing changed"):
        after = snapshot_state(**args)
        assert_rejected_no_trace(before=before, after=after, namespace_expected=False)

    with When("DROP TABLE in a namespace outside the filter"):
        pyiceberg_table(catalog=catalog, namespace=other, table_name=table_name)
        before = snapshot_state(**args)
        drop_table(
            database_name=database_name,
            namespace=other,
            table_name=table_name,
            exitcode=CATALOG_NAMESPACE_DISABLED,
            message="Namespace",
        )

    with Then("the external table is still registered"):
        after = snapshot_state(**args)
        assert_state_unchanged(before=before, after=after)

    with When("CREATE and DROP in the allowed namespace"):
        args = dict(
            catalog=catalog,
            namespace=allowed,
            table_name=table_name,
            database_name=database_name,
        )
        before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=allowed,
            table_name=table_name,
            columns=COLUMNS,
            purge_on_exit=False,
        )
        mid = snapshot_state(**args)
        assert_table_created(before=before, after=mid)
        drop_table(
            database_name=database_name,
            namespace=allowed,
            table_name=table_name,
            purge=1,
        )

    with Then("both worked"):
        after = snapshot_state(**args)
        assert_table_dropped(before=mid, after=after, purged=True)


@TestFeature
@Name("namespaces")
def feature(self, minio_root_user, minio_root_password):
    """Namespace behaviour of native CREATE / DROP."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
