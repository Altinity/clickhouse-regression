from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import create_replicated_merge_tree_table
from .export_status import wait_for_export_to_complete
from .storage import create_s3_table


@TestStep(When)
def get_partitions(self, table_name, node):
    """Get all partitions for a table on a given node."""

    output = node.query(
        f"SELECT DISTINCT partition_id FROM system.parts "
        f"WHERE table = '{table_name}' AND partition_id NOT LIKE 'patch-%'",
        exitcode=0,
        steps=True,
    ).output
    return sorted([row.strip() for row in output.splitlines()])


@TestStep(When)
def export_partitions(
    self,
    source_table,
    destination_table,
    node,
    partitions=None,
    exitcode=0,
    settings=None,
    inline_settings=True,
    retry_times=60,
    force_export=False,
    check_export=True,
):
    """Export partitions from a source table to a destination table on the same node. If partitions are not provided, all partitions will be exported."""

    if partitions is None:
        partitions = get_partitions(table_name=source_table, node=node)

    if inline_settings:
        # Copy so appending force_export below does not mutate the shared
        # context.default_settings list and leak into unrelated tests.
        inline_settings = list(self.context.default_settings)

    if force_export:
        inline_settings.append(("export_merge_tree_partition_force_export", 1))

    no_checks = exitcode != 0

    output = []
    with By(f"running EXPORT PARTITION for {source_table} partitions"):
        for partition in partitions:
            for attempt in retries(count=retry_times, delay=5):
                with attempt:
                    output.append(
                        node.query(
                            f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition}' TO TABLE {destination_table}",
                            exitcode=exitcode,
                            no_checks=no_checks,
                            steps=True,
                            settings=settings,
                            inline_settings=inline_settings,
                        )
                    )
                    if check_export:
                        wait_for_export_to_complete(
                            partition_id=partition, source_table=source_table, node=node
                        )

    return output


@TestStep(When)
def export_partition_all(
    self,
    source_table,
    destination_table,
    node,
    exitcode=0,
    settings=None,
    inline_settings=True,
    wait=True,
    check_export=True,
):
    """Export all active partitions from a source table to a destination table in one ALTER."""

    if inline_settings:
        inline_settings = self.context.default_settings

    no_checks = exitcode != 0

    with By(f"running EXPORT PARTITION ALL for {source_table}"):
        node.query(
            f"ALTER TABLE {source_table} EXPORT PARTITION ALL TO TABLE {destination_table}",
            exitcode=exitcode,
            no_checks=no_checks,
            steps=True,
            settings=settings,
            inline_settings=inline_settings,
        )

    if wait and check_export and exitcode == 0:
        partitions = get_partitions(table_name=source_table, node=node)
        for partition in partitions:
            wait_for_export_to_complete(
                partition_id=partition, source_table=source_table, node=node
            )


@TestStep(When)
def export_partition_by_id(
    self,
    source_table,
    destination_table,
    partition_id,
    node,
    exitcode=0,
    settings=None,
    query_settings_sql="",
):
    """Issue a single ``EXPORT PARTITION ID`` and, on success, wait for
    completion. Returns the raw query result so callers can inspect reject
    output when ``exitcode != 0``.
    """
    if settings is None:
        settings = self.context.default_settings

    # Do not wrap this ``query`` in an extra ``By``: TestFlows can terminate
    # a nested step after the command has already finished, which would leave
    # ``result`` unassigned (``UnboundLocalError``). ``steps=True`` still
    # records the command in the test tree.
    result = node.query(
        f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition_id}' "
        f"TO TABLE {destination_table}{query_settings_sql}",
        settings=settings,
        exitcode=exitcode,
        ignore_exception=(exitcode != 0),
        steps=True,
    )
    if exitcode == 0:
        wait_for_export_to_complete(
            partition_id=partition_id, source_table=source_table, node=node
        )
    return result


