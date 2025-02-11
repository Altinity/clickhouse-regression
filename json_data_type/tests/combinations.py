from testflows.core import *
from testflows.combinatorics import *

import json_data_type.tests.steps.steps as steps
from json_data_type.tests.steps.generate_json import random_json

from helpers.common import getuid


@TestScenario
def combination(self, max_dynamic_path, max_dynamic_type, max_depth, max_length):

    with Given("create json column definition"):
        json_col = steps.JsonColumn(
            "json_col",
            max_dynamic_paths=max_dynamic_path,
            max_dynamic_types=max_dynamic_type,
        )

    with And("generate json object"):
        json_obj, type_map = random_json(max_depth=max_depth, max_length=max_length)

    with And("create table with one column of JSON type"):
        table_name = f"json_table_{getuid()}"
        steps.create_table_with_json_column(
            table_name=table_name,
            column_description=json_col.generate_column_definition(),
        )

    with Then("insert JSON object into the table"):
        steps.insert_json_to_table(table_name=table_name, json_object=json_obj)
        self.context.node.query(f"SELECT * FROM {table_name}")


@TestScenario
def combinations(self):
    """Test different combinations of creating JSON columns and inserting JSON objects."""
    max_dynamic_paths_options = [0, 1, 2, 100, 1000, 10000]
    max_dynamic_types_options = [0, 1, 2, 100, 254]
    max_depth_options = [1, 2, 5, 7]
    max_length_options = [1, 2, 10, 20]

    for max_dynamic_path, max_dynamic_type, max_depth, max_length in product(
        max_dynamic_paths_options,
        max_dynamic_types_options,
        max_depth_options,
        max_length_options,
    ):
        Scenario(test=combination)(
            max_dynamic_path=max_dynamic_path,
            max_dynamic_type=max_dynamic_type,
            max_depth=max_depth,
            max_length=max_length,
        )


@TestFeature
def feature(self):
    Scenario(run=combinations)
