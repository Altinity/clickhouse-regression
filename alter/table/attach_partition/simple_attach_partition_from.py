from testflows.core import *
from testflows.combinatorics import product

from alter.table.attach_partition.common import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import getuid
from helpers.tables import *


def get_node(self, table):
    """Returns first node for non-replicated tables and returns random node for replicated tables."""

    if table == "source":
        if "Replicated" in self.context.source_engine:
            return random.choice(
                [self.context.node_1, self.context.node_2, self.context.node_3]
            )
        else:
            return self.context.node_1

    elif table == "destination":
        if "Replicated" in self.context.destination_engine:
            return random.choice(
                [self.context.node_1, self.context.node_2, self.context.node_3]
            )
        else:
            return self.context.node_1


def attach_all(
    self,
    partition_ids,
    source_table_name,
    destination_table_name,
    exitcode=None,
    message=None,
):
    """Attach all partitions from source table to destination table."""

    for partition_id in partition_ids:
        query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
        self.context.node_1.query(
            query,
            exitcode=exitcode,
            message=message,
        )


def get_partition_ids(self, table_name, node):
    """Return list of partition ids for specified table."""
    partition_list_query = f"SELECT partition FROM system.parts WHERE table='{table_name}' ORDER BY partition_id FORMAT TabSeparated"
    return sorted(list(set(node.query(partition_list_query).output.split())))


@TestStep
def attach_all_partitions(self, source_table_name, destination_table_name, node):
    """Attach all partitions from source table to destination table."""
    partition_ids = get_partition_ids(self, source_table_name, node)
    attach_all(
        self,
        partition_ids,
        source_table_name,
        destination_table_name,
    )


@TestStep
def attach_partition_from_table(
    self,
    partition_key,
    source_table,
    destination_table,
):
    """Check `attach partition from` with different types of source and destination tables
    and different partition keys."""

    self.context.source_engine = source_table.__name__.split("_")[-1]
    self.context.destination_engine = destination_table.__name__.split("_")[-1]

    source_table_name = "source_" + getuid()
    destination_table_name = "destination_" + getuid()

    with Given(
        "I create two tables with specified engines and partition keys",
        description=f"""
            partition key: {partition_key}
            engines:
            source table engine: {self.context.source_engine}
            destination table engine: {self.context.destination_engine}
            """,
    ):
        source_table(
            table_name=source_table_name,
            partition_by=partition_key,
            node=self.context.node_1,
        )
        destination_table(
            table_name=destination_table_name,
            partition_by=partition_key,
            node=self.context.node_1,
        )

    with And("check that all replicas of source have the same data"):
        if "Replicated" in self.context.source_engine:
            for attempt in retries(timeout=300, delay=10):
                with attempt:
                    source_data_1 = self.context.node_1.query(
                        f"SELECT * FROM {source_table_name} ORDER BY tuple(*) FORMAT TabSeparated"
                    )
                    source_data_2 = self.context.node_2.query(
                        f"SELECT * FROM {source_table_name} ORDER BY tuple(*) FORMAT TabSeparated"
                    )
                    source_data_3 = self.context.node_3.query(
                        f"SELECT * FROM {source_table_name} ORDER BY tuple(*) FORMAT TabSeparated"
                    )
                    assert (
                        source_data_1.output == source_data_2.output
                        and source_data_1.output == source_data_3.output
                    ), error()

    with And("attach all partitions from source table to destination table"):
        attach_all_partitions(
            source_table_name=source_table_name,
            destination_table_name=destination_table_name,
            node=self.context.node_1,
        )

    with And("check that all replicas of destination table have the same data"):
        if "Replicated" in self.context.destination_engine:
            for attempt in retries(timeout=300, delay=10):
                with attempt:
                    destination_data_1 = self.context.node_1.query(
                        f"SELECT * FROM {destination_table_name} ORDER BY tuple(*) FORMAT TabSeparated"
                    )
                    destination_data_2 = self.context.node_2.query(
                        f"SELECT * FROM {destination_table_name} ORDER BY tuple(*) FORMAT TabSeparated"
                    )
                    destination_data_3 = self.context.node_3.query(
                        f"SELECT * FROM {destination_table_name} ORDER BY tuple(*) FORMAT TabSeparated"
                    )
                    assert (
                        destination_data_1.output == destination_data_2.output
                        and destination_data_1.output == destination_data_3.output
                    ), error()

    with Then(f"check that all partitions were attached correctly"):
        for attempt in retries(timeout=300, delay=10):
            with attempt:
                source_partition_data = get_node(self, "source").query(
                    f"SELECT * FROM {source_table_name} ORDER BY tuple(*) FORMAT TabSeparated"
                )
                destination_partition_data = get_node(self, "destination").query(
                    f"SELECT * FROM {destination_table_name} ORDER BY tuple(*) FORMAT TabSeparated"
                )
                assert (
                    destination_partition_data.output == source_partition_data.output
                ), error()


@TestScenario
@Repeat(100)
@Flags(TE)
def attach_partition_from(self):
    """Run test check with different partition keys and different engines for both source
    and destination tables."""

    partition_keys = {
        "intDiv(a,2)",
        "intDiv(a,3)",
        "intDiv(b,2)",
        "(a%2,b%2)",
        "(intDiv(a,2),intDiv(b,2))",
        "(intDiv(a,2),intDiv(b,2),intDiv(c,2))",
    }

    source_table_types = {
        partitioned_MergeTree,
        partitioned_ReplicatedMergeTree,
    }
    destination_table_types = {
        empty_partitioned_MergeTree,
        empty_partitioned_ReplicatedMergeTree,
    }

    table_pairs = product(source_table_types, destination_table_types)
    combinations = list(product(partition_keys, table_pairs))

    with Pool(6) as executor:
        for partition_key, tables in combinations:
            source_table, destination_table = tables
            partition_key_str = clean_name(partition_key)

            Scenario(
                f"partition key {partition_key_str} tables {source_table.__name__} {destination_table.__name__}",
                test=attach_partition_from_table,
                parallel=True,
                executor=executor,
            )(
                source_table=source_table,
                destination_table=destination_table,
                partition_key=partition_key,
            )
        join()


@TestFeature
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Replicas("1.0"),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom("1.0"),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_KeepData("1.0"),
)
@Name("check simple attach partition")
def feature(self):
    """Check that `ATTACH PARTITION FROM` works correctly."""
    Scenario("simple attach partition", test=attach_partition_from)()
