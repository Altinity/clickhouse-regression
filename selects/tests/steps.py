import time
import random
import hashlib
from helpers.common import getuid
from testflows.core import *
from helpers.common import create_xml_config_content, add_config
from helpers.common import getuid, instrument_clickhouse_server_log


class Table:
    def __init__(self, name, engine, final_modifier_available):
        self.name = name
        self.engine = engine
        self.final_modifier_available = final_modifier_available


@TestStep(Given)
def create_and_populate_tables(self):
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
            self.context.tables.append(create_and_populate_table(engine=engine))


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
def create_and_populate_table(self, engine, name=None):
    """
    Create clickhouse table.

    :param name: core table name
    :param engine: core table engine
    :param schema: core table schema
    :param final_modifier_available: true if `FINAL` modifier available for engine
    """
    if name is None:
        name = engine
        symbols = [("(", "_"), (",", "_"), (")", ""), ("{", ""), ("}", "")]
        for symbol in symbols:
            name = name.replace(symbol[0], symbol[1])
        name = f"{name}_table_{getuid()}"

    if engine.startswith("Replacing"):
        return create_and_populate_replacing_table(
            name=name,
            engine=engine,
        )
    elif engine.startswith("Collapsing"):
        return create_and_populate_collapsing_table(
            name=name,
            engine=engine,
        )

    elif engine.startswith("Aggregating"):
        return create_and_populate_aggregating_table(
            name=name,
            engine=engine,
        )

    elif engine.startswith("Summing"):
        return create_and_populate_summing_table(
            name=name,
            engine=engine,
        )

    elif engine.startswith("Merge"):
        return create_and_populate_merge_table(
            name=name,
            engine=engine,
        )
    elif engine.startswith("Versioned"):
        return create_and_populate_versioned_table(name=name, engine=engine)
    elif engine.startswith("StripeLog"):
        return create_and_populate_stripelog_table(name=name, engine=engine)
    elif engine.startswith("TinyLog"):
        return create_and_populate_tinylog_table(name=name, engine=engine)
    elif engine.startswith("Log"):
        return create_and_populate_log_table(name=name, engine=engine)


