#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser
from session_timezone.requirements import *
from session_timezone.common import *


xfails = {

}

ffails = {
}


@TestModule
@Name("session timezone")
@ArgumentParser(argparser)
@Specifications(SRS037_ClickHouse_Session_Timezone)
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone("1.0"))
@XFails(xfails)
@FFails(ffails)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=False,
):
    """ClickHouse Session Timezone regression module."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
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

    with Cluster(
        local,
        clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(
            current_dir(), "session_timezone_env"
        ),
    ) as cluster:
        self.context.cluster = cluster

        if check_clickhouse_version("<23.5")(self):
            skip(reason="only supported on ClickHouse version >= 23.5")

        Feature(run=load("session_timezone.tests.sanity", "feature"))
        Feature(run=load("session_timezone.tests.basic", "feature"))


if main():
    regression()
