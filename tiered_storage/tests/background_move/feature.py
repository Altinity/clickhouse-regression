#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from tiered_storage.requirements import *


@TestFeature
@Name("background move")
@Requirements(
    RQ_SRS_004_StoragePolicy_Rules_MoveData_FreeSpace("1.0"),
    RQ_SRS_004_StoragePolicy_Enforcement_INSERT("1.0"),
    RQ_SRS_004_MovingDataBetweenStorageDevices_Automatic("1.0"),
    RQ_SRS_004_AutomaticPartMovementInTheBackground("1.0"),
    RQ_SRS_004_Configuration_StorageConfiguration_MoveFactor("1.0"),
    RQ_SRS_004_Configuration_StorageConfiguration_MoveFactor_Range("1.0"),
    RQ_SRS_004_StoragePolicy_RuleMatchOrder("1.0"),
    RQ_SRS_004_StoragePolicy_Enforcement_Background("1.0"),
)
def feature(self, cluster):
    """Check that when data in the volume reaches the limit
    specified by the **move_factor** option
    then in the background the parts are moved to the next volume.
    """
    args = {"cluster": cluster}
    Scenario(
        run=load("tiered_storage.tests.background_move.custom_move_factor", "scenario"),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.background_move.default_move_factor", "scenario"
        ),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.background_move.max_move_factor", "scenario"),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.background_move.min_move_factor", "scenario"),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.background_move.adding_another_volume", "scenario"
        ),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.background_move.adding_another_volume_one_large_part",
            "scenario",
        ),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.background_move.concurrent_read", "scenario"),
        args=args,
        flags=TE,
    )
