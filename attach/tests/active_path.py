import time

from testflows.core import *
from helpers.common import *
from helpers.tables import *
from attach.tests.common import *
from attach.requirements.requirements import (
    RQ_SRS_039_ClickHouse_Attach_ReplicaPath_ActivePath,
)


@TestStep
def get_table_path(self, node, table):
    return node.query(
        f"SELECT data_paths FROM system.tables WHERE table = '{table}'"
    ).output.strip("'[]\n")


@TestStep
def set_convert_flags(self, node, table):
    node.command(f"touch {get_table_path(node=node, table=table)}convert_to_replicated")


@TestScenario
def check_active_path_convert(self, engine):
    node = self.context.node
    table1 = "table1_" + getuid()
    table2 = "table2_" + getuid()

    with Given("I create MergeTree table and set convert flags"):
        node.query(
            f"CREATE TABLE {table1} ( A Int64, D Date, S String ) ENGINE MergeTree() PARTITION BY toYYYYMM(D) ORDER BY A"
        )

    with Given("I create replicated table"):
        node.query(
            f"CREATE TABLE {table2} ( A Int64, D Date, S String ) ENGINE ReplicatedMergeTree('/clickhouse/tables/replicated_cluster/{{database}}/{table1}', '{{replica}}') PARTITION BY toYYYYMM(D) ORDER BY A"
        )
        node.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )
        time.sleep(10)

    with Given("I create MergeTree table and set convert flags"):
        set_convert_flags(node=node, table=table1)

    with When("I restart server"):
        node.restart_clickhouse()

    with And("I check that table was converted"):
        node.query(
            f"SELECT name, engine_full, create_table_query FROM system.tables WHERE name = '{table1}' or name = '{table2}'"
        )
        node.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )


@TestScenario
def check_active_path_convert_3(self, engine):
    node = self.context.node
    table1 = "table1_" + getuid()
    table2 = "table2_" + getuid()

    with Given("I create replicated table"):
        node.query(
            f"CREATE TABLE {table2} ( A Int64, D Date, S String ) ENGINE ReplicatedMergeTree('/clickhouse/tables/replicated_cluster/{{database}}/{table1}', '{{replica}}') PARTITION BY toYYYYMM(D) ORDER BY A"
        )
        node.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )

    with Given("I create MergeTree table and set convert flags"):
        node.query(
            f"CREATE TABLE {table1} ( A Int64, D Date, S String ) ENGINE MergeTree() PARTITION BY toYYYYMM(D) ORDER BY A"
        )

    with Given("I set convert flags"):
        set_convert_flags(node=node, table=table1)

    with When("I restart server"):
        node.restart_clickhouse()

    with And("I check that table was converted"):
        node.query(
            f"SELECT name, engine_full, create_table_query FROM system.tables WHERE name = '{table1}' or name = '{table2}'"
        )
        node.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )


@TestScenario
def check_active_path_convert_2(self, engine):
    node = self.context.node
    node2 = self.context.node_2
    table1 = "table1_" + getuid()
    table2 = "table2_" + getuid()

    with Given("I create MergeTree table and set convert flags"):
        node2.query(
            f"CREATE TABLE {table2} ( A Int64, D Date, S String ) ENGINE MergeTree() PARTITION BY toYYYYMM(D) ORDER BY A"
        )

    with Given("I set convert flags"):
        # node2.query(f"CREATE TABLE {table2} ( A Int64, D Date, S String ) ENGINE MergeTree() PARTITION BY toYYYYMM(D) ORDER BY A")
        set_convert_flags(node=node2, table=table2)

    with Given("I create replicated table on cluster"):
        node.query(
            f"CREATE TABLE {table1} ON CLUSTER replicated_cluster ( A Int64, D Date, S String ) ENGINE ReplicatedMergeTree('/clickhouse/tables/replicated_cluster/{{database}}/{table2}', '{{replica}}') PARTITION BY toYYYYMM(D) ORDER BY A"
        )
        node.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )

    with And("I insert data into the table"):
        node.query(f"INSERT INTO {table1} (A) SELECT number FROM numbers(10)")

    with And("I rename table"):
        node.query(f"RENAME TABLE {table1} TO {table2}")

    with When("I restart server"):
        node2.restart_clickhouse()

    with And("I check that table was converted"):
        # node.query(f"SELECT name, engine_full, create_table_query FROM system.tables WHERE name = '{table1}' or name = '{table2}'")
        node.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )
        # node2.query(f"SELECT name, engine_full, create_table_query FROM system.tables WHERE name = '{table1}' or name = '{table2}'")
        node2.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )

    with And("I drop table and create it back"):
        node2.query(f"DROP TABLE {table2} SYNC")
        node2.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )
        node2.query(
            f"CREATE TABLE {table2} ( A Int64, D Date, S String ) ENGINE ReplicatedMergeTree('/clickhouse/tables/replicated_cluster/{{database}}/{table2}', '{{replica}}') PARTITION BY toYYYYMM(D) ORDER BY A"
        )

    with And("I check that table was converted"):
        # node.query(f"SELECT name, engine_full, create_table_query FROM system.tables WHERE name = '{table1}' or name = '{table2}'")
        node.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )
        # node2.query(f"SELECT name, engine_full, create_table_query FROM system.tables WHERE name = '{table1}' or name = '{table2}'")
        node2.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )

    with And("I insert data into both tables on second node"):
        node2.query(f"INSERT INTO {table1} (A) SELECT * FROM numbers(400000000)")
        node2.query(f"INSERT INTO {table2} (A) SELECT * FROM numbers(400000000)")

    # with And("I select data from both tables"):
    #     node2.query(f"SELECT * FROM {table1}")
    #     node2.query(f"SELECT * FROM {table2}")


