#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "../..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as argparser_base

def argparser(parser):
    """Default argument for regressions."""
    argparser_base(parser)

    parser.add_argument(
        "--s3-storage",
        action="store_true",
        help="Specify whether to use s3 storage for merge tree tables.",
        default=False,
        dest="s3",
    )

    parser.add_argument(
        "---replicated-database",
        action="store_true",
        help="Run tests on a Replicated database.",
        default=False,
        dest="replicated_database",
    )

xfails = {}

xflags = {}

ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("external tests")
def regression(self, local, clickhouse_binary_path, clickhouse_version, s3, replicated_database, stress=None):
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
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:
        node = cluster.node("clickhouse1")

        with Given("set ENV variables for install.sh",
            description=f"USE_POLYMORPHIC_PARTS=1, USE_S3_STORAGE_FOR_MERGE_TREE={s3}, USE_DATABASE_REPLICATED={replicated_database}"): #
            node.command(f"export USE_POLYMORPHIC_PARTS=1;  export USE_S3_STORAGE_FOR_MERGE_TREE={s3}; export USE_DATABASE_REPLICATED={replicated_database}") #export EXPORT_S3_STORAGE_POLICIES=False;

        with And("update configs"):
            node.command("/functional/config/install.sh")

        with And("change the listening port in listen.xml from :: to 0.0.0.0"):
            node.command("sed -i 's/::/0.0.0.0/g' /etc/clickhouse-server/config.d/listen.xml")

        with And("setup minio"):
            node.command("/functional/setup_minio.sh")

        if replicated_database:
            with And("launch two other clickhouse server for replication"):
                node.command("/usr/bin/clickhouse server --config /etc/clickhouse-server1/config.xml --daemon \
                    -- --path /var/lib/clickhouse1/ --logger.stderr /var/log/clickhouse-server/stderr1.log \
                    --logger.log /var/log/clickhouse-server/clickhouse-server1.log --logger.errorlog /var/log/clickhouse-server/clickhouse-server1.err.log \
                    --tcp_port 19000 --tcp_port_secure 19440 --http_port 18123 --https_port 18443 --interserver_http_port 19009 --tcp_with_proxy_port 19010 \
                    --mysql_port 19004 --postgresql_port 19005 \
                    --keeper_server.tcp_port 19181 --keeper_server.server_id 2")

                node.command("/usr/bin/clickhouse server --config /etc/clickhouse-server2/config.xml --daemon \
                    -- --path /var/lib/clickhouse2/ --logger.stderr /var/log/clickhouse-server/stderr2.log \
                    --logger.log /var/log/clickhouse-server/clickhouse-server2.log --logger.errorlog /var/log/clickhouse-server/clickhouse-server2.err.log \
                    --tcp_port 29000 --tcp_port_secure 29440 --http_port 28123 --https_port 28443 --interserver_http_port 29009 --tcp_with_proxy_port 29010 \
                    --mysql_port 29004 --postgresql_port 29005 \
                    --keeper_server.tcp_port 29181 --keeper_server.server_id 3")

        with And("restart"):
            node.restart_clickhouse()

        with Suite("stateless"):
            with Given("get all stateless tests", description="test endings: .sql, .sh, .sql.j2, .py, .expect"):
                output = node.command("ls --color=none /functional/queries/0_stateless/*{.expect,.py,.sh,.sql,.sql.j2}").output
                stateless_tests = output.replace("\n", "").split("/functional/queries/0_stateless/")[1:]

            for test in stateless_tests:
                with Scenario(test):
                    cmd = f"/functional/clickhouse-test {test} --output /reports/{test.split('.')[0]} --shard --zookeeper"
                    if s3:
                        cmd += "--s3-storage"
                    if replicated_database:
                        cmd += "--replicated-database"
                    node.command(
                        cmd,
                        timeout=3600,
                        message="1 tests passed",
                    )

        with Suite("stateful"):
            with Given("get all stateful tests", description="test endings: .sql, .sh, .sql.j2, .py, .expect"):
                output = node.command("ls --color=none /functional/queries/1_stateful/*{.expect,.py,.sh,.sql,.sql.j2}").output
                stateful_tests = output.replace("\n", "").split("/functional/queries/1_stateful/")[1:]

            for test in stateful_tests:
                with Scenario(test):
                    cmd = f"/functional/clickhouse-test {test} --output /reports/{test.split('.')[0]} --shard --zookeeper"
                    if s3:
                        cmd += "--s3-storage"
                    if replicated_database:
                        cmd += "--replicated-database"
                    node.command(
                        cmd,
                        timeout=3600,
                        message="1 tests passed",
                    )

if main():
    regression()
