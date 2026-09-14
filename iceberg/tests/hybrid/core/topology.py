"""Topology / DoD smokes: remoteSecure, clusterAllReplicas, multi-segment, Dist-over-Dist."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import create_table

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_Topology_SecureCluster,
    RQ_ClickHouse_Hybrid_Topology_ClusterAllReplicas,
    RQ_ClickHouse_Hybrid_Topology_ThreeSegments,
    RQ_ClickHouse_Hybrid_DistributedOverDistributed,
)

from iceberg.tests.export_partition.steps.export_operations import (
    insert_into_iceberg_destination,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_s3_destination,
)

from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    COLUMNS,
    COLUMNS_SQL,
    LEFT_PREDICATE,
    PREFER_LOCALHOST,
    RIGHT_PREDICATE,
    WATERMARK,
    assert_hybrid_matches_reference,
    create_mergetree_segment,
    create_mt_mt_hybrid,
    fingerprint_sql,
    remote_tf,
    settings_clause,
    values_sql,
)
from iceberg.tests.hybrid.lifecycle.common import cluster_tf


def secure_cluster_tf(table_name, cluster="replicated_cluster_secure"):
    """TLS path via remote_servers secure cluster (tcp_port_secure).

    Prefer this over bare ``remoteSecure('localhost:9440', …)``: the iceberg
    suite openSSL client uses ``RejectCertificateHandler``, which rejects the
    self-signed server cert for ad-hoc remoteSecure.
    """
    return f"cluster('{cluster}', currentDatabase(), '{table_name}')"


def cluster_all_replicas_tf(table_name, cluster="replicated_cluster"):
    return f"clusterAllReplicas('{cluster}', currentDatabase(), '{table_name}')"


@TestScenario
@Name("secure cluster smoke")
def secure_cluster_smoke(self):
    """Hybrid first segment over replicated_cluster_secure (TLS to replicas)."""
    with Given("MT+MT Hybrid via secure cluster"):
        ctx = create_mt_mt_hybrid(
            left_tf_fn=secure_cluster_tf,
            right_tf_fn=secure_cluster_tf,
            cluster="replicated_cluster",
            seed_all_nodes=False,
        )

    with Then("fingerprint matches exclusive reference"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=ctx["left_from"],
            right_from=ctx["right_from"],
            left_pred=ctx["left_pred"],
            right_pred=ctx["right_pred"],
            settings_row=PREFER_LOCALHOST,
        )

    with And("SHOW CREATE mentions the secure cluster"):
        show = self.context.node.query(f"SHOW CREATE TABLE {ctx['hybrid']}").output
        assert "replicated_cluster_secure" in show, error()


@TestScenario
@Name("clusterAllReplicas smoke")
def cluster_all_replicas_smoke(self):
    """Hybrid with clusterAllReplicas() first segment (read-mostly path)."""
    node = self.context.node

    with Given("MergeTree on replicated_cluster"):
        left = create_mergetree_segment(cluster="replicated_cluster", rows=ALL_ROWS)
        right = create_mergetree_segment(cluster="replicated_cluster", rows=ALL_ROWS)

    left_tf = cluster_all_replicas_tf(left)
    right_tf = cluster_all_replicas_tf(right)
    hybrid = f"hybrid_{getuid()}"

    with And("create Hybrid over clusterAllReplicas segments"):
        create_table(
            name=hybrid,
            engine=f"Hybrid({left_tf}, {LEFT_PREDICATE}, {right_tf}, {RIGHT_PREDICATE})",
            columns=COLUMNS,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    with Then("fingerprint matches exclusive reference"):
        # Reference reads local tables (same rows); Hybrid fans out to all replicas.
        assert_hybrid_matches_reference(
            hybrid_table=hybrid,
            left_from=left,
            right_from=right,
            left_pred=LEFT_PREDICATE,
            right_pred=RIGHT_PREDICATE,
            settings_row=PREFER_LOCALHOST,
        )

    with And("SHOW CREATE mentions clusterAllReplicas"):
        show = node.query(f"SHOW CREATE TABLE {hybrid}").output
        assert "clusterAllReplicas" in show, error()


@TestScenario
@Name("three segment hybrid")
def three_segment_hybrid(self, minio_root_user, minio_root_password):
    """Three exclusive date bands: hot MT / warm MT / cold Iceberg."""
    node = self.context.node
    self.context.catalog = "no"

    # Bands: cold < 2025-01-15 <= warm < 2025-03-01 <= hot
    w1 = WATERMARK  # 2025-01-15
    w2 = "2025-03-01"
    hot_pred = f"date_col >= '{w2}'"
    warm_pred = f"date_col >= '{w1}' AND date_col < '{w2}'"
    cold_pred = f"date_col < '{w1}'"

    with Given("two MergeTree segments and Iceberg cold segment"):
        hot = create_mergetree_segment(rows=ALL_ROWS)
        warm = create_mergetree_segment(rows=ALL_ROWS)
        ice = create_iceberg_s3_destination(
            columns=COLUMNS_SQL,
            partition_by="",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(destination=ice, values=values_sql(ALL_ROWS))

    hybrid = f"hybrid_{getuid()}"
    left_tf = remote_tf(hot)
    mid_tf = remote_tf(warm)

    with And("create three-segment Hybrid"):
        create_table(
            name=hybrid,
            engine=(
                f"Hybrid({left_tf}, {hot_pred}, {mid_tf}, {warm_pred}, "
                f"{ice}, {cold_pred})"
            ),
            columns=COLUMNS,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    clause = settings_clause(PREFER_LOCALHOST)

    with Then("Hybrid count equals exclusive three-way UNION ALL"):
        hybrid_count = node.query(
            f"SELECT count() FROM {hybrid} {clause}"
        ).output.strip()
        ref_count = node.query(
            f"SELECT count() FROM ("
            f"SELECT id FROM {hot} WHERE {hot_pred} "
            f"UNION ALL SELECT id FROM {warm} WHERE {warm_pred} "
            f"UNION ALL SELECT id FROM {ice} WHERE {cold_pred}"
            f") {clause}"
        ).output.strip()
        assert hybrid_count == ref_count, error()
        assert hybrid_count == str(len(ALL_ROWS)), error()

    with And("fingerprint matches three-way reference"):
        hybrid_fp = node.query(fingerprint_sql(hybrid) + f" {clause}").output.strip()
        ref_fp = node.query(
            fingerprint_sql(
                f"(SELECT id, value, date_col FROM {hot} WHERE {hot_pred} "
                f"UNION ALL SELECT id, value, date_col FROM {warm} WHERE {warm_pred} "
                f"UNION ALL SELECT id, value, date_col FROM {ice} WHERE {cold_pred})"
            )
            + f" {clause}"
        ).output.strip()
        assert hybrid_fp == ref_fp, error()


@TestScenario
@Name("distributed over distributed")
def distributed_over_distributed(self, minio_root_user, minio_root_password):
    """Hybrid first segment remotes into a Distributed table (nested fan-out)."""
    node = self.context.node
    self.context.catalog = "no"

    local = f"local_{getuid()}"
    dist = f"dist_{getuid()}"

    with Given("local MergeTree + Distributed head on replicated_cluster"):
        create_table(
            name=local,
            engine="MergeTree",
            columns=COLUMNS,
            order_by="(date_col, id)",
            partition_by="toYYYYMM(date_col)",
            cluster="replicated_cluster",
        )
        node.query(
            f"INSERT INTO {local} (id, value, date_col) VALUES {values_sql(ALL_ROWS)}"
        )
        node.query(
            f"CREATE TABLE {dist} AS {local} "
            f"ENGINE = Distributed('replicated_cluster', currentDatabase(), {local}, id)"
        )

    with And("Iceberg cold segment with mirrored rows"):
        ice = create_iceberg_s3_destination(
            columns=COLUMNS_SQL,
            partition_by="",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(destination=ice, values=values_sql(ALL_ROWS))

    hybrid = f"hybrid_{getuid()}"
    # remote() → Distributed → local shards/replicas
    left_tf = remote_tf(dist)

    with And("create Hybrid over Distributed + Iceberg"):
        create_table(
            name=hybrid,
            engine=f"Hybrid({left_tf}, {LEFT_PREDICATE}, {ice}, {RIGHT_PREDICATE})",
            columns=COLUMNS,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    with Then("fingerprint matches exclusive reference via Distributed left"):
        assert_hybrid_matches_reference(
            hybrid_table=hybrid,
            left_from=dist,
            right_from=ice,
            left_pred=LEFT_PREDICATE,
            right_pred=RIGHT_PREDICATE,
            settings_row=PREFER_LOCALHOST,
        )

    with And("matches cluster() over local as an alternate reference"):
        assert_hybrid_matches_reference(
            hybrid_table=hybrid,
            left_from=cluster_tf(local),
            right_from=ice,
            left_pred=LEFT_PREDICATE,
            right_pred=RIGHT_PREDICATE,
            settings_row=PREFER_LOCALHOST,
        )


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_Topology_SecureCluster("1.0"),
    RQ_ClickHouse_Hybrid_Topology_ClusterAllReplicas("1.0"),
    RQ_ClickHouse_Hybrid_Topology_ThreeSegments("1.0"),
    RQ_ClickHouse_Hybrid_DistributedOverDistributed("1.0"),
)
@Name("topology")
def feature(self, minio_root_user, minio_root_password):
    """Secure cluster / clusterAllReplicas / three-segment / Distributed-over-Distributed."""
    for scenario in (secure_cluster_smoke, cluster_all_replicas_smoke):
        Scenario(run=scenario)

    for scenario in (three_segment_hybrid, distributed_over_distributed):
        Scenario(test=scenario)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
