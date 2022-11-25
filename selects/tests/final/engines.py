from testflows.core import *
from testflows.asserts import error
from selects.requirements import *
from selects.tests.steps import *


@TestOutline
def select_final(
    self,
    ignore_force_select_final=False,
    select_count=None,
    engine=None,
    graphite=False,
):
    """Check applying of 'FINAL' modifier automatically for different engines"""
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_table_{uid}"

    try:
        with Given("I create table with with `force_select_final=1`"):
            if graphite:
                retry(node.query, timeout=100, delay=1)(
                    f"CREATE TABLE IF NOT EXISTS {table_name}"
                    f" (d Date, a String, b UInt8, x String, y Int8, Path String, "
                    f"Time DateTime, Value Float64, col UInt64, Timestamp Int64) "
                    f"ENGINE = {engine}"
                    " PARTITION BY y ORDER BY (b, d) PRIMARY KEY b "
                    "SETTINGS force_select_final=1;",
                )
            else:
                node.query(
                    f"create table if not exists {table_name} (x String, sign Int8 DEFAULT 1, version Int8 DEFAULT 1)"
                    f" engine={engine} ORDER BY x SETTINGS force_select_final=1;"
                )

        with Then(f"I make insert into table"):
            if graphite:
                node.query(
                    f"insert into {table_name} values (now(),'a',1,'b',1,'c', 1,1,1,1)"
                )
                node.query(
                    f"insert into {table_name} values (now(),'a',1,'b',1,'c', 1,1,1,1)"
                )
                pause()
            else:
                node.query(f"insert into {table_name} values ('abc',1, 1);")
                node.query(f"insert into {table_name} values ('abc',1, 1);")

        with Then("I check 'SELECT count()' output"):
            if graphite:
                pause()
                node.query(
                    f"select count() from {table_name}"
                    f"{' SETTINGS ignore_force_select_final=1' if ignore_force_select_final else ''};",
                    message=f"{select_count}",
                )
            else:
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
def force_select_final_available_engines(self):
    """
    Check 'force_select_final' and 'ignore_force_select_final' settings for available to `FINAL` modifier
    MergeTree table engines.
    """
    for engine in [
        "ReplacingMergeTree()",
        "CollapsingMergeTree(sign)",
        "SummingMergeTree()",
        "AggregatingMergeTree()",
    ]:
        with Given(
            f"I check 'force_select_final' and 'ignore_force_select_final' settings for {engine} table ENGINE"
        ):
            select_final(ignore_force_select_final=False, select_count=1, engine=engine)
            select_final(ignore_force_select_final=True, select_count=2, engine=engine)


@TestScenario
def force_select_final_unavailable_engines(self):
    """
    Check 'force_select_final' and 'ignore_force_select_final' settings for unavailable to `FINAL` modifier
    MergeTree table engines.
    """
    for engine in ["MergeTree()", "VersionedCollapsingMergeTree(sign,version)"]:
        with Given(
            f"I check 'force_select_final' and 'ignore_force_select_final' settings for {engine} table ENGINE"
        ):
            if engine == "GraphiteMergeTree('graphite_rollup_example')":
                select_final(
                    ignore_force_select_final=False,
                    select_count=2,
                    engine=engine,
                    graphite=True,
                )
                select_final(
                    ignore_force_select_final=True,
                    select_count=2,
                    engine=engine,
                    graphite=True,
                )
            else:
                select_final(
                    ignore_force_select_final=False, select_count=2, engine=engine
                )
                select_final(
                    ignore_force_select_final=True, select_count=2, engine=engine
                )


@TestFeature
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_MergeTree("1.0")
)
@Name("engines")
def feature(self):
    """Check enabling automatic FINAL modifier on different table engines."""
    for scenario in loads(current_module(), Scenario):
        scenario()
