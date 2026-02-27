from testflows.core import *
from testflows.asserts import error

from helpers.common import (
    getuid,
)

from pyiceberg.schema import Schema
from pyiceberg.types import (
    LongType,
    NestedField,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder
from pyiceberg.transforms import IdentityTransform

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine


@TestScenario
def write_min_max_pruning(self, minio_root_user, minio_root_password):
    """Test that ClickHouse correctly writes data to Iceberg table with min/max pruning.
    Verifies PR: https://github.com/Altinity/ClickHouse/pull/1192
    """
    namespace = f"iceberg_{getuid()}"
    table_name = f"name_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema and create {namespace}.{table_name} table"):
        schema = Schema(
            NestedField(field_id=1, name="x", field_type=LongType(), required=False),
            NestedField(field_id=2, name="y", field_type=LongType(), required=False),
        )

        partition_spec = PartitionSpec(
            PartitionField(
                source_id=1,
                field_id=1001,
                transform=IdentityTransform(),
                name="x",
            ),
        )

        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=partition_spec,
            sort_order=SortOrder(),
        )

    with And("create table with Iceberg engine"):
        iceberg_table_engine.create_table_with_iceberg_engine(
            table_name=table_name,
            url="http://minio:9000/warehouse/data",
            access_key_id=minio_root_user,
            secret_access_key=minio_root_password,
        )

    with And("write data to table"):
        self.context.node.query(
            f"INSERT INTO {table_name} (x, y) VALUES (1, 1), (1, 2)",
            settings=[("allow_experimental_insert_into_iceberg", 1)],
        )

    with Then("check data in table"):
        result1 = self.context.node.query(
            f"SELECT * FROM {table_name} WHERE y = 1",
        )
        assert result1.output.strip() == "1\t1", error()
        result2 = self.context.node.query(
            f"SELECT * FROM {table_name} WHERE y = 2",
        )
        assert result2.output.strip() == "1\t2", error()