from testflows.core import *
from helpers.common import check_clickhouse_version

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_WelchTTest,
)

from aggregate_functions.tests.steps import get_snapshot_id, execute_query
from aggregate_functions.tests.quantileWeighted import scenario as checks


@TestScenario
@Name("welchTTest")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_WelchTTest("1.0"))
def scenario(
    self,
    func="welchTTest({params})",
    table=None,
    snapshot_id=None,
    decimal=True,
    date=False,
    datetime=False,
):
    """Check welchTTest aggregate function by using the same tests as for quantileWeighted."""
    clickhouse_version = (
        ">=22.6" if check_clickhouse_version("<23.2")(self) else ">=23.2"
    )
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    if 'Merge' in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    with Check("single value in 0 population"):
        execute_query(
            f"SELECT {func.format(params='sample_data,sample_index')}, any(toTypeName(sample_data)), any(toTypeName(sample_index)) FROM values('sample_data Int8, sample_index Int8', (10,0), (11,1), (12,1), (1,1), (2,1), (3,1))"
        )

    with Check("single value in 1 population"):
        execute_query(
            f"SELECT {func.format(params='sample_data,sample_index')}, any(toTypeName(sample_data)), any(toTypeName(sample_index)) FROM values('sample_data Int8, sample_index Int8', (10,1), (11,0), (12,0), (1,0), (2,0), (3,0))"
        )

    checks(
        func=func,
        decimal=decimal,
        date=date,
        datetime=datetime,
        snapshot_id=self.context.snapshot_id,
    )
