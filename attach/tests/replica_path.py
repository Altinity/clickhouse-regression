from testflows.core import *
from helpers.common import *
from helpers.tables import *


@TestScenario
@Flags(TE)
def check_replica_path_intersection(self):
    """Check that replica path intersection is not allowed."""
    first_table_name = "first_table_" + getuid()
    second_table_name = "second_table_" + getuid()

    with Given("I create table on cluster"):
        columns = [
            Column(name="id", datatype=Int32()),
        ]
        create_table(
            name=first_table_name,
            engine=f"ReplicatedMergeTree('/clickhouse/tables/replicated_cluster/default/{second_table_name}',"
            + "'{replica}')",
            cluster="replicated_cluster",
            columns=columns,
            order_by="id",
            node=self.context.node_1,
        )

    with And("I insert data"):
        self.context.node_1.query(
            f"INSERT INTO {first_table_name} SELECT * FROM numbers(100000000)"
        )

    with And("I rename table"):
        self.context.node_1.query(
            f"RENAME TABLE {first_table_name} TO {second_table_name}"
        )

    with When("I attach table"):
        uuid = getuid()
        self.context.node_2.query(
            f"ATTACH TABLE {second_table_name} UUID '{uuid}' (id Int32)"
            + f"ENGINE = ReplicatedMergeTree('/clickhouse/tables/replicated_cluster/default/{second_table_name}',"
            "'{replica}') ORDER BY id SETTINGS index_granularity = 8192"
        )

    with And("I check system.replicas"):
        assert self.context.node_2.query(
            f"""
            SELECT
                table,
                is_readonly,
                replica_name,
                replica_path,
                replica_is_active
            FROM system.replicas
            WHERE table IN ('{second_table_name}', '{first_table_name}')
            FORMAT PrettyCompactMonoBlock
            """
        )

    with And("I drop second table"):
        self.context.node_2.query(f"DROP TABLE {second_table_name} SYNC")

    with And("I create table second table"):
        columns = [
            Column(name="id", datatype=Int32()),
        ]
        create_table(
            name=second_table_name,
            engine=f"ReplicatedMergeTree('/clickhouse/tables/replicated_cluster/default/{second_table_name}',"
            + "'{replica}')",
            columns=columns,
            order_by="id",
            node=self.context.node_2,
        )

    with And("I insert data"):
        self.context.node_2.query(
            f"INSERT INTO {second_table_name} SELECT * FROM numbers(400000000)"
        )

    with And("I insert into first table"):
        self.context.node_2.query(
            f"INSERT INTO {first_table_name} SELECT * FROM numbers(500000000)"
        )


@TestFeature
@Name("replica_path")
def feature(self):
    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node_1, self.context.node_2, self.context.node_3]
    Scenario(run=check_replica_path_intersection)
