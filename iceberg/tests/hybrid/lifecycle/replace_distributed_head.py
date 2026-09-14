from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import create_table

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_Lifecycle_ReplaceDistributed,
)

from iceberg.tests.export_partition.steps.export_operations import (
    insert_into_iceberg_destination,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
    create_iceberg_destination,
)

from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    COLUMNS,
    COLUMNS_SQL,
    FORCE_REMOTE,
    LEFT_PREDICATE,
    PREFER_LOCALHOST,
    RIGHT_PREDICATE,
    assert_hybrid_matches_reference,
    fingerprint_sql,
    settings_clause,
    values_sql,
)
from iceberg.tests.hybrid.core.insert_routing import insert_sql
from iceberg.tests.hybrid.lifecycle.common import (
    cluster_tf,
    create_local_and_distributed,
)


@TestScenario
@Name("hybrid replaces distributed head")
def hybrid_replaces_distributed_head(self, minio_root_user, minio_root_password):
    """Replace a Distributed head with Hybrid; queries and INSERT path stay correct.

    Uses ``replicated_cluster`` (single shard) so Hybrid INSERT works: multi-shard
    ``cluster('all')`` requires a sharding key that Hybrid/cluster() don't take.
    Local MergeTree rows are seeded on every replica so force-remote still sees
    hot data (plain MergeTree is not cross-replica replicated).
    """
    node = self.context.node
    self.context.catalog = "no"

    with Given("local MergeTree + Distributed head over replicated_cluster"):
        tables = create_local_and_distributed(cluster="replicated_cluster")
        local = tables["local"]
        distributed = tables["distributed"]
        cluster = tables["cluster"]

    with And("Iceberg cold segment seeded with full dataset"):
        # Mirrored cold+hot rows so exclusive watermarks still cover every id
        # (same pattern as core mergetree_iceberg).
        ice = create_iceberg_destination(
            columns=COLUMNS_SQL,
            partition_by="",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(
            destination=ice,
            values=values_sql(ALL_ROWS),
        )
        ice_name = as_destination_name(ice)

    clause = settings_clause(PREFER_LOCALHOST)

    with When("capture Distributed baseline fingerprint"):
        dist_fp = node.query(fingerprint_sql(distributed) + f" {clause}").output.strip()

    head = f"head_{getuid()}"

    with And("drop Distributed and create Hybrid head with the same logical role"):
        node.query(f"DROP TABLE {distributed} SYNC")
        left_tf = cluster_tf(local, cluster=cluster)
        create_table(
            name=head,
            engine=(
                f"Hybrid({left_tf}, {LEFT_PREDICATE}, {ice_name}, {RIGHT_PREDICATE})"
            ),
            columns=COLUMNS,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    with Then("Hybrid fingerprint matches former Distributed baseline"):
        hybrid_fp = node.query(fingerprint_sql(head) + f" {clause}").output.strip()
        assert hybrid_fp == dist_fp, error(
            f"Hybrid={hybrid_fp!r} vs Distributed={dist_fp!r}"
        )

    with And("Hybrid matches exclusive UNION ALL reference (prefer localhost)"):
        assert_hybrid_matches_reference(
            hybrid_table=head,
            left_from=left_tf,
            right_from=ice_name,
            left_pred=LEFT_PREDICATE,
            right_pred=RIGHT_PREDICATE,
            settings_row=PREFER_LOCALHOST,
        )

    with And("same under force remote"):
        assert_hybrid_matches_reference(
            hybrid_table=head,
            left_from=left_tf,
            right_from=ice_name,
            left_pred=LEFT_PREDICATE,
            right_pred=RIGHT_PREDICATE,
            settings_row=FORCE_REMOTE,
        )

    with When("INSERT through Hybrid head"):
        new_row = (77, 770, "2025-08-01")
        node.query(insert_sql(head, new_row), exitcode=0)

    with Then("row lands on local MergeTree only"):
        local_count = node.query(
            f"SELECT count() FROM {local} WHERE id = 77"
        ).output.strip()
        ice_count = node.query(
            f"SELECT count() FROM {ice_name} WHERE id = 77 {clause}"
        ).output.strip()
        assert local_count == "1", error()
        assert ice_count == "0", error()

    with And("Hybrid SELECT sees the inserted row"):
        hybrid_count = node.query(
            f"SELECT count() FROM {head} WHERE id = 77 {clause}"
        ).output.strip()
        assert hybrid_count == "1", error()


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_Lifecycle_ReplaceDistributed("1.0"),
)
@Name("replace distributed head")
def feature(self, minio_root_user, minio_root_password):
    """Distributed → Hybrid head replacement recipe."""
    Scenario(test=hybrid_replaces_distributed_head)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
