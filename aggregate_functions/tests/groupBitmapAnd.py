import random

from testflows.core import *

from helpers.tables import *
from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapAnd,
)


def generate_test_data(table_name=None, datatype=None, sample_size=150, num=4):
    if table_name is None or datatype is None:
        return ""
    rng = random.Random(41)
    return [
        rng.sample(
            range(datatype.max + 1 - sample_size * 3, datatype.max + 1), sample_size
        )
        for _ in range(num)
    ]


@TestCheck
def check(self, datatype, func, sample_size=150, num=4, same=False, same_values=False):
    with Given(f"I create temporary table with {datatype.name} columns"):
        datatype_name = f"AggregateFunction(groupBitmap, {datatype.name})"
        uid = getuid()
        self.context.table = create_table(
            name=uid,
            engine="MergeTree",
            columns=[
                Column(name="tag_id", datatype=String()),
                Column(name="z", datatype=DataType(name=datatype_name)),
            ],
            order_by="tag_id",
        )

    with And(f"I populate table with {datatype.name} test data"):
        values = generate_test_data(
            table_name=self.context.table.name,
            datatype=datatype,
            sample_size=sample_size,
            num=num,
        )
        if same_values:
            values[0] = [values[0][0] for _ in range(sample_size)]
        if same:
            values = [values[0] for _ in range(num)]
        data = ",".join(
            [
                f"('tag{i}', bitmapBuild(cast({values[i]} as Array({datatype.name}))))"
                for i in range(num)
            ]
        )
        self.context.node.query(f"INSERT INTO {self.context.table.name} VALUES {data}")

    with Check(f"result length {datatype.name}"):
        execute_query(
            f"SELECT {func.format(params='z')}, any(toTypeName(z)) FROM {self.context.table.name} WHERE like(tag_id, 'tag%')"
        )

    with Check(f"array output {datatype.name}"):
        if "State" in self.name:
            skip(reason=f"State used in test")
        func_ = func.replace("({params})", "State({params})")
        execute_query(
            f"SELECT arraySort(bitmapToArray({func_.format(params='z')})) FROM {self.context.table.name} WHERE like(tag_id, 'tag%')"
        )


@TestScenario
@Name("groupBitmapAnd")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapAnd("1.0"))
def scenario(
    self,
    func="groupBitmapAnd({params})",
    snapshot_id=None,
    table=None,
):
    """Check groupBitmapAnd aggregate function."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=">=23.10"
    )

    if "Merge" in self.name:
        skip(reason=f"Does not support -Merge combinator")

    datatype_list = [UInt8(), UInt16(), UInt32(), UInt64()]

    for datatype in datatype_list:
        with Check(f"example {datatype.name}"):
            check(datatype=datatype, func=func)

        with Check(f"same array in all rows of type {datatype.name}"):
            check(datatype=datatype, func=func, sample_size=30, num=15, same=True)

        with Check(f"single array of type {datatype.name}"):
            check(datatype=datatype, func=func, sample_size=30, num=1)

        with Check(f"empty array of type {datatype.name}"):
            check(datatype=datatype, func=func, sample_size=0, num=1)

        with Check(f"same arrays with same numbers"):
            check(
                datatype=datatype,
                func=func,
                sample_size=30,
                num=15,
                same=True,
                same_values=True,
            )
