from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Sparkbar,
)

from helpers.datatypes import *
from helpers.tables import (
    is_numeric,
    is_unsigned_integer,
    is_low_cardinality,
    is_nullable,
)
from aggregate_functions.tests.steps import (
    get_snapshot_id,
    execute_query,
    permutations_with_replacement,
)


@TestScenario
@Name("sparkbar")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Sparkbar("1.0"))
def scenario(self, func="sparkbar({params})", table=None, snapshot_id=None):
    """Check sparkbar aggregate function by using the same tests as for quantileWeighted."""
    clickhouse_version = (
        ">=23.2" if check_clickhouse_version("<23.4")(self) else ">=23.4"
    )
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id, clickhouse_version=clickhouse_version)

    if table is None:
        table = self.context.table

    func = func.replace("({params})", f"(9)({{params}})")

    if 'Merge' in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1,2')}, any(toTypeName(1)), any(toTypeName(2))")

    with Check("zero rows"):
        execute_query(
            f"SELECT {func.format(params='toUInt64(number), toUInt64(number+1)')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(0)"
        )

    with Check("single row"):
        execute_query(
            f"SELECT {func.format(params='toUInt64(number),toUInt64(number)')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1)"
        )

    with Check("single row with zero weight"):
        execute_query(
            f"SELECT {func.format(params='toUInt64(number),toUInt64(number-1)')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='toUInt64(number), toUInt64(number)')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(10) GROUP BY even"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x,1')}, any(toTypeName(x)), any(toTypeName(1))  FROM values('x Nullable(UInt8)', 0, 1, NULL, 3, 4, 5)"
        )

    with Check("weight NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x,w')}, any(toTypeName(x)), any(toTypeName(w))  FROM values('x UInt8, w Nullable(UInt8)', (1,0), (1,1), (2,NULL), (3,3), (0,4), (1, 5))"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x,w')}, any(toTypeName(x)), any(toTypeName(w))  FROM values('x Nullable(UInt8), w Nullable(UInt8)', (NULL,NULL) )"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='toUInt8(number),toUInt64(number)')}), any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Scenario("datatypes"):
        with Scenario(
            "permutations",
            description="sanity check most common column type permutations",
        ):
            with Pool(3) as executor:
                columns = [
                    col
                    for col in table.columns
                    if is_unsigned_integer(
                        col.datatype,
                        decimal=False,
                        date=True,
                        datetime=True,
                        extended_precision=False,
                    )
                ]

                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.name, col1.datatype.name
                    col2_name, col2_type = col2.name, col2.datatype.name

                    if not is_unsigned_integer(col2.datatype):
                        continue

                    if is_nullable(col1.datatype):
                        continue

                    if is_low_cardinality(col1.datatype):
                        continue

                    with Check(f"{col1_name},{col2_name}"):
                        if isinstance(
                            unwrap(col1.datatype),
                            (UInt16, UInt32, UInt64, UInt128, UInt256),
                        ):
                            xfail(
                                reason="https://github.com/ClickHouse/ClickHouse/issues/44467"
                            )

                        params = f"{col1_name},{col2_name}"
                        self.context.node.query(
                            f"SELECT {params} FROM {table.name} FORMAT CSV"
                        )
                        execute_query(
                            f"SELECT {func.format(params=params)}, any(toTypeName({col1_name})), any(toTypeName({col2_name})) FROM {table.name}"
                        )
