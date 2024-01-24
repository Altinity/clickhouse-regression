import random

from testflows.core import *

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


"""
RQ_SRS_038_DiskObjectStorageVFS_Parts_Fetch
RQ_SRS_038_DiskObjectStorageVFS_Parts_BackgroundCollapse
RQ_SRS_038_DiskObjectStorageVFS_Parts_Manipulation
"""


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
                final_part_count = get_active_part_count(node=nodes[0], table_name=table_name)
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
