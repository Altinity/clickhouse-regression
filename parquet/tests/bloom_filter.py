import os
import json

from parquet.requirements import *
from parquet.tests.outline import import_export
from parquet.tests.steps import *
from helpers.common import *


def rows_read(json_data):
    """Get the number of rows read from the json data."""

    return int(json.loads(json_data)["statistics"]["rows_read"])


@TestStep(Given)
def total_number_of_rows(self, file_name, node=None):
    """Get the total number of rows in the parquet file."""

    if node is None:
        node = self.context.node

    with By(f"getting the total number of rows in the parquet file {file_name}"):
        r = f"SELECT COUNT(*) FROM file('{file_name}', Parquet)"
        data = node.query(r)

    return int(data.output.strip())


@TestScenario
def read_and_write_file_with_bloom(self):
    """Read all files from a bloom directory that contains parquet files with bloom filters."""
    files = [
        "binary_bloom.gz.parquet",
        "timestamp_bloom.gz.parquet",
        "double_bloom.gz.parquet",
        "integer_bloom.gz.parquet",
        "decimal_bloom.gz.parquet",
        "struct_bloom.gz.parquet",
        "long_bloom.gz.parquet",
        "date_bloom.gz.parquet",
        "boolean_bloom.gz.parquet",
        "map_bloom.gz.parquet",
        "multi_column_bloom.gz.parquet",
        "array_bloom.gz.parquet",
        "float_bloom.gz.parquet",
    ]

    for file in files:
        with Given(f"I import and export the parquet file {file}"):
            import_export(
                snapshot_name=f"{file}_structure",
                import_file=os.path.join("bloom", file),
            )


@TestCheck
def check_parquet_with_bloom(
    self, file_name, statement, condition, bloom_filter, filter_pushdown, native_reader
):
    """Check if the bloom filter is being used by ClickHouse."""

    with Given("I get the total number of rows in the parquet file"):
        initial_rows = total_number_of_rows(
            file_name="bloom/multi_column_bloom.gz.parquet"
        )

    with And(
        "I read from the parquet file",
        description=f"Bloom Filter: {bloom_filter}, Filter Pushdown: {filter_pushdown}",
    ):
        with By("selecting and saving the data from a parquet file without bloom filter enabled"):
            data_without_bloom = select_from_parquet(
                file_name=file_name,
                statement=statement,
                condition=condition,
                format="Json",
                settings=f"input_format_parquet_use_native_reader={native_reader}",
                order_by="tuple(*)",
            )

        with And(f"selecting and saving the data from a parquet file with bloom filter {bloom_filter} and filter pushdown {filter_pushdown}"):
            data = select_from_parquet(
                file_name=file_name,
                statement=statement,
                condition=condition,
                format="Json",
                settings=f"input_format_parquet_bloom_filter_push_down={bloom_filter},input_format_parquet_filter_push_down={filter_pushdown},use_cache_for_count_from_files=false, input_format_parquet_use_native_reader={native_reader}",
                order_by="tuple(*)",

            )

    with Then("I check that the number of rows read is correct"):
        read_rows = rows_read(data.output.strip())
        if bloom_filter == "true":
            with By(
                "Checking that the number of rows read is lower then the total number of rows of a file"
            ):
                assert read_rows < initial_rows, error()
        else:
            with By(
                "Checking that the number of rows read is equal to the total number of rows of a file"
            ):
                assert read_rows == initial_rows, error()

    with And("I check that the data is the same when reading with bloom filter and without"):
        assert data.output.strip() == data_without_bloom.output.strip(), error()


