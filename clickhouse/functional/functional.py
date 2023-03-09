#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "../..")

from helpers.cluster import Cluster
from helpers.argparser import argparser

xfails = {}

xflags = {}

ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("functional")
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=None,
):
    """Run the ClickHouse functional (stateless and stateful) tests."""
    nodes = {"clickhouse": ("clickhouse1",)}
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
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:
        node = cluster.node("clickhouse1")

        with Given("update configs"):
            node.command("/functional/config/install.sh")

        with And("change the listening port in listen.xml from :: to 0.0.0.0"):
            node.command(
                "sed -i 's/::/0.0.0.0/g' /etc/clickhouse-server/config.d/listen.xml"
            )

        with And("change the host from localhost to zookeeper in zookeeper.xml"):
            node.command(
                "sed -i 's/localhost/zookeeper/g' /etc/clickhouse-server/config.d/zookeeper.xml"
            )

        with And("restart"):
            node.restart_clickhouse()

        with Suite("stateless"):
            with Given(
                "get all stateless tests",
                description="test endings: .sql, .sh, .sql.j2, .py, .expect",
            ):
                output = node.command(
                    "ls --color=none /functional/queries/0_stateless/*{.expect,.py,.sh,.sql,.sql.j2}"
                ).output
                stateless_tests = output.replace("\n", "").split(
                    "/functional/queries/0_stateless/"
                )[1:]

            for test in stateless_tests:
                with Scenario(test):
                    cmd = f"/functional/clickhouse-test {test} --output /reports/{test.split('.')[0]} --shard --zookeeper"
                    node.command(
                        cmd,
                        timeout=3600,
                        message="1 tests passed",
                    )

        with Suite("stateful"):
            with Given(
                "get all stateful tests",
                description="test endings: .sql, .sh, .sql.j2, .py, .expect",
            ):
                output = node.command(
                    "ls --color=none /functional/queries/1_stateful/*{.expect,.py,.sh,.sql,.sql.j2}"
                ).output
                stateful_tests = output.replace("\n", "").split(
                    "/functional/queries/1_stateful/"
                )[1:]

            for test in stateful_tests:
                with Scenario(test):
                    node.command(
                        cmd,
                        timeout=3600,
                        message="1 tests passed",
                    )


if main():
    regression()
