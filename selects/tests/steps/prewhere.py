from selects.tests.steps.main_steps import *


@TestStep
@Name("SELECT `PREWHERE`")
def prewhere(self, table, final_modifier_available, node=None):
    """Execute select 'PREWHERE' query without `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT PREWHERE` from table {table}"):
        node.query(
            f"SELECT * FROM {table} "
            f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT PREWHERE with FINAL")
def prewhere_with_final_clause(self, table, final_modifier_available, node=None):
    """Execute select 'PREWHERE' query step with `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT PREWHERE FINAL` from table {table}"):
        node.query(
            f"SELECT * FROM {table} {'FINAL' if final_modifier_available else ''}"
            f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT PREWHERE with --final")
def prewhere_with_force_final(self, table, final_modifier_available, node=None):
    """Execute select 'PREWHERE' query step without `FINAL` clause but with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT PREWHERE` with --final setting enabled from table {table}"
    ):
        node.query(
            f"SELECT * FROM {table} "
            f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep
@Name("SELECT PREWHERE with FINAL and --final")
def prewhere_with_final_clause_and_force_final(
    self, table, final_modifier_available, node=None
):
    """Select 'PREWHERE' query step with `FINAL` clause and --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT PREWHERE FINAL` with --final setting enabled from table {table}"
    ):
        node.query(
            f"SELECT * FROM {table} {'FINAL' if final_modifier_available else ''}"
            f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep(Then)
@Name("'PREWHERE' compare results")
def prewhere_result_check(self, table, final_modifier_available, node=None):
    """Compare results between 'PREWHERE' query with `FINAL`  clause and
    'PREWHERE' query with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are the same"):
        assert (
            node.query(
                f"SELECT * FROM {table} {'FINAL' if final_modifier_available else ''}"
                f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            == node.query(
                f"SELECT * FROM {table} "
                f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                settings=[("final", 1)],
            ).output.strip()
        )


@TestStep
@Name("'PREWHERE' negative compare results")
def prewhere_negative_result_check(self, table, final_modifier_available, node=None):
    """Compare results between prewhere query with --final and prewhere query without `FINAL` and without --final.

    The expectation is that query results should be different when collapsed rows are present but FINAL modifier is not applied
    either explicitly using FINAL clause or using --final query setting."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are different"):
        if (
            final_modifier_available
            and node.query(
                f"SELECT * FROM {table}"
                f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
            ).output.strip()
            != node.query(
                f"SELECT * FROM {table} FINAL"
                f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
            ).output.strip()
        ):
            assert (
                node.query(
                    f"SELECT * FROM {table} "
                    f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", 0)],
                ).output.strip()
                != node.query(
                    f"SELECT * FROM {table} "
                    f" PREWHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()
            )
        else:
            xfail("not enough data for negative check")


@TestStep
def prewhere_all_combinations(self, table):
    """Step to start all `SELECT PREWHERE` combinations with/without `FINAL` and --final enabled/disabled"""

    selects = []

    with Given("I select prewhere query without FINAL and without --final"):
        selects.append(prewhere)

    with And("I select prewhere query with FINAL clause"):
        selects.append(prewhere_with_final_clause)

    with And("I select prewhere query with --final"):
        selects.append(prewhere_with_force_final)

    with And("I select prewhere query with FINAL clause and with --final"):
        selects.append(prewhere_with_final_clause_and_force_final)

    with When("I execute selects concurrently"):
        run_queries_in_parallel(table=table, selects=selects, iterations=10)
