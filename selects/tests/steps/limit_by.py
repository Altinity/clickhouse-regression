from selects.tests.steps.main_steps import *


@TestStep
@Name("SELECT `LIMIT BY`")
def limit_by(self, table, node=None):
    """Execute select 'LIMIT BY' query without `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT LIMIT BY` from table {table.name}"):
        node.query(
            f"SELECT * FROM  {table.name} "
            f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT LIMIT BY with FINAL")
def limit_by_with_final_clause(self, table, node=None):
    """Execute select 'LIMIT BY' query step with `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT LIMIT BY FINAL` from table {table.name}"):
        node.query(
            f"SELECT * FROM  {table.name} {'FINAL' if table.final_modifier_available else ''}"
            f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT LIMIT BY with --final")
def limit_by_with_force_final(self, table, node=None):
    """Execute select 'LIMIT BY' query step without `FINAL` clause but with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT LIMIT BY` with --final setting enabled from table {table.name}"
    ):
        node.query(
            f"SELECT * FROM  {table.name} "
            f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep
@Name("SELECT LIMIT BY with FINAL and --final")
def limit_by_with_final_clause_and_force_final(self, table, node=None):
    """Select 'LIMIT BY' query step with `FINAL` clause and --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT LIMIT BY FINAL` with --final setting enabled from table {table.name}"
    ):
        node.query(
            f"SELECT * FROM  {table.name} {'FINAL' if table.final_modifier_available else ''}"
            f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep(Then)
@Name("'LIMIT BY' compare results")
def limit_by_result_check(self, table, node=None):
    """Compare results between 'LIMIT BY' query with `FINAL`  clause and
    'LIMIT BY' query with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are the same"):
        assert (
            node.query(
                f"SELECT * FROM  {table.name} {'FINAL' if table.final_modifier_available else ''}"
                f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            == node.query(
                f"SELECT * FROM  {table.name} "
                f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
                settings=[("final", 1)],
            ).output.strip()
        )


@TestStep
@Name("'LIMIT BY' negative compare results")
def limit_by_negative_result_check(self, table, node=None):
    """Compare results between limit_by query with --final and limit_by query without `FINAL` and without --final.

    The expectation is that query results should be different when collapsed rows are present but FINAL modifier is not applied
    either explicitly using FINAL clause or using --final query setting."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are different"):
        if (
            table.final_modifier_available
            and node.query(
                f"SELECT * FROM {table.name}"
                f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;"
            ).output.strip()
            != node.query(
                f"SELECT * FROM {table.name} FINAL"
                f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;"
            ).output.strip()
        ):
            assert (
                node.query(
                    f"SELECT * FROM  {table.name} "
                    f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
                    settings=[("final", 0)],
                ).output.strip()
                != node.query(
                    f"SELECT * FROM  {table.name} "
                    f" ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()
            )
        else:
            xfail("not enough data for negative check")


@TestStep
def limit_by_all_combinations(self, table):
    """Step to start all `SELECT LIMIT BY` combinations with/without `FINAL` and --final enabled/disabled"""

    selects = []

    with Given("I select limit_by query without FINAL and without --final"):
        selects.append(limit_by)

    with And("I select limit_by query with FINAL clause"):
        selects.append(limit_by_with_final_clause)

    with And("I select limit_by query with --final"):
        selects.append(limit_by_with_force_final)

    with And("I select limit_by query with FINAL clause and with --final"):
        selects.append(limit_by_with_final_clause_and_force_final)

    with When("I execute selects concurrently"):
        run_queries_in_parallel(table=table, selects=selects, iterations=10)
