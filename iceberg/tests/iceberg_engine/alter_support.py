from testflows.core import *

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from helpers.common import getuid
import pyarrow as pa

import time
import random


@TestStep(Given)
def rename_column(self, table_name, column_name, new_column_name, if_exists=True):
    """Rename column in the existing table using alter."""
    with By("executing alter rename column command on the table"):
        if if_exists:
            if_exists = "IF EXISTS "
        else:
            if_exists = ""
        query = f"SET allow_insert_into_iceberg = 1;ALTER TABLE {table_name} RENAME COLUMN {if_exists} {column_name} TO {new_column_name}"
        self.context.node.query(query)


@TestStep(Given)
def add_column(self, table_name, column_name, column_type, if_not_exists=True):
    """Add column to the existing table using alter."""
    with By("executing alter add column command on the table"):
        if if_not_exists:
            if_not_exists = "IF NOT EXISTS "
        else:
            if_not_exists = ""
        query = f"SET allow_insert_into_iceberg = 1; ALTER TABLE {table_name} ADD COLUMN {if_not_exists} {column_name} {column_type}"
        self.context.node.query(query)


@TestStep(Given)
def drop_column(self, table_name, column_name, if_exists=True):
    """Drop column from the existing table using alter."""
    with By("executing alter drop column command on the table"):
        if if_exists:
            if_exists = "IF EXISTS "
        else:
            if_exists = ""
        query = f"SET allow_insert_into_iceberg = 1; ALTER TABLE {table_name} DROP COLUMN {if_exists} {column_name}"
        self.context.node.query(query)


@TestStep(Given)
def modify_column_datatype(
    self, table_name, column_name, new_column_type, if_exists=True
):
    """Modify column datatype in the existing table using alter."""
    if if_exists:
        if_exists = "IF EXISTS "
    else:
        if_exists = ""
    with By("executing alter modify column datatype command on the table"):
        query = f"SET allow_insert_into_iceberg = 1; ALTER TABLE {table_name} MODIFY COLUMN {if_exists} {column_name} {new_column_type}"
        self.context.node.query(query)


@TestStep(Given)
def run_alter_actions(self, table_name):
    """Run all alter actions on the table."""
    actions = [
        add_column(
            table_name=table_name, column_name="name", column_type="Nullable(String)"
        ),
        add_column(
            table_name=table_name, column_name="age", column_type="Nullable(UInt64)"
        ),
        add_column(
            table_name=table_name, column_name="email", column_type="Nullable(String)"
        ),
        add_column(
            table_name=table_name, column_name="double", column_type="Nullable(Float64)"
        ),
        add_column(
            table_name=table_name, column_name="integer", column_type="Nullable(UInt64)"
        ),
        drop_column(table_name=table_name, column_name="name"),
        drop_column(table_name=table_name, column_name="age"),
        drop_column(table_name=table_name, column_name="email"),
        drop_column(table_name=table_name, column_name="double"),
        drop_column(table_name=table_name, column_name="integer"),
        rename_column(
            table_name=table_name, column_name="name", new_column_name="first_name"
        ),
        rename_column(
            table_name=table_name, column_name="first_name", new_column_name="name"
        ),
        rename_column(
            table_name=table_name, column_name="age", new_column_name="age_in_years"
        ),
        rename_column(
            table_name=table_name, column_name="age_in_years", new_column_name="age"
        ),
        rename_column(
            table_name=table_name, column_name="email", new_column_name="email_address"
        ),
        rename_column(
            table_name=table_name, column_name="email_address", new_column_name="email"
        ),
        rename_column(
            table_name=table_name, column_name="double", new_column_name="double_value"
        ),
        rename_column(
            table_name=table_name, column_name="double_value", new_column_name="double"
        ),
        rename_column(
            table_name=table_name,
            column_name="integer",
            new_column_name="integer_value",
        ),
        rename_column(
            table_name=table_name,
            column_name="integer_value",
            new_column_name="integer",
        ),
    ]
    time_start = time.time()
    while time.time() - time_start < 100:
        action = random.choice(actions)
        with When(f"executing {action.__name__} on the table"):
            action()


@TestScenario
def alter_column(self, minio_root_user, minio_root_password):
    """Check that ALTER TABLE ADD COLUMN, DROP COLUMN, RENAME COLUMN are
    not supported for Iceberg tables."""

    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"

    with Given("create iceberg catalog and table"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with Then("create database with Iceberg engine"):
        database_name = f"iceberg_database_{getuid()}"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
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

    with Pool(4) as pool:
        for _ in range(4):
            Step(test=run_alter_actions, parallel=True, executor=pool)(
                table_name=f"{database_name}.\\`{namespace}.{table_name}\\`"
            )
        join()


@TestFeature
@Name("alter support")
def feature(self, minio_root_user, minio_root_password):
    """Check that ALTER TABLE operations are supported for tables from Iceberg database."""
    Scenario(test=alter_column)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
