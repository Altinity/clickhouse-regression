import time
import random
from helpers.common import getuid
from testflows.core import *
from helpers.common import create_xml_config_content, add_config
from helpers.common import getuid, instrument_clickhouse_server_log

engines = [
    "ReplacingMergeTree",
    "ReplicatedReplacingMergeTree" "ReplacingMergeTree({version})",
    "CollapsingMergeTree({sign})",
    "AggregatingMergeTree",
    "SummingMergeTree",
    "VersionedCollapsingMergeTree({sign},{version})",
    "MergeTree",
    "StripeLog",
    "TinyLog",
    "Log",
]


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
    Creating and populating clickhouse table.
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
            retry(node.query, timeout=100, delay=5,)(
                f"CREATE TABLE {name} "
                f"{' ON CLUSTER {cluster_name}'.format(cluster_name=cluster_name) if cluster_name is not None else ''}"
                f" {schema} "
                f"ENGINE = {engine} "
                f"{' ORDER BY key' if not engine.endswith('Log') else ''};",
                exitcode=0,
            )

        if populate:
            with And("populating table"):
                insert(table_name=name, values=values, range_value=range_value)

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
def create_and_populate_core_tables(self, duplicate=False):
    """Creating and populating core tables for different table engines.
    :param duplicate: if true create table with _duplicate flag in the end of name
    """
    for engine in engines:
        with Given(f"{engine} table"):
            name = engine
            symbols = [("(", "_"), (",", "_"), (")", ""), ("{", ""), ("}", "")]
            for symbol in symbols:
                name = name.replace(symbol[0], symbol[1])
            name = f"{name}_table_{getuid()}_core{'_duplicate' if duplicate else ''}"

            if engine.startswith("Replacing"):
                self.context.tables.append(
                    create_and_populate_replacing_table(
                        name=name,
                        engine=engine,
                    )
                )
                if not engine.endswith("({version})"):
                    self.context.tables.append(
                        create_and_populate_replacing_table(
                            name="Replicated" + name,
                            engine="Replicated"
                            + engine
                            + "('/clickhouse/tables/{shard}/{database}/"
                            + "{table_name}'".format(table_name="Replicated" + name)
                            + ", '{replica}')",
                        )
                    )
            elif engine.startswith("Collapsing"):
                self.context.tables.append(
                    create_and_populate_collapsing_table(
                        name=name,
                        engine=engine,
                    )
                )

            elif engine.startswith("ReplicatedCollapsing"):
                self.context.tables.append(
                    create_and_populate_collapsing_table(
                        name=name,
                        engine=engine
                        + "('/clickhouse/tables/{shard}/{database}/"
                        + f"{name}'"
                        + ", '{replica}')",
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
    """Adding system tables to tables list."""
    tables_list = [
        "system.users",
        "system.warnings",
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
    """
    Creating and populating 'ReplacingMergeTree' engine table.
    """
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
    """
    Creating and populating 'CollapsingMergeTree' engine table.
    """
    schema = "( key UInt64, someCol UInt8, Duration UInt8, Sign Int8)"

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
    """
    Creating and populating 'AggregatingMergeTree' engine table
    """
    schema = "(key String, someCol UInt8, c SimpleAggregateFunction(max, UInt8))"
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
    """
    Creating and populating 'SummingMergeTree' engine table.
    """
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
    """
    Creating and populating 'MergeTree' engine table.
    """
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
    """
    Creating and populating 'VersionedCollapsingMergeTree' engine table.
    """
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
    """
    Creating and populating 'Log' engine family table.
    """
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
    """
    Creating 'Distributed' engine table and populating dependent tables.
    """
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
            insert(
                table_name=distributed_table_name,
                values=values,
                range_value=range_value,
                distributed=True,
            )

        yield Table(distributed_table_name, "Distributed", final_modifier_available)

    finally:
        with Finally(f"drop the table {distributed_table_name}"):
            node.query(f"DROP TABLE IF EXISTS {distributed_table_name}")


@TestStep(When)
def insert(self, table_name, values, range_value, distributed=False, node=None):
    """Insert data having specified number of partitions and parts."""
    if node is None:
        node = current().context.node

    if distributed:
        node.query("system stop merges")
        for i in range(range_value):
            node.query(
                f"INSERT INTO {table_name} VALUES {values[0].format(i=i)}",
                settings=[("insert_distributed_one_random_shard", 1)],
            )
            node.query(
                f"INSERT INTO {table_name} VALUES {values[1].format(i=i)}",
                settings=[("insert_distributed_one_random_shard", 1)],
            )
    else:
        node.query("system stop merges")
        for i in range(range_value):
            node.query(f"INSERT INTO {table_name} VALUES {values[0].format(i=i)}")
            node.query(f"INSERT INTO {table_name} VALUES {values[1].format(i=i)}")


@TestStep(Given)
def create_and_populate_distributed_tables(self):
    """Creating and populating all 'Distributed' engine tables and populating dependent tables for different engines."""

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
                    final_modifier_available = False
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


@TestStep(Given)
def create_normal_view(self, core_table, final_modifier_available, node=None):
    """
    Creating `NORMAL VIEW` to some table.
    """
    if node is None:
        node = current().context.node

    view_type = "VIEW"
    view_name = core_table + "_nview"

    try:
        with By(f"creating normal view {view_name}"):
            node.query(
                f"CREATE {view_type} IF NOT EXISTS {view_name}"
                f" AS SELECT * FROM {core_table}",
            )
        yield Table(view_name, view_type, final_modifier_available)
    finally:
        with Finally("I drop data"):
            node.query(f"DROP VIEW IF EXISTS {view_name}")


@TestStep(Given)
def create_materialized_view(self, core_table, final_modifier_available, node=None):
    """
    Creating `MATERIALIZED VIEW` to some table.
    """
    if node is None:
        node = current().context.node

    view_type = "MATERIALIZED VIEW"
    view_name = core_table + "_mview"

    try:
        with By("create core table copy"):
            node.query(f"CREATE TABLE {core_table}_mcopy AS {core_table}")

        with And(f"creating materialized view {view_name}"):
            node.query(
                f"CREATE {view_type} IF NOT EXISTS {view_name}"
                f" TO {core_table}_mcopy"
                f" AS SELECT * FROM {core_table}",
            )

        yield Table(view_name, view_type, final_modifier_available)
    finally:
        with Finally("I drop data"):
            node.query(f"DROP VIEW IF EXISTS {view_name}")


@TestStep(Given)
def create_live_view(self, core_table, final_modifier_available, node=None):
    """
    Creating `LIVE VIEW` to some table.
    """
    if node is None:
        node = current().context.node

    view_type = "LIVE VIEW"
    view_name = core_table + "_lview"

    try:
        with By(f"creating live view {view_name}"):
            node.query(
                f"CREATE {view_type} IF NOT EXISTS {view_name}"
                f" AS SELECT * FROM {core_table}",
                settings=[("allow_experimental_live_view", 1)],
            )

        yield Table(view_name, view_type, final_modifier_available)
    finally:
        with Finally("I drop data"):
            node.query(f"DROP VIEW IF EXISTS {view_name}")


@TestStep(Given)
def create_window_view(self, core_table, final_modifier_available, node=None):
    """
    Creating `WINDOW VIEW` to some table.
    """
    if node is None:
        node = current().context.node

    view_type = "WINDOW VIEW"
    view_name = core_table + "_wview"

    try:
        with By("create core table copy"):
            node.query(
                f"CREATE TABLE {core_table}_windowcore (w_start DateTime, counter UInt64)"
                f" ENGINE=MergeTree ORDER BY w_start"
            )

        with And(f"creating window view {view_name}"):
            node.query(
                f"CREATE {view_type} IF NOT EXISTS {view_name}"
                f" TO {core_table}_windowcore"
                f" AS select tumbleStart(w_id) AS w_start, count(someCol) as counter FROM {core_table} "
                f"GROUP BY tumble(now(), INTERVAL '5' SECOND) as w_id",
                settings=[("allow_experimental_window_view", 1)],
            )

        yield Table(view_name, view_type, final_modifier_available)
    finally:
        with Finally("I drop data"):
            node.query(f"DROP VIEW IF EXISTS {view_name}")


@TestStep(Given)
def create_all_views(self):
    """
    Creating all types of 'VIEWS' to all core tables.
    """
    for table in self.context.tables:
        if not (
            table.name.startswith("system")
            or table.name.startswith("distr")
            or table.name.startswith("Replicated")
            or table.name.endswith("view")
        ):
            self.context.tables.append(
                create_normal_view(
                    core_table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )
            )

            self.context.tables.append(
                create_materialized_view(
                    core_table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )
            )

            self.context.tables.append(
                create_live_view(
                    core_table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )
            )
            self.context.tables.append(
                create_window_view(
                    core_table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )
            )


@TestStep(Given)
def create_and_populate_all_tables(self):
    """
    Creating all kind of tables.
    """
    create_and_populate_core_tables()
    add_system_tables()
    create_and_populate_distributed_tables()
    create_all_views()
