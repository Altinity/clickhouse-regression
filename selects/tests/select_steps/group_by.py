from selects.tests.steps import *


@TestStep
@Name("SELECT `GROUP BY`")
def group_by(self, table, final_modifier_available, node=None):
    """Execute select 'GROUP BY' query without `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT GROUP BY ... ` from table {table}"):
        node.query(
            f"SELECT id, count(x) as cx FROM {table}"
            f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT GROUP BY with FINAL")
def group_by_with_final_clause(self, table, final_modifier_available, node=None):
    """Execute select 'GROUP BY' query step with `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT GROUP BY FINAL` from table {table}"):
        node.query(
            f"SELECT id, count(x) as cx FROM {table} {'FINAL' if final_modifier_available else ''}"
            f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT GROUP BY with --final")
def group_by_with_force_final(self, table, final_modifier_available, node=None):
    """Execute select 'GROUP BY' query step without `FINAL` clause but with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT GROUP BY ` with --final setting enabled from table {table}"
    ):
        node.query(
            f"SELECT id, count(x) as cx FROM {table}"
            f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep
@Name("SELECT GROUP BY with FINAL and --final")
def group_by_with_final_clause_and_force_final(
    self, table, final_modifier_available, node=None
):
    """Select 'GROUP BY' query step with `FINAL` clause and --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT GROUP BY ... FINAL` with --final setting enabled from table {table}"
    ):
        node.query(
            f"SELECT id, count(x) as cx FROM {table} {'FINAL' if final_modifier_available else ''}"
            f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep(Then)
@Name("'GROUP BY' compare results")
def group_by_result_check(self, table, final_modifier_available, node=None):
    """Compare results between 'GROUP BY' query with `FINAL`  clause and
    'GROUP BY' query with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are the same"):
        assert (
            node.query(
                f"SELECT id, count(x) as cx FROM {table} {'FINAL' if final_modifier_available else ''}"
                f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            == node.query(
                f"SELECT id, count(x) as cx FROM {table}"
                f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
                settings=[("final", 1)],
            ).output.strip()
        )


@TestStep
@Name("'GROUP BY' negative compare results")
def group_by_negative_result_check(self, table, final_modifier_available, node=None):
    """Compare results between group_by query with --final and group_by query without `FINAL` and without --final.

    The expectation is that query results should be different when collapsed rows are present but FINAL modifier is not applied
    either explicitly using FINAL clause or using --final query setting."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are different"):
        if (
            final_modifier_available
            and node.query(
                f"SELECT id, count(x) as cx FROM {table}"
                f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            != node.query(
                f"SELECT id, count(x) as cx FROM {table} FINAL"
                f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
        ):
            assert (
                node.query(
                    f"SELECT id, count(x) as cx FROM {table}"
                    f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
                    settings=[("final", 0)],
                ).output.strip()
                != node.query(
                    f"SELECT id, count(x) as cx FROM {table}"
                    f" GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()
            )
        else:
            xfail("not enough data for negative check")


@TestStep
def group_by_all_combinations(self, table):
    """Step to start all `SELECT GROUP BY` combinations with/without `FINAL` and --final enabled/disabled"""

    selects = []

    with Given("I select group by query without FINAL and without --final"):
        selects.append(group_by)

    with And("I select group by query with FINAL clause"):
        selects.append(group_by_with_final_clause)

    with And("I select group by query with --final"):
        selects.append(group_by_with_force_final)

    with And("I select group by query with FINAL clause and with --final"):
        selects.append(group_by_with_final_clause_and_force_final)

    with When("I execute selects concurrently"):
        run_queries_in_parallel(table=table, selects=selects, iterations=10)
