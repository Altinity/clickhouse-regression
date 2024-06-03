#!/usr/bin/env python3
from testflows.core import *

from clickhouse_keeper.requirements import (
    RQ_SRS_024_ClickHouse_Keeper_Disaster_Recovery_ManualRecovery,
)

from clickhouse_keeper_failover.tests.steps import *


@TestFeature
@Name("manual failover rcvr")
@Requirements(RQ_SRS_024_ClickHouse_Keeper_Disaster_Recovery_ManualRecovery("1.0"))
def feature(self, restart_on_reconfig=False):
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
            node.stop_keeper(signal="KILL")

    with Given("I enable leadership on DR ensemble"):
        set_keeper_config(
            nodes=dr_ensemble,
            config_file_name="keeper_config_3node_failover.xml",
            restart=restart_on_reconfig,
        )

    with When("I choose a node to perform the recovery"):
        recovery_node = dr_ensemble[0]

    # with And("I stop the other failover nodes"):
    #     for node in dr_ensemble[1:]:
    #         node.stop_keeper()

    if restart_on_reconfig:
        with Then("I wait for the server to finish starting"):
            retry(check_logs, timeout=30, delay=1)(
                node=recovery_node,
                message="INIT RAFT SERVER",
                tail=30,
            )

    with When("I send 'rcvr' to the recovery node"):
        r = recovery_node.command("echo rcvr | nc localhost 9181", no_checks=True)
        assert r.exitcode in [0, 1], error("Unexpected code from nc")

    with Then("I wait for the node to enter recovery mode"):
        retry(check_logs, timeout=60, delay=2)(
            node=recovery_node,
            message="KeeperServer: This instance is in recovery mode",
            tail=50,
        )

    # with When("I restart all other DR nodes"):
    #     for node in dr_ensemble[1:]:
    #         node.start_keeper()
    #         retry(check_logs, timeout=30, delay=1)(
    #             node=node,
    #             message="INIT RAFT SERVER",
    #             tail=30,
    #         )

    with Then("I check that the leader exists"):
        current_leader = retry(
            get_current_leader, timeout=60, delay=10, initial_delay=10
        )()

    with And("I check that the cluster is healthy"):
        for attempt in retries(timeout=120, delay=10, initial_delay=10):
            with attempt:
                r = keeper_query(node=recovery_node, query="srvr")
                assert "Mode: leader" in r.output, error()
                r = keeper_query(node=recovery_node, query="mntr")
                assert "zk_synced_followers\t2" in r.output, error()
