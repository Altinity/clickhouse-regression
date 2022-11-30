import time

from testflows.core import *
from helpers.common import create_xml_config_content, add_config
from helpers.common import getuid, instrument_clickhouse_server_log


@TestStep(Given)
def instrument_cluster_nodes(self, test, cluster_nodes, always_dump=True):
    """Instrument logs on cluster nodes."""
    for name in cluster_nodes:
        instrument_clickhouse_server_log(
            node=self.context.cluster.node(name), test=test, always_dump=always_dump
        )


@TestStep(Given)
def create_table(
    self,
    core_table=None,
    core_table_engine=None,
    distributed=None,
    cluster=None,
    distributed_table=None,
):
    """
    Create clickhouse table.

    :param core_table: core table name
    :param core_table_engine: core table engine
    :param distributed: enable distributed engine
    :param cluster: cluster name
    :param distributed_table: distributed table engine
    """

    node = self.context.cluster.node("clickhouse1")

    try:
        with Given("I create data table"):
            node.query(
                f"create table if not exists {core_table} (x String, sign Int8 DEFAULT 1, version Int8 DEFAULT 1)"
                f" engine={core_table_engine} ORDER BY x SETTINGS force_select_final=1;"
            )
            if distributed:
                retry(node.query, timeout=100, delay=1)(
                    f"CREATE TABLE IF NOT EXISTS {distributed_table}  ON CLUSTER '{cluster}'"
                    f" as {core_table}"
                    " ENGINE = Distributed"
                    f"({cluster}, currentDatabase(), {core_table})",
                    steps=False,
                )
        yield
    finally:
        with Finally("I drop tables"):
            node.query(f"DROP TABLE {core_table};")
            if distributed:
                node.query(f"DROP TABLE {distributed_table} ON CLUSTER '{cluster}';")


@TestStep(Given)
def insert_into_table(
    self,
    table_name=None,
    block_number=1,
    row_number=1,
    unique_rows=True,
    equal_rows=False,
):
    node = self.context.cluster.node("clickhouse1")
    for i in range(block_number):
        for k in range(row_number):
            if unique_rows:
                node.query(
                    f"insert into {table_name} values (randomString(5) ,{i+1}, {k+1});"
                )
            elif equal_rows:
                node.query(f"insert into {table_name} values ('abc',{i+1}, {k+1});")


@TestStep(Given)
def select(self, table_name=None, output=None):
    with Given(f"Select from table {table_name}"):
        for node_name in self.context.cluster.nodes["clickhouse"]:
            with When(f"on {node_name} "):
                retry(
                    self.context.cluster.node(node_name).query,
                    timeout=100,
                    delay=1,
                )(
                    f"select count() from {table_name}",
                    message=f"{output}",
                    exitcode=0,
                )
