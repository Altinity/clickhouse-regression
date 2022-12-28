from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *


@TestOutline
def select(self, statement, statement_final, node=None, negative=False):
    """Checking basic selects with `FINAL` clause equal to force_select_final select only for core table."""
    if node is None:
        node = self.context.node

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        if negative:
            tables = [
                table for table in self.context.tables if table.name.endswith("core")
            ]
        else:
            tables = [
                table
                for table in self.context.tables
                if table.name.endswith("core")
                or table.name.endswith("_nview_final")
                or table.name.endswith("_mview")
            ]

    for table in tables:
        with When(f"{table.name}"):
            with When("I execute query with FINAL modifier specified explicitly"):
                explicit_final = node.query(
                    statement_final.format(
                        name=table.name,
                        final=f"{' FINAL' if table.final_modifier_available else ''}",
                    )
                ).output.strip()

            with And("I execute the same query without FINAL modifier"):
                without_final = node.query(
                    statement.format(name=table.name)
                ).output.strip()

            with And(
                "I execute the same query without FINAL modifiers but with force_select_final=1 setting"
            ):
                force_select_final = node.query(
                    statement.format(name=table.name),
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
    with Given("I create statements with and without `FINAL`."):
        statement = "SELECT count() FROM {name} FORMAT JSONEachRow;"
        statement_final = "SELECT count() FROM {name} {final} FORMAT JSONEachRow;"

    with Then(
        "I verify for query with `FINAL` data equivalence and non-equivalence for query without `FINAL`."
    ):
        select(statement=statement, statement_final=statement_final)
        select(statement=statement, statement_final=statement_final, negative=True)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Limit("1.0"))
def select_limit(self):
    """Check SELECT query with `LIMIT` clause."""
    with Given("I create statements with and without `FINAL`."):
        statement = (
            "SELECT * FROM {name} ORDER BY (id, x, someCol) LIMIT 1 FORMAT JSONEachRow;"
        )
        statement_final = "SELECT * FROM {name} {final} ORDER BY (id, x, someCol) LIMIT 1 FORMAT JSONEachRow;"

    with Then(
        "I verify for query with `FINAL` data equivalence and non-equivalence for query without `FINAL`."
    ):
        select(statement=statement, statement_final=statement_final)
        select(statement=statement, statement_final=statement_final, negative=True)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_LimitBy("1.0"))
def select_limit_by(self):
    """Check SELECT query with `LIMIT BY` clause."""
    with Given("I create statements with and without `FINAL`."):
        statement = "SELECT * FROM {name} ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;"
        statement_final = "SELECT * FROM {name} {final} ORDER BY (id, x, someCol) LIMIT 1 BY id FORMAT JSONEachRow;"

    with Then(
        "I verify data equivalence for query with `FINAL` and non-equivalence for query without `FINAL`."
    ):
        select(statement=statement, statement_final=statement_final)
        select(statement=statement, statement_final=statement_final, negative=True)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_GroupBy("1.0"))
