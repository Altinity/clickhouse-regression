from testflows.core import *
from testflows.asserts import error

from helpers.tables import *
from helpers.datatypes import *
from helpers.common import getuid

from alter.table.attach_partition.replica.common import get_partition_list

from steps.export import export_partitions_to_s3
from steps.common import generate_database_name
from steps.ice_steps import ice_create_table_from_parquet, ice_insert_data_from_parquet

import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestStep(Given)
def create_merge_tree_table_with_specific_column_datatype(
    self, datatype, table_name=None
):
    """Create merge tree table with specific datatype for both partition and data columns."""
    node = self.context.node
    if table_name is None:
        table_name = f"mt_{datatype.name.lower().replace('(', '_').replace(')', '_').replace(',', '_')}_{getuid()}"

    partition_col = Column(name="year", datatype=UInt16())
    data_col = Column(name="data_col", datatype=datatype)
    columns = [partition_col, data_col]

    try:
        with By(f"creating merge tree table {table_name} with {datatype.name}"):
            table = create_table(
                name=table_name,
                engine="MergeTree()",
                columns=columns,
                partition_by="year",
                order_by="data_col",
                node=node,
            )

        with And("inserting test data"):
            table.insert_test_data(
                row_count=10,
                cardinality=1,
                node=node,
                shuffle_values=True,
            )

        yield table_name

    finally:
        with Finally(f"drop the table {table_name}"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


@TestStep(Given)
def create_s3_table_with_specific_column_datatype(self, datatype, table_name=None):
    """Create S3 table with specific datatype for both partition and data columns."""
    node = self.context.node
    if table_name is None:
        table_name = f"s3_{datatype.name.lower().replace('(', '_').replace(')', '_').replace(',', '_')}_{getuid()}"

    partition_col = Column(name="year", datatype=UInt16())
    data_col = Column(name="data_col", datatype=datatype)
    columns = [partition_col, data_col]

    try:
        with By(f"creating S3 table {table_name} with {datatype.name}"):
            create_table(
                name=table_name,
                engine=f"S3(s3_conn, filename='{table_name}', format=Parquet, partition_strategy='hive')",
                columns=columns,
                order_by="data_col",
                partition_by="year",
                node=node,
            )

        yield table_name

    finally:
        with Finally(f"drop the table {table_name}"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


@TestStep(Given)
def test_datatype_export_pipeline(self, datatype, minio_root_user, minio_root_password):
    """Test `export partitions + ice create + ice insert` pipeline for a specific datatype."""
    ice_node = self.context.ice_node
    node = self.context.node

    with Given(f"create merge tree table with {datatype.name} columns"):
        mt_table_name = create_merge_tree_table_with_specific_column_datatype(
            datatype=datatype
        )

    with And(f"create s3 table with {datatype.name} columns"):
        s3_table_name = create_s3_table_with_specific_column_datatype(datatype=datatype)

    with And("get partition ids for merge tree table"):
        partition_ids = get_partition_list(table_name=mt_table_name, node=node)

    with When("exporting partitions from merge tree to s3"):
        export_partitions_to_s3(
            merge_tree_table_name=mt_table_name,
            s3_table_name=s3_table_name,
            partition_ids=partition_ids,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("creating Iceberg database"):
        database_name = generate_database_name(datatype)
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("creating Iceberg table from Parquet schema"):
        iceberg_table_name = f"iceberg_{datatype.name.lower().replace('(', '_').replace(')', '_').replace(',', '_')}_{getuid()}"
        ice_create_table_from_parquet(
            iceberg_table_name=iceberg_table_name,
            parquet_path=f"s3://warehouse/{s3_table_name}/year=*/*.parquet",
            partition_column="year",
            sort_column="data_col",
            ice_node=ice_node,
        )

    with And("inserting data into Iceberg table"):
        for partition_id in partition_ids:
            ice_insert_data_from_parquet(
                iceberg_table_name=iceberg_table_name,
                parquet_path=f"s3://warehouse/{s3_table_name}/year={partition_id}/*.parquet",
                ice_node=ice_node,
            )

    with Then("verifying data integrity"):
        mt_result = node.query(f"SELECT * FROM {mt_table_name} ORDER BY data_col")
        iceberg_result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace="default",
            table_name=iceberg_table_name,
            object_storage_cluster=None,
            order_by="data_col",
        )
        assert mt_result.output == iceberg_result.output, error()

    with And("checking table schema"):
        node.query(
            f"SHOW CREATE TABLE {database_name}.\\`default.{iceberg_table_name}\\`"
        )


@TestFeature
def test_basic_datatypes_export(self, minio_root_user, minio_root_password):
    """Test `export partitions + ice create + ice insert` pipeline with all basic datatypes."""

    basic_datatypes_list = basic_datatypes()

    for datatype in basic_datatypes_list:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
