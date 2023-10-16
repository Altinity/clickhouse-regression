from testflows.core import *


def create_table(
    table_name,
    columns=None,
    engine=None,
    primary_key=None,
    constraints=None,
    if_not_exists=False,
    db=None,
    cluster=None,
    as_select_query=None,
    as_table_function=None,
    as_table=None,
    order_by=None,
    comment=None,
):
    """
    Generates a query to create a table in ClickHouse.
    Parameters:
        table_name (str): Name of the table to be created.
        columns (list of dict, optional): Definition of columns for the table.
        engine (str, optional): Name of the table engine.
        order_by (str, optional): The value the table will be ordered by. Required if the engine is MergeTree.
        primary_key (str, optional): Primary key of the table.
        constraints (list of str, optional): List of constraints.
        if_not_exists (bool, optional): Whether to include IF NOT EXISTS clause.
        db (str, optional): Name of the database.
        cluster (str, optional): Name of the cluster.
        as_select_query (str, optional): SELECT query to create a table based on its result.
        as_table_function (str, optional): Table function to create a table based on its result.
        as_table (str, optional): Another table to copy the schema from.
        comment (str, optional): Comment for the table.

    Returns:
        str: ClickHouse query to create a table.
    """
    query = "CREATE TABLE"
    if if_not_exists:
        query += " IF NOT EXISTS"
    if db:
        query += f" {db}."
        query += f"{table_name}"
    else:
        query += f" {table_name}"

    if cluster:
        query += f" ON CLUSTER {cluster}"

    if columns:
        query += " (\n"
        for col in columns:
            query += f"    {col['name']} {col['type']}"
            for modifier in [
                "null",
                "default",
                "materialized",
                "alias",
                "codec",
                "ttl",
                "comment",
            ]:
                if modifier in col:
                    query += f" {modifier.upper()} {col[modifier]}"
            query += ",\n"
        if primary_key:
            query += f"    PRIMARY KEY({primary_key}),\n"
        if constraints:
            for constraint in constraints:
                query += f"    CONSTRAINT {constraint},\n"
        query = query.rstrip(",\n") + "\n) "
    elif as_table:
        query += f" AS {as_table}"
    elif as_table_function:
        query += f" AS {as_table_function}()"
    elif as_select_query:
        query += f" AS {as_select_query}"

    if engine:
        query += f" ENGINE = {engine}"

    if order_by:
        query += f" ORDER BY {order_by}"
    if comment:
        query += f" COMMENT '{comment}'"

    query += ";"

    return query


@TestStep
def create_merge_tree(
    self,
    node,
    name: str,
    columns: list[dict],
    order_by: str,
    if_not_exists: bool,
    db: str,
    comment: str,
    primary_key=None,
):
    with Given(
        "I execute a ClickHouse query to create a table with a MergeTree engine"
    ):
        node.query(
            create_table(
                table_name=name,
                columns=columns,
                engine="MergeTree",
                order_by=order_by,
                primary_key=primary_key,
                if_not_exists=if_not_exists,
                db=db,
                comment=comment,
            )
        )


@TestStep
def create_replicated_merge_tree(
    self,
    node,
    name: str,
    columns: list[dict],
    order_by: str,
    if_not_exists: bool,
    db: str,
    comment: str,
    primary_key=None,
):
    with Given(
        "I execute a ClickHouse query to create a table with a ReplicatedMergeTree engine"
    ):
        node.query(
            create_table(
                table_name=name,
                columns=columns,
                engine="ReplicatedMergeTree",
                order_by=order_by,
                primary_key=primary_key,
                if_not_exists=if_not_exists,
                db=db,
                comment=comment,
            )
        )


columns_example = [
    {"name": "id", "type": "UInt64"},
    {"name": "name", "type": "String", "null": "NULL", "comment": "'user name'"},
    {"name": "created_at", "type": "DateTime", "default": "now()"},
]
