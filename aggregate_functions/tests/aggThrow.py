from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_AggThrow,
)

import rbac.helper.errors as errors


@TestScenario
@Name("aggThrow")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_AggThrow("1.0")
)
def scenario(
    self,
    func="aggThrow({params})",
    table=None,
):
    """Check aggThrow aggregate function."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table
    
    exitcode, message = errors.aggregate_function_throw()
    
    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1')}", exitcode=exitcode, message=message)

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='number')} FROM numbers(0)", exitcode=exitcode, message=message)

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number')} FROM numbers(10) GROUP BY even",
            exitcode=exitcode, 
            message=message
        )

    with Check("some negative values"):
        execute_query(f"SELECT {func.format(params='number-5')} FROM numbers(1, 10)", exitcode=exitcode, message=message)

    with Check("first non-NULL value"):
        execute_query(
            f"SELECT {func.format(params='x')}  FROM values('x Nullable(Int8)', NULL, NULL, NULL, 3, 4, 5)",
            exitcode=exitcode, 
            message=message
        )

    with Check("NULL for all rows"):
        execute_query(
            f"SELECT {func.format(params='distinct if(number % 2, NULL, NULL)')} FROM numbers(10)"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number')}) FROM numbers(1, 10)",
            exitcode=exitcode, 
            message=message
        )

    with Check("with another aggregate function"):
        execute_query(
            f"SELECT {func.format(params='x')}, max(y) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'there'), (NULL, NULL), (5, 'you'))",
            exitcode=exitcode, 
            message=message
        )

    with Check("with another aggregate function and group by"):
        execute_query(
            f"SELECT {func.format(params='x')}, max(y) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'hello'), (NULL, NULL), (5, 'you')) GROUP BY y",
            exitcode=exitcode, 
            message=message
        )

    with Check("string that ends with \\0"):
        execute_query(
            f"SELECT {func.format(params='x')} FROM values('x String', 'hello\0\0')",
            exitcode=exitcode, 
            message=message
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x')}  FROM values('x Float64', ({v}))",
            exitcode=exitcode, 
            message=message
            )

    for column in table.columns:
        with Check(f"{column.datatype.name}"):
            execute_query(
            f"SELECT {func.format(params=column.name)} FROM {table.name}",
            exitcode=exitcode, 
            message=message
            )

    