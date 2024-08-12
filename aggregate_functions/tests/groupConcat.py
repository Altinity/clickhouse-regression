from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupConcat,
)


@TestCheck
def datatype(self, func, table, col_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col_name)}, any(toTypeName({col_name})) FROM {table.name}"
    )


@TestCheck
@Flags(TE)
def sanity_check(self, col_name, table):
    """Check that groupConcat is the same as arrayStringConcat(groupArray(column))."""
    node = self.context.node
    query_1 = f"SELECT groupConcat({col_name}) FROM {table.name}"
    query_2 = f"SELECT arrayStringConcat(groupArray({col_name})) FROM {table.name}"
    # node.query(f"SELECT {col_name} FROM {table.name} FORMAT Values")
    assert node.query(query_1).output == node.query(query_2).output, error()


@TestScenario
@Name("groupConcat")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupConcat("1.0"))
def scenario(self, func="groupConcat({params})", table=None, snapshot_id=None):
    """Check groupConcat aggregate function."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, add_analyzer=True
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

    with Pool(5) as executor:
        for column in table.columns:
            Check(
                f"datatype {column.datatype.name}",
                test=datatype,
                parallel=True,
                executor=executor,
            )(func=func, table=table, col_name=column.name)
        join()

    if "State" not in self.name:
        with Pool(5) as executor:
            for column in table.columns:
                if "FixedString(51)" in column.datatype.name:
                    with Check(f"sanity check datatype {column.datatype.name}"):
                        skip("https://github.com/ClickHouse/ClickHouse/issues/67977")
                else:
                    Check(
                        f"sanity check datatype {column.datatype.name}",
                        test=sanity_check,
                        parallel=True,
                        executor=executor,
                    )(table=table, col_name=column.name)
            join()
