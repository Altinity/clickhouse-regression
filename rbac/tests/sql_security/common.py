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
def create_table_with_two_columns_with_data(
    self,
    node=None,
    table_name=None,
    column_names=["x", "y"],
    order_by="x",
    cluster=None,
    rows=0,
):
    """Create simple MergeTree table with two Int32 columns."""
    if table_name is None:
        table_name = "table_" + getuid()

    if node is None:
        node = self.context.node

    query = f"CREATE TABLE {table_name} "

    columns_def = ", ".join([f"{column} Int32" for column in column_names])

    if cluster is not None:
        query += f"ON CLUSTER {cluster} ({columns_def}) ENGINE = ReplicatedMergeTree ORDER BY {order_by}"
    else:
        query += f"({columns_def}) ENGINE = MergeTree ORDER BY {order_by}"

    try:
        node.query(query)

        if rows > 0:
            column1_data = [str(i) for i in range(rows)]
            column2_data = [str(i) for i in range(rows - 15, rows - 15 + rows)]
            data = ", ".join(
                [f"({column1_data[i]}, {column2_data[i]})" for i in range(rows)]
            )
            node.query(f"INSERT INTO {table_name} VALUES {data}")

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
def create_user_on_cluster(self, cluster, node=None, user_name=None):
    """Create user on cluster."""
    if node is None:
        node = self.context.node

    if user_name is None:
        user_name = "user_" + getuid()
    try:
        node.query(f"CREATE USER {user_name} ON CLUSTER {cluster}")
        yield user_name

    finally:
        with Finally("I drop the user if exists"):
            node.query(f"DROP USER IF EXISTS {user_name} ON CLUSTER {cluster}")


@TestStep(Given)
def grant_privilege(self, privilege, object, user, node=None):
    """Grant privilege on table/view/database to user."""
    if node is None:
        node = self.context.node

    node.query(f"GRANT {privilege} ON {object} TO {user}")


@TestStep(Given)
def revoke_privilege(self, privilege, object, user, node=None):
    """Revoke privilege on table/view/database from user."""
    if node is None:
        node = self.context.node

    node.query(f"REVOKE {privilege} ON {object} FROM {user}")


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
def grant_privileges_on_cluster(self, cluster, privileges, object, user, node=None):
    """Grant privileges on table/view/database to user on cluster."""
    if node is None:
        node = self.context.node

    for privilege in privileges:
        node.query(f"GRANT ON CLUSTER {cluster} {privilege} ON {object} TO {user}")


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
            if cluster is not None:
                node.query(f"DROP TABLE IF EXISTS {view_name} ON CLUSTER {cluster}")
            else:
                node.query(f"DROP TABLE IF EXISTS {view_name}")


