from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl_fips import *
import csv


@TestStep
def start_bench_scenario(
    self, cluster_name="'cluster_1replica_1shard'", number=100000, timeout=30000
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

        retry(node.query, timeout=1000, delay=1)(
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

        # with Step("I check zoo metrics from system.events after scenario"):
        #     system_zoo_check()

        time_value = metric(name="Time", value=current_time(), units="sec")

        self.context.list.append(f"{current_time()}")

        # self.context.cluster.node("clickhouse1").cmd(f"echo {current_time()} > /etc/1.csv")


@TestScenario
def standalone(
    self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=1
):
    """
    Standalone Keeper configuration bench test.
    """
    cluster = self.context.cluster
    control_nodes = cluster.nodes["clickhouse"][
        number_clickhouse_cluster_nodes : number_clickhouse_cluster_nodes
        + number_of_clickhouse_keeper_nodes
    ]
    cluster_nodes = cluster.nodes["clickhouse"][:number_clickhouse_cluster_nodes]

    cluster_name = "'Cluster_3shards_with_3replicas'"
    self.context.list = []
    try:
        with Given("I start mixed ClickHouse Keepers"):
            if self.context.ssl == "true":
                start_stand_alone_keeper_ssl(
                    control_nodes=control_nodes, cluster_nodes=cluster_nodes
                )
            else:
                start_stand_alone_keeper(
                    control_nodes=control_nodes, cluster_nodes=cluster_nodes
                )

        with And("I start bench scenario"):
            for i in range(5):
                start_bench_scenario(cluster_name=cluster_name, number=100)

        with open("bench.csv", "a", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)

            writer.writerow(["standalone:" + self.context.clickhouse_version])

            writer.writerow(self.context.list)

    finally:

        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestScenario
def mixed(self, number_clickhouse_cluster_nodes=9, number_of_clickhouse_keeper_nodes=1):
    """
    Mixed keeper configuration bench test.
    """
    cluster = self.context.cluster
    control_nodes = cluster.nodes["clickhouse"][
        number_clickhouse_cluster_nodes
        - number_of_clickhouse_keeper_nodes : number_clickhouse_cluster_nodes
    ]
    cluster_nodes = cluster.nodes["clickhouse"][:number_clickhouse_cluster_nodes]
    rest_cluster_nodes = cluster.nodes["clickhouse"][
        : number_clickhouse_cluster_nodes - number_of_clickhouse_keeper_nodes
    ]
    cluster_name = "'Cluster_3shards_with_3replicas'"
    self.context.list = []

    try:
        with Given("I start mixed ClickHouse Keepers"):
            if self.context.ssl == "true":
                start_mixed_keeper_ssl(
                    control_nodes=control_nodes,
                    cluster_nodes=cluster_nodes,
                    rest_cluster_nodes=rest_cluster_nodes,
                )
            else:
                start_mixed_keeper(
                    control_nodes=control_nodes,
                    cluster_nodes=cluster_nodes,
                    rest_cluster_nodes=rest_cluster_nodes,
                )

        with And("I start bench scenario"):
            for i in range(5):
                start_bench_scenario(cluster_name=cluster_name, number=100)

            with open("bench.csv", "a", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)

                writer.writerow(["mixed:" + self.context.clickhouse_version])

                writer.writerow(self.context.list)

    finally:
        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestScenario
def zookeeper(self, number_clickhouse_cluster_nodes=9):
    """
    Check bench macros ZooKeeper.
    """
    cluster = self.context.cluster
    keeper_cluster_nodes = cluster.nodes["zookeeper"][0:3]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][
        :number_clickhouse_cluster_nodes
    ]
    cluster_name = "'Cluster_3shards_with_3replicas'"

    try:
        with Given("I create 1 keeper cluster configuration"):
            create_config_section(
                control_nodes=keeper_cluster_nodes,
                cluster_nodes=clickhouse_cluster_nodes,
            )

        with And("I start bench scenario"):
            for i in range(5):
                start_bench_scenario(cluster_name=cluster_name, number=100)

            with open("bench.csv", "a", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)

                writer.writerow(["zookeeper:" + self.context.clickhouse_version])

                writer.writerow(self.context.list)
    finally:
        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestFeature
# @Requirements(RQ_QA_SRS024_ClickHouse_Keeper_Configurations("1.0"))
@Name("bench")
def feature(self):
    """Bench tests of CLickHouse Keeper"""
    self.context.list = []

    for scenario in loads(current_module(), Scenario):
        scenario()
