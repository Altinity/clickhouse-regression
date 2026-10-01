"""ORDER BY and SAMPLE BY ALTER TABLE scenarios for CAS MergeTree."""

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import *

# Enough rows, with a small granule, that SAMPLE 0.1 can skip most of the table.
SAMPLE_ROWS = 2000


def keys_table(self, suffix):
    """Create and fill an isolated table for one key ALTER scenario."""
    table_name = f"cas_alter_keys_{suffix}_{getuid()}"
    create_filled_alter_table(table_name=table_name)
    return table_name


def sample_table(self):
    """Hash-ordered table large enough for sampling to skip granules."""
    table_name = f"cas_alter_keys_sample_{getuid()}"
    create_cas_merge_tree_table(
        table_name=table_name,
        columns="id UInt64, value UInt64",
        partition_by="tuple()",
        order_by="intHash32(id)",
        extra_settings=[
            "index_granularity = 128",
            "index_granularity_bytes = 0",
        ],
    )
    self.context.node.query(
        f"INSERT INTO {table_name} SELECT number, number FROM numbers({SAMPLE_ROWS})"
    )
    return table_name


def sort_prefix_and_result(node, table, order_by):
    """Return the read-in-order prefix and the requested ORDER BY from EXPLAIN.

    When the prefix equals the result, the sorting key already satisfies the
    query and no residual columns are sorted.
    """
    explain = node.query(
        "EXPLAIN PLAN actions = 1 "
        f"SELECT * FROM {table} ORDER BY {order_by}",
        settings=[("optimize_read_in_order", 1)],
    ).output
    prefix = result = None
    for line in explain.splitlines():
        stripped = line.strip()
        if stripped.startswith("Prefix sort description:"):
            prefix = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Result sort description:"):
            result = stripped.split(":", 1)[1].strip()
    assert prefix and result, error(explain)
    return prefix, result


def finished_read_rows(node, sql):
    """Run ``sql`` and return its output plus logged read_rows."""
    query_id = f"cas-alter-keys-{getuid()}"
    output = node.query(
        sql,
        settings=[("use_query_cache", 0)],
        query_id=query_id,
    ).output.strip()
    node.query("SYSTEM FLUSH LOGS")
    read_rows = node.query(
        "SELECT read_rows FROM system.query_log "
        f"WHERE query_id = '{query_id}' AND type = 'QueryFinish' "
        "ORDER BY event_time_microseconds DESC LIMIT 1"
    ).output.strip()
    assert read_rows, error(f"query log has no QueryFinish entry for {query_id}")
    return output, int(read_rows)


def assert_sampling_rejected(node, table):
    """SAMPLE fails when the table has no sampling key."""
    result = node.query(f"SELECT count() FROM {table} SAMPLE 0.1", no_checks=True)
    assert result.exitcode != 0, error(result.output)
    assert "SAMPLING_NOT_SUPPORTED" in result.output, error(result.output)


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_OrderBy("1.0"))
def order_by(self):
    """MODIFY ORDER BY extends the key that read-in-order uses."""
    table = keys_table(self, "order_by")
    node = self.context.node

    with Given("add a column and include it in ORDER BY"):
        modify_order_by(
            table_name=table,
            extra_alters="ADD COLUMN extra UInt64",
            expression="(partition_column, id, extra)",
        )

    with Then("read-in-order already satisfies ORDER BY the new sorting key"):
        prefix, result = sort_prefix_and_result(
            node, table, "partition_column, id, extra"
        )
        assert prefix == result, error(f"prefix={prefix}\nresult={result}")
        assert "extra" in prefix, error(prefix)

    with And("a column outside the sorting key still needs a residual sort"):
        prefix, result = sort_prefix_and_result(
            node, table, "partition_column, id, value"
        )
        assert prefix != result, error(f"prefix={prefix}\nresult={result}")
        assert "value" not in prefix, error(prefix)

    with And("the primary key is unchanged and stored values are intact"):
        keys = node.query(
            "SELECT sorting_key, primary_key FROM system.tables "
            f"WHERE database = currentDatabase() AND name = '{table}'"
        ).output.strip()
        assert keys == "partition_column, id, extra\tpartition_column, id", error(keys)
        values = node.query(
            f"SELECT count(), sum(value) FROM {table}"
        ).output.strip()
        assert values == "10\t20", error(values)


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_SampleBy("1.0"))
def sample_by(self):
    """MODIFY SAMPLE BY makes SAMPLE skip granules; REMOVE turns it off."""
    table = sample_table(self)
    node = self.context.node

    with Given("sampling is rejected before a sampling key exists"):
        assert_sampling_rejected(node, table)

    with When("I set SAMPLE BY to the primary key"):
        modify_sample_by(table_name=table, expression="intHash32(id)")

    with Then("SAMPLE 0.1 reads fewer rows than a full scan"):
        full, full_read_rows = finished_read_rows(
            node, f"SELECT sum(value) FROM {table}"
        )
        expected_sum = str(SAMPLE_ROWS * (SAMPLE_ROWS - 1) // 2)
        assert full == expected_sum, error(full)
        assert full_read_rows == SAMPLE_ROWS, error(full_read_rows)

        sampled, sampled_read_rows = finished_read_rows(
            node, f"SELECT count() FROM {table} SAMPLE 0.1"
        )
        assert 0 < int(sampled) < SAMPLE_ROWS, error(sampled)
        assert sampled_read_rows * 2 < full_read_rows, error(
            f"sample read {sampled_read_rows} rows, full scan read {full_read_rows}"
        )

    with And("SAMPLE 0.5 and its offset partition the table"):
        left = int(
            node.query(f"SELECT count() FROM {table} SAMPLE 0.5").output.strip()
        )
        right = int(
            node.query(
                f"SELECT count() FROM {table} SAMPLE 0.5 OFFSET 0.5"
            ).output.strip()
        )
        assert left > 0 and right > 0, error(f"{left}, {right}")
        assert left + right == SAMPLE_ROWS, error(f"{left} + {right}")

    with When("I remove SAMPLE BY"):
        remove_sample_by(table_name=table)

    with Then("sampling is rejected again and every row remains"):
        assert_sampling_rejected(node, table)
        count = node.query(f"SELECT count() FROM {table}").output.strip()
        assert count == str(SAMPLE_ROWS), error(count)


@TestFeature
@Name("keys")
def feature(self):
    """Sorting-key and sampling-key ALTER TABLE operations on CAS."""
    for scenario in loads(current_module(), Scenario):
        scenario()
