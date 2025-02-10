#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from helpers.common import create_user, getuid

from pyiceberg.schema import Schema
from pyiceberg.types import (
    DoubleType,
    StringType,
    NestedField,
    LongType,
)


@TestScenario
@Name("changing schema")
def sanity(self, minio_root_user, minio_root_password):

    node = self.context.node
    namespace = "iceberg"
    table_name = "name"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
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
        table_name = iceberg_engine.create_table_with_iceberg_engine(
            config_name="iceberg_conf",
            allow_dynamic_metadata_for_data_lakes=True,
        )

    with And("select data from table"):
        result = node.query(f"SELECT * FROM {table_name} FORMAT TabSeparated")
        assert "Alice	195.23	20" in result.output, error()
        assert "Bob	123.45	30" in result.output, error()
        assert "Charlie	67.89	40" in result.output, error()

    with And("change schema"):
        with table.update_schema() as update:
            update.add_column("some_field", LongType(), "doc")

    with And("insert data into table"):
        df = pa.Table.from_pylist(
            [
                {"name": "Masha", "double": 212.3, "integer": 24, "some_field": 1},
            ]
        )
        table.append(df)

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

    with And("select data from table"):
        result = node.query(f"SELECT * FROM {table_name} FORMAT TabSeparated")
        pause()

    with And("change schema again"):
        new_schema = Schema(
            NestedField(
                field_id=1, name="name", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=2, name="double", field_type=DoubleType(), required=False
            ),
            NestedField(
                field_id=3, name="integer", field_type=LongType(), required=False
            ),
            NestedField(10, "population", LongType(), required=False),
        )

        with table.update_schema() as update:
            update.union_by_name(new_schema)

    with And("select data from table"):
        result = node.query(f"SELECT * FROM {table_name} FORMAT TabSeparated")


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=sanity)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