def select_group_by(self):
    """Check SELECT query with `GROUP BY` clause."""
    with Given("I create statements with and without `FINAL`"):
        statement = "SELECT id, count(x) as cx FROM {name} GROUP BY (id, x) ORDER BY (id, cx) FORMAT JSONEachRow;"
        statement_final = (
            "SELECT id, count(x) as cx FROM {name} {final} GROUP BY (id, x) ORDER BY (id, cx)"
            " FORMAT JSONEachRow;"
        )

    with Then(
        "I verify for query with `FINAL` data equivalence and non-equivalence for query without `FINAL`"
    ):
        select(statement=statement, statement_final=statement_final)
        select(statement=statement, statement_final=statement_final, negative=True)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Distinct("1.0")
)
def select_distinct(self):
    """Check SELECT query with `DISTINCT` clause."""
    with Given("I create statements with and without `FINAL`"):
        statement = "SELECT DISTINCT * FROM {name} ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
        statement_final = (
            "SELECT DISTINCT * FROM {name} {final} ORDER BY (id, x, someCol)"
            " FORMAT JSONEachRow;"
        )

    with Then(
        "I verify for query with `FINAL` data equivalence and non-equivalence for query without `FINAL`"
    ):
        select(statement=statement, statement_final=statement_final)
        select(statement=statement, statement_final=statement_final, negative=True)


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
    with Given("I create statements with and without `FINAL`"):
        statement = "SELECT * FROM {name} WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;"
        statement_final = "SELECT * FROM {name} {final} WHERE x > 3 ORDER BY (id, x, someCol) FORMAT JSONEachRow;"

    with Then(
        "I verify for query with `FINAL` data equivalence and non-equivalence for query without `FINAL`"
    ):
        select(statement=statement, statement_final=statement_final)
        select(statement=statement, statement_final=statement_final, negative=True)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_ArrayJoin("1.0")
)
def select_array_join(self, node=None):
    """Check SELECT query with `ARRAY JOIN` clause."""
    if node is None:
        node = self.context.node

    with Given("I create engines list for current test"):
        engines = [
            "ReplacingMergeTree",
            "AggregatingMergeTree",
            "SummingMergeTree",
            "MergeTree",
            "StripeLog",
            "TinyLog",
            "Log",
        ]

    with And(
        "I form `create` and `populate` statements for table with array data type and all engines from engine list"
    ):
        table = """CREATE TABLE arrays_test
                        (
                            s String,
                            arr Array(UInt8)
                        ) ENGINE = {engine}
                        {order}"""

        insert = """INSERT INTO arrays_test VALUES ('Hello', [1,2]), ('World', [3,4,5]), ('Goodbye', []);"""

        for engine in engines:
            with When(f"{engine}"):
                try:
                    with When(
                        f"I create and populate table with array type for {engine} from engine list"
                    ):
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

                        if engine.startswith("Merge") or engine.endswith("Log"):
                            with When(
                                "I execute the same query with FINAL modifier specified explicitly"
                            ):
                                without_final = node.query(
                                    f"SELECT count() FROM arrays_test ARRAY JOIN arr"
                                ).output.strip()
                            with Then("I compare results are the same"):
                                assert without_final == force_select_final

                        else:
                            with When(
                                "I execute the same query with FINAL modifier specified explicitly"
                            ):
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

    for join_type in join_types:
        with Given(f"I check force_select_final feature for {join_type}"):
            for table1 in self.context.tables:
                if table1.name.endswith("core"):

                    with When(f"I select {table1.name} as table a"):
                        for table2 in self.context.tables:
                            if (
                                table2.name.endswith("duplicate")
                                and table2.engine == table1.engine
                            ):

                                with When(
                                    f"I select table with the same structure {table2.name} as table b"
                                ):
                                    with Then(
                                        "I check that select with force_select_final=1 setting"
                                        f" equal 'SELECT...FINAL' for {table1.name} and {table2.name} "
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

    with Given("I exclude doesn't support engines"):
        join_types_local = [
            join_type
            for join_type in join_types if not join_type.startswith("CROSS") or not join_type.startswith("ASOF")
                                           or not join_type.startswith("LEFT ASOF")
        ]

    for join_type in join_types_local:
        with When(f"I check force_select_final feature for {join_type}"):
            for table1 in self.context.tables:
                if table1.name.endswith("core"):
                    with When(f"I select {table1.name} as table a"):
                        for table2 in self.context.tables:
                            if (
                                table2.name.endswith("duplicate")
                                and table2.engine == table1.engine
                            ):
                                with When(
                                    f"I select same structure table {table2.name} as table b"
                                ):
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

    with Given(f"I check force_select_final feature for `INNER JOIN`"):
        for table1 in self.context.tables:
            if table1.name.endswith("core"):

                with When(f"I select {table1.name} as table a"):
                    for table2 in self.context.tables:

                        if (table2.name != table1.name) and table2.name.endswith(
                            "core"
                        ):
                            with When(f"I select {table2.name} as table b"):
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
def select_family_union_clause(self, node=None, clause=None):
    """Check `SELECT` that is using union family clause with `FINAL`
    equal to the same select without `FINAL` but with force_select_final=1 setting."""
    if node is None:
        node = self.context.node

    with Given(f"I check force_select_final setting with union family clause"):
        for table1 in self.context.tables:
            if table1.name.endswith("core") and table1.final_modifier_available:
                with When(f"I select {table1.name} as first table"):
                    for table2 in self.context.tables:
                        if table2.name.endswith("duplicate") and table2.name.startswith(
                            table1.engine
                        ):
                            with When(f"I select {table2.name} as second table"):
                                with Then(
                                    f"I check that select with {clause} with force_select_final"
                                    f" equal 'SELECT...FINAL'"
                                ):
                                    assert (
                                        node.query(
                                            f"SELECT id, count(*) FROM {table1.name}"
                                            f"{' FINAL' if table1.final_modifier_available else ''} "
                                            f" GROUP BY id"
                                            f" {clause}"
                                            f" SELECT id, count(*) FROM {table2.name}"
                                            f"{' FINAL' if table2.final_modifier_available else ''} "
                                            f" GROUP BY id"
                                        ).output.strip()
                                        == node.query(
                                            f"SELECT id, count(*) FROM {table1.name} GROUP BY id"
                                            f" {clause}"
                                            f" SELECT id, count(*) FROM {table2.name} GROUP BY id",
                                            settings=[("force_select_final", 1)],
                                        ).output.strip()
                                    )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Union("1.0"))
