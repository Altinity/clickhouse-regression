from testflows.core import *

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


@TestScenario
def write_min_max_pruning(self, minio_root_user, minio_root_password):
    """Test that ClickHouse correctly writes data to Iceberg table with min/max pruning."""
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
