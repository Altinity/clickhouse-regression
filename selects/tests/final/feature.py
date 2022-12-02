from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *


@TestScenario
def select_count(self, table_name, final_modifier, node=None):
    """
    Check select count() with `FINAL` clause equal to force_select_final select.
    """
    if node is None:
        node = current().context.node
    if final_modifier:
        with Given(
            "I check that select with force_select_final equal 'SELECT...FINAL'"
        ):
            assert (
                node.query(f"SELECT count() FROM {table_name} FINAL;").output.strip()
                == node.query(
                    f"SELECT count() FROM {table_name};",
                    settings=[("force_select_final", 1)],
                ).output.strip()
            )


@TestScenario
def select(self, table_name, final_modifier, node=None):
    """
    Check select all data with `FINAL` clause equal to force_select_final select.
    """
    if node is None:
        node = current().context.node
    if final_modifier:
        with Given(
            "I check that select with force_select_final equal 'SELECT...FINAL'"
        ):
            assert (
                node.query(f"SELECT * FROM {table_name} FINAL;").output.strip()
                == node.query(
                    f"SELECT * FROM {table_name};", settings=[("force_select_final", 1)]
                ).output.strip()
            )


@TestFeature
@Name("final")
def feature(self):
    """Check FINAL modifier."""
    self.context.tables = []

    with Given("ReplacingMergeTree table without version"):
        self.context.tables.append(
            create_table(
                engine="ReplacingMergeTree",
                schema="(key Int64, someCol String, eventTime DateTime)",
                final_modifier_available=True,
                name="ReplacingMT_without_ver",
            )
        )

    with Given("ReplacingMergeTree table with version"):
        self.context.tables.append(
            create_table(
                engine="ReplacingMergeTree(eventTime)",
                schema="(key Int64, someCol String, eventTime DateTime)",
                final_modifier_available=True,
                name="ReplacingMT_with_ver",
            )
        )

    with Given("CollapsingMergeTree table"):
        self.context.tables.append(
            create_table(
                engine="CollapsingMergeTree(Sign)",
                schema="( UserID UInt64, PageViews UInt8, Duration UInt8, Sign Int8)",
                final_modifier_available=True,
                name="CollapsingMT",
            )
        )

    with Given("I create AggregatingMergeTree table"):
        self.context.tables.append(
            create_table(
                engine="AggregatingMergeTree",
                schema="(a String, b UInt8, c SimpleAggregateFunction(max, UInt8))",
                final_modifier_available=True,
                name="AggregatingMT",
            )
        )

    with Given("SummingMergeTree tables"):
        pass

    with And("I populate tables with test data"):
        for i in range(len(self.context.tables)):
            self.context.tables[i].insert_test_data()

    for table in self.context.tables:
        for scenario in loads(current_module(), Scenario):
            scenario(
                table_name=table.name, final_modifier=table.final_modifier_available
            )
