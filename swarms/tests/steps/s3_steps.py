from testflows.core import *


@TestStep(Then)
def read_data_with_s3_table_function(
    self,
    s3_access_key_id,
    s3_secret_access_key,
    endpoint="http://minio:9000/warehouse/data/**/**.parquet",
    columns="*",
    group_by=None,
    order_by=None,
    format="TabSeparated",
    object_storage_cluster=None,
    use_hive_partitioning=None,
    exitcode=None,
    message=None,
    node=None,
):
    """Read data from S3 using the s3 table function.

    Args:
        s3_access_key_id: Minio user
        s3_secret_access_key: Minio password
        endpoint: Bucket url with path to file
        columns: Columns to select
        group_by: Columns to group by
        order_by: Columns to order by
        format: Format of the result
        object_storage_cluster: swarm cluster name
        use_hive_partitioning: Use hive partitioning
        exitcode: Exit code of the query
        message: Message of the query
        node: Node to run the query on

    Returns:
        Result of the query
    """
    if node is None:
        node = self.context.node

    settings = []

    if object_storage_cluster:
        settings.append(
            (
                "object_storage_cluster",
                object_storage_cluster,
            )
        )
    if use_hive_partitioning is not None:
        settings.append(
            (
                "use_hive_partitioning",
                use_hive_partitioning,
            )
        )

    query = f"""
            SELECT {columns} 
            FROM s3('{endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}') 
            """

    if group_by:
        query += f" GROUP BY {group_by}"

    if order_by:
        query += f" ORDER BY {order_by}"

    if format:
        query += f" FORMAT {format}"

    result = node.query(
        query,
        settings=settings,
        exitcode=exitcode,
        message=message,
    )
    return result


@TestStep(Given)
def read_data_with_s3Cluster_table_function(
    self,
    cluster_name,
    s3_access_key_id,
    s3_secret_access_key,
    columns="*",
    url="http://minio:9000/warehouse/data/data/**/**.parquet",
    group_by=None,
    order_by=None,
    format="TabSeparated",
    exitcode=None,
    message=None,
    node=None,
):
    """Read data from S3 using the s3Cluster table function.

    Args:
        cluster_name: Name of the swarm cluster to use
        s3_access_key_id: Minio user
        s3_secret_access_key: Minio password
        columns: Columns to select
        url: Bucket url with path to files
        group_by: Columns to group by
        order_by: Columns to order by
        format: Format of the result
        exitcode: Exit code of the query
        message: Message of the query
        node: Node to run the query on

    Returns:
        Result of the query
    """
    if node is None:
        node = self.context.node

    query = f"""
            SELECT {columns} 
            FROM s3Cluster('{cluster_name}', '{url}', '{s3_access_key_id}', '{s3_secret_access_key}')
            """

    if group_by:
        query += f" GROUP BY {group_by}"

    if order_by:
        query += f" ORDER BY {order_by}"

    if format:
        query += f" FORMAT {format}"

    result = node.query(query, exitcode=exitcode, message=message)
    return result
