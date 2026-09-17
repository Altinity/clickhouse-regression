"""Access control on native CREATE / DROP (plan §3.12, invariants H)."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid, create_user

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *

COLUMNS = ["id Int64", "name String"]


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_RBAC("1.0"))
def create_requires_grant(self):
    """H1: without CREATE TABLE on the database the statement is
    ACCESS_DENIED and registers nothing; with the grant it works."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    node = self.context.node
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    with Given("user"):
        user = create_user()
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with When("CREATE TABLE as a user with no grants"):
        before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
            settings=[("user", user)],
            exitcode=ACCESS_DENIED,
            message="ACCESS_DENIED",
        )

    with Then("nothing registered"):
        assert_rejected_no_trace(
            before=before, after=snapshot_state(**args), namespace_expected=False
        )

    with When("GRANT CREATE TABLE and retry"):
        node.query(f"GRANT CREATE TABLE ON {database_name}.* TO {user}")
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
            settings=[("user", user)],
        )

    with Then("created"):
        after = snapshot_state(**args)
        assert_table_created(before=before, after=after)
        check_state_invariants(**args, expected=PRESENT, state=after)

    with And("H2: no credential in the registered metadata or SHOW CREATE TABLE"):
        metadata, location = read_registered_metadata(
            catalog=catalog, namespace=namespace, table_name=table_name
        )
        blob = (
            str(metadata)
            + node.query(
                f"SHOW CREATE TABLE {clickhouse_table_name(database_name, namespace, table_name)}"
            ).output
        )
        assert minio_root_password not in blob, error("secret leaked")


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_RBAC("1.0"))
def drop_requires_grant(self):
    """H1: without DROP TABLE on the database the statement is ACCESS_DENIED
    and the table stays; with the grant it works."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    node = self.context.node
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    with Given("user"):
        user = create_user()
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with Given("a table"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
        )
        before = snapshot_state(**args)

    with When("DROP TABLE as a user with no grants"):
        node.query(
            f"DROP TABLE {clickhouse_table_name(database_name, namespace, table_name)}",
            settings=[("user", user)],
            exitcode=ACCESS_DENIED,
            message="ACCESS_DENIED",
            ignore_exception=True,
        )

    with Then("the table stays"):
        assert_state_unchanged(before=before, after=snapshot_state(**args))

    with When("GRANT DROP TABLE and retry with purge"):
        node.query(f"GRANT DROP TABLE ON {database_name}.* TO {user}")
        node.query(
            f"DROP TABLE {clickhouse_table_name(database_name, namespace, table_name)}",
            settings=[("user", user), (PURGE_SETTING, 1)],
        )

    with Then("dropped and purged"):
        assert_table_dropped(before=before, after=snapshot_state(**args), purged=True)


@TestFeature
@Name("rbac")
def feature(self, minio_root_user, minio_root_password):
    """Grants for native CREATE / DROP."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
