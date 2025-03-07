#!/usr/bin/env python3

from testflows.core import *

import random

random.seed(42)

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.common as common

from pyiceberg.types import (
    DoubleType,
    StringType,
    LongType,
    DateType,
    IntegerType,
    FloatType,
    NestedField,
)
from pyiceberg.schema import Schema

from helpers.common import getuid


iceberg_clickhouse_type_mapping = {
    "Nullable(Int32)": IntegerType(),
    "Nullable(Int64)": LongType(),
    "Nullable(Float32)": FloatType(),
    "Nullable(Float64)": DoubleType(),
    "Nullable(String)": StringType(),
    "Nullable(Date)": DateType(),
}


@TestStep(Given)
def add_column(self, merge_tree_table_name, iceberg_table):
    """Add one new column to both MergeTree and Iceberg tables."""
    column_name = f"new_column_{getuid()}"
    column_type = "Nullable(Int64)"
    with By("add column to MergeTree table"):
        self.context.node.query(
            f"ALTER TABLE {merge_tree_table_name} ADD COLUMN {column_name} {column_type}"
        )

    with And("add column to Iceberg table"):
        with iceberg_table.update_schema() as update:
            update.add_column(
                column_name,
                iceberg_clickhouse_type_mapping[column_type],
                required=False,
            )

    with And("update column list"):
        self.context.columns.append({"name": column_name, "type": column_type})


@TestStep(Given)
def delete_column(self, merge_tree_table_name, iceberg_table):
    """Delete one column from both MergeTree and Iceberg tables."""
    if self.context.columns:
        delete_column = random.choice(self.context.columns)
    else:
        return

    with By("delete column from MergeTree table"):
        self.context.node.query(
            f"ALTER TABLE {merge_tree_table_name} DROP COLUMN {delete_column['name']}"
        )

    with And("delete column from Iceberg table"):
        with iceberg_table.update_schema() as update:
            update.delete_column(delete_column["name"])

    with And("update column list"):
        self.context.columns.remove(delete_column)


@TestStep(Given)
def move_column_first(self, merge_tree_table_name, iceberg_table):
    """Move one column to the first position in both MergeTree and Iceberg tables."""
    if self.context.columns:
        move_column = random.choice(self.context.columns)
    else:
        return

    with By("move column to the first position in MergeTree table"):
        self.context.node.query(
            f"ALTER TABLE {merge_tree_table_name} MODIFY COLUMN {move_column['name']} {move_column['type']} FIRST"
        )

    with And("move column to the first position in Iceberg table"):
        with iceberg_table.update_schema() as update:
            update.move_first(move_column["name"])


@TestStep(Given)
def move_column_after(self, merge_tree_table_name, iceberg_table):
    """Move one column after another column in both MergeTree and Iceberg tables."""
    if len(self.context.columns) < 2:
        return

    move_column, after_column = random.sample(self.context.columns, 2)

    with By("move column after another column in MergeTree table"):
        self.context.node.query(
            f"ALTER TABLE {merge_tree_table_name} MODIFY COLUMN {move_column['name']} {move_column['type']} AFTER {after_column['name']}"
        )

    with And("move column after another column in Iceberg table"):
        with iceberg_table.update_schema() as update:
            update.move_after(move_column["name"], after_column["name"])
            note(iceberg_table.schema())


@TestStep(Given)
def update_column_type(self, iceberg_table, merge_tree_table_name):
    """Only valid promotions for Iceberg tables are: int to long, float to double."""
    column_name = None
    new_column_type = None

    with By("search for column to update"):
        random.shuffle(self.context.columns)
        for i in range(len(self.context.columns)):
            if self.context.columns[i]["type"] == "Nullable(Int32)":
                column_name = self.context.columns[i]["name"]
                new_column_type = "Nullable(Int64)"
                self.context.columns[i]["type"] = new_column_type
            elif self.context.columns[i]["type"] == "Nullable(Float32)":
                column_name = self.context.columns[i]["name"]
                new_column_type = "Nullable(Float64)"
                self.context.columns[i]["type"] = new_column_type

        if column_name is None or new_column_type is None:
            return

    with And("update column type in Iceberg table"):
        with iceberg_table.update_schema() as update:
            update.update_column(
                column_name, field_type=iceberg_clickhouse_type_mapping[new_column_type]
            )

    with And("update column type in MergeTree table"):
        self.context.node.query(
            f"ALTER TABLE {merge_tree_table_name} MODIFY COLUMN {column_name} {new_column_type}"
        )


