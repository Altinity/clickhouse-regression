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


@TestScenario
def check(
    self,
    func,
    datatypes,
    hex_repr,
    snapshot_name,
    short_name,
    is_low_cardinality=False,
    is_parametric=False,
    combinator="ArgMin",
):
    if is_low_cardinality:
        self.context.node.query(f"SET allow_suspicious_low_cardinality_types = 1")

    with Given("I add datatype of expression for -ArgMin combinator"):
        if len(datatypes) > 0:
            datatypes += " , UInt8"
        else:
            datatypes = "UInt8"

    with When("I cast the data"):
        if "'" in func:
            func_ = func.replace("'", "\\'")
        else:
            func_ = func
        values = (
            f"(CAST(unhex('{hex_repr}'), 'AggregateFunction({func_}, {datatypes})'))"
        )

    with Then("I check the result"):
        if "alias" in short_name:
            short_name = short_name.replace("_alias", "")
        if is_parametric:
            correct_form = func.replace(short_name, short_name + "Merge")
        else:
            correct_form = func + "Merge"

        self.context.compare_json_values = True
        self.context.snapshot_id = self.context.snapshot_id.replace(
            f"{combinator}Merge", ""
        )
        if "group_by" in snapshot_name:
            skip("Needs to be fixed")
        if "some_negative_values" in snapshot_name:
            skip("Needs to be fixed")

        execute_query(
            f"SELECT {correct_form}{values}",
            snapshot_name=snapshot_name,
        )


@TestScenario
def merge(self, scenario, short_name, is_parametric, combinator="ArgMin"):
    """Check -Merge combinator function."""

    snapshot_id, func = scenario()
    snapshot_id = snapshot_id.lower().replace(
        "merge", "state_const_expr"
    )  # need state from snapshots of -State combinator
    snapshot_path = os.path.join(
        current_dir(), "snapshots", f"steps.py.{snapshot_id}.{current_cpu()}.snapshot"
    )

    if not os.path.exists(snapshot_path):
        xfail(reason=f"no snapshot found {snapshot_path}")

    func = func.replace(short_name, short_name + combinator)
    short_name = short_name
    snapshot_module = SourceFileLoader(func, snapshot_path).load_module()  # add UUID

    snapshot_attrs = {
        k: v for k, v in vars(snapshot_module).items() if not k.startswith("__")
    }

    with Pool(3) as executor:
        for key, value in snapshot_attrs.items():
            with By("I break single snapshot value into lines"):
                data = value.strip().split("\n")

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

                with By("I create snapshot name for the -Merge combinator"):
                    if (
                        hex_repr is not None
                        and len(hex_repr) > 0
                        and len(datatypes) > 0
                    ):
                        note(key)
                        name = key.replace(
                            f"{combinator}StateCombinator_constant_expression_{short_name}{combinator}State_const_expr",
                            f"{short_name}",
                        )
                        scenario_name = f"{func.replace(combinator, '')}"
                        Scenario(
                            scenario_name,
                            test=check,
                            parallel=True,
                            executor=executor,
                        )(
                            func=func,
                            datatypes=datatypes,
                            hex_repr=hex_repr,
                            snapshot_name=name,
                            is_low_cardinality="LowCardinality" in datatypes,
                            short_name=short_name + combinator,
                            is_parametric=is_parametric,
                            combinator=combinator,
                        )
        join()


@TestFeature
@Name("ArgMinMergeCombinator_constant_expression")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Merge("1.0"))
def feature(self):
    """Check aggregate functions with combination of `-Merge` and -ArgMin combinators."""
    not_implemented = [
        "windowFunnel",
        "quantileDeterministic",
        "quantilesDeterministic",
        "stochasticLinearRegression",
        "stochasticLogisticRegression",
        "sumMap",
        "maxMap",
        "minMap",
        "sumMapFiltered",  # parameters of different type
        "sumMapFilteredWithOverflow",  # parameters of different type
        "quantileTDigestWeighted",
        "singleValueOrNull",  # problem on 22.8
        "sequenceCount",
        "sequenceMatch",
        "sequenceNextNode",
    ]

    test_funcs = [i for i in aggregate_functions]
    for i in not_implemented:
        if i in test_funcs:
            test_funcs.remove(i)

    with Pool(10) as executor:
        for name in test_funcs:
            try:
                scenario = load(f"aggregate_functions.tests.{name}", "scenario")
            except ModuleNotFoundError as e:
                with Scenario(f"{name}Merge"):
                    skip(reason=f"{name}State() test is not implemented")
            else:
                is_parametric = False
                if name in parametric:
                    is_parametric = True
                Scenario(
                    f"{name}ArgMinMerge",
                    description=f"Get snapshot name to retrieve state of {name} function",
                    test=merge,
                    parallel=True,
                    executor=executor,
                )(scenario=scenario, short_name=name, is_parametric=is_parametric)
        join()
