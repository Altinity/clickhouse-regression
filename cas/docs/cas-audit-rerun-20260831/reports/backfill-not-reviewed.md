# backfill-not-reviewed -- fresh audit 2026-08-31

## Scope
Anything in the CAS tree this batch's other ten audits do not own: **plain objects**, **event dispatcher**, **tools**, **clickhouse-disks**.

- Files/dirs examined: `Pool/CasPlainObjects.{h,cpp}`, `Pool/CasEventDispatcher.{h,cpp}`, `Tools/CasInspect.{h,cpp}`, `Tools/CasFsck.{h,cpp}` (only surfaces not claimed by gc/tier1), `Tools/CasDecommission.{h,cpp}` (prefix already in tier2; remaining tool UX), `programs/disks/CommandCa{Inspect,GcDryRun,GcRebuild,DropMember}.cpp`, `DisksApp.cpp` registration, `benchmarks/benchmark_cas_ref_protocol.cpp` (existence only).
- Explicitly out of scope: re-auditing Backend/Gc/RefLedger (other batches); inventing accountability-of-the-round findings.

## Findings
### backfill-not-reviewed-1 -- `cas-inspect` has no decoder branch for pool meta, catalog, owner, epoch, GC outcomes/heartbeat, or janitor state (Low)
- Anchor: `Tools/CasInspect.cpp:567-636` (`caInspectToJson` recognized prefixes: manifests, ref ckpt/snap/log, `gc/state`, `/mount`, `/fold_seal`, blob-target runs, `blobs` / `.meta`). No `poolMetaKey`, `refCatalogKey`, owner/epoch keys, `GcOutcomes`, `GcHeartbeat`, `GcMaintenanceState`.
- Trigger: `clickhouse-disks cas-inspect` on `_pool_meta`, `cas/ref_catalog`, `gc/server-roots/<srid>/owner|epoch`, a GC outcomes object, or the janitor cursor.
- Evidence: the command throws `unrecognized key layout`. Those objects are live and are what an operator inspects during mount/GC incidents. Format unit tests exist; the CLI does not decode them. Same class as the 08-12 inspect-completeness gap, narrowed (mount/fold_seal/runs/ckpt are now present).
- Notes: former inspect residual / CAS-097 class.

### backfill-not-reviewed-2 -- namespace-file CAS retries 100 times with no sleep (Low)
- Anchor: `Pool/CasPlainObjects.cpp:18,40-56` (`MAX_CAS_ATTEMPTS = 100`; loop is head + putIfAbsent/putOverwrite; comment says retry on `PreconditionFailed` only).
- Trigger: two writers on the same verbatim namespace file (not the production mutation-entry single-appender path). Or a token that never matches.
- Evidence: the loop has no backoff. Production appender is documented as single-writer (`ContentAddressedTransaction.cpp:825-832`). Residual is a live-lock delay on a violated invariant, then `ABORTED`. Same class as CAS-011's "100 sleepless attempts" half.
- Notes: CAS-011 residual.

### backfill-not-reviewed-3 -- event dispatcher still builds every event even when the SQL sink is unused, and the queue is unbounded under one mutex (Low)
- Anchor: `Pool/CasEventDispatcher.cpp:10-54` (`setSink`, `emit` pushes then drains; sink runs unlocked). Shipping config installs a `cas_log` sink; removing the section still leaves a sink that discards (prior observation — confirm: `has_sink` is whatever `setSink` last stored; if a no-op sink is installed, events are still built by callers).
- Trigger: high-rate `createHardLink` / resolve (already HEADs per file) on a pool whose `system.cas_log` is disabled or full.
- Evidence: `emit` always enqueues. A slow or discarding sink serializes builders on `mutex` only for the push, then drains. Unbounded `queue` if the sink is slower than emit. Diagnosability/cost, not a protocol break. Same class as CAS-104 residual.
- Notes: CAS-104.

## By-design / info / non-actionable
- `casPutObject` single-appender invariant is documented and matches the only production appender (mutation-entry CSN).
- `clickhouse-disks` CAS verbs are registered (`cas-inspect`, `cas-gc-dryrun`, `cas-gc-rebuild`, `cas-drop-member`). Rebuild/drop-member require a read-only disk open.
- `CasFsck` remains counts-oriented on the SQL path; repair is a different verb. Not re-opened here.
- The ref-protocol microbenchmark exists (`benchmarks/benchmark_cas_ref_protocol.cpp`) and is not a product surface.

## Closed-since-2026-08-12
- Detached work is a tracked dispatcher drained at shutdown (`205af29c7f2`) — no longer an unowned thread class in this backfill.
- `cas_` settings prefix (`917600b122b`) — settings loading is not a leftover.

## Coverage
- Reviewed: `CasPlainObjects` CAS loop; `EventDispatcher` emit/drain; `cas-inspect` dispatch vs `FormatId`; clickhouse-disks command set and readonly gates.
- N-A: Backend/Gc/RefLedger (other audits).
- Deferred: whether `system.cas_log` can be fully uninstalled without a discard sink (would need the interpreter wiring, outside this tree walk).
