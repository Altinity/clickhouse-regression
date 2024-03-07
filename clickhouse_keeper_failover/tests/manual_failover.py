#!/usr/bin/env python3
from testflows.core import *

from clickhouse_keeper_failover.tests.steps import *

@TestFeature
@Name("manual failover")
def feature(self):
    """Test keeper manual failover."""

    with Given("I know the current leader"):
        current_leader = retry(get_current_leader, timeout=10, delay=2)()

    with And("I split the nodes into ensembles for PR and DR"):
        pr_ensemble = self.context.keeper_nodes[:3]
        dr_ensemble = self.context.keeper_nodes[3:]

    with When("I stop the PR ensemble"):
        for node in pr_ensemble:
            node.stop()


        