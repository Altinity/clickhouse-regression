from testflows.core import *


@TestStep(Then)
def read_data_with_icebergS3_table_function(
    self,
    storage_endpoint,
    s3_access_key_id,
    s3_secret_access_key,
    node=None,
    columns="*",
):
    """Read Iceberg tables from S3 using the icebergS3 table function."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"SELECT {columns} FROM iceberg('{storage_endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}')"
    )
    return result
