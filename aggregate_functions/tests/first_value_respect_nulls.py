from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_FirstValueRespectNulls,
)
from helpers.tables import common_columns
from helpers.tables import is_map, is_array

from aggregate_functions.tests.steps import *


@TestCheck
def datatype(self, func, table, col1_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name)}, any(toTypeName({col1_name})) FROM {table.name} FORMAT JSONEachRow"
    )


@TestScenario
@Name("first_value_respect_nulls")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_FirstValueRespectNulls("1.0")
)
def scenario(
    self,
    func="first_value_respect_nulls({params})",
    table=None,
    snapshot_id=None,
    decimal=True,
    extended_precision=True,
):
    """Check first_value_respect_nulls aggregate function."""

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=">=23.11"
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

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='number-5')}, any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("first non-NULL value"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x))  FROM values('x Nullable(Int8)', NULL, NULL, NULL, 3, 4, 5)"
        )

    with Check("NULL for all rows"):
        execute_query(
            f"SELECT {func.format(params='distinct if(number % 2, NULL, NULL)')}, any(toTypeName(NULL)) FROM numbers(10)"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number')}), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("with another aggregate function"):
        execute_query(
            f"SELECT {func.format(params='x')}, max(y), any(toTypeName(x)) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'there'), (NULL, NULL), (5, 'you'))"
        )

    with Check("with another aggregate function and group by"):
        execute_query(
            f"SELECT {func.format(params='x')}, max(y), any(toTypeName(x)) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'hello'), (NULL, NULL), (5, 'you')) GROUP BY y"
        )

    with Check("string that ends with \\0"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x String', 'hello\0\0')"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x')}, any(toTypeName(x))  FROM values('x Float64', ({v}))"
            )

    with Check("datatypes"):
        with Pool(3) as executor:
            columns = [
                col
                for col in table.columns
                if col in common_columns()
                and not is_map(col.datatype)
                and not is_array(col.datatype)
            ]

            for col1 in columns:
                col1_name, col1_type = col1.name, col1.datatype.name
                Check(
                    f"{col1_type}",
                    test=datatype,
                    parallel=True,
                    executor=executor,
                )(func=func, table=table, col1_name=col1_name)

            join()
