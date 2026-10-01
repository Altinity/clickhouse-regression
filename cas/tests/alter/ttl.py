"""Table TTL ALTER TABLE scenarios for CAS MergeTree."""

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import *

TTL_COLUMNS = (
    "partition_column UInt8, id UInt64, value Int64, "
    "string_column String DEFAULT '', ts DateTime"
)


@TestStep(Given)
def ttl_table(self, suffix):
    """Create a table with a timestamp column; caller inserts the rows."""
    table_name = f"cas_alter_ttl_{suffix}_{getuid()}"
    create_filled_alter_table(table_name=table_name, columns=TTL_COLUMNS, insert=False)
    return table_name


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_TTL("1.0"))
def modify_materialize_remove(self):
    """MODIFY / MATERIALIZE / REMOVE TTL apply as on non-CAS MergeTree."""
    node = self.context.node

    with Given("create a table"):
        table = ttl_table(suffix="round_trip")

    with When("insert expired and live rows"):
        node.query(
            f"INSERT INTO {table} "
            f"(partition_column, id, value, string_column, ts) "
            "SELECT 1, number, number, '', toDateTime('2000-01-01') FROM numbers(5)"
        )
        node.query(
            f"INSERT INTO {table} "
            f"(partition_column, id, value, string_column, ts) "
            "SELECT 2, number, number, '', now() FROM numbers(5)"
        )

    with And("I set table TTL and materialize it"):
        modify_ttl(table_name=table, expression="ts + INTERVAL 1 DAY")
        materialize_ttl(table_name=table)

    with Then("expired rows are gone and live rows remain"):
        result = node.query(
            f"SELECT partition_column, count() FROM {table} "
            f"GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert result == "2\t5", error(result)

    with And("I remove table TTL"):
        remove_ttl(table_name=table)

    with And("SHOW CREATE no longer declares TTL"):
        create_query = show_create_table(node, table)
        assert "TTL" not in create_query, error(create_query)


@TestFeature
@Name("ttl")
def feature(self):
    """Table TTL ALTER TABLE operations on CAS."""
    for scenario in loads(current_module(), Scenario):
        scenario()
