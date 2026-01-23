from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import create_replicated_merge_tree_table
from .storage import valid_partition_key_types_columns
from helpers.create import create_replicated_merge_tree_table
from .storage import valid_partition_key_types_columns


@TestStep(Given)
def create_distributed_table(
    self,
    cluster,
    local_table_name,
    distributed_table_name=None,
    sharding_key="rand()",
    node=None,
):
    """Create a Distributed table that points to local tables on a cluster."""
    if node is None:
        node = self.context.node

    if distributed_table_name is None:
        distributed_table_name = f"distributed_{getuid()}"

    node.query(
        f"""
        CREATE TABLE {distributed_table_name} AS {local_table_name}
        ENGINE = Distributed({cluster}, default, {local_table_name}, {sharding_key})
        """,
        exitcode=0,
        steps=True,
    )

    return distributed_table_name


@TestStep(When)
def wait_for_distributed_table_data(self, table_name, expected_count, node=None):
    """Wait for data to be distributed to all shards in a Distributed table."""
    if node is None:
        node = self.context.node

    for attempt in retries(timeout=60, delay=1):
        with attempt:
            result = node.query(
                f"SELECT count() FROM {table_name}",
                exitcode=0,
                steps=True,
            )
            assert int(result.output.strip()) == expected_count, error()


@TestStep(When)
def insert_all_datatypes(self, table_name, rows_per_part=1, num_parts=1, node=None):
    """Insert all datatypes into a MergeTree table."""
    if node is None:
        node = self.context.node

    for part in range(num_parts):
        node.query(
            f"INSERT INTO {table_name} (int8, int16, int32, int64, uint8, uint16, uint32, uint64, date, date32, datetime, datetime64, string, fixedstring) SELECT 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, '13', '14' FROM numbers({rows_per_part})"
        )


@TestStep(Given)
def create_replicated_merge_tree_all_valid_partition_key_types(
    self, column_name, cluster=None, node=None, rows_per_part=1
):
    """Create a MergeTree table with all valid partition key types and both wide and compact parts."""
    if node is None:
        node = self.context.node

    with By("creating a MergeTree table with all data types"):
        table_name = f"table_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=table_name,
            columns=valid_partition_key_types_columns(),
            partition_by=column_name,
            cluster=cluster,
            stop_merges=False,
            query_settings="min_rows_for_wide_part=10",
        )

    with And("I insert compact and wide parts into the table"):
        insert_all_datatypes(
            table_name=table_name,
            rows_per_part=rows_per_part,
            num_parts=self.context.num_parts,
            node=node,
        )

    return table_name


