from testflows.core import *
from testflows.asserts import error

from helpers.common import create_user, getuid, check_clickhouse_version

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestScenario
def select_privilege(self, minio_root_user, minio_root_password):
    """Test basic RBAC with tables from Iceberg engine."""
    node = self.context.node
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog and Iceberg table with data"):
        table_name, namespace = (
            catalog_steps.create_catalog_and_iceberg_table_with_data(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("read data in clickhouse from the previously created table"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name
        )
        assert "true	1000	456.78	Alice	2024-01-01" in result.output, error()
        assert "true	3000	6.7	Charlie	2022-01-01" in result.output, error()
        assert "false	2000	456.78	Bob	2023-05-15" in result.output, error()
        assert "false	4000	8.9	1	2021-01-01" in result.output, error()

    with Then("create new user"):
        user_name = f"test_user_{getuid()}"
        create_user(name=user_name)

    with And("try to read from iceberg table with new user"):
        exitcode, message = 241, f"DB::Exception: {user_name}: Not enough privileges."
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            user=user_name,
            exitcode=exitcode,
            message=message,
        )

    with And("grant SELECT privilege on table from Iceberg engine"):
        node.query(
            f"GRANT SELECT ON {database_name}.\\`{namespace}.{table_name}\\` TO {user_name}"
        )

    with And("try to read from iceberg table with new user"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            user=user_name,
        )
        assert "true	1000	456.78	Alice	2024-01-01" in result.output, error()
        assert "true	3000	6.7	Charlie	2022-01-01" in result.output, error()
        assert "false	2000	456.78	Bob	2023-05-15" in result.output, error()
        assert "false	4000	8.9	1	2021-01-01" in result.output, error()


@TestScenario
def drop_table_privilege(self, minio_root_user, minio_root_password):
    """Check that it is not possible to drop tables from Iceberg engine."""
    node = self.context.node
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog and Iceberg table with data"):
        table_name, namespace = (
            catalog_steps.create_catalog_and_iceberg_table_with_data(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
        )
        clickhouse_iceberg_table_name = (
            f"{database_name}.\\`{namespace}.{table_name}\\`"
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create new user"):
        user_name = f"test_user_{getuid()}"
        create_user(name=user_name)

    if check_clickhouse_version("<25.8")(self):
        with Then("attempt to drop table"):
            exitcode, message = (
                241,
                f"DB::Exception: {user_name}: Not enough privileges.",
            )
            node.query(
                f"DROP TABLE {clickhouse_iceberg_table_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )

        with And("grant DROP TABLE privilege to the user"):
            node.query(f"GRANT DROP ON {clickhouse_iceberg_table_name} TO {user_name}")

        with And("check that it is not possible to drop iceberg table"):
            database_engine_name = (
                "DatabaseIceberg"
                if check_clickhouse_version("<25.3")(self)
                else "DatabaseDataLakeCatalog"
            )
            exitcode = 48
            message = f"DB::Exception: There is no DROP TABLE query for {database_engine_name}."
            node.query(
                f"DROP TABLE {clickhouse_iceberg_table_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )

        with And("check that table is still there"):
            res = node.query(f"SHOW TABLES FROM {database_name}")
            assert f"{namespace}.{table_name}" in res.output, error()
            result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
            )
            assert "true	1000	456.78	Alice	2024-01-01" in result.output, error()
            assert "true	3000	6.7	Charlie	2022-01-01" in result.output, error()
            assert "false	2000	456.78	Bob	2023-05-15" in result.output, error()
            assert "false	4000	8.9	1	2021-01-01" in result.output, error()
    else:
        with Then("attempt to drop table"):
            exitcode, message = (
                241,
                f"DB::Exception: {user_name}: Not enough privileges.",
            )
            node.query(
                f"DROP TABLE {clickhouse_iceberg_table_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )

        with And("grant DROP TABLE privilege to the user"):
            node.query(f"GRANT DROP ON {clickhouse_iceberg_table_name} TO {user_name}")

        with And("check that it is not possible to drop iceberg table"):
            node.query(
                f"DROP TABLE {clickhouse_iceberg_table_name}",
                settings=[("user", user_name)],
            )

        with And("check that table is dropped"):
            res = node.query(f"SHOW TABLES FROM {database_name}")
            assert f"{namespace}.{table_name}" not in res.output, error()

        with And("check that select fails"):
            result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                exitcode=60,
                message=f"DB::Exception: Unknown table expression identifier '{database_name}.{namespace}.{table_name}'",
            )


@TestScenario
def drop_database_privilege(self, minio_root_user, minio_root_password):
    """Check that it is not possible to drop database from Iceberg engine."""
    node = self.context.node
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog and Iceberg table with data"):
        catalog_steps.create_catalog_and_iceberg_table_with_data(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And(f"create new user"):
        user_name = f"test_user_{getuid()}"
        create_user(name=user_name)

    with Then(f"attempt to drop database as {user_name}"):
        exitcode, message = 241, f"DB::Exception: {user_name}: Not enough privileges."
        node.query(
            f"DROP DATABASE {database_name}",
            settings=[("user", user_name)],
            exitcode=exitcode,
            message=message,
        )

    with And(f"grant DROP DATABASE privilege to the user {user_name}"):
        node.query(f"GRANT DROP DATABASE ON {database_name}.* TO {user_name}")

    with And(f"drop database as {user_name}"):
        node.query(
            f"DROP DATABASE {database_name}",
            settings=[("user", user_name)],
        )

    with And("check that database is dropped"):
        res = node.query(f"SHOW DATABASES")
        assert f"{database_name}" not in res.output, error()


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Check simple RBAC for tables from Iceberg engine."""
    Scenario(test=select_privilege)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=drop_table_privilege)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=drop_database_privilege)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
