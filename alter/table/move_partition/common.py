from testflows.core.name import basename
from testflows.asserts import values, error, snapshot

from helpers.common import *

def execute_query(
    sql,
    expected=None,
    exitcode=None,
    message=None,
    no_checks=False,
    snapshot_name=None,
    format="TabSeparatedWithNames",
    node=None,
    path=None,
):
    """Execute SQL query and compare the output to the snapshot."""
    if snapshot_name is None:
        snapshot_name="/alter/table/move_partition" + current().name

    if node is None:
        node = current().context.node

    with When("I execute query", description=sql):
        r = node.query(
            sql + " FORMAT " + format,
            exitcode=exitcode,
            message=message,
            no_checks=no_checks,
        )
        if no_checks:
            return r

    if message is None:
        if expected is not None:
            with Then("I check output against expected"):
                assert r.output.strip() == expected, error()
        else:
            with Then("I check output against snapshot"):
                with values() as that:
                    for attempt in retries(timeout=30, delay=5):
                        with attempt:
                            assert that(
                                snapshot(
                                    "\n" + r.output.strip() + "\n",
                                    "tests." + current_cpu(),
                                    name=snapshot_name,
                                    path=path,
                                    encoder=str,
                                    mode=snapshot.CHECK | snapshot.UPDATE,
                                )
                            ), error()