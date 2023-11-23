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
def check(
    self, func, datatypes, hex_repr, snapshot_name, short_name, is_low_cardinality=False
):
    if is_low_cardinality:
        self.context.node.query(f"SET allow_suspicious_low_cardinality_types = 1")

    with Given("I create temporary table"):
        datatype_name = f"AggregateFunction({func}, {datatypes})"
        self.context.table = create_table(
            engine="MergeTree",
            columns=[Column(name="state", datatype=DataType(name=datatype_name))],
            order_by="tuple()",
        )

    with When("I insert data in temporary table"):
        if is_low_cardinality:
            values = (
                f"(CAST(unhex('{hex_repr}'), 'AggregateFunction({func}, {datatypes})'))"
            )
        else:
            values = f"(unhex('{hex_repr}'))"
        self.context.node.query(
            f"INSERT INTO {self.context.table.name} VALUES {values}"
        )

    with Then("I check the result"):
        correct_form = func.replace(short_name, short_name + "Merge")
        execute_query(
            f"SELECT {correct_form}(state) FROM {self.context.table.name}",
            snapshot_name=snapshot_name,
        )


@TestScenario
def merge(self, scenario, short_name):
    snapshot_id, func = scenario()
    snapshot_id = snapshot_id.lower().replace(
        "merge", "state"
    )  # need state from snapshots of -State combinator
    snapshot_path = os.path.join(
        current_dir(), "snapshots", f"steps.py.{snapshot_id}.{current_cpu()}.snapshot"
    )

    if not os.path.exists(snapshot_path):
        xfail(reason=f"no snapshot found {snapshot_path}")

    snapshot_module = SourceFileLoader(func, snapshot_path).load_module()  # add UUID
    snapshot_attrs = {
        k: v for k, v in vars(snapshot_module).items() if not k.startswith("__")
    }

    with Pool(3) as executor:
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

                with By("I create snapshot name for the -Merge combinator"):
                    if (
                        hex_repr is not None
                        and len(hex_repr) > 0
                        and len(datatypes) > 0
                    ):
                        name = (
                            key.replace("state_", "merge_").replace("State", "Merge")
                            + f"_{idx}"
                        )
                        idx += 1
                        Check(f"name", test=check, parallel=True, executor=executor)(
                            func=func,
                            datatypes=datatypes,
                            hex_repr=hex_repr,
                            snapshot_name=name,
                            is_low_cardinality="LowCardinality" in datatypes,
                            short_name=short_name,
                        )
        join()


@TestFeature
@Name("merge")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_Merge("1.0"))
def feature(self):
    """Check aggregate functions `-Merge` combinator."""
    not_implemented = [
        "mannWhitneyUTest",
        "quantileDeterministic",  # two arguments
        "quantilesDeterministic",
        "stochasticLinearRegression",
        "stochasticLogisticRegression",
        "sumMap",
        "maxMap",
        "minMap",
        "quantileTDigestWeighted",
        "uniq",
        "uniqHLL12",  # problem on 22.8 and 23.8
        "singleValueOrNull",  # problem on 22.8
        "topKWeighted",  # fails on 23.3
        "uniqExact",  # problem on 23.8 aarch
        "welchTTest",  # problem on 22.8 aarch
        "studentTTest",
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
                Scenario(
                    f"{name}Merge",
                    description=f"Get snapshot name to retrieve state of {name} function",
                    test=merge,
                    parallel=True,
                    executor=executor,
                )(scenario=scenario, short_name=name)
        join()
