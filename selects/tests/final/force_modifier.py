from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *


@TestScenario
def select_count(self, node=None):
    """Check select count() with `FINAL` clause equal to force_select_final select."""
    if node is None:
        node = self.context.node

    for table in self.context.tables:
        with Then("I check that select with force_select_final equal 'SELECT...FINAL'"):
            assert (
                node.query(
                    f"SELECT count() FROM {table.name}"
                    f"{' FINAL' if table.final_modifier_available else ''} "
                    f" FORMAT JSONEachRow;"
                ).output.strip()
                == node.query(
                    f"SELECT count() FROM {table.name}  FORMAT JSONEachRow;",
                    settings=[("force_select_final", 1)],
                ).output.strip()
            )


@TestScenario
def select(self, node=None):
    """Check select all data with `FINAL` clause equal to force_select_final select."""
    if node is None:
        node = self.context.node

    for table in self.context.tables:
        with Then("I check that select with force_select_final equal 'SELECT...FINAL'"):
            assert (
                node.query(
                    f"SELECT * FROM {table.name}"
                    f"{' FINAL' if table.final_modifier_available else ''} "
                    f"{' ORDER BY (key, someCol)' if not table.name.startswith('system') else ''} FORMAT JSONEachRow;"
                ).output.strip()
                == node.query(
                    f"SELECT * FROM "
                    f"{table.name}{' ORDER BY (key, someCol)' if not table.name.startswith('system') else ''}"
                    f" FORMAT JSONEachRow;",
                    settings=[("force_select_final", 1)],
                ).output.strip()
            )


@TestScenario
def select_join_equal_table(self, node=None):
    """Check select count() with `FINAL` clause equal to force_select_final for 'JOIN' clause."""
    if node is None:
        node = self.context.node
    with Given("I create duplicate table to core tables"):
        create_and_populate_core_tables(duplicate=True)
        self.context.tables.pop()

    join_types = ["INNER JOIN", "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "FULL OUTER JOIN", "CROSS JOIN",
                  "LEFT SEMI JOIN", "RIGHT SEMI JOIN", "LEFT ANTI JOIN", "RIGHT ANTI JOIN", "LEFT ANY JOIN",
                  "RIGHT ANY JOIN", "INNER ANY JOIN", "ASOF JOIN", "LEFT ASOF JOIN"]

    for join_type in join_types:
        for table in self.context.tables:
            if table.name.endswith("core"):
                for table2 in self.context.tables:
                    if table2.name.endswith("duplicate") and table2.name.startswith(
                            table.engine
                    ):
                        with Then(
                                "I check that select with force_select_final equal 'SELECT...FINAL'"
                        ):
                            assert (
                                    node.query(
                                        f"SELECT count() FROM {table.name}"
                                        f"{' FINAL' if table.final_modifier_available else ''}"
                                        f" {join_type} "
                                        f" {table2.name} on"
                                        f" {table.name}.key = {table2.name}.key"
                                    ).output.strip()
                                    == node.query(
                                f"SELECT count() FROM {table.name} {join_type}"
                                f" {table2.name} on {table.name}.key = {table2.name}.key",
                                settings=[("force_select_final", 1)],
                            ).output.strip()
                            )


@TestFeature
@Name("force modifier")
def feature(self):
    """Check force_final_modifier setting."""
    for scenario in loads(current_module(), Scenario):
        scenario()
