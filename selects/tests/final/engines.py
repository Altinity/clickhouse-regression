from testflows.core import *
from testflows.asserts import error
from selects.requirements import *
from selects.tests.steps import *


@TestOutline
def select_final(self, ignore_force_select_final=False, select_count=None, engine=None):
    """Check applying of 'FINAL' modifier automatically for different engines"""
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_table_{uid}"

    try:
        with Given("I create table with with `force_select_final=1`"):
            node.query(
                f"create table if not exists {table_name} (x String, sign Int8 DEFAULT 1)"
                f" engine={engine}() ORDER BY x SETTINGS force_select_final=1;"
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
def force_select_final_replacingmergetree(self):
    """
    ReplacingMergeTree table engine check for 'force_select_final' and 'ignore_force_select_final' settings
    """
    select_final(
        ignore_force_select_final=False, select_count=1, engine="ReplacingMergeTree"
    )
    select_final(
        ignore_force_select_final=True, select_count=2, engine="ReplacingMergeTree"
    )


@TestScenario
def force_select_final_collapsingmergetree(self):
    """
    CollapsingMergeTree table engine check for 'force_select_final' and 'ignore_force_select_final' settings
    """
    select_final(
        ignore_force_select_final=False, select_count=1, engine="CollapsingMergeTree"
    )
    select_final(
        ignore_force_select_final=True, select_count=2, engine="CollapsingMergeTree"
    )


@TestFeature
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_MergeTree("1.0")
)
@Name("engines")
def feature(self):
    """Check FINAL modifier."""
    for scenario in loads(current_module(), Scenario):
        scenario()
