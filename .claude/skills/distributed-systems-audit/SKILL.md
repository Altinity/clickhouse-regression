---
name: distributed-systems-audit
description: Perform a static, distributed-systems-focused audit of a PR or feature. Use when reviewing changes to replication, cluster coordination, RPC/network paths, consensus- or Keeper-style dependencies, multi-node protocols, distributed state, retries/timeouts, or any logic whose correctness depends on behavior across nodes under partial failure.
---

# Distributed-Systems Audit

## Purpose

Run a repeatable static audit focused on **distributed-systems failure modes** and report **confirmed defects** with severity, grouped by fault class. Default mode is static reasoning unless runtime execution is explicitly performed.

This skill is **narrower and DS-first** compared to the broader [`audit-review`](../audit-review/SKILL.md) skill:

- Use **this skill** when the risk surface is dominated by cross-node behavior: RPC, replication, coordination, leases/fencing, quorum, retries/idempotency, recovery, version skew.
- Use **`audit-review`** when you need the full transition-matrix + C++ bug-class + interleaving matrix for a complex local feature.
- Running both is fine; deduplicate findings by root cause when you do.

## Workflow

1. **Establish the distributed model**:
   - Identify **actors** (nodes, clients, services, workers, coordinator/leader, Keeper/ZK, object store).
   - Identify **channels** between them (sync RPC, async queues, replicated logs, shared storage, broadcast).
   - Identify **authoritative state** for each piece of data (who owns it, who may cache it, who may write it).
   - Note the **failure model the code assumes** vs. what the environment actually provides (crash-stop vs. crash-recover, reliable vs. lossy messages, bounded vs. unbounded delay, synchronous vs. partially synchronous clocks).

2. **Per-class logical review**. Walk the fault classes below in order. For each class: either analyze it or mark **N/A** with a one-line justification.

3. **Fault injection (mental tests)**: For each applicable class, reason about **minimal realistic triggers** (timeout after commit, duplicate retry, partition between A and B, peer on older version, clock jump, slow disk on one replica) and verify the code fails **safely** (define "safe" per feature: no data loss, no split brain, bounded unavailability, idempotent effect, etc.).

4. **Evidence**: Each confirmed defect must cite **file + function/code path** and the **trigger** that reveals it. Static reasoning only unless the user asked for runtime reproduction.

5. **Coverage accounting**: Record which fault classes were **Reviewed / N/A / Deferred** and why.

## Fault Classes (fixed spine)

Walk these in order. Keep each class in scope or explicitly mark N/A.

### 1. Network / transport
- Timeouts present, finite, and propagated; no unbounded waits on sockets, futures, or locks held across I/O.
- Retry policy: bounded attempts, backoff, jitter; retries only on safe (idempotent) operations.
- Connection lifecycle: half-open connections, reconnect storms, connection reuse after error.
- Error classification: transient vs. terminal mapped correctly; errors not silently swallowed or remapped to success.

### 2. Partition / availability
- Behavior when a subset of peers is unreachable: does the code make progress, block, or produce wrong answers?
- Quorum/majority assumptions explicit and enforced; minority side cannot accept authoritative writes.
- Split-brain risk: two nodes believing they are leader/primary; presence of fencing tokens, epochs, or leases.
- Stale-read window bounded (or documented) after failover.

### 3. Timing / ordering
- Happens-before across nodes established by the mechanism the code actually uses (log index, term/epoch, version, Lamport/vector clocks) — not by wall clock unless intended.
- Wall-clock dependence audited: clock skew, NTP jumps, monotonic vs. realtime clocks.
- Monotonicity of versions/epochs/sequence numbers preserved across restart and failover.

