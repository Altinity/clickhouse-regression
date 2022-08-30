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
@Name("alter move")
@Requirements(
    RQ_SRS_004_MovingDataBetweenStorageDevices_Manual("1.0"),
    RQ_SRS_004_SQLStatement_MoveTablePartitions("1.0"),
    RQ_SRS_004_MovingDataBetweenStorageDevices_Manual_NoDowntime("1.0"),
)
def feature(self, cluster):
    """Check manually moving parts and partitions with downtime using
    ALTER MOVE PART and ALTER MOVE PARTITION commands.
    """
    args = {"cluster": cluster}
    Scenario(
        run=load("tiered_storage.tests.alter_move.alter_move", "scenario"),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.alter_move.alter_move_half_of_partition", "scenario"
        ),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.alter_move.alter_double_move_partition", "scenario"
        ),
        args=args,
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.alter_move.opposing_moves", "scenario"),
        args=args,
        flags=TE,
    )

    with Scenario("concurrent", flags=TE):
        Scenario(
            run=load(
                "tiered_storage.tests.alter_move.concurrent_alter_modify", "scenario"
            ),
            args=args,
            flags=TE,
        )
        Scenario(
            run=load(
                "tiered_storage.tests.alter_move.concurrent_alter_move", "scenario"
            ),
            args=args,
            flags=TE,
        )
        Scenario(
            run=load(
                "tiered_storage.tests.alter_move.concurrent_alter_move_and_drop",
                "scenario",
            ),
            args=args,
            flags=TE,
        )
        Scenario(
            run=load(
                "tiered_storage.tests.alter_move.concurrent_alter_move_and_select",
                "scenario",
            ),
            args=args,
            flags=TE,
        )
        Scenario(
            run=load(
                "tiered_storage.tests.alter_move.concurrent_alter_move_insert_and_select",
                "scenario",
            ),
            args=args,
            flags=TE,
        )
