from testflows.core import *
from helpers.common import check_clickhouse_version


def wait_for_metrics(log_comment, node=None):
    """Wait until QueryFinish event is logged and metrics are collected."""
    for retry in retries(count=10, delay=1):
        with retry:
            count = node.query(
                f"""
                    SELECT count()
                    FROM system.query_log
                    WHERE log_comment = '{log_comment}'
                    AND type = 'QueryFinish'
                    """
            )
            assert int(count.output) > 0


@TestStep(Then)
def get_IcebergPartitionPrunedFiles(
    self, log_comment, node=None, format="TabSeparated"
):
    """Get the number of skipped files during Iceberg partition pruning."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    if check_clickhouse_version(">=25.5")(self):
        profile_event_field_name = "IcebergPartitionPrunedFiles"
    else:
        profile_event_field_name = "IcebergPartitionPrunnedFiles"

    result = node.query(
        f"""
            SELECT ProfileEvents['{profile_event_field_name}'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )
    return result


@TestStep(Then)
def get_IcebergTrivialCountOptimizationApplied(
    self, log_comment, node=None, format="TabSeparated"
):
    """Get the number of times trivial count optimization was applied while
    reading from Iceberg."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebergTrivialCountOptimizationApplied'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )
    return result


@TestStep(Then)
def get_IcebergVersionHintUsed(self, log_comment, node=None, format="TabSeparated"):
    """Get the number of times version hint has been used."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    if check_clickhouse_version(">=25.5")(self):
        profile_event_field_name = "IcebergVersionHintUsed"
    else:
        profile_event_field_name = "IcebegerVersionHintUsed"

    result = node.query(
        f"""
            SELECT ProfileEvents['{profile_event_field_name}'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )
    return result


@TestStep(Then)
def get_IcebergMinMaxIndexPrunedFiles(
    self, log_comment, node=None, format="TabSeparated"
):
    """Get the number of skipped files by using MinMax index in Iceberg."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    if check_clickhouse_version(">=25.5")(self):
        profile_event_field_name = "IcebergMinMaxIndexPrunedFiles"
    else:
        profile_event_field_name = "IcebergMinMaxIndexPrunnedFiles"

    result = node.query(
        f"""
            SELECT ProfileEvents['{profile_event_field_name}'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )
    return result


@TestStep(Then)
def get_IcebergMetadataFilesCacheHits(
    self, log_comment, node=None, format="TabSeparated"
):
    """Returns the number of times iceberg metadata files have been
    found in the cache."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebergMetadataFilesCacheHits'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )
    return result


@TestStep(Then)
def get_IcebergMetadataFilesCacheMisses(
    self, log_comment, node=None, format="TabSeparated"
):
    """Get the number of times iceberg metadata files have not been found in the
    iceberg metadata cache and had to be read from (remote) disk."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebergMetadataFilesCacheMisses'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )

    return result


@TestStep(Then)
def get_IcebergMetadataFilesCacheWeightLost(
    self, log_comment, node=None, format="TabSeparated"
):
    """Get the approximate number of bytes evicted from the iceberg metadata cache."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebergMetadataFilesCacheWeightLost'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )
    return result


@TestStep(Then)
def get_read_rows(self, log_comment, node=None, format="TabSeparated"):
    """Get the number of read rows."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    result = node.query(
        f"""
            SELECT read_rows 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )
    return result


@TestStep(Then)
def get_S3ReadRequestsCount(
    self, log_comment, node=None, format="TabSeparated", is_initial_query=None
):
    """Get the number of S3 read requests."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    query = f"""
            SELECT ProfileEvents['S3ReadRequestsCount'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
        """

    if is_initial_query is not None:
        if is_initial_query:
            query += f" AND is_initial_query= 1"
        else:
            query += f" AND is_initial_query = 0"

    if format is not None:
        query += f" FORMAT {format}"

    result = node.query(query)
    return result


@TestStep(Then)
def get_S3GetObject(
    self, log_comment, node=None, format="TabSeparated", is_initial_query=False
):
    """Get the number of S3 get object requests."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    query = f"""
            SELECT ProfileEvents['S3GetObject'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
        """

    if is_initial_query is not None:
        if is_initial_query:
            query += f" AND is_initial_query= 1"
        else:
            query += f" AND is_initial_query = 0"

    if format is not None:
        query += f" FORMAT {format}"

    result = node.query(query)
    return result


@TestStep(Then)
def get_memory_usage(self, log_comment, node=None, format="TabSeparated"):
    """Get the memory usage of the query."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    result = node.query(
        f"""
            SELECT memory_usage 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )
    return result


@TestStep(Then)
def check_all_iceberg_metrics(self, log_comment, node=None, format="Vertical"):
    """Check all iceberg related metrics."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    IcebergPartitionPrunedFiles = (
        "IcebergPartitionPrunedFiles"
        if check_clickhouse_version(">=25.5")(self)
        else "IcebergPartitionPrunnedFiles"
    )
    IcebergMinMaxIndexPrunedFiles = (
        "IcebergMinMaxIndexPrunedFiles"
        if check_clickhouse_version(">=25.5")(self)
        else "IcebergMinMaxIndexPrunnedFiles"
    )
    IcebergVersionHintUsed = (
        "IcebergVersionHintUsed"
        if check_clickhouse_version(">=25.5")(self)
        else "IcebegerVersionHintUsed"
    )

    with And("check metrics"):
        result = node.query(
            f"""
                SELECT 
                ProfileEvents['{IcebergPartitionPrunedFiles}'] as iceberg_partition_pruned_files,
                ProfileEvents['IcebergTrivialCountOptimizationApplied'] as iceberg_trivial_count_optimization_applied,
                ProfileEvents['{IcebergVersionHintUsed}'] as iceberg_version_hint_used,
                ProfileEvents['{IcebergMinMaxIndexPrunedFiles}'] as iceberg_min_max_index_pruned_files,
                ProfileEvents['IcebergMetadataFilesCacheHits'] as iceberg_metadata_files_cache_hits,
                ProfileEvents['IcebergMetadataFilesCacheMisses'] as iceberg_metadata_files_cache_misses,
                ProfileEvents['IcebergMetadataFilesCacheWeightLost'] as iceberg_metadata_files_cache_weight_lost,
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
        )
    return result


@TestStep(Then)
def get_s3_profile_events(self, log_comment, node=None, format="Vertical"):
    """Get S3 related fields from ProfileEvents."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    result = node.query(
        f"""
        SELECT arrayJoin(
            mapFilter((k, v) -> (k LIKE 'S3%'), 
            sumMap(ProfileEvents))
        ) AS s3_events
        FROM system.query_log
        WHERE type = 'QueryFinish' and log_comment = '{log_comment}'
        FORMAT {format}
        """
    )
    return result


@TestStep(Then)
def get_query_duration(self, log_comment, node=None, format="TabSeparated"):
    """Get the query duration in milliseconds from system.query_log table."""
    if node is None:
        node = self.context.node

    with By("wait for metrics to be collected"):
        wait_for_metrics(log_comment, node)

    result = node.query(
        f"""
            SELECT query_duration_ms 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )
    return result
