from testflows.core import *
from helpers.common import check_clickhouse_version, getuid


@TestStep
def clickhouse_local(
    self,
    query="select timezone()",
    node=None,
    timezone="UTC",
    message="",
    exitcode=0,
):
    """Step to enable clickhouse local query"""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    # From 26.11.1.876, clickhouse-local keeps its database in the home
    # directory, so a later invocation sees tables created by an earlier one.
    # --tmp is the previous per-process directory. Earlier 26.11 builds reject it.
    tmp = ""
    if check_clickhouse_version(">=26.11.1.876")(self):
        tmp = " --tmp"

    with When("I make clickhouse local query"):
        node.command(
            f'TZ={timezone} clickhouse local{tmp} -q  "{query}" --multiquery',
            message=f"{message}",
            exitcode=exitcode,
        )
