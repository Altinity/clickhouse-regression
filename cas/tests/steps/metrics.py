"""CAS ProfileEvents and CurrentMetrics helpers."""

import re

from testflows.core import *
from testflows.asserts import error

BLOB_PUT = "CASBlobPut"


CAS_PROFILE_EVENTS = (
    "CASBlobPut",
    "CASBlobPutDeduplicated",
    "CASBlobOverwrite",
    "CASBlobCompareSwap",
    "CASBlobCompareSwapConflict",
    "CASBlobHead",
    "CASBlobHeadMiss",
    "CASBlobBodyPutAvoided",
    "CASBlobUploadFanoutBatches",
    "CASBlobUploadFanoutTasks",
    "CASRefBatchFlushes",
    "CASRefBatchedMutations",
    "CASRefBatchScopeCuts",
    "CASRefQueueWaitMicroseconds",
    "CASHotKeyQueueWaitMicroseconds",
    "CASHotKeyCacheStarts",
    "CASHotKeyReadStarts",
    "CASHotKeyCacheVerdictsReread",
    "CASRefRecoveryRestarts",
    "CASRefRecoveryRetries",
    "CASRefAppendWedged",
    "CASRefAppendPreAttemptRefused",
    "CASRefAppendUnwedged",
    "CASRefAppendDefiniteFailure",
    "CASRefAppendSealRejected",
    "CASRefAppendOccupantUnreadable",
    "CASRelinkConfirmRefusedRefMutationInFlight",
    "CASRelinkConfirmRefusedLaneWedged",
    "CASRelinkConfirmRefusedLaneBroken",
    "CASRelinkConfirmRefusedStateLockBusy",
    "CASRelinkConfirmRefusedMountCannotSpeak",
    "CASRefNeedsRecovery",
    "CASRefSweepDeferred",
    "CASRefSweepRearmed",
    "CASRefStalePrecommitsReclaimed",
    "CASRefRollbackBestEffortDropFailed",
    "CASRefTableEvictions",
    "CASRefGlobalListPages",
    "CASRefLogBodyGets",
    "CASRefManifestBodyFoldGets",
    "CASRefEmittedEdges",
    "CASRefCleanupObjectsDeleted",
    "CASRefSnapshotPutBytes",
    "CASRefSnapshotTailLogs",
    "CASRefSnapshotPublishDispatched",
    "CASRefMaterializeInPlace",
    "CASRefMaterializeCopy",
    "CASRefSnapshotPublishBackoff",
    "CASRefCheckpointPublished",
    "CASRefCheckpointIdenticalSkip",
    "CASRefCheckpointNotAdvanced",
    "CASGCClampSuppressedPasses",
    "CASGCDeadPrecommitSkipped",
    "CASBlobGet",
    "CASBlobGetStream",
    "CASBlobDelete",
    "CASBlobList",
    "CASRefRepoint",
    "CASManifestPut",
    "CASManifestPutDeduplicated",
    "CASManifestOverwrite",
    "CASManifestCompareSwap",
    "CASManifestCompareSwapConflict",
    "CASManifestHead",
    "CASManifestHeadMiss",
    "CASManifestGet",
    "CASManifestGetStream",
    "CASManifestDelete",
    "CASManifestList",
    "CASRootPut",
    "CASRootPutDeduplicated",
    "CASRootOverwrite",
    "CASRootCompareSwap",
    "CASRootCompareSwapConflict",
    "CASRootHead",
    "CASRootHeadMiss",
    "CASRootGet",
    "CASRootGetStream",
    "CASRootDelete",
    "CASRootList",
    "CASGCPut",
    "CASGCPutDeduplicated",
    "CASGCOverwrite",
    "CASGCCompareSwap",
    "CASGCRetireReplaced",
    "CASGCCompareSwapConflict",
    "CASGCHead",
    "CASGCHeadMiss",
    "CASGCGet",
    "CASGCGetStream",
    "CASGCDelete",
    "CASGCList",
    "CASGCReadAheadHit",
    "CASGCReadAheadMiss",
    "CASGCReadAheadWasted",
    "CASServerPut",
    "CASServerPutDeduplicated",
    "CASServerOverwrite",
    "CASServerCompareSwap",
    "CASServerCompareSwapConflict",
    "CASServerHead",
    "CASServerHeadMiss",
    "CASServerGet",
    "CASServerGetStream",
    "CASServerDelete",
    "CASServerList",
    "CASOtherPut",
    "CASOtherPutDeduplicated",
    "CASOtherOverwrite",
    "CASOtherCompareSwap",
    "CASOtherCompareSwapConflict",
    "CASOtherHead",
    "CASOtherHeadMiss",
    "CASOtherGet",
    "CASOtherGetStream",
    "CASOtherDelete",
    "CASOtherList",
    "CASGCRetiredCondemned",
    "CASGCRetiredSpared",
    "CASGCRetiredSparedByReref",
    "CASGCRetiredGraduated",
    "CASGCRetiredRedeleted",
    "CASGCUnmatchedRemoveDeltas",
    "CASGCCondemnMarkerUnconfirmedCarry",
    "CASGCHeartbeatFenceOuts",
    "CASGCMetaWriteAnomaly",
    "CASMetaPut",
    "CASMetaCompareSwap",
    "CASMetaDelete",
    "CASMetaCreateClean",
    "CASMetaAdoptBackfill",
    "CASMetaResurrectClean",
    "CASGCMetaOps",
    "CASGCEnumerationPages",
    "CASBulkDeleteRequests",
    "CASGCRefWalkPlansBuilt",
    "CASGCUnmatchedAdoptedParentLives",
    "CASGCStuckRemovals",
    "CASGCNamespaceCleanupLeaks",
    "CASDetachedWorkDrainTimeouts",
    "CASEventDroppedContextExpired",
    "CASGCUnappliedFoldedTransactions",
    "CASGCRebuildVirginByEnumeration",
    "CASPartFolderViewHits",
    "CASPartFolderViewValidationMismatches",
    "CASPartFolderViewMisses",
    "CASPartFolderViewOversizedBypasses",
    "CASPartFolderViewInvalidations",
    "CASPartFolderManifestGets",
    "CASConditionalWriteAttempts",
    "CASConditionalWriteCommitted",
    "CASConditionalWriteDefiniteFailure",
    "CASConditionalWriteUnresolved",
    "CASConditionalWriteFenceLostPostWrite",
    "CASRequestAttempt",
    "CASRequestReissue",
    "CASRequestConflictPause",
    "CASRequestResolveRead",
    "CASRequestGaveUp",
    "CASRequestRefused",
    "CASRequestFenceLostPostWrite",
    "CASRequestConnectFailureHint",
    "CASRequestFirstAttemptFuse",
    "CASMountRenewalAttempts",
    "CASMountRenewalRetries",
    "CASMountRenewalResolved",
    "CASMountRenewalRecovered",
    "CASMountRenewalDeadlineExceeded",
    "CASMountLeaseLost",
    "CASRemountAttempts",
    "CASRemountSucceeded",
    "CASRemountFailed",
    "CASMountReleaseSkippedForeignOccupant",
    "CASMountExclusivityViolation",
    "CASRemountHeldTransient",
    "CASIdentityLost",
    "CASDataRootVanished",
    "CASRefRecoveryEpochSealed",
    "CASRefRecoveryEpochSealAdopted",
    "CASRefRecoveryStragglerAdopted",
    "CASRefRecoveryCancelled",
    "CASRefRecoveryStreamHole",
    "CASBlobAdoptTrusted",
)

