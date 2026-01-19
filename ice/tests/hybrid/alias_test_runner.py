import os
import json

from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.tables import *


def load_test_cases(json_file_path):
    """Load test cases from JSON file."""
    with open(json_file_path, "r") as f:
        data = json.load(f)
    return data.get("test_cases", [])


def datatype_from_string(datatype_str):
    """Convert datatype string to Column datatype object."""
    datatype_map = {
        "Int32": Int32,
        "Int64": Int64,
        "UInt8": UInt8,
        "UInt16": UInt16,
        "UInt32": UInt32,
        "Date": Date,
        "String": String,
        "Float32": Float32,
        "Float64": Float64,
    }
    datatype_class = datatype_map.get(datatype_str)
    if datatype_class is None:
        raise ValueError(f"Unknown datatype: {datatype_str}")
    return datatype_class()


def create_columns_from_config(base_columns, alias_columns):
    """Create Column objects from JSON configuration for left and right tables."""
    columns = []

    for col in base_columns:
        columns.append(Column(name=col["name"], datatype=datatype_from_string(col["datatype"])))

    for col in alias_columns:
        columns.append(Column(name=col["name"], alias=col["expression"]))

    return columns


def create_hybrid_columns_from_config(base_columns, alias_columns):
    """Create Column objects for hybrid table definition."""
    columns = []

    for col in base_columns:
        columns.append(Column(name=col["name"], datatype=datatype_from_string(col["datatype"])))

    for col in alias_columns:
        if "hybrid_type" not in col:
            raise ValueError(f"hybrid_type is required for alias column '{col['name']}'")
        columns.append(Column(name=col["name"], datatype=datatype_from_string(col["hybrid_type"])))

    return columns


@TestScenario
def run_test_case(self, test_case, node=None):
    """Run a single test case from JSON configuration."""
    if node is None:
        node = self.context.node

    with Given("create left table and populate it with test data"):
        left_table_name = f"left_{getuid()}"
        right_table_name = f"right_{getuid()}"

        segment_columns = create_columns_from_config(test_case["base_columns"], test_case["alias_columns"])

        create_table_params = {
            "name": left_table_name,
            "engine": "MergeTree",
            "columns": segment_columns,
        }
        if "order_by" in test_case:
            create_table_params["order_by"] = test_case["order_by"]
        if "partition_by" in test_case:
            create_table_params["partition_by"] = test_case["partition_by"]

        left_table = create_table(**create_table_params)

        left_table.insert_test_data(cardinality=1, shuffle_values=False)

    with And("create right table and populate it with test data"):
        create_table_params = {
            "name": right_table_name,
            "engine": "MergeTree",
            "columns": segment_columns,
        }
        if "order_by" in test_case:
            create_table_params["order_by"] = test_case["order_by"]
        if "partition_by" in test_case:
            create_table_params["partition_by"] = test_case["partition_by"]

        right_table = create_table(**create_table_params)

        right_table.insert_test_data(cardinality=1, shuffle_values=False)

    with And("create hybrid table"):
        hybrid_table_name = f"hybrid_{getuid()}"
        hybrid_columns = create_hybrid_columns_from_config(test_case["base_columns"], test_case["alias_columns"])

        left_table_func = f"remote('localhost', currentDatabase(), '{left_table_name}')"
        left_predicate = test_case["watermark"]["left_predicate"]
        right_table_func = f"remote('localhost', currentDatabase(), '{right_table_name}')"
        right_predicate = test_case["watermark"]["right_predicate"]
        hybrid_engine = f"Hybrid({left_table_func}, {left_predicate}, {right_table_func}, {right_predicate})"

        create_table(
            name=hybrid_table_name,
            engine=hybrid_engine,
            columns=hybrid_columns,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    if test_case.get("test_query"):
        with And("create reference MergeTree table with same structure and data"):
            merge_tree_reference_table = f"reference_merge_tree_{getuid()}"

            reference_columns = create_columns_from_config(test_case["base_columns"], test_case["alias_columns"])

            create_table_params = {
                "name": merge_tree_reference_table,
                "engine": "MergeTree",
                "columns": reference_columns,
            }
            if "order_by" in test_case:
                create_table_params["order_by"] = test_case["order_by"]
            if "partition_by" in test_case:
                create_table_params["partition_by"] = test_case["partition_by"]

            create_table(**create_table_params)

        with And("populate reference table from left and right segment tables using watermark predicates"):
            node.query(
                f"INSERT INTO {merge_tree_reference_table} SELECT * FROM {left_table_name} WHERE {left_predicate}"
            )
            node.query(
                f"INSERT INTO {merge_tree_reference_table} SELECT * FROM {right_table_name} WHERE {right_predicate}"
            )

        with Then("compare hybrid table results with MergeTree reference table"):
            test_query = test_case["test_query"].format(hybrid_table=hybrid_table_name)
            reference_query = test_case["test_query"].format(hybrid_table=merge_tree_reference_table)

            hybrid_result = node.query(test_query).output
            reference_result = node.query(reference_query).output

            assert hybrid_result == reference_result, error()


@TestFeature
@Name("alias combinatorics from json")
def feature(self, minio_root_user, minio_root_password):
    """
    Test suite for ALIAS columns in hybrid tables.

    Loads test cases from a JSON file and runs them.
    Each test case defines:
    - Column structure (base columns and alias columns)
    - Watermark predicates
    - Expected exit code and error message
    - Test queries for comparison

    Results are verified by comparing query results from hybrid tables with
    MergeTree reference tables that have the same ALIAS columns and data.
    """

    json_file_path = os.path.join(os.path.dirname(__file__), "alias_test_cases.json")

    test_cases = load_test_cases(json_file_path)

    note(f"Loaded {len(test_cases)} test cases from {json_file_path}")

    for test_case in test_cases:
        name = test_case["name"]
        Scenario(name=name, test=run_test_case)(test_case=test_case)
