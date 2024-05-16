from testflows.core import *

from helpers.tables import common_columns
from helpers.tables import is_array


from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayIntersect,
)


@TestCheck
def datatype(self, func, table, col_name):
    """Check different column types."""
    execute_query(
        f"SELECT {func.format(params=col_name)}, any(toTypeName({col_name})) FROM {table.name}"
    )


@TestScenario
@Name("groupArrayIntersect")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayIntersect("1.0")
)
def scenario(
    self,
    func="groupArrayIntersect({params})",
    table=None,
    snapshot_id=None,
):
    """Check groupArrayIntersect aggregate function."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, add_analyzer=True
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='[1]')}, any(toTypeName([1]))")

    with Check("zero rows"):
        execute_query(
            f"SELECT {func.format(params='[number]')}, any(toTypeName([number])) FROM numbers(0)"
        )

    with Check("single row"):
        execute_query(
            f"SELECT {func.format(params='[number]')}, any(toTypeName([number])) FROM numbers(1)"
        )

    with Check("with group by 1"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='[number]')}, any(toTypeName([number])) FROM numbers(10) GROUP BY even"
        )

    with Check("with group by 2"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='[number]')}, any(toTypeName([number])) FROM numbers(2) GROUP BY even"
        )

    with Check("inf, -inf, nan"):
        for i in ["inf", "-inf", "nan"]:
            with Check(f"{i}"):
                execute_query(
                    f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x Array(Float64)', [0,1,0.3,1,{i}], [1,2.3,0,inf,nan], [0,1,2,3,3.5,inf,nan], [0,1,6.7,3, inf,nan])"
                )

    with Check("some negative values"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x Array(Float64)', [0,1,0.3,1,-1,-1000], [1,2.3,0,-1,-4], [0,1,2,3,3.5,-5,-1], [0,1,6.7,3, -1,-100])"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='x')}), any(toTypeName(x)) FROM values('x Array(Float64)', [0,1,0.3,1,-1,-1000], [1,2.3,0,-1,-4], [0,1,2,3,3.5,-5,-1], [0,1,6.7,3, -1,-100])"
        )

    with Check("example1"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x Array(Float64)',[1,2,4], [1,5,2,8,-1,0], [1,5,7,5,8,2])"
        )

    with Check("datatypes"):
        with Check(
            "datatypes",
            description="sanity check most common column type",
        ):
            with Pool(3) as executor:
                columns = [
                    col
                    for col in table.columns
                    if is_array(
                        col.datatype,
                    )
                ]

                for col in columns:
                    col_name, col_type = col.name, col.datatype.name
                    Check(
                        f"{col_type}",
                        test=datatype,
                        parallel=True,
                        executor=executor,
                    )(
                        func=func,
                        table=table,
                        col_name=col_name,
                    )

                join()
