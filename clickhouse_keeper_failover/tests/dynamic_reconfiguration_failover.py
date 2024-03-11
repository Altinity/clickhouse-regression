#!/usr/bin/env python3
from testflows.core import *

from clickhouse_keeper_failover.tests.steps import *


@TestFeature
@Name("dynamic failover")
def feature(self, restart_on_reconfig=True):
    """Test keeper dynamic reconfiguration failover."""

    with Given("I check that the leader exists"):
        current_leader = retry(
            get_current_leader, timeout=10, delay=1, initial_delay=2
        )()

    with Given("I split the nodes into ensembles for PR and DR"):
        all_nodes = self.context.keeper_nodes
        pr_ensemble = all_nodes[:3]
        dr_ensemble = all_nodes[3:]
        note(len(all_nodes))
        note(len(pr_ensemble))
        note(len(dr_ensemble))

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
                    node.restart()

            with Then(f"I check that {node.name} is now a follower"):
                assert r.output.count("participant") == i, error()

            with When(f"I request leadership"):
                r = retry(keeper_query, timeout=60, delay=5, initial_delay=10)(
                    node=node, query="rqld"
                )
                assert r.output == "Sent leadership request to leader.", error()

            with Then(f"I check that {node.name} is now a leader"):
                for attempt in retries(timeout=10, delay=2, initial_delay=2):
                    with attempt:
                        assert get_node_role(node=node) == "leader", error()

    with When("I stop the PR ensemble"):
        for node in pr_ensemble:
            node.command("kill 1")

    with When("I run `mntr` on all DR nodes"):
        for node in dr_ensemble:
            keeper_query(node=node, query="mntr")
