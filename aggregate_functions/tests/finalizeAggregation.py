import os
import json
from importlib.machinery import SourceFileLoader

from testflows.core import *
from helpers.tables import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_FinalizeAggregationFunction,
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

    with When("I cast the data"):
        if "'" in func:
            func_ = func.replace("'", "\\'")
        else:
            func_ = func
        values = (
            f"(CAST(unhex('{hex_repr}'), 'AggregateFunction({func_}, {datatypes})'))"
        )

    with Then("I check the result"):
        execute_query(
            f"SELECT finalizeAggregation{values}", snapshot_name=snapshot_name
        )


@TestScenario
def finalizeAggregation(self, scenario, short_name, extra_data=None):
    if extra_data is not None:
        if short_name in funcs_to_run_with_extra_data:
            snapshot_id, func = scenario(func=short_name, extra_data=extra_data)
    else:
        snapshot_id, func = scenario()

    snapshot_id = snapshot_id.lower().replace(
        "_finalizeaggregation_merge", "state"
    )  # need state from snapshots of -State combinator
    snapshot_path = os.path.join(
        current_dir(), "snapshots", f"steps.py.{snapshot_id}.{current_cpu()}.snapshot"
    )
    self.context.snapshot_id = self.context.snapshot_id.replace("_merge", "")

    if not os.path.exists(snapshot_path):
        xfail(reason=f"no snapshot found {snapshot_path}")

    fullname = func + getuid()
    snapshot_module = SourceFileLoader(fullname, snapshot_path).load_module()
    snapshot_attrs = {
        k: v for k, v in vars(snapshot_module).items() if not k.startswith("__")
    }

    with Pool(7) as executor:
        for key, value in snapshot_attrs.items():
            with By("I break single snapshot value into lines"):
                data = value.strip().split("\n")

            idx = 0
            for hex_and_datatype in data:
                with By("I convert entry into JSON"):
                    value_dict = json.loads(
                        hex_and_datatype, object_pairs_hook=array_on_duplicate_keys
                    )

                with By(
                    "I get hex representation of the state and aggregate function data types"
                ):
                    hex_repr = ""
                    datatypes = ""
                    for k, val in value_dict.items():
                        if "hex(" in k and "toTypeName" not in k:
                            hex_repr = val[0]
                        elif "toTypeName" in k:
                            if len(datatypes) == 0:
                                datatypes += " ,".join(
                                    datatype for datatype in val if len(datatype) > 0
                                )
                            else:
                                datatypes += " ," + " ,".join(
                                    datatype for datatype in val if len(datatype) > 0
                                )

                with By("I create snapshot name for the finalizeAggregation function"):
                    if (
                        hex_repr is not None
                        and len(hex_repr) > 0
                        and len(datatypes) > 0
                    ):
                        name = (
                            key.replace("state_", "finalizeAggregation_").replace(
                                "State", "finalizeAggregation"
                            )
                            + f"_{idx}"
                        )
                        idx += 1
                        Check(f"{name}", test=check, parallel=True, executor=executor)(
                            func=func,
                            datatypes=datatypes,
                            hex_repr=hex_repr,
                            snapshot_name=name,
                            is_low_cardinality="LowCardinality" in datatypes,
                        )
        join()


@TestFeature
@Name("finalizeAggregation")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State_With_FinalizeAggregationFunction(
        "1.0"
    )
)
def feature(self, extra_data=None, aggregate_functions=aggregate_functions):
    """Check aggregate function finalizeAggregation."""
    not_implemented = [
        "quantileDeterministic",
        "quantilesDeterministic",
        "stochasticLinearRegression",
        "stochasticLogisticRegression",
        "sumMap",
        "sumMapFiltered",  # parameters of different type
        "sumMapFilteredWithOverflow",  # parameters of different type
        "maxMap",
        "minMap",
        "quantileTDigestWeighted",
        "singleValueOrNull",  # problem on 22.8
        "sequenceCount",
        "sequenceMatch",
        "windowFunnel",
        "quantileGK",
        "sequenceNextNode",
        "sequenceMatchEvents",
    ]

    test_funcs = [i for i in aggregate_functions]
    for i in not_implemented:
        if i in test_funcs:
            test_funcs.remove(i)

    if extra_data is not None:
        with Pool(15) as executor:
            for name in funcs_to_run_with_extra_data:
                try:
                    scenario = load(f"aggregate_functions.tests.{name}", "scenario")
                except ModuleNotFoundError as e:
                    with Scenario(f"{name}_finalizeAggregation_Merge"):
                        skip(reason=f"{name}State() test is not implemented")
                else:
                    Scenario(
                        f"{name}_finalizeAggregation_Merge",
                        description=f"Get snapshot name to retrieve state of {name} function",
                        test=finalizeAggregation,
                        parallel=True,
                        executor=executor,
                    )(scenario=scenario, short_name=name, extra_data=extra_data)
            join()
    else:
        with Pool(15) as executor:
            for name in test_funcs:
                try:
                    scenario = load(f"aggregate_functions.tests.{name}", "scenario")
                except ModuleNotFoundError as e:
                    with Scenario(f"{name}_finalizeAggregation_Merge"):
                        skip(reason=f"{name}State() test is not implemented")
                else:
                    Scenario(
                        f"{name}_finalizeAggregation_Merge",
                        description=f"Get snapshot name to retrieve state of {name} function",
                        test=finalizeAggregation,
                        parallel=True,
                        executor=executor,
                    )(scenario=scenario, short_name=name)
            join()
