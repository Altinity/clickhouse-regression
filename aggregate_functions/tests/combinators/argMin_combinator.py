from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_ArgMin,
)

from helpers.tables import is_numeric


@TestScenario
@Name("argMin_combinator")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_ArgMin("1.0"))
def scenario(
    self, func, snapshot_id=None, clickhouse_version=None, table=None, decimal=True
):
    """Check -ArgMin combinator."""

    if table is None:
        table = self.context.table

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    func = f"{func}ArgMin({{params}})"

    with Check("constant"):
        expression = "1"
        execute_query(
            f"SELECT {func.format(params=f'1, {expression}')}, any(toTypeName(1)), any(toTypeName({expression}))"
        )

    with Check("zero rows"):
        expression = "number % 3"
        execute_query(
            f"SELECT {func.format(params=f'number, {expression}')}, any(toTypeName(number)), any(toTypeName({expression})) FROM numbers(0)"
        )

    with Check("with group by"):
        expression = "number % 2"
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params=f'number, {expression}')}, any(toTypeName(number)), any(toTypeName({expression})) FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        expression = "number % 3"
        execute_query(
            f"SELECT {func.format(params=f'number-5, {expression}')}, any(toTypeName(number)), any(toTypeName({expression})) FROM numbers(1, 10)"
        )

    with Check("first non-NULL value"):
        expression = "x % 2"
        execute_query(
            f"SELECT {func.format(params=f'x, {expression}')}, any(toTypeName(x)), any(toTypeName({expression}))  FROM values('x Nullable(Int8)', NULL, NULL, NULL, 3, 4, 5)"
        )

    with Check("NULL for all rows"):
        expression = "number % 2"
        execute_query(
            f"SELECT {func.format(params=f'distinct if(number % 2, NULL, NULL), {expression}')}, any(toTypeName(NULL)), any(toTypeName({expression})) FROM numbers(10)"
        )

    with Check("return type"):
        expression = "number % 2"
        execute_query(
            f"SELECT toTypeName({func.format(params=f'number, {expression}')}), any(toTypeName(number)), any(toTypeName({expression})) FROM numbers(1, 10)"
        )

    with Check("with another aggregate function"):
        expression = "toString(x)"
        execute_query(
            f"SELECT {func.format(params=f'x, {expression}')}, max(y), any(toTypeName(x)), any(toTypeName({expression})) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'there'), (NULL, NULL), (5, 'you'))"
        )

    with Check("with another aggregate function and group by"):
        expression = "x"
        execute_query(
            f"SELECT {func.format(params=f'x, {expression}')}, max(y), any(toTypeName(x)), any(toTypeName({expression})) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'hello'), (NULL, NULL), (5, 'you')) GROUP BY y"
        )

    for v in ["inf", "-inf", "nan"]:
        expression = "(x - 1) * 100"
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params=f'x, {expression}')}, any(toTypeName(x)), any(toTypeName({expression})) FROM values('x Float64', ({v}))"
            )

    for column in table.columns:
        column_name, column_type = column.name, column.datatype.name

        if not is_numeric(column.datatype, decimal=decimal):
            continue

        expression = f"{column.name} % 2"
        with Check(f"{column.datatype.name}"):
            execute_query(
                f"SELECT {func.format(params=f'{column.name}, {expression}')}, any(toTypeName({column.name})), any(toTypeName({expression})) FROM {table.name}"
            )


@TestFeature
@Name("argMin_combinator")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_ArgMin("1.0"))
def feature(self, table=None, snapshot_id=None):
    for func in aggregate_functions:
        Scenario(name="argMin_combinator", test=scenario)(func=func)
