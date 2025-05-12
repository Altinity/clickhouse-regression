from testflows.core import *
from testflows.asserts import error

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine

from helpers.common import create_user, getuid

import random

random.seed(42)


@TestScenario
def drop_table(self, minio_root_user, minio_root_password, node=None):
    """Check privileges for DROP TABLE."""
    if node is None:
        node = self.context.node

    namespace = "row_policy"
    table_name = f"table_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:5000/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with When(f"define schema and create {namespace}.{table_name} Iceberg table"):
        iceberg_table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("create ClickHouse table with Iceberg engine"):
        iceberg_table_name = "table_with_iceberg_engine_" + getuid()
        iceberg_table_engine.create_table_with_iceberg_engine(
            table_name=iceberg_table_name,
            url="http://minio:9000/warehouse/data",
            access_key_id=minio_root_user,
            secret_access_key=minio_root_password,
        )

    with And("create new user without any privileges"):
        user_name = f"test_user_{getuid()}"
        create_user(name=user_name)

    with Then("attempt to drop table"):
        exitcode, message = 241, f"DB::Exception: {user_name}: Not enough privileges."
        node.query(
            f"DROP TABLE {iceberg_table_name}",
            settings=[("user", user_name)],
            exitcode=exitcode,
            message=message,
        )

    with And("check that table is not dropped"):
        res = node.query(f"SHOW TABLES")
        assert iceberg_table_name in res.output, error()

    with And("grant DROP TABLE privilege to the user"):
        node.query(f"GRANT DROP ON {iceberg_table_name} TO {user_name}")

    with And("attempt to drop table with DROP TABLE privilege"):
        node.query(
            f"DROP TABLE {iceberg_table_name}",
            settings=[("user", user_name)],
        )

    with And("check that table is dropped"):
        res = node.query(f"SHOW TABLES")
        for retry in retries(count=10, delay=1):
            with retry:
                assert res.output == "", error()


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Test RBAC for Iceberg tables."""
    Scenario(test=drop_table)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
