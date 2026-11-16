"""Generic query steps and the setting names that changed between releases."""

from testflows.asserts import error
from testflows.core import *

from helpers.feature_support import setting_supported
from delta_lake.tests.steps.access import function_call
from delta_lake.tests.steps.catalog import _credentials, _node, list_keys, get_object


def writes_setting(self):
    """``allow_delta_lake_writes`` from 26.7, the experimental name before."""
    if setting_supported("allow_delta_lake_writes")(self):
        return "allow_delta_lake_writes"
    return "allow_experimental_delta_lake_writes"


def kernel_setting(self):
    """``allow_delta_kernel_rs`` from 26.8, the experimental name before."""
    if setting_supported("allow_delta_kernel_rs")(self):
        return "allow_delta_kernel_rs"
    return "allow_experimental_delta_kernel_rs"


def catalog_tables_setting(self):
    """The setting that puts catalog tables in ``system.tables`` and ``system.columns``."""
    if setting_supported("show_data_lake_catalogs_in_system_tables")(self):
        return "show_data_lake_catalogs_in_system_tables"
    return "show_remote_databases_in_system_tables"


def delta_function(self, url, access_key=None, secret_key=None):
    """``deltaLake(url, key, secret)`` with the suite keys by default."""
    access_key, secret_key = _credentials(self, access_key, secret_key)
    return function_call("deltaLake", url, access_key, secret_key)


def catalog_source(database, table):
    return f"{database}.{table.identifier}"


@TestStep(When)
def query_lines(self, sql, node=None):
    """Run a query in TabSeparated and return its output lines."""
    node = _node(self, node)
    return node.query(f"{sql} FORMAT TabSeparated").output.splitlines()


@TestStep(When)
def try_query(self, sql, node=None):
    """Run a statement and return the result, failure included."""
    node = _node(self, node)
    return node.query(sql, no_checks=True, retry_count=0)


@TestStep(Then)
def expect_query_lines(self, sql, expected, node=None):
    """The query returns exactly these lines, in order."""
    found = query_lines(sql=sql, node=node)
    assert found == list(expected), error(f"{found}\n!=\n{list(expected)}")


@TestStep(Then)
def expect_error(self, result, message=None, forbidden=None):
    """The statement failed. ``message`` is in the error, ``forbidden`` is not."""
    assert result.exitcode != 0, error(result.output)
    if message is not None:
        assert message.lower() in result.output.lower(), error(result.output)
    if forbidden is not None:
        assert forbidden not in result.output, error(result.output)


@TestStep(When)
def log_files(self, table):
    """``_delta_log/*.json`` keys of a table and their content."""
    prefix = f"{table.prefix}/_delta_log/"
    return {
        key: get_object(key=key)
        for key in list_keys(prefix=prefix)
        if key.endswith(".json")
    }


@TestStep(Then)
def expect_log_unchanged(self, table, before):
    """The commit files are exactly the ones recorded in ``before``."""
    after = log_files(table=table)
    assert after == before, error(f"{sorted(before)}\n!=\n{sorted(after)}")


@TestStep(Then)
def expect_one_new_commit(self, table, before):
    """One new commit file exists, and every earlier one is byte-for-byte the same."""
    after = log_files(table=table)
    added = sorted(set(after) - set(before))
    assert len(added) == 1, error(added)
    for key, body in before.items():
        assert after.get(key) == body, error(f"{key} was replaced")
    return added[0]
