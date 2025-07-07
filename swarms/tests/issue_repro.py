from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType
from pyiceberg.partitioning import PartitionSpec
from pyiceberg.table.sorting import SortOrder

from helpers.common import getuid

from testflows.core import *

import pyarrow as pa
import boto3


@TestStep(Given)
def foo_step(self):
    """Foo step."""
    pass


@TestStep(Given)
def foo_step_with_finally(self, minio_root_user, minio_root_password):
    """Foo step with finally."""
    try:
        catalog = load_catalog(
            "warehouse",
            **{
                "uri": "http://localhost:5000/",
                "type": "rest",
                "s3.endpoint": "http://localhost:9002",
                "s3.access-key-id": minio_root_user,
                "s3.secret-access-key": minio_root_password,
                "token": "foo",
            },
        )
        namespace = "test"
        catalog.create_namespace(namespace)
        schema = Schema(
            NestedField(
                field_id=1, name="name", field_type=StringType(), required=False
            ),
        )
        table_name = f"test_table_{getuid()}"
        table = catalog.create_table(
            f"{namespace}.{table_name}",
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
        )
        df = pa.Table.from_pylist(
            [
                {"name": "Alice"},
                {"name": "Bob"},
            ]
        )
        table.append(df)
        note(f"Added test data to Iceberg table: {table_name}")
        yield

    finally:
        with Finally("finally"):
            s3_client = boto3.client(
                "s3",
                endpoint_url="http://localhost:9002",
                aws_access_key_id=minio_root_user,
                aws_secret_access_key=minio_root_password,
            )
            objects = s3_client.list_objects_v2(Bucket="warehouse")
            note(objects)


@TestScenario
def issue_repro(self, minio_root_user, minio_root_password, node=None):
    """Reproduce issue with timestamp problem."""
    if node is None:
        node = self.context.node

    with Given("foo step with finally"):
        foo_step_with_finally(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Pool() as pool:
        Step("foo step", test=foo_step, parallel=True, executor=pool)()
        Step("foo step", test=foo_step, parallel=True, executor=pool)()
        join()


