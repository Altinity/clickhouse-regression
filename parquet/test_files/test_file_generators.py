import pyarrow as pa
import pyarrow.parquet as pq


def chunked_array_file():
    arr = pa.array([[("a" * 2**30, 1)]], type=pa.map_(pa.string(), pa.int32()))
    arr = pa.chunked_array([arr, arr])
    tab = pa.table({"arr": arr})
    pq.write_table(tab, "chunked_array_test_file.parquet")