CAS_CURRENT_METRICS = (
    "CASPartFolderCacheBytes",
    "CASPartFolderCacheEntries",
    "CASManifestDecodeCacheBytes",
    "CASManifestDecodeCacheEntries",
    "CASHotKeyCacheBytes",
    "CASHotKeyCacheEntries",
    "CASBlobUploadPoolThreads",
    "CASBlobUploadPoolThreadsActive",
    "CASBlobUploadPoolThreadsScheduled",
)

_CAS_NAME = re.compile(r"^CAS[A-Za-z0-9]+$")

# Write-path counters a first insert of new content must move. From
# ProfileEvents.cpp / CasPartWriteTxn / CasInstrumentedBackend / CasRefLedger.
# GC, recovery, conflict, and mount-loss events stay at zero here.
INSERT_PROFILE_EVENTS = (
    "CASBlobPut",
    "CASBlobUploadFanoutBatches",
    "CASBlobUploadFanoutTasks",
    "CASManifestPut",
    "CASMetaPut",
    "CASMetaCreateClean",
    "CASRefBatchedMutations",
    "CASRefBatchFlushes",
    "CASConditionalWriteAttempts",
    "CASConditionalWriteCommitted",
)


def _int_map(output):
    """Parse ``name\\tvalue`` rows into ``{name: int}``."""
    out = {}
    for line in output.splitlines():
        if "\t" not in line:
            continue
        name, value = line.split("\t", 1)
        try:
            out[name] = int(value)
        except ValueError:
            pass
    return out


def _cas_name(name):
    """Reject anything that is not a bare CAS identifier before it goes into SQL."""
    if not _CAS_NAME.fullmatch(name):
        raise ValueError(f"not a CAS metric name: {name!r}")
    return name


