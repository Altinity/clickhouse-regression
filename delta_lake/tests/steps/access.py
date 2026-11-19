"""Steps for reading a Delta table directly from RustFS.

SQL builders at the top are plain functions. Everything a scenario runs
is a TestFlows step.
"""

import io

import pyarrow as pa
import pyarrow.parquet as pq
from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from delta_lake.tests.steps.catalog import (
    STORAGE_ENDPOINT,
    _credentials,
    _node,
    delete_prefix,
    list_keys,
    put_object,
)

VIRTUAL_COLUMNS = {"_path", "_file", "_size", "_time", "_etag"}
ATTACH_OFF = "SET allow_delta_lake_create_table = 0; "


def sql_literal(value):
    escaped = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def function_call(
    function, url, access_key, secret_key, cluster=None, data_format=None
):
    """Positional ``deltaLake*`` call. Format is appended only when set."""
    arguments = []
    if cluster is not None:
        arguments.append(sql_literal(cluster))
    arguments.extend(
        (
            sql_literal(url),
            sql_literal(access_key),
            sql_literal(secret_key),
        )
    )
    if data_format is not None:
        arguments.append(sql_literal(data_format))
    return f"{function}({', '.join(arguments)})"


def engine_arguments(url, access_key, secret_key, data_format=None):
    arguments = [
        sql_literal(url),
        sql_literal(access_key),
        sql_literal(secret_key),
    ]
    if data_format is not None:
        arguments.append(sql_literal(data_format))
    return ", ".join(arguments)


def prefix_http_url(prefix):
    return f"{STORAGE_ENDPOINT}/{prefix}/"


def _parquet_bytes(marker):
    buf = io.BytesIO()
    pq.write_table(pa.table({"name": [marker], "value": [1]}), buf)
    return buf.getvalue()


def _select_sql(source):
    return f"SELECT name, value FROM {source} ORDER BY name FORMAT TabSeparated"


def _source(self, function, url, access_key, secret_key, data_format, cluster):
    access_key, secret_key = _credentials(self, access_key, secret_key)
    return function_call(
        function,
        url,
        access_key,
        secret_key,
        cluster=cluster,
        data_format=data_format,
    )


@TestStep(When)
def read_function(
    self,
    function,
    url,
    access_key=None,
    secret_key=None,
    data_format=None,
    cluster=None,
    node=None,
):
    """SELECT name, value from a deltaLake function."""
    node = _node(self, node)
    source = _source(
        self, function, url, access_key, secret_key, data_format, cluster
    )
    return node.query(_select_sql(source))


@TestStep(When)
def read_source(self, source, node=None):
    """SELECT name, value from a table or other source."""
    node = _node(self, node)
    return node.query(_select_sql(source))


@TestStep(When)
def try_function(
    self,
    function,
    url,
    access_key=None,
    secret_key=None,
    data_format=None,
    cluster=None,
    node=None,
):
    """Run a deltaLake read and return the result, failure included."""
    node = _node(self, node)
    source = _source(
        self, function, url, access_key, secret_key, data_format, cluster
    )
    return node.query(_select_sql(source), no_checks=True, retry_count=0)


@TestStep(When)
def try_engine(self, url, access_key=None, secret_key=None, node=None):
    """Try to attach an engine table. Drop it if the statement succeeds."""
    node = _node(self, node)
    access_key, secret_key = _credentials(self, access_key, secret_key)
    name = f"delta_bad_{getuid()}"
    result = node.query(
        ATTACH_OFF
        + "CREATE TABLE "
        + name
        + " ENGINE = DeltaLake("
        + engine_arguments(url, access_key, secret_key)
        + ")",
        no_checks=True,
        retry_count=0,
    )
    node.query(f"DROP TABLE IF EXISTS {name}")
    return result


@TestStep(When)
def read_collection(self, function, collection, cluster=None, node=None):
    """SELECT name, value through a named collection."""
    node = _node(self, node)
    if cluster is None:
        source = f"{function}({collection})"
    else:
        source = f"{function}({sql_literal(cluster)}, {collection})"
    return node.query(_select_sql(source))


