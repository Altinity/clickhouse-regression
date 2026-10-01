"""Column statistics ALTER TABLE scenarios for CAS MergeTree."""

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import *


@TestStep(Given)
def statistics_table(self, suffix):
    """Create and fill an isolated table for one statistics ALTER scenario."""
    table_name = f"cas_alter_statistics_{suffix}_{getuid()}"
    create_filled_alter_table(table_name=table_name)
    return table_name


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Statistics("1.0"))
def add_materialize_drop(self):
    """ADD / MATERIALIZE / DROP STATISTICS round-trip on CAS."""
    with Given("create a table"):
        table = statistics_table(suffix="add_drop")

    with When("add, materialize, then drop tdigest statistics"):
        add_statistics(table_name=table, definition="value TYPE tdigest")
        materialize_statistics(table_name=table, columns="value")

    with And("SHOW CREATE declares the statistic"):
        create_query = show_create_table(self.context.node, table)
        assert "statistics(tdigest)" in create_query.lower(), error(create_query)

    with And("drop the statistic"):
        drop_statistics(table_name=table, columns="value")

    with Then("the statistic is gone and rows remain"):
        create_query = show_create_table(self.context.node, table)
        assert "tdigest" not in create_query.lower(), error(create_query)
        result = self.context.node.query(f"SELECT count() FROM {table}").output.strip()
        assert result == "10", error(result)


@TestFeature
@Name("statistics")
def feature(self):
    """Column-statistics ALTER TABLE operations on CAS."""
    for scenario in loads(current_module(), Scenario):
        scenario()
