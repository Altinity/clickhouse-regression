#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from helpers.common import create_user, getuid


@TestScenario
@Name("named collections config")
def sanity_named_collections_in_config(self, minio_root_user, minio_root_password):
    """Test basic creating table with Iceberg table engine
    using named collection defined in config.xml."""
    node = self.context.node
    namespace = "iceberg"
    table_name = "name"

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

    with When(f"create {namespace}.{table_name} table with three columns"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And(f"insert data into {namespace}.{table_name} table"):
        df = pa.Table.from_pylist(
            [
                {"name": "Alice", "double": 195.23, "integer": 20},
                {"name": "Bob", "double": 123.45, "integer": 30},
                {"name": "Charlie", "double": 67.89, "integer": 40},
            ]
        )
        table.append(df)

    with Then(
        "create table with Iceberg engine with named collection iceberg_conf defined in config.xml"
    ):
        table_name = iceberg_engine.create_table_with_iceberg_engine_from_config(
            config_name="iceberg_conf"
        )

    with And("select data from table"):
        result = node.query(f"SELECT * FROM {table_name} FORMAT TabSeparated")
        assert "Alice	195.23	20" in result.output, error()
        assert "Bob	123.45	30" in result.output, error()
        assert "Charlie	67.89	40" in result.output, error()


@TestScenario
@Name("named collections")
def sanity_named_collections(self, minio_root_user, minio_root_password):
    """Test basic creating table with Iceberg table engine
    using named collections."""
    node = self.context.node
    namespace = "iceberg"
    table_name = "name"

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

    with When(f"create {namespace}.{table_name} table with three columns"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And(f"insert data into {namespace}.{table_name} table"):
        df = pa.Table.from_pylist(
            [
                {"name": "Alice", "double": 195.23, "integer": 20},
                {"name": "Bob", "double": 123.45, "integer": 30},
                {"name": "Charlie", "double": 67.89, "integer": 40},
            ]
        )
        table.append(df)

    with And("create named collection"):
        named_collection = "named_collection_" + getuid()
        iceberg_engine.create_named_collection(
            name=named_collection,
            dict={
                "url": "http://minio:9000/warehouse/",
                "access_key_id": minio_root_user,
                "secret_access_key": minio_root_password,
            },
        )

    with Then(
        "create table with Iceberg engine with named collection iceberg_conf defined in config.xml"
    ):
        table_name = iceberg_engine.create_table_with_iceberg_engine_from_config(
            config_name=named_collection
        )

    with And("select data from table"):
        result = node.query(f"SELECT * FROM {table_name} FORMAT TabSeparated")
        assert "Alice	195.23	20" in result.output, error()
        assert "Bob	123.45	30" in result.output, error()
        assert "Charlie	67.89	40" in result.output, error()


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=sanity_named_collections_in_config)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=sanity_named_collections)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
