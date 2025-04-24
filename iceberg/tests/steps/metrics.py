from testflows.core import *


@TestStep(Then)
def get_IcebergPartitionPrunnedFiles(self, log_comment, node=None):
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebergPartitionPrunnedFiles'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
        """
    )
    return result


@TestStep(Then)
def get_IcebergTrivialCountOptimizationApplied(self, log_comment, node=None):
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebergTrivialCountOptimizationApplied'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
        """
    )
    return result


@TestStep(Then)
def get_IcebegerVersionHintUsed(self, log_comment, node=None):
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebegerVersionHintUsed'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
        """
    )
    return result


@TestStep(Then)
def get_IcebergMinMaxIndexPrunnedFiles(self, log_comment, node=None):
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
            SELECT ProfileEvents['IcebergMinMaxIndexPrunnedFiles'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}' 
            AND type = 'QueryFinish'
        """
    )
    return result
