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
        mt_table_name = (
            create_replicated_merge_tree_table_with_specific_column_datatype(
                datatype=datatype
            )
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
        for partition_id in partition_ids:
            ice_insert_data_from_parquet(
                iceberg_table_name=iceberg_table_name,
                parquet_path=f"s3://warehouse/{s3_table_name}/year={partition_id}/*.parquet",
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
def test_basic_datatypes_export(self, minio_root_user, minio_root_password):
    """Test `export partitions + ice create + ice insert` pipeline with all
    basic datatypes.
    """
    basic_datatypes_list = basic_datatypes()

    for datatype in basic_datatypes_list:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def test_comprehensive_numeric_datatypes_export(
    self, minio_root_user, minio_root_password
):
    """Test export pipeline with comprehensive numeric datatypes."""
    numeric_datatypes = [
        UInt8(),
        UInt16(),
        UInt32(),
        UInt64(),
        # # UInt128(),
        # # UInt256(),
        Int8(),
        Int16(),
        Int32(),
        Int64(),
        # Int128(),
        # Int256(),
        Float32(),
        Float64(),
        Decimal32(scale=2),
        Decimal32(scale=9),
        Decimal64(scale=2),
        Decimal64(scale=18),
        Decimal128(scale=2),
        Decimal128(scale=38),
        Decimal256(scale=2),
        Decimal256(scale=76),
    ]

    for datatype in numeric_datatypes:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def test_comprehensive_string_datatypes_export(
    self, minio_root_user, minio_root_password
):
    """Test export pipeline with comprehensive string datatypes."""
    string_datatypes = [
        String(),
        FixedString(length=1),  # can not be used in sort by
        FixedString(length=10),
        FixedString(length=50),
        FixedString(length=100),
        FixedString(length=255),
        # UUID(), #problem
    ]

    for datatype in string_datatypes:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def test_comprehensive_datetime_datatypes_export(
    self, minio_root_user, minio_root_password
):
    """Test export pipeline with comprehensive datetime datatypes."""
    datetime_datatypes = [
        Date(),
        Date32(),  # problem
        DateTime(),
        DateTime64(precision=0),
        DateTime64(precision=1),
        DateTime64(precision=2),
        DateTime64(precision=3),
        DateTime64(precision=4),
        DateTime64(precision=5),
        DateTime64(precision=6),
        DateTime64(precision=7),
        DateTime64(precision=8),
        DateTime64(precision=9),
    ]

    for datatype in datetime_datatypes:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def test_nullable_datatypes_export(self, minio_root_user, minio_root_password):
    """Test export pipeline with nullable datatypes."""
    nullable_datatypes = [
        Nullable(UInt32()),
        Nullable(Int64()),
        Nullable(Float64()),
        Nullable(String()),
        Nullable(Date()),
        Nullable(DateTime()),
        Nullable(Boolean()),
        # Nullable(UUID()),
    ]

    for datatype in nullable_datatypes:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def test_low_cardinality_datatypes_export(self, minio_root_user, minio_root_password):
    """Test export pipeline with low cardinality datatypes."""
    low_cardinality_datatypes = [
        LowCardinality(String()),
        LowCardinality(FixedString(length=20)),
        LowCardinality(Date()),
        LowCardinality(DateTime()),
        LowCardinality(UInt32()),
        LowCardinality(Int64()),
        LowCardinality(Float64()),
    ]

    for datatype in low_cardinality_datatypes:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def test_enum_datatypes_export(self, minio_root_user, minio_root_password):
    """Test export pipeline with enum datatypes."""
    enum_datatypes = [
        Enum8([("red", 1), ("green", 2), ("blue", 3)]),
        Enum8([("small", 1), ("medium", 2), ("large", 3), ("xlarge", 4)]),
        Enum16([("january", 1), ("february", 2), ("march", 3), ("april", 4)]),
        Enum16(
            [("low", 1), ("medium", 2), ("high", 3), ("critical", 4), ("urgent", 5)]
        ),
    ]

    for datatype in enum_datatypes:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def test_array_datatypes_export(self, minio_root_user, minio_root_password):
    """Test export pipeline with array datatypes."""
    array_datatypes = [
        Array(UInt32()),
        Array(Int64()),
        Array(Float64()),
        Array(String()),
        Array(Date()),
        Array(DateTime()),
        Array(Boolean()),
        # Array(UUID()),
    ]

    for datatype in array_datatypes:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def test_map_datatypes_export(self, minio_root_user, minio_root_password):
    """Test export pipeline with map datatypes."""
    map_datatypes = [
        # Map(key=String(), value=UInt32()),
        Map(key=String(), value=Int64()),
        Map(key=String(), value=Float64()),
        Map(key=String(), value=String()),
        # Map(key=String(), value=Date()),
        # Map(key=String(), value=DateTime()),
        Map(key=String(), value=Boolean()),
        # Map(key=UInt32(), value=String()),
        Map(key=Int64(), value=Float64()),
    ]

    for datatype in map_datatypes:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
def test_tuple_datatypes_export(self, minio_root_user, minio_root_password):
    """Test export pipeline with tuple datatypes."""
    tuple_datatypes = [
        # Tuple([String(), UInt32()]),
        Tuple([String(), Int32()]),
        Tuple([Int64(), Float64()]),
        Tuple([Date(), DateTime(), String()]),
        Tuple([Boolean(), UUID(), Int32()]),
        Tuple([String(), Array(UInt32())]),
        Tuple([Map(key=String(), value=Int64()), Date()]),
    ]

    for datatype in tuple_datatypes:
        Scenario(name=f"testing {datatype.name}", test=test_datatype_export_pipeline)(
            datatype=datatype,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
