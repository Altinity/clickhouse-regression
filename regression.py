#!/usr/bin/env python3
import sys
from testflows.core import *

append_path(sys.path, ".")

from s3.regression import argparser


ffails = {
    "tiered_storage": (
        Skip,
        "Required inputs are not specified, must be launch seperately.",
    ),
}


@TestModule
@Name("clickhouse")
@FFails(ffails)
@ArgumentParser(argparser)
def regression(
    self,
    local,
    clickhouse_version,
    clickhouse_binary_path,
    collect_service_logs,
    storages,
    minio_uri,
    gcs_uri,
    aws_s3_region,
    aws_s3_bucket,
    minio_root_user,
    minio_root_password,
    aws_s3_access_key,
    aws_s3_key_id,
    gcs_key_secret,
    gcs_key_id,
    node="clickhouse1",
    stress=None,
    allow_vfs=False,
    with_analyzer=False,
):
    """ClickHouse regression."""
    args = {
        "local": local,
        "clickhouse_binary_path": clickhouse_binary_path,
        "clickhouse_version": clickhouse_version,
        "stress": stress,
        "collect_service_logs": collect_service_logs,
        "with_analyzer": with_analyzer,
    }

    s3_args = {
        "local": local,
        "clickhouse_binary_path": clickhouse_binary_path,
        "clickhouse_version": clickhouse_version,
        "stress": stress,
        "collect_service_logs": collect_service_logs,
        "with_analyzer": with_analyzer,
        "storages": storages,
        "minio_uri": minio_uri,
        "gcs_uri": gcs_uri,
        "aws_s3_region": aws_s3_region,
        "aws_s3_bucket": aws_s3_bucket,
        "minio_root_user": minio_root_user,
        "minio_root_password": minio_root_password,
        "aws_s3_access_key": aws_s3_access_key,
        "aws_s3_key_id": aws_s3_key_id,
        "gcs_key_secret": gcs_key_secret,
        "gcs_key_id": gcs_key_id,
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
            )(**args)
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
