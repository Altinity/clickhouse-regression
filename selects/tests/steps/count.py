from selects.tests.steps.main_steps import *


@TestStep(When)
@Name("SELECT count()")
def count(self, table, node=None):
    """Execute select count() query without `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT count() ... ` from table {table.name}"):
        node.query(
            f"SELECT count() FROM {table.name} FORMAT JSONEachRow;", settings=[("final", 0)]
        ).output.strip()


@TestStep
@Name("SELECT count() with FINAL")
def count_with_final_clause(self, table, node=None):
    """Execute select count() query step with `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT count() ... FINAL` from table {table.name}"):

        node.query(
            f"SELECT count() FROM {table.name} {'FINAL' if table.final_modifier_available else ''} FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT count() with --final")
def count_with_force_final(self, table, node=None):
    """Execute select count() query step without `FINAL` clause but with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT count() ... ` with --final setting enabled from table {table.name}"
    ):
        node.query(
            f"SELECT count() FROM {table.name} FORMAT JSONEachRow;", settings=[("final", 1)]
        ).output.strip()


@TestStep
@Name("SELECT count() with FINAL and --final")
def count_with_final_clause_and_force_final(
    self, table, node=None
):
    """Select count() query step with `FINAL` clause and --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT count() ... FINAL` with --final setting enabled from table {table.name}"
    ):
        node.query(
            f"SELECT count() FROM {table.name} {'FINAL' if table.final_modifier_available else ''} FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep(Then)
@Name("count() compare results")
def count_result_check(self, table, node=None):
    """Compare results between count() query with `FINAL`  clause and count() query with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are the same"):
        assert (
            node.query(
                f"SELECT count() FROM {table.name} {'FINAL' if table.final_modifier_available else ''} FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            == node.query(
                f"SELECT count() FROM {table.name} FORMAT JSONEachRow;",
                settings=[("final", 1)],
            ).output.strip()
        )


@TestStep
@Name("count() negative compare results")
def count_negative_result_check(self, table, node=None):
    """Compare results between count() query with --final and count() query without `FINAL` and without --final.

    The expectation is that query results should be different when collapsed rows are present but FINAL modifier is not applied
    either explicitly using FINAL clause or using --final query setting."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are different"):
        if (
            table.final_modifier_available
            and node.query(f"SELECT count() FROM {table.name}").output.strip()
            != node.query(f"SELECT count() FROM {table.name} FINAL").output.strip()
        ):
            assert (
                node.query(
                    f"SELECT count() FROM {table.name} FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()
                != node.query(
                    f"SELECT count() FROM {table.name} FORMAT JSONEachRow;",
                    settings=[("final", 0)],
                ).output.strip()
            )
        else:
            xfail("not enough data for negative check")


@TestStep
def count_all_combinations(self, table):
    """Step to start all `SELECT count()` combinations with/without `FINAL` and --final enabled/disabled"""

    selects = []

    with Given("I select count() query without FINAL and without --final"):
        selects.append(count)

    with And("I select count() query with FINAL clause"):
        selects.append(count_with_final_clause)

    with And("I select count() query with --final"):
        selects.append(count_with_force_final)

    with And("I select count() query with FINAL clause and with --final"):
        selects.append(count_with_final_clause_and_force_final)

    with When("I execute selects concurrently"):
        run_queries_in_parallel(table=table, selects=selects, iterations=10)
