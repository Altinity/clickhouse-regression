from helpers.tables import *
from helpers.datatypes import Float64

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_sequenceMatchEvents,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
    params = f"{col1_name},{col2_name}>100,{col2_name}>1000"
    execute_query(
        f"SELECT {func_.format(params=params)} FROM {table.name} FORMAT JSONEachRow"
    )


@TestScenario
@Name("sequenceMatchEvents")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_sequenceMatchEvents("1.0")
)
def scenario(
    self,
    func="sequenceMatchEvents({params})",
    table=None,
    decimal=True,
    snapshot_id=None,
    date=True,
    datetime=True,
):
    """Check sequenceMatchEvents parametric aggregate function"""

    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        _func = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        return self.context.snapshot_id, _func.replace("({params})", "")

    if table is None:
        table = self.context.table

    with Check("constant"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "1,1,1"
        execute_query(f"SELECT {func_.format(params=params)}")

    with Check("zero rows"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "number, number=1, number=1"
        execute_query(f"SELECT {func_.format(params=params)} FROM numbers(0)")

    with Check("single row"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "number, number=1, number=1"
        execute_query(f"SELECT {func_.format(params=params)} FROM numbers(1)")

    with Check("with group by"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "number, number=1, number=1"
        execute_query(
            f"SELECT number % 2 AS even, {func_.format(params=params)} FROM numbers(10) GROUP BY even"
        )

    with Check("NULL value handling"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "time, number=NULL, number=2"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM values ('time Date, number Nullable(UInt32)', (1,NULL), (2,NULL), (3,2))"
        )

    with Check("NULL value handling"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "time, number=NULL, number=2"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM values ('time Date, number Nullable(UInt32)', (1,NULL), (2,NULL), (3,2))"
        )

    with Check("single NULL value"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "time, number=1, number=2"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM values ('time Date, number Nullable(UInt32)', (1,1), (2,NULL), (3,2))"
        )

    with Check("return type"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "number, number=1, number=2"
        execute_query(
            f"SELECT toTypeName({func_.format(params=params)}) FROM numbers(1, 10)"
        )

    with Check("example1"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "time, number=1, number=2"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM values('time Date, number UInt32', (1,1), (2,3), (3,2))"
        )

    with Check("example2"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "time, number = 1, number = 2, number = 3"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM values('time Date, number UInt32', (1,1), (2,3), (3,2))"
        )

    with Check("example3"):
        func_ = func.replace("({params})", f"('(?1)(?2)')({{params}})")
        params = "time, number = 1, number = 2, number = 4"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM values('time Date, number UInt32', (1,1), (2,3), (3,2))"
        )

    with Check("example4"):
        func_ = func.replace("({params})", f"('(?1).*(?2)')({{params}})")
        params = "time, number = 1, number = 2"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM values('time Date, number UInt32', (1,1), (2,3), (3,2), (4,1), (5,3), (6,2))"
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
                        Check(
                            f"{col1_type},{col2_type}",
                            test=datatype,
                            parallel=True,
                            executor=executor,
                        )(
                            func=func,
                            table=table,
                            col1_name=col1_name,
                            col2_name=col2_name,
                        )

                join()
