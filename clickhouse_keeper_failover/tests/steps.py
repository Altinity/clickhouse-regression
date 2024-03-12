#!/usr/bin/env python3
import re
import json

from testflows.core import *
from testflows.asserts import error


@TestStep
def get_external_ports(self, internal_port):
    port_regex = r"(keeper-\d).*:(\d+)->" + str(internal_port)

    cluster = self.context.cluster
    r = cluster.command(None, f"{cluster.docker_compose} ps")

    port_map = {}

    for match in re.finditer(port_regex, r.output):
        name, port = match.groups()
        port_map[name] = port

    assert port_map != {}

    return port_map


@TestStep
def get_current_leader(self):
    cluster = self.context.cluster

    for node, port in self.context.keeper_ports.items():
        r = cluster.command(None, f"curl 'http://localhost:{port}/ready'")
        is_leader = json.loads(r.output)["details"]["role"] == "leader"
        if is_leader:
            return node


@TestStep
def get_node_role(self, node):
    cluster = self.context.cluster

    port = self.context.keeper_ports[node.name]
    r = cluster.command(None, f"curl 'http://localhost:{port}/ready'")
    return json.loads(r.output)["details"]["role"]


@TestStep
def keeper_query(self, node, query):
    return node.command(f'clickhouse-keeper-client -q "{query}"')


@TestStep
def set_keeper_config(self, config_file_name, nodes=None, restart=False):
    assert not (nodes is None and restart), "Nodes to restart must be specified"

    config_dir = current_dir() + "/../configs/keeper/config/"
    source_path = "/etc/clickhouse-keeper-configs/"
    dest_file = config_dir + "keeper_config.xml"

    source_file = source_path + config_file_name

    cluster = self.context.cluster
    cluster.command(None, f"ln -s -f {source_file} {dest_file}", exitcode=0)

    if restart:
        for node in nodes:
            node.restart()


@TestStep
def check_logs(self, node, message, tail=30, use_compose=False):
    """
    Check for a given message in the server logs

    use_compose is a workaround for containers that were started with `run`
    """
    cmd = f'tail -n {tail} /var/log/clickhouse-keeper/clickhouse-keeper.log | grep "{message}"'
    if not use_compose:
        return node.command(cmd, exitcode=0)
    else:
        cluster = self.context.cluster
        cluster.command(
            None,
            f"{cluster.docker_compose} run {node.name} {cmd}",
            exitcode=0,
            steps=False,
        )
