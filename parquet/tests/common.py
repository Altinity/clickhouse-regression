import uuid

from testflows._core.testtype import TestSubType
from testflows.core.name import basename, parentname
from testflows.core import current
from helpers.common import *

@TestStep(Given)
def instrument_cluster_nodes(self, test, cluster_nodes, always_dump=True):
    """Instrument logs on cluster nodes."""
    for name in cluster_nodes:
        instrument_clickhouse_server_log(
            node=self.context.cluster.node(name), test=test, always_dump=always_dump
        )


@TestStep(When)
def create_simple_table(
    self,
    node=None,
    table_name="test",
    cluster_name="'Cluster_3shards_with_3replicas'",
    values="Id Int32, partition Int32",
    manual_cleanup=False,
):
    """Create simple table with timeout option.

    :param node: node for table
    :param table_name: table name
    :param cluster_name: name of cluster for replicated table
    :param manual_cleanup: manual cleanup
    """
    if node is None:
        node = self.context.cluster.node("clickhouse1")
    try:
        retry(node.query, timeout=100, delay=1)(
            f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
            f" ({values}) "
            "ENGINE = ReplicatedMergeTree('/clickhouse/tables/replicated/{shard}"
            f"/{table_name}'"
            ", '{replica}') "
            "ORDER BY Id PARTITION BY Id",
            steps=False,
        )
        yield table_name
    finally:
        with Finally("I clean up"):
            if manual_cleanup is False:
                with By("dropping table if exists"):
                    node.query(
                        f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
                    )


@TestStep(Given)
def create_table(timezone, node):
    try:
        node.query(
            f"CREATE TABLE dt(timestamp DateTime64(3, {timezone})) Engine = TinyLog"
        )
        yield
    finally:
        node.query("DROP TABLE dt")


@TestOutline
def insert_check_datetime(self, datetime, expected, precision=0, timezone="UTC"):
    """Check how a particular datetime value works with different
    functions that accept DateTime64 data type.

    :param datetime: datetime string
    :param expected: expected result
    :param precision: time precision, default: 0
    :param timezone: timezone, default: UTC
    """
    with create_table(timezone, self.context.node):
        with When("I use toDateTime64"):
            r = self.context.node.query(
                f"SELECT toDateTime64('{datetime}', {precision}, '{timezone}')"
            )

    with Then(f"I expect {expected}"):
        assert r.output == expected, error()


@TestStep(Given)
def allow_experimental_map_type(self):
    """Set allow_experimental_map_type = 1"""
    setting = ("allow_experimental_map_type", 1)
    default_query_settings = None

    try:
        with By("adding allow_experimental_map_type to the default query settings"):
            default_query_settings = getsattr(
                current().context, "default_query_settings", []
            )
            default_query_settings.append(setting)
        yield
    finally:
        with Finally(
            "I remove allow_experimental_map_type from the default query settings"
        ):
            if default_query_settings:
                try:
                    default_query_settings.pop(default_query_settings.index(setting))
                except ValueError:
                    pass


@TestStep(Given)
def table(self, data_type, name="table0"):
    """Create a table."""
    node = current().context.node

    try:
        with By("creating table"):
            node.query(f"CREATE TABLE {name}(a {data_type}) ENGINE = Memory")
        yield

    finally:
        with Finally("drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep(When)
def insert(
    self,
    table_name,
    values=None,
    partitions=1,
    parts_per_partition=1,
    block_size=1000,
    no_checks=False,
    settings=[],
    node=None,
    table_engine=None,
):
    """Insert data having specified number of partitions and parts."""
    if node is None:
        node = self.context.node

    if table_engine is None:
        table_engine = self.context.table_engine

    if values is None:
        if table_engine in (
            "MergeTree",
            "ReplacingMergeTree",
            "SummingMergeTree",
            "AggregatingMergeTree",
        ):
            values = ",".join(
                f"({x},{y})"
                for x in range(partitions)
                for y in range(block_size * parts_per_partition)
            )

        if table_engine in ("CollapsingMergeTree", "VersionedCollapsingMergeTree"):
            values = ",".join(
                f"({x},{y},1)"
                for x in range(partitions)
                for y in range(block_size * parts_per_partition)
            )

        if table_engine == "GraphiteMergeTree":
            values = ",".join(
                f"({x},{y}, '1', toDateTime(10), 10, 10)"
                for x in range(partitions)
                for y in range(block_size * parts_per_partition)
            )

    return node.query(
        f"INSERT INTO {table_name} VALUES {values}",
        settings=[("max_block_size", block_size)] + settings,
        no_checks=no_checks,
    )


@TestStep(Given)
def create_view(self, view_type, view_name, condition, node=None):
    """Create view."""
    if node is None:
        node = self.context.node

    try:
        with Given("I create view"):
            if view_type == "LIVE":
                node.query(
                    f"CREATE {view_type} VIEW {view_name} as {condition}",
                    settings=[("allow_experimental_live_view", 1)],
                )
            elif view_type == "WINDOW":
                node.query(
                    f"CREATE {view_type} VIEW {view_name} as {condition}",
                    settings=[("allow_experimental_window_view", 1)],
                )
            else:
                node.query(f"CREATE {view_type} VIEW {view_name} as {condition}")

        yield
    finally:
        with Finally("I delete view"):
            node.query(f"DROP VIEW {view_name} SYNC")


def getuid():
    if current().subtype == TestSubType.Example:
        testname = (
            f"{basename(parentname(current().name)).replace(' ', '_').replace(',','')}"
        )
    else:
        testname = f"{basename(current().name).replace(' ', '_').replace(',','')}"
    return testname + "_" + str(uuid.uuid1()).replace("-", "_")