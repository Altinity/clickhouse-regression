from testflows.core import *

from helpers.tables import *
from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapAnd,
)


def generate_test_data(table_name=None, datatype=None, num_rows=4):
    if table_name is None or datatype is None:
        return ""
    random.seed(42)
    return [
        random.sample(range(datatype.max + 1 - 255, datatype.max + 1), 150)
        for _ in range(num_rows)
    ]


@TestScenario
@Name("groupBitmapAnd")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapAnd("1.0"))
def scenario(
    self,
    func="groupBitmapAnd({params})",
    snapshot_id=None,
):
    """Check groupBitmapAnd aggregate function."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    datatype_list = [UInt8(), UInt16(), UInt32(), UInt64()]

    for datatype in datatype_list:
        with Given(f"I create temporary table with {datatype.name} columns"):
            datatype_name = f"AggregateFunction(groupBitmap, {datatype.name})"
            self.context.table = create_table(
                engine="MergeTree",
                columns=[
                    Column(name="tag_id", datatype=String()),
                    Column(name="z", datatype=DataType(name=datatype_name)),
                ],
                order_by="()",
            )

        with And("I populate table with test data"):
            values = generate_test_data(
                table_name=self.context.table.name, datatype=datatype
            )
            data = ",".join(
                [
                    f"('tag{i}', bitmapBuild(cast({values[i]} as Array({datatype.name}))))"
                    for i in range(len(values))
                ]
            )
            self.context.node.query(
                f"INSERT INTO {self.context.table.name} VALUES {data}"
            )

        with Check(f"length of the result {datatype.name}"):
            execute_query(
                f"SELECT {func.format(params='z')} FROM {self.context.table.name} WHERE like(tag_id, 'tag%')"
            )

        with Check(f"groupBitmapAndState {datatype.name}"):
            func_ = func.replace("({params})", "State({params})")
            execute_query(
                f"SELECT arraySort(bitmapToArray({func_.format(params='z')})) FROM {self.context.table.name} WHERE like(tag_id, 'tag%')"
            )

    with Given(f"I create temporary table with {datatype.name} columns"):
        datatype_name = f"AggregateFunction(groupBitmap, UInt32)"
        self.context.table = create_table(
            engine="MergeTree",
            columns=[
                Column(name="tag_id", datatype=String()),
                Column(name="z", datatype=DataType(name=datatype_name)),
            ],
            order_by="()",
        )

    with And("I populate table with test data"):
        values = generate_test_data(
            table_name=self.context.table.name, datatype=UInt32(), num_rows=1
        )
        data = ",".join(
            [
                f"('tag{i}', bitmapBuild(cast({values[0]} as Array(UInt32))))"
                for i in range(15)
            ]
        )
        self.context.node.query(f"INSERT INTO {self.context.table.name} VALUES {data}")

    with Check("Same array in all rows result length"):
        func_ = func.replace("({params})", "State({params})")
        execute_query(
            f"SELECT {func.format(params='z')} FROM {self.context.table.name} WHERE like(tag_id, 'tag%')"
        )

    with Check("Same array in all rows"):
        func_ = func.replace("({params})", "State({params})")
        execute_query(
            f"SELECT arraySort(bitmapToArray({func_.format(params='z')})) FROM {self.context.table.name} WHERE like(tag_id, 'tag%')"
        )
