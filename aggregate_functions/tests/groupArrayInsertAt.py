from testflows.core import *
from aggregate_functions.tests.steps import *

from helpers.tables import common_columns, is_unsigned_integer
from helpers.cluster import QueryRuntimeException

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayInsertAt,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name+','+col2_name + '% 16')} FROM {table.name} FORMAT JSONEachRow"
    )


@TestFeature
@Name("groupArrayInsertAt")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayInsertAt("1.0")
)
def feature(self, func="groupArrayInsertAt({params})", table=None):
    """Check topKWeighted aggregate function."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    params = "({params})"

    _func = func.replace(params, f"{params}")

    with Check("constant"):
        execute_query(f"SELECT {_func.format(params='1,1')}")

    with Check("zero rows"):
        execute_query(f"SELECT {_func.format(params='number,number')} FROM numbers(0)")

    with Check("single row"):
        execute_query(
            f"SELECT {_func.format(params='number,number+1')} FROM numbers(1)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {_func.format(params='number,even')} FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {_func.format(params='number-5,number+10')} FROM numbers(1, 10)"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {_func.format(params='x,y')}  FROM values('x Nullable(Int8), y UInt8', (0, 1), (1, 1), (NULL,2), (NULL,3), (4,4), (5, 1))"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {_func.format(params='x,y')}  FROM values('x Nullable(Int8), y UInt8', (NULL, 2))"
        )

    for x in ["inf", "-inf", "nan"]:
        with Check(f"{x}"):
            execute_query(
                f"SELECT {_func.format(params='x,y')}  FROM values('x Float64, y UInt64', (0, 1), (1, 2), ({x},3), (6.7,3), (4,4), (5, 1))"
            )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({_func.format(params='number, number+1')}) FROM numbers(1, 10)"
        )

    with Check("example"):
        execute_query(
            f"SELECT {_func.format(params='y,x')} FROM values('x UInt8, y Float64', (0,0.1), (1,0.34), (2,.88), (3,-1.23), (4,-3.3), (5,5.4))"
        )

    with Feature("datatypes"):
        with Feature(
            "permutations",
            description="sanity check most common column type permutations",
        ):
            with Pool(3) as executor:
                columns = [col for col in table.columns if col in common_columns()]
                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.name, col1.datatype.name
                    col2_name, col2_type = col2.name, col2.datatype.name

                    if not is_unsigned_integer(col2.datatype):
                        continue

                    Check(
                        f"{col1_type},{col2_type}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, col1_name=col1_name, col2_name=col2_name)

                join()
