from testflows.core import *

from helpers.tables import *
from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapAnd
)


@TestScenario
@Name("groupBitmapAnd")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapAnd("1.0"))
def scenario(
    self,
    func="groupBitmapAnd({params})",
    table=None,
    extended_precision=False,
    snapshot_id=None,
):
    """Check groupBitAnd aggregate function."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    with Given("I create temporary table"):
        datatypes='UInt32'
        datatype_name = f"AggregateFunction({func}, {datatypes})"
        self.context.table = create_table(
            engine="MergeTree",
            columns=[Column(name="state", datatype=DataType(name=datatype_name)), 
                     Column(name='tag_id', datatype=DataType(name='String'))],
            order_by="tag_id",
        )


    for column in table.columns:
        column_name, column_type = column.name, column.datatype.name

        if not is_unsigned_integer(
            column.datatype, extended_precision=extended_precision
        ):
            continue

        with Check(f"{column_type}"):
            execute_query(
                f"SELECT {func.format(params=column_name)}, any(toTypeName({column_name})) FROM {table.name}"
            )