@TestStep(Then)
def expect_lines(self, result, expected):
    """The query output is these lines, in order."""
    assert result.output.splitlines() == list(expected), error(result.output)


@TestStep(Then)
def expect_failed(self, result, forbidden):
    """The query failed, and the output does not contain ``forbidden``."""
    assert result.exitcode != 0, error(result.output)
    assert forbidden not in result.output, error(result.output)


@TestStep(Then)
def expect_log_columns(
    self,
    columns,
    source=None,
    function=None,
    url=None,
    access_key=None,
    secret_key=None,
    data_format=None,
    cluster=None,
    node=None,
):
    """DESCRIBE lists these data columns. Virtual columns are ignored."""
    node = _node(self, node)
    if source is None:
        source = _source(
            self, function, url, access_key, secret_key, data_format, cluster
        )
    result = node.query(f"DESCRIBE TABLE {source} FORMAT TabSeparated")
    found = []
    for line in result.output.splitlines():
        name, type_name = line.split("\t")[:2]
        if name in VIRTUAL_COLUMNS:
            continue
        found.append((name, type_name))
    assert found == list(columns), error(result.output)


@TestStep(Then)
def expect_show_create(self, table_name, marker, columns, node=None):
    """SHOW CREATE lists DeltaLake, the marker, and these columns in order.

    The marker is the storage prefix, or the collection name when the
    engine argument is a named collection.
    """
    node = _node(self, node)
    show = node.query(f"SHOW CREATE TABLE {table_name}").output
    assert "ENGINE = DeltaLake" in show, error(show)
    assert marker in show, error(show)
    cursor = -1
    for name, type_name in columns:
        found = show.find(f"`{name}`", cursor + 1)
        assert found > cursor, error(show)
        assert type_name in show, error(show)
        cursor = found


@TestStep(Then)
def expect_same_keys(self, prefix, expected):
    """The prefix still holds exactly these object keys."""
    found = list_keys(prefix=prefix)
    assert found == list(expected), error(f"{expected}\n{found}")


@TestStep(Then)
def expect_no_delta_log(self, prefix, before):
    """The prefix is unchanged and still has no ``_delta_log``."""
    found = list_keys(prefix=prefix)
    assert found == list(before), error(f"{before}\n{found}")
    assert not any("_delta_log" in key for key in found), error(found)


@TestStep(Given)
def create_engine_table(self, url=None, collection=None, node=None):
    """Attach an engine table with no column list. Drop it when the scenario ends."""
    node = _node(self, node)
    if collection is None:
        access_key, secret_key = _credentials(self, None, None)
        arguments = engine_arguments(url, access_key, secret_key)
    else:
        arguments = collection
    name = f"delta_{getuid()}"
    try:
        node.query(ATTACH_OFF + f"CREATE TABLE {name} ENGINE = DeltaLake({arguments})")
        yield name
    finally:
        with Finally(f"drop table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep(Given)
def create_named_collection(self, url, access_key=None, secret_key=None, node=None):
    """Create a collection with the URL and the keys. Drop it when the scenario ends."""
    node = _node(self, node)
    access_key, secret_key = _credentials(self, access_key, secret_key)
    name = f"delta_conf_{getuid()}"
    try:
        node.query(
            f"CREATE NAMED COLLECTION {name} AS "
            f"url = {sql_literal(url)}, "
            f"access_key_id = {sql_literal(access_key)}, "
            f"secret_access_key = {sql_literal(secret_key)}"
        )
        yield name
    finally:
        with Finally(f"drop named collection {name}"):
            node.query(f"DROP NAMED COLLECTION IF EXISTS {name}")


@TestStep(Given)
def create_parquet_prefix(self, marker):
    """Upload one Parquet object and no ``_delta_log``. Delete it later."""
    prefix = f"delta/plain_{getuid()}"
    try:
        put_object(key=f"{prefix}/part.parquet", body=_parquet_bytes(marker))
        yield prefix
    finally:
        with Finally(f"delete files {prefix}"):
            delete_prefix(prefix=prefix)
