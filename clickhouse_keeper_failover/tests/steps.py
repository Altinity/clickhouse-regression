#!/usr/bin/env python3
import re
import json

from testflows.core import *
from testflows.asserts import error


@TestStep
def get_external_ports(self, internal_port):
    """Get the mapping of external ports per node for a given internal port."""
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
    """Query keeper nodes until one responds claiming to be leader."""
    cluster = self.context.cluster

    for node, port in self.context.keeper_ports.items():
        r = cluster.command(
            None, f"curl 'http://localhost:{port}/ready'", no_checks=True
        )
        if r.exitcode != 0:
            continue

        is_leader = json.loads(r.output)["details"]["role"] == "leader"
        if is_leader:
            return node

    fail("did not receive a leader response from any node")


@TestStep
def get_node_role(self, node):
    """Get the keeper role of a given node."""
    cluster = self.context.cluster

    port = self.context.keeper_ports[node.name]
    r = cluster.command(None, f"curl 'http://localhost:{port}/ready'")
    return json.loads(r.output)["details"]["role"]


@TestStep
def cluster_command_workaround(self, node_name, cmd):
    """
    Node.command isn't compatible with the method used to activate recovery mode.
    """
    cluster = self.context.cluster
    return cluster.command(
        None,
        f"{cluster.docker_compose} exec {node_name} {cmd}",
        exitcode=0,
        steps=False,
    )


@TestStep
def keeper_query(self, node, query):
    """Send a query to keeper client."""
    cmd = f'clickhouse-keeper-client -q "{query}"'
    return node.command(cmd)



@TestStep
def set_keeper_config(self, config_file_name, nodes=None, restart=False):
    """Swaps the config file."""
    assert not (nodes is None and restart), "Nodes to restart must be specified"

    config_dir = current_dir() + "/../configs/keeper/config/"
    source_path = "/etc/clickhouse-keeper-configs/"
    dest_file = config_dir + "keeper_config.xml"
    source_file = source_path + config_file_name

    cluster = self.context.cluster

    with By("I return early if the link is already set"):
        r = cluster.command(None, f"ls -l {dest_file}", no_checks=True)
        if source_file in r.output:
            return

    with And("I replace the link with the new target"):
        cluster.command(None, f"ln -s -f {source_file} {dest_file}", exitcode=0)

    if restart:
        with By("I restart all nodes"):
            for node in nodes:
                node.restart_keeper()


@TestStep
def check_logs(self, node, message, tail=30):
    """
    Check for a given message in the server logs
    """
    cmd = f'tail -n {tail} /var/log/clickhouse-keeper/clickhouse-keeper.log | grep "{message}"'
    return node.command(cmd, exitcode=0)

