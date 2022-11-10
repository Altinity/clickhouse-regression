import itertools

from helpers.tables import common_columns
from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Argmin,
)


@TestCheck
def execute_multi_query(self, query):
    """Execute multi query statement."""
    execute_query("".join(query), use_file=True, format=None, hash_output=False)


@TestCheck
def datatype(self, func, table, col1_name, col2_name):
    """Check different column types."""
    execute_query(f"SELECT {func.format(params=col1_name+','+col2_name)} FROM {table.name} FORMAT JSONEachRow")


@TestFeature
@Name("argMin")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Argmin("1.0"))
def feature(self, func="argMin({params})", table=None):
    """Check argMin or argMax or one of their combinator aggregate functions. By default: argMin."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    with Check("constant"):
        execute_query(f"SELECT {func.format(params='1,2')}")

    with Check("zero rows"):
        execute_query(f"SELECT {func.format(params='number, number+1')} FROM numbers(0)")

    with Check("with group by"):
        execute_query(
            f"SELECT number % 2 AS even, {func.format(params='number, even')} FROM numbers(10) GROUP BY even"
        )

    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x, y')} FROM values('x Nullable(Int8), y Nullable(String)', (1, NULL), (NULL, 'hello'), (3, 'there'), (NULL, NULL), (5, 'you'))"
        )
    
    with Check("doc example"):
        execute_query(
            f"SELECT {func.format(params='user, salary')} FROM values('user String, salary Float64',('director',5000),('manager',3000),('worker', 1000))"
        )

    with Suite("datatypes"):
        if self.context.stress:
            with Suite("stress", description="check all possible column type permutations"):
                with Pool(10) as executor:
                    permutations = list(itertools.permutations(table.columns, 2))
                    permutations.sort()

                    for i in range(0, len(permutations), 1000):
                        chunk = permutations[i:i+1000]

                        query = []
                        for col1, col2 in chunk:
                            col1_name, col1_type = col1.split(" ", 1)
                            col2_name, col2_type = col2.split(" ", 1)

                            query.append(f"SELECT {func.format(params=col1_name+','+col2_name)} FROM {table.name} FORMAT JSONEachRow; ")
                        
                        Check(f"datatypes {i}", test=execute_multi_query, parallel=True, executor=executor)(query=query)

                    join()
        else:
            with Suite("sanity", description="sanity check most common column type permutations"):
                with Pool(3) as executor:
                    columns = [col for col in table.columns if col in common_columns]
                    permutations = list(itertools.permutations(columns, 2))
                    permutations.sort()

                    for col1, col2 in permutations:
                        col1_name, col1_type = col1.split(" ", 1)
                        col2_name, col2_type = col2.split(" ", 1)

                        Check(f"{col1_type},{col2_type}", test=datatype, parallel=True, executor=executor)(func=func, table=table, col1_name=col1_name, col2_name=col2_name)

                    join()