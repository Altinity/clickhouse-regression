#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser
from helpers.common import check_clickhouse_version
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
    )
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
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=None,
):
    """ClickHouse disk level encryption regression."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
        "cmd-clickhouse": ("clickhouse_cmd",),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    from platform import processor as current_cpu

    folder_name = os.path.basename(current_dir())
    if current_cpu() == "aarch64":
        env = f"{folder_name}_env_arm64"
    else:
        env = f"{folder_name}_env"

    if check_clickhouse_version("<21.9")(self):
        skip(reason="only supported on ClickHouse version >= 21.9")

    with Cluster(
        local,
        clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:
        self.context.cluster = cluster

        Feature(run=load("disk_level_encryption.tests.memory", "feature"))
        Feature(run=load("disk_level_encryption.tests.column_ttl", "feature"))
        Feature(run=load("disk_level_encryption.tests.encrypted_disk", "feature"))
        Feature(
            run=load("disk_level_encryption.tests.application_of_changes", "feature")
        )
        Feature(
            run=load("disk_level_encryption.tests.wide_access_permission", "feature")
        )
        Feature(run=load("disk_level_encryption.tests.no_access_rights", "feature"))
        Feature(run=load("disk_level_encryption.tests.new_directories", "feature"))
        Feature(run=load("disk_level_encryption.tests.invalid_disk", "feature"))
        Feature(run=load("disk_level_encryption.tests.distributed_table", "feature"))
        Feature(run=load("disk_level_encryption.tests.replicated_table", "feature"))
        Feature(run=load("disk_level_encryption.tests.invalid_key_size", "feature"))
        Feature(
            run=load("disk_level_encryption.tests.encryption_algorithms", "feature")
        )
        Feature(
            run=load("disk_level_encryption.tests.comparable_performance", "feature")
        )
        Feature(
            run=load("disk_level_encryption.tests.comparable_part_sizes", "feature")
        )
        Feature(
            run=load("disk_level_encryption.tests.wide_and_compact_formats", "feature")
        )
        Feature(run=load("disk_level_encryption.tests.multi_disk_volume", "feature"))
        Feature(run=load("disk_level_encryption.tests.multi_volume_policy", "feature"))
        Feature(run=load("disk_level_encryption.tests.missing_key", "feature"))
        Feature(
            run=load(
                "disk_level_encryption.tests.merge_parts_with_different_keys", "feature"
            )
        )
        Feature(
            run=load("disk_level_encryption.tests.invalid_current_key_id", "feature")
        )
        Feature(run=load("disk_level_encryption.tests.multiple_keys", "feature"))
        Feature(run=load("disk_level_encryption.tests.default_path", "feature"))
        Feature(run=load("disk_level_encryption.tests.valid_path", "feature"))
        Feature(run=load("disk_level_encryption.tests.invalid_path", "feature"))
        Feature(run=load("disk_level_encryption.tests.sanity", "feature"))
        Feature(run=load("disk_level_encryption.tests.operations.feature", "feature"))
        Feature(run=load("disk_level_encryption.tests.key_formats", "feature"))
        Feature(run=load("disk_level_encryption.tests.encryption_at_rest", "feature"))


if main():
    regression()
