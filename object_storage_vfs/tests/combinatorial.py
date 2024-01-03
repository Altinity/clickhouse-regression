#!/usr/bin/env python3
from testflows.core import *
from testflows.combinatorics import CoveringArray

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *

table_configurations = {
    "engine": [
        "MergeTree",
        "ReplacingMergeTree",
        "CollapsingMergeTree",
        "VersionedCollapsingMerge",
        "AggregatingMergeTree",
        "SummingMergeTree",
    ],
    "replicated": [True, False],
    "n_cols": [10, 100, 1000, 10000],
    "storage_policy": ["external", "external_tiered"],
}


@TestOutline(Combination)
def test_combination(
    self,
    engine: str,
    replicated: bool,
    n_cols: int,
    storage_policy: str,
    operations: list = [],
):
    pass


@TestScenario
def check_table_combinations(self):
    for table_config in CoveringArray(table_configurations, strength=2):
        title = ",".join([f"{k}={v}" for k, v in table_config.items()])
        Combination(title, test=test_combination)(**table_config)


@TestFeature
@Name("combinatorial")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS("1.0"))
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
