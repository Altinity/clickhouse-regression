#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.common import check_clickhouse_version, experimental_analyzer
from disk_level_encryption.requirements import *


xfails = {
    "memory disk/memory disk": [(Fail, "not supported")],
    "wide access permission/wide permission": [(Fail, "not implemented")],
    "multi volume policy": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/pull/30664")
    ],
    "encryption at rest/corner case check": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/38381")
    ],
}

ffails = {
    "default path/default path": (
        XError,
        "https://github.com/ClickHouse/ClickHouse/issues/29072",
    ),
    "memory disk": (
        Skip,
        "not implemented in versions >= 23",
        check_clickhouse_version(">=23"),
    ),
}

xflags = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("disk level encryption")
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption("1.0"))
@Specifications(QA_SRS025_ClickHouse_Disk_Level_Encryption)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    allow_vfs=False,
    with_analyzer=False,
):
    """ClickHouse disk level encryption regression."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
        "cmd-clickhouse": ("clickhouse_cmd",),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    if check_clickhouse_version("<21.9")(self):
        skip(reason="only supported on ClickHouse version >= 21.9")

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Feature(run=load("disk_level_encryption.tests.memory", "feature"))
    Feature(run=load("disk_level_encryption.tests.column_ttl", "feature"))
    Feature(run=load("disk_level_encryption.tests.encrypted_disk", "feature"))
    Feature(run=load("disk_level_encryption.tests.application_of_changes", "feature"))
    Feature(run=load("disk_level_encryption.tests.wide_access_permission", "feature"))
    Feature(run=load("disk_level_encryption.tests.no_access_rights", "feature"))
    Feature(run=load("disk_level_encryption.tests.new_directories", "feature"))
    Feature(run=load("disk_level_encryption.tests.invalid_disk", "feature"))
    Feature(run=load("disk_level_encryption.tests.distributed_table", "feature"))
    Feature(run=load("disk_level_encryption.tests.replicated_table", "feature"))
    Feature(run=load("disk_level_encryption.tests.invalid_key_size", "feature"))
    Feature(run=load("disk_level_encryption.tests.encryption_algorithms", "feature"))
    Feature(run=load("disk_level_encryption.tests.comparable_performance", "feature"))
    Feature(run=load("disk_level_encryption.tests.comparable_part_sizes", "feature"))
    Feature(run=load("disk_level_encryption.tests.wide_and_compact_formats", "feature"))
    Feature(run=load("disk_level_encryption.tests.multi_disk_volume", "feature"))
    Feature(run=load("disk_level_encryption.tests.multi_volume_policy", "feature"))
    Feature(run=load("disk_level_encryption.tests.missing_key", "feature"))
    Feature(
        run=load(
            "disk_level_encryption.tests.merge_parts_with_different_keys", "feature"
        )
    )
    Feature(run=load("disk_level_encryption.tests.invalid_current_key_id", "feature"))
    Feature(run=load("disk_level_encryption.tests.multiple_keys", "feature"))
    Feature(run=load("disk_level_encryption.tests.default_path", "feature"))
    Feature(run=load("disk_level_encryption.tests.valid_path", "feature"))
    Feature(run=load("disk_level_encryption.tests.invalid_path", "feature"))
    Feature(run=load("disk_level_encryption.tests.operations.feature", "feature"))
    Feature(run=load("disk_level_encryption.tests.key_formats", "feature"))
    Feature(run=load("disk_level_encryption.tests.encryption_at_rest", "feature"))


if main():
    regression()
