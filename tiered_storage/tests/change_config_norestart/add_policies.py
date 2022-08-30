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
@Name("add policies")
@Requirements(RQ_SRS_004_Configuration_Changes_NoRestart_NewPolicies("1.0"))
@Examples(
    "name volumes inplace",
    [
        (
            "custom_policy_inplace",
            [{"name": "main", "disks": ["jbod1", "jbod2"]}],
            True,
        ),
        (
            "custom_policy_new_file",
            [{"name": "main", "disks": ["jbod1", "jbod2"]}],
            False,
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that we can add and remove new policy from
    in the storage config."""
    for example in self.examples:
        policy, volumes, inplace = example
        name = f'add new policy {policy}{" using new file" if not inplace else " in place"}'

        Scenario(
            run=add_policy,
            name=name,
            args=args(
                cluster=cluster,
                node=node,
                name=policy,
                volumes=volumes,
                inplace=inplace,
                cleanup=True,
            ),
        )