@TestStep(Given)
def create_materialized_view_with_join(
    self,
    source_table_name_1,
    source_table_name_2,
    source_table_name_3,
    join_option="INNER JOIN",
    node=None,
    view_name=None,
    target_table_name=None,
    definer=None,
    sql_security=None,
    if_not_exists=False,
    cluster=None,
    settings=None,
    exitcode=None,
    message=None,
    order_by=None,
    engine=None,
    populate=False,
):
    """Create materialized view with join clause."""

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

    if join_option == "CROSS JOIN":
        query += f"""
            AS SELECT {source_table_name_1}.x as x, {source_table_name_2}.y as y
            FROM {source_table_name_1} CROSS JOIN {source_table_name_2}
            """
    elif "ASOF" in join_option:
        query += f"""
            AS SELECT {source_table_name_1}.x as x, {source_table_name_2}.y as y
            FROM {source_table_name_1} {join_option} {source_table_name_2} 
            ON {source_table_name_1}.x == {source_table_name_2}.x AND {source_table_name_2}.x <= {source_table_name_1}.x
            """
    elif join_option == "PASTE JOIN":
        query += f"""
            AS SELECT x,y
            FROM
                (
                    SELECT {source_table_name_1}.x as x
                    FROM {source_table_name_1} 
                    INNER JOIN {source_table_name_3} 
                    ON {source_table_name_1}.x = {source_table_name_3}.x
                ) a
            {join_option}
                (
                    SELECT y 
                    FROM {source_table_name_2} 
                    WHERE x > 3
                ) b
            """
    else:
        query += f"""
            AS SELECT {source_table_name_1}.x as x, {source_table_name_2}.y as y
            FROM {source_table_name_1} {join_option} {source_table_name_2} 
            ON {source_table_name_1}.x == {source_table_name_2}.x
            """

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
def create_normal_view_with_join(
    self,
    source_table_name_1,
    source_table_name_2,
    source_table_name_3,
    join_option="INNER JOIN",
    node=None,
    view_name=None,
    definer=None,
    sql_security=None,
    if_not_exists=False,
    cluster=None,
    settings=None,
    exitcode=None,
    message=None,
):
    """Create normal view with join clause."""

    if node is None:
        node = self.context.node

    if view_name is None:
        view_name = "view_" + getuid()

    query = f"CREATE VIEW "

    if if_not_exists:
        query += "IF NOT EXISTS "

    query += f"{view_name} "

    if cluster is not None:
        query += f"ON CLUSTER {cluster} "

    if definer is not None:
        query += f"DEFINER = {definer} "

    if sql_security is not None:
        query += f"SQL SECURITY {sql_security} "

    if join_option == "CROSS JOIN":
        query += f"""
            AS SELECT {source_table_name_1}.x as x, {source_table_name_2}.y as y
            FROM {source_table_name_1} CROSS JOIN {source_table_name_2}
            """
    elif "ASOF" in join_option:
        query += f"""
            AS SELECT {source_table_name_1}.x as x, {source_table_name_2}.y as y
            FROM {source_table_name_1} {join_option} {source_table_name_2} 
            ON {source_table_name_1}.x == {source_table_name_2}.x AND {source_table_name_2}.x <= {source_table_name_1}.x
            """
    elif join_option == "PASTE JOIN":
        query += f"""
            AS SELECT x,y
            FROM
                (
                    SELECT {source_table_name_1}.x as x
                    FROM {source_table_name_1} 
                    INNER JOIN {source_table_name_3} 
                    ON {source_table_name_1}.x = {source_table_name_3}.x
                ) a
            {join_option}
                (
                    SELECT y 
                    FROM {source_table_name_2} 
                    WHERE x > 3
                ) b
            """
    else:
        query += f"""
            AS SELECT {source_table_name_1}.x as x, {source_table_name_2}.y as y
            FROM {source_table_name_1} {join_option} {source_table_name_2} 
            ON {source_table_name_1}.x == {source_table_name_2}.x
            """

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
    source_table_name,
    view_name=None,
    node=None,
    definer=None,
    sql_security=None,
    if_not_exists=False,
    cluster=None,
    select_columns="*",
):
    """Create view."""

    if node is None:
        node = self.context.node

    query = f"CREATE VIEW "

    if if_not_exists:
        query += "IF NOT EXISTS "

    if view_name is None:
        view_name = "view_" + getuid()

    query += f"{view_name} "

    if cluster is not None:
        query += f"ON CLUSTER {cluster} "

    if definer is not None:
        query += f"DEFINER = {definer} "

    if sql_security is not None:
        query += f"SQL SECURITY {sql_security} "

    query += f"AS SELECT {select_columns} FROM {source_table_name}"

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
    node=None,
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
        return add_config(config, restart=restart, modify=modify, user=user, node=node)


@TestStep(Given)
def create_distributed_table(
    self,
    nodes=None,
    table_name=None,
    dist_table_name=None,
    row_number=5,
):
    """Create distributed table on cluster with 2 shards and only one replica on 2 of the nodes.
    Insert row_number rows into the table on first and second node."""

    if table_name is None:
        table_name = "table_" + getuid()

    if dist_table_name is None:
        dist_table_name = "dist_table_" + getuid()

    if nodes is None:
        nodes = self.context.nodes

    node_1 = nodes[0]
    node_2 = nodes[1]

    try:
        node_1.query(
            f"""
            CREATE TABLE {table_name} ON CLUSTER sharded_cluster12
            (  
            x UInt64,  
            column1 String  
            )  
            ENGINE = MergeTree  
            ORDER BY column1
            """
        )
        node_1.query(
            f"""
            INSERT INTO {table_name} SELECT number, toString(number) FROM numbers({row_number})
            """
        )
        node_2.query(
            f"""
            INSERT INTO {table_name} SELECT number, toString(number) FROM numbers({row_number})
            """
        )
        node_1.query(
            f"""
            CREATE TABLE {dist_table_name} (
                x UInt64,
                column1 String
            )
            ENGINE = Distributed(sharded_cluster12,default,{table_name}, rand())
            """
        )
        yield table_name, dist_table_name

    finally:
        with Finally("I drop the table if exists"):
            node_1.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER sharded_cluster12 SYNC"
            )
            node_1.query(f"DROP TABLE IF EXISTS {dist_table_name}")


def get_name(items):
    try:
        return [item.__name__ for item in items]
    except AttributeError:
        raise AttributeError(f"The object does not have a __name__ attribute.")
