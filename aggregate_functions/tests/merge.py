import os 
import json
from importlib.machinery import SourceFileLoader

from testflows.core import *
from helpers.tables import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Merge,
)

def array_on_duplicate_keys(ordered_pairs):
    """Convert duplicate keys to arrays."""
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            d[k].append(v)
        else:
           d[k] = [v]
    return d


@TestCheck
def check(self, func, datatypes, hex_repr, snapshot_name, is_low_cardinality=False):
    if is_low_cardinality:
        self.context.node.query(f"SET allow_suspicious_low_cardinality_types = 1")

    with Given("I create temporary table"):
        datatype_name = f"AggregateFunction({func}, {datatypes})"
        self.context.table = create_table(
                                        engine="MergeTree", 
                                        columns=[Column(name="state", datatype=DataType(name=datatype_name))], 
                                        order_by="tuple()"
                                        )
        
    with When("I insert data in temporary table"):
        if is_low_cardinality:
            values = f"(CAST(unhex('{hex_repr}'), 'AggregateFunction({func}, {datatypes})'))"
        else:
            values = (f"(unhex('{hex_repr}'))")
        self.context.node.query(f"INSERT INTO {self.context.table.name} VALUES {values}")

    with Then("I check the result"):
        execute_query(
            f"SELECT {func}Merge(state) FROM {self.context.table.name}", snapshot_name=snapshot_name
        )


@TestScenario
def merge(self, func, snapshot_id):
    """Check aggregate function -Merge combinator."""
    snapshot_path = os.path.join(current_dir(), "snapshots", f"steps.py.{snapshot_id}.{current_cpu()}.snapshot")
  
    if not os.path.exists(snapshot_path):
        xfail(reason=f"no snapshot found {snapshot_path}")

    snapshot_module = SourceFileLoader("snapshot", snapshot_path).load_module()
    snapshot_attrs = {k:v for k,v in vars(snapshot_module).items() if not k.startswith('__')}

    for key, value in snapshot_attrs.items():
        data = value.strip().split('\n')
        idx = 0
        for hex_and_datatype in data:
            value_dict = json.loads(hex_and_datatype, object_pairs_hook=array_on_duplicate_keys)
            hex_repr = ''
            datatypes = ''
            note(value_dict)
            for k, val in value_dict.items():
                if 'hex(' in k and 'toTypeName' not in k:
                    hex_repr = val[0]
                elif 'toTypeName' in k:
                    if len(datatypes) == 0:
                        datatypes += ' ,'.join(datatype for datatype in val if len(datatype) > 0)
                    else:
                        datatypes += ' ,'+ ' ,'.join(datatype for datatype in val if len(datatype) > 0)
            if hex_repr is not None and len(hex_repr) > 0 and len(datatypes) > 0:
                name = key.replace('state_', 'merge_')
                name = name.replace('State', 'Merge') + '_' + str(idx)
                idx += 1 
                Check(test=check)(func=func, datatypes=datatypes, hex_repr=hex_repr, snapshot_name=name, 
                                  is_low_cardinality='LowCardinality' in datatypes)
        

@TestFeature
@Name("merge")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Merge("1.0"))
def feature(self):
    """Check aggregate functions `-Merge` combinator."""
    for name in aggregate_functions:
        try:
            scenario = load(f"aggregate_functions.tests.{name}", "scenario")
        except ModuleNotFoundError as e:
            with Scenario(f"{name}Merge"):
                skip(reason=f"{name}State() test is not implemented")
        else:
            with Scenario(f"{name}Merge", description=f"Get snapshot name to retrieve state of {name} function"):
                snapshot_id = scenario(func=name).lower().replace("merge", "state")
                merge(func=name, snapshot_id=snapshot_id)

