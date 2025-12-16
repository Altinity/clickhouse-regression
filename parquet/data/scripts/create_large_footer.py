import os

from testflows.core import *
import pyarrow as pa
import pyarrow.parquet as pq

from helpers.common import getuid


@TestStep(Given)
def create_parquet_with_large_footer(self, file_path=None, node=None):
    """Create a parquet file with large footer, upload it to a node, and delete the local file."""
    if node is None:
        node = self.context.node

    if file_path is None:
        file_name = f"large_footer_{getuid()}.parquet"
        file_path = os.path.join(current_dir(), "..", "arrow", file_name)
    else:
        file_name = os.path.basename(file_path)
        local_dir = os.path.join(current_dir(), "..", "arrow")
        os.makedirs(local_dir, exist_ok=True)
        file_path = os.path.join(local_dir, file_name)

    TARGET = 120 * 1024 * 1024

    table = pa.table({"x": pa.array([1, 2, 3], type=pa.int32())})

    payload = b"A" * TARGET
    meta = dict(table.schema.metadata or {})
    meta[b"giant_meta"] = payload
    table2 = table.replace_schema_metadata(meta)

    pq.write_table(table2, file_path, compression="snappy")

    try:
        with By("uploading the parquet file to the node"):
            container_name = self.context.cluster.command(
                None, f"docker ps | grep {node.name} | cut -d ' ' -f 1 | head -n 1"
            ).output.strip()

            node_file_path = f"/var/lib/clickhouse/user_files/{file_name}"
            self.context.cluster.command(
                None, f"docker cp {file_path} {container_name}:{node_file_path}"
            )

        return file_name
    finally:
        with Finally("deleting the local file"):
            if os.path.exists(file_path):
                os.remove(file_path)
