from helpers.tables import unwrap, Array, Map, Tuple, Decimal

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_UniqApacheHLL,
)
from aggregate_functions.tests.any import scenario as checks


def is_supported(datatype):
    """Return True if uniqApacheHLL accepts the data type."""
    datatype = unwrap(datatype)

    if isinstance(datatype, (Array, Map, Tuple, Decimal)):
        return False

    return not datatype.is_extended_precision


@TestScenario
@Name("uniqApacheHLL")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_UniqApacheHLL("1.0")
)
def scenario(self, func="uniqApacheHLL({params})", table=None, snapshot_id=None):
    """Check uniqApacheHLL aggregate function by using the same tests as for any."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=">=26.6", add_analyzer=True
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(
        func=func,
        table=table,
        snapshot_id=self.context.snapshot_id,
        datatype_filter=is_supported,
    )

    for column in table.columns:
        if is_supported(column.datatype):
            continue

        with Check(f"{column.datatype.name}"):
            execute_query(
                f"SELECT {func.format(params=column.name)} FROM {table.name}",
                exitcode=43,
                message="DB::Exception: Illegal type",
            )

    with Check("estimation mode"):
        execute_query(
            f"SELECT {func.format(params='number')}, any(toTypeName(number)) FROM numbers(100000) SETTINGS max_threads = 1"
        )

    params = "({params}"

    with Check("parameters"):
        for p in ["4", "14", "12, 'HLL_6'", "12, 'HLL_8'"]:
            with When(f"{p}"):
                _func = func.replace(params, f"({p}){params}")
                execute_query(
                    f"SELECT {_func.format(params='number')}, any(toTypeName(number)) FROM numbers(100000) SETTINGS max_threads = 1"
                )

    with Check("empty string"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x String', (''))"
        )

    with Check("empty string with non-empty string"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x String', (''), ('a'))"
        )

    if "State" not in self.name:
        with Check("Apache DataSketches state"):
            execute_query(
                "SELECT finalizeAggregation(CAST(unhex('1C0201070C03080500CBD7C2042BF2FB06862FF90D7581660781BC5D06'), 'AggregateFunction(uniqApacheHLL, UInt64)'))"
            )
