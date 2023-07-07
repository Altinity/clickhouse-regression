from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl_fips import *
import csv


@TestStep
def start_bench_scenario(self, cluster_name, number=100000, timeout=30000):
    """Step creates a 'bad' table and inserts 10000 rows. Every row generates ZK transaction.
    It checks insert time and zoo metrics from system.events before and after insert."""

    node = self.context.cluster.node("clickhouse1")

    table_name = f"bench_{getuid()}"

    try:
        with Given("I create 'bad' table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
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

        with And("I check zoo metrics from system.events before scenario"):
            system_zoo_check()

        with And("I make insert into the table and collect its time into a list."):
            retry(node.query, timeout=1000, delay=1)(
                f"insert into {table_name} select rand(1)%100,"
                f" rand(2) from numbers({number}) "
                f"settings max_block_size=100, "
                f"min_insert_block_size_bytes=1, "
                f"min_insert_block_size_rows=1, "
                f"insert_deduplicate=0, "
                f"max_threads=128, "
                f"max_insert_threads=128;",
                timeout=timeout,
            )

            metric(name="Time", value=current_time(), units="sec")

            self.context.list.append(f"{current_time()}")

        with Then("I check zoo metrics from system.events after scenario"):
            system_zoo_check()

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def standalone_1_node(
    self,
    number_clickhouse_cluster_nodes=9,
    number_of_clickhouse_keeper_nodes=1,
    number_of_tests=5,
    number_of_inserts=100,
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
        with Given("I start standalone ClickHouse Keepers"):
            if self.context.ssl == "true":
                start_stand_alone_keeper_ssl(
                    control_nodes=control_nodes, cluster_nodes=cluster_nodes
                )
            else:
                start_stand_alone_keeper(
                    control_nodes=control_nodes, cluster_nodes=cluster_nodes
                )

        for i in range(number_of_tests):
            with When(f"I start bench scenario №{number_of_tests}"):
                start_bench_scenario(
                    cluster_name=cluster_name, number=number_of_inserts
                )

        with Then("I write results to file"):
            new_list = [float(i) for i in self.context.list]

            with open(self.context.name, "a", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)

                writer.writerow(
                    [
                        "insert time (sec)",
                        "1-node keeper",
                        "standalone:" + self.context.clickhouse_version,
                        "ssl:" + self.context.ssl,
                        "cluster:" + cluster_name,
                        f"insert value: {number_of_inserts}",
                    ]
                )

                writer.writerow(self.context.list)

                writer.writerow(
                    [
                        "mean value (sec):",
                        sum(new_list) / len(new_list),
                    ]
                )
    finally:
        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestScenario
def mixed_1_node(
    self,
    number_clickhouse_cluster_nodes=9,
    number_of_clickhouse_keeper_nodes=1,
    number_of_tests=5,
    number_of_inserts=100,
):
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

        for i in range(number_of_tests):
            with When(f"I start bench scenario №{number_of_tests}"):
                start_bench_scenario(
                    cluster_name=cluster_name, number=number_of_inserts
                )

        with Then("I write results to file"):
            new_list = [float(i) for i in self.context.list]

            with open(self.context.name, "a", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)

                writer.writerow(
                    [
                        "insert time (sec)",
                        "1-node keeper",
                        "mixed:" + self.context.clickhouse_version,
                        "ssl:" + self.context.ssl,
                        "cluster:" + cluster_name,
                        f"insert value: {number_of_inserts}",
                    ]
                )

                writer.writerow(self.context.list)

                writer.writerow(
                    [
                        "mean value (sec):",
                        sum(new_list) / len(new_list),
                    ]
                )

    finally:
        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestScenario
def zookeeper_1_node(
    self, number_clickhouse_cluster_nodes=9, number_of_tests=5, number_of_inserts=100
):
    """
    Check bench macros ZooKeeper.
    """
    cluster = self.context.cluster
    keeper_cluster_nodes = cluster.nodes["zookeeper"][3:4]
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

        for i in range(number_of_tests):
            with When(f"I start bench scenario №{number_of_tests}"):
                start_bench_scenario(
                    cluster_name=cluster_name, number=number_of_inserts
                )

        with Then("I write results to file"):
            new_list = [float(i) for i in self.context.list]

            with open(self.context.name, "a", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)

                writer.writerow(
                    [
                        "insert time (sec)",
                        "1-node zookeeper",
                        "standalone:" + self.context.clickhouse_version,
                        "ssl:" + self.context.ssl,
                        "cluster:" + cluster_name,
                        f"insert value: {number_of_inserts}",
                    ]
                )

                writer.writerow(self.context.list)

                writer.writerow(
                    [
                        "mean value (sec):",
                        sum(new_list) / len(new_list),
                    ]
                )
    finally:
        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestScenario
def standalone_3_node(
    self,
    number_clickhouse_cluster_nodes=9,
    number_of_clickhouse_keeper_nodes=3,
    number_of_tests=5,
    number_of_inserts=100,
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

        for i in range(number_of_tests):
            with When(f"I start bench scenario №{number_of_tests}"):
                start_bench_scenario(
                    cluster_name=cluster_name, number=number_of_inserts
                )

        with Then("I write results to file"):
            new_list = [float(i) for i in self.context.list]

            with open(self.context.name, "a", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)

                writer.writerow(
                    [
                        "insert time (sec)",
                        "3-node keeper",
                        "standalone:" + self.context.clickhouse_version,
                        "ssl:" + self.context.ssl,
                        "cluster:" + cluster_name,
                        f"insert value: {number_of_inserts}",
                    ]
                )

                writer.writerow(self.context.list)

                writer.writerow(
                    [
                        "mean value (sec):",
                        sum(new_list) / len(new_list),
                    ]
                )
    finally:

        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestScenario
def mixed_3_node(
    self,
    number_clickhouse_cluster_nodes=9,
    number_of_clickhouse_keeper_nodes=3,
    number_of_tests=5,
    number_of_inserts=100,
):
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

        for i in range(number_of_tests):
            with When(f"I start bench scenario №{number_of_tests}"):
                start_bench_scenario(
                    cluster_name=cluster_name, number=number_of_inserts
                )

        with Then("I write results to file"):
            new_list = [float(i) for i in self.context.list]

            with open(self.context.name, "a", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)

                writer.writerow(
                    [
                        "insert time (sec)",
                        "3-node keeper",
                        "mixed:" + self.context.clickhouse_version,
                        "ssl:" + self.context.ssl,
                        "cluster:" + cluster_name,
                        f"insert value: {number_of_inserts}",
                    ]
                )

                writer.writerow(self.context.list)

                writer.writerow(
                    [
                        "mean value (sec):",
                        sum(new_list) / len(new_list),
                    ]
                )

    finally:
        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestScenario
def zookeeper_3_node(
    self, number_clickhouse_cluster_nodes=9, number_of_tests=5, number_of_inserts=100
):
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

        for i in range(number_of_tests):
            with When(f"I start bench scenario №{number_of_tests}"):
                start_bench_scenario(
                    cluster_name=cluster_name, number=number_of_inserts
                )

        with Then("I write results to file"):
            new_list = [float(i) for i in self.context.list]
            with open(self.context.name, "a", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)

                writer.writerow(
                    [
                        "insert time (sec)",
                        "3-node zookeeper",
                        "standalone:" + self.context.clickhouse_version,
                        "ssl:" + self.context.ssl,
                        "cluster:" + cluster_name,
                        f"insert value: {number_of_inserts}",
                    ]
                )

                writer.writerow(self.context.list)

                writer.writerow(["mean value (sec):", sum(new_list) / len(new_list)])
    finally:
        with Finally("I clean up files"):
            clean_coordination_on_all_nodes()
            self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")


@TestFeature
@Name("bench")
def feature(self):
    """Bench tests of CLickHouse Keeper"""
    self.context.list = []

    self.context.name = f"bench{getuid()}.csv"

    for scenario in loads(current_module(), Scenario):
        scenario()
