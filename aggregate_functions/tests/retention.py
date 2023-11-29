from helpers.tables import is_numeric

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_Retention,
)


@TestScenario
@Name("retention")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_Retention("1.0"))
def scenario(
    self, func="retention({params})", table=None, decimal=False, snapshot_id=None
):
    """Check retention aggregate function"""

    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    with Check("constant"):
        params = "1,1"
        execute_query(
            f"SELECT {func.format(params=params)}, any(toTypeName(1)),  any(toTypeName(1))"
        )

    with Check("zero rows"):
        params = "number = 1, number = 1"
        execute_query(
            f"SELECT {func.format(params=params)}, any(toTypeName(1)), any(toTypeName(1)) FROM numbers(0)"
        )

    with Check("single row"):
        params = "number = 1, number = 1"
        execute_query(
            f"SELECT {func.format(params=params)}, any(toTypeName(1)), any(toTypeName(1)) FROM numbers(1)"
        )

    with Check("with group by"):
        params = "number = 1, number = 1"
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params=params)}, any(toTypeName(1)), any(toTypeName(1)) FROM numbers(10) GROUP BY even"
        )

    with Check("NULL value handling"):
        params = "x = 1, x = NULL"
        execute_query(
            f"SELECT {func.format(params=params)}, any(toTypeName(1)), any(toTypeName(1))  FROM values('x Nullable(UInt8)', 0, 1, NULL, 3, 4, 5)"
        )

    with Check("single NULL value"):
        params = "x = 1, x = NULL"
        execute_query(
            f"SELECT {func.format(params=params)}, any(toTypeName(1)), any(toTypeName(1)) FROM values('x Nullable(UInt8), w Nullable(UInt8)', (NULL,NULL))"
        )

    with Check("return type"):
        params = "number = 1, number = 2"
        execute_query(
            f"SELECT toTypeName({func.format(params=params)}), any(toTypeName(1)), any(toTypeName(1)) FROM numbers(1, 10)"
        )

    with Check("example"):
        params = "a = 1, a = 2, a = 4, a = 1"
        execute_query(
            f"SELECT {func.format(params=params)}, any(toTypeName(1)), any(toTypeName(1)), any(toTypeName(1)), any(toTypeName(1)) FROM values('a Int32', (1), (1), (1), (2), (3))"
        )

    for column in table.columns:
        column_name, column_type = column.name, column.datatype.name

        if not is_numeric(column.datatype, decimal=decimal):
            continue

        with Check(f"{column_type}"):
            params = f"{column_name} = 0, {column_name} = 1"
            execute_query(
                f"SELECT {func.format(params=params)}, any(toTypeName(1)), any(toTypeName(1)) FROM {table.name}"
            )
