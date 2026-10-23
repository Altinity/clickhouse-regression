"""Materialized-view helpers for CAS scenarios."""

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from cas.tests.steps.checksums import payload_table_checksum
from cas.tests.steps.disk import storage_settings
from cas.tests.steps.pool import blob_keys, settled_pool_snapshot, size_in_bytes
from cas.tests.steps.tables import (
    create_cas_merge_tree_table,
    create_local_merge_tree_table,
)

# A payload column of ``insert_cas_payload_rows`` default size is about 1 MiB
# and does not compress. Metadata files stay well under this.
PAYLOAD_BLOB_BYTES = 512 * 1024

ID_COLUMNS = "id UInt64, v UInt64"
PAYLOAD_COLUMNS = "p UInt8, i UInt64, payload String"
WIDE_PART_SETTINGS = [
    "min_bytes_for_wide_part = 0",
    "min_rows_for_wide_part = 0",
]

LIGHTWEIGHT_DELETE_SETTINGS = [
    ("mutations_sync", 2),
    ("allow_experimental_lightweight_delete", 1),
]


def payload_blob_count(snapshot):
    """Count unique content blobs large enough to be a payload column copy."""
    return sum(
        1
        for key in blob_keys(snapshot)
        if size_in_bytes(snapshot[key]) >= PAYLOAD_BLOB_BYTES
    )


def _node(self, node):
    """Return the explicitly supplied node or the suite default."""
    return node or self.context.node


def quote_identifier(name):
    """Backtick-quote ``name`` for SQL that ``node.query`` sends through
    ``echo -e "..."``, where a bare backtick is shell command substitution.
    """
    return f"\\`{name}\\`"


def payload_engine(self, pool_prefix, disk_name):
    """Inner-table ``ENGINE`` clause for a wide payload MergeTree on its own pool."""
    disk = storage_settings(self, pool_prefix=pool_prefix, disk_name=disk_name)
    return (
        "ENGINE = MergeTree PARTITION BY p ORDER BY (p, i) "
        f"{disk}, {', '.join(WIDE_PART_SETTINGS)}"
    )


@TestStep(Given)
@Name("create an id/value MergeTree")
def create_id_table(
    self,
    table_name,
    where,
    engine="MergeTree",
    extra_settings=None,
    partition_by="tuple()",
    columns=ID_COLUMNS,
    node=None,
):
    """Create ``id, v`` MergeTree on ``local`` or on ``cas_policy``.

    Ordered by ``id``. ``columns`` may add columns such as a projection.
    """
    kwargs = dict(
        table_name=table_name,
        columns=columns,
        partition_by=partition_by,
        order_by="id",
        engine=engine,
        node=node,
    )
    if where == "local":
        create_local_merge_tree_table(extra_settings=extra_settings, **kwargs)
    elif where == "cas":
        create_cas_merge_tree_table(extra_settings=extra_settings, **kwargs)
    else:
        fail(f"unknown storage {where!r}; expected 'local' or 'cas'")
    return table_name


@TestStep(Given)
@Name("create a wide payload table on its own CAS pool")
def create_payload_table(self, table_name, pool_prefix, disk_name, node=None):
    """Create ``p, i, payload`` MergeTree on an inline CAS disk.

    Wide parts are forced so the payload column is one file whose bytes can
    be compared across tables.
    """
    create_cas_merge_tree_table(
        table_name=table_name,
        columns=PAYLOAD_COLUMNS,
        order_by="(p, i)",
        pool_prefix=pool_prefix,
        disk_name=disk_name,
        extra_settings=WIDE_PART_SETTINGS,
        node=node,
    )
    return table_name


@TestStep(Given)
@Name("create a materialized view")
def create_materialized_view(
    self,
    view_name,
    select,
    to_table=None,
    engine=None,
    populate=False,
    refresh=None,
    on_cluster=None,
    node=None,
    drop_sync=True,
):
    """Create a materialized view and drop it when the scenario ends.

    ``select`` includes the ``SELECT`` keyword. Pass ``to_table`` for a
    ``TO`` view, or ``engine`` for the inner-table clause
    (``ENGINE = MergeTree ... SETTINGS ...``). Exactly one of the two.
    ``POPULATE`` is valid only with ``engine``. ``TO`` and ``POPULATE``
    together are a syntax error, on CAS and on a local disk.
    ``refresh`` makes the view refreshable, for example
    ``REFRESH EVERY 1 HOUR`` or ``REFRESH EVERY 1 HOUR APPEND``. A
    refreshable view runs its first refresh as soon as it is created.
    ``on_cluster`` emits ``ON CLUSTER`` for both CREATE and DROP.
    """
    if (to_table is None) == (engine is None):
        fail("pass exactly one of to_table or engine")
    if to_table is not None and populate:
        fail("POPULATE cannot be combined with TO")

    node = _node(self, node)
    cluster = f" ON CLUSTER {on_cluster}" if on_cluster else ""
    refresh_clause = f"\n{refresh}" if refresh else ""
    target = f"TO {to_table}" if to_table else engine
    populate_clause = "\nPOPULATE" if populate else ""

    node.query(f"DROP TABLE IF EXISTS {view_name}{cluster} SYNC")
    node.query(
        f"""
        CREATE MATERIALIZED VIEW {view_name}{cluster}{refresh_clause}
        {target}{populate_clause}
        AS {select}
        """
    )

    try:
        yield view_name
    finally:
        with Finally(f"drop materialized view {view_name}"):
            suffix = " SYNC" if drop_sync else ""
            node.query(
                f"DROP TABLE IF EXISTS {view_name}{cluster}{suffix}",
                no_checks=True,
            )


