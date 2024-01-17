from testflows.core import *

from alter.table.attach_partition.common import (
    create_partitioned_table_with_data,
    create_empty_partitioned_table,
)
from alter.table.attach_partition.requirements.requirements import *
from helpers.common import getuid, attach_partition_from
from helpers.tables import Column
from helpers.datatypes import UInt64, UInt16


@TestScenario
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_TableName("1.0"))
def check_table_name(self, source_table_name, destination_table_name, with_id):
    """Check if table name is valid."""

    node = self.context.node

    with Given(
        "I create source and destination tables",
        description=f"""          
            Names:
            source table name: {destination_table_name}
            destination table name: {source_table_name}
            """,
    ):
        create_partitioned_table_with_data(
            table_name=source_table_name,
            partition_by="a",
        )
        create_partitioned_table_with_data(
            table_name=destination_table_name,
            partition_by="a",
            bias=5,
        )

    if with_id:
        partition_list_query = f"SELECT partition_id FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id"
    else:
        partition_list_query = f"SELECT partition FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id"

    partition_ids = sorted(list(set(node.query(partition_list_query).output.split())))
    note(partition_ids)
    pause()

    if "source" in source_table_name and "destination" in destination_table_name:
        for partition_id in partition_ids:
            if with_id:
                query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition_id}' FROM {source_table_name}"
            else:
                query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
            node.query(query)
    elif "source" in destination_table_name and "destination" in source_table_name:
        pass
    else:
        for partition_id in partition_ids:
            if with_id:
                query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition_id}' FROM {source_table_name}"
            else:
                query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
            node.query(query, exitcode=62, message="Syntax error: failed at position")


@TestSketch(Scenario)
@Flags(TE)
def table_name(self, with_id=False):
    """Run test check with different table names to see if `attach partition from` is possible."""

    table_names = {
        "source_" + getuid(),
        "destination_" + getuid(),
        "1",
        "!@DL",
        ".",
        # utf8 chars
        # very long string
        # all ascii chars
    }

    check_table_name(
        source_table_name=either(*table_names),
        destination_table_name=either(*table_names),
        with_id=with_id,
    )


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions("1.0"))
@Name("miscellaneous")
def feature(self, node="clickhouse1"):

    self.context.node = self.context.cluster.node(node)

    Scenario("check table names with id", test=table_name)(with_id=True)
    Scenario("check table names without id", test=table_name)(with_id=False)
