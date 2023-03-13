from selects.tests.steps.main_steps import *


@TestStep
@Name("SELECT `LIMIT`")
def limit(self, table, node=None):
    """Execute select 'LIMIT' query without `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT LIMIT` from table {table.name}"):
        node.query(
            f"SELECT * FROM  {table.name} LIMIT 1 FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT LIMIT with FINAL")
def limit_with_final_clause(self, table, node=None):
    """Execute select 'LIMIT' query step with `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make `SELECT LIMIT FINAL` from table {table.name}"):
        node.query(
            f"SELECT * FROM  {table.name} {'FINAL' if table.final_modifier_available else ''}"
            f" LIMIT 1 FORMAT JSONEachRow;",
            settings=[("final", 0)],
        ).output.strip()


@TestStep
@Name("SELECT LIMIT with --final")
def limit_with_force_final(self, table, node=None):
    """Execute select 'LIMIT' query step without `FINAL` clause but with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT LIMIT` with --final setting enabled from table {table.name}"
    ):
        node.query(
            f"SELECT * FROM  {table.name} LIMIT 1 FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep
@Name("SELECT LIMIT with FINAL and --final")
def limit_with_final_clause_and_force_final(self, table, node=None):
    """Select 'LIMIT' query step with `FINAL` clause and --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make `SELECT LIMIT FINAL` with --final setting enabled from table {table.name}"
    ):
        node.query(
            f"SELECT * FROM  {table.name} {'FINAL' if table.final_modifier_available else ''}"
            f" LIMIT 1 FORMAT JSONEachRow;",
            settings=[("final", 1)],
        ).output.strip()


@TestStep(Then)
@Name("'LIMIT' compare results")
def limit_result_check(self, table, node=None):
    """Compare results between 'LIMIT' query with `FINAL`  clause and
    'LIMIT' query with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are the same"):
        assert (
            node.query(
                f"SELECT * FROM  {table.name} {'FINAL' if table.final_modifier_available else ''}"
                f" LIMIT 1 FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            == node.query(
                f"SELECT * FROM  {table.name} LIMIT 1 FORMAT JSONEachRow;",
                settings=[("final", 1)],
            ).output.strip()
        )


@TestStep(Then)
@Name("'LIMIT' with expression column as alias compare results")
def limit_result_check_with_alias(self, table, node=None):
    """Compare results between 'LIMIT' query with expression column as alias with `FINAL`  clause and
    'LIMIT' query with expression column as alias with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are the same"):
        assert (
            node.query(
                f"SELECT id*10 as new_id FROM  {table.name} {'FINAL' if table.final_modifier_available else ''}"
                f" LIMIT 1 FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            == node.query(
                f"SELECT id*10 as new_id FROM  {table.name} LIMIT 1 FORMAT JSONEachRow;",
                settings=[("final", 1)],
            ).output.strip()
        )


@TestStep
@Name("'LIMIT' negative compare results")
def limit_negative_result_check(self, table, node=None):
    """Compare results between limit query with --final and limit query without `FINAL` and without --final.

    The expectation is that query results should be different when collapsed rows are present but FINAL modifier is not applied
    either explicitly using FINAL clause or using --final query setting."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are different"):
        if (
            table.final_modifier_available
            and node.query(
                f"SELECT * FROM {table.name}" f" LIMIT 1 FORMAT JSONEachRow"
            ).output.strip()
            != node.query(
                f"SELECT * FROM {table.name}" f" FINAL LIMIT 1 FORMAT JSONEachRow"
            ).output.strip()
        ):
            assert (
                node.query(
                    f"SELECT * FROM  {table.name} LIMIT 1 FORMAT JSONEachRow;",
                    settings=[("final", 0)],
                ).output.strip()
                != node.query(
                    f"SELECT * FROM  {table.name} LIMIT 1 FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()
            )
        else:
            xfail("not enough data for negative check")


@TestStep
def limit_all_combinations(self, table):
    """Step to start all `SELECT LIMIT` combinations with/without `FINAL` and --final enabled/disabled."""

    selects = []

    with Given("I select limit query without FINAL and without --final"):
        selects.append(limit)

    with And("I select limit query with FINAL clause"):
        selects.append(limit_with_final_clause)

    with And("I select limit query with --final"):
        selects.append(limit_with_force_final)

    with And("I select limit query with FINAL clause and with --final"):
        selects.append(limit_with_final_clause_and_force_final)

    with When("I execute selects concurrently"):
        run_queries_in_parallel(table=table, selects=selects, iterations=10)
