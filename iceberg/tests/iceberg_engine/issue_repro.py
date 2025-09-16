#!/usr/bin/env python3

from testflows.core import *

import pyarrow as pa

from helpers.common import getuid

from pyiceberg.schema import Schema
from pyiceberg.types import (
    StringType,
    LongType,
    NestedField,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder
from pyiceberg.transforms import IdentityTransform


from pyiceberg.catalog import load_catalog


@TestScenario
def hive_issue(self, minio_root_user, minio_root_password):
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"

    with Given("create catalog"):
        conf = {
            "uri": "http://localhost:5000/",
            "type": "rest",
            "s3.endpoint": "http://localhost:9002",
            "s3.access-key-id": minio_root_user,
            "s3.secret-access-key": minio_root_password,
            "token": "foo",
        }

        catalog = load_catalog(
            "test_catalog",
            **conf,
        )

    with And("create namespace"):
        catalog.create_namespace(namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        schema = Schema(
            NestedField(
                field_id=1, name="name", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=2,
                name="int",
                field_type=LongType(),
                required=False,
            ),
        )
        partition_spec = PartitionSpec(
            PartitionField(
                source_id=1,
                field_id=1001,
                transform=IdentityTransform(),
                name="symbol_partition",
            ),
        )

        table = catalog.create_table(
            identifier=f"{namespace}.{table_name}",
            schema=schema,
            location="s3://warehouse/data",
            sort_order=SortOrder(),
            partition_spec=partition_spec,
        )

    with Then("insert data into table"):
        data = [
            {"name": "Alice", "int": 1},
            {"name": "Bob", "int": 2},
            {"name": "Charlie", "int": 3},
        ]
        df = pa.Table.from_pylist(data)
        table.append(df)

    pause()


@TestFeature
@Name("issue repro")
def feature(self, minio_root_user, minio_root_password):
    """Test issue reproductions."""
    Scenario(test=hive_issue)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
