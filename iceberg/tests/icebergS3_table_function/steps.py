from testflows.core import *

S3_ACCESS_KEY_ID = "minio"
S3_SECRET_ACCESS_KEY = "minio123"


@TestStep(Then)
def read_data_with_icebergS3_table_function(
    self,
    storage_endpoint,
    node=None,
    columns="*",
    s3_access_key_id=S3_ACCESS_KEY_ID,
    s3_secret_access_key=S3_SECRET_ACCESS_KEY,
):
    if node is None:
        node = self.context.node

    result = node.query(
        f"SELECT {columns} FROM icebergS3('{storage_endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}')"
    )
    return result
