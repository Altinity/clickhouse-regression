#!/usr/bin/env python3
import random

from testflows.core import *

from helpers.common import getuid
from alter.stress.tests.steps import (
    interrupt_node,
    insert_random,
    assert_row_count,
    optimize,
)
from alter.stress.tests.actions import check_consistency
from ssl_server.tests.zookeeper.steps import add_zookeeper_config_file
from s3.tests.common import default_s3_disk_and_volume, replicated_table


@TestScenario
def stop_zookeeper(self):
    """Table creation and inserts with zookeepers offline."""

    insert_rows = 100000
    n_inserts = 12
    columns = "d UInt64"

    cluster = self.context.cluster
    nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]
    zk_nodes = [cluster.node(n) for n in ["zookeeper1", "zookeeper2", "zookeeper3"]]

    with When("I create a replicated table with a zookeeper offline"):
        with interrupt_node(random.choice(zk_nodes)):
            table_name = "table_" + getuid()
            for node in nodes:
                for attempt in retries(timeout=120, delay=5):
                    with attempt:
                        replicated_table(
                            node=node, table_name=table_name, columns=columns
                        )

    with When("I insert data with a zookeeper offline"):
        with interrupt_node(random.choice(zk_nodes)):
            retry(insert_random, timeout=120, delay=5)(
                node=random.choice(nodes),
                table_name=table_name,
                columns=columns,
                rows=insert_rows,
            )
            for _ in range(n_inserts - 1):
                insert_random(
                    node=random.choice(nodes),
                    table_name=table_name,
                    columns=columns,
                    rows=insert_rows,
                )

    with When("I optimize with zookeepers offline"):
        with interrupt_node(zk_nodes[0]):
            with interrupt_node(zk_nodes[1]):
                with interrupt_node(zk_nodes[2]):
                    with When("I trigger merges"):
                        for node in nodes:
                            optimize(node=node, table_name=table_name, final=False)

    with Then("I check that tables are consistent"):
        with interrupt_node(random.choice(zk_nodes)):
            for node in nodes:
                retry(assert_row_count, timeout=120, delay=5)(
                    node=node, table_name=table_name, rows=insert_rows * n_inserts
                )


@TestOutline(Scenario)
@Examples(
    "settings, check_inserts",
    [
        [{"syncLimit": "1"}, True],
        [{"tickTime": "30"}, True],
        [{"maxSessionTimeout": "2000"}, True],
        [{"syncLimit": "1", "tickTime": "30"}, True],
        [{"syncLimit": "1", "tickTime": "30", "maxSessionTimeout": "2000"}, True],
    ],
)
def zookeeper_timeout(self, settings, check_inserts=True):
    """Check for data loss with various zookeeper timeouts."""

    rows_per_insert = 5000
    insert_rounds = 5
    columns = "d UInt64"

    cluster = self.context.cluster
    nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]
    zk_nodes = [cluster.node(n) for n in ["zookeeper1", "zookeeper2", "zookeeper3"]]

    with Given("a replicated vfs table"):
        table_name = "table_" + getuid()
        for node in nodes:
            replicated_table(node=node, table_name=table_name, columns=columns)

    with When("I perform inserts"):
        for _ in range(insert_rounds):
            for node in nodes:
                with By(f"Inserting {rows_per_insert} rows on {node.name}"):
                    insert_random(
                        node=node,
                        table_name=table_name,
                        columns=columns,
                        rows=rows_per_insert,
                        no_checks=False,
                    )

    with Given("short timeout config for zookeeper"):
        for node in zk_nodes:
            add_zookeeper_config_file(entries=settings, restart=True, node=node)

    with When("I perform more inserts"):
        for _ in range(insert_rounds):
            for node in nodes:
                with By(f"Inserting {rows_per_insert} rows on {node.name}"):
                    insert_random(
                        node=node,
                        table_name=table_name,
                        columns=columns,
                        rows=rows_per_insert,
                        no_checks=(not check_inserts),
                    )

    with And("I optimize"):
        for node in nodes:
            optimize(node=node, table_name=table_name)

    with Then("I check the number of rows in the table"):
        check_consistency(nodes=nodes, table_name=table_name)

        if check_inserts:
            assert_row_count(
                node=nodes[0],
                table_name=table_name,
                rows=(rows_per_insert * insert_rounds * len(nodes) * 2),
            )


@TestFeature
@Name("zookeeper")
def feature(self, uri):
    """Test cluster functionality."""

    self.context.uri = uri

    with Given("I have S3 disks configured"):
        default_s3_disk_and_volume()

    for scenario in loads(current_module(), Scenario):
        scenario()
