#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from testflows.asserts import error


@TestScenario
@Name("attach or replace partition different policies")
def scenario(self, cluster, node="clickhouse1"):
    """Check that attaching or replacing partition from a table that has different
    storage policy fails.
    """
    name = "mt_attach_or_replace_different_policies"

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
        with When("I create first table table with one storage policy"):
            node.query(table % {"name": f"{name}_first", "policy": "only_jbod2"})

        with And("I create second table with another storage policy"):
            node.query(table % {"name": f"{name}_second", "policy": "only_jbod3"})

        with When("I insert some data into first table"):
            node.query(
                f"INSERT INTO {name}_first VALUES (toDate('2019-03-05'), 'hello')"
            )

        with And("I check what partitions are now available"):
            r = node.query(
                f"SELECT partition, name FROM system.parts WHERE table = '{name}_first'"
            ).output.strip()
            with Then("result should match the expected"):
                assert r == "201903\t201903_1_1_0", error()

        with When("I try to attach partition to the second table from the first table"):
            message = "Exception:"
            node.query(
                f"ALTER TABLE {name}_second ATTACH PARTITION '201903' FROM {name}_first",
                message=message,
            )

        with When(
            "I try to replace partition in the second table from the first table"
        ):
            message = "Exception:"
            node.query(
                f"ALTER TABLE {name}_second REPLACE PARTITION '201903' FROM {name}_first",
                message=message,
            )

    finally:
        with Finally("I drop all the tables"):
            node.query(f"DROP TABLE IF EXISTS {name}_first SYNC")
            node.query(f"DROP TABLE IF EXISTS {name}_second SYNC")
