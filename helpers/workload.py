"""Background workload simulator for ClickHouse nodes.

Generates realistic activity (DDL, DML, queries) on a node so tests can run
against a busy server instead of an idle one.

Typical use is the ``background_workload`` context manager, which starts the
workload and then stops and cleans it up on exit::

    with background_workload(node, intensity="medium"):
        ...  # test logic runs while the server is under load

Action groups can be toggled independently via ``enable_*`` flags (all default
True): ``enable_creates``, ``enable_inserts``, ``enable_selects``,
``enable_alters``, ``enable_drops``, ``enable_system``.
"""

import random
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import Event
from typing import Callable, Dict, List, Optional

from testflows.core import *

from helpers.common import getuid
from helpers.alter import (
    alter_table_add_column,
    alter_table_drop_column,
    alter_table_rename_column,
    alter_table_update_column,
    alter_table_delete_rows,
)


# --- State ---


@dataclass
class WorkloadState:
    """Objects created by the workload, used to check action preconditions."""

    tables: Dict[str, List[dict]] = field(default_factory=dict)
    rows_inserted: Dict[str, int] = field(default_factory=dict)
    views: List[str] = field(default_factory=list)
    uid: str = field(default_factory=getuid)

    def has_tables(self):
        return len(self.tables) > 0

    def has_rows(self):
        return any(count > 0 for count in self.rows_inserted.values())

    def pick_table(self):
        return random.choice(list(self.tables.keys()))

    def pick_table_with_rows(self):
        candidates = [t for t, c in self.rows_inserted.items() if c > 0]
        return random.choice(candidates) if candidates else None

    def table_prefix(self):
        return f"workload_{self.uid}_"

@dataclass
class Action:
    name: str
    func: Callable
    group: str
    preconditions: List[str]


ACTION_REGISTRY: Dict[str, Action] = {}

GROUP_FLAGS = {
    "create": "enable_creates",
    "insert": "enable_inserts",
    "select": "enable_selects",
    "alter": "enable_alters",
    "drop": "enable_drops",
    "system": "enable_system",
}


def action(name, group, preconditions=()):
    """Register an action implementation under the given name and group."""

    def register(func):
        ACTION_REGISTRY[name] = Action(
            name=name, func=func, group=group, preconditions=list(preconditions)
        )
        return func

    return register


INTENSITY_PROFILES = {
    "low": {"repeat_min": 1, "repeat_max": 3, "delay": 1.0},
    "medium": {"repeat_min": 3, "repeat_max": 10, "delay": 0.2},
    "high": {"repeat_min": 5, "repeat_max": 20, "delay": 0.05},
}


def _repeat_count(profile):
    return random.randint(profile["repeat_min"], profile["repeat_max"])


COLUMN_TYPES = [
    "UInt8",
    "UInt16",
    "UInt32",
    "UInt64",
    "Int8",
    "Int16",
    "Int32",
    "Int64",
    "Float32",
    "Float64",
    "String",
    "DateTime",
]


def _cluster_clause(cluster):
    return f" ON CLUSTER '{cluster}'" if cluster else ""


def _generate_row_value(col_type):
    """Random literal value for a given ClickHouse type."""
    if col_type.startswith(("UInt", "Int")):
        return str(random.randint(0, 100000))
    if col_type.startswith("Float"):
        return str(round(random.uniform(0, 100000), 2))
    if col_type == "String":
        return f"'row_{random.randint(0, 999999)}'"
    if col_type == "DateTime":
        return f"toDateTime({random.randint(1600000000, 1700000000)})"
    return "0"


def _numeric_columns(columns, include_id=False):
    return [
        c
        for c in columns
        if c["type"].startswith(("UInt", "Int", "Float"))
        and (include_id or c["name"] != "id")
    ]

@action("create_table", group="create")
def _action_create_table(node, state, cluster=None, **kwargs):
    """Create a MergeTree table with random columns."""
    table_name = f"{state.table_prefix()}t{len(state.tables)}_{random.randint(0, 9999)}"
    columns = [{"name": "id", "type": "UInt64"}]
    for i in range(random.randint(2, 6)):
        columns.append({"name": f"col{i}", "type": random.choice(COLUMN_TYPES)})

    col_defs = ", ".join(f"{c['name']} {c['type']}" for c in columns)
    with By(f"creating table {table_name}"):
        node.query(
            f"CREATE TABLE IF NOT EXISTS {table_name}{_cluster_clause(cluster)} "
            f"({col_defs}) ENGINE = MergeTree() ORDER BY id",
            no_checks=True,
            steps=False,
        )
    state.tables[table_name] = columns
    state.rows_inserted[table_name] = 0


