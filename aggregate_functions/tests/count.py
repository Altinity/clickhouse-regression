from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count,
)


@TestCheck
def expr(self, func="count({params})"):
    """Check that count(expr) counts how many times expr
    returned not NULL and returned type is UInt64.
    """
    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1')}, any(toTypeName(1))")

    with Check("NULL for some rows"):
        execute_query(
            f"SELECT {func.format(params='if(number % 2, NULL, 1)')}, any(toTypeName(1)) FROM numbers(10)"
        )

    with Check("NULL for all rows"):
        execute_query(
            f"SELECT {func.format(params='if(number % 2, NULL, NULL)')}, any(toTypeName(number)) FROM numbers(10)"
        )

    with Check("Nullable type"):
        execute_query(
            f"SELECT {func.format(params='toNullable(if(number % 2, NULL, 1))')}, any(toTypeName(1)) AS count, toTypeName(count) FROM numbers(1)"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='1')}), any(toTypeName(1))"
        )


@TestCheck
def distinct_expr(self, func="count({params})"):
    """Check that COUNT(DISTINCT expr) by default
    is equivalent to uniqExact(expr) and returned type is UInt64.
    """
    with Check("constant"):
        execute_query(f"SELECT {func.format(params='distinct 1')}, any(toTypeName(1))")

    with Check("NULL for some rows"):
        execute_query(
            f"SELECT {func.format(params='distinct if(number % 2, NULL, 1)')}, any(toTypeName(1)) FROM numbers(10)"
        )

    with Check("NULL for all rows"):
        execute_query(
            f"SELECT {func.format(params='distinct if(number % 2, NULL, NULL)')}, any(toTypeName(number)) FROM numbers(10)"
        )

    with Check("Nullable type"):
        execute_query(
            f"SELECT {func.format(params='distinct toNullable(if(number % 2, NULL, 1))')}, any(toTypeName(number)) AS count, toTypeName(count) FROM numbers(1)"
        )

    with Check("returned type is UInt64"):
        execute_query(
            f"SELECT toTypeName({func.format(params='distinct 1')}), any(toTypeName(1))"
        )

    with Check("default function"):
        execute_query(
            f"SELECT {func.format(params='distinct 1')}, any(toTypeName(number)) FROM numbers(10) FORMAT JSONEachRow"
        )


@TestCheck
def zero_parameters(self, func="count({params})"):
    """Check that count() and COUNT(*) counts number of rows."""
    for f in [f"{func.format(params='')}", f"{func.format(params='*')}"]:
        with Check(f"{f}"):
            with Check("zero rows"):
                execute_query(f"SELECT {f}, any(toTypeName(number)) FROM numbers(0)")

            with Check("one row"):
                execute_query(f"SELECT {f}")

            with Check("more than one row"):
                execute_query(f"SELECT {f}, any(toTypeName(number)) FROM numbers(10)")

            with Check("rows with Nullable"):
                execute_query(
                    f"SELECT {f}, any(toTypeName(x)) FROM (SELECT toNullable(number) as x FROM numbers(10))"
                )


@TestScenario
@Name("count")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count("1.0"))
def scenario(self, func="count({params})", table=None, snapshot_id=None):
    """Check count aggregate function."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id, clickhouse_version=">=23.2")

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    for check in loads(current_module(), Check):
        Check(test=check)(func=func)
