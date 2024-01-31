from testflows.core import *

from helpers.tables import *
from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_FlameGraph,
)


@TestCheck
def check(self):
    with Given(f"I create temporary table"):
        uid = getuid()
        self.context.table = create_table(
            name=uid,
            engine="Memory",
            columns=[
                Column(name="tag_id", datatype=String()),
                Column(name="z", datatype=Int16()),
            ],
        )

    a = None
    with And(f"I populate table with some data"):
        self.context.node.query("set query_profiler_cpu_time_period_ns=10000000")
        self.context.node.query(
            f"INSERT INTO {self.context.table.name} VALUES ('a', 1), ('b', 2)",
            query_id=2000,
        )

    with Check(f"I check the results"):
        if a is not None:
            execute_query(
                f"select arrayJoin(flameGraph(arrayReverse(trace))) from system.trace_log WHERE query_id = '2000' settings allow_introspection_functions=1"
            )


@TestScenario
@Name("flameGraph")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_FlameGraph("1.0"))
def scenario(self, func="flameGraph({params})", table=None, snapshot_id=None):
    """Check flameGraph aggregate function by using the same tests as for any."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table