@TestStep(Given)
@Name("check that the database can exchange tables")
def table_exchange_works(self, node=None):
    """Return False when ``EXCHANGE TABLES`` loses a metadata file.

    A full refresh swaps tables with ``EXCHANGE``, which relies on
    ``renameat2(RENAME_EXCHANGE)`` in the metadata directory. A Docker
    Desktop bind mount on macOS performs it as a plain rename: the statement
    succeeds and one ``.sql`` file is gone. Every full refresh then fails
    with ``ATOMIC_RENAME_FAIL`` on a local disk as well as on CAS.
    """
    node = _node(self, node)
    left, right = f"exchange_probe_{getuid()}", f"exchange_probe_{getuid()}"
    try:
        for name in (left, right):
            node.query(f"CREATE TABLE {name} (x UInt8) ENGINE = Memory")
        node.query(f"EXCHANGE TABLES {left} AND {right}")
        paths = node.query(
            "SELECT metadata_path FROM system.tables "
            f"WHERE database = currentDatabase() AND name IN ('{left}', '{right}')"
        ).output.split()
        missing = [
            path
            for path in paths
            if node.command(
                f"test -f '/var/lib/clickhouse/{path}'", no_checks=True
            ).exitcode
            != 0
        ]
    finally:
        for name in (left, right):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC", no_checks=True)

    if missing:
        note(f"EXCHANGE TABLES lost {missing} on this metadata filesystem")
    return not missing


@TestStep(Then)
@Name("inner table of a materialized view")
def inner_table_name(self, view_name, node=None):
    """Return the MergeTree that stores an inner-engine materialized view.

    Atomic databases name it ``.inner_id.<view uuid>``. Ordinary databases
    name it ``.inner.<view>``.
    """
    node = _node(self, node)
    found = node.query(
        "SELECT name FROM system.tables "
        "WHERE database = currentDatabase() AND name IN ("
        f"concat('.inner.', '{view_name}'), "
        "concat('.inner_id.', toString(("
        "SELECT uuid FROM system.tables "
        f"WHERE database = currentDatabase() AND name = '{view_name}'"
        "))))"
    ).output.strip()
    names = [line for line in found.splitlines() if line.strip()]
    if len(names) != 1:
        visible = node.query(
            "SELECT name, engine FROM system.tables "
            "WHERE database = currentDatabase() "
            f"AND (name = '{view_name}' OR startsWith(name, '.inner'))"
        ).output.strip()
        fail(
            f"expected one inner table for {view_name}, found {names or 'none'}:\n"
            f"{visible}"
        )
    return names[0]


@TestStep(When)
@Name("insert values")
def insert_values(
    self, table_name, values, node=None, settings=None, exitcode=None, message=None
):
    """``INSERT INTO table VALUES ...``. ``values`` includes the parentheses.

    ``exitcode`` and ``message`` assert that the insert is rejected.
    """
    return _node(self, node).query(
        f"INSERT INTO {table_name} VALUES {values}",
        settings=settings,
        exitcode=exitcode,
        message=message,
    )


@TestStep(When)
@Name("insert select")
def insert_select(self, table_name, select, node=None, settings=None):
    """``INSERT INTO table SELECT ...``. ``select`` includes the keyword."""
    _node(self, node).query(f"INSERT INTO {table_name} {select}", settings=settings)


@TestStep(Then)
@Name("query result matches")
def assert_query_result(self, query, expected, node=None, settings=None):
    """Run ``query`` and compare its TabSeparated output to ``expected``."""
    actual = _node(self, node).query(query, settings=settings).output.strip()
    assert actual == expected, error(actual)


@TestStep(When)
@Name("stop merges")
def stop_merges(self, table_name, node=None):
    """Pause background merges on ``table_name``."""
    _node(self, node).query(f"SYSTEM STOP MERGES {table_name}")


