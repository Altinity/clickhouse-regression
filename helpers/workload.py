"""Workload simulator for ClickHouse nodes.

Provides a testflows step that generates realistic background activity
(DDL, DML, queries) on a given ClickHouse node. Designed to run in
parallel with other tests via testflows' ``parallel=True`` mechanism.

Usage::

    from threading import Event
    from helpers.workload import simulate_workload

    stop = Event()

    with Given("background workload is running"):
        When("I start simulating activity", test=simulate_workload, parallel=True)(
            node=node, stop_event=stop, intensity="medium",
        )

    # ... main test logic ...

    with Finally("I stop the workload"):
        stop.set()
"""

import random
import time
from dataclasses import dataclass, field
from threading import Event
from typing import Callable, Dict, List, Optional

from testflows.core import *

from helpers.common import getuid


# ---------------------------------------------------------------------------
# State tracking
# ---------------------------------------------------------------------------


@dataclass
class WorkloadState:
    """Tracks objects created by the workload so preconditions can be checked."""

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


# ---------------------------------------------------------------------------
# Action registry
# ---------------------------------------------------------------------------


@dataclass
class Action:
    name: str
    func: Callable
    preconditions: List[str]


ACTION_REGISTRY: Dict[str, Action] = {}


def action(name, preconditions=()):
    """Register an action implementation under the given name."""

    def register(func):
        ACTION_REGISTRY[name] = Action(
            name=name, func=func, preconditions=list(preconditions)
        )
        return func

    return register


# ---------------------------------------------------------------------------
# Intensity profiles
# ---------------------------------------------------------------------------

INTENSITY_PROFILES = {
    "low": {"repeat_min": 1, "repeat_max": 3, "delay": 1.0},
    "medium": {"repeat_min": 3, "repeat_max": 10, "delay": 0.2},
    "high": {"repeat_min": 5, "repeat_max": 20, "delay": 0.05},
}


def _repeat_count(profile):
    """Random number of repetitions for a query action, per intensity profile."""
    return random.randint(profile["repeat_min"], profile["repeat_max"])


# ---------------------------------------------------------------------------
# Column type pool for random table generation
# ---------------------------------------------------------------------------

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
    """Generate a random literal value for a given ClickHouse type."""
    if col_type.startswith(("UInt", "Int")):
        return str(random.randint(0, 100000))
    if col_type.startswith("Float"):
        return str(round(random.uniform(0, 100000), 2))
    if col_type == "String":
        return f"'row_{random.randint(0, 999999)}'"
    if col_type == "DateTime":
        return f"toDateTime({random.randint(1600000000, 1700000000)})"
    return "0"


# ---------------------------------------------------------------------------
# DDL actions
# ---------------------------------------------------------------------------


@action("create_table")
def _action_create_table(node, state, cluster=None, **kwargs):
    """Create a MergeTree table with random columns."""
    table_name = f"{state.table_prefix()}t{len(state.tables)}_{random.randint(0, 9999)}"
    num_cols = random.randint(2, 6)
    columns = [{"name": "id", "type": "UInt64"}]
    for i in range(num_cols):
        columns.append({"name": f"col{i}", "type": random.choice(COLUMN_TYPES)})

    col_defs = ", ".join(f"{c['name']} {c['type']}" for c in columns)
    node.query(
        f"CREATE TABLE IF NOT EXISTS {table_name}{_cluster_clause(cluster)} "
        f"({col_defs}) ENGINE = MergeTree() ORDER BY id",
        no_checks=True,
        steps=False,
    )
    state.tables[table_name] = columns
    state.rows_inserted[table_name] = 0


@action("drop_table", preconditions=["table_exists"])
def _action_drop_table(node, state, cluster=None, **kwargs):
    """Drop a random managed table."""
    table_name = state.pick_table()
    node.query(
        f"DROP TABLE IF EXISTS {table_name}{_cluster_clause(cluster)}",
        no_checks=True,
        steps=False,
    )
    state.tables.pop(table_name, None)
    state.rows_inserted.pop(table_name, None)


@action("add_column", preconditions=["table_exists"])
def _action_add_column(node, state, cluster=None, **kwargs):
    """Add a random column to a managed table."""
    table_name = state.pick_table()
    col_name = f"col_added_{random.randint(0, 99999)}"
    col_type = random.choice(COLUMN_TYPES)
    node.query(
        f"ALTER TABLE {table_name}{_cluster_clause(cluster)} "
        f"ADD COLUMN IF NOT EXISTS {col_name} {col_type}",
        no_checks=True,
        steps=False,
    )
    state.tables[table_name].append({"name": col_name, "type": col_type})


