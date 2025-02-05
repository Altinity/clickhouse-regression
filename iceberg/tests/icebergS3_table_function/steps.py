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
    if node is None:
        node = self.context.node

    result = node.query(
        f"SELECT {columns} FROM icebergS3('{storage_endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}')"
    )
    return result