@TestStep(Then)
def assert_no_scheduled_exports(
    self,
    source_table,
    node,
    destination_table=None,
    partition_id=None,
):
    """Assert nothing matching the filter was scheduled in
    ``system.replicated_partition_exports`` (i.e. the gate rejected
    synchronously)."""
    where = [f"source_table = '{source_table}'"]
    if destination_table is not None:
        where.append(f"destination_table = '{destination_table}'")
    if partition_id is not None:
        where.append(f"partition_id = '{partition_id}'")
    count = node.query(
        "SELECT count() FROM system.replicated_partition_exports "
        f"WHERE {' AND '.join(where)}"
    ).output.strip()
    assert count == "0", error(f"expected 0 scheduled tasks for {where}, got {count}")


@TestStep(When)
def get_partition_min_max(self, source_table, partition_id, columns, node):
    """Return ``{col: (min, max), ...}`` for ``columns`` on one source
    partition. Values are the raw string form returned by ClickHouse."""
    if not columns:
        return {}
    projection = ", ".join(f"min({c}), max({c})" for c in columns)
    row = (
        node.query(
            f"SELECT {projection} FROM {source_table} "
            f"WHERE _partition_id = '{partition_id}' FORMAT TabSeparated"
        )
        .output.strip()
        .split("\t")
    )
    return {c: (row[2 * i], row[2 * i + 1]) for i, c in enumerate(columns)}


@TestStep(When)
def get_partition_id_where(self, source_table, where, node):
    """Return the single ``_partition_id`` matching a WHERE filter on the
    source table (fails loudly if the filter matches multiple partitions)."""
    output = (
        node.query(
            f"SELECT DISTINCT _partition_id FROM {source_table} "
            f"WHERE {where} FORMAT TabSeparated"
        )
        .output.strip()
        .splitlines()
    )
    assert len(output) == 1, error(
        f"expected exactly one partition matching {where!r}, got {output!r}"
    )
    return output[0].strip()


# NOTE: The helpers below are intentionally plain Python functions, not
# ``@TestStep``s. A ``@TestStep`` called from a ``@TestScenario`` gets
# wrapped in a Step context that returns the inner ``Result`` object
# (message, reason, type) instead of the function's raw return value; the
# caller then unpacks/formats the ``Result`` and gets garbage like
# ``'OK'`` (the enum member's stringification). Plain functions always
# return their raw value regardless of caller context. Where these
# helpers internally invoke a value-returning ``@TestStep`` (e.g.
# ``create_s3_table``), that call is wrapped in a local
# ``with Given()/When()`` block so the raw value is returned there too.


def _current_node(node):
    """Resolve default node from the current test's context."""
    if node is not None:
        return node
    from testflows.core import current

    return current().context.node


def insert_values(table_name, values, node=None):
    """``INSERT INTO {table_name} VALUES {values}`` on the given node."""
    _current_node(node).query(f"INSERT INTO {table_name} VALUES {values}")


def select_rows(table_name, columns="*", order_by=None, where=None, node=None):
    """``SELECT {columns} [WHERE ...] [ORDER BY ...] FORMAT TabSeparated``;
    returns the query's output as a stripped string.
    """
    query = f"SELECT {columns} FROM {table_name}"
    if where:
        query += f" WHERE {where}"
    if order_by:
        query += f" ORDER BY {order_by}"
    query += " FORMAT TabSeparated"
    return _current_node(node).query(query).output.strip()


def count_rows(table_name, where=None, node=None):
    """Return ``SELECT count() FROM {table_name} [WHERE ...]`` as an int."""
    query = f"SELECT count() FROM {table_name}"
    if where:
        query += f" WHERE {where}"
    return int(_current_node(node).query(query).output.strip())


def drop_partition_by_id(table_name, partition_id, node=None):
    """``ALTER TABLE {table_name} DROP PARTITION ID '{partition_id}'``."""
    _current_node(node).query(
        f"ALTER TABLE {table_name} DROP PARTITION ID '{partition_id}'"
    )


