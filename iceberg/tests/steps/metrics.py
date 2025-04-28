from testflows.core import *


@TestStep(Then)
def get_IcebergPartitionPrunnedFiles(
    self, log_comment, node=None, format="TabSeparated"
):
    """Number of skipped files during Iceberg partition pruning."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebergPartitionPrunnedFiles'] 
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
    """Trivial count optimization applied while reading from Iceberg."""
    if node is None:
        node = self.context.node

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
def get_IcebegerVersionHintUsed(self, log_comment, node=None, format="TabSeparated"):
    """Number of times version-hint.text has been used."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebegerVersionHintUsed'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
            FORMAT {format}
        """
    )
    return result


@TestStep(Then)
def get_IcebergMinMaxIndexPrunnedFiles(
    self, log_comment, node=None, format="TabSeparated"
):
    """Number of skipped files by using MinMax index in Iceberg."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebergMinMaxIndexPrunnedFiles'] 
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
    """
    Returns the number of times iceberg metadata files have been
    found in the cache.
    """
    if node is None:
        node = self.context.node

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
    """
    Number of times iceberg metadata files have not been found in the
    iceberg metadata cache and had to be read from (remote) disk.
    """
    if node is None:
        node = self.context.node

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
    """Approximate number of bytes evicted from the iceberg metadata cache."""
    if node is None:
        node = self.context.node

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
    """Number of rows read from Iceberg."""
    if node is None:
        node = self.context.node

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
