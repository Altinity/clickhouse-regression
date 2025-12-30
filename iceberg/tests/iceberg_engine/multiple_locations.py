from testflows.core import *
from testflows.asserts import error

from helpers.common import (
    getuid,
)

import os
import shutil
import subprocess
import time
import uuid
import pyarrow as pa
import pyarrow.parquet as pq
from pyiceberg.io.pyarrow import _pyarrow_to_schema_without_ids

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField,
    LongType,
    StringType,
)


@TestScenario
def local_file_path_issue(self, minio_root_user, minio_root_password):
    """Test that ClickHouse correctly handles Iceberg tables with local file:// paths."""
    namespace = f"test_ns_{getuid()}"
    table_name = f"table1_{getuid()}"
    database_name = f"iceberg_catalog_{getuid()}"
    container_file_path = None
    iceberg_schema = None

    with Given("create REST catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:5000",
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create local parquet file with test data and copy to container"):
        # Get container ID first (this might take time)
        container_id = self.context.cluster.node_container_id(self.context.node.name)

        # Create parquet file in current working directory (more persistent than /tmp)
        parquet_file_path = os.path.join(
            os.getcwd(), f"iceberg_test_data_{getuid()}.parquet"
        )

        # Create test data
        data = pa.Table.from_pylist(
            [
                {"name": "Alice", "double": 195.23, "integer": 20},
                {"name": "Bob", "double": 123.45, "integer": 30},
                {"name": "Charlie", "double": 67.89, "integer": 40},
            ]
        )

        # Write parquet file
        pq.write_table(data, parquet_file_path)
        note(f"Created parquet file at: {parquet_file_path}")

        # Verify file exists and is readable
        if not os.path.exists(parquet_file_path):
            raise FileNotFoundError(f"Parquet file not found: {parquet_file_path}")
        if not os.access(parquet_file_path, os.R_OK):
            raise PermissionError(f"Parquet file not readable: {parquet_file_path}")

        # Read parquet schema before copying (we need it for creating the table)
        parquet_schema = pq.read_table(parquet_file_path).schema
        # Convert to Iceberg schema
        iceberg_schema = _pyarrow_to_schema_without_ids(parquet_schema)
        note(f"Iceberg schema: {iceberg_schema}")

        # Copy file to container's /tmp so ClickHouse can access it
        # Use a path that doesn't match the expected namespace/table pattern
        container_file_path = "/tmp/data.parquet"

        # Verify file still exists before copying
        if not os.path.exists(parquet_file_path):
            raise FileNotFoundError(
                f"Parquet file disappeared before copy: {parquet_file_path}"
            )

        # Copy file to both container and host /tmp
        # Container: so ClickHouse can access it
        # Host: so pyiceberg can read it when add_files() is called
        subprocess.run(
            [
                "docker",
                "cp",
                parquet_file_path,
                f"{container_id}:{container_file_path}",
            ],
            check=True,
        )
        note(f"Copied parquet file to container at: {container_file_path}")

        # Also copy to host /tmp so pyiceberg can read it
        shutil.copy2(parquet_file_path, container_file_path)
        note(f"Copied parquet file to host {container_file_path} for pyiceberg access")

    with And(f"create Iceberg table and add local file"):
        # Create table if not exists (iceberg_schema was read above)
        table = catalog.create_table_if_not_exists(
            f"{namespace}.{table_name}", iceberg_schema
        )

        # Add local file using file:// protocol
        # Use /tmp/data.parquet - this path doesn't match the expected namespace/table pattern
        # Both pyiceberg (on host) and ClickHouse (in container) will look for /tmp/data.parquet
        # We've copied the file to both locations
        file_uri = f"file://{container_file_path}"
        note(f"Adding file with URI: {file_uri}")
        table.add_files([file_uri])

        # Note: We don't verify with table.scan() here because:
        # 1. The file path doesn't match the expected pattern, so ClickHouse will reject it
        # 2. We're testing ClickHouse's validation, not pyiceberg's functionality
        # 3. The file needs to remain in the container for ClickHouse to attempt to read it

        # Clean up host file after pyiceberg add_files() is done
        # Keep the file in the container so ClickHouse can attempt to read it
        try:
            os.remove(container_file_path)
        except Exception:
            pass

        # Clean up original temp file
        try:
            os.remove(parquet_file_path)
        except Exception:
            pass

    with Then("create DataLakeCatalog database in ClickHouse"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("list tables (this should work fine)"):
        result = self.context.node.query(f"SHOW TABLES FROM {database_name}")
        note(f"Tables in database: {result.output}")

    with And(
        "attempt to query the Iceberg table (this should fail with expected error)"
    ):
        # This should fail with Error 1: Expected to find 'test_ns/table1' in data path
        # or Error 2: Failed to get object info if file is under namespace/table_name
        result = self.context.node.query(
            f"SELECT * FROM {database_name}.\\`{namespace}.{table_name}\\`",
        )
        note(f"Query result: {result.output}")
        pause()


@TestScenario
def local_metadata_and_data(self, minio_root_user, minio_root_password):
    """Test that ClickHouse correctly handles Iceberg tables with both metadata and data stored locally."""
    import os

    note(f"Warehouse path: {os.path.abspath('./warehouse')}")
    pause()
    catalog = load_catalog(
        "local_rest",
        type="rest",
        uri="http://localhost:8183",
        warehouse=os.path.abspath("./warehouse"),
    )

    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    identifier = f"{namespace}.{table_name}"

    # Create namespace if it does not exist
    existing_namespaces = [ns[0] for ns in catalog.list_namespaces()]
    if namespace not in existing_namespaces:
        catalog.create_namespace(namespace)

    # Define Iceberg schema
    schema = Schema(
        NestedField(1, "id", LongType(), required=False),
        NestedField(2, "name", StringType(), required=False),
    )

    table_location = os.path.abspath(f"./warehouse/{namespace}/{table_name}")

    if identifier not in [t[1] for t in catalog.list_tables(namespace)]:
        table = catalog.create_table(
            identifier=identifier,
            schema=schema,
            location=f"file:{table_location}",
        )
    else:
        table = catalog.load_table(identifier)

    note(f"Table name: {table.name()}")
    note(f"Location: {table.location}")

    # ----------------------------
    # Append data
    # ----------------------------
    arrow_table = pa.table(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )

    table.append(arrow_table)

    note("Data appended")

    # ----------------------------
    # Scan data
    # ----------------------------
    scan = table.scan()
    result = scan.to_arrow()

    note("Scan result:")
    note(result.to_pandas())
    pause()


@TestFeature
@Name("multiple locations")
def feature(self, minio_root_user, minio_root_password):
    """Test that ClickHouse correctly handles Iceberg tables with files in different locations."""
    # Scenario(test=local_file_path_issue)(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # pause()
    Scenario(test=local_metadata_and_data)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
