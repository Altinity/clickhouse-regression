from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Max,
)


@TestCheck
def datatype(self, func, table, col_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col_name)}, any(toTypeName({col_name})) FROM {table.name}",
    )


@TestScenario
@Name("max")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Max("1.0"))
def scenario(self, func="max({params})", table=None, snapshot_id=None):
    """Check max aggregate function."""

    if check_clickhouse_version(">=24.1")(self):
        clickhouse_version = ">=24.1"
    elif check_clickhouse_version(">=23.12")(self):
        clickhouse_version = ">=23.12"
    else:
        clickhouse_version = ">=23.2"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
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

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x Nullable(Int8)', 0, 1, NULL, 3, 4, 5)"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x Float64', (0), (2.3), ({v}), (6.7), (4), (5))"
            )
    with Check(f"inf, -inf, nan"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x Float64', (nan), (2.3), (inf), (6.7), (-inf), (5))"
        )

    with Pool(6) as executor:
        for column in table.columns:
            column_name, column_type = column.name, column.datatype.name
            Check(
                f"{column_type}",
                test=datatype,
                parallel=True,
                executor=executor,
            )(func=func, table=table, col_name=column_name)
        join()