@TestSketch(Scenario)
def read_bloom_filter_parquet_files(self):
    """Read all files from a bloom directory that contains parquet files with bloom filters."""

    file_name = "bloom/multi_column_bloom.gz.parquet"
    statements = [
        "*",
        "f32",
        "f64",
        "int",
        "str",
        "fixed_str",
        "array",
        "f32,f64,int,str,fixed_str,array",
    ]
    filter = ["true", "false"]
    native_reader = "false"
    conditions = [
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC'",
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC' OR str='KCGEY'",
        "WHERE f32=toFloat32(-15.910733) AND fixed_str IN ('BYYC', 'DCXV') ORDER BY f32 ASC",
        "WHERE f64 IN (toFloat64(22.89182051713945), toFloat64(68.62704389505595)) ORDER BY f32",
        "WHERE has(array, 69778) ORDER BY f32 ASC",
        "WHERE hasAll(array, [69778,58440,2913,64975,92300]) ORDER BY f32 ASC",
        "WHERE has(array, toInt32(toString(69778)))",
        "WHERE hasAny(array, [69778,58440,2913,64975,92300]) ORDER BY f32 asc",
        "WHERE '48' NOT IN 'int' AND fixed_str='BYYC'",
    ]

    check_parquet_with_bloom(
        file_name=file_name,
        bloom_filter=either(*filter),
        filter_pushdown=either(*filter),
        condition=either(*conditions),
        statement=either(*statements),
        native_reader=native_reader,
    )


@TestSketch(Scenario)
def read_bloom_filter_parquet_files_native_reader(self):
    """Read all files from a bloom directory that contains parquet files with bloom filters using the ClickHouse parquet native reader."""

    file_name = "bloom/bloom_no_arrays.gz.parquet"
    statements = [
        "*",
        "f32",
        "f64",
        "int",
        "str",
        "fixed_str",
        "f32,f64,int,str,fixed_str",
    ]
    filter = ["true", "false"]
    native_reader = "true"
    conditions = [
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC'",
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC' OR str='KCGEY'",
        "WHERE f32=toFloat32(-15.910733) AND fixed_str IN ('BYYC', 'DCXV') ORDER BY f32 ASC",
        "WHERE f64 IN (toFloat64(22.89182051713945), toFloat64(68.62704389505595)) ORDER BY f32",
        "WHERE '48' NOT IN 'int' AND fixed_str='BYYC'",
    ]

    check_parquet_with_bloom(
        file_name=file_name,
        bloom_filter=either(*filter),
        filter_pushdown=either(*filter),
        condition=either(*conditions),
        statement=either(*statements),
        native_reader=native_reader,
    )


@TestScenario
def native_reader_array_bloom(self):
    """Read a parquet file with bloom filter and array column using the ClickHouse parquet native reader."""
    file = "array_bloom.gz.parquet"

    select_from_parquet(
        file_name=file,
        format="Json",
        settings=f"input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=false,use_cache_for_count_from_files=false, input_format_parquet_use_native_reader=true",
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter("1.0"))
@Name("bloom")
def feature(self, node="clickhouse1"):
    """Check if we can read from ap parquet file with bloom filter and validate that the bloom filter is being used
    by ClickHouse.

    The combinations used:
        - Check that ClickHouse can read and then write back the parquet files that have bloom filter applied to them.
    Combinatorics:
        statements:
            - "*",
            - "f32",
            - "f64",
            - "int",
            - "str",
            - "fixed_str",
            - "array",
            - "f32,f64,int,str,fixed_str,array",
        settings:
            - input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=true
            - input_format_parquet_bloom_filter_push_down=false,input_format_parquet_filter_push_down=false
            - input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=false
            - input_format_parquet_bloom_filter_push_down=false,input_format_parquet_filter_push_down=true
        conditions:
            - WHERE
            - OR
            - AND
            - IN
            - NOT IN
            - has()
            - hasAny()
            - hasAll()
    """
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "bloom"

    # Scenario(run=read_and_write_file_with_bloom)
    Scenario(run=read_bloom_filter_parquet_files)
    Scenario(run=read_bloom_filter_parquet_files_native_reader)
    Scenario(run=native_reader_array_bloom)
