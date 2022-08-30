#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from tiered_storage.requirements import *
from tiered_storage.tests.change_config_norestart.tests import add_disk


@TestScenario
@Name("add disks")
@Requirements(RQ_SRS_004_Configuration_Changes_NoRestart_AddingNewDisks("1.0"))
@Examples(
    "name path inplace",
    [
        ("jbod4", "/jbod4/", True),
        ("jbod4", "/jbod4/", False),
        ("external2", "/external2/", True),
        ("external2", "/external2/", False),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that we can add and remove new disks from storage config."""
    for example in self.examples:
        disk, path, inplace = example
        name = f'add new disk {disk}{" using new file" if not inplace else " in place"}'

        Scenario(
            run=add_disk,
            name=name,
            args=args(
                cluster=cluster,
                node=node,
                name=disk,
                path=path,
                inplace=inplace,
                cleanup=True,
            ),
        )