### 4. Partial / gray failure
- Slow-but-alive peers: timeouts detect them without starving the healthy path.
- Ambiguous outcomes: request may have succeeded on the peer even though the caller saw an error — the code must assume "maybe done" and reconcile.
- Asymmetric reachability (A→B works, B→A doesn't) doesn't cause silent divergence.

### 5. Idempotency & duplicates
- At-least-once delivery assumed for any retried operation; effects are idempotent or deduplicated by stable key (request ID, version, fencing token).
- Duplicate application to state (replicated log, local commit) cannot double-count.
- Retried writes after ambiguous failure do not violate invariants.

### 6. Backpressure & resource limits
- Queues/buffers are bounded; overflow policy is explicit (drop, block, shed, reject) and safe.
- No memory growth proportional to unacked/in-flight work without a cap.
- Timeouts are not longer than upstream timeouts in ways that cause cascading retry amplification.
- Slow consumers cannot pin shared resources (threads, fds, locks) indefinitely.

### 7. Recovery & rollback
- Crash at every intermediate point of a multi-step protocol leaves either a resumable or a cleanly-aborted state; no orphaned resources or half-applied state.
- Startup reconciliation (replay log, scan state, query peers) converges to a consistent view before serving traffic.
- Partial failure of a multi-target write is handled (compensate, fence, retry) rather than left inconsistent.

### 8. Configuration & version skew
- Mixed-version clusters during rolling upgrades: new code handles old peers and vice versa (or upgrade is explicitly gated).
- Feature flags and config changes applied atomically per node; no window where half the cluster acts on the new rule and half on the old.
- Schema/format changes backward- and forward-compatible within the supported skew window.

### 9. Security / trust across nodes (if applicable)
- Peer identity authenticated (not just network-reachable).
- Authorization checks not bypassed via internal RPC path.
- No confused-deputy: a low-privilege caller cannot use the service to act with the service's credentials against another peer.

### 10. Observability & diagnosability
- Errors preserve root cause across node boundaries (no "RPC failed" with the real cause dropped).
- Correlation IDs / trace context propagated across hops.
- Logs/metrics distinguish transient from terminal failure, and local from remote cause.

## Severity Rubric

- **High**: realistic trigger leads to data loss, split brain, silent wrong answer, or unbounded unavailability.
- **Medium**: correctness/reliability issue with narrower trigger (specific partition shape, specific timing, specific mixed-version window).
- **Low**: diagnosability or consistency-of-behavior issues without direct correctness break.

## Output Contract (Required)

Always perform the full workflow above, but keep the final user-visible report short and grouped by fault class.

```markdown
AI audit note: This review comment was generated by AI (<model>).

Distributed-systems audit for PR #<id> (<short title/scope>):

Model assumptions:
- Actors: <one line>
- Channels: <one line>
- Failure model assumed by code: <one line>

Confirmed defects:

### <Fault class name>

    <Severity>: <short defect title>
        Impact: <concrete cross-node impact>
        Anchor: <file> / <function or code path>
        Trigger: <smallest realistic distributed trigger>
        Why defect: <1-2 lines, behavior not preference>
        Fix direction (short): <1 line>
        Regression test direction (short): <1 line>

<repeat defects under their class, sorted High -> Medium -> Low>

Coverage summary:

    Classes reviewed: <list by name>
    Classes N/A: <list with one-line reason each>
    Classes deferred: <list with one-line reason each>
    Assumptions/limits: <one line>
```

If no confirmed defects:
- output `No confirmed distributed-systems defects in reviewed scope.`
- still include `Model assumptions` and `Coverage summary`.

### Short-form constraints (required)

- Only include **confirmed** defects with code-path evidence.
- Group by fault class; do not re-describe the workflow in the report.
- Use snippets only when needed to prove a defect, or when the user asks.

## Non-goals

- Not a replacement for language-level audits (use-after-free, UB, iterator invalidation, lock-order within one process). Those belong in [`audit-review`](../audit-review/SKILL.md), unless the defect only manifests as a distributed hazard (e.g. a race that corrupts replicated state).
- Not a performance audit unless a resource/backpressure issue causes correctness or availability loss.

## Checklist

- Actors, channels, and authoritative state explicitly identified.
- Failure model assumed by the code is stated and compared to reality.
- Each fault class is either reviewed or explicitly marked N/A with reason.
- Minimal realistic triggers are stated per defect.
- Safe-failure criterion is defined per feature (no data loss / no split brain / bounded unavailability / idempotent effect).
- Evidence cites file + code path for every confirmed defect.
- Findings are deduplicated by root cause across fault classes.
- Coverage summary lists reviewed / N/A / deferred classes.
- Severity reflects realistic impact, not theoretical worst case.
