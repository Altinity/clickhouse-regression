from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl_fips import *


@TestStep
def performance_check(
    self,
    timeout=30000,
):
    """Step creates a 'bad' table and make inserts. Every row generates ZooKeeper transaction.
    It checks insert time and zoo metrics from system.events before and after insert."""

    node = self.context.cluster.node("clickhouse1")

    insert_time_list = []

    table_name = f"performance_{getuid()}"

    for i in range(self.context.repeats):
        with When(f"I start performance scenario #{self.context.repeats}"):
            try:
                with Given("I create 'bad' table"):
                    retry(node.query, timeout=100, delay=1)(
                        f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {self.context.cluster_name}"
                        f" (p UInt64, x UInt64) "
                        "ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/replicated/{shard}"
                        f"/{table_name}'"
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

                with And(
                    "I make insert into the table and collect insert time (sec) into a list."
                ):
                    retry(node.query, timeout=1000, delay=1)(
                        f"insert into {table_name} select rand(1)%100,"
                        f" rand(2) from numbers({self.context.inserts}) "
                        f"settings max_block_size=100, "
                        f"min_insert_block_size_bytes=1, "
                        f"min_insert_block_size_rows=1, "
                        f"insert_deduplicate=0, "
                        f"max_threads=128, "
                        f"max_insert_threads=128;",
                        timeout=timeout,
                    )

                    metric(name="Time", value=current_time(), units="sec")

                    insert_time_list.append(float(current_time()))

            finally:
                with Finally("I drop table if exists and provide cleanup"):
                    node.query(
                        f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {self.context.cluster_name} SYNC"
                    )
                    clean_coordination_on_all_nodes()
                    self.context.cluster.node("clickhouse1").cmd(f"rm -rf /share/")

    return insert_time_list
