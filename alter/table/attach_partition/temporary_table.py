from testflows.asserts import *
from testflows.core import *
from testflows.combinatorics import product

from alter.table.attach_partition.common import *
from alter.table.attach_partition.requirements.requirements import *
from helpers.common import getuid, attach_partition, detach_partition


timeout = 30
delay = 2


@TestCheck
def check_attach_partition_detached_with_temporary_tables(self, table, engine):
    """Check if it is possible to use attach partition with temporary tables."""

    node = self.context.node
    table_name = getuid()

    with Given("I open a single clickhouse instance"):
        with node.client() as client:
            with Given(
                "I create a table",
                description=f"""
                    table type: {table.__name__}
                    table engine: {engine}
                    """,
            ):
                table(
                    table_name=table_name,
                    engine=engine,
                    partition_by="a",
                    node=client,
                )

                table_before = client.query(
                    f"SELECT * FROM {table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
                )

            with And(
                "I detach partition from the table and check that partition was detached"
            ):
                if "temporary" in table.__name__ and check_clickhouse_version(
                    "<=23.10"
                )(self):
                    exitcode = 60
                else:
                    exitcode = 0

                note(f"exitcode should be {exitcode}")

                detach_partition(
                    table=table_name, partition=1, node=client, exitcode=exitcode
                )
                if exitcode == 0:
                    table_after_detach = client.query(
                        f"SELECT * FROM {table_name} ORDER BY a,b,c,extra FORMAT TabSeparated",
                    )
                else:
                    table_after_detach = client.query(
                        f"SELECT * FROM {table_name} ORDER BY a,b,c,extra FORMAT TabSeparated",
                        errorcode=exitcode,
                    )

                if exitcode == 0:
                    for attempt in retries(timeout=timeout, delay=delay):
                        with attempt:
                            assert table_before != table_after_detach, error()

            with And("I attach detached partition back"):
                if "temporary" in table.__name__ and check_clickhouse_version(
                    "<=23.10"
                )(self):
                    exitcode = 60
                else:
                    exitcode = 0
                attach_partition(
                    table=table_name, partition=1, node=client, exitcode=exitcode
                )

            if exitcode == 0:
                with Then(
                    "I check that data is the same as it was before attach detach"
                ):
                    table_after = client.query(
                        f"SELECT * FROM {table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
                    )
                    for attempt in retries(timeout=timeout, delay=delay):
                        with attempt:
                            assert table_before == table_after, error()


@TestScenario
def check_attach_partition_from_with_temporary_tables(
    self, source_table, destination_table, source_table_engine, destination_table_engine
):
    """Check if it is possible to use attach partition from with temporary tables."""

    node = self.context.node
    destination_table_name = "destination_" + getuid()
    source_table_name = "source_" + getuid()

    with Given("I create replicated tables if they are in combination"):
        if "replicated" in source_table.__name__:
            source_table(
                table_name=source_table_name,
                engine=source_table_engine,
                partition_by="a",
            )
        if "replicated" in destination_table.__name__:
            destination_table(
                table_name=destination_table_name,
                engine=destination_table_engine,
                partition_by="a",
            )

    with Given("I open a single clickhouse instance"):
        with node.client() as client:
            with Given(
                "I create two tables with specified engines and types",
                description=f"""
                    types:
                    source table: {source_table.__name__}
                    destination table: {destination_table.__name__}
                    engines:
                    source table engine: {source_table_engine}
                    destination table engine: {destination_table_engine}
                    """,
            ):
                if "replicated" not in source_table.__name__:
                    source_table(
                        table_name=source_table_name,
                        engine=source_table_engine,
                        partition_by="a",
                        node=client,
                    )
                if "replicated" not in destination_table.__name__:
                    destination_table(
                        table_name=destination_table_name,
                        engine=destination_table_engine,
                        partition_by="a",
                        node=client,
                    )

            with And(
                "I attach all partitions from source table to the destination table"
            ):
                if (
                    "temporary" in destination_table.__name__
                    and check_clickhouse_version("<=23.10")(self)
                ):
                    exitcode = 60
                elif (
                    "temporary" in destination_table.__name__ + source_table.__name__
                    and check_clickhouse_version("<=23.4")(self)
                ):
                    exitcode = 60
                else:
                    exitcode = 0

                note(f"exitcode should be {exitcode}")

                for partition_id in [
                    "1",
                    "2",
                    "3",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "17",
                    "18",
                    "19",
                ]:
                    query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
                    if exitcode == 0:
                        client.query(query)
                    else:
                        client.query(query, errorcode=exitcode)

            if exitcode == 0:
                with Then(
                    f"I check that partitions were attached to the destination table"
                ):
                    for attempt in retries(timeout=30, delay=2):
                        with attempt:
                            source_partition_data = client.query(
                                f"SELECT a,b,c,extra FROM {source_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
                            )
                            destination_partition_data = client.query(
                                f"SELECT a,b,c,extra FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
                            )
                            assert (
                                source_partition_data.output
                                == destination_partition_data.output
                            ), error()

    with And(f"I check that all replicas of destination table have same data:"):
        if "replicated" in destination_table.__name__:
            destination_partition_data_1 = self.context.node_1.query(
                f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
            )
            destination_partition_data_2 = self.context.node_2.query(
                f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
            )
            destination_partition_data_3 = self.context.node_3.query(
                f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
            )
            for attempt in retries(timeout=30, delay=2):
                with attempt:
                    assert (
                        destination_partition_data_1.output
                        == destination_partition_data_2.output
                        == destination_partition_data_3.output
                    )


@TestSketch(Scenario)
@Flags(TE)
def attach_partition_detached_with_temporary_tables(self):
    """Run test check with different table types to see if attach partition is possible."""
    tables = {
        create_regular_partitioned_table_with_data,
        create_temporary_partitioned_table_with_data,
    }
    engines = {
        "MergeTree",
        "ReplacingMergeTree",
        "AggregatingMergeTree",
        "SummingMergeTree",
        "CollapsingMergeTree",
        "VersionedCollapsingMergeTree",
        "GraphiteMergeTree",
    }

    check_attach_partition_detached_with_temporary_tables(
        table=either(*tables),
        engine=either(*engines),
    )


@TestSketch(Scenario)
@Flags(TE)
def attach_partition_from_with_temporary_tables(self):
    """Run test check with different table types to see if attach partition is possible."""
    source_tables = {
        create_regular_partitioned_table_with_data,
        create_temporary_partitioned_table_with_data,
        create_partitioned_replicated_table_with_data,
    }
    destination_tables = {
        create_empty_regular_partitioned_table,
        create_empty_temporary_partitioned_table,
        create_empty_partitioned_replicated_table,
    }
    engines = {
        "MergeTree",
        "ReplacingMergeTree",
        "AggregatingMergeTree",
        "SummingMergeTree",
        "CollapsingMergeTree",
        "VersionedCollapsingMergeTree",
        "GraphiteMergeTree",
    }

    check_attach_partition_from_with_temporary_tables(
        source_table=either(*source_tables),
        destination_table=either(*destination_tables),
        source_table_engine=either(*engines),
        destination_table_engine=either(*engines),
    )


@TestFeature
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_FromTemporaryTable("1.0")
)
@Name("temporary table")
def feature(self):
    """Check that it is possible to use temporary tables to attach partition from the source table to the destination table."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node("clickhouse1"),
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]

    Scenario(run=attach_partition_detached_with_temporary_tables)
    Scenario(run=attach_partition_from_with_temporary_tables)
