from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import *


@TestStep(Given)
def index_table(self, suffix):
    """Create and fill an isolated table for one index ALTER scenario."""
    table_name = f"cas_alter_index_{suffix}_{getuid()}"
    create_filled_alter_table(table_name=table_name)
    return table_name


def count_and_read_rows(node, table, condition, index_name=None):
    """Run a count query and return its result and logged read_rows."""
    query_id = f"cas-alter-index-{getuid()}"
    settings = [
        ("use_query_cache", 0),
        ("use_statistics_for_part_pruning", 0),
    ]
    if index_name is not None:
        settings.append(("force_data_skipping_indices", index_name))

    result = node.query(
        f"SELECT count() FROM {table} WHERE {condition}",
        settings=settings,
        query_id=query_id,
    ).output.strip()
    node.query("SYSTEM FLUSH LOGS")
    read_rows = node.query(
        "SELECT read_rows FROM system.query_log "
        f"WHERE query_id = '{query_id}' AND type = 'QueryFinish' "
        "ORDER BY event_time_microseconds DESC LIMIT 1"
    ).output.strip()
    assert read_rows, error(f"query log has no QueryFinish entry for {query_id}")
    return result, int(read_rows)


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Index("1.0"))
def add_materialize_drop(self):
    """Check ADD / MATERIALIZE / DROP INDEX round-trip on CAS."""
    node = self.context.node

    with Given("create a table"):
        table = index_table(suffix="add_drop")

    with And("a predicate outside the data range requires a full scan"):
        result, unindexed_read_rows = count_and_read_rows(node, table, "value = 99")
        assert result == "0", error(result)
        assert unindexed_read_rows == 10, error(
            f"expected an unindexed scan to read 10 rows, read {unindexed_read_rows}"
        )

    with When("add and materialize a minmax index"):
        add_index(table_name=table, definition="idx value TYPE minmax GRANULARITY 1")
        materialize_index(table_name=table, index_name="idx")

    with And("queries use the index and it skips all non-matching granules"):
        result, indexed_read_rows = count_and_read_rows(
            node, table, "value = 99", index_name="idx"
        )
        assert result == "0", error(result)
        assert indexed_read_rows == 0, error(
            f"expected idx to skip every row, read {indexed_read_rows}"
        )

    with And("the forced index returns matching rows correctly"):
        result, indexed_read_rows = count_and_read_rows(
            node, table, "value = 3", index_name="idx"
        )
        assert result == "2", error(result)
        assert indexed_read_rows > 0, error(
            f"expected the matching granules to be read, read {indexed_read_rows}"
        )

    with And("the index is present in table metadata"):
        create_query = show_create_table(node, table)
        assert "INDEX idx value TYPE minmax" in create_query, error(create_query)

    with And("drop the index"):
        drop_index(table_name=table, index_name="idx")

    with Then("the index is gone and rows remain"):
        create_query = show_create_table(node, table)
        assert "INDEX idx" not in create_query, error(create_query)
        result = node.query(f"SELECT count() FROM {table}").output.strip()
        assert result == "10", error(result)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Alter_Index("1.0"),
    RQ_SRS_048_CAS_Partition_ClearIndex("1.0"),
)
def clear_in_partition(self):
    """Check that CLEAR INDEX IN PARTITION removes index files but keeps the definition."""
    node = self.context.node

    with Given("create a table"):
        table = index_table(suffix="clear_partition")

    with And("an absent value requires reading all rows in partition 1"):
        result, unindexed_read_rows = count_and_read_rows(
            node, table, "partition_column = 1 AND value = 99"
        )
        assert result == "0", error(result)
        assert unindexed_read_rows == 5, error(
            f"expected an unindexed partition scan to read 5 rows, "
            f"read {unindexed_read_rows}"
        )

    with When("add and materialize an index"):
        add_index(table_name=table, definition="idx value TYPE minmax GRANULARITY 1")
        materialize_index(table_name=table, index_name="idx")

    with And("the index skips the non-matching partition granule"):
        result, indexed_read_rows = count_and_read_rows(
            node,
            table,
            "partition_column = 1 AND value = 99",
            index_name="idx",
        )
        assert result == "0", error(result)
        assert indexed_read_rows == 0, error(
            f"expected idx to skip partition 1, read {indexed_read_rows} rows"
        )

    with And("clear the index in partition 1"):
        clear_index(table_name=table, index_name="idx", partition=1)

    with Then("partition 1 is scanned again because its index file is gone"):
        result, cleared_read_rows = count_and_read_rows(
            node,
            table,
            "partition_column = 1 AND value = 99",
            index_name="idx",
        )
        assert result == "0", error(result)
        assert cleared_read_rows == unindexed_read_rows, error(
            f"expected cleared partition to read {unindexed_read_rows} rows, "
            f"read {cleared_read_rows}"
        )

    with And("the index definition remains and data is readable"):
        create_query = show_create_table(node, table)
        assert "INDEX idx value TYPE minmax" in create_query, error(create_query)
        result = node.query(f"SELECT count() FROM {table}").output.strip()
        assert result == "10", error(result)


@TestFeature
@Name("index")
def feature(self):
    """Skip-index ALTER TABLE operations on CAS."""
    for scenario in loads(current_module(), Scenario):
        scenario()
