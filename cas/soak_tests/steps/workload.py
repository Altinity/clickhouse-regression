from testflows.core import *

from cas.soak_tests.oracle.rowgen import BASE_TIME, NBUCKETS
from cas.soak_tests.oracle.workload import (
    delete_sql,
    insert_values_sql,
    truncate_sql,
    update_sql,
)


@TestStep(When)
def insert_block(self, table, seed, op_id, n, node=None, base_time=BASE_TIME, settings=""):
    if node is None:
        node = self.context.node
    sql = insert_values_sql(
        seed=seed, op_id=op_id, n=n, table=table, base_time=base_time, settings=settings
    )
    node.query(sql)
    return n


@TestStep(When)
def update_bucket(self, table, param, node=None):
    if node is None:
        node = self.context.node
    bucket = param % NBUCKETS
    node.query(update_sql(table=table, bucket=bucket))
    return bucket


@TestStep(When)
def delete_bucket(self, table, param, node=None):
    if node is None:
        node = self.context.node
    bucket = param % NBUCKETS
    node.query(delete_sql(table=table, bucket=bucket))
    return bucket


@TestStep(When)
def truncate_table(self, table, node=None):
    if node is None:
        node = self.context.node
    node.query(truncate_sql(table=table))
