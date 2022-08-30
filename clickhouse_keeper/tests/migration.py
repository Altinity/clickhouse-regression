from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from helpers.common import getuid
import time


@TestOutline
def migrate_from_zookeeper(self, use_standalone_keeper_server):
    """Check migration of ClickHouse cluster that used ZooKeeper to standalone `clickhouse-keeper` servers
    when one ClickHouse node is down and become available after Zookeeper cluster is down
    and `clickhouse-keeper` is available when `use_standalone_keeper_server=True`.

    Check migration of ClickHouse cluster that used ZooKeeper to ClickHouse server that are also act as
    `clickhouse-keeper` when one ClickHouse node is down and become available after Zookeeper cluster is down
    and `clickhouse-keeper` is available when `use_standalone_keeper_server=False`.
    """
    cluster = self.context.cluster
    try:
        with Given("I add ZooKeeper server configuration file to ClickHouse servers"):
            create_config_section(
                control_nodes=cluster.nodes["zookeeper"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:9],
            )

        # with Then("I restart ClickHouse server nodes with new configs"):
        #     for name in cluster.nodes["clickhouse"][:9]:
        #         cluster.node(name).restart_clickhouse()

        with And("I get table name with UID"):
            uid = getuid()
            table_name = f"test{uid}"

        with Then("I create ReplicateMergeTree table"):
            create_simple_table(
                table_name=table_name,
                cluster_name="'Cluster_3shards_with_3replicas'",
                manual_cleanup=True,
            )

        with And("I stop ClickHouse server 1 node"):
            cluster.node("clickhouse1").stop_clickhouse()

        with Then("I insert data into the table from ClickHouse server 2 node "):
            table_insert(table_name=table_name, node_name="clickhouse2")

        with And("I check data is available on the second node"):
            table_select(
                table_name=table_name, node_name="clickhouse2", message="1,111"
            )

        with And("I check data is available on the third node"):
            table_select(
                table_name=table_name, node_name="clickhouse3", message="1,111"
            )

        with And("I stop all ClickHouse server nodes"):
            for name in cluster.nodes["clickhouse"][:9]:
                if name == "clickhouse1":
                    pass
                else:
                    cluster.node(name).stop_clickhouse()

        with Then("I stop all ZooKeeper nodes"):
            stop_all_zookeepers()

        with Given(
            "I use converter utility to convert ZooKeeper snapshots and logs",
            description="""converter utility: clickhouse-keeper-converter
            --zookeeper-logs-dir /var/lib/zookeeper1/datalog/version-2
            --zookeeper-snapshots-dir /var/lib/zookeeper1/data/version-2
            --output-dir /var/lib/clickhouse/coordination/""",
        ):

            cluster.node("clickhouse1").cmd(
                f"clickhouse keeper-converter"
                f" --zookeeper-logs-dir /share/zookeeper3/datalog/version-2 --zookeeper-snapshots-dir "
                f"/share/zookeeper3/data/version-2 --output-dir /share/{uid}/snapshots"
            )

        if use_standalone_keeper_server:
            with Given("I copy configured snapshot to all Keeper nodes"):
                for name in cluster.nodes["clickhouse"][9:12]:
                    node = cluster.node(name)
                    node.cmd(
                        f"rm -rf /var/lib/clickhouse/coordination/snapshots "
                        f"&& rm -rf /var/lib/clickhouse/coordination/log && cp -r /share/{uid}/snapshots/ "
                        f"/var/lib/clickhouse/coordination"
                    )

            with Given("I start standalone 3 nodes Keeper server"):
                create_keeper_cluster_configuration(
                    nodes=cluster.nodes["clickhouse"][9:12]
                )

            with Given("I start all standalone Keepers nodes"):
                for name in cluster.nodes["clickhouse"][9:12]:
                    cluster.node(name).stop_clickhouse()
                start_keepers(
                    standalone_keeper_nodes=cluster.nodes["clickhouse"][9:12],
                    manual_cleanup=True,
                )

            with And("I add Keeper server configuration file"):
                time.sleep(3)
                create_config_section(
                    control_nodes=cluster.nodes["clickhouse"][9:12],
                    cluster_nodes=cluster.nodes["clickhouse"][:12],
                    check_preprocessed=False,
                )

            with And("I start all ClickHouse server nodes"):
                for name in cluster.nodes["clickhouse"][:9]:
                    cluster.node(name).start_clickhouse()

        else:
            with Given("I copy configured snapshot to all server Keeper nodes"):
                for name in self.context.cluster.nodes["clickhouse"][6:9]:
                    node = self.context.cluster.node(name)
                    node.cmd(
                        f"rm -rf /var/lib/clickhouse/coordination/snapshots "
                        f"&& rm -rf /var/lib/clickhouse/coordination/log && cp -r /share/{uid}/snapshots/ "
                        f"/var/lib/clickhouse/coordination"
                    )

            with Given("I create mixed 3 nodes Keeper server config file"):
                create_keeper_cluster_configuration(
                    nodes=cluster.nodes["clickhouse"][6:9], check_preprocessed=False
                )

            with And("I create server Keeper config"):
                create_config_section(
                    control_nodes=cluster.nodes["clickhouse"][6:9],
                    cluster_nodes=cluster.nodes["clickhouse"][:9],
                    check_preprocessed=False,
                )

            with And("I start mixed ClickHouse server nodes"):
                for name in cluster.nodes["clickhouse"][6:9]:
                    cluster.node(name).start_clickhouse(wait_healthy=False)

            with And("I start all ClickHouse server nodes"):
                time.sleep(5)
                for name in cluster.nodes["clickhouse"][:6]:
                    cluster.node(name).start_clickhouse()

        with Then("I insert data into the table from the ClickHouse server 1 node"):
            table_insert(table_name=table_name, node_name="clickhouse1", values="7,777")

        with Then("I check information in the clickhouse keeper server 1 node"):
            table_select(
                table_name=table_name, node_name="clickhouse1", message="1,111\n7,777"
            )

        if use_standalone_keeper_server:
            with Then("I start clickhouse servers"):
                stop_keepers(cluster_nodes=cluster.nodes["clickhouse"][9:12])
                for name in cluster.nodes["clickhouse"][9:12]:
                    self.context.cluster.node(name).start_clickhouse(wait_healthy=False)
                    time.sleep(5)

    finally:
        with Finally("I clean up"):
            with By("Clear Zookeeper meta information", flags=TE):
                self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")
                clean_coordination_on_all_nodes()

            with By("I restart ZooKeepers back up", flags=TE):
                for name in self.context.cluster.nodes["zookeeper"]:
                    node = self.context.cluster.node(name)
                    with When(f"I restart {name}"):
                        node.start()

            with By(
                "I add ZooKeeper server configuration file to ClickHouse servers",
                flags=TE,
            ):
                for name in cluster.nodes["clickhouse"][:12]:
                    cluster.node(name).stop_clickhouse()
                time.sleep(15)
                create_config_section(
                    control_nodes=cluster.nodes["zookeeper"][:3],
                    cluster_nodes=cluster.nodes["clickhouse"][:12],
                    check_preprocessed=False,
                )

            with And("I start all ClickHouse server nodes", flags=TE):
                time.sleep(15)
                for name in cluster.nodes["clickhouse"][:12]:
                    cluster.node(name).start_clickhouse()

            with By("Dropping table if exists", flags=TE):
                self.context.cluster.node("clickhouse1").query(
                    f"DROP TABLE IF EXISTS {table_name} ON CLUSTER "
                    "'Cluster_3shards_with_3replicas' SYNC"
                )

            with Then("I stop all ZooKeeper nodes"):
                stop_all_zookeepers()

            with By("Clear Zookeeper meta information", flags=TE):
                self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")
                clean_coordination_on_all_nodes()

            with By("I restart ZooKeepers back up", flags=TE):
                for name in self.context.cluster.nodes["zookeeper"]:
                    node = self.context.cluster.node(name)
                    with When(f"I restart {name}"):
                        node.start()


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Converter_ZookeeperMigrationToKeeper_Procedure_PartOfServer(
        "1.0"
    )
)
def migrate_from_zookeeper_to_mixed_servers(self):
    """Check migration of ClickHouse cluster that used ZooKeeper to ClickHouse
    server that are also act as `clickhouse-keeper` when one ClickHouse node
    is down and become available after Zookeeper cluster is down and
    `clickhouse-keeper` is available.
    """
    migrate_from_zookeeper(use_standalone_keeper_server=False)


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Converter_ZookeeperMigrationToKeeper_Procedure_Standalone(
        "1.0"
    )
)
def migrate_from_zookeeper_to_standalone_keeper(self):
    """Check migration of ClickHouse cluster that used ZooKeeper to standalone
    `clickhouse-keeper` servers when one ClickHouse node is down and become
    available after Zookeeper cluster is down and `clickhouse-keeper`
    is available.
    """
    migrate_from_zookeeper(use_standalone_keeper_server=True)


@TestFeature
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_Converter_ZookeeperMigrationToKeeper_Procedure("1.0")
)
@Name("migration")
def feature(self):
    """Check ClickHouse cluster migration operations
    from ZooKeeper to ClickHouse Keeper.
    """
    for scenario in loads(current_module(), Scenario):
        scenario()
