#!/usr/bin/env python3
import sys

from testflows.core import *

append_path(sys.path, "../../..")


@TestFeature
@Name("replace partition")
def feature(self):
    """Run features from the replace partition suite."""
    Feature(run=load("alter.table.replace_partition.partition_types", "feature"))
    Feature(run=load("alter.table.replace_partition.rbac", "feature"))
    Feature(run=load("alter.table.replace_partition.data_integrity", "feature"))
    Feature(run=load("alter.table.replace_partition.prohibited_actions", "feature"))
    Feature(run=load("alter.table.replace_partition.temporary_table", "feature"))
    Feature(run=load("alter.table.replace_partition.engines", "feature"))