@action("drop_column", preconditions=["table_exists"])
def _action_drop_column(node, state, cluster=None, **kwargs):
    """Drop a non-pk column from a managed table if more than one exists."""
    table_name = state.pick_table()
    non_pk_cols = [c for c in state.tables[table_name] if c["name"] != "id"]
    if len(non_pk_cols) <= 1:
        return
    col = random.choice(non_pk_cols)
    node.query(
        f"ALTER TABLE {table_name}{_cluster_clause(cluster)} "
        f"DROP COLUMN IF EXISTS {col['name']}",
        no_checks=True,
        steps=False,
    )
    state.tables[table_name] = [
        c for c in state.tables[table_name] if c["name"] != col["name"]
    ]


@action("rename_column", preconditions=["table_exists"])
def _action_rename_column(node, state, cluster=None, **kwargs):
    """Rename a non-pk column in a managed table."""
    table_name = state.pick_table()
    non_pk_cols = [c for c in state.tables[table_name] if c["name"] != "id"]
    if not non_pk_cols:
        return
    col = random.choice(non_pk_cols)
    new_name = f"col_renamed_{random.randint(0, 99999)}"
    node.query(
        f"ALTER TABLE {table_name}{_cluster_clause(cluster)} "
        f"RENAME COLUMN IF EXISTS {col['name']} TO {new_name}",
        no_checks=True,
        steps=False,
    )
    for c in state.tables[table_name]:
        if c["name"] == col["name"]:
            c["name"] = new_name
            break


@action("truncate_table", preconditions=["table_exists"])
def _action_truncate_table(node, state, cluster=None, **kwargs):
    """Truncate a random managed table."""
    table_name = state.pick_table()
    node.query(
        f"TRUNCATE TABLE IF EXISTS {table_name}{_cluster_clause(cluster)}",
        no_checks=True,
        steps=False,
    )
    state.rows_inserted[table_name] = 0


@action("create_mv", preconditions=["table_exists"])
def _action_create_mv(node, state, cluster=None, **kwargs):
    """Create a materialized view over a managed table."""
    table_name = state.pick_table()
    mv_name = f"{table_name}_mv_{random.randint(0, 9999)}"
    node.query(
        f"CREATE MATERIALIZED VIEW IF NOT EXISTS {mv_name}{_cluster_clause(cluster)} "
        f"ENGINE = MergeTree() ORDER BY id "
        f"AS SELECT id, count() as cnt FROM {table_name} GROUP BY id",
        no_checks=True,
        steps=False,
    )
    state.views.append(mv_name)


# ---------------------------------------------------------------------------
# DML actions
# ---------------------------------------------------------------------------


@action("insert_batch", preconditions=["table_exists"])
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
    for i in range(0, len(rows), batch_size):
        chunk = rows[i : i + batch_size]
        node.query(
            f"INSERT INTO {table_name} ({col_names}) VALUES {', '.join(chunk)}",
            no_checks=True,
            steps=False,
        )
    state.rows_inserted[table_name] = state.rows_inserted.get(table_name, 0) + num_rows


@action("delete_rows", preconditions=["table_exists", "has_rows"])
def _action_delete_rows(node, state, **kwargs):
    """Lightweight delete of some rows."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    node.query(
        f"DELETE FROM {table_name} WHERE id < {random.randint(1, 50000)}",
        no_checks=True,
        steps=False,
    )
    state.rows_inserted[table_name] = max(0, state.rows_inserted[table_name] // 2)


@action("update_rows", preconditions=["table_exists", "has_rows"])
def _action_update_rows(node, state, cluster=None, **kwargs):
    """ALTER TABLE UPDATE on some rows."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    numeric_cols = [
        c
        for c in state.tables[table_name]
        if c["type"].startswith(("UInt", "Int", "Float")) and c["name"] != "id"
    ]
    if not numeric_cols:
        return
    col = random.choice(numeric_cols)
    node.query(
        f"ALTER TABLE {table_name}{_cluster_clause(cluster)} "
        f"UPDATE {col['name']} = {col['name']} + 1 WHERE id > {random.randint(0, 50000)}",
        no_checks=True,
        steps=False,
    )


# ---------------------------------------------------------------------------
# Query actions
# ---------------------------------------------------------------------------


@action("select_count", preconditions=["table_exists"])
def _action_select_count(node, state, profile=None, **kwargs):
    """Run SELECT count() multiple times."""
    table_name = state.pick_table()
    for _ in range(_repeat_count(profile)):
        node.query(f"SELECT count() FROM {table_name}", no_checks=True, steps=False)


