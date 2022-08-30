#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from tiered_storage.requirements import *
from tiered_storage.tests.change_config_norestart.tests import add_disks_to_volume


@TestScenario
@Name("add disks to volumes")
@Requirements(RQ_SRS_004_Configuration_Changes_NoRestart_AddingNewDisks("1.0"))
@Examples(
    "policy volume disks inplace",
    [
        ("one_small_disk", "main", ["external"], True),
        # ("one_small_disk", "main", ["external"], False),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that we can add and remove disks to and from volumes
    for a policy defined in the storage config."""
    for example in self.examples:
        policy, volume, disks, inplace = example
        name = f'add new disks {",".join(disks)} to volume {volume} in policy {policy}'

        Scenario(
            run=add_disks_to_volume,
            name=name,
            args=args(
                cluster=cluster,
                node=node,
                policy=policy,
                volume=volume,
                disks=disks,
                inplace=inplace,
                cleanup=True,
            ),
        )
