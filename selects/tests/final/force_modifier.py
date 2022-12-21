from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *


@TestOutline
def simple_select(
    self,
    statement,
    order_by=False,
    distinct=False,
    group_by=False,
    limit=False,
    where=False,
    node=None,
):
    """Check all basic selects with `FINAL` clause equal to force_select_final select."""
    if node is None:
        node = self.context.node

    for table in self.context.tables:
        if not table.name.endswith("duplicate"):
            with Then(
                "I check that select with force_select_final equal 'SELECT...FINAL'"
            ):
                assert (
                    node.query(
                        f"SELECT{' DISTINCT' if distinct else ''} "
                        f"{statement if not table.name.startswith('system') else '*'} "
                        f"FROM {table.name}"
                        f"{' FINAL' if table.final_modifier_available else ''}"
                        f"{' WHERE x > 10' if not table.name.startswith('system') and where else ''}"
                        f"{' GROUP BY (id, x, someCol)' if not table.name.startswith('system') and group_by else ''}"
                        f"{' ORDER BY (id, x, someCol)' if not table.name.startswith('system') and order_by else ''}"
                        f"{' LIMIT 1' if limit else ''}"
                        f" FORMAT JSONEachRow;"
                    ).output.strip()
                    == node.query(
                        f"SELECT{' DISTINCT' if distinct else ''} "
                        f"{statement if not table.name.startswith('system') else '*'} "
                        f"FROM {table.name}"
                        f"{' WHERE x > 10' if not table.name.startswith('system') and where else ''}"
                        f"{' GROUP BY (id, x, someCol)' if not table.name.startswith('system') and group_by else ''}"
                        f"{' ORDER BY (id, x, someCol)' if not table.name.startswith('system') and order_by else ''}"
                        f"{' LIMIT 1' if limit else ''}"
                        f"  FORMAT JSONEachRow;",
                        settings=[("force_select_final", 1)],
                    ).output.strip()
                )


@TestScenario
def select_count(self):
    """Check select count() with `FINAL` clause equal to force_select_final select."""
    simple_select(statement="count()")


@TestScenario
def select_limit(self):
    """Check  `FINAL` clause equal to force_select_final select all data with `LIMIT`."""
    simple_select(statement="*", limit=True)


@TestScenario
def select_group_by(self):
    """Check  `FINAL` clause equal to force_select_final select all data with `GROUP BY`."""
    simple_select(statement="id, x, someCol", order_by=True, group_by=True)


@TestScenario
def select_distinct(self):
    """Check  `FINAL` clause equal to force_select_final select all data with `DISTINCT`."""
    simple_select(statement="*", order_by=True, distinct=True)


@TestScenario
def select_where(self):
    """Check  `FINAL` clause equal to force_select_final select all data with `WHERE`."""
    simple_select(statement="*", order_by=True, where=True)


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
def select_join_clause_select(self, node=None):
    """Check select count() that is using 'JOIN' clause `SELECT ... FINAL` with `FINAL`
    equal to  the same select without force_select_final `FINAL`."""
    if node is None:
        node = self.context.node

    join_types = [
        "INNER JOIN",
        "LEFT OUTER JOIN",
        "RIGHT OUTER JOIN",
        "FULL OUTER JOIN",
        "LEFT SEMI JOIN",
        "RIGHT SEMI JOIN",
        "LEFT ANTI JOIN",
        "RIGHT ANTI JOIN",
        "LEFT ANY JOIN",
        "RIGHT ANY JOIN",
        "INNER ANY JOIN",
    ]

    for join_type in join_types:
        for table in self.context.tables:
            if table.name.endswith("core") and not table.name.startswith("Log") and not \
                    table.name.startswith("StripeLog") and not table.name.startswith("TinyLog"):
                for table2 in self.context.tables:
                    if table2.name.endswith("duplicate") and table2.name.startswith(
                        table.engine
                    ):
                        with Then(
                            "I check that select with force_select_final equal 'SELECT...FINAL'"
                        ):
                            assert (
                                node.query(
                                    f"SELECT * FROM {table.name} a"
                                    f"{' FINAL' if table.final_modifier_available else ''}"
                                    f" {join_type} "
                                    f"(SELECT * FROM {table2.name}"
                                    f"{' FINAL' if table2.final_modifier_available else ''}) b on"
                                    f" a.id = b.id"
                                    f" ORDER BY (id, b.id, x, someCol, b.x, b.someCol)",
                                    settings=[("joined_subquery_requires_alias", 0)]
                                ).output.strip()
                                == node.query(
                                    f"SELECT * FROM {table.name} {join_type}"
                                    f" {table2.name} on {table.name}.id = {table2.name}.id"
                                    f" ORDER BY (id, {table2.name}.id, x, someCol,  {table2.name}.x, {table2.name}.someCol)",
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
                        for union in ["UNION ALL", "UNION DISTINCT"]:
                            assert (
                                    node.query(
                                        f"SELECT id, count(*) FROM {table.name}"
                                        f"{' FINAL' if table.final_modifier_available else ''} "
                                        f" GROUP BY id"
                                        f" {union}"
                                        f" SELECT id, count(*) FROM {table2.name}"
                                        f"{' FINAL' if table2.final_modifier_available else ''} "
                                        f" GROUP BY id"
                                    ).output.strip()
                                    == node.query(
                                f"SELECT id, count(*) FROM {table.name} GROUP BY id"
                                f" {union}"
                                f" SELECT id, count(*) FROM {table2.name} GROUP BY id",
                                settings=[("force_select_final", 1)],
                            ).output.strip()
                            )



@TestScenario
def select_with_clause(self, node=None):
    """Check `SELECT` that is using 'WITH' clause with `FINAL`
    equal to the same select without force_select_final `FINAL`."""
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
                node.query(
                    some_query.format(
                        table_name=table.name,
                        final=f"{'FINAL' if table.final_modifier_available else ''}",
                    ),
                    exitcode=0,
                ).output.strip()
                == node.query(
                    some_query.format(table_name=table.name, final=""),
                    exitcode=0,
                    settings=[("force_select_final", 1)],
                ).output.strip()
            )


@TestFeature
@Name("force modifier")
def feature(self):
    """Check force_final_modifier setting."""
    for scenario in loads(current_module(), Scenario):
        scenario()
