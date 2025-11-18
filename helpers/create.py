from testflows.core import *

from alter.table.replace_partition.common import (
    create_partitions_with_random_uint64,
    create_partitions_for_collapsing_merge_tree,
)


@TestStep(Given)
def create_table(
    self,
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
    settings=None,
    partition_by=None,
    stop_merges=False,
    query_settings=None,
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
        settings (list, optional): query level settings.
        partition_by (str, optional): partition key for the MergeTree tables with partitions.

        Example how to define columns:
            columns_example = [
                {"name": "id", "type": "UInt64"},
                {"name": "name", "type": "String", "null": "NULL", "comment": "'user name'"},
                {"name": "created_at", "type": "DateTime", "default": "now()"},
            ]
    """
    node = current().context.node

    if settings is None:
        settings = [("allow_suspicious_low_cardinality_types", 1)]

    try:
        query = "CREATE TABLE"
        if if_not_exists:
            query += " IF NOT EXISTS"
        if db is not None:
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
        if partition_by:
            query += f" PARTITION BY {partition_by}"
        if comment:
            query += f" COMMENT '{comment}'"

        if query_settings:
            query += f" SETTINGS {query_settings}"

        query += ";"

        if stop_merges:
            query += f" SYSTEM STOP MERGES {table_name};"

        node.query(query)
        yield

    finally:
        with Finally(f"drop the table {table_name}"):
            query = f"DROP TABLE IF EXISTS {table_name}"
            if cluster:
                query += f" ON CLUSTER {cluster}"
            node.query(query)

    return query


@TestStep(Given)
def create_merge_tree_table(
    self,
    table_name: str,
    columns: list[dict],
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
    partition_by: str = None,
    cluster: str = None,
    stop_merges: bool = False,
    query_settings: str = None,
):
    """Create a table with the MergeTree engine."""
    create_table(
        table_name=table_name,
        columns=columns,
        engine="MergeTree",
        order_by=order_by,
        primary_key=primary_key,
        if_not_exists=if_not_exists,
        db=db,
        comment=comment,
        partition_by=partition_by,
        cluster=cluster,
        stop_merges=stop_merges,
        query_settings=query_settings,
    )


@TestStep(Given)
def create_replacing_merge_tree_table(
    self,
    table_name: str,
    columns: list[dict],
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
    partition_by: str = None,
    cluster: str = None,
    stop_merges: bool = False,
):
    """Create a table with the ReplacingMergeTree engine."""
    create_table(
        table_name=table_name,
        columns=columns,
        engine="ReplacingMergeTree",
        order_by=order_by,
        primary_key=primary_key,
        if_not_exists=if_not_exists,
        db=db,
        comment=comment,
        partition_by=partition_by,
        cluster=cluster,
        stop_merges=stop_merges,
    )


@TestStep(Given)
def create_summing_merge_tree_table(
    self,
    table_name: str,
    columns: list[dict],
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
    partition_by: str = None,
    cluster: str = None,
    stop_merges: bool = False,
):
    """Create a table with the SummingMergeTree engine."""
    create_table(
        table_name=table_name,
        columns=columns,
        engine="SummingMergeTree",
        order_by=order_by,
        primary_key=primary_key,
        if_not_exists=if_not_exists,
        db=db,
        comment=comment,
        partition_by=partition_by,
        cluster=cluster,
        stop_merges=stop_merges,
    )


@TestStep(Given)
def create_aggregating_merge_tree_table(
    self,
    table_name: str,
    columns: list[dict],
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
    partition_by: str = None,
    cluster: str = None,
    stop_merges: bool = False,
):
    """Create a table with the AggregatingMergeTree engine."""
    create_table(
        table_name=table_name,
        columns=columns,
        engine="AggregatingMergeTree",
        order_by=order_by,
        primary_key=primary_key,
        if_not_exists=if_not_exists,
        db=db,
        comment=comment,
        partition_by=partition_by,
        cluster=cluster,
        stop_merges=stop_merges,
    )


@TestStep(Given)
def create_collapsing_merge_tree_table(
    self,
    table_name: str,
    columns: list[dict],
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
    partition_by: str = None,
    sign: str = "Sign",
    cluster: str = None,
    stop_merges: bool = False,
):
    """Create a table with the CollapsingMergeTree engine.

    Description:
        Sign must be an Int8 datatype with either value of 1 or -1.
    """
    create_table(
        table_name=table_name,
        columns=columns,
        engine=f"CollapsingMergeTree({sign})",
        order_by=order_by,
        primary_key=primary_key,
        if_not_exists=if_not_exists,
        db=db,
        comment=comment,
        partition_by=partition_by,
        cluster=cluster,
        stop_merges=stop_merges,
    )


@TestStep(Given)
def create_versioned_collapsing_merge_tree_table(
    self,
    table_name: str,
    columns: list[dict],
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
    partition_by: str = None,
    sign: str = "Sign",
    version: str = "Version",
    cluster: str = None,
    stop_merges: bool = False,
):
    """Create a table with the VersionedCollapsingMergeTree engine.

    Description:
        Sign must be an Int8 datatype with either value of 1 or -1.
        Version can be any UInt datatype value
    """
    create_table(
        table_name=table_name,
        columns=columns,
        engine=f"VersionedCollapsingMergeTree({sign}, {version})",
        order_by=order_by,
        primary_key=primary_key,
        if_not_exists=if_not_exists,
        db=db,
        comment=comment,
        partition_by=partition_by,
        cluster=cluster,
        stop_merges=stop_merges,
    )


@TestStep(Given)
def create_graphite_merge_tree_table(
    self,
    table_name: str,
    columns: list[dict],
    config: str,
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
    partition_by: str = None,
    cluster: str = None,
    stop_merges: bool = False,
):
    """Create a table with the GraphiteMergeTree engine.

    Description:
        config should be a name of the section in the configuration file, where are the rules of rollup set.
    """
    create_table(
        table_name=table_name,
        columns=columns,
        engine=f"GraphiteMergeTree('{config}')",
        order_by=order_by,
        primary_key=primary_key,
        if_not_exists=if_not_exists,
        db=db,
        comment=comment,
        partition_by=partition_by,
        cluster=cluster,
        stop_merges=stop_merges,
    )


@TestStep(Given)
def create_replicated_merge_tree_table(
    self,
    table_name: str,
    columns: list[dict] = None,
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
    partition_by: str = "p",
    cluster: str = None,
    stop_merges: bool = False,
    query_settings: str = None,
):
    """Create a table with the MergeTree engine."""
    if columns is None:
        columns = [
            {"name": "p", "type": "Int8"},
            {"name": "i", "type": "UInt64"},
            {"name": "extra", "type": "Int8"},
        ]

    create_table(
        table_name=table_name,
        columns=columns,
        engine=f"ReplicatedMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica0')",
        order_by=order_by,
        primary_key=primary_key,
        if_not_exists=if_not_exists,
        db=db,
        comment=comment,
        partition_by=partition_by,
        cluster=cluster,
        stop_merges=stop_merges,
        query_settings=query_settings,
    )


@TestStep(Given)
def partitioned_merge_tree_table(
    self,
    table_name,
    partition_by,
    columns,
    cluster=None,
    stop_merges=False,
    populate=True,
    number_of_partitions=5,
    number_of_parts=1,
    number_of_values=3,
    query_settings=None,
):
    """Create a MergeTree table partitioned by a specific column."""
    with By(f"creating a partitioned {table_name} table with a MergeTree engine"):
        create_merge_tree_table(
            table_name=table_name,
            columns=columns,
            partition_by=partition_by,
            cluster=cluster,
            stop_merges=stop_merges,
            query_settings=query_settings,
        )

    if populate:
        with And("populating it with the data needed to create multiple partitions"):
            create_partitions_with_random_uint64(
                table_name=table_name,
                number_of_partitions=number_of_partitions,
                number_of_parts=number_of_parts,
                number_of_values=number_of_values,
            )

    return table_name


@TestStep(Given)
def partitioned_replicated_merge_tree_table(
    self,
    table_name,
    partition_by,
    columns=None,
    cluster=None,
    stop_merges=False,
    populate=True,
    number_of_partitions=5,
    number_of_parts=1,
    query_settings=None,
):
    """Create a ReplicatedMergeTree table partitioned by a specific column."""
    with By(
        f"creating a partitioned {table_name} table with a ReplicatedMergeTree engine"
    ):
        create_replicated_merge_tree_table(
            table_name=table_name,
            columns=columns,
            partition_by=partition_by,
            cluster=cluster,
            stop_merges=stop_merges,
            query_settings=query_settings,
        )

    if populate:
        with And("populating it with the data needed to create multiple partitions"):
            create_partitions_with_random_uint64(
                table_name=table_name,
                number_of_partitions=number_of_partitions,
                number_of_parts=number_of_parts,
            )

    return table_name


@TestStep(Given)
def create_replicated_partitioned_table_with_compact_and_wide_parts(
    self,
    table_name: str,
    min_rows_for_wide_part: int = 10,
    min_bytes_for_wide_part: int = 100,
    columns: list[dict] = None,
    partition_by: str = "p",
    cluster: str = None,
    stop_merges: bool = False,
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
):
    """Create a ReplicatedMergeTree table that has specific settings in order
    to get both wide and compact parts."""
    if columns is None:
        columns = [
            {"name": "p", "type": "Int8"},
            {"name": "i", "type": "UInt64"},
        ]

    query_settings = f"min_rows_for_wide_part={min_rows_for_wide_part}, min_bytes_for_wide_part={min_bytes_for_wide_part}"

    create_table(
        table_name=table_name,
        columns=columns,
        engine=f"ReplicatedMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica0')",
        order_by=order_by,
        primary_key=primary_key,
        if_not_exists=if_not_exists,
        db=db,
        comment=comment,
        partition_by=partition_by,
        cluster=cluster,
        stop_merges=stop_merges,
        query_settings=query_settings,
    )


@TestStep(Given)
def partitioned_replacing_merge_tree_table(
    self,
    table_name,
    partition_by,
    columns,
    cluster=None,
    stop_merges=False,
    populate=True,
    number_of_partitions=5,
    number_of_parts=1,
):
    """Create a ReplacingMergeTree table partitioned by a specific column."""
    with By(
        f"creating a partitioned {table_name} table with a ReplacingMergeTree engine"
    ):
        create_replacing_merge_tree_table(
            table_name=table_name,
            columns=columns,
            partition_by=partition_by,
            cluster=cluster,
            stop_merges=stop_merges,
        )

    if populate:
        with And("populating it with the data needed to create multiple partitions"):
            create_partitions_with_random_uint64(
                table_name=table_name,
                number_of_partitions=number_of_partitions,
                number_of_parts=number_of_parts,
            )

    return table_name


@TestStep(Given)
def partitioned_summing_merge_tree_table(
    self,
    table_name,
    partition_by,
    columns,
    cluster=None,
    stop_merges=False,
    populate=True,
    number_of_partitions=5,
    number_of_parts=1,
):
    """Create a SummingMergeTree table partitioned by a specific column."""
    with By(
        f"creating a partitioned {table_name} table with a SummingMergeTree engine"
    ):
        create_aggregating_merge_tree_table(
            table_name=table_name,
            columns=columns,
            partition_by=partition_by,
            cluster=cluster,
            stop_merges=stop_merges,
        )

    if populate:
        with And("populating it with the data needed to create multiple partitions"):
            create_partitions_with_random_uint64(
                table_name=table_name,
                number_of_partitions=number_of_partitions,
                number_of_parts=number_of_parts,
            )

    return table_name


@TestStep(Given)
def partitioned_collapsing_merge_tree_table(
    self,
    table_name,
    partition_by,
    columns,
    cluster=None,
    stop_merges=False,
    populate=True,
    number_of_partitions=1,
    number_of_parts=1,
):
    """Create a CollapsingMergeTree table partitioned by a specific column."""
    with By(
        f"creating a partitioned {table_name} table with a CollapsingMergeTree engine"
    ):
        create_collapsing_merge_tree_table(
            table_name=table_name,
            columns=columns,
            partition_by=partition_by,
            sign="p",
            cluster=cluster,
            stop_merges=stop_merges,
        )

    if populate:
        with And("populating it with the data needed to create multiple partitions"):
            create_partitions_for_collapsing_merge_tree(
                table_name=table_name,
                number_of_partitions=number_of_partitions,
                number_of_parts=number_of_parts,
            )

    return table_name


@TestStep(Given)
def partitioned_versioned_collapsing_merge_tree_table(
    self,
    table_name,
    partition_by,
    columns,
    cluster=None,
    stop_merges=False,
    populate=True,
    number_of_partitions=1,
    number_of_parts=1,
):
    """Create a VersionedCollapsingMergeTree table partitioned by a specific column."""
    with By(
        f"creating a partitioned {table_name} table with a VersionedCollapsingMergeTree engine"
    ):
        create_versioned_collapsing_merge_tree_table(
            table_name=table_name,
            columns=columns,
            partition_by=partition_by,
            sign="p",
            version="i",
            cluster=cluster,
            stop_merges=stop_merges,
        )

    if populate:
        with And("populating it with the data needed to create multiple partitions"):
            create_partitions_with_random_uint64(
                table_name=table_name,
                number_of_partitions=number_of_partitions,
                number_of_parts=number_of_parts,
            )

    return table_name


@TestStep(Given)
def partitioned_aggregating_merge_tree_table(
    self,
    table_name,
    partition_by,
    columns,
    cluster=None,
    stop_merges=False,
    populate=True,
    number_of_partitions=5,
    number_of_parts=1,
):
    """Create a AggregatingMergeTree table partitioned by a specific column."""
    with By(
        f"creating a partitioned {table_name} table with a AggregatingMergeTree engine"
    ):
        create_summing_merge_tree_table(
            table_name=table_name,
            columns=columns,
            partition_by=partition_by,
            cluster=cluster,
            stop_merges=stop_merges,
        )

    if populate:
        with And("populating it with the data needed to create multiple partitions"):
            create_partitions_with_random_uint64(
                table_name=table_name,
                number_of_partitions=number_of_partitions,
                number_of_parts=number_of_parts,
            )

    return table_name


@TestStep(Given)
def partitioned_graphite_merge_tree_table(
    self,
    table_name,
    partition_by,
    columns,
    cluster=None,
    stop_merges=False,
    populate=True,
    number_of_partitions=5,
    number_of_parts=1,
):
    """Create a GraphiteMergeTree table partitioned by a specific column."""
    with By(
        f"creating a partitioned {table_name} table with a GraphiteMergeTree engine"
    ):
        create_graphite_merge_tree_table(
            table_name=table_name,
            columns=columns,
            partition_by=partition_by,
            config="graphite_rollup_example",
            cluster=cluster,
            stop_merges=stop_merges,
        )

    if populate:
        with And("populating it with the data needed to create multiple partitions"):
            create_partitions_with_random_uint64(
                table_name=table_name,
                number_of_partitions=number_of_partitions,
                number_of_parts=number_of_parts,
            )

    return table_name
