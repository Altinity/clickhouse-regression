import pyarrow as pa
import pyarrow.parquet as pq

if __name__ == "__main__":
    """Generates a parquet file with a chunked array."""
    arr = pa.array([[("a" * 2**30, 1)]], type=pa.map_(pa.string(), pa.int32()))
    arr = pa.chunked_array([arr, arr])
    tab = pa.table({"arr": arr})
    pq.write_table(
        tab, "/var/lib/clickhouse/user_files/chunked_array_test_file.parquet"
    )