@TestStep(Given)
def create_table_with_alias_column(self, table_name):
    """Create a MergeTree table with ALIAS column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "a", "type": "UInt32"},
            {"name": "arr", "type": "Array(UInt64)"},
            {"name": "arr_1", "type": "UInt64", "alias": "arr[1]"},
        ],
        partition_by="a",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_materialized_column(self, table_name):
    """Create a MergeTree table with MATERIALIZED column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "a", "type": "UInt32"},
            {"name": "arr", "type": "Array(UInt64)"},
            {"name": "arr_1", "type": "UInt64", "materialized": "arr[1]"},
        ],
        partition_by="a",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_ephemeral_and_default_column(self, table_name):
    """Create a MergeTree table with EPHEMERAL and DEFAULT columns."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "name_input", "type": "String", "ephemeral": ""},
            {"name": "name_upper", "type": "String", "default": "upper(name_input)"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_simple_default_column(self, table_name):
    """Create a MergeTree table with simple DEFAULT column (not dependent on EPHEMERAL)."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "value", "type": "UInt32"},
            {"name": "status", "type": "String", "default": "'active'"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_mixed_columns(self, table_name):
    """Create a MergeTree table with mixed ALIAS, MATERIALIZED, and EPHEMERAL columns."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "value", "type": "UInt32"},
            {"name": "tag_input", "type": "String", "ephemeral": ""},
            {"name": "doubled", "type": "UInt64", "alias": "value * 2"},
            {"name": "tripled", "type": "UInt64", "materialized": "value * 3"},
            {"name": "tag", "type": "String", "default": "upper(tag_input)"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_complex_expressions(self, table_name):
    """Create a MergeTree table with complex expressions in computed columns."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "name", "type": "String"},
            {"name": "upper_name", "type": "String", "alias": "upper(name)"},
            {
                "name": "concat_result",
                "type": "String",
                "materialized": "concat(name, '-', toString(id))",
            },
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_json_column(self, table_name):
    """Create a MergeTree table with JSON column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "json_data", "type": "JSON"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_json_column_with_hints(self, table_name):
    """Create a MergeTree table with JSON column that has type hints."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "json_data", "type": "JSON(a.b UInt32, a.c String)"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_nested_column(self, table_name):
    """Create a MergeTree table with Nested column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "nested_data", "type": "Nested(key String, value UInt64)"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_complex_nested_column(self, table_name):
    """Create a MergeTree table with complex Nested column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {
                "name": "nested_data",
                "type": "Nested(name String, age UInt8, scores Array(UInt32))",
            },
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(When)
def insert_all_datatypes(self, table_name, rows_per_part=1, num_parts=1, node=None):
    """Insert all datatypes into a MergeTree table."""
    if node is None:
        node = self.context.node

    for part in range(num_parts):
        node.query(
            f"INSERT INTO {table_name} (int8, int16, int32, int64, uint8, uint16, uint32, uint64, date, date32, datetime, datetime64, string, fixedstring) SELECT 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, '13', '14' FROM numbers({rows_per_part})"
        )


@TestStep(Given)
def create_replicated_merge_tree_all_valid_partition_key_types(
    self, column_name, cluster=None, node=None, rows_per_part=1
):
    """Create a MergeTree table with all valid partition key types and both wide and compact parts."""
    if node is None:
        node = self.context.node

    with By("creating a MergeTree table with all data types"):
        table_name = f"table_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=table_name,
            columns=valid_partition_key_types_columns(),
            partition_by=column_name,
            cluster=cluster,
            stop_merges=False,
            query_settings="min_rows_for_wide_part=10",
        )

    with And("I insert compact and wide parts into the table"):
        insert_all_datatypes(
            table_name=table_name,
            rows_per_part=rows_per_part,
            num_parts=self.context.num_parts,
            node=node,
        )

    return table_name


@TestStep(Given)
def create_table_with_alias_column(self, table_name):
    """Create a MergeTree table with ALIAS column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "a", "type": "UInt32"},
            {"name": "arr", "type": "Array(UInt64)"},
            {"name": "arr_1", "type": "UInt64", "alias": "arr[1]"},
        ],
        partition_by="a",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_materialized_column(self, table_name):
    """Create a MergeTree table with MATERIALIZED column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "a", "type": "UInt32"},
            {"name": "arr", "type": "Array(UInt64)"},
            {"name": "arr_1", "type": "UInt64", "materialized": "arr[1]"},
        ],
        partition_by="a",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_ephemeral_and_default_column(self, table_name):
    """Create a MergeTree table with EPHEMERAL and DEFAULT columns."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "name_input", "type": "String", "ephemeral": ""},
            {"name": "name_upper", "type": "String", "default": "upper(name_input)"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_simple_default_column(self, table_name):
    """Create a MergeTree table with simple DEFAULT column (not dependent on EPHEMERAL)."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "value", "type": "UInt32"},
            {"name": "status", "type": "String", "default": "'active'"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_mixed_columns(self, table_name):
    """Create a MergeTree table with mixed ALIAS, MATERIALIZED, and EPHEMERAL columns."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "value", "type": "UInt32"},
            {"name": "tag_input", "type": "String", "ephemeral": ""},
            {"name": "doubled", "type": "UInt64", "alias": "value * 2"},
            {"name": "tripled", "type": "UInt64", "materialized": "value * 3"},
            {"name": "tag", "type": "String", "default": "upper(tag_input)"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_complex_expressions(self, table_name):
    """Create a MergeTree table with complex expressions in computed columns."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "name", "type": "String"},
            {"name": "upper_name", "type": "String", "alias": "upper(name)"},
            {
                "name": "concat_result",
                "type": "String",
                "materialized": "concat(name, '-', toString(id))",
            },
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_json_column(self, table_name):
    """Create a MergeTree table with JSON column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "json_data", "type": "JSON"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_json_column_with_hints(self, table_name):
    """Create a MergeTree table with JSON column that has type hints."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "json_data", "type": "JSON(a.b UInt32, a.c String)"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_nested_column(self, table_name):
    """Create a MergeTree table with Nested column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "nested_data", "type": "Nested(key String, value UInt64)"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_complex_nested_column(self, table_name):
    """Create a MergeTree table with complex Nested column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {
                "name": "nested_data",
                "type": "Nested(name String, age UInt8, scores Array(UInt32))",
            },
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )
