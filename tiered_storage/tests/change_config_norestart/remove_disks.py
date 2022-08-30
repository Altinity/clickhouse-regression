#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from tiered_storage.requirements import *
from tiered_storage.tests.change_config_norestart.steps import *


@TestScenario
@Name("remove disks")
@Examples("name", [("jbod4",), ("external2",)])
def scenario(self, cluster, node="clickhouse1"):
    """Check that we can add new disk to storage config."""
    for example in self.examples:
        name = "add new disk {name}".format(**example._asdict())
        Scenario(
            run=remove_disk,
            name=name,
            flags=TE,
            args=args(cluster=cluster, node=node, name=example.name),
        )


@TestScenario
def remove_disk(self, cluster, node="clickhouse1", name="jbod4"):
    with Given("cluster node"):
        node = cluster.node(node)

    with When("I remove disk from the config"):
        By(run=removing_disk, args={"node": node, "name": name})

    with And("I reload config"):
        By(run=reloading_config, args={"node": node})

    with Then("I check disk is not available"):
        By(
            run=checking_disk_is_not_present_in_system_disks_by_name,
            args={"node": node, "name": name},
        )