@TestStep(When)
@Name("start merges")
def start_merges(self, table_name, node=None):
    """Resume background merges on ``table_name``."""
    _node(self, node).query(f"SYSTEM START MERGES {table_name}")


@TestStep(When)
@Name("lightweight delete rows")
def lightweight_delete(self, table_name, condition, node=None):
    """``DELETE FROM table WHERE condition`` and wait for the mutation."""
    _node(self, node).query(
        f"DELETE FROM {table_name} WHERE {condition}",
        settings=LIGHTWEIGHT_DELETE_SETTINGS,
    )


@TestStep(When)
@Name("drop table")
def drop_table(self, table_name, node=None):
    """``DROP TABLE IF EXISTS ... SYNC``."""
    _node(self, node).query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep(When)
@Name("try to drop a table")
def drop_table_result(self, table_name, node=None, settings=None):
    """``DROP TABLE ... SYNC``, returning the result without failing the step.

    Used when the statement is expected to be rejected. ``settings`` is a
    list of ``(name, value)`` client settings for that one statement.
    """
    return _node(self, node).query(
        f"DROP TABLE {table_name} SYNC",
        settings=settings,
        no_checks=True,
    )


@TestStep(When)
@Name("modify the view query")
def modify_view_query(self, view_name, select, node=None):
    """``ALTER TABLE view MODIFY QUERY select``."""
    _node(self, node).query(f"ALTER TABLE {view_name} MODIFY QUERY {select}")


@TestStep(When)
@Name("refresh a refreshable view")
def refresh_view(self, view_name, node=None):
    """Start a refresh and wait until it finishes."""
    node = _node(self, node)
    node.query(f"SYSTEM REFRESH VIEW {view_name}")
    node.query(f"SYSTEM WAIT VIEW {view_name}")


@TestStep(When)
@Name("wait for a refreshable view")
def wait_view(self, view_name, node=None):
    """Wait for the running or scheduled refresh to finish."""
    _node(self, node).query(f"SYSTEM WAIT VIEW {view_name}")


@TestStep(When)
@Name("detach table")
def detach_table(self, table_name, node=None):
    """``DETACH TABLE``. Works for views too."""
    _node(self, node).query(f"DETACH TABLE {table_name}")


@TestStep(When)
@Name("attach table")
def attach_table(self, table_name, node=None):
    """``ATTACH TABLE`` a table or view detached earlier."""
    _node(self, node).query(f"ATTACH TABLE {table_name}")


@TestStep(When)
@Name("rename table")
def rename_table(self, table_name, new_name, node=None):
    """``RENAME TABLE``. The caller owns dropping ``new_name``."""
    _node(self, node).query(f"RENAME TABLE {table_name} TO {new_name}")


@TestStep(When)
@Name("truncate table")
def truncate_table(self, table_name, node=None):
    """``TRUNCATE TABLE ... SYNC``. On a view this empties its inner table."""
    _node(self, node).query(f"TRUNCATE TABLE {table_name} SYNC")


@TestStep(When)
@Name("restart the server")
def restart_server(self, node=None):
    """Restart ClickHouse on ``node`` and wait until it answers."""
    _node(self, node).restart_clickhouse()


@TestStep(Then)
@Name("check table")
def assert_check_table(self, table_name, node=None):
    """``CHECK TABLE`` reports every part of ``table_name`` as intact.

    The name is quoted because inner tables are named ``.inner_id.<uuid>``.
    """
    actual = (
        _node(self, node)
        .query(
            f"CHECK TABLE {quote_identifier(table_name)}",
            settings=[("check_query_single_value_result", 1)],
        )
        .output.strip()
    )
    assert actual == "1", error(f"CHECK TABLE {table_name} returned {actual!r}")


@TestStep(Then)
@Name("payload checksums match")
def assert_payload_checksums_match(self, left, right, node=None):
    """Both tables return the same payload checksum. Returns that checksum."""
    node = _node(self, node)
    left_checksum = payload_table_checksum(node, left)
    right_checksum = payload_table_checksum(node, right)
    assert left_checksum == right_checksum, error(
        f"{left}={left_checksum}, {right}={right_checksum}"
    )
    return left_checksum


@TestStep(Then)
@Name("payload blob count")
def assert_payload_blob_count(self, pool_prefix, count):
    """The settled pool holds exactly ``count`` payload-sized blobs."""
    snapshot = settled_pool_snapshot(pool_prefix=pool_prefix)
    actual = payload_blob_count(snapshot)
    note(f"{pool_prefix}: payload blobs={actual}, expected={count}")
    assert actual == count, error(
        f"expected {count} payload blobs in {pool_prefix}, found {actual}: "
        f"{blob_keys(snapshot)}"
    )
