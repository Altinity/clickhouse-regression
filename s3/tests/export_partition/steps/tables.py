from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid


@TestStep(Given)
def create_distributed_table(
    self,
    cluster,
    local_table_name,
    distributed_table_name=None,
    sharding_key="rand()",
    node=None,
):
    """Create a Distributed table that points to local tables on a cluster."""
    if node is None:
        node = self.context.node

    if distributed_table_name is None:
        distributed_table_name = f"distributed_{getuid()}"

    node.query(
        f"""
        CREATE TABLE {distributed_table_name} AS {local_table_name}
        ENGINE = Distributed({cluster}, default, {local_table_name}, {sharding_key})
        """,
        exitcode=0,
        steps=True,
    )

    return distributed_table_name


@TestStep(When)
def wait_for_distributed_table_data(self, table_name, expected_count, node=None):
    """Wait for data to be distributed to all shards in a Distributed table."""
    if node is None:
        node = self.context.node

    for attempt in retries(timeout=60, delay=1):
        with attempt:
            result = node.query(
                f"SELECT count() FROM {table_name}",
                exitcode=0,
                steps=True,
            )
            assert int(result.output.strip()) == expected_count, error()
