#!/usr/bin/env python3
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.argparser import argparser


@TestModule
@Name("ldap")
@ArgumentParser(argparser)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    keeper_binary_path=None,
    zookeeper_version=None,
    stress=None,
    allow_vfs=False,
    allow_experimental_analyzer=False,
):
    """ClickHouse LDAP integration regression module."""
    args = {
        "local": local,
        "clickhouse_binary_path": clickhouse_binary_path,
        "keeper_binary_path": keeper_binary_path,
        "zookeeper_version": zookeeper_version,
        "clickhouse_version": clickhouse_version,
        "collect_service_logs": collect_service_logs,
        "allow_vfs": allow_vfs,
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Pool(3) as pool:
        try:
            Feature(
                test=load("ldap.authentication.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("ldap.external_user_directory.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
            Feature(
                test=load("ldap.role_mapping.regression", "regression"),
                parallel=True,
                executor=pool,
            )(**args)
        finally:
            join()


if main():
    regression()
