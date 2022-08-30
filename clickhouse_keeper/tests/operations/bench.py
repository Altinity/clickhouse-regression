from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *


@TestStep
def start_bench_scenario(
    self, cluster_name="'cluster_1replica_1shard'", number=100000, timeout=3000
):
    node = self.context.cluster.node("clickhouse1")
    with Given("I drop table if exists"):
        cluster_name = cluster_name
        node.query(
            f"DROP TABLE IF EXISTS zookeeper_bench ON CLUSTER {cluster_name} SYNC"
        )

    # And("I make interval IOPS check", test=iops_check, parallel=True)(sleep=14, check_points=21)
    #
    # And("I make interval number of rows check", test=rows_number, parallel=True)(sleep=14, check_points=21)

    with And("I create table"):
        retry(node.query, timeout=100, delay=1)(
            f"CREATE TABLE IF NOT EXISTS zookeeper_bench on CLUSTER {cluster_name}"
            f" (p UInt64, x UInt64) "
            "ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/replicated/{shard}"
            f"/zookeeper_bench'"
            ", '{replica}') "
            "ORDER BY tuple() PARTITION BY p "
            "SETTINGS  in_memory_parts_enable_wal=0, "
            "min_bytes_for_wide_part=104857600, "
            "min_bytes_for_wide_part=104857600, "
            "parts_to_delay_insert=1000000, "
            "parts_to_throw_insert=1000000, "
            "max_parts_in_total=1000000;",
            steps=False,
        )

    with And("I make insert in table"):
        with Step("I check zoo metrics from system.events before scenario"):
            system_zoo_check()

        retry(node.query, timeout=100, delay=1)(
            f"insert into zookeeper_bench select rand(1)%100,"
            f" rand(2) from numbers({number}) "
            f"settings max_block_size=100, "
            f"min_insert_block_size_bytes=1, "
            f"min_insert_block_size_rows=1, "
            f"insert_deduplicate=0, "
            f"max_threads=128, "
            f"max_insert_threads=128;",
            timeout=timeout,
        )

        # retry(node.query, timeout=100, delay=1)(f"insert into zookeeper_bench select *%10,"
        #                                         f" * from numbers({number}) "
        #                                         f"settings max_block_size=100, "
        #                                         # f"min_insert_block_size_bytes=100, "
        #                                         # f"min_insert_block_size_rows=100, "
        #                                         # f"insert_deduplicate=0, "
        #                                         f"max_threads=512, "
        #                                         f"max_insert_threads=512;", timeout=timeout)

        with Step("I check zoo metrics from system.events after scenario"):
            system_zoo_check()

        metric(name="Time", value=current_time(), units="sec")


@TestScenario
def bench_macros_standalone(self):
    """
    Check bench macros on standalone Keeper.
    """
    cluster = self.context.cluster
    keeper_cluster_nodes = cluster.nodes["clickhouse"][1:2]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:1]

    with Given("I create remote config"):
        entries = {
            "cluster_1replica_1shard": {
                "shard": {"replica": {"host": "clickhouse1", "port": "9000"}}
            }
        }
        create_remote_configuration(entries=entries)

    # with Given("I stop all unused nodes"):
    #     for name in cluster.nodes["zookeeper"][:4]:
    #         cluster.node(name).stop()
    #     for name in cluster.nodes["clickhouse"][2:13]:
    #         cluster.node(name).stop()

    with And("I start standalone 1 nodes Keeper server"):
        create_keeper_cluster_configuration(nodes=keeper_cluster_nodes)

    with And("I start all standalone Keepers nodes"):
        time.sleep(10)
        for name in keeper_cluster_nodes:
            cluster.node(name).stop_clickhouse()
        start_keepers(standalone_keeper_nodes=keeper_cluster_nodes, manual_cleanup=True)

    with And("I add Keeper server configuration file"):
        create_config_section(
            control_nodes=keeper_cluster_nodes, cluster_nodes=clickhouse_cluster_nodes
        )

    with And("I start bench scenario"):
        start_bench_scenario(cluster_name="'cluster_1replica_1shard'", number=1500)

    with And("I stop all standalone Keepers nodes"):
        stop_keepers(cluster_nodes=keeper_cluster_nodes)

    with And("I start restart Clickhouse nodes"):
        time.sleep(3)
        for name in keeper_cluster_nodes:
            cluster.node(name).start_clickhouse()


