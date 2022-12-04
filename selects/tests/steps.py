import time
import random
from helpers.common import getuid
from testflows.core import *
from helpers.common import create_xml_config_content, add_config
from helpers.common import getuid, instrument_clickhouse_server_log


@TestStep(Given)
def create_and_populate_table(
    self,
    name,
    engine,
    schema,
    final_modifier_available,
    cluster_name=None,
    values=None,
    populate=True,
    range_value=5,
    node=None,
):
    """
    Create clickhouse table.
    :param name: core table name
    :param populate: populates table default: True
    :param engine: core table engine
    :param schema: core table schema
    :param final_modifier_available: true if `FINAL` modifier available for engine
    """

    if node is None:
        node = current().context.node
    try:
        with By(f"creating table {name}"):
            node.query(
                f"CREATE TABLE {name} "
                f"{' ON CLUSTER {cluster_name}'.format(cluster_name=cluster_name) if cluster_name is not None else ''}"
                f" {schema} "
                f"ENGINE = {engine} "
                f"{' ORDER BY key' if not engine.endswith('Log') else ''};"
            )

        if populate:
            with And("populating table"):
                node.query("system stop merges")
                for i in range(range_value):
                    node.query(f"INSERT INTO {name} VALUES {values[0].format(i=i)}")
                    node.query(f"INSERT INTO {name} VALUES {values[1].format(i=i)}")
        yield Table(name, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(
                f"DROP TABLE IF EXISTS {name} "
                f"{' ON CLUSTER {cluster_name}'.format(cluster_name=cluster_name) if cluster_name is not None else ''}"
            )


class Table:
    def __init__(self, name, engine, final_modifier_available, cluster=None):
        self.name = name
        self.engine = engine
        self.final_modifier_available = final_modifier_available
        self.cluster = cluster


@TestStep(Given)
def create_and_populate_core_tables(self):
    """Create and populate all test tables for different table engines."""
    engines = [
        "ReplacingMergeTree",
        "ReplacingMergeTree({version})",
        "CollapsingMergeTree({sign})",
        "AggregatingMergeTree",
        "SummingMergeTree",
        "VersionedCollapsingMergeTree({sign},{version})",
        "MergeTree",
        "StripeLog",
        "TinyLog",
        "Log",
    ]
    for engine in engines:
        with Given(f"{engine} table"):
            name = engine
            symbols = [("(", "_"), (",", "_"), (")", ""), ("{", ""), ("}", "")]
            for symbol in symbols:
                name = name.replace(symbol[0], symbol[1])
            name = f"{name}_table_{getuid()}"

            if engine.startswith("Replacing"):
                self.context.tables.append(
                    create_and_populate_replacing_table(
                        name=name,
                        engine=engine,
                    )
                )
            elif engine.startswith("Collapsing"):
                self.context.tables.append(
                    create_and_populate_collapsing_table(
                        name=name,
                        engine=engine,
                    )
                )

            elif engine.startswith("Aggregating"):
                self.context.tables.append(
                    create_and_populate_aggregating_table(
                        name=name,
                        engine=engine,
                    )
                )

            elif engine.startswith("Summing"):
                self.context.tables.append(
                    create_and_populate_summing_table(
                        name=name,
                        engine=engine,
                    )
                )

            elif engine.startswith("Merge"):
                self.context.tables.append(
                    create_and_populate_merge_table(
                        name=name,
                        engine=engine,
                    )
                )
            elif engine.startswith("Versioned"):
                self.context.tables.append(
                    create_and_populate_versioned_table(name=name, engine=engine)
                )
            elif (
                engine.startswith("StripeLog")
                or engine.startswith("TinyLog")
                or engine.startswith("Log")
            ):
                self.context.tables.append(
                    create_and_populate_log_table(name=name, engine=engine)
                )


@TestStep
def add_system_tables(self):
    tables_list = [
        "system.time_zones",
        "system.trace_log",
        "system.user_directories",
        "system.users",
        "system.warnings",
        "system.zeros",
        "system.zeros_mt",
        "system.zookeeper",
    ]
    for table_name in tables_list:
        with Given(f"{table_name} table"):
            self.context.tables.append(
                Table(name=table_name, engine=None, final_modifier_available=False)
            )


@TestStep(Given)
def create_and_populate_replacing_table(
    self,
    name,
    populate=True,
    final_modifier_available=True,
    engine="ReplacingMergeTree",
    node=None,
    cluster_name=None,
):
    if node is None:
        node = current().context.node

    schema = "(key Int64, someCol String, eventTime DateTime)"

    engine_local = (
        engine.format(version="eventTime") if engine.endswith("({version})") else engine
    )

    values = [
        "({i}, 'first', '2020-01-01 01:01:01')",
        "({i}, 'second', '2020-01-01 00:00:00')",
    ]

    return create_and_populate_table(
        name=name,
        engine=engine_local,
        schema=schema,
        values=values,
        final_modifier_available=final_modifier_available,
        populate=populate,
        node=node,
        cluster_name=cluster_name,
    )


@TestStep
def create_and_populate_collapsing_table(
    self,
    name,
    populate=True,
    final_modifier_available=True,
    engine="CollapsingMergeTree",
    node=None,
    cluster_name=None,
):
    schema = "( key UInt64, PageViews UInt8, Duration UInt8, Sign Int8)"

    engine_local = engine.format(sign="Sign") if engine.endswith("({sign})") else engine

    values = [
        "(4324182021466249494, {i}, 146, 1)",
        "(4324182021466249494, {i}, 146, -1)," "(4324182021466249494, {i}, 185, 1)",
    ]

    return create_and_populate_table(
        name=name,
        engine=engine_local,
        schema=schema,
        values=values,
        final_modifier_available=final_modifier_available,
        populate=populate,
        node=node,
        cluster_name=cluster_name,
    )


@TestStep
def create_and_populate_aggregating_table(
    self,
    name,
    populate=True,
    final_modifier_available=True,
    engine="AggregatingMergeTree",
    node=None,
    cluster_name=None,
):
    schema = "(key String, b UInt8, c SimpleAggregateFunction(max, UInt8))"
    values = ["('a', {i}, 1)", "('a', {i}+1, 2)"]
    return create_and_populate_table(
        name=name,
        engine=engine,
        schema=schema,
        values=values,
        final_modifier_available=final_modifier_available,
        populate=populate,
        node=node,
        cluster_name=cluster_name,
    )


@TestStep
def create_and_populate_summing_table(
    self,
    name,
    populate=True,
    final_modifier_available=True,
    engine="SummingMergeTree",
    node=None,
    cluster_name=None,
):
    schema = "(key Int64, someCol String, eventTime DateTime)"
    values = [
        "({i}, 'first', '2020-01-01 01:01:01')",
        "({i}, 'second', '2020-01-01 00:00:00')",
    ]
    return create_and_populate_table(
        name=name,
        engine=engine,
        schema=schema,
        values=values,
        final_modifier_available=final_modifier_available,
        populate=populate,
        node=node,
        cluster_name=cluster_name,
    )


@TestStep
def create_and_populate_merge_table(
    self,
    name,
    populate=True,
    final_modifier_available=False,
    engine="MergeTree",
    node=None,
    cluster_name=None,
):
    values = [
        "({i}, 'first', '2020-01-01 01:01:01')",
        "({i}, 'second', '2020-01-01 00:00:00')",
    ]
    schema = "(key Int64, someCol String, eventTime DateTime)"
    return create_and_populate_table(
        name=name,
        engine=engine,
        schema=schema,
        values=values,
        final_modifier_available=final_modifier_available,
        populate=populate,
        node=node,
        cluster_name=cluster_name,
    )


@TestStep
def create_and_populate_versioned_table(
    self,
    name,
    populate=True,
    final_modifier_available=True,
    engine="VersionedCollapsingMergeTree(sign,version)",
    node=None,
    cluster_name=None,
):
    values = [
        "({i}, 'first', 1, 1)",
        "({i}, 'second', 1, 1),({i}+1, 'third', -1, 2)",
    ]
    schema = "(key Int64, someCol String, Sign Int8, version UInt8)"

    engine_local = (
        engine.format(sign="Sign", version="version")
        if engine.endswith("({sign},{version})")
        else engine
    )
    return create_and_populate_table(
        name=name,
        engine=engine_local,
        schema=schema,
        values=values,
        final_modifier_available=final_modifier_available,
        populate=populate,
        node=node,
        cluster_name=cluster_name,
    )


@TestStep
def create_and_populate_log_table(
    self,
    name,
    populate=True,
    final_modifier_available=False,
    engine="Log",
    node=None,
    cluster_name=None,
):
    values = [
        "({i}, 'first', '2020-01-01 01:01:01')",
        "({i}, 'second', '2020-01-01 00:00:00')",
    ]
    schema = "(key Int64, someCol String, eventTime DateTime)"
    return create_and_populate_table(
        name=name,
        engine=engine,
        schema=schema,
        values=values,
        final_modifier_available=final_modifier_available,
        populate=populate,
        node=node,
        cluster_name=cluster_name,
    )


@TestStep(Given)
def create_and_populate_distributed_table(
    self,
    distributed_table_name,
    core_table_name,
    cluster_name,
    final_modifier_available,
    values,
    node=None,
    range_value=10,
):
    if node is None:
        node = current().context.node

    try:
        with By("I create distributed table over core table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {distributed_table_name} as {core_table_name} "
                f"ENGINE = Distributed"
                f"({cluster_name}, currentDatabase(), {core_table_name}) "
            )

        with And("populating table"):
            node.query("system stop merges")
            for i in range(range_value):
                node.query(
                    f"INSERT INTO {distributed_table_name} VALUES {values[0].format(i=i)}",
                    settings=[("insert_distributed_one_random_shard", 1)],
                )
                node.query(
                    f"INSERT INTO {distributed_table_name} VALUES {values[1].format(i=i)}",
                    settings=[("insert_distributed_one_random_shard", 1)],
                )

        yield Table(distributed_table_name, "Distributed", final_modifier_available)

    finally:
        with Finally(f"drop the table {distributed_table_name}"):
            node.query(f"DROP TABLE IF EXISTS {distributed_table_name}")


@TestStep(Given)
def create_and_populate_distributed_tables(self):
    """Create and populate all test tables for different table engines."""
    engines = [
        "ReplacingMergeTree",
        "ReplacingMergeTree({version})",
        "CollapsingMergeTree({sign})",
        "AggregatingMergeTree",
        "SummingMergeTree",
        "VersionedCollapsingMergeTree({sign},{version})",
        "MergeTree",
        "StripeLog",
        "TinyLog",
        "Log",
    ]

    clusters = ["replicated_cluster", "sharded_cluster"]

    for engine in engines:
        for cluster in clusters:
            with Given(f"{engine} table"):
                name = engine
                symbols = [("(", "_"), (",", "_"), (")", ""), ("{", ""), ("}", "")]
                for symbol in symbols:
                    name = name.replace(symbol[0], symbol[1])
                name = f"distr_{name}_table_{getuid()}" + cluster

                if engine.startswith("Replacing"):
                    values = [
                        "({i}, 'first', '2020-01-01 01:01:01')",
                        "({i}, 'second', '2020-01-01 00:00:00')",
                    ]
                    final_modifier_available = True

                    create_and_populate_replacing_table(
                        name=name, engine=engine, populate=False, cluster_name=cluster
                    )

                elif engine.startswith("Collapsing"):
                    values = [
                        "(4324182021466249494, {i}, 146, 1)",
                        "(4324182021466249494, {i}, 146, -1),"
                        "(4324182021466249494, {i}, 185, 1)",
                    ]
                    final_modifier_available = True

                    create_and_populate_collapsing_table(
                        name=name, engine=engine, populate=False, cluster_name=cluster
                    )

                elif engine.startswith("Aggregating"):
                    values = ["('a', {i}, 1)", "('a', {i}+1, 2)"]
                    final_modifier_available = True
                    create_and_populate_aggregating_table(
                        name=name, engine=engine, populate=False, cluster_name=cluster
                    )

                elif engine.startswith("Summing"):
                    values = [
                        "({i}, 'first', '2020-01-01 01:01:01')",
                        "({i}, 'second', '2020-01-01 00:00:00')",
                    ]
                    final_modifier_available = True
                    create_and_populate_summing_table(
                        name=name, engine=engine, populate=False, cluster_name=cluster
                    )

                elif engine.startswith("Merge"):
                    values = [
                        "({i}, 'first', '2020-01-01 01:01:01')",
                        "({i}, 'second', '2020-01-01 00:00:00')",
                    ]
                    final_modifier_available = False
                    create_and_populate_merge_table(
                        name=name, engine=engine, populate=False, cluster_name=cluster
                    )

                elif engine.startswith("Versioned"):
                    values = [
                        "({i}, 'first', 1, 1)",
                        "({i}, 'second', 1, 1),({i}+1, 'third', -1, 2)",
                    ]
                    final_modifier_available = True
                    create_and_populate_versioned_table(
                        name=name, engine=engine, populate=False, cluster_name=cluster
                    )
                elif (
                    engine.startswith("StripeLog")
                    or engine.startswith("TinyLog")
                    or engine.startswith("Log")
                ):
                    values = [
                        "({i}, 'first', '2020-01-01 01:01:01')",
                        "({i}, 'second', '2020-01-01 00:00:00')",
                    ]
                    final_modifier_available = True
                    create_and_populate_log_table(
                        name=name, engine=engine, populate=False, cluster_name=cluster
                    )

                self.context.tables.append(
                    create_and_populate_distributed_table(
                        distributed_table_name=name + "distributed",
                        core_table_name=name,
                        cluster_name=cluster,
                        final_modifier_available=final_modifier_available,
                        values=values,
                    )
                )
