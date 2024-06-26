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
@Name("ttl moves")
@Requirements(
    RQ_SRS_004_TTLExpressions_RuleNotSatisfied("1.0"),
    RQ_SRS_004_TTLExpressionsForDataRelocation("1.0"),
)
def feature(self, cluster):
    """Check moving parts using TTL expressions."""

    Scenario(
        run=load("tiered_storage.tests.ttl_moves.syntax", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.multi_column_ttl", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.delete", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.alter_delete", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.alter_column_in_ttl", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.ttl_moves.mutation_update_column_in_ttl", "scenario"
        ),
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.ttl_moves.mutation_delete_column_in_ttl", "scenario"
        ),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.defaults_to_delete", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.inserts_to_disk", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.moves_to_disk", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.moves_to_eventually", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.inserts_to_volume", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.moves_to_volume", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.merges", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.merges_with_full_disk", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.moves_after_merges", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.inserts_multiple_ttls", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.most_recent", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.alter_multiple_ttls", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.ttl_moves.alter_with_existing_parts", "scenario"
        ),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.alter_with_merge", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.alter_drop_all_ttls", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.ttl_moves.alter_policy_and_ttl_with_existing_parts",
            "scenario",
        ),
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.ttl_moves.moves_to_disk_concurrent_read", "scenario"
        ),
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.ttl_moves.moves_to_volume_concurrent_read", "scenario"
        ),
        flags=TE,
    )
    Scenario(
        run=load(
            "tiered_storage.tests.ttl_moves.download_appropriate_disk", "scenario"
        ),
        flags=TE,
    )
    Scenario(
        run=load("tiered_storage.tests.ttl_moves.materialize_ttl", "scenario"),
        flags=TE,
    )
