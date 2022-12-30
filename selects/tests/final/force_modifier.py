from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *


@TestOutline
def select(self, query, query_with_final, node=None, negative=False):
    """Checking basic selects with `FINAL` clause equal to force_select_final select only for core table."""
    if node is None:
        node = self.context.node

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        tables = define("tables", [
            table
            for table in self.context.tables
            if table.name.endswith("core")
            or table.name.endswith("_nview_final")
            or table.name.endswith("_mview")
        ], encoder=lambda tables: ", ".join([table.name for table in tables]))

    for table in tables:
        with When(f"{table.name}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    query_with_final.format(
                        name=table.name,
                        final=f"{' FINAL' if table.final_modifier_available else ''}",
                    )
                ).output.strip()

            with And("I execute the same query without FINAL modifier"):
                without_final = node.query(query.format(name=table.name)).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    query.format(name=table.name),
                    settings=[("force_select_final", 1)],
                ).output.strip()

            if negative:
                with Then("I check that compare results are different"):
                    if (
                        table.final_modifier_available
                        and without_final != explicit_final
                    ):
                        assert without_final != force_select_final
            else:
                with Then("I check that compare results are the same"):
                    assert explicit_final == force_select_final


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Select("1.0"))
def select_count(self):
    """Check `SELECT count()` clause."""
    with Given("I create queries with and without `FINAL`."):
        query = define(
            "query without FINAL", "SELECT count() FROM {name} FORMAT JSONEachRow;"
        )
        query_with_final = define(
            "query with FINAL", "SELECT count() FROM {name} {final} FORMAT JSONEachRow;"
        )

    with Then("I check positive case"):
        select(query=query, query_with_final=query_with_final)

    with And("I check negative case"):
        select(query=query, query_with_final=query_with_final, negative=True)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Limit("1.0"))
def select_limit(self):
    """Check SELECT query with `LIMIT` clause."""
    with Given("I create queries with and without `FINAL`."):
        query = define(
            "query without FINAL",
            "SELECT * FROM {name} ORDER BY (id, x, someCol) LIMIT 1 FORMAT JSONEachRow;",
        )
        query_with_final = define(
            "query with FINAL",
            "SELECT * FROM {name} {final} ORDER BY (id, x, someCol) LIMIT 1 FORMAT JSONEachRow;",
        )

    with Then("I check positive case"):
        select(query=query, query_with_final=query_with_final)

    with And("I check negative case"):
        select(query=query, query_with_final=query_with_final, negative=True)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_LimitBy("1.0"))
def select_limit_by(self):
    """Check SELECT query with `LIMIT BY` clause."""
    with Given("I create queries with and without `FINAL`."):
        query = define(
            "query without FINAL",
            "SELECT * FROM {name} ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;",
        )
        query_with_final = define(
            "query with FINAL",
            "SELECT * FROM {name} {final} ORDER BY (id, x, someCol)"
            " LIMIT 1 BY id FORMAT JSONEachRow;",
        )

    with Then("I check positive case"):
        select(query=query, query_with_final=query_with_final)

    with And("I check negative case"):
        select(query=query, query_with_final=query_with_final, negative=True)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_GroupBy("1.0"))
