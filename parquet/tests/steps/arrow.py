import pandas as pd
from testflows.core import *
import pyarrow as pa
import pyarrow.parquet as pq
import os

from helpers.common import getuid


@TestStep(Given)
def boolean_header_v2(self, file_path):
    """Create a parquet file with a boolean column and writer version 2.0."""
    file_name = file_path + f"/boolean_v2_{getuid()}.parquet"

    table = pa.Table.from_pydict(
        {"bool_col": [True, False, None]},
        schema=pa.schema([pa.field("bool_col", pa.bool_())]),
    )
    pq.write_table(table, file_name, version="2.0", data_page_version="2.0")

    return file_name


@TestStep(Given)
def int32_header_v2(self, file_path):
    """Create a parquet file with an int32 column and writer version 2.0."""
    file_name = file_path + f"/int32_v2_{getuid()}.parquet"

    table = pa.Table.from_pydict(
        {"int32_col": [1, 2, None]},
        schema=pa.schema([pa.field("int32_col", pa.int32())]),
    )
    pq.write_table(table, file_name, version="2.0", data_page_version="2.0")

    return file_name


@TestStep(Given)
def int64_header_v2(self, file_path):
    """Create a parquet file with an int64 column and writer version 2.0."""
    file_name = file_path + f"/int64_v2_{getuid()}.parquet"

    table = pa.Table.from_pydict(
        {"int64_col": [1, 2, None]},
        schema=pa.schema([pa.field("int64_col", pa.int64())]),
    )
    pq.write_table(table, file_name, version="2.0", data_page_version="2.0")
    return file_name


@TestStep(Given)
def float32_header_v2(self, file_path):
    """Create a parquet file with a float32 column and writer version 2.0."""
    file_name = file_path + f"/float32_v2_{getuid()}.parquet"

    table = pa.Table.from_pydict(
        {"float32_col": [1.1, 2.2, None]},
        schema=pa.schema([pa.field("float32_col", pa.float32())]),
    )
    pq.write_table(table, file_name, version="2.0", data_page_version="2.0")
    return file_name


@TestStep(Given)
def float64_header_v2(self, file_path):
    """Create a parquet file with a float64 column and writer version 2.0."""
    file_name = file_path + f"/float64_v2_{getuid()}.parquet"
    table = pa.Table.from_pydict(
        {"float64_col": [1.1, 2.2, None]},
        schema=pa.schema([pa.field("float64_col", pa.float64())]),
    )
    pq.write_table(table, file_name, version="2.0", data_page_version="2.0")
    return file_name


@TestStep(Given)
def string_header_v2(self, file_path):
    """Create a parquet file with a string column and writer version 2.0."""
    file_name = file_path + f"/string_v2_{getuid()}.parquet"

    table = pa.Table.from_pydict(
        {"string_col": ["a", "b", None]},
        schema=pa.schema([pa.field("string_col", pa.string())]),
    )
    pq.write_table(table, file_name, version="2.0", data_page_version="2.0")
    return file_name


@TestStep(Given)
def binary_header_v2(self, file_path):
    """Create a parquet file with a binary column and writer version 2.0."""
    file_name = file_path + f"/binary_v2_{getuid()}.parquet"
    table = pa.Table.from_pydict(
        {"binary_col": [b"a", b"b", None]},
        schema=pa.schema([pa.field("binary_col", pa.binary())]),
    )
    pq.write_table(table, file_name, version="2.0", data_page_version="2.0")
    return file_name


@TestStep(Given)
def timestamp_header_v2(self, file_path):
    """Create a parquet file with a timestamp column and writer version 2.0."""
    file_name = file_path + f"/timestamp_v2_{getuid()}.parquet"
    table = pa.Table.from_pydict(
        {"timestamp_col": [pa.timestamp("ms").from_pandas(pd.Timestamp.now())]},
        schema=pa.schema([pa.field("timestamp_col", pa.timestamp("ms"))]),
    )
    pq.write_table(table, file_name, version="2.0", data_page_version="2.0")
    return file_name


@TestStep(Given)
def list_header_v2(self, file_path):
    """Create a parquet file with a list column and writer version 2.0."""
    file_name = file_path + f"/list_v2_{getuid()}.parquet"

    list_array = pa.array([[1, 2, 3], None, [4, 5]], pa.list_(pa.int32()))
    table = pa.Table.from_arrays(
        [list_array],
        names=["list_col"],
        schema=pa.schema([pa.field("list_col", pa.list_(pa.int32()))]),
    )
    pq.write_table(table, file_name, version="2.0", data_page_version="2.0")
    return file_name


@TestStep(Given)
def struct_header_v2(self, file_path):
    """Create a parquet file with a struct column and writer version 2.0."""
    file_name = file_path + f"/struct_v2_{getuid()}.parquet"

    struct_array = pa.array(
        [{"a": 1, "b": 2}, None, {"a": 3, "b": 4}],
        pa.struct([("a", pa.int32()), ("b", pa.int32())]),
    )
    table = pa.Table.from_arrays(
        [struct_array],
        names=["struct_col"],
        schema=pa.schema(
            [pa.field("struct_col", pa.struct([("a", pa.int32()), ("b", pa.int32())]))]
        ),
    )
    pq.write_table(table, file_name, version="2.0", data_page_version="2.0")

    return file_name
