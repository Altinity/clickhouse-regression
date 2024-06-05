from contextlib import contextmanager

from testflows.core import *

import rbac.helper.errors as errors
from rbac.requirements import *
from rbac.helper.common import *
from rbac.tests.sql_security.common import *

from helpers.common import getuid


@TestStep(Given)
def create_simple_MergeTree_table(
    self, node=None, table_name=None, column_name="x", cluster=None, rows=0
):
    """Create simple MergeTree table with one UInt32 column."""
    if table_name is None:
        table_name = "table_" + getuid()

    if node is None:
        node = self.context.node

    query = f"CREATE TABLE {table_name} "

    if cluster is not None:
        query += f"ON CLUSTER {cluster} (x UInt32) ENGINE = ReplicatedMergeTree ORDER BY {column_name}"
    else:
        query += f"({column_name} UInt32) ENGINE = MergeTree ORDER BY {column_name}"

    try:
        node.query(query)

        if rows > 0:
            node.query(f"INSERT INTO {table_name} SELECT number FROM numbers({rows})")

        yield table_name

    finally:
        with Finally("I drop the table if exists"):
            if cluster is not None:
                node.query(
                    f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster} SYNC"
                )
            else:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep(Given)
def create_user(self, node=None, user_name=None):
    """Create user with given name. If name is not provided, it will be generated."""

    if node is None:
        node = self.context.node

    if user_name is None:
        user_name = "user_" + getuid()
    try:
        node.query(f"CREATE USER {user_name}")
        yield user_name

    finally:
        with Finally("I drop the user if exists"):
            node.query(f"DROP USER IF EXISTS {user_name}")


@TestStep(Given)
def grant_privilege(self, node, privilege, object, user):
    """Grant privilege on table/view/database to user."""
    node.query(f"GRANT {privilege} ON {object} TO {user}")


@TestStep(Given)
def grant_privileges_directly(self, privileges, object, user, node=None):
    """Grant privilege on table/view/database to user directly."""
    if node is None:
        node = self.context.node

    for privilege in privileges:
        node.query(f"GRANT {privilege} ON {object} TO {user}")


@TestStep(Given)
def grant_privileges_via_role(self, privileges, object, user, node=None):
    """Grant privilege on table/view/database to user via role."""
    if node is None:
        node = self.context.node

    role = create_role()
    for privilege in privileges:
        node.query(f"GRANT {privilege} ON {object} TO {role}")
    node.query(f"GRANT {role} TO {user}")


@TestStep(Given)
def create_materialized_view(
    self,
    source_table_name,
    node=None,
    view_name=None,
    target_table_name=None,
    definer=None,
    sql_security=None,
    if_not_exists=False,
    cluster=None,
    select_columns="*",
    settings=None,
    exitcode=None,
    message=None,
    order_by=None,
    engine=None,
    populate=False,
):
    """Create materialized view."""

    if node is None:
        node = self.context.node

    if view_name is None:
        view_name = "mv_" + getuid()

    query = f"CREATE MATERIALIZED VIEW "

    if if_not_exists:
        query += "IF NOT EXISTS "

    query += f"{view_name} "

    if cluster is not None:
        query += f"ON CLUSTER {cluster} "

    if target_table_name is not None:
        query += f"TO {target_table_name} "

    if engine is not None:
        query += f"ENGINE = {engine} "

    if order_by is not None:
        query += f"ORDER BY {order_by} "

    if populate:
        query += "POPULATE "

    if definer is not None:
        query += f"DEFINER = {definer} "

    if sql_security is not None:
        query += f"SQL SECURITY {sql_security} "

    query += f"AS SELECT {select_columns} FROM {source_table_name}"

    try:
        if settings is not None:
            node.query(query, settings=settings, exitcode=exitcode, message=message)
        else:
            node.query(query, exitcode=exitcode, message=message)
        yield view_name

    finally:
        with Finally("I drop the materialized view if exists"):
            node.query(f"DROP TABLE IF EXISTS {view_name}")


@TestStep(Given)
def populate_table(
    self, destination_table_name, source_table_name, node=None, select_columns="*"
):
    """Insert data into table."""
    if node is None:
        node = self.context.node

    node.query(
        f"INSERT INTO {destination_table_name} SELECT {select_columns} FROM {source_table_name}"
    )


@TestStep(Given)
def create_view(
    self,
    node,
    view_name,
    select_table_name,
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

    if definer is not None:
        query += f"DEFINER = {definer} "

    if sql_security is not None:
        query += f"SQL SECURITY {sql_security} "

    query += f"AS SELECT {select_columns} FROM {select_table_name}"

    try:
        node.query(query)
        yield view_name

    finally:
        with Finally("I drop the view if exists"):
            node.query(f"DROP VIEW IF EXISTS {view_name}")


def insert_data_from_numbers(table_name, rows=10, node=None):
    """Insert data into table from numbers table function."""
    if node is None:
        node = current().context.node

    node.query(f"INSERT INTO {table_name} SELECT number FROM numbers({rows})")


@TestStep(Given)
def create_role(self, privilege=None, object=None, role_name=None, node=None):
    """Create role and grant privilege."""

    if node is None:
        node = self.context.node

    if role_name is None:
        role_name = f"role_{getuid()}"

    query = f"CREATE ROLE {role_name};"

    try:
        node.query(query)
        yield role_name

    finally:
        with Finally("I drop the role"):
            node.query(f"DROP ROLE IF EXISTS {role_name}")


@TestStep(Given)
def change_core_settings(
    self,
    entries,
    modify=False,
    restart=True,
    format=None,
    user=None,
    config_d_dir="/etc/clickhouse-server/users.d",
    preprocessed_name="users.xml",
):
    """Create configuration file and add it to the server."""
    with By("converting config file content to xml"):
        config = create_xml_config_content(
            entries,
            "change_settings.xml",
            config_d_dir=config_d_dir,
            preprocessed_name=preprocessed_name,
        )
        if format is not None:
            for key, value in format.items():
                config.content = config.content.replace(key, value)

    with And("adding xml config file to the server"):
        return add_config(config, restart=restart, modify=modify, user=user)


@TestStep(Given)
def create_user_on_cluster(self, node, cluster, user_name=None):
    """Create user on cluster."""
    if user_name is None:
        user_name = "user_" + getuid()
    try:
        node.query(f"CREATE USER {user_name} ON CLUSTER {cluster}")
        yield user_name

    finally:
        with Finally("I drop the user if exists"):
            node.query(f"DROP USER IF EXISTS {user_name} ON CLUSTER {cluster}")
