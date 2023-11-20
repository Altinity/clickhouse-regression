from helpers.tables import is_numeric

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_Histogram,
)


@TestScenario
@Name("histogram")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_Histogram("1.0"))
def scenario(self, func="histogram({params})", table=None, decimal=False):
    """Check histogram aggregate function"""

    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='5)(1')}")

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='5)(number')} FROM numbers(0)")

    with Check("single row"):
        execute_query(f"SELECT {func.format(params='5)(number')} FROM numbers(1)")

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='5)(number')} FROM numbers(10) GROUP BY even"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='5)(x')}  FROM values('x Nullable(UInt8)', 0, 1, NULL, 3, 4, 5)"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='5)(x')}  FROM values('x Nullable(UInt8), w Nullable(UInt8)', (NULL,NULL) )"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='5)(number')}) FROM numbers(1, 10)"
        )

    with Check("different number of bins"):
        for k in range(1, 10):
            with When(f"{k}"):
                execute_query(
                    f"SELECT {func.format(params=f'{k})(number')} FROM numbers(100)"
                )

    for column in table.columns:
        column_name, column_type = column.name, column.datatype.name

        if not is_numeric(column.datatype, decimal=decimal):
            continue

        with Check(f"{column_type}"):
            execute_query(
                f"SELECT {func.format(params=f'5)({column_name}')} FROM {table.name}"
            )
