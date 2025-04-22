from testflows.core import *


@TestStep(Given)
def select_with_s3Cluster(
    self,
    cluster_name,
    select_columns="*",
    group_by_columns=None,
    url="http://minio:9000/warehouse/data/data/**/**.parquet",
    minio_user="minio_user",
    minio_password="minio_password",
    node=None,
    format="TabSeparated",
    exitcode=None,
    message=None,
):
    """Check select with s3 table function and swarm cluster.

    Args:
        cluster_name: Name of the swarm cluster to use
        select_columns: Columns to select
        group_by_columns: Columns to group by
        url: Bucket url with path to file.
        minio_user: Minio user
        minio_password: Minio password
        node: Node to run the query on
        format: Format of the result
        exitcode: Exit code of the query
        message: Message of the query
    Returns:
        Result of the query
    """
    if node is None:
        node = self.context.node

    query = f"""
            SELECT {select_columns} 
            FROM s3Cluster('{cluster_name}', '{url}', '{minio_user}', '{minio_password}')
            """

    if group_by_columns:
        query += f" GROUP BY {group_by_columns}"

    if format:
        query += f" FORMAT {format}"

    query += f" SETTINGS object_storage_cluster='{cluster_name}'"

    with By("select with s3 table function and swarm cluster"):
        result = node.query(query, exitcode=exitcode, message=message)
        return result
