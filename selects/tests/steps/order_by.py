from selects.tests.steps.main_steps import *


@TestStep(Then)
@Name("'ORDER BY' compare results")
def order_by_with_alias(self, table, node=None):
    """Compare results between 'ORDER BY' query with alias with `FINAL`  clause and
    'ORDER BY' query with a;ias with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with Then("I check that compare results are the same"):
        assert (
            node.query(
                f"SELECT id, count(x) as cx FROM {table.name} {'FINAL' if table.final_modifier_available else ''}"
                f" GROUP BY id ORDER BY (id, cx) FORMAT JSONEachRow;",
                settings=[("final", 0)],
            ).output.strip()
            == node.query(
                f"SELECT id, count(x) as cx FROM {table.name}"
                f" GROUP BY id ORDER BY (id, cx) FORMAT JSONEachRow;",
                settings=[("final", 1)],
            ).output.strip()
        )
