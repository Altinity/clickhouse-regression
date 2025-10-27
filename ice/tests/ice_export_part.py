from testflows.core import *
from testflows.asserts import error

from helpers.tables import *
from helpers.datatypes import *
from helpers.common import getuid


from steps.export import *
from steps.common import generate_database_name
from steps.ice_steps import ice_create_table_from_parquet, ice_insert_data_from_parquet

import iceberg.tests.steps.iceberg_engine as iceberg_engine


def get_part_list(table_name, node):
    """Return list of part names for specified table."""
    part_list_query = f"SELECT name FROM system.parts WHERE table='{table_name}' ORDER BY name FORMAT TabSeparated"
    return sorted(list(set(node.query(part_list_query).output.split())))


@TestStep(Given)
def create_merge_tree_table_with_specific_column_datatype(
    self, datatype, table_name=None
):
    """Create merge tree table with specific datatype for both partition and data columns."""
    node = self.context.node
    if table_name is None:
        sanitized_name = (
            datatype.name.lower()
            .replace("(", "_")
            .replace(")", "_")
            .replace(",", "_")
            .replace("'", "")
            .replace("=", "_")
            .replace(" ", "_")
        )
        table_name = f"mt_{sanitized_name}_{getuid()}"

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
                query_settings="allow_nullable_key=1",
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
def create_replicated_merge_tree_table_with_specific_column_datatype(
    self, datatype, table_name=None
):
    """Create merge tree table with specific datatype for both partition and data columns."""
    node = self.context.node
    if table_name is None:
        sanitized_name = (
            datatype.name.lower()
            .replace("(", "_")
            .replace(")", "_")
            .replace(",", "_")
            .replace("'", "")
            .replace("=", "_")
            .replace(" ", "_")
        )
        table_name = f"mt_{sanitized_name}_{getuid()}"

    partition_col = Column(name="year", datatype=UInt16())
    data_col = Column(name="data_col", datatype=datatype)
    columns = [partition_col, data_col]

    try:
        with By(f"creating merge tree table {table_name} with {datatype.name}"):
            table = create_table(
                name=table_name,
                columns=columns,
                engine=f"ReplicatedMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica0')",
                order_by="data_col",
                partition_by="year",
                node=node,
                query_settings="allow_nullable_key=1",
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
        sanitized_name = (
            datatype.name.lower()
            .replace("(", "_")
            .replace(")", "_")
            .replace(",", "_")
            .replace("'", "")
            .replace("=", "_")
            .replace(" ", "_")
        )
        table_name = f"s3_{sanitized_name}_{getuid()}"

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
@Flags(TE)
def test_datatype_export_pipeline(self, datatype, minio_root_user, minio_root_password):
    """Test `export partitions + ice create + ice insert` pipeline for a specific datatype."""
    ice_node = self.context.ice_node
    node = self.context.node

    with Given(f"create replicated merge tree table with {datatype.name} columns"):
        mt_table_name = create_merge_tree_table_with_specific_column_datatype(
            datatype=datatype
        )

    with And(f"create s3 table with {datatype.name} columns"):
        s3_table_name = create_s3_table_with_specific_column_datatype(datatype=datatype)

    with And("get partition ids for merge tree table"):
        part_names = get_part_list(table_name=mt_table_name, node=node)

    with When("exporting partitions from merge tree to s3"):
        export_parts_to_s3(
            merge_tree_table_name=mt_table_name,
            s3_table_name=s3_table_name,
            part_names=part_names,
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
        sanitized_name = (
            datatype.name.lower()
            .replace("(", "_")
            .replace(")", "_")
            .replace(",", "_")
            .replace("'", "")
            .replace("=", "_")
            .replace(" ", "_")
        )
        iceberg_table_name = f"iceberg_{sanitized_name}_{getuid()}"
        ice_create_table_from_parquet(
            iceberg_table_name=iceberg_table_name,
            parquet_path=f"s3://warehouse/{s3_table_name}/year=*/*.parquet",
            partition_column="year",
            sort_column="data_col",
            ice_node=ice_node,
        )

    with And("inserting data into Iceberg table"):
        ice_insert_data_from_parquet(
            iceberg_table_name=iceberg_table_name,
            parquet_path=f"s3://warehouse/{s3_table_name}/year=*/*.parquet",
            ice_node=ice_node,
        )

    with Then("verifying data integrity"):
        mt_result = node.query(f"SELECT * FROM {mt_table_name} ORDER BY year, data_col")

        def get_cast_function(datatype):
            name = datatype.name

            if name.startswith("Array(UInt32"):
                return "CAST(data_col, 'Array(UInt32)')"

            if name.startswith("Decimal"):
                decimal_type = name.split("(")[0]
                scale = name.split("(")[1].split(")")[0]
                return f"to{decimal_type}(data_col, {scale})"

            if name.startswith("DateTime") or name.startswith(
                "LowCardinality(DateTime"
            ):
                return "toDateTime(data_col, 'Europe/Berlin')"

            if name.startswith("Nullable(DateTime"):
                return "toDateTime(data_col, 'Europe/Berlin')"

            if name.startswith("FixedString"):
                length = name.split("(")[1].split(")")[0]
                return f"toFixedString(data_col, {length})"

            if name.startswith("LowCardinality(FixedString"):
                length = name.split("(")[2].split(")")[0]
                return f"toFixedString(data_col, {length})"

            if name.startswith("Enum"):
                return f"CAST(data_col, '{name}')"

            if name.startswith("Nullable("):
                inner_type = name[9:-1]
                return f"to{inner_type.split('(')[0]}(data_col)"

            if name.startswith("LowCardinality("):
                inner_type = name[15:-1]
                return f"to{inner_type.split('(')[0]}(data_col)"

            if (
                name.startswith("Array(")
                or name.startswith("Map(")
                or name.startswith("Tuple(")
            ):
                return "data_col"

            base_type = name.split("(")[0]
            return f"to{base_type}(data_col)"

        cast_expression = get_cast_function(datatype)
        iceberg_result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace="default",
            columns=f"year, {cast_expression}",
            table_name=iceberg_table_name,
            object_storage_cluster=None,
            order_by=f"year, {cast_expression}",
        )
        assert mt_result.output == iceberg_result.output, error()

    with And("checking table schema"):
        node.query(
            f"SHOW CREATE TABLE {database_name}.\\`default.{iceberg_table_name}\\`"
        )


@TestFeature
@Name("export parts")
def test_basic_datatypes_export(self, minio_root_user, minio_root_password):
    """Test `export parts + ice create + ice insert` pipeline with all
    basic datatypes.
    """
    basic_datatypes_list = basic_datatypes()

    for datatype in basic_datatypes_list:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
