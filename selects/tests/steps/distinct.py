from selects.tests.steps.main_steps import *


@TestStep(When)
@Name("SELECT 'DISTINCT'")
def distinct(self, table, final_modifier_available, node=None):
    """Execute select 'DISTINCT' query without `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT DISTINCT ... ` from table {name}"):
        node.query(
            f"SELECT DISTINCT * FROM {table} ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT DISTINCT with FINAL")
def distinct_with_final_clause(self, table, final_modifier_available, node=None):
    """Execute select 'DISTINCT' query step with `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT DISTINCT ... FINAL` from table {name}"):
        node.query(
            f"SELECT DISTINCT * FROM {table} {'FINAL' if final_modifier_available else ''} "
            f"ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT DISTINCT with --final")
def distinct_with_force_final(self, table, final_modifier_available, node=None):
    """Execute select 'DISTINCT' query step without `FINAL` clause but with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT DISTINCT ... ` with --final setting enabled from table {name}"
    ):
        node.query(
            f"SELECT DISTINCT * FROM {table} ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep
@Name("SELECT DISTINCT with FINAL and --final")
def distinct_with_final_clause_and_force_final(
    self, table, final_modifier_available, node=None
):
    """Select 'DISTINCT' query step with `FINAL` clause and --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT DISTINCT ... FINAL` with --final setting enabled from table {name}"
    ):
        node.query(
            f"SELECT DISTINCT * FROM {table} {'FINAL' if final_modifier_available else ''} "
            f"ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep(Then)
@Name("'DISTINCT' compare results")
def distinct_result_check(self, table, final_modifier_available, node=None):
    """Compare results between 'DISTINCT' query with `FINAL`  clause and
    'DISTINCT' query with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are the same"):
        assert (
            node.query(
                f"SELECT DISTINCT * FROM {table} {'FINAL' if final_modifier_available else ''} "
                f"ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            == node.query(
                f"SELECT DISTINCT * FROM {table} ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                settings=[("final", 1)],
            ).output.strip()
        )


@TestStep
@Name("'DISTINCT' negative compare results")
def distinct_negative_result_check(self, table, final_modifier_available, node=None):
    """Compare results between distinct query with --final and distinct query without `FINAL` and without --final.

    The expectation is that query results should be different when collapsed rows are present but FINAL modifier is not applied
    either explicitly using FINAL clause or using --final query setting."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are different"):
        if (
            final_modifier_available
            and node.query(
                f"SELECT DISTINCT * FROM {table}"
                f" ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
            ).output.strip()
            != node.query(
                f"SELECT DISTINCT * FROM {table} FINAL"
                f" ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
            ).output.strip()
        ):
            assert (
                node.query(
                    f"SELECT DISTINCT * FROM {table} ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", 0)],
                ).output.strip()
                != node.query(
                    f"SELECT DISTINCT * FROM {table} ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()
            )
        else:
            xfail("not enough data for negative check")


@TestStep
def distinct_all_combinations(self, table):
    """Step to start all `SELECT DISTINCT` combinations with/without `FINAL` and --final enabled/disabled"""

    selects = []

    with Given("I select distinct query without FINAL and without --final"):
        selects.append(distinct)

    with And("I select distinct query with FINAL clause"):
        selects.append(distinct_with_final_clause)

    with And("I select distinct query with --final"):
        selects.append(distinct_with_force_final)

    with And("I select distinct query with FINAL clause and with --final"):
        selects.append(distinct_with_final_clause_and_force_final)

    with When("I execute selects concurrently"):
        run_queries_in_parallel(table=table, selects=selects, iterations=10)