def select_group_by(self):
    """Check SELECT query with `GROUP BY` clause."""
    with Given("I create queries with and without `FINAL`"):
        query = define(
            "query without FINAL",
            "SELECT id, count(x) as cx FROM {name} GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
        )
        query_with_final = define(
            "query with FINAL",
            "SELECT id, count(x) as cx FROM {name} {final} "
            "GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;",
        )

    with Then("I check positive case"):
        select(query=query, query_with_final=query_with_final)

    with And("I check negative case"):
        select(query=query, query_with_final=query_with_final, negative=True)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Distinct("1.0")
)
def select_distinct(self):
    """Check SELECT query with `DISTINCT` clause."""
    with Given("I create queries with and without `FINAL`"):
        query = define(
            "query without FINAL",
            "SELECT DISTINCT * FROM {name} ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
        )
        query_with_final = define(
            "query with FINAL",
            "SELECT DISTINCT * FROM {name} {final} ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
        )

    with Then("I check positive case"):
        select(query=query, query_with_final=query_with_final)

    with And("I check negative case"):
        select(query=query, query_with_final=query_with_final, negative=True)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Prewhere("1.0")
)
def select_prewhere(self, node=None):
    """Check SELECT query with `PREWHERE` clause."""
    if node is None:
        node = self.context.node

    with Given("I exclude Log family engines as they don't support `PREWHERE`"):
        tables = [
            table
            for table in self.context.tables
            if table.name.endswith("core") and not table.engine.endswith("Log")
        ]

    for table in tables:
        with When(f"{table}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    f"SELECT * FROM {table.name} {' FINAL' if table.final_modifier_available else ''}"
                    f" PREWHERE x > 3 "
                    f"ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
                ).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    f"SELECT * FROM {table.name} PREWHERE x > 3 "
                    f"ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
                    settings=[("force_select_final", 1)],
                ).output.strip()

            with Then("I compare results are the same"):
                assert explicit_final == force_select_final


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Where("1.0"))
def select_where(self):
    """Check SELECT query with `WHERE` clause."""
    with Given("I create queries with and without `FINAL`"):
        query = define(
            "query without FINAL",
            "SELECT * FROM {name} WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
        )
        query_with_final = define(
            "query with FINAL",
            "SELECT * FROM {name} {final} WHERE x > 3 "
            "ORDER BY (id, x, someCol) FORMAT JSONEachRow;",
        )

    with Then("I check positive case"):
        select(query=query, query_with_final=query_with_final)

    with And("I check negative case"):
        select(query=query, query_with_final=query_with_final, negative=True)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_ArrayJoin("1.0")
)
def select_array_join(self, node=None):
    """Check SELECT query with `ARRAY JOIN` clause."""
    if node is None:
        node = self.context.node

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
            """CREATE TABLE arrays_test
            (
                s String,
                arr Array(UInt8)
            ) ENGINE = {engine}
            {order}""",
        )

        insert = define(
            "array value insert query",
            "INSERT INTO arrays_test VALUES ('Hello', [1,2]), ('World', [3,4,5]), ('Goodbye', []);",
        )

    for engine in engines:
        with When(f"{engine}"):
            try:
                with When(f"I create and populate table with array type"):
                    node.query(
                        f"{table.format(engine=engine, order='') if engine.endswith('Log') else table.format(engine=engine, order='ORDER BY s;')}"
                    )
                    node.query("SYSTEM STOP MERGES")
                    node.query(insert)
                    node.query(insert)

                with When("I execute query with force_select_final=1 setting"):
                    force_select_final = node.query(
                        "SELECT count() FROM arrays_test ARRAY JOIN arr",
                        settings=[("force_select_final", 1)],
                    ).output.strip()

                with And(
                    "I execute the same query with FINAL modifier specified explicitly"
                ):
                    if engine.startswith("Merge") or engine.endswith("Log"):
                        explicit_final = node.query(
                            f"SELECT count() FROM arrays_test ARRAY JOIN arr"
                        ).output.strip()
                    else:
                        explicit_final = node.query(
                            "SELECT count() FROM arrays_test FINAL ARRAY JOIN arr"
                        ).output.strip()

                with Then("I compare results are the same"):
                    assert explicit_final == force_select_final

            finally:
                node.query("DROP TABLE arrays_test")


@TestScenario
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

    for join_type in join_types:
        with When(f"{join_type}"):
            for table1, table2 in table_pairs:
                with When(f"I have {table1.name} and corresponding {table2.name}"):
                    with Then(
                        "I check that select with force_select_final=1 setting"
                        f" equals 'SELECT...FINAL' for {table1.name} and {table2.name} "
                        f"with {join_type} clause"
                    ):
                        join_statement = (
                            f"SELECT count() FROM {table1.name}"
                            f"{' FINAL' if table1.final_modifier_available else ''}"
                            f" {join_type} "
                            f" {table2.name} on"
                            f" {table1.name}.key = {table2.name}.key"
                        )

                        assert_joins(
                            join_statement=join_statement,
                            table=table1,
                            table2=table2,
                            join_type=join_type,
                            node=node,
                        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join("1.0"))