def select_union_clause(self):
    """Check SELECT query with `UNION` clause."""
    select_family_union_clause(clause="UNION ALL")
    select_family_union_clause(clause="UNION DISTINCT")


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Intersect("1.0")
)
def select_intersect_clause(self):
    """Check SELECT query with `INTERSECT` clause."""
    select_family_union_clause(clause="INTERSECT")


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Except("1.0"))
def select_except_clause(self):
    """Check SELECT query with `EXCEPT` clause."""
    select_family_union_clause(clause="EXCEPT")


@TestScenario
def select_union_clause_negative(self, node=None):
    """Check `SELECT` that is using 'UNION' clause
    not equal to the same select with force_select_final=1 setting`."""
    if node is None:
        node = self.context.node

    with Given(
        f"I check negative case for force_select_final setting with union clause"
    ):
        for table1 in self.context.tables:
            if table1.name.endswith("core") and table1.final_modifier_available:
                with When(f"I select {table1.name} as first table"):
                    for table2 in self.context.tables:
                        if table2.name.endswith("duplicate") and table2.name.startswith(
                            table1.engine
                        ):
                            with When(f"I select {table2.name} as second table"):
                                with Then(
                                    f"I check that select with union with force_select_final not equal "
                                    f"to simple 'SELECT...' "
                                ):
                                    for union in ["UNION ALL", "UNION DISTINCT"]:
                                        assert (
                                            node.query(
                                                f"SELECT id, count(*) FROM {table1.name}"
                                                f" GROUP BY id"
                                                f" {union}"
                                                f" SELECT id, count(*) FROM {table2.name}"
                                                f" GROUP BY id"
                                            ).output.strip()
                                            != node.query(
                                                f"SELECT id, count(*) FROM {table1.name} GROUP BY id"
                                                f" {union}"
                                                f" SELECT id, count(*) FROM {table2.name} GROUP BY id",
                                                settings=[("force_select_final", 1)],
                                            ).output.strip()
                                        )


@TestFeature
@Name("force modifier")
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries("1.0"))
def feature(self):
    """Check force_final_modifier setting."""
    for scenario in loads(current_module(), Scenario):
        scenario()
