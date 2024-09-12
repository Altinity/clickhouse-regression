from helpers.tables import common_columns, is_string

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMin,
)


@TestCheck
def execute_multi_query(self, query):
    """Execute multi query statement."""
    execute_query("".join(query), use_file=True, format=None, hash_output=False)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name+','+col2_name)}, any(toTypeName({col1_name})), any(toTypeName({col2_name})) FROM {table.name}",
        use_result_in_snapshot_name=True,
    )


@TestScenario
@Name("argMin")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMin("1.0"))
def scenario(
    self, func="argMin({params})", table=None, snapshot_id=None, extra_data=None
):
    """Check argMin or argMax or one of their combinator aggregate functions. By default: argMin."""
    # https://github.com/ClickHouse/ClickHouse/pull/58139
    if check_clickhouse_version(">=24.8")(self):
        clickhouse_version = (
            ">=24.8"  # https://github.com/ClickHouse/ClickHouse/issues/69518
        )
    elif check_clickhouse_version(">=23.12")(self):
        clickhouse_version = ">=23.12"
    else:
        clickhouse_version = ">=23.2"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id,
        clickhouse_version=clickhouse_version,
        add_analyzer=True,
        extra_data=extra_data,
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(
            f"SELECT {func.format(params='1,2')}, any(toTypeName(1)), any(toTypeName(2))"
        )

    with Check("zero rows"):
        execute_query(
            f"SELECT {func.format(params='number, number+1')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(0)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number, even')}, any(toTypeName(number)), any(toTypeName(even)) FROM numbers(10) GROUP BY even"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x, y')}, any(toTypeName(x)), any(toTypeName(y)) FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'there'), (NULL, NULL), (5, 'you'))"
        )

    with Check("doc example"):
        execute_query(
            f"SELECT {func.format(params='user, salary')}, any(toTypeName(user)), any(toTypeName(salary)) FROM values('user String, salary Float64',('director',5000),('manager',3000),('worker', 1000))"
        )

    with Check("inf, -inf, nan"):
        for permutation in permutations_with_replacement(["inf", "-inf", "nan"], 2):
            x, y = permutation
            with Check(f"{x},{y}"):
                execute_query(
                    f"SELECT {func.format(params='x,y')}, any(toTypeName(x)), any(toTypeName(y))  FROM values('x Float64, y Float64', (0, 1), (1, 2.3), ({x},{y}), (6.7,3), (4,4), (5, 1))"
                )

    with Check("string that ends with \\0"):
        execute_query(
            f"SELECT {func.format(params='x, y')}, any(toTypeName(x)), any(toTypeName(y)) FROM values('x String, y String', ('1', 'hello\0\0'), ('hello\0\0', 'hello'), ('3', 'there'), ('hello\0\0', 'there\0\0'), ('5', 'you'))",
            use_result_in_snapshot_name=True,
        )

    with Check("user example"):
        use_result_in_snapshot_name = False
        # different representation of state
        if check_clickhouse_version(">=23.12")(self) and "argMaxState" in self.name:
            use_result_in_snapshot_name = True

        execute_query(
            f"""
            SELECT {func.format(params='value, toNullable(time)')}, any(toTypeName(value)), any(toTypeName(toNullable(time)))
            FROM VALUES ('uuid LowCardinality(String), time Nullable(DateTime64(3)), value Float64',
            ('a1000000-0000-0000-0000-0000000000a1','2021-01-01 00:00:00.000',0),
            ('a1000000-0000-0000-0000-0000000000a1','2021-01-01 00:00:39.000',-1),
            ('a1000000-0000-0000-0000-0000000000a1','2021-01-01 00:00:59.000',-1),
            ('a1000000-0000-0000-0000-0000000000a1','2021-01-01 00:01:00.000',0))
            """,
            use_result_in_snapshot_name=use_result_in_snapshot_name,
        )

    with Feature("datatypes"):
        with Pool(6) as executor:
            for column in table.columns:
                col_name, col_type = column.name, column.datatype.name
                Check(
                    f"String,{col_type}",
                    test=datatype,
                    parallel=True,
                    executor=executor,
                )(func=func, table=table, col1_name="string", col2_name=col_name)
                Check(
                    f"{col_type},String",
                    test=datatype,
                    parallel=True,
                    executor=executor,
                )(func=func, table=table, col1_name=col_name, col2_name="string")

            join()

        with Feature(
            "permutations",
            description="sanity check most common column type permutations",
        ):
            with Pool(6) as executor:
                columns = [col for col in table.columns if col in common_columns()]
                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()

                for col1, col2 in permutations:
                    # we already cover String data type above so skip it here
                    if is_string(col1.datatype) or is_string(col2.datatype):
                        continue
                    Check(
                        f"{col1.datatype.name},{col2.datatype.name}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, col1_name=col1.name, col2_name=col2.name)

                join()
