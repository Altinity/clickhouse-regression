from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *


@TestScenario
def select_count(self, node=None):
    """Check select count() with `FINAL` clause equal to force_select_final select."""
    if node is None:
        node = self.context.node

    for table in self.context.tables:
        if not table.name.endswith("duplicate"):
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
        if not table.name.endswith("duplicate"):
            with Then("I check that select with force_select_final equal 'SELECT...FINAL'"):
                assert (
                        node.query(
                            f"SELECT * FROM {table.name}"
                            f"{' FINAL' if table.final_modifier_available else ''} "
                            f"{' ORDER BY (id, x, someCol)' if not table.name.startswith('system') else ''} FORMAT JSONEachRow;"
                        ).output.strip()
                        == node.query(
                    f"SELECT * FROM "
                    f"{table.name}{' ORDER BY (id, x, someCol)' if not table.name.startswith('system') else ''}"
                    f" FORMAT JSONEachRow;",
                    settings=[("force_select_final", 1)],
                ).output.strip()
                )



@TestScenario
def select_join_clause(self, node=None):
    """Check select count() that is using 'JOIN' clause with `FINAL`
    equal to  the same select without force_select_final `FINAL`."""
    if node is None:
        node = self.context.node

    join_types = [
        "INNER JOIN",
        "LEFT OUTER JOIN",
        "RIGHT OUTER JOIN",
        "FULL OUTER JOIN",
        "CROSS JOIN",
        "LEFT SEMI JOIN",
        "RIGHT SEMI JOIN",
        "LEFT ANTI JOIN",
        "RIGHT ANTI JOIN",
        "LEFT ANY JOIN",
        "RIGHT ANY JOIN",
        "INNER ANY JOIN",
        "ASOF JOIN",
        "LEFT ASOF JOIN",
    ]

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


@TestScenario
def select_union_clause(self, node=None):
    """Check `SELECT` that is using 'UNION' clause with `FINAL`
    equal to the same select without force_select_final `FINAL`."""
    if node is None:
        node = self.context.node

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
                                    f"SELECT id, count(*) FROM {table.name}"
                                    f"{' FINAL' if table.final_modifier_available else ''} "
                                    f" GROUP BY id"
                                    f" UNION ALL"
                                    f" SELECT id, count(*) FROM {table2.name}"
                                    f"{' FINAL' if table2.final_modifier_available else ''} "
                                    f" GROUP BY id"
                                ).output.strip()
                                == node.query(
                            f"SELECT id, count(*) FROM {table.name} GROUP BY id"
                            f" UNION ALL"
                            f" SELECT id, count(*) FROM {table2.name} GROUP BY id",
                            settings=[("force_select_final", 1)],
                        ).output.strip()
                        )


@TestScenario
def select_with_clause(self, node=None):
    """Check `SELECT` that is using 'WITH' clause with `FINAL`
    equal to the same select without force_select_final `FINAL`."""
    # xfail("not implemented")
    if node is None:
        node = self.context.node

    some_query = """
    WITH
        (
            SELECT count(id)
            FROM {table_name} {final}
        ) AS total_ids
    SELECT
        (x / total_ids) AS something,
        someCol
    FROM {table_name} {final}
    GROUP BY (x,someCol)
    ORDER BY something,someCol DESC;
    """
    for table in self.context.tables:
        if table.name.endswith("core"):
            assert (
                    node.query(some_query.format(table_name=table.name,
                                                 final=f"{'FINAL' if table.final_modifier_available else ''}"),
                               exitcode=0).output.strip() ==
                    node.query(some_query.format(table_name=table.name, final=""), exitcode=0,
                               settings=[("force_select_final", 1)]).output.strip())


@TestFeature
@Name("force modifier")
def feature(self):
    """Check force_final_modifier setting."""
    for scenario in loads(current_module(), Scenario):
        scenario()