def cas_event(node, name):
    """Return one ProfileEvent from ``system.events``, including zero."""
    name = _cas_name(name)
    result = node.query(
        f"SELECT value FROM system.events WHERE event = '{name}' "
        "SETTINGS system_events_show_zero_values = 1"
    )
    value = result.output.strip()
    assert value.lstrip("-").isdigit(), error(
        f"{name} is not in system.events: {result.output}"
    )
    return int(value)


def cas_event_grew(node, name, before):
    """Assert ``name`` is strictly larger than the saved baseline."""
    after = cas_event(node, name)
    assert after > before, error(f"{name}: before={before} after={after}")
    return after


def cas_event_unchanged(node, name, before):
    """Assert ``name`` is still at the saved baseline."""
    after = cas_event(node, name)
    assert after == before, error(f"{name}: before={before} after={after}")
    return after


def cas_gauge(node, name):
    """Return one CurrentMetrics gauge from ``system.metrics``."""
    name = _cas_name(name)
    result = node.query(f"SELECT value FROM system.metrics WHERE metric = '{name}'")
    value = result.output.strip()
    assert value.lstrip("-").isdigit(), error(
        f"{name} is not in system.metrics: {result.output}"
    )
    return int(value)


def cas_events_snapshot(node):
    """All ``CAS*`` ProfileEvents on ``node``, including zeros.

    ``system.events`` omits a counter that has never incremented unless
    ``system_events_show_zero_values = 1``. Without that, "not in the binary"
    and "still zero" look the same.
    """
    result = node.query(
        "SELECT event, value FROM system.events "
        "WHERE event LIKE 'CAS%' "
        "FORMAT TabSeparated "
        "SETTINGS system_events_show_zero_values = 1"
    )
    return _int_map(result.output)


def cas_current_metrics(node):
    """All ``CAS*`` CurrentMetrics gauges on ``node``."""
    result = node.query(
        "SELECT metric, value FROM system.metrics "
        "WHERE metric LIKE 'CAS%' FORMAT TabSeparated"
    )
    return _int_map(result.output)


def cas_metrics(node):
    """All CAS ProfileEvents and CurrentMetrics on ``node``.

    Returns ``(events, gauges)``. Events are cumulative counters; gauges are
    the live cache / thread-pool sizes from ``system.metrics``.
    """
    return cas_events_snapshot(node), cas_current_metrics(node)


def cas_events_delta(before, after):
    """Positive deltas of CAS counters between two snapshots."""
    delta = {}
    for name, value in after.items():
        change = value - before.get(name, 0)
        if change > 0:
            delta[name] = change
    return delta


def blob_body_puts(delta):
    """Large blob body uploads in a CAS events delta."""
    return int(delta.get(BLOB_PUT, 0))


def blob_puts_avoided_or_deduped(delta):
    """Dedup / body-put-avoided signal that a fetch reused existing blobs."""
    return int(delta.get("CASBlobPutDeduplicated", 0)) + int(
        delta.get("CASBlobBodyPutAvoided", 0)
    )


@TestStep(Then)
@Name("assert the writer uploaded blob bodies")
def assert_blob_bodies_were_uploaded(self, delta):
    """Assert a writer's delta shows real blob uploads.

    This is the control for the relink proof: if the build never reports
    ``CASBlobPut`` then a flat counter on the reader proves nothing, so the
    absence of uploads on the writer is a harness failure, not a pass.
    """
    puts = blob_body_puts(delta)
    note(f"writer {BLOB_PUT}={puts}")
    assert puts > 0, error(
        f"expected blob bodies to be published but {BLOB_PUT}={puts}. Either the "
        f"payload was too small to create blob bodies or this build does not "
        f"report {BLOB_PUT}, in which case counter-based proofs are not "
        f"meaningful here. Observed CAS counters: {sorted(delta)}"
    )
    return puts


@TestStep(Then)
@Name("assert the reader did not re-upload blob bodies")
def assert_no_blob_reupload_on_fetch(self, delta, writer_puts, tolerance=0.25):
    """Assert a reader's delta looks like relink/dedup rather than re-upload.

    The bound is relative to what the writer actually uploaded: a byte fetch
    that re-published the same content would approach ``writer_puts``.
    """
    puts = blob_body_puts(delta)
    avoided = blob_puts_avoided_or_deduped(delta)
    limit = max(1, int(writer_puts * tolerance))
    note(f"reader {BLOB_PUT}={puts} (limit {limit}), avoided/deduped={avoided}")
    assert puts <= limit, error(
        f"reader re-uploaded blob bodies during fetch: {BLOB_PUT}={puts} "
        f"against a writer that uploaded {writer_puts}; fetch should relink "
        f"shared content instead of copying it. Reader delta: {delta}"
    )
