#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from tiered_storage.tests.change_config_norestart.steps import *


@TestScenario
def add_disk(
    self, cluster, name, path=None, node="clickhouse1", inplace=True, cleanup=True
):
    node = cluster.node(node)

    if path is None:
        path = f"/{name}/"

    with Given("I add new disk to the config"):
        By(run=adding_disk, args=args(node=node, name=name, path=path, inplace=inplace))

    try:
        with And("I reload config"):
            By(run=reloading_config, args=args(node=node))

        with Then("I check disk is available"):
            By(
                run=checking_disk_is_present_in_system_disks_by_name,
                args=args(node=node, name=name),
            )
    finally:
        if cleanup:

            def callback():
                By(
                    run=remove_disk,
                    args=args(
                        cluster=cluster, node=node.name, name=name, inplace=inplace
                    ),
                )

            self.context.cleanup(callback)


@TestScenario
def add_volume(
    self, cluster, policy, name, disks, node="clickhouse1", inplace=True, cleanup=True
):
    """Check that we can add new volume to storage config."""
    node = cluster.node(node)

    with Given("I add volume to the config"):
        By(
            run=adding_volume_to_policy,
            args=args(
                node=node, policy=policy, name=name, disks=disks, inplace=inplace
            ),
        )

    try:
        with And("I reload config"):
            By(run=reloading_config, args=args(node=node))

        with Then("I check volume is available"):
            By(
                run=checking_volume_is_present_in_system_policies_by_name,
                args=args(node=node, policy=policy, name=name),
            )
    finally:
        if cleanup:

            def callback():
                By(
                    run=remove_volume,
                    args=args(
                        cluster=cluster,
                        node=node.name,
                        policy=policy,
                        name=name,
                        inplace=inplace,
                    ),
                )

            self.context.cleanup(callback)


@TestScenario
def add_policy(
    self, cluster, name, volumes, node="clickhouse1", inplace=True, cleanup=True
):
    """Check that we can add new policy to storage config."""
    node = cluster.node(node)

    with Given("I add new policy to the config"):
        By(
            run=adding_policy,
            args=args(node=node, name=name, volumes=volumes, inplace=inplace),
        )

    try:
        with And("reload the config"):
            By(run=reloading_config, args=args(node=node))

        with Then("I check that the new policy is present"):
            By(
                run=checking_policy_is_present_in_system_policies_by_name,
                args=args(node=node, name=name),
            )
    finally:
        if cleanup:

            def callback():
                By(
                    run=remove_policy,
                    args=args(
                        cluster=cluster, node=node.name, name=name, inplace=inplace
                    ),
                )

            self.context.cleanup(callback)


@TestScenario
def add_disks_to_volume(
    self, cluster, policy, volume, disks, node="clickhouse1", inplace=True, cleanup=True
):
    """Check that we can add new disks to volume in the storage config."""
    node = cluster.node(node)

    with Given("I add disks to volume in the config"):
        By(
            run=adding_disks_to_volume,
            args=args(
                node=node, policy=policy, volume=volume, disks=disks, inplace=inplace
            ),
        )

    try:
        with And("I reload config"):
            By(run=reloading_config, args=args(node=node))

        with Then("I check disks in volume is present"):
            By(
                run=checking_disks_in_volume_is_present_in_system_policies_by_name,
                args=args(node=node, policy=policy, volume=volume, disks=disks),
            )
    finally:
        if cleanup:

            def callback():
                By(
                    run=remove_disks_from_volume,
                    args=args(
                        cluster=cluster,
                        node=node.name,
                        policy=policy,
                        volume=volume,
                        disks=disks,
                        inplace=inplace,
                    ),
                )

            self.context.cleanup(callback)


@TestScenario
def remove_disk(self, cluster, name, node="clickhouse1", inplace=True):
    node = cluster.node(node)

    with When("I remove disk from the configuration"):
        By(run=removing_disk, args=args(node=node, name=name, inplace=inplace))

    with And("I reload config by restarting server"):
        By(run=reloading_config, args=args(node=node, restart=True))

    with Then("I check disk is not present"):
        By(
            run=checking_disk_is_not_present_in_system_disks_by_name,
            args=args(node=node, name=name),
        )


@TestScenario
def remove_volume(self, cluster, policy, name, node="clickhouse1", inplace=True):
    node = cluster.node(node)

    with When("I remove volume from the configuration"):
        By(
            run=removing_volume,
            args=args(node=node, policy=policy, name=name, inplace=inplace),
        )

    with And("I reload config by restarting server"):
        By(run=reloading_config, args=args(node=node, restart=True))

    with Then("I check volume is not present"):
        By(
            run=checking_volume_is_not_present_in_system_policies_by_name,
            args=args(node=node, policy=policy, name=name),
        )


@TestScenario
def remove_policy(self, cluster, name, node="clickhouse1", inplace=True):
    node = cluster.node(node)

    with When("I remove policy from the configuration"):
        By(run=removing_policy, args=args(node=node, name=name, inplace=inplace))

    with And("I reload config by restarting server"):
        By(run=reloading_config, args=args(node=node, restart=True))

    if name != "default":
        with Then("I check policy is not present"):
            By(
                run=checking_policy_is_not_present_in_system_policies_by_name,
                args=args(node=node, name=name),
            )


@TestScenario
def remove_disks_from_volume(
    self, cluster, policy, volume, disks, node="clickhouse1", inplace=True
):
    node = cluster.node(node)

    with When("I remove disks from a volume in a policy"):
        By(
            run=removing_disks_from_volume,
            args=args(
                node=node, policy=policy, volume=volume, disks=disks, inplace=inplace
            ),
        )

    with And("I reload config by restarting server"):
        By(run=reloading_config, args=args(node=node, restart=True))

    with Then("I check disks in volume is not present"):
        By(
            run=checking_disks_in_volume_is_not_present_in_system_policies_by_name,
            args=args(node=node, policy=policy, volume=volume, disks=disks),
        )
