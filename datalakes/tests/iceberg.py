from testflows.core import *
from testflows.asserts import error
from clickhouse_driver import Client
import boto3
from pyiceberg.catalog import load_catalog
from pyiceberg.table import Table
from pyiceberg.schema import Schema
from pyiceberg.types import IntegerType, StringType


# Test scenario to create an Iceberg table and integrate it with ClickHouse
@TestScenario
def create_and_register_iceberg_table(self):
    # Connection parameters for ClickHouse
    clickhouse_host = "localhost"
    clickhouse_port = 9000
    clickhouse_user = "default"
    clickhouse_password = ""
    clickhouse_database = "default"

    # Iceberg table details
    iceberg_catalog_name = "my_s3_catalog"
    iceberg_table_name = "example_iceberg_table"
    clickhouse_table_name = "example_clickhouse_table"
    bucket_name = "your-bucket"
    storage_path = f"s3://{bucket_name}/path/to/iceberg/table/"
    s3_access_key = "your-access-key"
    s3_secret_key = "your-secret-key"

    # Schema definition for Iceberg table
    schema = Schema(
        IntegerType().field("id"),
        StringType().field("name"),
        IntegerType().field("age"),
    )

    # Create an S3 client for Iceberg table creation
    s3_client = boto3.client(
        "s3", aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key
    )

    # Load or create an Iceberg catalog
    catalog = load_catalog(
        name=iceberg_catalog_name,
        conf={"type": "hive", "uri": storage_path, "s3.client": s3_client},
    )

    # Establish a connection to ClickHouse
    client = Client(
        host=clickhouse_host,
        port=clickhouse_port,
        user=clickhouse_user,
        password=clickhouse_password,
        database=clickhouse_database,
    )

    try:
        # Create an Iceberg table in the catalog
        if not catalog.table_exists(iceberg_table_name):
            catalog.create_table(
                identifier=iceberg_table_name, schema=schema, location=storage_path
            )
            print(f"Iceberg table '{iceberg_table_name}' created successfully.")

        # Register the Iceberg table with ClickHouse
        iceberg_create_sql = f"""
        CREATE TABLE {clickhouse_table_name} (
            id Int32,
            name String,
            age Int32
        ) ENGINE = Iceberg
        PARTITION BY id
        SETTINGS
            storage_path = '{storage_path}',
            s3_access_key_id = '{s3_access_key}',
            s3_secret_access_key = '{s3_secret_key}'
        """

        client.execute(iceberg_create_sql)
        print(
            f"ClickHouse table '{clickhouse_table_name}' created successfully from Iceberg table."
        )
    except Exception as e:
        with Then("An error occurred while creating and registering the Iceberg table"):
            error(str(e))
    finally:
        # Clean up: Drop the Iceberg table if it exists
        client.execute(f"DROP TABLE IF EXISTS {clickhouse_table_name}")
        print("ClickHouse table cleaned up.")


@TestFeature
def feature(self, servers=None, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