def get_first_partition_id(table_name, node=None):
    """Return the first partition_id from ``system.parts`` for the table.
    Inlines the query (rather than calling the ``get_partitions``
    ``@TestStep``) so it can be called safely from any context.
    """
    output = (
        _current_node(node)
        .query(
            f"SELECT DISTINCT partition_id FROM system.parts "
            f"WHERE table = '{table_name}' AND partition_id NOT LIKE 'patch-%'"
        )
        .output
    )
    return sorted(row.strip() for row in output.splitlines())[0]


def setup_source_and_hive_destination(
    src_columns,
    src_partition_by,
    dst_columns=None,
    dst_partition_by=None,
    stop_merges=False,
):
    """Create a replicated MergeTree source and a hive S3 destination with
    matching (or provided) columns/partition_by. Returns
    ``(source_table, destination_table)``. Inner ``@TestStep`` calls are
    wrapped in ``with Given()`` blocks so the raw destination table name
    is returned (not a ``Result``).
    """
    if dst_columns is None:
        dst_columns = src_columns
    if dst_partition_by is None:
        dst_partition_by = src_partition_by
    source_table = f"src_{getuid()}"
    with Given(f"replicated MergeTree source PARTITION BY {src_partition_by}"):
        create_replicated_merge_tree_table(
            table_name=source_table,
            columns=src_columns,
            partition_by=src_partition_by,
            cluster="replicated_cluster",
            stop_merges=stop_merges,
        )
    with Given(f"hive S3 destination PARTITION BY {dst_partition_by}"):
        destination_table = create_s3_table(
            table_name="dst",
            create_new_bucket=True,
            columns=dst_columns,
            partition_by=dst_partition_by,
        )
    return source_table, destination_table


def assert_export_rejected(
    source_table,
    destination_table,
    partition_id,
    exitcode,
    expected_substrings=(),
    node=None,
    check_no_scheduled=True,
    query_settings_sql="",
):
    """Attempt ``export_partition_by_id`` and assert it fails with the
    given ``exitcode`` and every substring in ``expected_substrings`` is
    present in the error output. Also asserts no task was scheduled
    unless ``check_no_scheduled=False``. Returns the raw result.

    ``query_settings_sql`` is appended to the ALTER verbatim, for rejects
    that are only reachable once an earlier guard has been opted past
    (e.g. asserting a partition-key rejection on a schema pair that also
    needs ``export_merge_tree_part_allow_lossy_cast``).
    """
    node = _current_node(node)
    with When(
        f"I attempt to export partition '{partition_id}' expecting exit={exitcode}"
    ):
        result = export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id=partition_id,
            node=node,
            exitcode=exitcode,
            query_settings_sql=query_settings_sql,
        )
    for fragment in expected_substrings:
        assert fragment in result.output, error(
            f"expected {fragment!r} in error, got: {result.output!r}"
        )
    if check_no_scheduled:
        with Then("no export task was scheduled"):
            assert_no_scheduled_exports(
                source_table=source_table,
                destination_table=destination_table,
                partition_id=partition_id,
                node=node,
            )
    return result


@TestStep(When)
def kill_export_partition(
    self,
    partition_id,
    source_table,
    destination_table,
    node=None,
    exitcode=0,
):
    """Kill an export partition operation.

    Args:
        partition_id: The partition ID to kill the export for
        source_table: The source table name
        destination_table: The destination table name
        node: The node to execute the query on (defaults to context.node)
        exitcode: Expected exit code (default: 0)
    """
    if node is None:
        node = self.context.node

    no_checks = exitcode != 0

    with By(
        f"killing EXPORT PARTITION for partition_id='{partition_id}', "
        f"source_table='{source_table}', destination_table='{destination_table}'"
    ):
        result = node.query(
            f"KILL EXPORT PARTITION WHERE partition_id = '{partition_id}' "
            f"AND source_table = '{source_table}' "
            f"AND destination_table = '{destination_table}'",
            exitcode=exitcode,
            no_checks=no_checks,
            steps=True,
        )

    return result
