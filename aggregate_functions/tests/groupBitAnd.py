from testflows.core import *

from helpers.tables import is_unsigned_integer
from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitAnd,
)


@TestFeature
@Name("groupBitAnd")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitAnd("1.0"))
def feature(self, func="groupBitAnd({params})", table=None, extended_precision=False):
    """Check groupBitAnd aggregate function."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table
    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1')}")

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='number')} FROM numbers(0)")

    with Check("single row"):
        execute_query(f"SELECT {func.format(params='number')} FROM numbers(1)")

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number')} FROM numbers(10) GROUP BY even"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x')}  FROM values('x Nullable(UInt8)', 0, 1, NULL, 3, 4, 5)"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x')}  FROM values('x Nullable(UInt8)', NULL)"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number')}) FROM numbers(1, 10)"
        )

    with Check("doc example"):
        execute_query(
            f"SELECT {func.format(params='x')} FROM values('x UInt8', 0, 1, 2, 3, 4, 5)"
        )

    for column in table.columns:
        column_name, column_type = column.name, column.datatype.name

        if not is_unsigned_integer(
            column.datatype, extended_precision=extended_precision
        ):
            continue

        with Check(f"{column_type}"):
            execute_query(f"SELECT {func.format(params=column_name)} FROM {table.name}")
