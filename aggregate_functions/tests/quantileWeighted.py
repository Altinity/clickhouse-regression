from helpers.tables import is_numeric, is_unsigned_integer

from aggregate_functions.tests.steps import *


@TestScenario
@Name("quantileWeighted")
def scenario(
    self,
    func="avg({params})",
    table=None,
    decimal=True,
    date=True,
    datetime=True,
    extended_precision=False,
    snapshot_id=None,
):
    """Checks for quantile Weighted aggregate functions."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=">=23.2"
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
            f"SELECT {func.format(params='number, toUInt64(number+1)')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(0)"
        )

    with Check("single row"):
        execute_query(
            f"SELECT {func.format(params='number,toUInt64(number)')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1)"
        )

    with Check("single row with zero weight"):
        execute_query(
            f"SELECT {func.format(params='number,toUInt64(number-1)')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number, toUInt64(number)')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(10) GROUP BY even"
        )

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='number-5, toUInt64(number)')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x,1')}, any(toTypeName(x)), any(toTypeName(1)) FROM values('x Nullable(Int8)', 0, 1, NULL, 3, 4, 5)"
        )

    with Check("weight NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x,w')}, any(toTypeName(x)), any(toTypeName(w)) FROM values('x Int8, w Nullable(UInt8)', (1,0), (1,1), (2,NULL), (3,3), (0,4), (1, 5))"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x,w')}, any(toTypeName(x)), any(toTypeName(w)) FROM values('x Nullable(Int8), w Nullable(UInt8)', (NULL,NULL) )"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number,toUInt64(number)')}), any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("doc example"):
        execute_query(
            f"SELECT {func.format(params='x,1')}, any(toTypeName(x)), any(toTypeName(1)) FROM values('x Int8', 0, 1, 2, 3, 4, 5)"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x,1')}, any(toTypeName(x)), any(toTypeName(1)) FROM values('x Float64', (0), (2.3), ({v}), (6.7), (4), (5))"
            )
    with Check(f"inf, -inf, nan"):
        execute_query(
            f"SELECT {func.format(params='x,1')}, any(toTypeName(x)), any(toTypeName(1)) FROM values('x Float64', (nan), (2.3), (inf), (6.7), (-inf), (5))"
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
                    if is_numeric(
                        col.datatype,
                        decimal=decimal,
                        date=date,
                        datetime=datetime,
                        extended_precision=extended_precision,
                    )
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
                            f"SELECT {func.format(params=params)}, any(toTypeName({col1_name})), any(toTypeName({col2_name})) FROM {table.name}"
                        )
