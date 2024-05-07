from contextlib import contextmanager

from testflows.core import *

import rbac.helper.errors as errors
from rbac.requirements import *
from rbac.helper.common import *
from rbac.tests.sql_security.common import *


@TestStep
def create_simple_MergeTree_table(self, node, table_name, column_name="x"):
    """Create table with one UInt32 column."""
    node.query(
        f"CREATE TABLE {table_name} (x UInt32) ENGINE = MergeTree() ORDER BY {column_name}"
    )


@TestStep
def create_user(self, node, user_name=None):
    """Create user."""
    if user_name is None:
        user_name = "user_" + getuid()

    node.query(f"CREATE USER {user_name}")

    return user_name


@TestStep
def grant_privilege(self, node, privilege, object, user):
    """Grant privilege on table/view/database to user."""
    node.query(f"GRANT {privilege} ON {object} TO {user}")


@TestStep
def create_materialized_view(
    self,
    node,
    view_name,
    mv_table_name,
    table_name,
    definer=None,
    sql_security=None,
    if_not_exists=False,
    on_cluster=None,
    select_columns="*",
):
    """Create materialized view."""

    query = f"CREATE MATERIALIZED VIEW "

    if if_not_exists:
        query += "IF NOT EXISTS "

    query += f"{view_name} "

    if on_cluster is not None:
        query += f"ON CLUSTER {on_cluster} "

    query += f"TO {mv_table_name} "

    if definer is not None:
        query += f"DEFINER = {definer} "

    if sql_security is not None:
        query += f"SQL SECURITY {sql_security} "

    query += f"AS SELECT {select_columns} FROM {table_name}"

    node.query(query)


@TestStep
def populate_mv_table(self, node, mv_table_name, table_name, select_columns="*"):
    """Insert data into materialized view table."""
    node.query(f"INSERT INTO {mv_table_name} SELECT {select_columns} FROM {table_name}")


@TestStep
def create_view(
    self,
    node,
    view_name,
    table_name,
    definer=None,
    sql_security=None,
    if_not_exists=False,
    on_cluster=None,
    select_columns="*",
):
    """Create view."""

    query = f"CREATE VIEW "

    if if_not_exists:
        query += "IF NOT EXISTS "

    query += f"{view_name} "

    if on_cluster is not None:
        query += f"ON CLUSTER {on_cluster} "

    query += f"TO {table_name} "

    if definer is not None:
        query += f"DEFINER = {definer} "

    if sql_security is not None:
        query += f"SQL SECURITY {sql_security} "

    query += f"AS SELECT {select_columns} FROM {table_name}"

    node.query(query)


def insert_data_from_numbers(node, table_name, rows=10):
    """Insert data into table from numbers."""
    node.query(f"INSERT INTO {table_name} SELECT number FROM numbers({rows})")
