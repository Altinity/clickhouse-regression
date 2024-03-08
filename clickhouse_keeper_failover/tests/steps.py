#!/usr/bin/env python3
import re
import json

from testflows.core import *


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
def set_keeper_config(self, nodes, config_file_name):
    source_path = "/etc/clickhouse-keeper-configs/"
    dest_file = "/etc/clickhouse-keeper/keeper_config.xml"

    source_file = source_path + config_file_name

    cmd = f"ln -s -f {source_file} {dest_file}"

    for node in nodes:
        node.command(
            "echo '||||||INSERTING NEW CONFIG' >> /var/log/clickhouse-keeper/clickhouse-keeper.log"
        )
        node.command(cmd)
