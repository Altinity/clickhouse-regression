from testflows.core import *

from helpers.tables import *
from helpers.common import *

from functions.tests.common import *


@TestCheck
def datatype(self, func, table, col_name):
    """Check different column types."""
    # self.context.node.query(f"SELECT {col_name} FROM {table.name} FORMAT Pretty")
    execute_query(
        f"SELECT {func.format(params=col_name)} FROM {table.name}",
    )


@TestScenario
def check(self, func, table, snapshot_id=None):

    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1')}")

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='number')} FROM numbers(0)")

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number')} FROM numbers(10) GROUP BY number"
        )

    with Check("some negative values"):
        execute_query(f"SELECT {func.format(params='number-5')} FROM numbers(1, 10)")

    with Check("first non-NULL value"):
        execute_query(
            f"SELECT {func.format(params='x')} FROM values('x Nullable(Int8)', NULL, NULL, NULL, 3, 4, 5)"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='number')}) FROM numbers(1, 10)"
        )

    with Check("only nan"):
        execute_query(f"SELECT {func.format(params='x')} FROM values('x Float64', nan)")

    with Check("string that ends with \\0"):
        execute_query(
            f"SELECT {func.format(params='x')} FROM values('x String', 'hello\0\0')",
            exitcode=43,
            message="DB::Exception: Illegal type String of argument of function",
        )

    for v in ["inf", "-inf", "nan"]:
        with Check(f"{v}"):
            execute_query(
                f"SELECT {func.format(params='x')}   FROM values('x Float64', ({v}))"
            )

    with Pool(5) as executor:
        for column in table.columns:
            Check(
                f"{column.datatype.name}",
                test=datatype,
                parallel=True,
                executor=executor,
            )(func=func, table=table, col_name=column.name)
        join()


@TestFeature
@Name("math functions")
def feature(self):
    """Test all math functions."""

    with Given("tables with all data types"):
        self.context.table = create_table(
            engine="MergeTree",
            columns=generate_all_basic_numeric_column_types(),
            order_by_all_columns=False,
            order_by="tuple()",
        )

    with And("populate table with test data"):
        self.context.table.insert_test_data(cardinality=1, shuffle_values=False)

    with Then("test all math functions"):
        with Pool(5) as executor:
            for func in one_parameter_functions:
                Scenario(f"{func}", test=check, parallel=True, executor=executor)(
                    func=f"{func}({{params}})", table=self.context.table
                )
            join()