@action("create_mv", group="create", preconditions=["table_exists"])
def _action_create_mv(node, state, cluster=None, **kwargs):
    """Create a materialized view over a managed table."""
    table_name = state.pick_table()
    mv_name = f"{table_name}_mv_{random.randint(0, 9999)}"
    with By(f"creating materialized view {mv_name}"):
        node.query(
            f"CREATE MATERIALIZED VIEW IF NOT EXISTS {mv_name}{_cluster_clause(cluster)} "
            f"ENGINE = MergeTree() ORDER BY id "
            f"AS SELECT id, count() as cnt FROM {table_name} GROUP BY id",
            no_checks=True,
            steps=False,
        )
    state.views.append(mv_name)

@action("insert_batch", group="insert", preconditions=["table_exists"])
def _action_insert_batch(node, state, **kwargs):
    """Insert a batch of random rows into a managed table."""
    table_name = state.pick_table()
    columns = state.tables[table_name]
    col_names = ", ".join(c["name"] for c in columns)

    num_rows = random.randint(100, 1000)
    rows = [
        f"({', '.join(_generate_row_value(c['type']) for c in columns)})"
        for _ in range(num_rows)
    ]

    batch_size = 100
    with By(f"inserting {num_rows} rows into {table_name}"):
        for i in range(0, len(rows), batch_size):
            chunk = rows[i : i + batch_size]
            node.query(
                f"INSERT INTO {table_name} ({col_names}) VALUES {', '.join(chunk)}",
                no_checks=True,
                steps=False,
            )
    state.rows_inserted[table_name] = state.rows_inserted.get(table_name, 0) + num_rows


@action("add_column", group="alter", preconditions=["table_exists"])
def _action_add_column(node, state, **kwargs):
    """Add a random column to a managed table."""
    table_name = state.pick_table()
    col_name = f"col_added_{random.randint(0, 99999)}"
    col_type = random.choice(COLUMN_TYPES)
    alter_table_add_column(
        table_name=table_name,
        column_name=col_name,
        column_type=col_type,
        node=node,
        if_not_exists=True,
        no_checks=True,
        steps=False,
    )
    state.tables[table_name].append({"name": col_name, "type": col_type})


@action("drop_column", group="alter", preconditions=["table_exists"])
def _action_drop_column(node, state, **kwargs):
    """Drop a non-pk column from a managed table."""
    table_name = state.pick_table()
    non_pk_cols = [c for c in state.tables[table_name] if c["name"] != "id"]
    if len(non_pk_cols) <= 1:
        return
    col = random.choice(non_pk_cols)
    alter_table_drop_column(
        table_name=table_name,
        column_name=col["name"],
        node=node,
        no_checks=True,
        steps=False,
    )
    state.tables[table_name] = [
        c for c in state.tables[table_name] if c["name"] != col["name"]
    ]


@action("rename_column", group="alter", preconditions=["table_exists"])
def _action_rename_column(node, state, **kwargs):
    """Rename a non-pk column in a managed table."""
    table_name = state.pick_table()
    non_pk_cols = [c for c in state.tables[table_name] if c["name"] != "id"]
    if not non_pk_cols:
        return
    col = random.choice(non_pk_cols)
    new_name = f"col_renamed_{random.randint(0, 99999)}"
    alter_table_rename_column(
        table_name=table_name,
        column_name_old=col["name"],
        column_name_new=new_name,
        node=node,
        no_checks=True,
        steps=False,
    )
    for c in state.tables[table_name]:
        if c["name"] == col["name"]:
            c["name"] = new_name
            break


