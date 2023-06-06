from testflows.core import *
from helpers.common import getuid


@TestStep
def clickhouse_local(
    self, query="select timezone()", node=None, timezone="UTC", message=""
):
    """Step to enable clickhouse local query"""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When("I make clickhouse local query"):
        node.cmd(f'TZ={timezone} clickhouse local -q  "{query}"', message=f"{message}")
