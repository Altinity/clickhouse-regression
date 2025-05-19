from testflows.core import *

from helpers.common import getuid


@TestStep(Then)
def get_number_of_requests_from_clickhouse_to_object_storage(
    self, log_comment, node=None
):
    """Get the number of requests from ClickHouse to object storage."""
    if node is None:
        node = self.context.node

    for retry in retries(timeout=15, delay=1):
        with retry:
            api_requests = node.query(
                f"""SELECT arrayJoin(mapFilter((k, v) -> (k LIKE 'S3%'), sumMap(ProfileEvents))) AS s3_events FROM system.query_log WHERE type = 'QueryFinish'  and event_date = today() and log_comment = '{log_comment}' FORMAT JSON"""
            )
            assert api_requests.output.strip() != "", "API requests are empty"

    return api_requests.output.strip()


@TestStep(Given)
def select_parquet_from_public_blockchain_bucket(
    self,
    node=None,
    where=None,
    group_by=None,
    order_by=None,
    settings=None,
    cache_list_object=True,
    output_format=None,
):
    """Select parquet from public blockchain bucket."""
    log_comment = f"log_{getuid()}"

    if node is None:
        node = self.context.node

    query_settings = " SETTINGS "

    if cache_list_object:
        query_settings += "use_object_storage_list_objects_cache = 1"
    else:
        query_settings += "use_object_storage_list_objects_cache = 0"

    query_settings += f", log_comment = '{log_comment}'"

    if settings:
        query_settings += f", {settings}"

    query = "SELECT date, count() FROM s3('s3://aws-public-blockchain/v1.0/btc/transactions/*/*.parquet', NOSIGN)"

    if where:
        query += f" WHERE {where}"

    if group_by:
        query += f" GROUP BY {group_by}"

    if order_by:
        query += f" ORDER BY {order_by}"

    if output_format is None:
        query += " FORMAT TabSeparated"
    else:
        query += f" FORMAT {output_format}"

    query += f"{query_settings}"

    return node.query(query), log_comment


@TestStep(Then)
def drop_list_object_cache(self, node=None):
    """Drop list object cache."""
    if node is None:
        node = self.context.node

    return node.query("SYSTEM DROP OBJECT STORAGE LIST OBJECTS CACHE")
