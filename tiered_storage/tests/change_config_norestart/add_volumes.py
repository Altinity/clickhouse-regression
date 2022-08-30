#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from tiered_storage.requirements import *
from tiered_storage.tests.change_config_norestart.tests import add_volume


@TestScenario
@Name("add volumes")
@Requirements(RQ_SRS_004_Configuration_Changes_NoRestart_AddingNewVolumes("1.0"))
@Examples(
    "policy name disks inplace",
    [
        ("one_small_disk", "external", ["external"], True),
        ("one_small_disk", "external", ["external"], False),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that we can add and remove new volume from
    a policy defined in the storage config."""
    for example in self.examples:
        policy, volume, disks, inplace = example
        name = f'add new volume {volume} to {policy}{" using new file" if not inplace else " in place"}'

        Scenario(
            run=add_volume,
            name=name,
            args=args(
                cluster=cluster,
                node=node,
                policy=policy,
                name=volume,
                disks=disks,
                inplace=inplace,
                cleanup=True,
            ),
        )
