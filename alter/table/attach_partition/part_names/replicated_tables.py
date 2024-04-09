import random

from alter.table.attach_partition.part_names.common_steps import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import getuid


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_PartNames_Replication("1.0")
)
def replicated_tables(self):
    """Check that parts in different replicas are the same when replication queue is empty."""
    node = self.context.node

    source_table = "source_" + getuid()
    destination_table = "destination_" + getuid()

    with Given("I create a source table on cluster with data"):
        create_table_on_cluster_with_data(
            table_name=source_table,
            cluster="replicated_cluster_secure",
            order_by="sign",
            partition_by="id%20",
            number_of_rows=100000000,
        )

    with And("I create an empty destination table on cluster"):
        create_table_on_cluster_with_data(
            table_name=destination_table,
            cluster="replicated_cluster_secure",
            order_by="sign",
            partition_by="id%20",
            number_of_rows=0,
        )

    with And("I update the source table"):
        update_table(table_name=source_table, update_column="a", node=node)
