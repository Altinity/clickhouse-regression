from testflows.core import *
from aggregate_functions.tests.steps import *
from helpers.tables import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Merge,
)

@TestScenario
@Name("merge")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Merge("1.0"))
def scenario(self, func="{name}Merge", table=None):
    """Check -Merge combinator"""
    self.context.snapshot_id = get_snapshot_id()
    note(self.context.snapshot_id)
    
    with Given("create temporary table"):
        datatype_name = "AggregateFunction(topKWeighted, UInt64, UInt64)"
        self.context.table = create_table(engine="MergeTree", 
                               columns=[Column(name="state", 
                                               datatype=DataType(name=datatype_name))], 
                                               order_by="tuple()")
        
    with When("insert data in temporary table"):
        values = ("(unhex('09FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF01002E194EEC2B33C3EEAEB2B8E2BEE5CCE1EE010052C67017181DDFE7D28CC3BB81A3C7EFE7010067751E7C48EEB0DDE7EAF9E087C9BBD8DD0100B9C6FBCB0C65577CB98DEFDFCCA1D9AB7C002B40FA3FF74F5647AB80E9FFF3FE93AB4700779ED5434C960538F7BCD69EC4C9E58238004D82B78BAA648E2ACD84DEDDA89599C72A0000000000000000000000800200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'))")
        node = self.context.node
        node.query(f"INSERT INTO {self.context.table.name} VALUES {values}")

    with Then("check the result"):
        query = f"SELECT topKWeightedMerge(state) FROM {self.context.table.name}"
        execute_query(
            query
        )
