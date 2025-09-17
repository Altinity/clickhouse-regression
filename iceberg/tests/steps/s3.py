from testflows.core import *


@TestStep(Then)
def read_data_with_s3_table_function(
    self, endpoint, s3_access_key_id, s3_secret_access_key, node=None, columns="*"
):
    """Read data from S3 using the s3 table function."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"SELECT {columns} FROM s3('{endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}') SETTINGS use_hive_partitioning=0"
    )
    return result
