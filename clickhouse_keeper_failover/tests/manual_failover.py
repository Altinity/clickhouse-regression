#!/usr/bin/env python3
from testflows.core import *

from clickhouse_keeper_failover.tests.steps import *


@TestFeature
@Name("manual failover")
def feature(self, restart_on_reconfig=True):
    """Test keeper manual failover."""

    with Given("I check that the leader exists"):
        current_leader = retry(
            get_current_leader, timeout=10, delay=1, initial_delay=2
        )()

    with Given("I split the nodes into ensembles for PR and DR"):
        pr_ensemble = self.context.keeper_nodes[:3]
        dr_ensemble = self.context.keeper_nodes[3:]

    with When("I stop the PR ensemble"):
        for node in pr_ensemble:
            node.command("kill 1")

    with Given("I enable leadership on DR ensemble"):
        set_keeper_config(
            nodes=dr_ensemble,
            config_file_name="keeper_config_manual_failover.xml",
            restart=restart_on_reconfig,
        )

    pause()
