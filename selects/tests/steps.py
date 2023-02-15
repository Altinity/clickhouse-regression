import time
import random
from helpers.common import getuid
from testflows.core import *
from helpers.common import create_xml_config_content, add_config
from helpers.common import getuid, instrument_clickhouse_server_log

engines = [
    "Log",
    "MergeTree",
    "ReplacingMergeTree",
    "ReplicatedReplacingMergeTree",
    "ReplacingMergeTree({version})",
    "ReplicatedReplacingMergeTree({version})",
    "CollapsingMergeTree({sign})",
    "ReplicatedCollapsingMergeTree({sign})",
    "AggregatingMergeTree",
    "ReplicatedAggregatingMergeTree",
    "SummingMergeTree",
    "ReplicatedSummingMergeTree",
    "VersionedCollapsingMergeTree({sign},{version})",
    "ReplicatedVersionedCollapsingMergeTree({sign},{version})",
    "ReplicatedMergeTree",
    "StripeLog",
    "TinyLog",
]

join_types = [
    "INNER JOIN",
    "LEFT OUTER JOIN",
    "RIGHT OUTER JOIN",
    "FULL OUTER JOIN",
    "CROSS JOIN",
    "LEFT SEMI JOIN",
    "RIGHT SEMI JOIN",
    "LEFT ANTI JOIN",
    "RIGHT ANTI JOIN",
    "LEFT ANY JOIN",
    "RIGHT ANY JOIN",
    "INNER ANY JOIN",
    "ASOF JOIN",
    "LEFT ASOF JOIN",
]


@TestStep(Given)
def allow_experimental_analyzer(self):
    """Add allow_experimental_analyzer to the default query settings."""
    default_query_settings = getsattr(current().context, "default_query_settings", [])
    default_query_settings.append(("allow_experimental_analyzer", 1))


