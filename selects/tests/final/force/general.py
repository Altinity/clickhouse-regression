import os
from testflows.core import *
from selects.requirements import *
from selects.tests.steps.main_steps import *
from helpers.common import check_clickhouse_version
import tests.steps as select


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Select("1.0"))
def simple_select_count(self):
    """Check `SELECT count()` clause."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and some not supported views",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                if not table.name.endswith("nview")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between count() query with `FINAL`  clause "
                "and count() query with --final setting enabled."
            ):
                select.count_result_check(table=table)

            with And(
                "Compare results between count() query with --final "
                "and count() query without `FINAL` and without --final."
            ):
                select.count_negative_result_check(table=table)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Distinct("1.0")
)
def simple_select_distinct(self):
    """Check SELECT query with `DISTINCT` clause."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                if not table.name.endswith("nview")
                if not table.name.startswith("system")
                if not table.name.endswith("_wview_final")
                if not table.name.startswith("expr_subquery")
                if not table.name.startswith("alias")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between distinct query with `FINAL`  clause "
                "and distinct query with --final setting enabled."
            ):
                select.distinct_result_check(table=table)

            with And(
                "Compare results between distinct query with --final "
                "and distinct query without `FINAL` and without --final."
            ):
                select.distinct_negative_result_check(table=table)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Limit("1.0"))
