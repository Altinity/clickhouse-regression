from testflows.core import *
from helpers.tables import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_WindowFunnel,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name, window):
    """Check different column types."""
    func_ = func.replace("({params})", f"({window})({{params}})")
    params = f"{col1_name},{col2_name}>100,{col2_name}>500,{col2_name}>1000,{col2_name}>10000,{col2_name}>100000"
    execute_query(
        f"SELECT {func_.format(params=params)} FROM {table.name} FORMAT JSONEachRow"
    )


@TestScenario
@Name("windowFunnel")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_WindowFunnel("1.0"))
def scenario(
    self,
    func="windowFunnel({params})",
    table=None,
    snapshot_id=None,
    decimal=True,
    datetime=True,
    date=True,
):
    """Check windowFunnel aggregate function by using the same checks as for avg."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if table is None:
        table = self.context.table

    func_ = func.replace("({params})", f"(6048000000000000)({{params}})")

    if "Merge" in self.name:
        return self.context.snapshot_id, func_.replace("({params})", "")

    with Check("constant"):
        params = "1,1,1"
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(1)), any(toTypeName(1)), any(toTypeName(1))"
        )

    with Check("zero rows"):
        params = "number, number=1, number=1"
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(number)), any(toTypeName(1)), any(toTypeName(1)) FROM numbers(0)"
        )

    with Check("single row"):
        params = "number, number=1, number=1"
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(number)), any(toTypeName(1)), any(toTypeName(1)) FROM numbers(1)"
        )

    with Check("with group by"):
        params = "number, number=1, number=1"
        execute_query(
            f"SELECT number % 2 AS even, {func_.format(params=params)}, any(toTypeName(number)), any(toTypeName(1)), any(toTypeName(1)) FROM numbers(10) GROUP BY even"
        )

    with Check("NULL value handling"):
        params = "time, number=NULL, number=2"
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(time)), any(toTypeName(1)), any(toTypeName(1)) FROM values ('time Date, number Nullable(UInt32)', (1,NULL), (2,NULL), (3,2))"
        )

    with Check("NULL value handling"):
        params = "time, number=NULL, number=2"
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(time)), any(toTypeName(1)), any(toTypeName(1)) FROM values ('time Date, number Nullable(UInt32)', (1,NULL), (2,NULL), (3,2))"
        )

    with Check("single NULL value"):
        params = "time, number=1, number=2"
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(time)), any(toTypeName(1)), any(toTypeName(1)) FROM values ('time Date, number Nullable(UInt32)', (1,1), (2,NULL), (3,2))"
        )

    with Check("return type"):
        params = "number, number=1, number=2"
        execute_query(
            f"SELECT toTypeName({func_.format(params=params)}), any(toTypeName(number)), any(toTypeName(1)), any(toTypeName(1)) FROM numbers(1, 10)"
        )

    with Check("example1"):
        params = "time, number=1, number=2"
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(time)), any(toTypeName(1)), any(toTypeName(1)) FROM values('time Date, number UInt32', (1,1), (2,3), (3,2))"
        )

    with Check("example2"):
        params = "time, number = 1, number = 2, number = 3"
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(time)), any(toTypeName(1)), any(toTypeName(1)), any(toTypeName(1)) FROM values('time Date, number UInt32', (1,1), (2,3), (3,2))"
        )

    with Check("example3"):
        params = "time, number = 1, number = 2, number = 4"
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(time)), any(toTypeName(1)), any(toTypeName(1)), any(toTypeName(1)) FROM values('time Date, number UInt32', (1,1), (2,3), (3,2))"
        )

    with Check("example4"):
        params = "time, number = 1, number = 2"
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(time)), any(toTypeName(1)), any(toTypeName(1)) FROM values('time Date, number UInt32', (1,1), (2,3), (3,2), (4,1), (5,3), (6,2))"
        )

    with Check("doc example"):
        params = (
            "timestamp, eventID = 1003, eventID = 1009, eventID = 1007, eventID = 1010"
        )
        execute_query(
            f"SELECT {func_.format(params=params)}, any(toTypeName(timestamp)), any(toTypeName(1)), any(toTypeName(1)), any(toTypeName(1)), any(toTypeName(1)) \
              FROM VALUES('event_date Date, user_id UInt32, timestamp DateTime, eventID UInt32, produnc String', ('2019-01-28',1,'2019-01-29 10:00:00',1003,'phone'), ('2019-01-31',1,'2019-01-31 09:00:00', 1007, 'phone'), ('2019-01-30', 1, '2019-01-30 08:00:00',1009, 'phone'), ('2019-02-01', 1, '2019-02-01 08:00:00', 1010, 'phone'))  \
              WHERE (event_date >= '2019-01-01') AND (event_date <= '2019-02-02') \
              GROUP BY user_id"
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
                    )
                    and not is_nullable(col.datatype)
                ]
                permutations = list(permutations_with_replacement(columns, 2))
                permutations.sort()

                for col1, col2 in permutations:
                    col1_name, col1_type = col1.name, col1.datatype.name
                    col2_name, col2_type = col2.name, col2.datatype.name
                    if (
                        isinstance(unwrap(col1.datatype), Date)
                        or isinstance(unwrap(col1.datatype), DateTime64)
                    ) and not (
                        isinstance(unwrap(col2.datatype), Date)
                        or isinstance(unwrap(col2.datatype), DateTime64)
                    ):
                        for w in [1, 10, 1000, 10000, 100000000]:
                            Check(
                                f"{col1_type},{col2_type}_{w}",
                                test=datatype,
                                parallel=True,
                                executor=executor,
                            )(
                                func=func,
                                table=table,
                                col1_name=col1_name,
                                col2_name=col2_name,
                                window=w,
                            )

                join()
