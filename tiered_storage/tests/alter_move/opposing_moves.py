#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import random

from testflows.core import *
from testflows.asserts import error
from helpers.cluster import QueryRuntimeException
from tiered_storage.tests.common import get_random_string


@TestScenario
@Name("opposing moves")
def scenario(self, cluster, node="clickhouse1"):
    """Check that moving the same partition in parallel to opposing disks
    does not cause any crashes or data duplication.
    """
    name = "mt_opposing_moves"

    with Given("cluster node"):
        node = cluster.node(node)

    table = """
        CREATE TABLE %(name)s (
            d Date,
            s String
        ) ENGINE = MergeTree
        ORDER BY tuple()
        PARTITION BY toYYYYMM(d)
        SETTINGS storage_policy='%(policy)s'
        """
    try:
        with When("I create a table with a storage policy that has three disks"):
            node.query(table % {"name": name, "policy": "fast_med_and_slow"})

        with When("I insert some data to create one large part"):
            data = []
            dates = []
            for i in range(28):
                data.append(
                    get_random_string(cluster, 1024 * 1024, steps=False)
                )  # 1MB value
                dates.append("toDate('2019-03-05')")
            values = ",".join(["(" + d + ", '" + s + "')" for d, s in zip(dates, data)])
            node.query(f"INSERT INTO {name} VALUES {values}", steps=False)

        with And("I check what partitions are now available"):
            r = node.query(
                f"SELECT partition, name FROM system.parts WHERE table = '{name}'"
            ).output.strip()
            with Then("result should match the expected"):
                assert r == "201903\t201903_1_1_0", error()

        def alter_move(num=30):
            disks = ["jbod1", "jbod2", "external"]
            for i in range(num):
                disk = disks[random.randint(0, 2)]
                with When(f"#{i} I move partition to disk {disk}"):
                    try:
                        node.query(
                            f"ALTER TABLE {name} MOVE PARTITION 201903 TO DISK '{disk}'",
                            raise_on_exception=True,
                        )
                    except QueryRuntimeException as e:
                        msg0 = "Exception: Nothing to move"
                        msg1 = "Exception: Cannot move part '201903_1_1_0' because it's participating in background process"
                        msg2 = "Exception: Move is not possible"
                        msg3 = "Exception: All parts of partition '201903' are already on disk"
                        assert (
                            msg0 in str(e)
                            or msg1 in str(e)
                            or msg2 in str(e)
                            or msg3 in str(e)
                        ), error()

        with When("in parallel I perform opposing moves"):
            with Pool(15) as p:
                tasks = []
                for i in range(15):
                    tasks.append(p.submit(alter_move))
                for task in tasks:
                    task.result(timeout=600)

        with When("I check the data in the table"):
            r = node.query(f"SELECT count() FROM {name}").output.strip()
            with Then("number of rows should stay the same"):
                assert r == "28", error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")
