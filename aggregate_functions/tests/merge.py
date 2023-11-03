import os 
import json
from importlib.machinery import SourceFileLoader

from testflows.core import *
from helpers.tables import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Merge,
)

def get_data_type(key, func):
    #_aggregate_functions_state_anyState_Array_Array_String__ 
    # Array(Array(String))
    key = [i for i in key.split(f"{func}State")[-1].split('_') if len(i) > 0]


    return ''


@TestScenario
def merge(self, func):
    """Check -Merge combinator function."""
    snapshot_path = os.path.join(current_dir(), "snapshots", f"steps.py.{func.lower()}state.{current_cpu()}.snapshot")
    if not os.path.exists(snapshot_path):
        xfail(reason=f"no snapshot found {snapshot_path}")

    snapshot_module = SourceFileLoader("snapshot", snapshot_path).load_module()
    snapshot_attrs = {k:v for k,v in vars(snapshot_module).items() if not k.startswith('__')}

    for key, value in snapshot_attrs.items():
        if value.strip() != value.split()[0].strip(): # add for loop with split lines
            note("Not implemented")
            continue

        value_dict = json.loads(value)
        for _, v in value_dict.items():
            hex_repr = v
            data_type = get_data_type(key, func)
            

            if "State" in query_data.split()[-2]:
                note(f"{key}")
                note(f"{hex_repr}, {data_type}")
                params = data_type
                with Given("create temporary table"):
                    datatype_name = f"AggregateFunction({func}, {params})"
                    self.context.table = create_table(engine="MergeTree", 
                                                        columns=[Column(name="state", 
                                                        datatype=DataType(name=datatype_name))], 
                                                        order_by="tuple()")
                with When("insert data in temporary table"):
                    values = (f"(unhex('{hex_repr}'))")
                    node = self.context.node
                    node.query(f"INSERT INTO {self.context.table.name} VALUES {values}")

                with Then(""):
                    self.context.snapshot_id = get_snapshot_id(f"{func}")
                    query = f"SELECT {func}Merge(state) FROM {self.context.table.name}"
                    execute_query(
                        query, snapshot_name=f"_aggregate_functions_any_Bool"
                    )
        



@TestFeature
@Name("merge")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Merge("1.0"))
def feature(self):
    """Check aggregate functions `-Merge` combinator."""
    for name in aggregate_functions:
        Scenario(f"{name}Merge", test=merge)(func=name)
        
    










# with Given("create temporary table"):
#     datatype_name = "AggregateFunction(topKWeighted, UInt64, UInt64)"
#     self.context.table = create_table(engine="MergeTree", 
#                            columns=[Column(name="state", 
#                                            datatype=DataType(name=datatype_name))], 
#                                            order_by="tuple()")
    
# with When("insert data in temporary table"):
#     values = ("(unhex('09FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF01002E194EEC2B33C3EEAEB2B8E2BEE5CCE1EE010052C67017181DDFE7D28CC3BB81A3C7EFE7010067751E7C48EEB0DDE7EAF9E087C9BBD8DD0100B9C6FBCB0C65577CB98DEFDFCCA1D9AB7C002B40FA3FF74F5647AB80E9FFF3FE93AB4700779ED5434C960538F7BCD69EC4C9E58238004D82B78BAA648E2ACD84DEDDA89599C72A0000000000000000000000800200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'))")
#     node = self.context.node
#     node.query(f"INSERT INTO {self.context.table.name} VALUES {values}")

# with Then("check the result"):
#     query = f"SELECT topKWeightedMerge(state) FROM {self.context.table.name}"
#     execute_query(
#         query
#     )