@TestScenario
def bench_macros_mixed(
    self, number_of_keeper_cluster_nodes=1, number_clickhouse_cluster_nodes=1
):
    """
    Check bench macros ClickHouse server Keeper.
    """
    cluster = self.context.cluster
    keeper_cluster_nodes = cluster.nodes["clickhouse"][0:number_of_keeper_cluster_nodes]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]

    cluster_name = "'cluster_1replica_1shard'"
    with Given("I create remote config"):
        entries = {
            "cluster_1replica_1shard": {
                "shard": {"replica": {"host": "clickhouse1", "port": "9000"}}
            }
        }
        create_remote_configuration(entries=entries)

        # cluster_name = '\'cluster_2replica_1shard\''
        # with Given("I create remote config"):
        #     entries = {
        #         "cluster_2replica_1shard": {
        #             "shard": [{
        #                 "replica": {
        #                     "host": "clickhouse1",
        #                     "port": "9000"
        #                 }
        #             },
        #             {
        #                 "replica": {
        #                     "host": "clickhouse2",
        #                     "port": "9000"
        #                 }
        #             }]
        #
        #         }}
        create_remote_configuration(entries=entries)

    with Given("I stop all unused nodes"):
        for name in cluster.nodes["zookeeper"][:4]:
            cluster.node(name).stop()
        for name in cluster.nodes["clickhouse"][1:13]:
            cluster.node(name).stop()

    with And("I create 1 keeper cluster configuration"):
        create_keeper_cluster_configuration(nodes=keeper_cluster_nodes)
        create_config_section(
            control_nodes=keeper_cluster_nodes, cluster_nodes=clickhouse_cluster_nodes
        )

    with And("I start bench scenario"):
        start_bench_scenario(cluster_name=cluster_name, number=15000)

    with And("I start bench scenario", flags=PAUSE_BEFORE):
        pass


@TestScenario
def bench_macros_zookeeper(self, number_clickhouse_cluster_nodes=2):
    """
    Check bench macros ZooKeeper.
    """
    cluster = self.context.cluster
    keeper_cluster_nodes = cluster.nodes["zookeeper"][0:1]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]

    # cluster_name = '\'cluster_1replica_1shard\''
    # with Given("I create remote config"):
    #     entries = {
    #         "cluster_1replica_1shard": {
    #             "shard": {
    #                 "replica": {
    #                     "host": "clickhouse1",
    #                     "port": "9000"
    #                 }
    #             }}}
    #     create_remote_configuration(entries=entries)

    cluster_name = "'cluster_2replica_1shard'"
    with Given("I create remote config"):
        entries = {
            "cluster_2replica_1shard": {
                "shard": [
                    {"replica": {"host": "clickhouse1", "port": "9000"}},
                    {"replica": {"host": "clickhouse2", "port": "9000"}},
                ]
            }
        }
        create_remote_configuration(entries=entries)

    with Given("I stop all unused nodes"):
        for name in cluster.nodes["zookeeper"][3:4]:
            cluster.node(name).stop()
        for name in cluster.nodes["clickhouse"][number_clickhouse_cluster_nodes:13]:
            cluster.node(name).stop()

    with And("I create 1 keeper cluster configuration"):
        create_config_section(
            control_nodes=keeper_cluster_nodes, cluster_nodes=clickhouse_cluster_nodes
        )

    with And("I start bench scenario"):
        start_bench_scenario(cluster_name=cluster_name, number=50000)

    with And("I start bench scenario", flags=PAUSE_BEFORE):
        pass


@TestFeature
@Requirements(RQ_QA_SRS024_ClickHouse_Keeper_Configurations("1.0"))
@Name("bench")
def feature(self):
    """Bench tests of CLickHouse Keeper"""

    for scenario in loads(current_module(), Scenario):
        scenario()
