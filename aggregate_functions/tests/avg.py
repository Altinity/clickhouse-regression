from helpers.tables import is_numeric

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Avg,
)


@TestScenario
@Name("avg")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Avg("1.0"))
def scenario(
    self,
    func="avg({params})",
    table=None,
    decimal=True,
    date=False,
    datetime=False,
    extended_precision=False,
    snapshot_id=None,
):
    """Check avg aggregate function."""
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

    with Check("single row"):
        execute_query(
            f"SELECT {func.format(params='number')}, any(toTypeName(number)) FROM numbers(1)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number')}, any(toTypeName(number)) FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='number-5')}, any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x Nullable(Int8)', 0, 1, NULL, 3, 4, 5)"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x Nullable(Int8)', NULL)"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number')}), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("doc example"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x Int8', 0, 1, 2, 3, 4, 5)"
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

    for column in table.columns:
        column_name, column_type = column.name, column.datatype.name

        if not is_numeric(
            column.datatype,
            decimal=decimal,
            date=date,
            datetime=datetime,
            extended_precision=extended_precision,
        ):
            continue

        with Check(f"{column_type}"):
            execute_query(
                f"SELECT {func.format(params=column_name)}, any(toTypeName({column_name})) FROM {table.name}"
            )
