from testflows.core import *

from helpers.tables import common_columns
from helpers.tables import is_numeric, is_nullable
from helpers.common import check_clickhouse_version


from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SumMapFiltered,
)


@TestCheck
def datatype(self, func, table, col1_name, col2_name, col1_type):
    """Check different column types."""
    r = self.context.node.query(
        f"SELECT any({col1_name}) FROM {table.name} GROUP BY {col1_name} ORDER BY {col1_name} LIMIT 1"
    ).output
    _func = func.replace(
        "({params})", f"(cast([{r}],'Array({col1_type})'))({{params}})"
    )
    execute_query(
        f"SELECT {_func.format(params='['+col1_name +'],['+col2_name+']')}, any(toTypeName([{col1_name}])), any(toTypeName([{col2_name}])) FROM {table.name} FORMAT JSONEachRow"
    )


@TestScenario
@Name("sumMapFiltered")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SumMapFiltered("1.0"))
def scenario(
    self,
    func="sumMapFiltered({params})",
    table=None,
    decimal=False,
    date=False,
    datetime=False,
    extended_precision=False,
    snapshot_id=None,
):
    """Check sumMapFiltered aggregate function."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, add_analyzer=True
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    _func = func.replace("({params})", f"([1,2,3,4,5,6,7])({{params}})")

    with Check("constant"):
        execute_query(
            f"SELECT {_func.format(params='[1],[1]')}, any(toTypeName([1])),  any(toTypeName([1]))"
        )

    with Check("zero rows"):
        execute_query(
            f"SELECT {_func.format(params='[number],[number]')}, any(toTypeName([number])), any(toTypeName([number])) FROM numbers(0)"
        )

    with Check("single row"):
        execute_query(
            f"SELECT {_func.format(params='[number],[number+1]')}, any(toTypeName([number])), any(toTypeName([number])) FROM numbers(1)"
        )

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {_func.format(params='[number],[even]')}, any(toTypeName([number])), any(toTypeName([even])) FROM numbers(10) GROUP BY even"
        )

    _func = func.replace("({params})", f"([6.7])({{params}})")

    with Check("inf, -inf, nan"):
        for permutation in permutations_with_replacement(["inf", "-inf", "nan"], 2):
            x, y = permutation
            with Check(f"{x},{y}"):
                execute_query(
                    f"SELECT {_func.format(params='[x],[y]')}, any(toTypeName([x])), any(toTypeName([y]))  FROM values('x Float64, y Float64', (0, 1), (1, 2.3), ({x},{y}), (6.7,3), (4,4), (5, 1))"
                )

    _func = func.replace(
        "({params})", f"(cast([1,2,3,4,5,6,7], 'Array(Int64)'))({{params}})"
    )

    with Check("some negative values"):
        execute_query(
            f"SELECT {_func.format(params='[number-5],[number+10]')}, any(toTypeName([number])), any(toTypeName([number])) FROM numbers(1, 10)"
        )

    _func = func.replace("({params})", f"([1,2,3,4,5,6,7])({{params}})")

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({_func.format(params='[number], [number+1]')}), any(toTypeName([number])), any(toTypeName([number])) FROM numbers(1, 10)"
        )

    with Check("example1"):
        execute_query(
            f"SELECT {_func.format(params='a,b')}, any(toTypeName(a)), any(toTypeName(b)) FROM values('a Array(UInt32), b Array(UInt64)', ([1, 2], [2, 2]), ([2, 3], [1, 1]))"
        )

    with Check("datatypes"):
        with Check(
            "permutations",
            description="sanity check most common column type permutations",
        ):
            with Pool(3) as executor:
                if check_clickhouse_version(">=23.11")(self):
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
                else:
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
                        and not is_nullable(col.datatype)
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
                    )(
                        func=func,
                        table=table,
                        col1_name=col1_name,
                        col2_name=col2_name,
                        col1_type=col1_type,
                    )

                join()