@TestScenario
def check_active_path_attach_detached(self, engine):
    """Check that it is not possible to attach detached table with the active path."""
    node = self.context.node_1
    table_id = getuid()

    with Given("I create replicated table"):
        table1 = "table1_" + getuid()
        for ch_node in self.context.ch_nodes:
            create_replicated_table(
                table_name=table1, table_id=table_id, engine=engine, node=ch_node
            )

    with And("I detach table on the first node"):
        detach_table(table=table1, node=self.context.node_1)

    with And("I attach table with the same replica path on the first node"):
        table2 = "table2_" + getuid()
        uuid = getuid()
        attach_table_UUID(
            table=table2,
            table_id=table_id,
            uuid=uuid,
            engine=engine,
            node=self.context.node_1,
        )

    with And("I insert data into the second table"):
        self.context.node_1.query(f"INSERT INTO {table2} (extra, sign) VALUES (2, 1)")

    with And("I attach first table back"):
        exitcode, message = (
            253,
            "DB::Exception: There already is an active replica with this replica path",
        )
        if check_clickhouse_version("<24.4")(self):
            exitcode, message = None, None

        node.query(f"ATTACH TABLE {table1}", exitcode=exitcode, message=message)

    if check_clickhouse_version("<24.4")(self):
        with Then("I expect first table to be in RO mode"):
            assert (
                node.query(
                    f"SELECT is_readonly FROM system.replicas WHERE table = '{table1}' FORMAT TabSeparated"
                ).output
                == "1"
            )
    else:
        with Then("I check that first table was not attached"):
            assert (
                node.query(
                    f"SELECT count() FROM system.replicas WHERE table = '{table1}' FORMAT TabSeparated"
                ).output
                == "0"
            )


@TestScenario
def check_active_path_uuid(self, engine):
    """Check that it is not possible to `ATTACH TABLE UUID'` with the active path."""
    node = self.context.node
    table_id = getuid()

    with Given("I create database"):
        database_name = create_database()

    with And("I create replicated table"):
        table1 = "table1_" + getuid()
        create_replicated_table(
            table_name=table1,
            database_name=database_name,
            table_id=table_id,
            engine=engine,
        )

    with Then("I attach table with same replica path and expect an exception"):
        uuid = getuid()
        table2 = "table2_" + getuid()
        exitcode, message = (
            253,
            "DB::Exception: There already is an active replica with this replica path",
        )
        if check_clickhouse_version("<24.4")(self):
            exitcode, message = None, None

        attach_table_UUID(
            table=table2,
            table_id=table_id,
            engine=engine,
            uuid=uuid,
            database_name=database_name,
            exitcode=exitcode,
            message=message,
        )

    if check_clickhouse_version("<24.4")(self):
        with Then("I expect second table to be in RO mode"):
            assert (
                node.query(
                    f"SELECT is_readonly FROM system.replicas WHERE table = '{table2}' FORMAT TabSeparated"
                ).output
                == "1"
            )
    else:
        with Then("I check that second table was not attached"):
            assert (
                node.query(
                    f"SELECT count() FROM system.replicas WHERE table = '{table2}' FORMAT TabSeparated"
                ).output
                == "0"
            )


@TestFeature
@Name("active path")
@Requirements(RQ_SRS_039_ClickHouse_Attach_ReplicaPath_ActivePath)
def feature(self):
    """Check that it is not possible to attach a table with the active path."""
    engines = [
        "ReplicatedMergeTree",
        #     "ReplicatedReplacingMergeTree",
        #     "ReplicatedAggregatingMergeTree",
        #     "ReplicatedCollapsingMergeTree",
        #     "ReplicatedGraphiteMergeTree",
        #     "ReplicatedSummingMergeTree",
        #     "ReplicatedVersionedCollapsingMergeTree",
    ]
    with Pool(4) as executor:
        for engine in engines:
            # Scenario(
            #     f"{engine} attach UUID",
            #     test=check_active_path_uuid,
            #     parallel=True,
            #     executor=executor,
            #     flags=TE,
            # )(engine=engine)
            # Scenario(
            #     f"{engine} attach detached",
            #     test=check_active_path_attach_detached,
            #     parallel=True,
            #     executor=executor,
            #     flags=TE,
            # )(engine=engine)
            Scenario(
                f"{engine} attach convert",
                test=check_active_path_convert_2,
                parallel=True,
                executor=executor,
                flags=TE,
            )(engine=engine)
        join()
