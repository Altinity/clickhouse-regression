#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from tiered_storage.requirements import *


@TestFeature
@Name("change config norestart")
@Requirements(RQ_SRS_004_Configuration_Changes_Restart("1.0"))
def feature(self, cluster):
    """Check that in some cases storage configuration changes do not require
    a full server restart but are applied as soon as change to the configuration
    has been detected.
    """
    args = {"cluster": cluster}

    Scenario(
        run=load("tiered_storage.tests.change_config_norestart.add_disks", "scenario"),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.change_config_norestart.add_volumes", "scenario"
        ),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.change_config_norestart.add_policies", "scenario"
        ),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.change_config_norestart.add_disks_to_volumes",
            "scenario",
        ),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.change_config_norestart.check_round_robin_after_adding_new_disk",
            "scenario",
        ),
        args=args,
        flags=TE,
    )
