#!/usr/bin/env python3
from testflows.core import *

from clickhouse_keeper_failover.tests.steps import *


@TestFeature
@Name("manual failover")
def feature(self):
    """Test keeper manual failover."""

    with Given("I check that the leader exists"):
        current_leader = retry(
            get_current_leader, timeout=30, delay=5, initial_delay=10
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
            restart=False,
        )

    with When("I restart one node with --force-recovery"):
        cluster = self.context.cluster
        new_leader_node = dr_ensemble[0]
        cluster.command(None, f"{cluster.docker_compose} stop {new_leader_node.name}")
        cluster.command(
            None,
            f"{cluster.docker_compose} run --service-ports -d {new_leader_node.name} ./entrypoint.sh --force-recovery",
        )

    with Then("I wait for the node to restart in recovery mode"):
        retry(check_logs, timeout=60, delay=1)(
            node=new_leader_node,
            message="KeeperServer: This instance is in recovery mode",
            use_compose_workaround=True,
            tail=50,
        )

    with Then("I wait for the server to finish starting"):
        retry(check_logs, timeout=30, delay=1)(
            node=new_leader_node,
            message="INIT RAFT SERVER",
            use_compose_workaround=True,
            tail=30,
        )

    with When("I restart all other DR nodes"):
        for node in dr_ensemble[1:]:
            node.restart()

    with Then("I check that the leader exists"):
        current_leader = retry(
            get_current_leader, timeout=30, delay=5, initial_delay=10
        )()

    with And("I check that the cluster is healthy"):
        r = keeper_query(
            node=new_leader_node, query="mntr", use_compose_workaround=True
        )
        assert "zk_synced_followers\t2" in r.output, error()