@TestStep(Given)
def create_and_populate_table(
    self,
    name,
    engine,
    final_modifier_available,
    extra_table_col="",
    cluster_name=None,
    values=None,
    populate=True,
    range_value=5,
    node=None,
):
    """Creating and populating clickhouse table.
    :param name: core table name
    :param populate: populates table default: True
    :param engine: core table engine
    :param extre_table_col: core table extre_table_col
    :param final_modifier_available: true if `FINAL` modifier available for engine
    """

    if node is None:
        node = current().context.node
    try:
        with By(f"creating table {name}"):
            retry(node.query, timeout=100, delay=5,)(
                f"CREATE TABLE {name} "
                f"{' ON CLUSTER {cluster_name}'.format(cluster_name=cluster_name) if cluster_name is not None else ''}"
                f"(id Int64, x Int64, {extra_table_col})"
                f"ENGINE = {engine}"
                f"{' PARTITION BY id' if not engine.endswith('Log') else ''}"
                f"{' ORDER BY id' if not engine.endswith('Log') else ''};",
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
    def __init__(
        self,
        name,
        engine,
        final_modifier_available,
        cluster=None,
    ):
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

            if engine.startswith("Replacing") or engine.startswith(
                "ReplicatedReplacing"
            ):
                self.context.tables.append(
                    create_and_populate_replacing_table(
                        name=name,
                        engine=engine,
                    )
                )

            elif engine.startswith("Collapsing") or engine.startswith(
                "ReplicatedCollapsing"
            ):
                self.context.tables.append(
                    create_and_populate_collapsing_table(
                        name=name,
                        engine=engine,
                    )
                )

            elif engine.startswith("Aggregating") or engine.startswith(
                "ReplicatedAggregating"
            ):
                self.context.tables.append(
                    create_and_populate_aggregating_table(
                        name=name,
                        engine=engine,
                    )
                )

            elif engine.startswith("Summing") or engine.startswith("ReplicatedSumming"):
                self.context.tables.append(
                    create_and_populate_summing_table(
                        name=name,
                        engine=engine,
                    )
                )

            elif engine.startswith("Merge") or engine.startswith("ReplicatedMerge"):
                self.context.tables.append(
                    create_and_populate_merge_table(
                        name=name,
                        engine=engine,
                    )
                )

            elif engine.startswith("Versioned") or engine.startswith(
                "ReplicatedVersioned"
            ):
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
    """Creating and populating 'ReplacingMergeTree' engine table."""
    if node is None:
        node = current().context.node

    extra_table_col = "key Int64, someCol String, eventTime DateTime"

    if engine.startswith("Replicated"):
        engine_local = (
            engine.format(
                version="'/clickhouse/tables/{shard}/{database}/"
                + f"{name}'"
                + ", '{replica}'"
                + ", eventTime"
            )
            if engine.endswith("({version})")
            else (
                engine
                + "('/clickhouse/tables/{shard}/{database}/"
                + f"{name}'"
                + ", '{replica}')"
            )
        )
    else:
        engine_local = (
            engine.format(version="eventTime")
            if engine.endswith("{version})")
            else engine
        )

    values = [
        "({x},{y}, 1, 'first', '2020-01-01 01:01:01')",
        "({x},{y}, 1, 'second', '2020-01-01 00:00:00')",
    ]

    return create_and_populate_table(
        name=name,
        engine=engine_local,
        extra_table_col=extra_table_col,
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
    """Creating and populating 'CollapsingMergeTree' engine table."""
    extra_table_col = "key UInt64, someCol UInt8, Duration UInt8, Sign Int8"

    if engine.startswith("Replicated"):
        engine_local = (
            engine.format(
                sign="'/clickhouse/tables/{shard}/{database}/"
                + f"{name}'"
                + ", '{replica}'"
                + ", Sign"
            )
            if engine.endswith("({sign})")
            else (
                engine
                + "('/clickhouse/tables/{shard}/{database}/"
                + f"{name}'"
                + ", '{replica}')"
            )
        )
    else:
        engine_local = (
            engine.format(sign="Sign") if engine.endswith("({sign})") else engine
        )

    values = [
        "({x},{y},4324182021466249494, 1, 146, 1)",
        "({x},{y},4324182021466249494, 1, 146, -1), ({x},{y},4324182021466249494, 1, 185, 1)",
    ]

    return create_and_populate_table(
        name=name,
        engine=engine_local,
        extra_table_col=extra_table_col,
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
    """Creating and populating 'AggregatingMergeTree' engine table."""
    if engine.startswith("Replicated"):
        engine = (
            engine
            + "('/clickhouse/tables/{shard}/{database}/"
            + f"{name}'"
            + ", '{replica}')"
        )
    extra_table_col = "key String, someCol UInt8, c SimpleAggregateFunction(max, UInt8)"
    values = ["({x},{y},'a', 1, 1)", "({x},{y},'a', 2, 2)"]
    return create_and_populate_table(
        name=name,
        engine=engine,
        extra_table_col=extra_table_col,
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
    """Creating and populating 'SummingMergeTree' engine table."""
    if engine.startswith("Replicated"):
        engine = (
            engine
            + "('/clickhouse/tables/{shard}/{database}/"
            + f"{name}'"
            + ", '{replica}')"
        )
    extra_table_col = "key Int64, someCol String, eventTime DateTime"
    values = [
        "({x},{y}, 1, 'first', '2020-01-01 01:01:01')",
        "({x},{y}, 2, 'second', '2020-01-01 00:00:00')",
    ]

    return create_and_populate_table(
        name=name,
        engine=engine,
        extra_table_col=extra_table_col,
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
    """Creating and populating 'MergeTree' engine table."""

    if engine.startswith("Replicated"):
        engine = (
            engine
            + "('/clickhouse/tables/{shard}/{database}/"
            + f"{name}'"
            + ", '{replica}')"
        )
    values = [
        "({x},{y}, 1, 'first', '2020-01-01 01:01:01')",
        "({x},{y}, 1, 'second', '2020-01-01 00:00:00')",
    ]
    extra_table_col = "key Int64, someCol String, eventTime DateTime"
    return create_and_populate_table(
        name=name,
        engine=engine,
        extra_table_col=extra_table_col,
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
    """Creating and populating 'VersionedCollapsingMergeTree' engine table."""

    values = [
        "({x},{y}, 1, 'first', 1, 1)",
        "({x},{y}, 1, 'second', 1, 1),({x},{y}, 2, 'third', -1, 2)",
    ]
    extra_table_col = "key Int64, someCol String, Sign Int8, version UInt8"

    if engine.startswith("Replicated"):
        engine_local = (
            engine.format(
                sign="'/clickhouse/tables/{shard}/{database}/"
                + f"{name}'"
                + ", '{replica}'"
                + ", Sign",
                version="version",
            )
            if engine.endswith("({sign},{version})")
            else (
                engine
                + "('/clickhouse/tables/{shard}/{database}/"
                + f"{name}'"
                + ", '{replica}')"
            )
        )
    else:
        engine_local = (
            engine.format(sign="Sign", version="version")
            if engine.endswith("({sign},{version})")
            else engine
        )

    return create_and_populate_table(
        name=name,
        engine=engine_local,
        extra_table_col=extra_table_col,
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
    """Creating and populating 'Log' engine family table."""

    values = [
        "({x},{y},1, 'first', '2020-01-01 01:01:01')",
        "({x},{y},1, 'second', '2020-01-01 00:00:00')",
    ]

    extra_table_col = "key Int64, someCol String, eventTime DateTime"

    return create_and_populate_table(
        name=name,
        engine=engine,
        extra_table_col=extra_table_col,
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
    """Creating 'Distributed' engine table and populating dependent tables."""
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


@TestStep(Given)
def create_and_populate_distributed_tables(self):
    """Creating and populating all 'Distributed' engine tables and populating dependent tables for different engines."""

    clusters = ["replicated_cluster", "sharded_cluster"]

    for engine in engines:
        if not engine.startswith("Replicated"):
            for cluster in clusters:
                with Given(f"{engine} table"):
                    name = engine
                    symbols = [("(", "_"), (",", "_"), (")", ""), ("{", ""), ("}", "")]
                    for symbol in symbols:
                        name = name.replace(symbol[0], symbol[1])
                    name = f"distr_{name}_table_{getuid()}" + cluster

                    if engine.startswith("Replacing"):
                        values = [
                            "({x},{y}, 1, 'first', '2020-01-01 01:01:01')",
                            "({x},{y}, 1, 'second', '2020-01-01 00:00:00')",
                        ]
                        final_modifier_available = True

                        create_and_populate_replacing_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                        )

                    elif engine.startswith("Collapsing"):
                        values = [
                            "({x},{y}, 4324182021466249494, 1, 146, 1)",
                            "({x},{y}, 4324182021466249494, 1, 146, -1),"
                            "({x},{y},4324182021466249494, 1, 185, 1)",
                        ]
                        final_modifier_available = True

                        create_and_populate_collapsing_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                        )

                    elif engine.startswith("Aggregating"):
                        values = ["({x},{y},'a', 1, 1)", "({x},{y},'a', 2, 2)"]
                        final_modifier_available = True
                        create_and_populate_aggregating_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                        )

                    elif engine.startswith("Summing"):
                        values = [
                            "({x},{y}, 1, 'first', '2020-01-01 01:01:01')",
                            "({x},{y}, 1, 'second', '2020-01-01 00:00:00')",
                        ]
                        final_modifier_available = True
                        create_and_populate_summing_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                        )

                    elif engine.startswith("Merge"):
                        values = [
                            "({x},{y}, 1, 'first', '2020-01-01 01:01:01')",
                            "({x},{y}, 1, 'second', '2020-01-01 00:00:00')",
                        ]
                        final_modifier_available = False
                        create_and_populate_merge_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                        )

                    elif engine.startswith("Versioned"):
                        values = [
                            "({x},{y}, 1, 'first', 1, 1)",
                            "({x},{y}, 1, 'second', 1, 1),({x},{y}, 2, 'third', -1, 2)",
                        ]
                        final_modifier_available = True
                        create_and_populate_versioned_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                        )

                    elif (
                        engine.startswith("StripeLog")
                        or engine.startswith("TinyLog")
                        or engine.startswith("Log")
                    ):
                        values = [
                            "({x},{y}, 1, 'first', '2020-01-01 01:01:01')",
                            "({x},{y}, 1, 'second', '2020-01-01 00:00:00')",
                        ]
                        final_modifier_available = False
                        create_and_populate_log_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
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
def create_normal_view(
    self,
    core_table,
    final_modifier_available,
    final=False,
    node=None,
    view_not_final=False,
):
    """Creating `NORMAL VIEW` to some table."""

    if node is None:
        node = current().context.node

    view_type = "VIEW"
    view_name = core_table + f"_nview{'_final' if final else ''}"

    try:
        with By(f"creating normal view {view_name}"):
            node.query(
                f"CREATE {view_type} IF NOT EXISTS {view_name}"
                f" AS SELECT * FROM {core_table}{' FINAL' if final and final_modifier_available else ''}",
            )
        yield Table(view_name, view_type, final_modifier_available)
    finally:
        with Finally("I drop data"):
            node.query(f"DROP VIEW IF EXISTS {view_name}")


@TestStep(Given)
def create_materialized_view(
    self,
    core_table,
    final_modifier_available,
    final=False,
    node=None,
    view_not_final=False,
):
    """Creating `MATERIALIZED VIEW` to some table."""

    if node is None:
        node = current().context.node

    view_type = "MATERIALIZED VIEW"
    view_name = core_table + f"_mview"

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
            node.query(f"DROP TABLE IF EXISTS {core_table}_mcopy")


@TestStep(Given)
def create_live_view(
    self,
    core_table,
    final_modifier_available,
    final=False,
    node=None,
    view_not_final=False,
):
    """Creating `LIVE VIEW` to some table."""

    if node is None:
        node = current().context.node

    view_type = "LIVE VIEW"
    view_name = core_table + f"_lview{'_final' if final else ''}"

    try:
        with By(f"creating live view {view_name}"):
            node.query(
                f"CREATE {view_type} IF NOT EXISTS {view_name}"
                f" AS SELECT * FROM {core_table}{' FINAL' if final  and final_modifier_available else ''}",
                settings=[("allow_experimental_live_view", 1)],
            )

        yield Table(view_name, view_type, final_modifier_available)
    finally:
        with Finally("I drop data"):
            node.query(f"DROP VIEW IF EXISTS {view_name}")


@TestStep(Given)
def create_window_view(
    self,
    core_table,
    final_modifier_available,
    final=False,
    node=None,
    view_not_final=False,
):
    """Creating `WINDOW VIEW` to some table."""

    if node is None:
        node = current().context.node

    view_type = "WINDOW VIEW"
    view_name = core_table + f"_wview{'_final' if final else ''}"

    try:
        with By("create core table copy"):
            node.query(
                f"CREATE TABLE {core_table}_windowcore{'_final' if final else ''} (w_start DateTime, counter UInt64)"
                f" ENGINE=MergeTree ORDER BY w_start"
            )

        with And(f"creating window view {view_name}"):
            node.query(
                f"CREATE {view_type} IF NOT EXISTS {view_name}"
                f" TO {core_table}_windowcore{'_final' if final else ''}"
                f" AS select tumbleStart(w_id) AS w_start, count(someCol) as counter FROM {core_table}"
                f"{' FINAL' if final else ''}"
                f" GROUP BY tumble(now(), INTERVAL '5' SECOND) as w_id",
                settings=[("allow_experimental_window_view", 1)],
            )

        yield Table(view_name, view_type, final_modifier_available)

    finally:
        with Finally("I drop data"):
            node.query(f"DROP VIEW IF EXISTS {view_name}")
            node.query(
                f"DROP TABLE IF EXISTS {core_table}_windowcore{'_final' if final else ''}"
            )


@TestStep(Given)
def create_all_views(self):
    """Creating all types of 'VIEWS' to all core tables."""

    for table in self.context.tables:
        if not (
            table.name.startswith("system")
            or table.name.startswith("expr_subquery")
            or table.name.startswith("distr")
            or table.name.startswith("Replicated")
            or table.name.endswith("view")
            or table.name.endswith("final")
        ):
            self.context.tables.append(
                create_normal_view(
                    core_table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )
            )

            self.context.tables.append(
                create_normal_view(
                    core_table=table.name,
                    final_modifier_available=table.final_modifier_available,
                    final=True,
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
                create_live_view(
                    core_table=table.name,
                    final_modifier_available=table.final_modifier_available,
                    final=True,
                )
            )

            if table.final_modifier_available:
                self.context.tables.append(
                    create_window_view(
                        core_table=table.name,
                        final_modifier_available=table.final_modifier_available,
                        final=True,
                    )
                )


@TestStep(Given)
def create_normal_view_with_join(self, node=None, final1=None, final2=None):
    """Creating `NORMAL VIEW` as `SELECT` with `JOIN` clause."""

    if node is None:
        node = current().context.node

    try:
        with By(f"creating normal view with stored select join"):
            for table in self.context.tables:
                if table.name.endswith("core"):
                    for table2 in self.context.tables:
                        if table2.name.endswith("duplicate") and table2.name.startswith(
                            table.engine
                        ):
                            view_name = (
                                table.name
                                + f"_nview_join{'_final' if table.final_modifier_available else ''}"
                            )
                            if final1 is None:
                                final1 = table.final_modifier_available
                            if final2 is None:
                                final2 = table2.final_modifier_available

                            node.query(
                                f"CREATE VIEW IF NOT EXISTS {view_name} AS "
                                f"SELECT * FROM {table.name} a"
                                f"{' FINAL' if final1 else ''}"
                                f" JOIN "
                                f"(SELECT * FROM {table2.name}"
                                f"{' FINAL' if final2 else ''}) b on"
                                f" a.id = b.id"
                                f" ORDER BY id",
                                settings=[("joined_subquery_requires_alias", 0)],
                            )

        yield Table(view_name, "VIEW", table.final_modifier_available)

    finally:
        with Finally("I drop data"):
            node.query(f"DROP VIEW IF EXISTS {view_name}")


@TestStep(Given)
def create_replicated_table_2shards3replicas(self, node=None):
    """Creating distributed table to replicated table on cluster with 2 shards and 2 replicas on one shard."""
    if node is None:
        node = current().context.node

    clusters = ["sharded_replicated_cluster"]

    for engine in engines:
        if engine.startswith("Replicated"):
            for cluster in clusters:
                with Given(f"{engine} table"):
                    name = engine
                    symbols = [("(", "_"), (",", "_"), (")", ""), ("{", ""), ("}", "")]
                    for symbol in symbols:
                        name = name.replace(symbol[0], symbol[1])
                    name = f"distr_{name}_table_{getuid()}" + cluster

                    if engine.startswith("ReplicatedReplacing"):
                        values = [
                            "({x},{y}, 1, 'first', '2020-01-01 01:01:01')",
                            "({x},{y}, 1, 'second', '2020-01-01 00:00:00')",
                        ]
                        final_modifier_available = True

                        create_and_populate_replacing_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                            final_modifier_available=final_modifier_available,
                        )

                    elif engine.startswith("ReplicatedCollapsing"):
                        values = [
                            "({x},{y}, 4324182021466249494, 1, 146, 1)",
                            "({x},{y}, 4324182021466249494, 1, 146, -1),"
                            "({x},{y},4324182021466249494, 1, 185, 1)",
                        ]
                        final_modifier_available = True

                        create_and_populate_collapsing_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                            final_modifier_available=final_modifier_available,
                        )

                    elif engine.startswith("ReplicatedAggregating"):
                        values = ["({x},{y},'a', 1, 1)", "({x},{y},'a', 2, 2)"]
                        final_modifier_available = True
                        create_and_populate_aggregating_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                            final_modifier_available=final_modifier_available,
                        )

                    elif engine.startswith("ReplicatedSumming"):
                        values = [
                            "({x},{y}, 1, 'first', '2020-01-01 01:01:01')",
                            "({x},{y}, 1, 'second', '2020-01-01 00:00:00')",
                        ]
                        final_modifier_available = True
                        create_and_populate_summing_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                            final_modifier_available=final_modifier_available,
                        )

                    elif engine.startswith("ReplicatedMerge"):
                        values = [
                            "({x},{y}, 1, 'first', '2020-01-01 01:01:01')",
                            "({x},{y}, 1, 'second', '2020-01-01 00:00:00')",
                        ]
                        final_modifier_available = False
                        create_and_populate_merge_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                            final_modifier_available=final_modifier_available,
                        )

                    elif engine.startswith("ReplicatedVersioned"):
                        values = [
                            "({x},{y}, 1, 'first', 1, 1)",
                            "({x},{y}, 1, 'second', 1, 1),({x},{y}, 2, 'third', -1, 2)",
                        ]
                        final_modifier_available = True
                        create_and_populate_versioned_table(
                            name=name,
                            engine=engine,
                            populate=False,
                            cluster_name=cluster,
                            final_modifier_available=final_modifier_available,
                        )

                    self.context.tables.append(
                        create_and_populate_distributed_table(
                            distributed_table_name=name + "distributed_replicated",
                            core_table_name=name,
                            cluster_name=cluster,
                            final_modifier_available=final_modifier_available,
                            values=values,
                        )
                    )