def select_join_clause_select_all_types(self, node=None):
    """Check `select count()` with some type of 'JOIN SELECT ... FINAL' clause with `FINAL` clause
    equal to the same select without `FINAL` but with force_select_final=1 setting."""
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
        with When(f"{join_type}"):
            for table1, table2 in table_pairs:
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
    """Check SELECT query with `INNER JOIN` clause."""
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
                        settings=[("force_select_final", 1)],
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
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_With("1.0"))
def select_with_clause(self, node=None, negative=False):
    """Check SELECT query with `WITH` clause."""
    if node is None:
        node = self.context.node

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        define(
            "Tables list for current test",
            [
                table.name
                for table in self.context.tables
                if table.name.endswith("core")
                or table.name.endswith("_nview_final")
                or table.name.endswith("_mview")
            ],
            encoder=lambda s: ", ".join(s),
        ) # FIXME: change!

        tables = [
            table
            for table in self.context.tables
            if table.name.endswith("core")
            or table.name.endswith("_nview_final")
            or table.name.endswith("_mview")
        ]

    with Given("I create `WITH` query with and without `FINAL`"):
        with_query = define(
            "query",
            """
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
            """,
        )

    for table in tables:
        with When(f"{table.name}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    with_query.format(
                        table_name=table.name,
                        final=f"{'FINAL' if table.final_modifier_available else ''}",
                    ),
                    exitcode=0,
                ).output.strip()

            with And("I execute the same query without FINAL modifier"):
                without_final = node.query(
                    with_query.format(
                        table_name=table.name,
                        final="",
                    ),
                    exitcode=0,
                ).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    with_query.format(table_name=table.name, final=""),
                    exitcode=0,
                    settings=[("force_select_final", 1)],
                ).output.strip()

            if negative:
                with Then("I check that compare results are different"):
                    if (
                        table.final_modifier_available
                        and without_final != explicit_final
                    ):
                        assert without_final != force_select_final
                        pause()
            else:
                with Then("I check that compare results are the same"):
                    assert explicit_final == force_select_final


@TestScenario
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
        # FIXME: use define
        core_tables = [
            table for table in self.context.tables if table.name.endswith("core")
        ]

    with And("I have a list of corresponding duplicate tables"):
        for table1 in core_tables:
            for table2 in self.context.tables:
                if table2.name.endswith("duplicate") and table2.engine == table1.engine:
                    table_pairs.append((table1, table2))

    for join_type in join_types_local:
        with When(f"{join_type}"):
            for table1, table2 in table_pairs:
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
                            settings=[("force_select_final", 1)],
                        ).output.strip()

                    with Then("I check that compare results are the same"):
                        assert explicit_final == force_select_final


@TestScenario
def select_multiple_join_clause_select(self, node=None):
    """Check SELECT query with nested `JOIN` clause."""
    # xfail("doesn't work ")
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
        with When(f"{join_type}"):
            for table1, table2 in table_pairs:
                with When(f"I have {table1.name} and corresponding {table2.name}"):
                    with When(
                        "I execute query with FINAL modifier specified explicitly"
                    ):
                        join_statement = define(
                            "Multiple join query",
                            f"SELECT count() FROM {table1.name} c"
                            f"{' FINAL' if table1.final_modifier_available else ''}  {join_type} "
                            f"(SELECT * FROM {table2.name} "
                            f"{' FINAL' if table2.final_modifier_available else ''}) a on c.id = a.id"
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
                            settings=[("force_select_final", 1)],
                        ).output.strip()

                    with Then("I check that compare results are the same"):
                        assert explicit_final == force_select_final


@TestFeature
@Name("force modifier")
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries("1.0"))
def feature(self):
    """Check force_final_modifier setting."""
    for scenario in loads(current_module(), Scenario):
        scenario()
