from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Any,
)


@TestScenario
@Name("any")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Any("1.0"))
def scenario(self, func="any({params})", table=None, snapshot_id=None):
    """Check any aggregate function."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=">=23.2"
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1')}, any(toTypeName(1))")

    with Check("zero rows"):
        execute_query(
            f"SELECT {func.format(params='number')}, any(toTypeName(number)) FROM numbers(0)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number')}, any(toTypeName(number)) FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='number-5')}, any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("first non-NULL value"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x))  FROM values('x Nullable(Int8)', NULL, NULL, NULL, 3, 4, 5)"
        )

    with Check("NULL for all rows"):
        execute_query(
            f"SELECT {func.format(params='distinct if(number % 2, NULL, NULL)')}, any(toTypeName(number)) FROM numbers(10)"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number')}), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("with another aggregate function"):
        execute_query(
            f"SELECT {func.format(params='x')}, max(y), any(toTypeName(x)) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'there'), (NULL, NULL), (5, 'you'))"
        )

    with Check("with another aggregate function and group by"):
        execute_query(
            f"SELECT {func.format(params='x')}, max(y), any(toTypeName(x)) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'hello'), (NULL, NULL), (5, 'you')) GROUP BY y"
        )

    with Check("string that ends with \\0"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x String', 'hello\0\0')"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x')}, any(toTypeName(x))  FROM values('x Float64', ({v}))"
            )

    for column in table.columns:
        with Check(f"{column.datatype.name}"):
            execute_query(
                f"SELECT {func.format(params=column.name)}, any(toTypeName({column.name})) FROM {table.name}"
            )
