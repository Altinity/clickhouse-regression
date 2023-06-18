from testflows.core import *
from testflows.asserts import error


@TestScenario
def select_1(self):
    """Check that SELECT 1 works on all nodes."""
    for name in self.context.cluster.nodes["clickhouse"]:
        node = self.context.cluster.node(name)

        with Check(f"{name}"):
            with When("I try to execute SELECT 1 query"):
                retry(node.query, timeout=300, delay=10)(
                    "SELECT 1", message="1", exitcode=0
                )


@TestScenario
def fips_build_check(self, node=None):
    """Check ClickHouse for FIPS build version."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    retry(node.query, timeout=300, delay=10)("SELECT 1", message="1", exitcode=0)

    with Given("I check ClickHouse build version"):
        version = node.query("select version() FORMAT CSV").output.strip()

    if version.endswith('altinityfips"'):
        with Then("I check that in logs that Fips mode is enabled"):
            node.cmd(
                "grep 'FIPS mode' /var/log/clickhouse-server/clickhouse-server.log",
                message="<Information> Application: Starting in \x1b[01;31m\x1b[KFIPS mode\x1b[m\x1b[K, KAT test result: 1",
            )
    else:
        with Then("I make pause and provide warning that non-FIPS build is testing"):
            pause("Warning: It's not a FIPS build")


@TestFeature
@Name("sanity")
def feature(self):
    """Sanity check suite."""
    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()
