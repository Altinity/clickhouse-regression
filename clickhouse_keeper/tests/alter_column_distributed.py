from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl_fips import *


@TestScenario
def alter_add_column(self):
    """Check ALTER query ADD COLUMN."""
    cluster = self.context.cluster
    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test{uid}"

        with And("I create simple replicated table"):
            create_simple_table(
                node=self.context.cluster.node("clickhouse2"), table_name=table_name
            )

        with When("I add column to this table"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} ADD COLUMN Added1 UInt32 FIRST;",
                exitcode=0,
                steps=False,
            )

        with Then("I check that column added on all shards"):
            for name in self.context.cluster.nodes["clickhouse"][:9]:
                retry(self.context.cluster.node(name).query, timeout=100, delay=1)(
                    f"DESC {table_name} FORMAT TSV;",
                    exitcode=0,
                    message="Added1\tUInt32",
                    steps=False,
                )

    finally:
        with Finally("I clean created data"):
            clean_coordination_on_all_nodes()


@TestScenario
def alter_drop_column(self):
    """Check ALTER query DROP COLUMN."""
    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test{uid}"

        with And("I create simple replicated table"):
            create_simple_table(
                node=self.context.cluster.node("clickhouse2"), table_name=table_name
            )

        with And("I add column to this table"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} ADD COLUMN Added1 UInt32 FIRST;",
                exitcode=0,
                steps=False,
            )

        with When("I drop this column"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} DROP COLUMN Added1;",
                exitcode=0,
                steps=False,
            )

        with Then("I check that column dropped on all shards"):
            for name in self.context.cluster.nodes["clickhouse"][:9]:
                self.context.cluster.node(name).query(
                    f"SELECT COLUMNS('Added1') FROM {table_name};",
                    exitcode=51,
                    message="DB::Exception: Empty list of columns in SELECT query.",
                )

    finally:
        with Finally("I clean created data"):
            clean_coordination_on_all_nodes()


@TestScenario
def alter_rename_column(self):
    """Check ALTER query RENAME COLUMN."""
    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test{uid}"

        with And("I create simple replicated table"):
            create_simple_table(
                node=self.context.cluster.node("clickhouse2"), table_name=table_name
            )

        with When("I add column to this table"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} ADD COLUMN Added1 UInt32 FIRST;",
                exitcode=0,
                steps=False,
            )

        with When("I rename this column"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} RENAME COLUMN Added1 to Added_new;",
                exitcode=0,
                steps=False,
            )

        with Then("I check that column renamed on all shards"):
            for name in self.context.cluster.nodes["clickhouse"][:9]:
                retry(self.context.cluster.node(name).query, timeout=100, delay=1)(
                    f"DESC {table_name} FORMAT TSV;",
                    exitcode=0,
                    message="Added_new\tUInt32",
                    steps=False,
                )

    finally:
        with Finally("I clean created data"):
            clean_coordination_on_all_nodes()


@TestScenario
def alter_clear_column(self):
    """Check ALTER query CLEAR COLUMN."""
    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test{uid}"

        with And("I create simple replicated table"):
            create_simple_table(
                node=self.context.cluster.node("clickhouse2"), table_name=table_name
            )

        with When("I make insert into table"):
            for name1 in ["clickhouse1", "clickhouse4", "clickhouse7"]:
                retry(self.context.cluster.node(name1).query, timeout=100, delay=1)(
                    f"INSERT INTO {table_name} values (1,1)", exitcode=0, steps=False
                )

        with And("I remove data  from column 'partition'"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} CLEAR COLUMN partition;",
                exitcode=0,
                steps=False,
            )

        with Then("I check data dropped from column 'partition'"):
            for name in self.context.cluster.nodes["clickhouse"][0:9]:
                retry(self.context.cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT * FROM {table_name};",
                    exitcode=0,
                    message="1\t0",
                    steps=False,
                )

    finally:
        with Finally("I clean created data"):
            clean_coordination_on_all_nodes()


