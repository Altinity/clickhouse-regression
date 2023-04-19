from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count,
)


@TestScenario
def expr(self, func="count({params})"):
    """Check that count(expr) counts how many times expr
    returned not NULL and returned type is UInt64.
    """
    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1')}")

    with Check("NULL for some rows"):
        execute_query(
            f"SELECT {func.format(params='if(number % 2, NULL, 1)')} FROM numbers(10)"
        )

    with Check("NULL for all rows"):
        execute_query(
            f"SELECT {func.format(params='if(number % 2, NULL, NULL)')} FROM numbers(10)"
        )

    with Check("Nullable type"):
        execute_query(
            f"SELECT {func.format(params='toNullable(if(number % 2, NULL, 1))')} AS count, toTypeName(count) FROM numbers(1)"
        )

    with Check("return type"):
        execute_query(f"SELECT toTypeName({func.format(params='1')})")


@TestScenario
def distinct_expr(self, func="count({params})"):
    """Check that COUNT(DISTINCT expr) by default
    is equivalent to uniqExact(expr) and returned type is UInt64.
    """
    with Check("constant"):
        execute_query(f"SELECT {func.format(params='distinct 1')}")

    with Check("NULL for some rows"):
        execute_query(
            f"SELECT {func.format(params='distinct if(number % 2, NULL, 1)')} FROM numbers(10)"
        )

    with Check("NULL for all rows"):
        execute_query(
            f"SELECT {func.format(params='distinct if(number % 2, NULL, NULL)')} FROM numbers(10)"
        )

    with Check("Nullable type"):
        execute_query(
            f"SELECT {func.format(params='distinct toNullable(if(number % 2, NULL, 1))')} AS count, toTypeName(count) FROM numbers(1)"
        )

    with Check("returned type is UInt64"):
        execute_query(f"SELECT toTypeName({func.format(params='distinct 1')})")

    with Check("default function"):
        execute_query(
            f"SELECT {func.format(params='distinct 1')} FROM numbers(10) FORMAT JSONEachRow"
        )


@TestScenario
def zero_parameters(self, func="count({params})"):
    """Check that count() and COUNT(*) counts number of rows."""
    for f in [f"{func.format(params='')}", f"{func.format(params='*')}"]:
        with Check(f"{f}"):
            with Check("zero rows"):
                execute_query(f"SELECT {f} FROM numbers(0)")

            with Check("one row"):
                execute_query(f"SELECT {f}")

            with Check("more than one row"):
                execute_query(f"SELECT {f} FROM numbers(10)")

            with Check("rows with Nullable"):
                execute_query(
                    f"SELECT {f} FROM (SELECT toNullable(number) FROM numbers(10))"
                )


@TestFeature
@Name("count")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_Count("1.0"))
def feature(self, func="count({params})", table=None):
    """Check count aggregate function."""
    self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=23.2")

    for scenario in loads(current_module(), Scenario):
        scenario(func=func)
