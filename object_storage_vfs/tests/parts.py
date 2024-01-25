import random

from testflows.core import *

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


"""
RQ_SRS_038_DiskObjectStorageVFS_Parts_BackgroundCollapse
RQ_SRS_038_DiskObjectStorageVFS_Parts_Manipulation
"""


@TestOutline(Scenario)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Parts_Fetch("0.0"))
@Examples("fetch_item", [["PARTITION 2"], ["PART '2_0_0_0'"]])
def fetch(self, fetch_item):
    """Test fetching a new part from another replica."""

    nodes = self.context.ch_nodes
    node = nodes[0]

    with Given("I have two replicated tables"):
        _, source_table_name = replicated_table_cluster(
            storage_policy="external_vfs", partition_by="key % 4"
        )
        _, destination_table_name = replicated_table_cluster(
            storage_policy="external_vfs", partition_by="key % 4"
        )

    with And("I insert data into the first table"):
        insert_random(node=node, table_name=source_table_name)

    with And("I count the rows in a partition"):
        # Can also get this information from system.parts
        r = node.query(f"SELECT count() FROM {source_table_name} where key % 4 = 2;")
        row_count = int(r.output)

    with When("I fetch a partition from the first table"):
        node.query(
            f"ALTER TABLE {destination_table_name} FETCH {fetch_item} FROM '/clickhouse/tables/{source_table_name}'"
        )

    with And("I attach the partition to the second table"):
        node.query(f"ALTER TABLE {destination_table_name} ATTACH {fetch_item}")

    with Then("I check the number of rows on the second table on all nodes"):
        for node in nodes:
            retry(assert_row_count, timeout=15, delay=1)(
                node=node, table_name=destination_table_name, rows=row_count
            )


@TestStep(When)
def get_active_part_count(self, node, table_name):
    r = node.query(f"SELECT sum(active) FROM system.parts where table='{table_name}'")
    return int(r.output)


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Parts_Optimize("0.0"))
def optimize(self):
    """Check that OPTIMIZE works as expected on VFS"""

    table_name = "opt_table"
    nodes = self.context.ch_nodes
    n_inserts = 3000
    insert_size = 1000

    with Given("I have a vfs table"):
        replicated_table_cluster(table_name=table_name, storage_policy="external_vfs")

    with And("I perform many inserts"):
        for _ in range(n_inserts):
            By(test=insert_random, parallel=True)(
                node=random.choice(nodes), table_name=table_name, rows=insert_size
            )
        join()

    with When("Check the number of active parts"):
        # SELECT count(), sum(active) FROM system.parts where table='opt_table'
        initial_part_count = get_active_part_count(node=nodes[0], table_name=table_name)

    with And("I perform OPTIMIZE"):
        nodes[0].query(f"OPTIMIZE TABLE {table_name}")

    with Then("There should be fewer active parts"):
        optimized_part_count = get_active_part_count(
            node=nodes[0], table_name=table_name
        )
        assert optimized_part_count < initial_part_count, error()

    with When("I perform OPTIMIZE FINAL"):
        nodes[0].query(f"OPTIMIZE TABLE {table_name} FINAL")

    with Then("There should be fewer active parts"):
        for attempt in retries(timeout=15, delay=1):
            with attempt:
                final_part_count = get_active_part_count(
                    node=nodes[0], table_name=table_name
                )
                assert final_part_count < optimized_part_count, error()

    with Then("There should be only one active part"):
        assert final_part_count == 1, error()


@TestFeature
@Name("parts")
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
