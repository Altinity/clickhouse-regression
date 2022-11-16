from testflows.core import *
from testflows.asserts import error
from selects.requirements import *
from selects.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSettingNotSupportted("1.0"))
def force_select_final_not_support(self):
    """Check exception message when `force_select_final` setting applies to MergeTree table with engine which
     doesn't support 'FINAL' modifier.
    """
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_table_{uid}"

    with Given(
            "I create table with `force_select_final=1` and make check for Exception"
    ):
        node.query(f"create table if not exists {table_name} (x String)"
                   f" engine=MergeTree() ORDER BY x SETTINGS force_select_final=1;",
                   exitcode=181, message="DB::Exception: Storage MergeTree doesn't support FINAL.")


@TestOutline
def select_final(self, ignore_force_select_final=False, select_count=None):
    """Check applying of 'FINAL' modifier automatically
    """
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_table_{uid}"

    with Given(
            "I create table with with `force_select_final=1`"
    ):
        node.query(f"create table if not exists {table_name} (x String)"
                   f" engine=ReplacingMergeTree() ORDER BY x SETTINGS force_select_final=1;")

    with Then(f"I make insert into table"):
        node.query(f"insert into {table_name} values ('abc');")
        node.query(f"insert into {table_name} values ('abc');")

    with Then("I check 'SELECT count()' output"):
        node.query(f"select count() from {table_name}"
                   f"{' SETTINGS ignore_force_select_final=1' if ignore_force_select_final else ''};",
                   message=f"{select_count}")


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_ForceSelectFinal("1.0"))
def force_select_final(self):
    """Check applying of 'FINAL' modifier automatically using with
    `force_select_final=1` MergeTree table setting.
    """
    select_final(ignore_force_select_final=False, select_count=1)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQuerySetting_IgnoreForceSelectFinal("1.0"))
def ignore_force_select_final(self):
    """Check disable of applying FINAL modifier automatically by using `ignore_force_select_final` query setting."""
    select_final(ignore_force_select_final=True, select_count=2)


@TestOutline
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join("1.0"))
def join(self, force_select_final_table1=False, force_select_final_table2=False, select_count=None):
    """Check auto 'FINAL' modifier with 'JOIN' clause."""
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table1_name = f"test_table1_{uid}"
    table2_name = f"test_table2_{uid}"

    with Given(
            "I create table with with 2 tables"
    ):
        node.query(f"create table if not exists {table1_name} (x String)"
                   f" engine=ReplacingMergeTree() ORDER BY x"
                   f"{' SETTINGS force_select_final=1' if force_select_final_table1 else ''};")
        node.query(f"create table if not exists {table2_name} (x String)"
                   f" engine=ReplacingMergeTree() ORDER BY x"
                   f"{' SETTINGS force_select_final=1' if force_select_final_table2 else ''};")

    with Then(f"I make insert into two tables table"):
        node.query(f"insert into {table1_name} values ('abc');")
        node.query(f"insert into {table1_name} values ('abc');")

        node.query(f"insert into {table2_name} values ('abc');")
        node.query(f"insert into {table2_name} values ('abc');")

    with Then("I check 'SELECT count() output'"):
        node.query(f"select count() from {table1_name} inner join {table2_name} on {table1_name}.x = {table2_name}.x;",
                   message=f"{select_count}")


@TestScenario
def join_two_tables_with_final(self):
    join(force_select_final_table1=True, force_select_final_table2=True, select_count=1)


@TestScenario
def join_first_table_with_final(self):
    join(force_select_final_table1=True, force_select_final_table2=False, select_count=2)


@TestScenario
def join_second_table_with_final(self):
    join(force_select_final_table1=False, force_select_final_table2=True, select_count=2)


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier("1.0"))
@Name("final")
def feature(self):
    """Check FINAL modifier."""
    for scenario in loads(current_module(), Scenario):
        scenario()
