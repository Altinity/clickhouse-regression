#!/usr/bin/env python3
import sys
from testflows.core import *

append_path(sys.path, ".")

from helpers.argparser import argparser

ffails = {
    "s3": (
        Skip,
        "Required inputs are not specified, must be launch seperately.",
    ),
    "tiered_storage": (
        Skip,
        "Required inputs are not specified, must be launch seperately.",
    ),
}

@TestModule
@Name("clickhouse")
@FFails(ffails)
@ArgumentParser(argparser)
def regression(self, local, clickhouse_binary_path, clickhouse_version, stress=None):
    """ClickHouse regression."""
    args = {
        "local": local,
        "clickhouse_binary_path": clickhouse_binary_path,
        "clickhouse_version": clickhouse_version,
        "stress": stress,
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
                test=load("aggregate_functions.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("atomic_inserts.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("base58.regression", "regression"),
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
                test=load("map_type.regression", "regression"),
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
                test=load("s3.regression", "regression"),
                parallel=True,
                executor=pool,
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
        finally:
            join()


if main():
    regression()
