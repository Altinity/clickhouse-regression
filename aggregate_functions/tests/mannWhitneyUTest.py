from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MannWhitneyUTest,
)

from helpers.tables import is_numeric, is_unsigned_integer
from helpers.common import check_clickhouse_version

from aggregate_functions.tests.steps import (
    get_snapshot_id,
    execute_query,
    permutations_with_replacement,
)


@TestFeature
@Name("mannWhitneyUTest")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MannWhitneyUTest("1.0"))
def feature(self, func="mannWhitneyUTest({params})", table=None, snapshot_id=None):
    """Check mannWhitneyUTest aggregate function by using the same tests as for welchTTest."""
    clickhouse_version = (
        ">=22.6" if check_clickhouse_version("<23.2")(self) else ">=23.2"
    )
    self.context.snapshot_id = get_snapshot_id(clickhouse_version=clickhouse_version)

    if table is None:
        table = self.context.table

    func = func.replace("({params})", f"('greater')({{params}})")

    exitcode = 36 if "State" not in func else 0
    message = "Exception:" if "State" not in func else None

    with Check("constant"):
        execute_query(
            f"SELECT {func.format(params='1,2')}", exitcode=exitcode, message=message
        )

    with Check("zero rows"):
        execute_query(
            f"SELECT {func.format(params='number, toUInt64(number+1)')} FROM numbers(0)",
            exitcode=exitcode,
            message=message,
        )

    with Check("single row"):
        execute_query(
            f"SELECT {func.format(params='number,toUInt64(number)')} FROM numbers(1)",
            exitcode=exitcode,
            message=message,
        )

    with Check("single row with zero weight"):
        execute_query(
            f"SELECT {func.format(params='number,toUInt64(number-1)')} FROM numbers(1)",
            exitcode=exitcode,
            message=message,
        )

    with Check("with group by"):
        execute_query(
            f"SELECT {func.format(params='number, number % 2')} FROM numbers(100) GROUP BY number % 5"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='number-5, number % 2')} FROM numbers(1, 10)"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x,x % 2')}  FROM values('x Nullable(Int8)', 0, 1, NULL, 3, 4, 5)"
        )

    with Check("weight NULL value handling"):
        if check_clickhouse_version("<23.2")(self):
            execute_query(
                f"SELECT {func.format(params='x,w')}  FROM values('x Int8, w Nullable(UInt8)', (1,0), (1,1), (2,NULL), (3,3), (0,4), (1, 5))"
            )
        else:
            execute_query(
                f"SELECT {func.format(params='x,w')}  FROM values('x Int8, w Nullable(UInt8)', (10,0), (11,0), (12,NULL), (1,1), (2,1), (3,1))"
            )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x,w')}  FROM values('x Nullable(Int8), w Nullable(UInt8)', (NULL,NULL) )",
            exitcode=exitcode,
            message=message,
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number,toUInt64(number) % 2')}) FROM numbers(1, 100)"
        )

    with Check("doc example"):
        execute_query(
            f"SELECT {func.format(params='sample_data,sample_index')} FROM values('sample_data Int8, sample_index Int8', (10,0), (11,0), (12,0), (1,1), (2,1), (3,1))"
        )

    with Check("single value in 0 population"):
        execute_query(
            f"SELECT {func.format(params='sample_data,sample_index')} FROM values('sample_data Int8, sample_index Int8', (10,0), (11,1), (12,1), (1,1), (2,1), (3,1))"
        )

    with Check("single value in 1 population"):
        execute_query(
            f"SELECT {func.format(params='sample_data,sample_index')} FROM values('sample_data Int8, sample_index Int8', (10,1), (11,0), (12,0), (1,0), (2,0), (3,0))"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x,y')}  FROM values('x Float64, y Int8', (0,0), (2.3,1), ({v},0), (6.7,1), (4,0), (5,0))"
            )
    with Check(f"inf, -inf, nan"):
        execute_query(
            f"SELECT {func.format(params='x,y')}  FROM values('x Float64, y Int8', (nan,0), (2.3,1), (inf,1), (6.7,0), (-inf,0), (5,1))"
        )

    with Feature("datatypes"):
        with Feature(
            "permutations",
            description="sanity check most common column type permutations",
        ):
            with Pool(3) as executor:
                columns = [
                    col
                    for col in table.columns
                    if is_numeric(col.datatype, decimal=True)
                ]

                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.name, col1.datatype.name
                    col2_name, col2_type = col2.name, col2.datatype.name

                    if not is_unsigned_integer(col2.datatype):
                        continue

                    with Check(f"{col1_name},{col2_name}"):
                        params = f"{col1_name},{col2_name}"
                        execute_query(
                            f"SELECT {func.format(params=params)} FROM {table.name}"
                        )