@TestStep(Given)
def create_expression_subquery_table(self, node=None):
    """Creating table for expressions with subquery."""

    name = f"expr_subquery_{getuid()}"
    table_statement = """
                        CREATE TABLE {name}
                    (
                        x Int32,
                        arr Array(UInt8)
                    )
                    ENGINE = ReplacingMergeTree
                    ORDER BY x"""

    if node is None:
        node = current().context.node

    try:
        with Given("I create simple table with integer and array columns"):
            node.query(table_statement.format(name=name))

        with Then("I insert few equal raws in it with stopped merges"):
            node.query("system stop merges")
            for i in range(3):
                node.query(f"INSERT INTO {name} VALUES (1, [1]);")

        yield self.context.tables.append(Table(name, "ReplacingMergeTree", True))

    finally:
        with Finally("I drop data"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep(Then)
def assert_joins(self, join_statement, table, table2, join_type, node=None):
    """ "Check `SELECT ... FINAL` equal to `SELECT` with force_select_final for all cases of using FINAL with JOINs."""

    if node is None:
        node = current().context.node

    with When("I execute query with FINAL modifier specified explicitly"):
        explicit_final = node.query(
            join_statement,
            settings=[("joined_subquery_requires_alias", 0)],
        ).output.strip()

    with And(
        "I execute the same query without FINAL modifiers and with force_select_final=1 setting"
    ):
        force_select_final_without = node.query(
            f"SELECT count() FROM {table.name} {join_type}"
            f" {table2.name} on {table.name}.id = {table2.name}.id",
            settings=[("final", 1)],
        ).output.strip()

    with And(
        "I execute the same query with `FINAL` clause on left table and with force_select_final=1 setting"
    ):
        force_select_final_left = node.query(
            f"SELECT count() FROM {table.name} "
            f"{' FINAL' if table.final_modifier_available else ''} {join_type}"
            f" {table2.name} on {table.name}.id = {table2.name}.id",
            settings=[("final", 1)],
        ).output.strip()

    with And(
        "I execute the same query with `FINAL` clause on right table and with force_select_final=1 setting"
    ):
        force_select_final_right = node.query(
            f"SELECT count() FROM {table.name} {join_type}"
            f" {table2.name} {' FINAL' if table2.final_modifier_available else ''} on {table.name}.id = {table2.name}.id",
            settings=[("final", 1)],
        ).output.strip()

    with And(
        "I execute the same query with `FINAL` clause on both tables and with force_select_final=1 setting"
    ):
        force_select_final_double = node.query(
            f"SELECT count() FROM {table.name} {' FINAL' if table.final_modifier_available else ''} {join_type}"
            f" {table2.name} {' FINAL' if table2.final_modifier_available else ''} on {table.name}.id = {table2.name}.id",
            settings=[("final", 1)],
        ).output.strip()

    with Then("I compare results are the same"):
        assert explicit_final == force_select_final_without
        assert explicit_final == force_select_final_left
        assert explicit_final == force_select_final_right
        assert explicit_final == force_select_final_double


@TestStep(When)
def insert(
    self,
    table_name,
    values,
    range_value,
    distributed=False,
    node=None,
    partitions=2,
    parts_per_partition=2,
    block_size=2,
):
    """Insert data having specified number of partitions and parts."""
    if node is None:
        node = current().context.node

        insert_values_1 = ",".join(
            f"{values[0]}".format(x=x, y=y)
            for x in range(partitions)
            for y in range(block_size * parts_per_partition)
        )
        insert_values_2 = ",".join(
            f"{values[1]}".format(x=x, y=y)
            for x in range(partitions)
            for y in range(block_size * parts_per_partition)
        )

        if distributed:
            node.query("system stop merges")
            for i in range(range_value):
                node.query(
                    f"INSERT INTO {table_name} VALUES {insert_values_1}",
                    settings=[
                        ("insert_distributed_one_random_shard", 1),
                        ("max_block_size", block_size),
                    ],
                )
                node.query(
                    f"INSERT INTO {table_name} VALUES {insert_values_2}",
                    settings=[
                        ("insert_distributed_one_random_shard", 1),
                        ("max_block_size", block_size),
                    ],
                )
        else:
            node.query("system stop merges")
            node.query(
                f"INSERT INTO {table_name} VALUES {insert_values_1}",
                settings=[("max_block_size", block_size)],
            )
            node.query(
                f"INSERT INTO {table_name} VALUES {insert_values_2}",
                settings=[("max_block_size", block_size)],
            )


@TestStep(Given)
def create_and_populate_all_tables(self):
    """Create all kind of tables."""
    create_and_populate_core_tables()
    # add_system_tables()
    # create_and_populate_distributed_tables()
    # create_all_views()
    # create_and_populate_core_tables(duplicate=True)
    # create_normal_view_with_join()
    # create_replicated_table_2shards3replicas()
    # create_expression_subquery_table()


@TestStep(When)
def simple_select(self, statement, name, final_manual, final=0, node=None):
    """Select query step."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make select from table"):
        node.query(
            f"{statement}".format(name=name, final=final_manual),
            settings=[("final", final)],
        )


@TestStep(When)
def simple_insert(self, first_insert_id, last_insert_id, table_name):
    """
    Insert query step
    :param self:
    :param first_delete_id:
    :param last_delete_id:
    :param table_name:
    :return:
    """
    node = self.context.cluster.node("clickhouse1")

    with When(f"I insert {first_insert_id - last_insert_id} rows of data"):
        for i in range(first_insert_id, last_insert_id):
            node.query(
                f"INSERT INTO {table_name} VALUES ({i},777, 77{i}, 'ivan', '2019-01-01 00:00:00')"
            )


@TestStep(When)
def delete(self, first_delete_id, last_delete_id, table_name):
    """
    Delete query step
    :param self:
    :param first_delete_id:
    :param last_delete_id:
    :param table_name:
    :return:
    """
    node = self.context.cluster.node("clickhouse1")

    with When(f"I delete {last_delete_id - first_delete_id} rows of data"):
        for i in range(first_delete_id, last_delete_id):
            node.query(f"ALTER TABLE {table_name} DELETE WHERE id={i}")


@TestStep(When)
def update(self, first_update_id, last_update_id, table_name):
    """
    Update query step
    :param self:
    :param first_update_id:
    :param last_update_id:
    :param table_name:
    :return:
    """
    node = self.context.cluster.node("clickhouse1")

    with When(f"I update {last_update_id - first_update_id} rows of data"):
        for i in range(first_update_id, last_update_id):
            node.query(f"ALTER TABLE {table_name} UPDATE x=x+5 WHERE id={i};")


@TestStep(When)
def concurrent_queries(
    self,
    statement,
    parallel_runs=1,
    parallel_selects=0,
    parallel_inserts=0,
    parallel_deletes=0,
    parallel_updates=0,
    final=0,
    final_manual="",
    table_name=None,
    node=None,
    first_insert_id=None,
    last_insert_id=None,
    first_delete_id=None,
    last_delete_id=None,
    first_update_id=None,
    last_update_id=None,
):
    """
    Run concurrent select queries with optional parallel insert, update, and delete.

    :param self:
    :param table_name: table name
    :param first_insert_number: first id of precondition insert
    :param last_insert_number:  last id of precondition insert
    :param first_insert_id: first id of concurrent insert
    :param last_insert_id: last id of concurrent insert
    :param first_delete_id: first id of concurrent delete
    :param last_delete_id: last id of concurrent delete
    :param first_update_id: first id of concurrent update
    :param last_update_id: last id of concurrent update
    :return:
    """
    for i in range(parallel_runs):
        if parallel_selects > 0:
            for i in range(parallel_selects):
                By("selecting data", test=simple_select, parallel=True)(
                    statement=statement,
                    name=table_name,
                    final_manual=final_manual,
                    final=final,
                    node=node,
                )

        if parallel_inserts > 0:
            for i in range(parallel_inserts):
                By("inserting data", test=simple_insert, parallel=True)(
                    first_insert_id=first_insert_id,
                    last_insert_id=last_insert_id,
                    table_name=table_name,
                )

        if parallel_deletes > 0:
            for i in range(parallel_deletes):
                By("deleting data", test=delete, parallel=True,)(
                    first_delete_id=first_delete_id,
                    last_delete_id=last_delete_id,
                    table_name=table_name,
                )

        if parallel_updates > 0:
            for i in range(parallel_updates):
                By("updating data", test=update, parallel=True,)(
                    first_update_id=first_update_id,
                    last_update_id=last_update_id,
                    table_name=table_name,
                )
