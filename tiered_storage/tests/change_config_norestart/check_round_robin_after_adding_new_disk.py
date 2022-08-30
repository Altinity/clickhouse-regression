#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from tiered_storage.requirements import *
from tiered_storage.tests.change_config_norestart.tests import *


@TestScenario
@Name("check round robin after adding new disk")
@Examples(
    "policy volume disks current_disks prepopulate",
    [
        ("default", "default", ["jbod4"], ["default"], True),
        ("default", "default", ["jbod4"], ["default"], False),
        # ("default", "default", ["jbod4", "external2"], ["default"], True),
        # ("default", "default", ["jbod4", "external2"], ["default"], False),
        ("one_small_disk", "main", ["jbod4"], ["jbod1"], True),
        ("one_small_disk", "main", ["jbod4"], ["jbod1"], False),
        ("one_small_disk", "main", ["jbod4", "external2"], ["jbod1"], True),
        ("one_small_disk", "main", ["jbod4", "external2"], ["jbod1"], False),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    for i, example in enumerate(self.examples):
        policy, volume, disks, current_disks, prepopulate = example
        name = f"{policy}_{volume}_new_{'_'.join(disks)}{'_prepopulate' if prepopulate else ''}"
        table = name

        Scenario(
            run=outline,
            name=name,
            args=args(
                cluster=cluster,
                node=node,
                table=table,
                policy=policy,
                volume=volume,
                disks=disks,
                current_disks=current_disks,
                prepopulate=prepopulate,
            ),
            flags=TE,
        )


@TestScenario
def outline(
    self,
    cluster,
    table,
    policy,
    volume,
    disks,
    current_disks,
    prepopulate,
    node="clickhouse1",
):
    """Check that after creating a table with a storage policy and then adding a new disk
    and making this disk available in the current volume of the policy
    we see that new inserts are divided between both disks using round robin.
    """
    node = cluster.node(node)

    with Given("I have a table"):
        By(
            run=creating_table,
            args=args(
                node=node, engine="MergeTree", name=table, policy=policy, cleanup=False
            ),
        )

        with And("I stop merges on the table to avoid conflicts"):
            node.query(f"SYSTEM STOP MERGES {table}")
    try:
        if prepopulate:
            with And("I pre-populate the table"):
                By(run=inserting_into_table, args=args(node=node, name=table, count=5))

            with Then("I check only current disk should be used"):
                By(
                    run=check_used_disks_for_table,
                    args=args(node=node, name=table, disks=current_disks),
                )

        if policy == "default":
            volumes = [{"name": "default", "disks": ["default"]}]
            with When("I add default policy definition to the configuration"):
                By(
                    run=add_policy,
                    args=args(
                        cluster=cluster, node=node.name, name=policy, volumes=volumes
                    ),
                )

        with When("I add new disk"):
            for disk in disks:
                By(
                    run=add_disk,
                    args=args(
                        cluster=cluster, node=node.name, name=disk, path=f"/{disk}/"
                    ),
                )

        with When("I add this disk to the volume"):
            for disk in disks:
                By(
                    run=add_disks_to_volume,
                    args=args(
                        cluster=cluster,
                        node=node.name,
                        policy=policy,
                        volume=volume,
                        disks=[disk],
                    ),
                )

        with And("I make a few inserts into the table"):
            for i in range(5):
                By(
                    run=inserting_into_table,
                    name=f"insert #{i}",
                    args=args(node=node, name=table, count=5),
                )

        with Then("I check row count matches"):
            count = 25
            if prepopulate:
                count += 5
            By(run=selecting_from_table, args=args(node=node, name=table, count=count))

        with And("old and new disk should now be used"):
            By(
                run=check_used_disks_for_table,
                args=args(node=node, name=table, disks=(disks + current_disks)),
            )
    finally:
        with Finally("I drop the table"):
            By(run=dropping_table, args=args(node=node, name=table))
