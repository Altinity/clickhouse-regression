from testflows.core import *

from helpers.common import *
from helpers.tables import *

from attach.tests.common import *
from attach.requirements.requirements import (
    RQ_SRS_039_ClickHouse_Attach_ReplicaPath_ActivePath,
)


columns = [
    Column(name="id", datatype=Int32()),
    Column(name="time", datatype=DateTime()),
    Column(name="date", datatype=Date()),
    Column(name="extra", datatype=UInt64()),
    Column(name="Path", datatype=String()),
    Column(name="Time", datatype=DateTime()),
    Column(name="Value", datatype=Float64()),
    Column(name="Timestamp", datatype=Int64()),
    Column(name="sign", datatype=Int8()),
]


@TestScenario
@Repeat(5)
def check_active_path_convert(self, engine="ReplicatedMergeTree"):
    node = self.context.node
    node2 = self.context.node_2
    table1 = "table1_" + getuid()
    table2 = "table2_" + getuid()

    with Given("I create replicated table on cluster"):
        create_replicated_table(
            table_name=table1,
            engine=engine,
            cluster="replicated_cluster",
            node=node,
            table_id=table2,
            columns=columns,
            order_by="id",
        )

    with And("I insert data into the table"):
        node.query(f"INSERT INTO {table1} (id) SELECT * FROM numbers(100000000)")

    with And("I rename table"):
        node.query(f"RENAME TABLE {table1} TO {table2}")

    with And("I create MergeTree table and set convert flags"):
        non_replicated_engine = engine.replace("Replicated", "")
        create_table(
            name=table2,
            engine=non_replicated_engine,
            node=node2,
            columns=columns,
            order_by="id",
        )
        set_convert_flags(node=node2, table=table2)

    with When("I restart server"):
        node2.restart_clickhouse()

    with And("I check that table was converted"):
        node.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )
        node2.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )

    with And("I drop table"):
        drop_table(table=table2, node=node2)

    with And("I check that table was dropped"):
        node2.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )

    with And("I create replicated table on the second node back"):
        create_replicated_table(
            table_name=table2,
            engine=engine,
            node=node2,
            table_id=table2,
            columns=columns,
            order_by="id",
        )

    with And("I check system.replicas"):
        node.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )
        node2.query(
            f"SELECT table, replica_path, is_readonly, replica_is_active FROM system.replicas WHERE table = '{table1}' or table = '{table2}' FORMAT Vertical"
        )

    with Then("I expect at least one table to be in RO mode"):
        is_readonly_table1 = node2.query(
            f"SELECT is_readonly FROM system.replicas WHERE table = '{table1}'"
        )
        is_readonly_table2 = node2.query(
            f"SELECT is_readonly FROM system.replicas WHERE table = '{table2}'"
        )
        assert (is_readonly_table1.output != "0") ^ (is_readonly_table2.output != "0")


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
        uuid = getuid().replace("_", "-")
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

        if check_clickhouse_version("<22.9")(self):
            exitcode, message = 220, "DB::Exception: Duplicate interserver IO endpoint:"

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
    """Check that it is not possible to `ATTACH TABLE UUID` with the active path."""
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
        uuid = getuid().replace("_", "-")
        table2 = "table2_" + getuid()
        exitcode, message = (
            253,
            "DB::Exception: There already is an active replica with this replica path",
        )
        if check_clickhouse_version("<24.4")(self):
            exitcode, message = None, None

        if check_clickhouse_version("<22.9")(self):
            exitcode, message = 220, "DB::Exception: Duplicate interserver IO endpoint:"

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
        "ReplicatedReplacingMergeTree",
        "ReplicatedAggregatingMergeTree",
        "ReplicatedCollapsingMergeTree",
        "ReplicatedGraphiteMergeTree",
        "ReplicatedSummingMergeTree",
        "ReplicatedVersionedCollapsingMergeTree",
    ]
    with Pool(4) as executor:
        for engine in engines:
            Scenario(
                f"{engine} attach UUID",
                test=check_active_path_uuid,
                parallel=True,
                executor=executor,
                flags=TE,
            )(engine=engine)
            Scenario(
                f"{engine} attach detached",
                test=check_active_path_attach_detached,
                parallel=True,
                executor=executor,
                flags=TE,
            )(engine=engine)
        join()

    for engine in engines:
        Scenario(
            f"check active path convert {engine}",
            test=check_active_path_convert,
            flags=TE,
        )(engine=engine)
