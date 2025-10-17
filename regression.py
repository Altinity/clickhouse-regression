#!/usr/bin/env python3
import sys
from testflows.core import *

append_path(sys.path, ".")

from helpers.argparser import argparser_s3, CaptureClusterArgs, CaptureS3Args

ffails = {
    "tiered_storage": (
        Skip,
        "Required inputs are not specified, must be launch separately.",
    ),
}


@TestModule
@Name("clickhouse")
@FFails(ffails)
@ArgumentParser(argparser_s3)
@CaptureClusterArgs
@CaptureS3Args
def regression(
    self,
    cluster_args,
    s3_args,
    clickhouse_version,
    use_specific_version=None,
    stress=None,
    with_analyzer=False,
):
    """ClickHouse regression."""
    args = {
        **cluster_args,
        "clickhouse_version": clickhouse_version,
        "stress": stress,
        "with_analyzer": with_analyzer,
    }

    s3_args = {
        **cluster_args,
        **s3_args,
        "clickhouse_version": clickhouse_version,
        "stress": stress,
        "with_analyzer": with_analyzer,
    }

    # FIXME: Remove use_specific_version and move it to the test level
    if use_specific_version is None:
        use_specific_version = (
            "docker://altinity/clickhouse-server:23.3.13.7.altinitytest"
        )

    alter_args = {
        **cluster_args,
        "clickhouse_version": clickhouse_version,
        "stress": stress,
        "with_analyzer": with_analyzer,
        "use_specific_version": use_specific_version,
    }

    self.context.stress = stress

    with Pool(4) as pool:
        try:
            Feature(
                test=load("aes_encryption.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("alter.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**alter_args)
            Feature(
                test=load("aggregate_functions.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("atomic_insert.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("base_58.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("clickhouse_keeper.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("datetime64_extended_range.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("disk_level_encryption.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("dns.regression", "regression"), parallel=True, executor=pool
            )(**args)
            Feature(
                test=load("example.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("extended_precision_data_types.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("functions.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("kafka.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("kerberos.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("key_value.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("ldap.regression", "regression"), parallel=True, executor=pool
            )(**args)
            Feature(
                test=load("lightweight_delete.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("memory.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("data_types.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("part_moves_between_shards.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("rbac.regression", "regression"), parallel=True, executor=pool
            )(**args)
            Feature(
                test=load("selects.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("ssl_server.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("tiered_storage.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("window_functions.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("s3.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**s3_args)
        finally:
            join()


if main():
    regression()
