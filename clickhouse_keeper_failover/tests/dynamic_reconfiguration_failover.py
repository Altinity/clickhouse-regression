#!/usr/bin/env python3
from testflows.core import *

from clickhouse_keeper_failover.tests.steps import *


@TestFeature
@Name("dynamic failover")
def feature(self, restart_on_reconfig=True):
    """Test keeper dynamic reconfiguration failover."""

    with Given("I check that the leader exists"):
        current_leader = retry(get_current_leader, timeout=10, delay=1)()
        note(f"The current leader is {current_leader}")

    with Given("I split the nodes into ensembles for PR and DR"):
        all_nodes = self.context.keeper_nodes
        pr_ensemble = all_nodes[:3]
        dr_ensemble = all_nodes[3:]

    with When("I update learner nodes to follower"):
        enabled_ids = []
        for i, node in enumerate(dr_ensemble, start=4):
            enabled_ids.append(str(i))

            with When(f"I enable leadership on nodes {enabled_ids}"):
                config_name = f"keeper_config_enable_{''.join(enabled_ids)}.xml"
                set_keeper_config(
                    nodes=all_nodes,
                    config_file_name=config_name,
                    restart=restart_on_reconfig,
                )

            with Then(f"I check {node.name} has changed to follower"):
                for attempt in retries(timeout=10, delay=2):
                    with attempt:
                        assert get_node_role(node=node) == "follower", error()

            with Then(f"I check configuration on node {node.name}"):
                r = keeper_query(node=node, query=f"get /keeper/config")
                assert r.output.count("participant") == i - 1, error()

            with When(f"I remove and re-add {node.name}"):
                keeper_query(node=pr_ensemble[0], query=f"reconfig remove {i}")
                r = keeper_query(
                    node=pr_ensemble[0],
                    query=f"reconfig add 'server.{i}=keeper-{i}:9234'",
                )
                if restart_on_reconfig:
                    node.restart_keeper()

            with Then(f"I check that {node.name} is now a follower"):
                assert r.output.count("participant") == i, error()

            with When(f"I wait for {node.name} to finish starting"):
                retry(get_node_role, timeout=30, delay=2, initial_delay=2)(node=node)

            with And(f"I request leadership"):
                r = retry(keeper_query, timeout=30, delay=5)(node=node, query="rqld")
                assert r.output == "Sent leadership request to leader.", error()

            with Then(f"I check that {node.name} is now a leader"):
                for attempt in retries(timeout=10, delay=2, initial_delay=2):
                    with attempt:
                        assert get_node_role(node=node) == "leader", error()

    with When("I check the current leader"):
        note(f"The current leader is {get_current_leader()}")

    with When("I remove the PR ensemble from the config"):
        set_keeper_config(
            nodes=dr_ensemble,
            config_file_name="keeper_config_3node_failover.xml",
            restart=restart_on_reconfig,
        )

    with When("I stop the PR ensemble"):
        for node in pr_ensemble:
            node.stop_keeper(signal="KILL")

    with Then("I get the current leader"):
        current_leader = retry(
            get_current_leader, timeout=60, delay=5, initial_delay=10
        )()

    with And("I check that the cluster is healthy"):
        for node in dr_ensemble:
            if node.name != current_leader:
                continue
            r = keeper_query(node=node, query="srvr")
            assert "Mode: leader" in r.output, error()
            r = keeper_query(node=node, query="mntr")
            assert "zk_synced_followers\t2" in r.output, error()
