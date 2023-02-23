from selects.tests.steps import *


@TestStep
@Name("SELECT column as new_column")
def as_statement(self, table, final_modifier_available, node=None):
    """Execute select `as` query without `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT column as new_column ... ` from table {name}"):
        node.query(
            f"SELECT id as new_id FROM {table} ORDER BY (id) FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT column as new_column with FINAL")
def as_with_final_clause(self, table, final_modifier_available, node=None):
    """Execute select `as` query step with `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT column as new_column ... FINAL` from table {table}"):
        node.query(
            f"SELECT id as new_id FROM {table} {'FINAL' if final_modifier_available else ''} ORDER BY (id) FORMAT"
            f" JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT column as new_column with --final")
def as_with_force_final(self, table, final_modifier_available, node=None):
    """Execute select `as` query step without `FINAL` clause but with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT column as new_column ... ` with --final setting enabled from table {table}"
    ):
        node.query(
            f"SELECT id as new_id FROM {table} ORDER BY (id) FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep
@Name("SELECT `as` FINAL force final")
def as_with_final_clause_and_force_final(
    self, table, final_modifier_available, node=None
):
    """Execute select as query step with `FINAL` clause and with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT column as new_column ... FINAL` with --final setting enabled from table {table}"
    ):
        node.query(
            f"SELECT id as new_id FROM {table} {'FINAL' if final_modifier_available else ''} ORDER BY (id)"
            f" FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep
@Name("`as` result check")
def as_result_check(self, table, final_modifier_available, node=None):
    """Compare results between `select column as new_column` query with `FINAL` clause and
    `select column as new_column` query with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are the same"):
        assert (
            node.query(
                f"SELECT id as new_id FROM {table} {'FINAL' if final_modifier_available else ''} ORDER BY (id) FORMAT"
                f" JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            == node.query(
                f"SELECT id as new_id FROM {table} ORDER BY (id) FORMAT JSONEachRow;",
                settings=[("final", 1)],
            ).output.strip()
        )


@TestStep
@Name("`as` negative result check")
def as_negative_result_check(self, table, final_modifier_available, node=None):
    """Compare results between `select column as new_column` query with --final and
     `select column as new_column` query without `FINAL` and without --final.

    The expectation is that query results should be different when collapsed rows are present but FINAL modifier is not applied
    either explicitly using FINAL clause or using --final query setting."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are different"):
        if (
            final_modifier_available
            and node.query(
                f"SELECT id as new_id FROM {table}"
                f" ORDER BY (id) FORMAT JSONEachRow;"
            ).output.strip()
            != node.query(
                f"SELECT id as new_id FROM {table} FINAL"
                f" ORDER BY (id) FORMAT JSONEachRow;"
            ).output.strip()
        ):
            assert (
                node.query(
                    f"SELECT id as new_id FROM {table} ORDER BY (id) FORMAT JSONEachRow;",
                    settings=[("final", 0)],
                ).output.strip()
                != node.query(
                    f"SELECT id as new_id FROM {table} ORDER BY (id) FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()
            )
        else:
            xfail("not enough data for negative check")


@TestStep
def as_all_combinations(self, table):
    """Step to start all `SELECT count()` combinations with/without `FINAL` and --final enabled/disabled"""

    selects = []

    with Given("I select count() query without FINAL and without --final"):
        selects.append(as_statement)

    with And("I select count() query with FINAL clause"):
        selects.append(as_with_final_clause)

    with And("I select count() query with --final"):
        selects.append(as_with_force_final)

    with And("I select count() query with FINAL clause and with --final"):
        selects.append(as_with_final_clause_and_force_final)

    with When("I execute selects concurrently"):
        run_queries_in_parallel(table=table, selects=selects, iterations=10)
