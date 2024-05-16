from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArraySorted,
)


@TestScenario
@Name("groupArraySorted")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArraySorted("1.0"))
def scenario(self, func="groupArraySorted({params})", table=None, snapshot_id=None):
    """Check groupArraySorted aggregate function."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=">=23.2", add_analyzer=True
    )

    if table is None:
        table = self.context.table

    params = "({params})"
    _func = func.replace(params, f"(10){params}")

    if "Merge" in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    with Check("constant"):
        execute_query(f"SELECT {_func.format(params='1')}, any(toTypeName(1))")

    with Check("zero rows"):
        execute_query(
            f"SELECT {_func.format(params='number')}, any(toTypeName(number)) FROM numbers(0)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {_func.format(params='number')}, any(toTypeName(number)) FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {_func.format(params='number-5')}, any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("first non-NULL value"):
        execute_query(
            f"SELECT {_func.format(params='x')}, any(toTypeName(x))  FROM values('x Nullable(Int8)', NULL, NULL, NULL, 3, 4, 5)"
        )

    with Check("NULL for all rows"):
        execute_query(
            f"SELECT {_func.format(params='distinct if(number % 2, NULL, NULL)')}, any(toTypeName(NULL)) FROM numbers(10)"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({_func.format(params='number')}), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("with another aggregate function"):
        execute_query(
            f"SELECT {_func.format(params='x')}, max(y), any(toTypeName(x)) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'there'), (NULL, NULL), (5, 'you'))"
        )

    with Check("with another aggregate function and group by"):
        execute_query(
            f"SELECT {_func.format(params='x')}, max(y), any(toTypeName(x)) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'hello'), (NULL, NULL), (5, 'you')) GROUP BY y"
        )

    with Check("string that ends with \\0"):
        execute_query(
            f"SELECT {_func.format(params='x')}, any(toTypeName(x)) FROM values('x String', 'hello\0\0')"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {_func.format(params='x')}, any(toTypeName(x))  FROM values('x Float64', ({v}))"
            )

    for column in table.columns:
        with Check(f"{column.datatype.name}"):
            execute_query(
                f"SELECT {_func.format(params=column.name)}, any(toTypeName({column.name})) FROM {table.name}"
            )
