import time

from testflows.core import *
from helpers.common import create_xml_config_content, add_config
from helpers.common import getuid, instrument_clickhouse_server_log


@TestStep(Given)
def instrument_cluster_nodes(self, test, cluster_nodes, always_dump=True):
    """Instrument logs on cluster nodes."""
    for name in cluster_nodes:
        instrument_clickhouse_server_log(
            node=self.context.cluster.node(name), test=test, always_dump=always_dump
        )