@TestStep(Given)
def create_and_populate_replacing_table(
    self, name, final_modifier_available=True, engine="ReplacingMergeTree", node=None
):
    if node is None:
        node = current().context.node
    try:
        schema = "(key Int64, someCol String, eventTime DateTime)"

        engine = (
            engine.format(version="eventTime")
            if engine.endswith("({version})")
            else engine
        )

        with By(f"creating table {name}"):
            node.query(
                f"CREATE TABLE {name} {schema} " f"ENGINE = {engine} ORDER BY key;"
            )

        with And("populating table"):
            (
                node.query("system stop merges"),
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'first', '2020-01-01 01:01:01')"
                    )
                    for i in range(5)
                ],
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'second', '2020-01-01 00:00:00')"
                    )
                    for i in range(5)
                ],
            )

        yield Table(name, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep
def create_and_populate_collapsing_table(
    self,
    name,
    final_modifier_available=True,
    engine="CollapsingMergeTree",
    node=None,
):
    if node is None:
        node = current().context.node
    try:

        schema = "( key UInt64, PageViews UInt8, Duration UInt8, Sign Int8)"

        engine = engine.format(sign="Sign") if engine.endswith("({sign})") else engine

        with By(f"creating table {name}"):
            node.query(f"CREATE TABLE {name} {schema} ENGINE = {engine} ORDER BY key;")

        with And("populating table"):
            (
                node.query("system stop merges"),
                [
                    node.query(
                        f"INSERT INTO {name} VALUES (4324182021466249494, {i}, 146, 1)"
                    )
                    for i in range(5)
                ],
                [
                    node.query(
                        f"INSERT INTO {name} VALUES (4324182021466249494, {i}, 146, -1),"
                        f"(4324182021466249494, {i}, 185, 1)"
                    )
                    for i in range(5)
                ],
            )
        yield Table(name, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep
def create_and_populate_aggregating_table(
    self,
    name,
    final_modifier_available=True,
    engine="AggregatingMergeTree",
    node=None,
):
    if node is None:
        node = current().context.node
    try:

        schema = "(key String, b UInt8, c SimpleAggregateFunction(max, UInt8))"

        with By(f"creating table {name}"):
            node.query(f"CREATE TABLE {name} {schema} ENGINE = {engine} ORDER BY key;")

        with And("populating table"):
            (
                node.query("system stop merges"),
                [
                    node.query(f"INSERT INTO {name} VALUES ('a', {i}, 1);")
                    for i in range(5)
                ],
                [
                    node.query(f"INSERT INTO {name}  VALUES ('a', {i + 1}, 2);")
                    for i in range(5)
                ],
            )

        yield Table(name, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep
def create_and_populate_summing_table(
    self,
    name,
    final_modifier_available=True,
    engine="SummingMergeTree",
    node=None,
):
    if node is None:
        node = current().context.node
    try:
        schema = "(key Int64, someCol String, eventTime DateTime)"

        with By(f"creating table {name}"):
            node.query(
                f"CREATE TABLE {name} {schema} " f"ENGINE = {engine} ORDER BY key;"
            )

        with And("populating table"):
            (
                node.query("system stop merges"),
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'first', '2020-01-01 01:01:01')"
                    )
                    for i in range(5)
                ],
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'second', '2020-01-01 00:00:00')"
                    )
                    for i in range(5)
                ],
            )

        yield Table(name, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep
def create_and_populate_merge_table(
    self,
    name,
    final_modifier_available=False,
    engine="MergeTree",
    node=None,
):
    if node is None:
        node = current().context.node
    try:
        schema = "(key Int64, someCol String, eventTime DateTime)"

        with By(f"creating table {name}"):
            node.query(
                f"CREATE TABLE {name} {schema} " f"ENGINE = {engine} ORDER BY key;"
            )

        with And("populating table"):
            (
                node.query("system stop merges"),
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'first', '2020-01-01 01:01:01')"
                    )
                    for i in range(5)
                ],
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'second', '2020-01-01 00:00:00')"
                    )
                    for i in range(5)
                ],
            )
        yield Table(name, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep
def create_and_populate_versioned_table(
    self,
    name,
    final_modifier_available=True,
    engine="VersionedCollapsingMergeTree(sign,version)",
    node=None,
):
    if node is None:
        node = current().context.node
    try:
        schema = "(key Int64, someCol String, Sign Int8, version UInt8)"

        engine = (
            engine.format(sign="Sign", version="version")
            if engine.endswith("({sign},{version})")
            else engine
        )

        with By(f"creating table {name}"):
            node.query(
                f"CREATE TABLE {name} {schema} " f"ENGINE = {engine} ORDER BY key;"
            )

        with And("populating table"):
            (
                node.query("system stop merges"),
                [
                    node.query(f"INSERT INTO {name} VALUES ({i}, 'first', 1, 1)")
                    for i in range(5)
                ],
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'second', 1, 1),"
                        f"({i+1}, 'third', -1, 2)"
                    )
                    for i in range(5)
                ],
            )
        yield Table(name, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep
def create_and_populate_stripelog_table(
    self,
    name,
    final_modifier_available=False,
    engine="StripeLog",
    node=None,
):
    if node is None:
        node = current().context.node
    try:
        schema = "(key Int64, someCol String, eventTime DateTime)"

        with By(f"creating table {name}"):
            node.query(f"CREATE TABLE {name} {schema} " f"ENGINE = {engine};")

        with And("populating table"):
            (
                node.query("system stop merges"),
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'first', '2020-01-01 01:01:01')"
                    )
                    for i in range(5)
                ],
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'second', '2020-01-01 00:00:00')"
                    )
                    for i in range(5)
                ],
            )
        yield Table(name, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep
def create_and_populate_tinylog_table(
    self,
    name,
    final_modifier_available=False,
    engine="TinyLog",
    node=None,
):
    if node is None:
        node = current().context.node
    try:
        schema = "(key Int64, someCol String, eventTime DateTime)"

        with By(f"creating table {name}"):
            node.query(f"CREATE TABLE {name} {schema} " f"ENGINE = {engine};")

        with And("populating table"):
            (
                node.query("system stop merges"),
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'first', '2020-01-01 01:01:01')"
                    )
                    for i in range(5)
                ],
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'second', '2020-01-01 00:00:00')"
                    )
                    for i in range(5)
                ],
            )

        yield Table(name, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep
def create_and_populate_log_table(
    self,
    name,
    final_modifier_available=False,
    engine="Log",
    node=None,
):
    if node is None:
        node = current().context.node
    try:
        schema = "(key Int64, someCol String, eventTime DateTime)"

        with By(f"creating table {name}"):
            node.query(f"CREATE TABLE {name} {schema} " f"ENGINE = {engine};")

        with And("populating table"):
            (
                node.query("system stop merges"),
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'first', '2020-01-01 01:01:01')"
                    )
                    for i in range(5)
                ],
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'second', '2020-01-01 00:00:00')"
                    )
                    for i in range(5)
                ],
            )
        yield Table(name, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")
