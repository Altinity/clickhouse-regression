from testflows.core import *


@TestStep(Then)
def get_number_of_requests_from_clickhouse_to_object_storage(
    self, log_comment, node=None
):
    """Get the number of requests from ClickHouse to object storage."""
    if node is None:
        node = self.context.node

    return node.query(
        f"""SELECT arrayJoin(mapFilter((k, v) -> (k LIKE 'S3%'), sumMap(ProfileEvents))) AS s3_events FROM system.query_log WHERE type = 'QueryFinish'  and event_date = today() and log_comment = '{log_comment}'"""
    )


@TestStep(Given)
def select_parquet_from_public_blockchain_bucket(
    self, node=None, where=None, group_by=None, settings=None, cache_list_object=True
):
    """Select parquet from public blockchain bucket."""
    if node is None:
        node = self.context.node

    query_settings = "SETTINGS "

    if cache_list_object:
        query_settings += "use_object_storage_list_objects_cache = 1"
    else:
        query_settings += "use_object_storage_list_objects_cache = 0"

    if settings:
        query_settings += settings

    query = "SELECT * FROM s3('s3://aws-public-blockchain/v1.0/btc/transactions/*/*.parquet', NOSIGN)"

    if where:
        query += f" WHERE {where}"
    if group_by:
        query += f" GROUP BY {group_by}"

    query += f" SETTINGS {query_settings}"

    return node.query(query)
