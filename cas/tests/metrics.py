from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from cas.requirements.requirements import (
    RQ_SRS_048_CAS_MergeTree_Replicated,
    RQ_SRS_048_CAS_Observability,
    RQ_SRS_048_CAS_Observability_ProfileEvents,
    RQ_SRS_048_CAS_Relink,
    RQ_SRS_048_CAS_Relink_HappyPath,
)
from cas.tests.steps import (
    CAS_CURRENT_METRICS,
    CAS_PROFILE_EVENTS,
    alter_update,
    assert_replicas_agree,
    cas_event,
    cas_event_grew,
    cas_event_unchanged,
    cas_metrics,
    collect_garbage,
    create_cas_merge_tree_table,
    create_replicated_cas_table,
    insert_cas_partitions,
    start_fetches,
    stop_fetches,
    stop_garbage_collection,
    sync_replica,
)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_Observability("1.0"),
    RQ_SRS_048_CAS_Observability_ProfileEvents("1.0"),
)
def cas_metric_registry_matches_binary(self):
    """Fail if this binary added or removed a CAS* event or gauge.

    Update ``CAS_PROFILE_EVENTS`` / ``CAS_CURRENT_METRICS`` when that happens.
    """
    node = self.context.node
    events, gauges = cas_metrics(node)
    note(
        f"binary: {len(events)} events, {len(gauges)} gauges; "
        f"list: {len(CAS_PROFILE_EVENTS)} events, {len(CAS_CURRENT_METRICS)} gauges"
    )

    with Then("system.events CAS* names match CAS_PROFILE_EVENTS"):
        extra = sorted(set(events) - set(CAS_PROFILE_EVENTS))
        missing = sorted(set(CAS_PROFILE_EVENTS) - set(events))
        assert not extra and not missing, error(
            f"new in binary: {extra}; gone from binary: {missing}"
        )

    with And("system.metrics CAS* names match CAS_CURRENT_METRICS"):
        extra = sorted(set(gauges) - set(CAS_CURRENT_METRICS))
        missing = sorted(set(CAS_CURRENT_METRICS) - set(gauges))
        assert not extra and not missing, error(
            f"new in binary: {extra}; gone from binary: {missing}"
        )


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_Observability("1.0"),
    RQ_SRS_048_CAS_Observability_ProfileEvents("1.0"),
)
def check_cas_metrics(self):
    """Check that CAS write-path counters move after insert and update, and that GC counters move after drop."""
    node = self.context.node
    table = f"cas_metrics_write_{getuid()}"
    pool_prefix = f"data/{table}"
    disk = f"cas_{table}"

    with Given("create a MergeTree on an isolated CAS pool"):
        create_cas_merge_tree_table(
            table_name=table,
            columns="p UInt8, i UInt64, v UInt64 DEFAULT 0",
            pool_prefix=pool_prefix,
            disk_name=disk,
        )

    with And("stop background garbage collection"):
        stop_garbage_collection(disk=disk, nodes=[node])

    with And("read write-path counters before the insert"):
        before_put = cas_event(node, "CASBlobPut")
        before_fanout_batches = cas_event(node, "CASBlobUploadFanoutBatches")
        before_fanout_tasks = cas_event(node, "CASBlobUploadFanoutTasks")
        before_manifest = cas_event(node, "CASManifestPut")
        before_meta_put = cas_event(node, "CASMetaPut")
        before_meta_clean = cas_event(node, "CASMetaCreateClean")
        before_ref_mutations = cas_event(node, "CASRefBatchedMutations")
        before_ref_flushes = cas_event(node, "CASRefBatchFlushes")
        before_cw_attempts = cas_event(node, "CASConditionalWriteAttempts")
        before_cw_committed = cas_event(node, "CASConditionalWriteCommitted")

    with When("insert one small part"):
        insert_cas_partitions(table_name=table, partitions=(1,), rows_per_partition=10)

    with Then("check that the rows can be read back"):
        result = node.query(f"SELECT count(), sum(i) FROM {table}")
        assert result.output.strip() == "10\t45", error(result.output)

    with And("CASBlobPut increased"):
        after_put = cas_event_grew(node, "CASBlobPut", before_put)
    with And("CASBlobUploadFanoutBatches increased"):
        cas_event_grew(node, "CASBlobUploadFanoutBatches", before_fanout_batches)
    with And("CASBlobUploadFanoutTasks increased"):
        cas_event_grew(node, "CASBlobUploadFanoutTasks", before_fanout_tasks)
    with And("CASManifestPut increased"):
        after_manifest = cas_event_grew(node, "CASManifestPut", before_manifest)
    with And("CASMetaPut increased"):
        cas_event_grew(node, "CASMetaPut", before_meta_put)
    with And("CASMetaCreateClean increased"):
        cas_event_grew(node, "CASMetaCreateClean", before_meta_clean)
    with And("CASRefBatchedMutations increased"):
        after_ref_mutations = cas_event_grew(
            node, "CASRefBatchedMutations", before_ref_mutations
        )
    with And("CASRefBatchFlushes increased"):
        cas_event_grew(node, "CASRefBatchFlushes", before_ref_flushes)
    with And("CASConditionalWriteAttempts increased"):
        cas_event_grew(node, "CASConditionalWriteAttempts", before_cw_attempts)
    with And("CASConditionalWriteCommitted increased"):
        cas_event_grew(node, "CASConditionalWriteCommitted", before_cw_committed)

    with When("update the part"):
        alter_update(table_name=table, assignments="v = v + 10", condition="1")

    with Then("check that the updated rows can be read back"):
        result = node.query(f"SELECT count(), sum(i), sum(v) FROM {table}")
        assert result.output.strip() == "10\t45\t100", error(result.output)

    with And("CASBlobPut increased after the update"):
        cas_event_grew(node, "CASBlobPut", after_put)
    with And("CASManifestPut increased after the update"):
        cas_event_grew(node, "CASManifestPut", after_manifest)
    with And("CASRefBatchedMutations increased after the update"):
        cas_event_grew(node, "CASRefBatchedMutations", after_ref_mutations)

    with And("read GC counters before drop"):
        before_condemned = cas_event(node, "CASGCRetiredCondemned")
        before_graduated = cas_event(node, "CASGCRetiredGraduated")
        before_redeleted = cas_event(node, "CASGCRetiredRedeleted")
        before_walks = cas_event(node, "CASGCRefWalkPlansBuilt")

    with When("drop the table and run GC until deletes can land"):
        node.query(f"DROP TABLE IF EXISTS {table} SYNC")
        collect_garbage(disk=disk, nodes=[node], rounds=3)

    with Then("CASGCRefWalkPlansBuilt increased"):
        cas_event_grew(node, "CASGCRefWalkPlansBuilt", before_walks)
    with And("CASGCRetiredCondemned increased"):
        cas_event_grew(node, "CASGCRetiredCondemned", before_condemned)
    with And("CASGCRetiredGraduated increased"):
        cas_event_grew(node, "CASGCRetiredGraduated", before_graduated)
    with And("CASGCRetiredRedeleted increased"):
        cas_event_grew(node, "CASGCRetiredRedeleted", before_redeleted)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_Observability("1.0"),
    RQ_SRS_048_CAS_Observability_ProfileEvents("1.0"),
    RQ_SRS_048_CAS_MergeTree_Replicated("1.0"),
    RQ_SRS_048_CAS_Relink("1.0"),
    RQ_SRS_048_CAS_Relink_HappyPath("1.0"),
)
def check_cas_replication_metrics(self):
    """Check that a ReplicatedMergeTree follower fetch moves relink counters and does not re-upload blobs."""
    leader, follower = self.context.nodes[0], self.context.nodes[1]
    replicas = [leader, follower]
    table = f"cas_metrics_rmt_{getuid()}"
    pool_prefix = f"data/{table}"

    with Given("a ReplicatedMergeTree on a shared CAS pool"):
        create_replicated_cas_table(
            table_name=table,
            pool_prefix=pool_prefix,
            nodes=replicas,
        )

    try:
        with And("pause fetches on the follower"):
            stop_fetches(table_name=table, node=follower)

        with And("read leader write-path and follower relink counters"):
            before_leader_put = cas_event(leader, "CASBlobPut")
            before_adopt = cas_event(follower, "CASBlobAdoptTrusted")
            before_follower_put = cas_event(follower, "CASBlobPut")
            before_ref_mutations = cas_event(follower, "CASRefBatchedMutations")
            before_ref_flushes = cas_event(follower, "CASRefBatchFlushes")
            before_manifest = cas_event(follower, "CASManifestPut")
            before_manifest_dedup = cas_event(follower, "CASManifestPutDeduplicated")
            before_cw_attempts = cas_event(follower, "CASConditionalWriteAttempts")
            before_cw_committed = cas_event(follower, "CASConditionalWriteCommitted")
            before_confirm_mutation = cas_event(
                follower, "CASRelinkConfirmRefusedRefMutationInFlight"
            )
            before_confirm_wedged = cas_event(
                follower, "CASRelinkConfirmRefusedLaneWedged"
            )
            before_confirm_broken = cas_event(
                follower, "CASRelinkConfirmRefusedLaneBroken"
            )
            before_confirm_lock = cas_event(
                follower, "CASRelinkConfirmRefusedStateLockBusy"
            )
            before_confirm_mount = cas_event(
                follower, "CASRelinkConfirmRefusedMountCannotSpeak"
            )

        with When("insert one small part on the leader"):
            insert_cas_partitions(
                table_name=table,
                partitions=(1,),
                rows_per_partition=10,
                node=leader,
            )

        with Then("check that the leader can read the rows"):
            result = leader.query(f"SELECT count(), sum(i) FROM {table}")
            assert result.output.strip() == "10\t45", error(result.output)

        with And("CASBlobPut increased on the leader"):
            cas_event_grew(leader, "CASBlobPut", before_leader_put)

        with When("resume fetches and let the follower catch up"):
            start_fetches(table_name=table, node=follower)
            sync_replica(table_name=table, node=follower)

        with Then("check that both replicas can read the rows"):
            result = follower.query(f"SELECT count(), sum(i) FROM {table}")
            assert result.output.strip() == "10\t45", error(result.output)
            assert_replicas_agree(table_name=table, nodes=replicas)

        with And("CASBlobAdoptTrusted increased on the follower"):
            cas_event_grew(follower, "CASBlobAdoptTrusted", before_adopt)
        with And("CASRefBatchedMutations increased on the follower"):
            cas_event_grew(follower, "CASRefBatchedMutations", before_ref_mutations)
        with And("CASRefBatchFlushes increased on the follower"):
            cas_event_grew(follower, "CASRefBatchFlushes", before_ref_flushes)
        with And("the follower published a manifest"):
            after_manifest = cas_event(follower, "CASManifestPut")
            after_manifest_dedup = cas_event(follower, "CASManifestPutDeduplicated")
            assert (
                after_manifest > before_manifest
                or after_manifest_dedup > before_manifest_dedup
            ), error(
                f"CASManifestPut before={before_manifest} after={after_manifest}; "
                f"CASManifestPutDeduplicated before={before_manifest_dedup} "
                f"after={after_manifest_dedup}"
            )
        with And("CASConditionalWriteAttempts increased on the follower"):
            cas_event_grew(follower, "CASConditionalWriteAttempts", before_cw_attempts)
        with And("CASConditionalWriteCommitted increased on the follower"):
            cas_event_grew(follower, "CASConditionalWriteCommitted", before_cw_committed)
        with And("CASBlobPut did not increase on the follower"):
            cas_event_unchanged(follower, "CASBlobPut", before_follower_put)
        with And("CASRelinkConfirmRefusedRefMutationInFlight did not increase"):
            cas_event_unchanged(
                follower,
                "CASRelinkConfirmRefusedRefMutationInFlight",
                before_confirm_mutation,
            )
        with And("CASRelinkConfirmRefusedLaneWedged did not increase"):
            cas_event_unchanged(
                follower, "CASRelinkConfirmRefusedLaneWedged", before_confirm_wedged
            )
        with And("CASRelinkConfirmRefusedLaneBroken did not increase"):
            cas_event_unchanged(
                follower, "CASRelinkConfirmRefusedLaneBroken", before_confirm_broken
            )
        with And("CASRelinkConfirmRefusedStateLockBusy did not increase"):
            cas_event_unchanged(
                follower, "CASRelinkConfirmRefusedStateLockBusy", before_confirm_lock
            )
        with And("CASRelinkConfirmRefusedMountCannotSpeak did not increase"):
            cas_event_unchanged(
                follower,
                "CASRelinkConfirmRefusedMountCannotSpeak",
                before_confirm_mount,
            )
    finally:
        with Finally("ensure follower fetches are resumed"):
            follower.query(f"SYSTEM START FETCHES {table}", no_checks=True)


@TestFeature
@Name("metrics")
@Requirements(RQ_SRS_048_CAS_Observability("1.0"))
def feature(self):
    """CAS ProfileEvents and CurrentMetrics."""
    Scenario(run=cas_metric_registry_matches_binary)
    Scenario(run=check_cas_metrics)
    Scenario(run=check_cas_replication_metrics)
