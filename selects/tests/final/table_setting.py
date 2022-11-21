from testflows.core import *
from testflows.asserts import error
from selects.requirements import *
from selects.tests.steps import *


@TestScenario
@Requirements(

)
def force_select_final_not_support(self):
    """Check exception message when `force_select_final` setting applies to MergeTree table with engine which
    doesn't support 'FINAL' modifier.
    """
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_table_{uid}"

    with Given(
        "I create table with `force_select_final=1` and check that Exception has been ignored"
    ):
        node.query(
            f"create table if not exists {table_name} (x String)"
            f" engine=MergeTree() ORDER BY x SETTINGS force_select_final=1;"
        )


@TestOutline
def select_final(self, ignore_force_select_final=False, select_count=None):
    """Check applying of 'FINAL' modifier automatically"""
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_table_{uid}"

    try:
        with Given("I create table with with `force_select_final=1`"):
            node.query(
                f"create table if not exists {table_name} (x String)"
                f" engine=ReplacingMergeTree() ORDER BY x SETTINGS force_select_final=1;"
            )

        with Then(f"I make insert into table"):
            node.query(f"insert into {table_name} values ('abc');")
            node.query(f"insert into {table_name} values ('abc');")

        with Then("I check 'SELECT count()' output"):
            node.query(
                f"select count() from {table_name}"
                f"{' SETTINGS ignore_force_select_final=1' if ignore_force_select_final else ''};",
                message=f"{select_count}",
            )
    finally:
        with Finally("I clean up"):
            with By("dropping table if exists"):
                node.query(f"DROP TABLE IF EXISTS {table_name}")


@TestScenario
@Requirements(

)
def force_select_final(self):
    """Check applying of 'FINAL' modifier automatically using with
    `force_select_final=1` MergeTree table setting.
    """
    select_final(ignore_force_select_final=False, select_count=1)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQuerySetting_IgnoreForceSelectFinal(
        "1.0"
    )
)
def ignore_force_select_final(self):
    """Check disable of applying FINAL modifier automatically by using `ignore_force_select_final` query setting."""
    select_final(ignore_force_select_final=True, select_count=2)


@TestOutline
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join("1.0"))
def join(
    self,
    force_select_final_table1=False,
    force_select_final_table2=False,
    select_count=None,
):
    """Check auto 'FINAL' modifier with 'JOIN' clause."""
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table1_name = f"test_table1_{uid}"
    table2_name = f"test_table2_{uid}"

    try:
        with Given("I create table with with 2 tables"):
            node.query(
                f"create table if not exists {table1_name} (x String)"
                f" engine=ReplacingMergeTree() ORDER BY x"
                f"{' SETTINGS force_select_final=1' if force_select_final_table1 else ''};"
            )
            node.query(
                f"create table if not exists {table2_name} (x String)"
                f" engine=ReplacingMergeTree() ORDER BY x"
                f"{' SETTINGS force_select_final=1' if force_select_final_table2 else ''};"
            )

        with Then(f"I make insert into two tables table"):
            node.query(f"insert into {table1_name} values ('abc');")
            node.query(f"insert into {table1_name} values ('abc');")
            node.query(f"insert into {table1_name} values ('abc');")

            node.query(f"insert into {table2_name} values ('abc');")
            node.query(f"insert into {table2_name} values ('abc');")

        with Then("I check 'SELECT count() output'"):
            node.query(
                f"select count() from {table1_name} inner join {table2_name} on {table1_name}.x = {table2_name}.x;",
                message=f"{select_count}",
            )
    finally:
        with Finally("I clean up"):
            with By("dropping table if exists"):
                node.query(f"DROP TABLE IF EXISTS {table1_name}")
                node.query(f"DROP TABLE IF EXISTS {table2_name}")


@TestScenario
def join_two_tables_with_final(self):
    """Check auto 'FINAL' modifier with 'JOIN' clause enabled for both tables."""
    join(force_select_final_table1=True, force_select_final_table2=True, select_count=1)


@TestScenario
def join_first_table_with_final(self):
    """Check auto 'FINAL' modifier with 'JOIN' clause enabled only for the first table."""
    join(
        force_select_final_table1=True, force_select_final_table2=False, select_count=2
    )


@TestScenario
def join_second_table_with_final(self):
    """Check auto 'FINAL' modifier with 'JOIN' clause enabled only for the second table."""
    join(
        force_select_final_table1=False, force_select_final_table2=True, select_count=3
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier("1.0"))
@Name("table_setting")
def feature(self):
    """Check enabling automatic final modifier using table engine settings."""
    for scenario in loads(current_module(), Scenario):
        scenario()
