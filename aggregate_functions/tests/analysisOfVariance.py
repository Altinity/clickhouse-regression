
from helpers.tables import is_numeric, is_unsigned_integer, common_columns

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_AnalysisOfVariance,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col1_name+','+col2_name+'%2')}, any(toTypeName({col1_name})), any(toTypeName({col2_name})) FROM {table.name} FORMAT JSONEachRow"
    )


@TestScenario
@Name("analysisOfVariance")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_AnalysisOfVariance("1.0")
)
def scenario(
    self,
    func="analysisOfVariance({params})",
    table=None,
    snapshot_id=None,
    decimal=True,
    datetime=False,
    date=False,
    extended_precision=True,
):
    """Check analysisOfVariance(anova) aggregate function."""

    if check_clickhouse_version(">=24.3")(self) and check_current_cpu("aarch64")(self):
        clickhouse_version = ">=24.3"
    else:
        clickhouse_version = ">=24.1"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='number-10, number%2')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='a,b')}, any(toTypeName(a)), any(toTypeName(b)) FROM VALUES('a Nullable(Int16), b UInt16', (NULL,0), (NULL,0), (1, 0), (1,1), (3,1), (NULL,0), (2,2), (1,2))"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='a,b')}, any(toTypeName(a)), any(toTypeName(b)) FROM VALUES('a Nullable(Int16), b UInt16', (1,0), (3,0), (NULL, 0), (1,1), (3,1), (1,0), (2,2), (1,2))"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number,number%2')}), any(toTypeName(number)), any(toTypeName(number)) FROM numbers(1, 10)"
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='a,b')}, any(toTypeName(a)), any(toTypeName(b)) FROM VALUES('a Float64, b UInt16', (0, 0), (2.3, 0), ({v}, 1), (6.7, 1), (4, 2), (5, 2))"
            )

    with Check("five groups"):
        execute_query(
            f"SELECT {func.format(params='a,b')}, any(toTypeName(a)), any(toTypeName(b)) FROM VALUES('a Float64, b UInt16', (1.1,0), (2.5,0), (1, 0), (1,1), (3,1), (1,0), (2,2), (1,2), (1,3), (7.6,3), (2.4,3), (3,4), (5.5,4))"
        )

    with Check("corner values of Int16"):
        execute_query(
            f"SELECT {func.format(params='a,b')}, any(toTypeName(a)), any(toTypeName(b)) FROM VALUES ('a Int16, b UInt16', (32767,0), (2,0), (1, 0), (32767,1), (3,1))"
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
                    if col in common_columns()
                    and is_numeric(
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
                    if not is_unsigned_integer(col2.datatype):
                        continue

                    col1_name, col1_type = col1.name, col1.datatype.name
                    col2_name, col2_type = col2.name, col2.datatype.name

                    Check(
                        f"{col1_type},{col2_type}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, col1_name=col1_name, col2_name=col2_name)

                join()