@TestScenario
def alter_comment_column(self):
    """Check ALTER query COMMENT COLUMN."""
    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test{uid}"

        with And("I create simple replicated table"):
            create_simple_table(
                node=self.context.cluster.node("clickhouse2"), table_name=table_name
            )

        with When("I add column to this table"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} ADD COLUMN Added1 UInt32 FIRST;",
                exitcode=0,
                steps=False,
            )

        with When("I add comment to this column"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} COMMENT COLUMN Added1"
                f" 'Just a test column.'",
                exitcode=0,
                steps=False,
            )

        with Then("I check that column commented on all shards"):
            for name in self.context.cluster.nodes["clickhouse"][:9]:
                retry(self.context.cluster.node(name).query, timeout=100, delay=1)(
                    f"DESCRIBE TABLE {table_name} FORMAT TSV;",
                    exitcode=0,
                    message="Just a test column.",
                    steps=False,
                )

    finally:
        with Finally("I clean created data"):
            clean_coordination_on_all_nodes()


@TestScenario
def alter_modify_column(self):
    """Check ALTER query MODIFY COLUMN."""
    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test{uid}"

        with And("I create simple replicated table"):
            create_simple_table(
                node=self.context.cluster.node("clickhouse2"), table_name=table_name
            )

        with When("I add column to this table"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} ADD COLUMN Added1 UInt32 FIRST;",
                exitcode=0,
                steps=False,
            )

        with When("I change type of this column"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} MODIFY COLUMN Added1 UInt16",
                exitcode=0,
                steps=False,
            )

        with Then("I check that column type was modified on all shards"):
            for name in self.context.cluster.nodes["clickhouse"][:9]:
                retry(self.context.cluster.node(name).query, timeout=100, delay=1)(
                    f"DESC {table_name} FORMAT TSV;",
                    exitcode=0,
                    message="Added1\tUInt16",
                    steps=False,
                )

    finally:
        with Finally("I clean created data"):
            clean_coordination_on_all_nodes()


@TestScenario
def alter_modify_column_remove(self):
    """Check ALTER query MODIFY COLUMN REMOVE."""
    cluster_name = "'Cluster_3shards_with_3replicas'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test{uid}"

        with And("I create replicated table with TTL"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS"
                f" {table_name} on CLUSTER {cluster_name}"
                f" (event_time DateTime, UserID UInt64, Comment String) "
                "ENGINE = ReplicatedMergeTree('/clickhouse/tables/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}') "
                "ORDER BY tuple()"
                " TTL event_time + INTERVAL 3 MONTH "
                "SETTINGS min_bytes_for_wide_part = 0;",
                steps=False,
            )

        with When("I remove TTL"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} ON CLUSTER {cluster_name} REMOVE TTL;",
                exitcode=0,
                steps=False,
            )

        with And("I make insert in this table"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (now(), 1, 'username1');",
                exitcode=0,
                steps=False,
            )

        with And("I make insert in this table in TTL off period"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (now() - INTERVAL 4 MONTH, 2, 'username2');",
                exitcode=0,
                steps=False,
            )

        with And("I run OPTIMIZE to force TTL cleanup"):
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"OPTIMIZE TABLE {table_name} FINAL;", exitcode=0, steps=False
            )

        with Then("I check that TTL removed"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name} FORMAT TSV",
                exitcode=0,
                message="2",
                steps=False,
            )

    finally:
        with Finally("I clean created data"):
            clean_coordination_on_all_nodes()


@TestFeature
@Requirements(RQ_SRS_024_ClickHouse_Keeper_ClickHouseOperation_Alter("1.0"))
@Name("alter_column_distributed")
def feature(self):
    """Check data synchronization between replicas for different ALTER column DDL queries."""
    with Given("I start mixed ClickHouse cluster"):
        if self.context.ssl == "false":
            start_mixed_keeper()
        else:
            start_mixed_keeper_ssl()

    for scenario in loads(current_module(), Scenario):
        scenario()
