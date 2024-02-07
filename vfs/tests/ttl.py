#!/usr/bin/env python3
import time, datetime

from testflows.core import *

from vfs.tests.steps import *
from vfs.requirements import *


@TestStep(Given)
def set_tiered_policy(self, allow_vfs=1, move_on_insert=0):
    """Enable vfs and set move_on_insert for the tiered policy."""
    policies = {
        "tiered": {"perform_ttl_move_on_insert": f"{move_on_insert}"},
    }
    disks = {
        n: {
            "allow_vfs": f"{allow_vfs}",
        }
        for n in ["external", "external_tiered"]
    }
    storage_config(disks=disks, policies=policies, restart=True)


@TestStep(When)
def insert_data_time(self, node, table_name, days_ago, rows):
    """Insert data with an offset timestamp."""
    t = time.mktime(
        (datetime.date.today() - datetime.timedelta(days=days_ago)).timetuple()
    )
    values = ",".join(f"({x},{t})" for x in range(rows))
    node.query(f"INSERT INTO {table_name} VALUES {values}")


@TestOutline(Scenario)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Table_TTLDelete("1.0"))
@Examples("move_on_insert", [[0], [1]])
def ttl_delete(self, move_on_insert):
    """Check that TTL delete works properly when <allow_vfs> parameter is set to 1."""
    nodes = self.context.ch_nodes
    table_name = "ttl_delete"

    with Given("I enable vfs and set ttl move on insert"):
        set_tiered_policy(move_on_insert=move_on_insert)

    with And("I have a replicated table"):
        replicated_table_cluster(
            table_name=table_name,
            storage_policy="tiered",
            columns="d UInt64, d1 DateTime",
            ttl="d1 + interval 2 day",
        )

    with When("I add data to the table"):
        with By("first inserting 200k rows"):
            insert_data_time(
                node=nodes[0], table_name=table_name, days_ago=7, rows=200000
            )

        with And("another insert of 400k rows"):
            insert_data_time(
                node=nodes[1], table_name=table_name, days_ago=3, rows=400000
            )

        with And("a large insert of 800k rows"):
            insert_data_time(
                node=nodes[2], table_name=table_name, days_ago=0, rows=800000
            )

    with Then("I check the row count"):
        retry(assert_row_count, timeout=5, delay=1)(
            node=nodes[0], table_name=table_name, rows=800000
        )


@TestOutline(Scenario)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Table_TTLMove("1.0"))
@Examples("move_on_insert", [[0], [1]])
def ttl_move(self, move_on_insert):
    """Check that TTL moves work properly when <allow_vfs> parameter is set to 1."""
    nodes = self.context.ch_nodes
    table_name = "ttl_move"

    with Given("I enable vfs and set ttl move on insert"):
        set_tiered_policy(move_on_insert=move_on_insert)

    with And("I have a replicated table"):
        replicated_table_cluster(
            table_name=table_name,
            storage_policy="tiered",
            columns="d UInt64, d1 DateTime",
            ttl="d1 + interval 2 day to volume 'external'",
        )

    with When("I add data to the table"):
        with By("first inserting 200k rows"):
            insert_data_time(
                node=nodes[0], table_name=table_name, days_ago=7, rows=200000
            )

        with And("another insert of 400k rows"):
            insert_data_time(
                node=nodes[1], table_name=table_name, days_ago=3, rows=400000
            )

        with And("a large insert of 800k rows"):
            insert_data_time(
                node=nodes[2], table_name=table_name, days_ago=0, rows=800000
            )

    with Then("I check the row count"):
        retry(assert_row_count, timeout=5, delay=1)(
            node=nodes[0], table_name=table_name, rows=1400000
        )


@TestFeature
@Name("ttl")
def feature(self):
    """Test TTL directives."""

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
