from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *


@TestOutline
def alter_partition(
    self,
    table_name="test_move",
    cluster_name="'cluster_2replica_2shard'",
    value_1=1,
    value_2=2,
):
    """alter_partition tests environment to create mixed ClickHouse cluster
    and filled with data replicated table with enabled part features in it."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    with Given("I create table"):
        retry(node.query, timeout=100, delay=1)(
            f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
            f" (v UInt64) "
            "ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables"
            "/replicated/{shard}"
            f"/{table_name}'"
            ", '{replica}') "
            "ORDER BY tuple() "
            "SETTINGS assign_part_uuids=1,"
            " part_moves_between_shards_enable=1,"
            " part_moves_between_shards_delay_seconds=1;",
            steps=False,
        )

    with And("I make insert into table"):
        retry(node.query, timeout=100, delay=1)(f"SYSTEM STOP MERGES {table_name}")

        retry(node.query, timeout=100, delay=1)(
            f"INSERT INTO {table_name} VALUES ({value_1})"
        )
        retry(node.query, timeout=100, delay=1)(
            f"INSERT INTO {table_name} VALUES ({value_2})"
        )

    with And("I check data on different shards"):
        cluster.node("clickhouse1").query(
            f"select count() from {table_name}", message="2"
        )


@TestScenario
def alter_detach_partition(self):
    """Check ALTER query DETACH PARTITION."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:

        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"

        with And("I create table and make 2 part insert"):
            alter_partition(table_name=table_name, cluster_name=cluster_name)

        with And("I detach part"):
            node.query(f"ALTER TABLE {table_name} DETACH PART 'all_0_0_0'")

            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check part detached"):
            for name in cluster.nodes["clickhouse"][0:3]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT count() FROM {table_name}", message="1"
                )
        with And("I check part moved to system.detached_parts"):
            for name in cluster.nodes["clickhouse"][0:1]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"select count() from system.detached_parts "
                    f"where table ilike '{table_name}'",
                    message="1",
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_drop_partition(self):
    """Check ALTER query DROP PARTITION."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"

        with And("I create table and make 2 part insert"):
            alter_partition(table_name=table_name, cluster_name=cluster_name)

        with And("I detach part"):
            node.query(f"ALTER TABLE {table_name} DROP PART 'all_0_0_0'")

            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check part dropped"):
            for name in cluster.nodes["clickhouse"][0:3]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT count() FROM {table_name}", message="1"
                )

        with And("I check part doesn't moved to system.detached_parts"):
            for name in cluster.nodes["clickhouse"][0:1]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"select count() from system.detached_parts "
                    f"where table ilike '{table_name}'",
                    message="0",
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_attach_partition(self):
    """Check ALTER query ATTACH PARTITION."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"

        with And("I create table and make 2 part insert"):
            alter_partition(table_name=table_name, cluster_name=cluster_name)

        with And("I detach part"):
            node.query(f"ALTER TABLE {table_name} DETACH PART 'all_0_0_0'")

            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with And("I attach part"):
            node.query(f"ALTER TABLE {table_name} ATTACH PART 'all_0_0_0'")

        with Then("I check part detached"):
            for name in cluster.nodes["clickhouse"][0:3]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT count() FROM {table_name}", message="2"
                )

        with And("I check part moved to system.detached_parts"):
            for name in cluster.nodes["clickhouse"][0:1]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"select count() from system.detached_parts "
                    f"where table ilike '{table_name}'",
                    message="0",
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_attach_partition_from(self):
    """Check ALTER query ATTACH PARTITION FROM."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"
            table_name2 = f"test_move2{uid}"

        with And("I create 2 tables and make insert of two parts"):
            alter_partition(table_name=table_name, cluster_name=cluster_name)
            alter_partition(
                table_name=table_name2, cluster_name=cluster_name, value_1=3, value_2=4
            )

        with And("I attach part from one table to another"):
            node.query(
                f"ALTER TABLE {table_name} ATTACH PARTITION tuple() FROM {table_name2}"
            )

            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check part attached"):
            for name in cluster.nodes["clickhouse"][0:1]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"select count() from {table_name}", message="4"
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )
            node.query(
                f"DROP TABLE IF EXISTS {table_name2} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_replace_partition_from(self):
    """Check ALTER query REPLACE PARTITION FROM."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"
            table_name2 = f"test_move2{uid}"

        with And("I create 2 tables and make insert of two parts"):
            alter_partition(table_name=table_name, cluster_name=cluster_name)
            alter_partition(
                table_name=table_name2, cluster_name=cluster_name, value_1=3, value_2=4
            )

        with And("I replace part from one table to another"):
            node.query(
                f"ALTER TABLE {table_name} REPLACE PARTITION tuple() FROM {table_name2}"
            )

            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check part replaced"):
            for name in cluster.nodes["clickhouse"][0:1]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"select count() from {table_name}", message="2"
                )
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"select * from {table_name}", message="4"
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )
            node.query(
                f"DROP TABLE IF EXISTS {table_name2} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_move_partition_to_table(self):
    """Check ALTER query MOVE PARTITION  TO TABLE."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"
            table_name2 = f"test_move2{uid}"

        with And("I create 2 tables and make insert of two parts"):
            alter_partition(table_name=table_name, cluster_name=cluster_name)
            alter_partition(
                table_name=table_name2, cluster_name=cluster_name, value_1=3, value_2=4
            )

        with And("I move partition from one table to another"):
            node.query(
                f"ALTER TABLE {table_name} MOVE PARTITION tuple() TO TABLE {table_name2}"
            )

            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check part moved"):
            for name in cluster.nodes["clickhouse"][0:1]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"select count() from {table_name}", message="0"
                )
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"select count() from {table_name2}", message="4"
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )
            node.query(
                f"DROP TABLE IF EXISTS {table_name2} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_clear_column_in_partition(self):
    """Check ALTER query CLEAR COLUMN IN PARTITION."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:

        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"
        with Given("I create table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
                f" (v UInt64,p UInt64) "
                "ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables"
                "/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}') "
                "PARTITION BY p "
                "ORDER BY tuple() "
                "SETTINGS assign_part_uuids=1,"
                " part_moves_between_shards_enable=1,"
                " part_moves_between_shards_delay_seconds=1;",
                steps=False,
            )

        with And("I make insert into table"):
            retry(node.query, timeout=100, delay=1)(f"SYSTEM STOP MERGES {table_name}")

            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (1,1)"
            )
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (2,2)"
            )

        with And("I clear partition in column"):
            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"ALTER TABLE {table_name} CLEAR COLUMN v IN PARTITION 1")

            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check partition in column 'v' cleared"):
            for name in cluster.nodes["clickhouse"][0:3]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT count() FROM {table_name}", message="1"
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_clear_index_in_partition(self):
    """Check ALTER query CLEAR INDEX IN PARTITION."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:

        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"

        with Given("I create table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
                f" (v UInt64,p UInt64) "
                "ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables"
                "/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}') "
                "PARTITION BY p "
                "ORDER BY tuple() "
                "SETTINGS assign_part_uuids=1,"
                " part_moves_between_shards_enable=1,"
                " part_moves_between_shards_delay_seconds=1;",
                steps=False,
            )

        with And("I make insert into table"):
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (1,1)"
            )
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (2,2)"
            )

        with And("I add index"):
            node.query(
                f"ALTER TABLE {table_name} ADD INDEX v_id (v) TYPE minmax GRANULARITY 8132"
            )

        with And("I clear index of partition in column"):
            node.query(f"ALTER TABLE {table_name} CLEAR INDEX v_id IN PARTITION 1")

            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_freeze_partition(self):
    """Check ALTER query FREEZE PARTITION."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"

        with And("I create table and make 2 part insert"):
            alter_partition(table_name=table_name, cluster_name=cluster_name)

        with And("I freeze all partitions"):
            node.query(f"ALTER TABLE {table_name} FREEZE WITH NAME 'freeze_test'")

            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with And("I check partition froze"):
            node.cmd("ls var/lib/clickhouse/shadow/", message="freeze_test")

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_unfreeze_partition(self):
    """Check ALTER query UNFREEZE PARTITION."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"

        with And("I create table and make 2 part insert"):
            alter_partition(table_name=table_name, cluster_name=cluster_name)

        with And("I freeze all partitions"):
            node.query(f"ALTER TABLE {table_name} FREEZE WITH NAME 'freeze_test'")

        with And("I unfreeze all partitions"):
            node.query(f"ALTER TABLE {table_name} UNFREEZE WITH NAME 'freeze_test'")

            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_fetch_partition(self):
    """Check ALTER query FETCH PARTITION."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"

        with And("I create table and make 2 part insert"):
            alter_partition(table_name=table_name, cluster_name=cluster_name)

        with And("I fetch part from shard one"):
            cluster.node("clickhouse4").query(
                f"ALTER TABLE {table_name} FETCH PART 'all_0_0_0' FROM '/clickhouse/tables/replicated/01/{table_name}'"
            )

        with And("I attach this part to table on shard two"):
            cluster.node("clickhouse4").query(
                f"alter table {table_name} attach part 'all_0_0_0'"
            )

        with Then("I check the data added"):
            cluster.node("clickhouse4").query(
                f"select * from {table_name}", message="1"
            )

            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_update_in_partition(self):
    """Check ALTER query UPDATE PARTITION."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:

        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"

        with Given("I create table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
                f" (v UInt64,p UInt64) "
                "ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables"
                "/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}') "
                "PARTITION BY p "
                "ORDER BY tuple() "
                "SETTINGS assign_part_uuids=1,"
                " part_moves_between_shards_enable=1,"
                " part_moves_between_shards_delay_seconds=1;",
                steps=False,
            )

        with And("I make insert into table"):
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (1,1)"
            )
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (2,2)"
            )

        with And("I update partition 2 of column v as v = v + 2"):
            node.query(
                f"ALTER TABLE {table_name} UPDATE v = v + 2 IN PARTITION 2 WHERE p = 2;"
            )

        with Then("I check data is updated"):
            for name in cluster.nodes["clickhouse"][0:3]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT * FROM {table_name}", message="4"
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
def alter_delete_in_partition(self):
    """Check ALTER query DELETE PARTITION."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:

        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_move{uid}"

        with Given("I create table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
                f" (v UInt64,p UInt64) "
                "ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables"
                "/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}') "
                "PARTITION BY p "
                "ORDER BY tuple() "
                "SETTINGS assign_part_uuids=1,"
                " part_moves_between_shards_enable=1,"
                " part_moves_between_shards_delay_seconds=1;",
                steps=False,
            )

        with And("I make insert into table"):
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (1,1)"
            )
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (2,2)"
            )

        with And("I delete partition 2"):
            node.query(f"ALTER TABLE {table_name} DELETE IN PARTITION 2 WHERE p = 2;")

        with Then("I check partition 2 data is deleted"):
            for name in cluster.nodes["clickhouse"][0:3]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT * FROM {table_name}", message="1"
                )
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT count() FROM {table_name}", message="1"
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestFeature
@Requirements(RQ_SRS_024_ClickHouse_Keeper_ClickHouseOperation_Alter("1.0"))
@Name("alter_partition_distributed")
def feature(self):
    """Check data synchronization between replicas for different ALTER  partition DDL queries."""
    with Given("I start mixed ClickHouse cluster"):
        if self.context.ssl == "false":
            start_mixed_keeper()
        else:
            start_mixed_keeper_ssl()

    for scenario in loads(current_module(), Scenario):
        scenario()