@TestStep(Given)
def rename_column(self, iceberg_table, merge_tree_table_name):
    """Rename one column in both MergeTree and Iceberg tables."""
    if not self.context.columns:
        return
    random.shuffle(self.context.columns)
    old_column_name = self.context.columns[0]["name"]
    new_column_name = f"new_{old_column_name}"
    self.context.columns[0]["name"] = new_column_name

    with By("rename column in MergeTree table"):
        self.context.node.query(
            f"ALTER TABLE {merge_tree_table_name} RENAME COLUMN {old_column_name} TO {new_column_name}"
        )

    with And("rename column in Iceberg table"):
        with iceberg_table.update_schema() as update:
            update.rename_column(old_column_name, new_column_name)


@TestStep(Given)
def union_by_name(self, merge_tree_table_name, iceberg_table):
    """Merge another schema into an existing Iceberg table. For
    MergeTree table analog is ALTER TABLE ... ADD COLUMN ..."""
    column_name = f"new_column_{getuid()}"
    column_type = "Nullable(Int64)"

    with By("add column to MergeTree table"):
        self.context.node.query(
            f"ALTER TABLE {merge_tree_table_name} ADD COLUMN {column_name} {column_type}"
        )

    new_schema = Schema(
        NestedField(1, "city", StringType(), required=False),
        NestedField(2, "lat", DoubleType(), required=False),
        NestedField(3, "long", DoubleType(), required=False),
        NestedField(10, "population", LongType(), required=False),
    )

    with iceberg_table.update_schema() as update:
        update.union_by_name(new_schema)


@TestScenario
def execute_schema_evolution_actions(
    self, minio_root_user, minio_root_password, actions_list
):

    database_name = f"iceberg_database_{getuid()}"
    namespace = f"iceberg_{getuid()}"
    iceberg_table_name = f"table_{getuid()}"
    clickhouse_iceberg_table_name = (
        f"{database_name}.\\`{namespace}.{iceberg_table_name}\\`"
    )

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with When(
        f"create namespace, define schema and create {namespace}.{iceberg_table_name} table"
    ):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
        iceberg_table = catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=iceberg_table_name
        )

    with Then("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create MergeTree table with same structure"):
        merge_tree_table_name = "merge_tree_table_" + getuid()
        common.create_merge_tree_table(table_name=merge_tree_table_name)

    with And("update column list"):
        self.context.columns = [
            # "boolean_col",
            {"name": "long_col", "type": "Nullable(Int64)"},
            {"name": "double_col", "type": "Nullable(Float64)"},
            {"name": "string_col", "type": "Nullable(String)"},
            {"name": "date_col", "type": "Nullable(Date)"},
        ]

    with And("insert same data into both tables"):
        num_rows = 10
        common.insert_same_data_to_iceberg_and_merge_tree_tables(
            iceberg_table=iceberg_table,
            merge_tree_table_name=merge_tree_table_name,
            num_rows=num_rows,
        )

    with Then("run schema evolution actions"):
        for action in actions_list:
            action(
                merge_tree_table_name=merge_tree_table_name,
                iceberg_table=iceberg_table,
            )
            self.context.node.query(f"describe table {merge_tree_table_name}")
            common.compare_data_in_two_tables(
                table_name1=merge_tree_table_name,
                table_name2=clickhouse_iceberg_table_name,
            )
            common.compare_iceberg_and_merge_tree_schemas(
                iceberg_table=iceberg_table, merge_tree_table_name=merge_tree_table_name
            )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    actions = [
        add_column,
        delete_column,
        move_column_first,
        move_column_after,
        update_column_type,
        rename_column,
    ]

    for num in range(100):
        actions_list = [random.choice(actions) for _ in range(10)]
        Scenario(name=f"#{num}", test=execute_schema_evolution_actions)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            actions_list=actions_list,
        )
