from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_Histogram
)

from helpers.datatypes import *
from helpers.tables import (
    is_numeric,
    is_unsigned_integer,
    is_low_cardinality,
    is_nullable,
)
from aggregate_functions.tests.steps import (
    get_snapshot_id,
    execute_query,
    permutations_with_replacement,
)


@TestScenario
@Name("histogram")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_Histogram("1.0"))
def scenario(self, func="histogram({params})({values})", table=None):
    """Check histogram aggregate function"""

    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='5', values='1')}")

    with Check("zero rows"):
        execute_query(
            f"SELECT {func.format(params='5', values='number')} FROM numbers(0)"
        )

    with Check("single row"):
        execute_query(
            f"SELECT {func.format(params='5', values='number')} FROM numbers(1)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='5', values='number')} FROM numbers(10) GROUP BY even"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='5', values='x')}  FROM values('x Nullable(UInt8)', 0, 1, NULL, 3, 4, 5)"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='5', values='x')}  FROM values('x Nullable(UInt8), w Nullable(UInt8)', (NULL,NULL) )"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='5', values='number')}) FROM numbers(1, 10)"
        )

