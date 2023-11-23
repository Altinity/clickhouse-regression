#!/usr/bin/env python3
import sys

from testflows.core import *

append_path(sys.path, "../../..")


@TestFeature
@Name("replace partition")
def feature(self):
    """Run features from the replace partition suite."""
    with Pool(2) as pool:
        Feature(
            run=load("alter.table.replace_partition.partition_types", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.replace_partition.rbac", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.replace_partition.data_integrity", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.replace_partition.prohibited_actions", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.replace_partition.temporary_table", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.replace_partition.engines", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.replace_partition.concurrent_actions", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load(
                "alter.table.replace_partition.concurrent_replace_partitions", "feature"
            )
        )
        Feature(
            run=load(
                "alter.table.replace_partition.concurrent_merges_and_mutations",
                "feature",
            )
        )
        Feature(
            run=load(
                "alter.table.replace_partition.storage",
                "feature",
            )
        )
        Feature(
            run=load(
                "alter.table.replace_partition.corrupted_partitions",
                "feature",
            )
        )
        join()
