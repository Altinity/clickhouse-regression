from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_CorrMatrix,
)

from helpers.tables import *


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name+','+col2_name)}, any(toTypeName({col1_name})), any(toTypeName({col2_name})) FROM {table.name} FORMAT JSONEachRow"
    )


@TestScenario
@Name("corrMatrix")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_CorrMatrix("1.0"))
def scenario(
    self,
    func="corrMatrix({params})",
    table=None,
    snapshot_id=None,
    extended_precision=False,
    decimal=True,
):
    """Check corrMatrix aggregate function."""
    clickhouse_version = None
    if check_current_cpu("aarch64")(self):
        clickhouse_version = ">=24.3"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id,
        clickhouse_version=clickhouse_version,
        add_analyzer=True,
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
            f"SELECT {func.format(params='distinct if(number % 2, NULL, NULL)')}, any(toTypeName(number)) FROM numbers(10)"
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

    with Check("example1"):
        execute_query(
            f"SELECT {func.format(params='a_value, b_value')}, any(toTypeName(a_value)), any(toTypeName(b_value)) FROM VALUES('a_value UInt32, b_value Float64, c_value Float64, d_value Float64', (1, 5.6,-4.4, 2.6),(2, -9.6, 3, 3.3),(3, -1.3,-4, 1.2),(4, 5.3,9.7,2.3),(5, 4.4,0.037,1.222),(6, -8.6,-7.8,2.1233),(7, 5.1,9.3,8.1222),(8, 7.9,-3.6,9.837),(9, -8.2,0.62,8.43555),(10, -3,7.3,6.762))"
        )

    with Check("example2"):
        execute_query(
            f"SELECT {func.format(params='a_value, b_value, c_value')}, any(toTypeName(a_value)), any(toTypeName(b_value)), any(toTypeName(c_value)) FROM VALUES('a_value UInt32, b_value Float64, c_value Float64, d_value Float64', (1, 5.6,-4.4, 2.6),(2, -9.6, 3, 3.3),(3, -1.3,-4, 1.2),(4, 5.3,9.7,2.3),(5, 4.4,0.037,1.222),(6, -8.6,-7.8,2.1233),(7, 5.1,9.3,8.1222),(8, 7.9,-3.6,9.837),(9, -8.2,0.62,8.43555),(10, -3,7.3,6.762))"
        )

    with Check("example3"):
        execute_query(
            f"SELECT {func.format(params='a_value, b_value, c_value, d_value')}, any(toTypeName(a_value)), any(toTypeName(b_value)), any(toTypeName(c_value)), any(toTypeName(d_value)) FROM VALUES('a_value UInt32, b_value Float64, c_value Float64, d_value Float64', (1, 5.6,-4.4, 2.6),(2, -9.6, 3, 3.3),(3, -1.3,-4, 1.2),(4, 5.3,9.7,2.3),(5, 4.4,0.037,1.222),(6, -8.6,-7.8,2.1233),(7, 5.1,9.3,8.1222),(8, 7.9,-3.6,9.837),(9, -8.2,0.62,8.43555),(10, -3,7.3,6.762))"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x')}, any(toTypeName(x))  FROM values('x Float64', ({v}))"
            )

    with Check("datatypes"):
        with Check(
            "permutations",
            description="sanity check most common column type permutations",
        ):
            with Pool(3) as executor:
                columns = [
                    col
                    for col in table.columns
                    if col in generate_all_column_types()
                    and is_numeric(
                        col.datatype,
                        decimal=decimal,
                        extended_precision=extended_precision,
                    )
                    and not is_low_cardinality(col.datatype)
                ]
                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.name, col1.datatype.name
                    col2_name, col2_type = col2.name, col2.datatype.name
                    Check(
                        f"{col1_type},{col2_type}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, col1_name=col1_name, col2_name=col2_name)

                join()
