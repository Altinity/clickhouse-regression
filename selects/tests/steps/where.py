from selects.tests.steps.main_steps import *


@TestStep
@Name("SELECT `WHERE`")
def where(self, table, node=None):
    """Execute select 'WHERE' query without `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT WHERE` from table {table.name}"):
        node.query(
            f"SELECT * FROM {table.name} "
            f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT WHERE with FINAL")
def where_with_final_clause(self, table, node=None):
    """Execute select 'WHERE' query step with `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT WHERE FINAL` from table {table.name}"):
        node.query(
            f"SELECT * FROM {table.name} {'FINAL' if table.final_modifier_available else ''}"
            f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT WHERE with --final")
def where_with_force_final(self, table, node=None):
    """Execute select 'WHERE' query step without `FINAL` clause but with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT WHERE` with --final setting enabled from table {table.name}"
    ):
        node.query(
            f"SELECT * FROM {table.name} "
            f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep
@Name("SELECT WHERE with FINAL and --final")
def where_with_final_clause_and_force_final(self, table, node=None):
    """Select 'WHERE' query step with `FINAL` clause and --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT WHERE FINAL` with --final setting enabled from table {table.name}"
    ):
        node.query(
            f"SELECT * FROM {table.name} {'FINAL' if table.final_modifier_available else ''}"
            f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep(Then)
@Name("'WHERE' compare results")
def where_result_check(self, table, node=None):
    """Compare results between 'WHERE' query with `FINAL`  clause and
    'WHERE' query with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are the same"):
        assert (
            node.query(
                f"SELECT * FROM {table.name} {'FINAL' if table.final_modifier_available else ''}"
                f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            == node.query(
                f"SELECT * FROM {table.name} "
                f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                settings=[("final", 1)],
            ).output.strip()
        )


@TestStep
@Name("'WHERE' negative compare results")
def where_negative_result_check(self, table, node=None):
    """Compare results between where query with --final and where query without `FINAL` and without --final.

    The expectation is that query results should be different when collapsed rows are present but FINAL modifier is not applied
    either explicitly using FINAL clause or using --final query setting."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are different"):
        if (
            table.final_modifier_available
            and node.query(
                f"SELECT * FROM {table.name}"
                f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
            ).output.strip()
            != node.query(
                f"SELECT * FROM {table.name} FINAL"
                f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
            ).output.strip()
        ):
            assert (
                node.query(
                    f"SELECT * FROM {table.name} "
                    f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", 0)],
                ).output.strip()
                != node.query(
                    f"SELECT * FROM {table.name} "
                    f" WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()
            )
        else:
            xfail("not enough data for negative check")


@TestStep
def where_all_combinations(self, table):
    """Step to start all `SELECT WHERE` combinations with/without `FINAL` and --final enabled/disabled"""

    selects = []

    with Given("I select where query without FINAL and without --final"):
        selects.append(where)

    with And("I select where query with FINAL clause"):
        selects.append(where_with_final_clause)

    with And("I select where query with --final"):
        selects.append(where_with_force_final)

    with And("I select where query with FINAL clause and with --final"):
        selects.append(where_with_final_clause_and_force_final)

    with When("I execute selects concurrently"):
        run_queries_in_parallel(table=table, selects=selects, iterations=10)
