import random

from testflows.core import *

from helpers.common import *
from helpers.tables import Column
from helpers.datatypes import UInt64, UInt16

from alter.table.attach_partition.common import (
    create_partitioned_table_with_data,
    version_when_attach_partition_with_different_keys_merged,
)
from alter.table.attach_partition.requirements.requirements import *
from alter.table.attach_partition.partition_key import valid_partition_key_pair


@TestScenario
def check_restart_clickhouse_server(
    self, node=None, source_partition_key="a", destination_partition_key="a"
):
    """Check that I can use newly attached data after restart ClickHouse server."""
    if check_clickhouse_version(
        f"<{version_when_attach_partition_with_different_keys_merged}"
    )(self):
        if source_partition_key != destination_partition_key:
            skip(
                f"`attach partition from` with tables that have different partition keys are not supported before {version_when_attach_partition_with_different_keys_merged}"
            )

    if node is None:
        node = self.context.node

    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given("I create source and destination tables"):
        create_partitioned_table_with_data(
            table_name=destination_table,
            partition_by=destination_partition_key,
        )
        create_partitioned_table_with_data(
            table_name=source_table,
            partition_by=source_partition_key,
        )

    if check_clickhouse_version(
        f">={version_when_attach_partition_with_different_keys_merged}"
    )(self):
        with And(
            "I add setting to allow alter partition with different partition keys"
        ):
            node.query(
                f"ALTER TABLE {destination_table} MODIFY SETTING allow_experimental_alter_partition_with_different_key=1"
            )

    with And("I get the list of partitions and validate partition keys pair"):
        partition_list_query = f"SELECT partition FROM system.parts WHERE table='{source_table}' ORDER BY partition_id FORMAT TabSeparated"

        partition_ids = sorted(
            list(set(node.query(partition_list_query).output.split()))
        )
        valid, _ = valid_partition_key_pair(
            source_partition_key, destination_partition_key
        )

    with And(
        "I try to attach partition to the destination table from the source table"
    ):
        if valid:
            attach_partition_from(
                destination_table=destination_table,
                source_table=source_table,
                partition=random.choice(partition_ids),
            )

    with And("I save the data from the destination table"):
        destination_data_before = node.query(
            f"SELECT * FROM {destination_table} ORDER BY tuple(*) FORMAT TabSeparated"
        ).output

    with And("restarting the server"):
        node.restart()

    with Then("I check that the data is still on the destination table"):
        destination_data_after = node.query(
            f"SELECT * FROM {destination_table} ORDER BY tuple(*) FORMAT TabSeparated"
        ).output

        assert destination_data_before == destination_data_after

    with And("I check that I can use other ALTERs on the table after restart"):
        if valid:
            destination_partition_list_query = f"SELECT partition FROM system.parts WHERE table='{destination_table}' ORDER BY partition_id FORMAT TabSeparated"
            destination_partition_ids = sorted(
                list(set(node.query(destination_partition_list_query).output.split()))
            )
            partition = random.choice(destination_partition_ids)

            data_before = node.query(
                f"SELECT * FROM {destination_table} ORDER BY tuple(*) FORMAT TabSeparated"
            ).output
            node.query(f"ALTER TABLE {destination_table} DETACH PARTITION {partition}")
            data_after = node.query(
                f"SELECT * FROM {destination_table} ORDER BY tuple(*) FORMAT TabSeparated"
            )
            for attempt in retries(timeout=30, delay=2):
                with attempt:
                    assert data_after.output != data_before, error()

            node.query(f"ALTER TABLE {destination_table} ATTACH PARTITION {partition}")
            data_after = node.query(
                f"SELECT * FROM {destination_table} ORDER BY tuple(*) FORMAT TabSeparated"
            )
            for attempt in retries(timeout=30, delay=2):
                with attempt:
                    assert data_after.output == data_before, error()


@TestSketch(Scenario)
@Flags(TE)
def restart_clickhouse_server(self):
    """Check that I can use newly attached data after restart ClickHouse server with
    differrent source and destination partition keys."""

    source_partition_keys = {
        "tuple()",
        "a",
        "a%2",
        "a%3",
        "intDiv(a,2)",
        "intDiv(a,3)",
        "b",
        "b%2",
        "intDiv(b,2)",
        "(a,b)",
        "(a%2,b%2)",
        "(a,intDiv(b,2))",
        "(a,b%2)",
        "(intDiv(a,2),b)",
        "(intDiv(a,2),intDiv(b,2))",
        "(b,a)",
        "(b%2,a%2)",
        "(intDiv(b,2),intDiv(a,2))",
        "(b,c)",
        "(a,c)",
        "(a,b,c)",
        "(a%2,b%2,c%2)",
        "(intDiv(a,2),intDiv(b,2),intDiv(c,2))",
        "(a,c,b)",
    }

    destination_partition_keys = {
        "tuple()",
        "a",
        "a%2",
        "a%3",
        "intDiv(a,2)",
        "intDiv(a,3)",
        "b",
        "b%2",
        "intDiv(b,2)",
        "(a,b)",
        "(a%2,b%2)",
        "(a,intDiv(b,2))",
        "(a,b%2)",
        "(intDiv(a,2),b)",
        "(intDiv(a,2),intDiv(b,2))",
        "(b,a)",
        "(b%2,a%2)",
        "(intDiv(b,2),intDiv(a,2))",
        "(b,c)",
        "(a,c)",
        "(a,b,c)",
        "(a%2,b%2,c%2)",
        "(intDiv(a,2),intDiv(b,2),intDiv(c,2))",
        "(c,b,a)",
    }

    check_restart_clickhouse_server(
        source_partition_key=either(*source_partition_keys),
        destination_partition_key=either(*destination_partition_keys),
    )


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions("1.0"))
@Name("restart clickhouse server")
def feature(self, node="clickhouse1"):
    """Check that I can use newly attached data after restart ClickHouse server."""
    self.context.node = self.context.cluster.node(node)
    Scenario(run=restart_clickhouse_server)