@action("select_agg", preconditions=["table_exists", "has_rows"])
def _action_select_agg(node, state, profile=None, **kwargs):
    """Run aggregate queries (sum, avg, min, max)."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    numeric_cols = [
        c
        for c in state.tables[table_name]
        if c["type"].startswith(("UInt", "Int", "Float"))
    ]
    if not numeric_cols:
        return
    col = random.choice(numeric_cols)
    for _ in range(_repeat_count(profile)):
        func = random.choice(["sum", "avg", "min", "max"])
        node.query(
            f"SELECT {func}({col['name']}) FROM {table_name}",
            no_checks=True,
            steps=False,
        )


@action("select_where", preconditions=["table_exists", "has_rows"])
def _action_select_where(node, state, profile=None, **kwargs):
    """Run SELECT with random WHERE filter."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    for _ in range(_repeat_count(profile)):
        node.query(
            f"SELECT * FROM {table_name} WHERE id > {random.randint(0, 100000)} LIMIT 100",
            no_checks=True,
            steps=False,
        )


@action("select_order_by", preconditions=["table_exists", "has_rows"])
def _action_select_order_by(node, state, profile=None, **kwargs):
    """Run SELECT with ORDER BY and LIMIT."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    for _ in range(_repeat_count(profile)):
        direction = random.choice(["ASC", "DESC"])
        node.query(
            f"SELECT * FROM {table_name} ORDER BY id {direction} LIMIT {random.randint(10, 100)}",
            no_checks=True,
            steps=False,
        )


@action("select_group_by", preconditions=["table_exists", "has_rows"])
def _action_select_group_by(node, state, profile=None, **kwargs):
    """Run SELECT with GROUP BY on a random column."""
    table_name = state.pick_table_with_rows()
    if table_name is None:
        return
    col = random.choice(state.tables[table_name])
    for _ in range(_repeat_count(profile)):
        node.query(
            f"SELECT {col['name']}, count() FROM {table_name} "
            f"GROUP BY {col['name']} LIMIT 50",
            no_checks=True,
            steps=False,
        )


@action("system_query")
def _action_system_query(node, state, profile=None, **kwargs):
    """Run harmless system queries."""
    queries = [
        "SHOW TABLES",
        "SELECT count() FROM system.parts",
        "SELECT name, engine FROM system.tables WHERE database = currentDatabase() LIMIT 20",
        "SELECT query_id, query FROM system.processes LIMIT 10",
        "SELECT * FROM system.metrics LIMIT 20",
        "SELECT event, value FROM system.events LIMIT 30",
        "SELECT database, table, partition_id FROM system.parts WHERE active LIMIT 20",
    ]
    for _ in range(_repeat_count(profile)):
        node.query(random.choice(queries), no_checks=True, steps=False)


# ---------------------------------------------------------------------------
# Scheduler helpers
# ---------------------------------------------------------------------------

PRECONDITION_CHECKS = {
    "table_exists": lambda state: state.has_tables(),
    "has_rows": lambda state: state.has_rows(),
}


def _preconditions_met(action_obj, state):
    """Return True if all preconditions for the action are met."""
    return all(PRECONDITION_CHECKS[pc](state) for pc in action_obj.preconditions)


def _bootstrap(node, state, cluster=None):
    """Create initial tables and insert data so any action can run immediately."""
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


# ---------------------------------------------------------------------------
# Main step
# ---------------------------------------------------------------------------


@TestStep(Given)
def simulate_workload(
    self,
    node,
    stop_event: Event,
    actions: Optional[List[str]] = None,
    intensity: str = "medium",
    cluster: Optional[str] = None,
    delay: Optional[float] = None,
):
    """Simulate realistic ClickHouse activity on a node until stop_event is set.

    Run this step with ``parallel=True`` to generate background load while
    other test logic executes.

    Args:
        node: ClickHouse node object (from ``self.context.cluster.node(...)``).
        stop_event: threading.Event; set it to stop the workload loop.
        actions: list of action names to enable (None = all registered actions).
        intensity: one of "low", "medium", "high".
        cluster: if provided, DDL statements use ON CLUSTER.
        delay: override the per-round sleep (seconds). If None, uses the
            intensity profile default.
    """
    profile = INTENSITY_PROFILES.get(intensity, INTENSITY_PROFILES["medium"])
    if delay is None:
        delay = profile["delay"]

    if actions is not None:
        enabled_actions = [ACTION_REGISTRY[a] for a in actions if a in ACTION_REGISTRY]
    else:
        enabled_actions = list(ACTION_REGISTRY.values())

    state = WorkloadState()

    try:
        _bootstrap(node, state, cluster=cluster)

        while not stop_event.is_set():
            eligible = [a for a in enabled_actions if _preconditions_met(a, state)]
            if not eligible:
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
