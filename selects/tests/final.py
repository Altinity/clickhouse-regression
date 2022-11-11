from testflows.core import *
from testflows.asserts import error
from selects.requirements import *
from selects.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSettingNotSupport("1.0"))
def force_select_final_not_support(self):
    """Check exception message when `force_select_final` setting applies to MergeTree table engine which
     doesn't support FINAL.
    """
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_table_{uid}"

    with Given(
            "I create table with with `force_select_final=1` and make check for Exception"
    ):
        node.query(f"create table if not exists {table_name} (x String)"
                   f" engine=MergeTree() ORDER BY x SETTINGS force_select_final=1;",
                   exitcode=181, message="DB::Exception: Storage MergeTree doesn't support FINAL.")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting("1.0"))
def force_select_final(self):
    """Check applying FINAL modifier automatically using
    `force_select_final` MergeTree table setting.
    """
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_table_{uid}"

    with Given(
            "I create table with with `force_select_final=1`"
    ):
        node.query(f"create table if not exists {table_name} (x String)"
                   f" engine=ReplacingMergeTree() ORDER BY x SETTINGS force_select_final=1;")

    with Then(f"I make insert to create ClickHouse table"):
        node.query(f"insert into {table_name} values ('abc');")
        node.query(f"insert into {table_name} values ('abc');")

    with Then("I check that 'SELECT count()' output is 1 because force_select_final is turned on"):
        node.query(f"select count() from {table_name};", message="1")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting("1.0"))
def ignore_force_select_final(self):
    """Check disable of applying FINAL modifier automatically by using `ignore_force_select_final` query setting."""
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_table_{uid}"

    with Given(
            "I create table with with `force_select_final=1`"
    ):
        node.query(f"create table if not exists {table_name} (x String)"
                   f" engine=ReplacingMergeTree() ORDER BY x SETTINGS force_select_final=1;")

    with Then(f"I make insert to create ClickHouse table"):
        node.query(f"insert into {table_name} values ('abc');")
        node.query(f"insert into {table_name} values ('abc');")

    with Then("I check that 'SELECT count()' output is 2 because ignore_force_select_final is turned on"):
        node.query(f"select count() from {table_name} SETTINGS ignore_force_select_final=1;", message="2")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier("1.0"))
@Name("final")
def feature(self):
    """Check FINAL modifier."""
    Scenario(run=force_select_final_not_support)
    Feature(run=force_select_final)
    Feature(run=ignore_force_select_final)