@action("update_rows", group="alter", preconditions=["table_exists", "has_rows"])
def _action_update_rows(node, state, **kwargs):
    """ALTER TABLE ... UPDATE on some rows."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    numeric_cols = _numeric_columns(state.tables[table_name])
    if not numeric_cols:
        return
    col = random.choice(numeric_cols)
    alter_table_update_column(
        table_name=table_name,
        column_name=col["name"],
        expression=f"{col['name']} + 1",
        condition=f"id > {random.randint(0, 50000)}",
        node=node,
        no_checks=True,
        steps=False,
    )


@action("delete_rows", group="alter", preconditions=["table_exists", "has_rows"])
def _action_delete_rows(node, state, **kwargs):
    """ALTER TABLE ... DELETE some rows."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    alter_table_delete_rows(
        table_name=table_name,
        condition=f"id < {random.randint(1, 50000)}",
        node=node,
        no_checks=True,
        steps=False,
    )
    state.rows_inserted[table_name] = max(0, state.rows_inserted[table_name] // 2)

@action("drop_table", group="drop", preconditions=["table_exists"])
def _action_drop_table(node, state, cluster=None, **kwargs):
    """Drop a random managed table."""
    table_name = state.pick_table()
    with By(f"dropping table {table_name}"):
        node.query(
            f"DROP TABLE IF EXISTS {table_name}{_cluster_clause(cluster)}",
            no_checks=True,
            steps=False,
        )
    state.tables.pop(table_name, None)
    state.rows_inserted.pop(table_name, None)


@action("truncate_table", group="drop", preconditions=["table_exists"])
def _action_truncate_table(node, state, cluster=None, **kwargs):
    """Truncate a random managed table."""
    table_name = state.pick_table()
    with By(f"truncating table {table_name}"):
        node.query(
            f"TRUNCATE TABLE IF EXISTS {table_name}{_cluster_clause(cluster)}",
            no_checks=True,
            steps=False,
        )
    state.rows_inserted[table_name] = 0


@action("select_count", group="select", preconditions=["table_exists"])
def _action_select_count(node, state, profile=None, **kwargs):
    """Run SELECT count()."""
    table_name = state.pick_table()
    with By(f"counting rows in {table_name}"):
        for _ in range(_repeat_count(profile)):
            node.query(f"SELECT count() FROM {table_name}", no_checks=True, steps=False)


@action("select_agg", group="select", preconditions=["table_exists", "has_rows"])
def _action_select_agg(node, state, profile=None, **kwargs):
    """Run aggregate queries (sum, avg, min, max)."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    numeric_cols = _numeric_columns(state.tables[table_name], include_id=True)
    if not numeric_cols:
        return
    col = random.choice(numeric_cols)
    with By(f"aggregating {col['name']} in {table_name}"):
        for _ in range(_repeat_count(profile)):
            func = random.choice(["sum", "avg", "min", "max"])
            node.query(
                f"SELECT {func}({col['name']}) FROM {table_name}",
                no_checks=True,
                steps=False,
            )


@action("select_where", group="select", preconditions=["table_exists", "has_rows"])
def _action_select_where(node, state, profile=None, **kwargs):
    """Run SELECT with a random WHERE filter."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    with By(f"filtering rows in {table_name}"):
        for _ in range(_repeat_count(profile)):
            node.query(
                f"SELECT * FROM {table_name} WHERE id > {random.randint(0, 100000)} LIMIT 100",
                no_checks=True,
                steps=False,
            )


@action("select_order_by", group="select", preconditions=["table_exists", "has_rows"])
def _action_select_order_by(node, state, profile=None, **kwargs):
    """Run SELECT with ORDER BY and LIMIT."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    with By(f"ordering rows in {table_name}"):
        for _ in range(_repeat_count(profile)):
            direction = random.choice(["ASC", "DESC"])
            node.query(
                f"SELECT * FROM {table_name} ORDER BY id {direction} LIMIT {random.randint(10, 100)}",
                no_checks=True,
                steps=False,
            )


@action("select_group_by", group="select", preconditions=["table_exists", "has_rows"])
def _action_select_group_by(node, state, profile=None, **kwargs):
    """Run SELECT with GROUP BY on a random column."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    col = random.choice(state.tables[table_name])
    with By(f"grouping rows in {table_name}"):
        for _ in range(_repeat_count(profile)):
            node.query(
                f"SELECT {col['name']}, count() FROM {table_name} "
                f"GROUP BY {col['name']} LIMIT 50",
                no_checks=True,
                steps=False,
            )


@action("system_query", group="system")
def _action_system_query(node, state, profile=None, **kwargs):
    """Run read-only system.* queries."""
    queries = [
        "SHOW TABLES",
        "SELECT count() FROM system.parts",
        "SELECT name, engine FROM system.tables WHERE database = currentDatabase() LIMIT 20",
        "SELECT query_id, query FROM system.processes LIMIT 10",
        "SELECT * FROM system.metrics LIMIT 20",
        "SELECT event, value FROM system.events LIMIT 30",
        "SELECT database, table, partition_id FROM system.parts WHERE active LIMIT 20",
    ]
    with By("running system queries"):
        for _ in range(_repeat_count(profile)):
            node.query(random.choice(queries), no_checks=True, steps=False)


PRECONDITION_CHECKS = {
    "table_exists": lambda state: state.has_tables(),
    "has_rows": lambda state: state.has_rows(),
}


def _preconditions_met(action_obj, state):
    return all(PRECONDITION_CHECKS[pc](state) for pc in action_obj.preconditions)


def _enabled_actions(flags):
    return [
        a for a in ACTION_REGISTRY.values() if flags.get(GROUP_FLAGS[a.group], True)
    ]


def _bootstrap(node, state, cluster=None):
    """Seed initial tables and rows.

    Runs regardless of the enable_* flags, which govern the ongoing random
    workload rather than this one-time seed that reads need to be meaningful.
    """
    for _ in range(2):
        _action_create_table(node, state, cluster=cluster)
        _action_insert_batch(node, state)


def _cleanup(node, state, cluster=None):
    """Drop all tables and views created by the workload."""
    clause = _cluster_clause(cluster)
    for view_name in state.views:
        node.query(
            f"DROP VIEW IF EXISTS {view_name}{clause}", no_checks=True, steps=False
        )
    for table_name in list(state.tables.keys()):
        node.query(
            f"DROP TABLE IF EXISTS {table_name}{clause}", no_checks=True, steps=False
        )
    state.views.clear()
    state.tables.clear()
    state.rows_inserted.clear()

@TestStep(Given)
def simulate_workload(
    self,
    node,
    stop_event: Event,
    intensity: str = "medium",
    cluster: Optional[str] = None,
    delay: Optional[float] = None,
    enable_creates: bool = True,
    enable_inserts: bool = True,
    enable_selects: bool = True,
    enable_alters: bool = True,
    enable_drops: bool = True,
    enable_system: bool = True,
):
    """Run a random ClickHouse workload on a node until stop_event is set.

    Prefer the ``background_workload`` context manager; use this step directly
    only when you need to own the stop_event.

    Args:
        node: ClickHouse node to run against.
        stop_event: set it to stop the loop.
        intensity: "low", "medium", or "high".
        cluster: if set, create/drop/truncate use ON CLUSTER.
        delay: per-round sleep override; defaults to the intensity profile.
        enable_creates/inserts/selects/alters/drops/system: toggle action groups.
    """
    profile = INTENSITY_PROFILES.get(intensity, INTENSITY_PROFILES["medium"])
    if delay is None:
        delay = profile["delay"]

    flags = {
        "enable_creates": enable_creates,
        "enable_inserts": enable_inserts,
        "enable_selects": enable_selects,
        "enable_alters": enable_alters,
        "enable_drops": enable_drops,
        "enable_system": enable_system,
    }
    enabled_actions = _enabled_actions(flags)

    state = WorkloadState()

    try:
        _bootstrap(node, state, cluster=cluster)

        while not stop_event.is_set():
            eligible = [a for a in enabled_actions if _preconditions_met(a, state)]
            if not eligible:
                if enable_creates:
                    _bootstrap(node, state, cluster=cluster)
                time.sleep(delay)
                continue

            action_obj = random.choice(eligible)
            try:
                action_obj.func(node, state, cluster=cluster, profile=profile)
            except Exception as e:
                note(f"workload action '{action_obj.name}' failed: {e}")

            time.sleep(delay)
    finally:
        with Finally("I clean up workload tables"):
            _cleanup(node, state, cluster=cluster)


@contextmanager
def background_workload(node, **kwargs):
    """Run a background workload for the duration of the ``with`` block.

    Starts ``simulate_workload`` in parallel and, on exit, signals it to stop
    and waits for it (including cleanup) to finish. Keyword arguments are
    forwarded to ``simulate_workload``.

    Example::
        with background_workload(node, intensity="high", enable_drops=False):
            ...
    """
    stop_event = Event()
    When("I start a background workload", test=simulate_workload, parallel=True)(
        node=node, stop_event=stop_event, **kwargs
    )
    try:
        yield stop_event
    finally:
        stop_event.set()
        with Finally("I stop the background workload"):
            join()
