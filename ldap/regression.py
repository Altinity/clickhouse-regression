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
    clickhouse_path,
    clickhouse_version,
    collect_service_logs,
    keeper_path=None,
    zookeeper_version=None,
    use_keeper=False,
    stress=None,
    with_analyzer=False,
):
    """ClickHouse LDAP integration regression module."""
    args = {
        "local": local,
        "clickhouse_path": clickhouse_path,
        "keeper_path": keeper_path,
        "use_keeper": use_keeper,
        "zookeeper_version": zookeeper_version,
        "clickhouse_version": clickhouse_version,
        "collect_service_logs": collect_service_logs,
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
