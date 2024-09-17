from testflows.core import *
from helpers.common import *
from helpers.tables import *


@TestScenario
@Flags(TE)
def check_replica_path_intersection(self):
    """Check that replica path intersection is not allowed."""
    first_table_name = "first_table_" + getuid()
    second_table_name = "second_table_" + getuid()
    node_1 = self.context.node_1
    node_2 = self.context.node_2

    with Given("I create `first table` on cluster with replica path of `second table`"):
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
            node=node_1,
        )

    with And("I insert data into `first table`"):
        node_1.query(f"INSERT INTO {first_table_name} SELECT * FROM numbers(100000000)")

    with And("I rename table 'first_table' to 'second_table'"):
        node_1.query(f"RENAME TABLE {first_table_name} TO {second_table_name}")

    with When(
        "I attach `second table` with the same replica path as `first table` on second node"
    ):
        uuid = getuid().replace("_", "-")
        if check_clickhouse_version(">=24.4")(self):
            exitcode, message = (
                253,
                "DB::Exception: There already is an active replica with this replica path",
            )
            node_2.query(
                f"ATTACH TABLE {second_table_name} UUID '{uuid}' (id Int32)"
                + f"ENGINE = ReplicatedMergeTree('/clickhouse/tables/replicated_cluster/default/{second_table_name}',"
                "'{replica}') ORDER BY id SETTINGS index_granularity = 8192",
                exitcode=exitcode,
                message=message,
            )
        else:
            with When(
                "I attach `second table` with the same replica path as `first table` on second node"
            ):
                uuid = getuid().replace("_", "-")
                node_2.query(
                    f"ATTACH TABLE {second_table_name} UUID '{uuid}' (id Int32)"
                    + f"ENGINE = ReplicatedMergeTree('/clickhouse/tables/replicated_cluster/default/{second_table_name}',"
                    "'{replica}') ORDER BY id SETTINGS index_granularity = 8192",
                )

            with And("I check system.replicas"):
                assert node_2.query(
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
                node_2.query(f"DROP TABLE {second_table_name} SYNC")

            with And("I create table `second table`"):
                columns = [
                    Column(name="id", datatype=Int32()),
                ]
                create_table(
                    name=second_table_name,
                    engine=f"ReplicatedMergeTree('/clickhouse/tables/replicated_cluster/default/{second_table_name}',"
                    + "'{replica}')",
                    columns=columns,
                    order_by="id",
                    node=node_2,
                )

            with Then("I insert data"):
                node_2.query(
                    f"INSERT INTO {second_table_name} SELECT * FROM numbers(400000000)"
                )

            with Then("I insert into first table"):
                node_2.query(
                    f"INSERT INTO {first_table_name} SELECT * FROM numbers(500000000)"
                )

            # sometimes I got Fatal


@TestFeature
@Name("replica path")
def feature(self):
    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node_1, self.context.node_2, self.context.node_3]
    Scenario(run=check_replica_path_intersection)