def simple_select_limit(self):
    """Check SELECT query with `LIMIT` clause."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                if not table.name.endswith("nview")
                if not table.name.endswith("nview_final")
                if not table.name.startswith("system")
                if not table.name.endswith("_wview_final")
                if not table.name.startswith("expr_subquery")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between `SELECT LIMIT` query with `FINAL`  clause "
                "and `SELECT LIMIT` query with --final setting enabled."
            ):
                select.limit_result_check(table=table)

            with And(
                "Compare results between `SELECT LIMIT` query with --final "
                "and `SELECT LIMIT` query without `FINAL` and without --final."
            ):
                select.limit_negative_result_check(table=table)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_LimitBy("1.0"))
def simple_select_limit_by(self):
    """Check SELECT query with `LIMIT BY` clause."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                if not table.name.endswith("nview")
                if not table.name.startswith("system")
                if not table.name.endswith("_wview_final")
                if not table.name.startswith("expr_subquery")
                if not table.name.startswith("alias")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between `SELECT LIMIT BY` query with `FINAL`  clause "
                "and `SELECT LIMIT BY` query with --final setting enabled."
            ):
                select.limit_by_result_check(table=table)

            with And(
                "Compare results between `SELECT LIMIT BY` query with --final "
                "and `SELECT LIMIT BY` query without `FINAL` and without --final."
            ):
                select.limit_by_negative_result_check(table=table)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Prewhere("1.0")
)
def simple_select_prewhere(self, node=None):
    """Check SELECT query with `PREWHERE` clause."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if table.name.endswith("core") and not table.engine.endswith("Log")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between `SELECT PREWHERE` query with `FINAL`  clause "
                "and `SELECT PREWHERE` query with --final setting enabled."
            ):
                select.prewhere_result_check(table=table)

            with And(
                "Compare results between `SELECT PREWHERE` query with --final "
                "and `SELECT PREWHERE` query without `FINAL` and without --final."
            ):
                select.prewhere_negative_result_check(table=table)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Where("1.0"))
def simple_select_where(self):
    """Check SELECT query with `WHERE` clause."""
    with Given("I chose tables for testing"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                if not table.name.endswith("nview")
                if not table.name.startswith("system")
                if not table.name.endswith("_wview_final")
                if not table.name.startswith("expr_subquery")
                if not table.name.startswith("alias")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with Example(f"{table.name}", flags=TE):
            with Then(
                "Compare results between `SELECT WHERE` query with `FINAL`  clause "
                "and `SELECT WHERE` query with --final setting enabled."
            ):
                select.where_result_check(table=table)

            with And(
                "Compare results between `SELECT WHERE` query with --final "
                "and `SELECT WHERE` query without `FINAL` and without --final."
            ):
                select.where_negative_result_check(table=table)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_ArrayJoin("1.0")
)
def select_array_join(self, node=None):
    """Check SELECT query with `ARRAY JOIN` clause."""
    if node is None:
        node = self.context.node

    name = f"arrays_test_{getuid()}"

    with Given("I create engines list for current test"):
        engines = define(
            "engines",
            [
                "ReplacingMergeTree",
                "AggregatingMergeTree",
                "SummingMergeTree",
                "MergeTree",
                "StripeLog",
                "TinyLog",
                "Log",
            ],
            encoder=lambda s: ", ".join(s),
        )

    with And(
        "I form `create` and `populate` queries for table with array data type and all engines from engine list"
    ):
        table = define(
            "array table query",
            """CREATE TABLE {name}
            (
                s String,
                arr Array(UInt8)
            ) ENGINE = {engine}
            {order}""",
        )

        insert = define(
            "array value insert query",
            f"INSERT INTO {name} VALUES ('Hello', [1,2]), ('World', [3,4,5]), ('Goodbye', []);",
        )

    for engine in engines:
        with When(f"{engine}"):
            try:
                with When(f"I create and populate table with array type"):
                    node.query(
                        f"{table.format(name=name, engine=engine, order='') if engine.endswith('Log') else table.format(name=name, engine=engine, order='ORDER BY s;')}"
                    )
                    node.query("SYSTEM STOP MERGES")
                    node.query(insert)
                    node.query(insert)

                with When("I execute query with force_select_final=1 setting"):
                    force_select_final = node.query(
                        f"SELECT count() FROM {name} ARRAY JOIN arr",
                        settings=[("final", 1)],
                    ).output.strip()

                with And(
                    "I execute the same query with FINAL modifier specified explicitly"
                ):
                    if engine.startswith("Merge") or engine.endswith("Log"):
                        explicit_final = node.query(
                            f"SELECT count() FROM {name} ARRAY JOIN arr"
                        ).output.strip()
                    else:
                        explicit_final = node.query(
                            f"SELECT count() FROM {name} FINAL ARRAY JOIN arr"
                        ).output.strip()

                with Then("I compare results are the same"):
                    assert explicit_final == force_select_final

            finally:
                node.query(f"DROP TABLE {name}")


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join("1.0"))
def select_join_clause(self, node=None):
    """Check SELECT query with `JOIN` clause."""
    if node is None:
        node = self.context.node

    table_pairs = []

    with Given("I have a list of core table"):
        core_tables = [
            table for table in self.context.tables if table.name.endswith("core")
        ]

    with And("I have a list of corresponding duplicate tables"):
        for table1 in core_tables:
            for table2 in self.context.tables:
                if table2.name.endswith("duplicate") and table2.engine == table1.engine:
                    table_pairs.append((table1, table2))

    with Given("I have a list of available join types for this test"):
        join_types_local = define(
            "Create a list of join types that are supported by test construction and exclude those that are not.",
            [
                join_type
                for join_type in join_types
                if not join_type.startswith("CROSS")
                and not join_type.startswith("ASOF")
                and not join_type.startswith("LEFT ASOF")
            ],
            encoder=lambda s: ", ".join(s),
        )

    for join_type in join_types_local:
        with Example(f"{join_type}", flags=TE):
            for table1, table2 in table_pairs:
                with When(
                    f"I have {table1.name} and corresponding {table2.name}", flags=TE
                ):
                    with Then(
                        "I check that select with force_select_final=1 setting"
                        f" equals 'SELECT...FINAL' for {table1.name} and {table2.name} "
                        f"with {join_type} clause"
                    ):
                        join_statement = (
                            f"SELECT count() FROM {table1.name}"
                            f"{' FINAL' if table1.final_modifier_available else ''}"
                            f" {join_type} "
                            f" {table2.name} {' FINAL' if table2.final_modifier_available else ''} on"
                            f" {table1.name}.id = {table2.name}.id"
                        )

                        assert_joins(
                            join_statement=join_statement,
                            table=table1,
                            table2=table2,
                            join_type=join_type,
                            node=node,
                        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join_Select("1.0")
)
def select_join_clause_select_all_types(self, node=None):
    """Check SELECT query with different types of `JOIN` clause for equal table engines."""
    if node is None:
        node = self.context.node

    table_pairs, join_types_local = [], []

    with Given("I have a list of available join types for this test"):
        join_types_local = define(
            "Join types list",
            [
                join_type
                for join_type in join_types
                if not join_type.startswith("CROSS")
                and not join_type.startswith("ASOF")
                and not join_type.startswith("LEFT ASOF")
            ],
            encoder=lambda s: ", ".join(s),
        )

    with And("I have a list of core table"):
        core_tables = [
            table for table in self.context.tables if table.name.endswith("core")
        ]

    with And("I have a list of corresponding duplicate tables"):
        for table1 in core_tables:
            for table2 in self.context.tables:
                if table2.name.endswith("duplicate") and table2.engine == table1.engine:
                    table_pairs.append((table1, table2))

    for join_type in join_types_local:
        for table1, table2 in table_pairs:
            with Example(f"{table1.engine} {join_type} {table2.engine}", flags=TE):
                with When(f"I have {table1.name} and corresponding {table2.name}"):
                    with Then(
                        "I check that select with force_select_final=1 setting"
                        f" equal 'SELECT...FINAL' for {table1.engine}"
                        f"with {join_type} clause"
                    ):
                        join_statement = (
                            f"SELECT count() FROM {table1.name} a"
                            f"{' FINAL' if table1.final_modifier_available else ''}"
                            f" {join_type} "
                            f"(SELECT * FROM {table2.name}"
                            f"{' FINAL' if table2.final_modifier_available else ''}) b on"
                            f" a.id = b.id"
                        )
                        assert_joins(
                            join_statement=join_statement,
                            table=table1,
                            table2=table2,
                            join_type=join_type,
                            node=node,
                        )


@TestScenario
def select_join_clause_select_all_engine_combinations(self, node=None):
    """Check SELECT query with `INNER JOIN` clause for all table engines."""
    if node is None:
        node = self.context.node

    table_pairs = []

    with Given("I have a list of core table"):
        core_tables = [
            table for table in self.context.tables if table.name.endswith("core")
        ]

    with And("I have a list of all core tables combinations tables"):
        for table1 in core_tables:
            for table2 in self.context.tables:
                if table2.name.endswith("core") and table2.engine != table1.engine:
                    table_pairs.append((table1, table2))

    for table1, table2 in table_pairs:
        with Example(f"{table1.engine} INNER JOIN {table2.engine}", flags=TE):
            with When(
                f"I check `INNER JOIN` for {table1.name} and corresponding {table2.name}"
            ):
                with Then(
                    "I check that select with force_select_final=1 setting"
                    f" equal 'SELECT...FINAL' for {table1.name} and {table2.name} "
                    f"with 'INNER JOIN' clause"
                ):
                    join_statement = (
                        f"SELECT count() FROM {table1.name} a"
                        f"{' FINAL' if table1.final_modifier_available else ''}"
                        f" INNER JOIN "
                        f"(SELECT * FROM {table2.name}"
                        f"{' FINAL' if table2.final_modifier_available else ''}) b on"
                        f" a.id = b.id"
                    )
                    assert_joins(
                        join_statement=join_statement,
                        table=table1,
                        table2=table2,
                        join_type="INNER JOIN",
                        node=node,
                    )


@TestOutline
def select_family_union_clause(self, node=None, clause=None, negative=False):
    """Check `SELECT` that is using union family clause."""
    if node is None:
        node = self.context.node

    table_pairs = []

    with Given("I have a list of core table"):
        core_tables = [
            table for table in self.context.tables if table.name.endswith("core")
        ]

    with And("I have a list of corresponding duplicate tables"):
        for table1 in core_tables:
            for table2 in self.context.tables:
                if table2.name.endswith("duplicate") and table2.engine == table1.engine:
                    table_pairs.append((table1, table2))

    for table1, table2 in table_pairs:
        with When(f"I have {table1.name} and corresponding {table2.name}"):
            with Then(
                f"I check that select with {clause} with force_select_final"
                f" equal 'SELECT...FINAL'"
            ):
                with When("I execute query with FINAL modifier specified explicitly"):
                    explicit_final = node.query(
                        f"SELECT id, count(*) FROM {table1.name}"
                        f"{' FINAL' if table1.final_modifier_available else ''} "
                        f" GROUP BY id"
                        f" {clause}"
                        f" SELECT id, count(*) FROM {table2.name}"
                        f"{' FINAL' if table2.final_modifier_available else ''} "
                        f" GROUP BY id"
                    ).output.strip()

                with And("I execute the same query without FINAL modifier"):
                    without_final = node.query(
                        f"SELECT id, count(*) FROM {table1.name}"
                        f" GROUP BY id"
                        f" {clause}"
                        f" SELECT id, count(*) FROM {table2.name}"
                        f" GROUP BY id"
                    ).output.strip()

                with And(
                    "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
                ):
                    force_select_final = node.query(
                        f"SELECT id, count(*) FROM {table1.name} GROUP BY id"
                        f" {clause}"
                        f" SELECT id, count(*) FROM {table2.name} GROUP BY id",
                        settings=[("final", 1)],
                    ).output.strip()

                if negative:
                    with Then("I check that compare results are different"):
                        if (
                            table1.final_modifier_available
                            and table2.final_modifier_available
                            and without_final != explicit_final
                        ):
                            assert without_final != force_select_final
                else:
                    with Then("I check that compare results are the same"):
                        assert explicit_final == force_select_final


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Union("1.0"))
def select_union_clause(self):
    """Check SELECT query with `UNION` clause."""
    with Check("UNION ALL"):
        with Then("I check positive case"):
            select_family_union_clause(clause="UNION ALL")

        with And("I check negative case"):
            select_family_union_clause(clause="UNION ALL", negative=True)

    with Check("UNION DISTINCT"):
        with Then("I check positive case"):
            select_family_union_clause(clause="UNION DISTINCT")

        with And("I check negative case"):
            select_family_union_clause(clause="UNION DISTINCT", negative=True)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Intersect("1.0")
)
def select_intersect_clause(self):
    """Check SELECT query with `INTERSECT` clause."""
    with Then("I check positive case"):
        select_family_union_clause(clause="INTERSECT")

    with And("I check negative case"):
        select_family_union_clause(clause="INTERSECT", negative=True)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Except("1.0"))
def select_except_clause(self):
    """Check SELECT query with `EXCEPT` clause."""
    with Then("I check positive case"):
        select_family_union_clause(clause="EXCEPT")

    with And("I check negative case"):
        select_family_union_clause(clause="EXCEPT", negative=True)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join_Nested("1.0")
)
def select_nested_join_clause_select(self, node=None):
    """Check SELECT query with nested `JOIN` clause."""
    if node is None:
        node = self.context.node

    table_pairs, join_types_local = [], []

    with Given("I have a list of available join types for this test"):
        join_types_local = define(
            "Join types list",
            [
                join_type
                for join_type in join_types
                if not join_type.startswith("CROSS")
                and not join_type.startswith("ASOF")
                and not join_type.startswith("LEFT ASOF")
            ],
            encoder=lambda s: ", ".join(s),
        )

    with Given("I have a list of core table"):
        core_tables = define(
            "List of tables for the test",
            [table for table in self.context.tables if table.name.endswith("core")],
            encoder=lambda tables: ", ".join(table.name for table in tables),
        )

    with And("I have a list of corresponding duplicate tables"):
        for table1 in core_tables:
            for table2 in self.context.tables:
                if table2.name.endswith("duplicate") and table2.engine == table1.engine:
                    table_pairs.append((table1, table2))

    for join_type in join_types_local:
        for table1, table2 in table_pairs:
            with Example(f"{table1.engine} {join_type} {table2.engine}", flags=TE):
                with When(f"I have {table1.name} and corresponding {table2.name}"):
                    with When(
                        "I execute query with FINAL modifier specified explicitly"
                    ):
                        join_statement = define(
                            "Nested join query",
                            f"SELECT count() FROM {table1.name} c "
                            f"{' FINAL' if table1.final_modifier_available else ''} {join_type}"
                            f"(SELECT * FROM {table1.name} a"
                            f"{' FINAL' if table1.final_modifier_available else ''}"
                            f" {join_type} "
                            f"(SELECT * FROM {table2.name}"
                            f"{' FINAL' if table2.final_modifier_available else ''}) b on"
                            f" a.id = b.id) d on c.id=d.id",
                        )

                        explicit_final = node.query(
                            join_statement,
                            settings=[("joined_subquery_requires_alias", 0)],
                        ).output.strip()

                    with And(
                        "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
                    ):
                        force_select_final = node.query(
                            f"SELECT count() FROM {table1.name} a {join_type}"
                            f"(SELECT * FROM {table1.name} {join_type}"
                            f" {table2.name} on {table1.name}.id = {table2.name}.id) b on a.id=b.id",
                            settings=[("final", 1)],
                        ).output.strip()

                    with Then("I check that compare results are the same"):
                        assert explicit_final == force_select_final


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join_Multiple("1.0")
)
def select_multiple_join_clause_select(self, node=None):
    """Check SELECT query with multiple `JOIN` clause."""
    if node is None:
        node = self.context.node

    table_pairs, join_types_local = [], []

    with Given("I have a list of available join types for this test"):
        join_types_local = define(
            "Join types list",
            [
                join_type
                for join_type in join_types
                if not join_type.startswith("CROSS")
                and not join_type.startswith("ASOF")
                and not join_type.startswith("LEFT ASOF")
            ],
            encoder=lambda s: ", ".join(s),
        )

    with And("I have a list of core table"):
        core_tables = [
            table for table in self.context.tables if table.name.endswith("core")
        ]

    with And("I have a list of corresponding duplicate tables"):
        for table1 in core_tables:
            for table2 in self.context.tables:
                if table2.name.endswith("duplicate") and table2.engine == table1.engine:
                    table_pairs.append((table1, table2))

    for join_type in join_types_local:
        for table1, table2 in table_pairs:
            with Example(f"{table1.engine} {join_type} {table2.engine}", flags=TE):
                with When(f"I have {table1.name} and corresponding {table2.name}"):
                    with When(
                        "I execute query with FINAL modifier specified explicitly"
                    ):
                        join_statement = define(
                            "Multiple join query",
                            f"SELECT count() FROM {table1.name} t"
                            f"{' FINAL' if table1.final_modifier_available else ''}  {join_type} "
                            f"(SELECT * FROM {table2.name} "
                            f"{' FINAL' if table2.final_modifier_available else ''}) a on t.id = a.id"
                            f" {join_type} "
                            f"(SELECT * FROM {table2.name} "
                            f"{' FINAL' if table2.final_modifier_available else ''}) b on"
                            f" a.id=b.id",
                        )

                        explicit_final = node.query(
                            join_statement,
                            settings=[("joined_subquery_requires_alias", 0)],
                        ).output.strip()

                    with And(
                        "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
                    ):
                        force_select_final = node.query(
                            f"SELECT count() FROM {table1.name} {join_type} "
                            f"{table2.name} on {table1.name}.id = {table2.name}.id {join_type}"
                            f" {table2.name} b on {table2.name}.id=b.id",
                            settings=[("final", 1)],
                        ).output.strip()

                    with Then("I check that compare results are the same"):
                        assert explicit_final == force_select_final


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery("1.0")
)
def select_subquery(self, node=None):
    """Check SELECT query with subquery."""
    if node is None:
        node = self.context.node

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        tables = define(
            "tables",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                and not table.name.startswith("expr_subquery")
                and not table.name.endswith("wview_final")
                and not table.name.endswith("_nview")
                and not table.name.endswith("_lview")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with When(f"{table.name}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    f"SELECT count() FROM (SELECT * FROM {table.name}"
                    f"{' FINAL' if table.final_modifier_available else ''})"
                ).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    f"SELECT count() FROM (SELECT * FROM {table.name})",
                    settings=[("final", 1)],
                ).output.strip()

            with Then("I compare results are the same"):
                assert explicit_final == force_select_final


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_Nested("1.0")
)
def select_nested_subquery(self, node=None):
    """Check SELECT query with nested 3 lvl subquery."""
    if node is None:
        node = self.context.node

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if not table.name.endswith("duplicate")
                and not table.name.startswith("expr_subquery")
                and not table.name.endswith("wview_final")
                and not table.name.endswith("_nview")
                and not table.name.endswith("_lview")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    for table in tables:
        with When(f"{table.name}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    f"SELECT count() FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM {table.name}"
                    f"{' FINAL' if table.final_modifier_available else ''})))"
                ).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    f"SELECT count() FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM {table.name})))",
                    settings=[("final", 1)],
                ).output.strip()

            with Then("I compare results are the same"):
                assert explicit_final == force_select_final


@TestOutline
def select_prewhere_where_subquery(self, node=None, clause=None):
    """Check SELECT query with `PREWHERE`/`WHERE' with subquery."""
    if node is None:
        node = self.context.node

    table_pairs = []

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        tables = define(
            "Source set of tables with excluded duplicate, system, auxiliary tables and "
            "some not supported views by this test",
            [
                table
                for table in self.context.tables
                if table.name.endswith("core")
                and not table.name.startswith("Merge")
                and not table.name.startswith("ReplicatedMerge")
                and not table.name.startswith("Log")
                and not table.name.startswith("StripeLog")
                and not table.name.startswith("TinyLog")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    with And("I create list of table pairs for this test"):
        for table1 in tables:
            for table2 in self.context.tables:
                if table2.name.startswith("expr_subquery"):
                    table_pairs.append((table1, table2))

    for table1, table2 in table_pairs:
        with When(f"I have {table1.name} and subquery table {table2.name}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    f"SELECT * FROM {table1.name} FINAL {clause}"
                    f" x = (SELECT x FROM {table2.name} FINAL) "
                    f"ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
                ).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    f"SELECT * FROM {table1.name} {clause} x = (SELECT x FROM {table2.name}) "
                    f"ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()

            with Then("I compare results are the same"):
                assert explicit_final == force_select_final


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_ExpressionInPrewhere(
        "1.0"
    )
)
def select_prewhere_subquery(self):
    """Check query with `PREWHERE` with subquery."""
    select_prewhere_where_subquery(clause="PREWHERE")


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_ExpressionInWhere(
        "1.0"
    )
)
def select_where_subquery(self):
    """Check query with`WHERE` with subquery."""
    select_prewhere_where_subquery(clause="WHERE")


@TestOutline
def select_prewhere_where_in_subquery(self, node=None, clause=None):
    """Check SELECT query with `PREWHERE`/`WHERE' with `IN` statement subquery."""
    if node is None:
        node = self.context.node

    table_pairs = []

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        tables = define(
            "tables",
            [
                table
                for table in self.context.tables
                if table.name.endswith("core")
                and not table.name.startswith("Merge")
                and not table.name.startswith("ReplicatedMerge")
                and not table.name.startswith("Log")
                and not table.name.startswith("StripeLog")
                and not table.name.startswith("TinyLog")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    with And("I create list of table pairs for this test"):
        for table1 in tables:
            for table2 in self.context.tables:
                if table2.name.startswith("expr_subquery"):
                    table_pairs.append((table1, table2))

    for table1, table2 in table_pairs:
        with When(f"I have {table1.name} and subquery table {table2.name}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    f"SELECT * FROM {table1.name} FINAL {clause}"
                    f" x IN (SELECT x FROM {table2.name} FINAL) "
                    f"ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
                ).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    f"SELECT * FROM {table1.name} {clause} x IN (SELECT x FROM {table2.name}) "
                    f"ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("final", 1)],
                ).output.strip()

            with Then("I compare results are the same"):
                assert explicit_final == force_select_final


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_INPrewhere(
        "1.0"
    )
)
def select_prewhere_in_subquery(self):
    """Check query with `PREWHERE` with `IN` statement subquery."""
    select_prewhere_where_in_subquery(clause="PREWHERE")


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_INWhere("1.0")
)
def select_where_in_subquery(self):
    """Check query with `WHERE` with `IN` statement subquery."""
    select_prewhere_where_in_subquery(clause="WHERE")


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery_ExpressionInArrayJoin(
        "1.0"
    )
)
def select_array_join_subquery(self, node=None):
    """Check SELECT query with `ARRAY JOIN` where array is build from a sub-query result."""
    if node is None:
        node = self.context.node

    name = f"arrays_test{getuid()}"

    with Given("I create engines list for current test"):
        engines = define(
            "engines",
            [
                "ReplacingMergeTree",
                "AggregatingMergeTree",
                "SummingMergeTree",
                "MergeTree",
                "StripeLog",
                "TinyLog",
                "Log",
            ],
            encoder=lambda s: ", ".join(s),
        )

    with And(
        "I form `create` and `populate` queries for table with array data type and all engines from engine list"
    ):
        table = define(
            "array table query",
            """CREATE TABLE {name}
            (
                s String,
                arr Array(UInt8)
            ) ENGINE = {engine}
            {order}""",
        )

        insert = define(
            "array value insert query",
            f"INSERT INTO {name} VALUES ('Hello', [1,2]), ('World', [3,4,5]), ('Goodbye', []);",
        )

    for engine in engines:
        with When(f"{engine}"):
            try:
                with When(f"I create and populate table with array type"):
                    node.query(
                        f"{table.format(name=name, engine=engine, order='') if engine.endswith('Log') else table.format(name=name, engine=engine, order='ORDER BY s;')}"
                    )
                    node.query("SYSTEM STOP MERGES")
                    node.query(insert)
                    node.query(insert)

                for table2 in self.context.tables:
                    if table2.name.startswith("expr_subquery"):
                        with When("I execute query with force_select_final=1 setting"):
                            force_select_final = node.query(
                                f"SELECT count() FROM {name} ARRAY JOIN "
                                f"(select arr from {table2.name} LIMIT 1) as zz",
                                settings=[("final", 1)],
                            ).output.strip()

                        with And(
                            "I execute the same query with FINAL modifier specified explicitly"
                        ):
                            if engine.startswith("Merge") or engine.endswith("Log"):
                                explicit_final = node.query(
                                    f"SELECT count() FROM {name} ARRAY JOIN "
                                    f"(select arr from {table2.name} LIMIT 1) as zz"
                                ).output.strip()
                            else:
                                explicit_final = node.query(
                                    f"SELECT count() FROM {name} FINAL ARRAY JOIN"
                                    f" (select arr from {table2.name} FINAL) as zz"
                                ).output.strip()

                        with Then("I compare results are the same"):
                            assert explicit_final == force_select_final

            finally:
                node.query(f"DROP TABLE {name}")


@TestFeature
def run_tests(self):
    """Feature to run all scenarios in this module."""
    with Pool(3) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()


@TestFeature
def with_experimental_analyzer(self):
    """Run all tests with allow_experimental_analyzer=1."""
    with Given("I set allow_experimental_analyzer=1"):
        allow_experimental_analyzer()
    run_tests()


@TestFeature
def without_experimental_analyzer(self):
    """Run all tests without allow_experimental_analyzer set."""
    run_tests()


@TestFeature
@Name("general")
@Specifications(SRS032_ClickHouse_Automatic_Final_Modifier_For_Select_Queries)
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier("1.0"),
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries("1.0"),
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_CreateStatement(
        "1.0"
    ),
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_MergeTree("1.0"),
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_ReplicatedMergeTree(
        "1.0"
    ),
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_EnginesOverOtherEngines(
        "1.0"
    ),
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_IgnoreOnNotSupportedTableEngines(
        "1.0"
    ),
)
def feature(self):
    """Sanity tests for --final query setting."""
    if check_clickhouse_version("<23.2")(self):
        skip(
            reason="--final query setting is only supported on ClickHouse version >= 23.2"
        )

    Feature(run=without_experimental_analyzer)
    Feature(run=with_experimental_analyzer)
