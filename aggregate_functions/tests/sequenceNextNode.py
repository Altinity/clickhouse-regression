from helpers.tables import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SequenceNextNode,
)


@TestScenario
@Name("sequenceNextNode")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SequenceNextNode("1.0")
)
def scenario(
    self,
    func="sequenceNextNode({params})",
    table=None,
    snapshot_id=None,
):
    """Check sequenceNextNode parametric aggregate function"""

    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    func_ = func.replace("({params})", f"('forward', 'head')({{params}})")

    with Check("doc example 1"):
        params = "dt, page, page = 'A', page = 'A', page = 'B'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String', (1, 1, 'A'), (2, 1, 'B'), (3, 1, 'C'), (4, 1, 'D'), (5, 1, 'E')) GROUP BY id settings allow_experimental_funnel_functions = 1"
        )

    with Check("doc example 2"):
        params = "dt, page, page = 'Basket', page = 'Basket', page = 'Gift'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String', (1, 1, 'Home'), (2, 1, 'Gift'), (3, 1, 'Exit'), (1, 2, 'Home'), (2, 2, 'Home'), (3, 2, 'Gift'), (4, 2, 'Basket'), (1, 3, 'Gift'), (2, 3, 'Home'), (3, 3, 'Gift'), (4, 3, 'Basket')) GROUP BY id settings allow_experimental_funnel_functions = 1"
        )

    func_ = func.replace("({params})", f"('backward', 'tail')({{params}})")

    with Check("doc example 3"):
        params = "dt, page, page = 'Home', page = 'Home', page = 'Gift'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String', (1, 1, 'Home'), (2, 1, 'Gift'), (3, 1, 'Exit'), (1, 2, 'Home'), (2, 2, 'Home'), (3, 2, 'Gift'), (4, 2, 'Basket'), (1, 3, 'Gift'), (2, 3, 'Home'), (3, 3, 'Gift'), (4, 3, 'Basket')) GROUP BY id settings allow_experimental_funnel_functions = 1"
        )

    func_ = func.replace("({params})", f"('forward', 'first_match')({{params}})")

    with Check("doc example 4"):
        params = "dt, page, page = 'Gift', page = 'Gift'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String', (1, 1, 'Home'), (2, 1, 'Gift'), (3, 1, 'Exit'), (1, 2, 'Home'), (2, 2, 'Home'), (3, 2, 'Gift'), (4, 2, 'Basket'), (1, 3, 'Gift'), (2, 3, 'Home'), (3, 3, 'Gift'), (4, 3, 'Basket')) GROUP BY id settings allow_experimental_funnel_functions = 1"
        )

    with Check("doc example 5"):
        params = "dt, page, page = 'Gift', page = 'Gift', page = 'Home'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String', (1, 1, 'Home'), (2, 1, 'Gift'), (3, 1, 'Exit'), (1, 2, 'Home'), (2, 2, 'Home'), (3, 2, 'Gift'), (4, 2, 'Basket'), (1, 3, 'Gift'), (2, 3, 'Home'), (3, 3, 'Gift'), (4, 3, 'Basket')) GROUP BY id settings allow_experimental_funnel_functions = 1"
        )

    func_ = func.replace("({params})", f"('backward', 'last_match')({{params}})")

    with Check("doc example 6"):
        params = "dt, page, page = 'Gift', page = 'Gift'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String', (1, 1, 'Home'), (2, 1, 'Gift'), (3, 1, 'Exit'), (1, 2, 'Home'), (2, 2, 'Home'), (3, 2, 'Gift'), (4, 2, 'Basket'), (1, 3, 'Gift'), (2, 3, 'Home'), (3, 3, 'Gift'), (4, 3, 'Basket')) GROUP BY id settings allow_experimental_funnel_functions = 1"
        )

    with Check("doc example 7"):
        params = "dt, page, page = 'Gift', page = 'Gift', page = 'Home'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String', (1, 1, 'Home'), (2, 1, 'Gift'), (3, 1, 'Exit'), (1, 2, 'Home'), (2, 2, 'Home'), (3, 2, 'Gift'), (4, 2, 'Basket'), (1, 3, 'Gift'), (2, 3, 'Home'), (3, 3, 'Gift'), (4, 3, 'Basket')) GROUP BY id settings allow_experimental_funnel_functions = 1"
        )

    func_ = func.replace("({params})", f"('forward', 'head')({{params}})")

    with Check("doc example 8"):
        params = "dt, page, ref = 'ref1', page = 'A'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String, ref String', (1, 1, 'A', 'ref4'), (2, 1, 'A', 'ref3'), (3, 1, 'B', 'ref2'), (4, 1, 'B', 'ref1')) settings allow_experimental_funnel_functions = 1"
        )

    func_ = func.replace("({params})", f"('backward', 'tail')({{params}})")

    with Check("doc example 9"):
        params = "dt, page, ref = 'ref4', page = 'B'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String, ref String', (1, 1, 'A', 'ref4'), (2, 1, 'A', 'ref3'), (3, 1, 'B', 'ref2'), (4, 1, 'B', 'ref1')) settings allow_experimental_funnel_functions = 1"
        )

    with Check("return type"):
        params = "dt, page, ref = 'ref4', page = 'B'"
        execute_query(
            f"SELECT toTypeName({func_.format(params=params)}) FROM VALUES ('dt DateTime, id int, page String, ref String', (1, 1, 'A', 'ref4'), (2, 1, 'A', 'ref3'), (3, 1, 'B', 'ref2'), (4, 1, 'B', 'ref1')) settings allow_experimental_funnel_functions = 1"
        )

    func_ = func.replace("({params})", f"('forward', 'first_match')({{params}})")

    with Check("doc example 10"):
        params = "dt, page, ref = 'ref3', page = 'A'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String, ref String', (1, 1, 'A', 'ref4'), (2, 1, 'A', 'ref3'), (3, 1, 'B', 'ref2'), (4, 1, 'B', 'ref1')) settings allow_experimental_funnel_functions = 1"
        )

    func_ = func.replace("({params})", f"('backward', 'last_match')({{params}})")

    with Check("doc example 11"):
        params = "dt, page, ref = 'ref2', page = 'B'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String, ref String', (1, 1, 'A', 'ref4'), (2, 1, 'A', 'ref3'), (3, 1, 'B', 'ref2'), (4, 1, 'B', 'ref1')) settings allow_experimental_funnel_functions = 1"
        )

    with Check("NULL value handling"):
        params = "dt, page, ref = 'ref2', page = 'B'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page Nullable(String), ref String', (1, 1, NULL, 'ref4'), (2, 1, NULL, 'ref3'), (3, 1, NULL, 'ref2'), (4, 1, 'B', 'ref1')) settings allow_experimental_funnel_functions = 1"
        )

    with Check("single NULL value"):
        params = "dt, page, ref = 'ref2', page = 'B'"
        execute_query(
            f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page Nullable(String), ref String', (1, 1, NULL, 'ref4'), (2, 1,'A', 'ref3'), (3, 1, 'A', 'ref2'), (4, 1, 'B', 'ref1')) settings allow_experimental_funnel_functions = 1"
        )

    with Check("permutations"):
        directions = ["forward", "backward"]
        bases = ["head", "tail", "first_match", "last_match"]
        invalid = {"forward": "tail", "backward": "head"}
        for direction in directions:
            for base in bases:
                if base == invalid.get(direction, ""):
                    continue
                with Check(f"{base}_{direction}"):
                    func_ = func.replace(
                        "({params})", f"('{direction}', '{base}')({{params}})"
                    )
                    params = "dt, page, page = 'Gift', page = 'Gift'"
                    execute_query(
                        f"SELECT {func_.format(params=params)} FROM VALUES ('dt DateTime, id int, page String', (1, 1, 'Home'), (2, 1, 'Gift'), (3, 1, 'Exit'), (1, 2, 'Home'), (2, 2, 'Home'), (3, 2, 'Gift'), (4, 2, 'Basket'), (1, 3, 'Gift'), (2, 3, 'Home'), (3, 3, 'Gift'), (4, 3, 'Basket')) GROUP BY id settings allow_experimental_funnel_functions = 1"
                    )
