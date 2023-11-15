from helpers.tables import common_columns
from helpers.tables import is_numeric

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_CategoricalInformationValue,
)


@TestScenario
@Name("categoricalInformationValue")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_CategoricalInformationValue("1.0")
)
def scenario(
    self,
    func="categoricalInformationValue({params})",
    table=None,
    snapshot_id=None
):
    """Check categoricalInformationValue aggregate function."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id)

    if table is None:
        table = self.context.table

    with Check("zero rows"):
        execute_query(
            f"SELECT {func.format(params='x.1,x.2')} FROM (SELECT arrayJoin(arrayPopBack([(1, 0)])) as x)"
        )

    with Check("single row"):
        execute_query(f"SELECT {func.format(params='x,y')} FROM VALUES ('x Nullable(UInt8), y Nullable(UInt8)', (0, 0))")
    
    with Check("NULL value handling"):
        execute_query(
            f"SELECT {func.format(params='x,y')} FROM VALUES ('x Nullable(UInt8), y Nullable(UInt8)', (1, NULL), (NULL,NULL), (NULL,3), (4,4), (5, 1))"
        )

    with Check("single NULL value"):
        execute_query(
            f"SELECT {func.format(params='x,y')} FROM VALUES ('x Nullable(UInt8), y Nullable(UInt8)', (NULL,NULL))"
        )

    with Check("return type"):
        execute_query(
            f"SELECT toTypeName({func.format(params='x,y')}) FROM VALUES ('x Nullable(UInt8), y Nullable(UInt8)', (NULL,NULL))"
        )

    with Check("single category 1"):
        execute_query(
            f"SELECT {func.format(params='x.1, x.2')} \
            FROM ( \
                SELECT \
                    arrayJoin([(1, 0), (1, 0), (1, 0), (1, 1), (1, 1)]) as x \
            )"
        )

    with Check("single category 2"):
        execute_query(
            f"SELECT {func.format(params='x.1, x.2')} \
            FROM ( \
                SELECT \
                    arrayJoin([(0, 0), (0, 1), (1, 0), (1, 1)]) as x \
            )"
        )

    with Check("single category 3"):
        execute_query(
            f"SELECT {func.format(params='x.1, x.2')} \
            FROM ( \
                SELECT \
                    arrayJoin([(0, 0), (0, 0), (1, 0), (1, 0)]) as x \
            )"
        )

    with Check("single category 4"):
        execute_query(
            f"SELECT {func.format(params='x.1, x.2')} \
            FROM ( \
                SELECT \
                    arrayJoin([(0, 1), (0, 1), (1, 1), (1, 1)]) as x \
            )"
        )

    with Check("single category 5"):
        execute_query(
            f"SELECT {func.format(params='x.1, x.2')} \
            FROM ( \
                SELECT \
                    arrayJoin([(0, 0), (0, 1), (1, 0), (1, 0)]) as x \
            )"
        )

    with Check("single category 6"):
        execute_query(
            f"SELECT round({func.format(params='x.1,x.2')}[1], 6), round((2 / 2 - 2 / 3) * (log(2 / 2) - log(2 / 3)), 6) \
            FROM ( \
            SELECT \
                arrayJoin([(0, 0), (1, 0), (1, 0), (1, 1), (1, 1)]) as x \
            )" 
        )

    with Check("multiple category 1"):
        execute_query(
            f"SELECT {func.format(params='x.1, x.2, x.3')} \
            FROM ( \
                SELECT \
                    arrayJoin([(1, 0, 0), (1, 0, 0), (1, 0, 1), (0, 1, 0), (0, 1, 0), (0, 1, 1)]) as x \
            )"
        )
    
    with Check("multiple category 2"):
        execute_query(
            f"SELECT \
                round({func.format(params='x.1, x.2, x.3')}[1], 6), \
                round({func.format(params='x.1, x.2, x.3')}[2], 6), \
                round((2 / 4 - 1 / 3) * (log(2 / 4) - log(1 / 3)), 6), \
                round((2 / 4 - 2 / 3) * (log(2 / 4) - log(2 / 3)), 6) \
            FROM ( \
                SELECT \
                    arrayJoin([(1, 0, 0), (1, 0, 0), (1, 0, 1), (0, 1, 0), (0, 1, 0), (0, 1, 1), (0, 1, 1)]) as x \
                FROM \
                    numbers(1000) \
            )"
        )

    with Check("multiple category 3"):
        execute_query(
            f"SELECT {func.format(params='x.1, x.2, x.3')} \
            FROM ( \
                SELECT \
                    arrayJoin([(1, 0, 0), (1, 0, 0), (1, 0, 1), (0, 1, 0), (0, 1, 0), (0, 1, 1)]) as x \
                FROM numbers(1000) \
            )"
        )

    

    


