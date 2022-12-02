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
        self.schema = schema
        self.engine = engine
        self.final_modifier_available = final_modifier_available

    def insert_test_data(self, node=None):
        """Insert data into the specified table."""

        if node is None:
            node = current().context.node

        name = self.name


        elif self.engine.startswith("Collapsing"):
            return (
                [
                    node.query(
                        f"INSERT INTO {name} VALUES (4324182021466249494, {i}, 146, 1)"
                    )
                    for i in range(50)
                ],
                [
                    node.query(
                        f"INSERT INTO {name} VALUES (4324182021466249494, {i}, 146, -1),"
                        f"(4324182021466249494, {i}, 185, 1)"
                    )
                    for i in range(50)
                ],
            )
        elif self.engine.startswith("Aggregating"):
            return (
                [
                    node.query(f"INSERT INTO {name} VALUES ('a', {i}, 1);")
                    for i in range(50)
                ],
                [
                    node.query(f"INSERT INTO {name}  VALUES ('a', {i + 1}, 2);")
                    for i in range(50)
                ],
            )

        
@TestStep(Given)
def create_and_populate_tables(self):
    """Create and popualate all test tables for different table engines.
    """
    engines = [
        "ReplacingMergeTree",
        "ReplacingMergeTree({version})",
        "CollapsingMergeTree({sign})",
        "AggregatingMergeTree"
    ]
    for engine in engines:
        with Given(f"{engine} table"):
            self.context.tables.append(
                create_and_populate_table(engine=engine)
            )

            
@TestStep(Given)
def create_and_populate_table(self, engine, schema, name=None):
    """
    Create clickhouse table.

    :param name: core table name
    :param engine: core table engine
    :param schema: core table schema
    :param final_modifier_available: true if `FINAL` modifier available for engine
    """
    if name is None:
        # generate proper table name based on engine
        name = f"table_{getuid()}"

    if engine.startswith("Replacing"):
        return create_and_populate_replacing_table(
            name=name,
            schema=schema,
            final_modifier_available=final_modifier_available,
            engine=engine,
        )
    elif engine.startswith("Collapsing"):
        return create_and_populate_collapsing_table(
            name=name,
            schema=schema,
            final_modifier_available=final_modifier_available,
            engine=engine,
        )

    elif engine.startswith("Aggregating"):
        return create_and_populate_aggregating_table(
            name=name,
            schema=schema,
            final_modifier_available=final_modifier_available,
            engine=engine,
        )

    elif engine.startswith("Summing"):
        pass


@TestStep(Given)
def create_and_populate_replacing_table(
    self, name, final_modifier_available, engine="ReplacingMergeTree", node=None
):
    if node is None:
        node = current().context.node
    try:
        schema = "(key Int64, someCol String, eventTime DateTime)",
        
        with By(f"creating table {name}"):
            node.query(
                f"CREATE TABLE {name} {schema} " f"ENGINE = {engine} ORDER BY key;"
            )
        
        with And("populating table"):
            (
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'first', '2020-01-01 01:01:01')"
                    )
                    for i in range(50)
                ],
                [
                    node.query(
                        f"INSERT INTO {name} VALUES ({i}, 'second', '2020-01-01 00:00:00')"
                    )
                    for i in range(50)
                ],
            )
    
        yield Table(name, schema, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep
def create_collapsing_table(
    self,
    name,
    schema,
    final_modifier_available,
    engine="CollapsingMergeTree",
    node=None,
):
    if node is None:
        node = current().context.node
    try:
        with By(f"creating table {name}"):
            node.query(
                f"CREATE TABLE {name} {schema} " f"ENGINE = {engine} ORDER BY UserID;"
            )
        yield Table(name, schema, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep
def create_aggregating_table(
    self,
    name,
    schema,
    final_modifier_available,
    engine="AggregatingMergeTree",
    node=None,
):
    if node is None:
        node = current().context.node
    try:
        with By(f"creating table {name}"):
            node.query(
                f"CREATE TABLE {name} {schema} " f"ENGINE = {engine} ORDER BY a;"
            )
        yield Table(name, schema, engine, final_modifier_available)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")
