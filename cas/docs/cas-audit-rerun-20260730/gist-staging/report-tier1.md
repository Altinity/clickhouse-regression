# cas-tier1 — re-run 2026-07-30

Re-verification of the 16 Tier1 findings against `cas-audit-20260730`
(tracks `altinity/cas-gc-rebuild`, PR #2073) at HEAD `834c9517f56`.

## Scope in current code

- `src/Storages/MergeTree/DataPartsExchange.cpp` (sender + fetcher / relink)
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`
  - `ContentAddressedExchange.{h,cpp}` (relink wire types, confirm)
  - `ContentAddressedMetadataStorage.{h,cpp}` (namespace mapping, directory shape)
  - `ContentAddressedTransaction.{h,cpp}` (`removeDirectory`, `removeRecursive`, `moveDirectory`)
  - `ContentAddressedSettings.cpp` (`gc_enabled`, `gc_interval_sec`)
  - `Formats/CasBlobEnvelopeFormat.{h,cpp}` (envelope encode/decode; JSON envelope replaces earlier 94-byte binary+CityHash64 header)
  - `Formats/CasPartManifestFormat.{h,cpp}`
  - `Primitives/CasBlobDigest.{h,cpp}` (hash algos: CityHash128, XXH3_128, **Sha256** – new)
  - `Primitives/CasBlobHashingWriteBuffer.{h,cpp}` (write-time hasher)
  - `Pool/CasPool.{h,cpp}`, `Pool/CasRefLedger.{h,cpp}`, `Pool/CasRefProtocol.h`, `Pool/CasPartWriteTxn.{h,cpp}`, `Pool/CasManifestReader.cpp`
  - `Gc/CasGc.{h,cpp}`, `Gc/CasGcScheduler.{h,cpp}`, `Gc/CasOrphanManifestSweep.{h,cpp}`, `Gc/CasBlobInDegree.{h,cpp}`, `Gc/CasGcShardPlan.{h,cpp}`
  - `Tools/CasFsck.{h,cpp}` (Reachable / Dangling / Unreachable / PendingGc / AwaitingGc / Unaccounted / StaleEdge)
  - `Tools/CasInspect.{h,cpp}`, `Tools/CasDecommission.{h,cpp}`
  - `Backend/CasObjectStorageBackend.{h,cpp}`, `Backend/CasInMemoryBackend.{h,cpp}`, `Backend/CasProbe.{h,cpp}`

Note: several file names in the original audit (`Core/CasStore.cpp`, `Core/CasEnvelope.cpp`,
`Core/CasFsck.*`) no longer exist — the tree has been re-organised into
`Pool/`, `Formats/`, `Tools/`. Anchors below use the current paths.

## Findings still present

### RPL-2 (Med — ZK part-set ↔ CAS ref divergence on partial commit)

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:991-1073` (`removeDirectory`, `removeRecursive`) — CAS ref mutations are *call-time durable*, independent of the outer transaction that also mutates ZK / MergeTree state.
- Trigger: crash between the ZK add of a fetched replicated part and the durable CAS ref promote — or between a ZK drop and `dropRefIfPresent` — leaves ZK and pool disagreeing.
- Evidence quote (`ContentAddressedTransaction.cpp:993-1010`):
  > "CONTRACT: `removeDirectory`/`moveDirectory` mutate durable refs at CALL TIME, not at commit … `removeDirectory(<part>)` – the SINGLE authoritative point at which the part's ref must" (drop.)
- Notes: no cross-registry two-phase commit was added. Same DUR1 face; still no orphan-namespace sweeper (see LC-2), so the CAS-has / ZK-missing branch still bleeds into a silent leak.

### RPL-3 (Med — relink promote ⨯ shared-pool GC TOCTOU)

- Anchor: `src/Storages/MergeTree/DataPartsExchange.cpp:1388-1600` (`Fetcher::relinkPartToDisk`, `adoptPartFromManifest`); confirm primitive: `ContentAddressedExchange.h:15-100`; ref-ledger confirm: `Pool/CasRefLedger.cpp` (`confirmExactRef`).
- Trigger: between offer and receiver promote, a GC round in the shared pool graduates a blob from `delete_pending` → `deleteExact` for a source-edge that becomes stale.
- Evidence quote (`DataPartsExchange.cpp:1381-1388`):
  > "A confirmed relink is therefore NOT proven" (dangle-free under all listing-page interleavings — TLA config `_sab_holeylist` shows `ConfirmedRelinkNeverDangles` still breaks with `{#list-as-journal-dataloss-2026-07-25}`.)
- Notes: **partially mitigated** by the new publish-then-confirm second RPC (`CasConfirmAnswer`, `CasRelinkSourceToken`) that gates promotion on the source still holding the exact manifest, plus the token gate at `DataPartsExchange.cpp:1418-1421` and the row-6 mount-fence ordering call-out. The residual window (list-page holes) is *documented in-code* but explicitly open. No dedicated integration test. Verdict: still-present, better defended.

### RPL-5 (Low — quorum / SYNC REPLICA / cloneReplica untested on CAS)

- Anchor: no CAS-scoped test hooks in `src/Disks/…/ContentAddressed/` reference these paths. Grep for `quorum|cloneReplica|SYNC.*REPLICA|REPLACE_RANGE|DROP_RANGE` inside the CAS subtree returns zero matches.
- Trigger: composition of many fetches / drops (some of which relink) on a table with CA disk — never exercised end-to-end.
- Notes: unchanged.

### LC-1 (Med — DROP TABLE frees no bytes synchronously; hard leak if GC off)

- Anchor: `ContentAddressedTransaction.cpp:1032-1074` (`removeRecursive` for table dir); `ContentAddressedSettings.cpp:72` (`gc_enabled` still defaults `true`, still per-disk togglable); `Gc/CasGc.cpp` — no synchronous reclaim entry point exposed to `DROP TABLE`.
- Trigger: `DROP TABLE t` returns after only tombstoning refs; S3 bytes remain until a full GC round cycle catches up. If `gc_enabled=false` (or the last writer of a pool has been decommissioned before GC folds), the bytes are permanently leaked.
- Evidence quote (`ContentAddressedTransaction.cpp:1068-1073`):
  > "Table dir: the table's namespace (live + folded-in detached refs) and every verbatim file go in one dropNamespace." (no synchronous blob delete; comment above says "blobs/trees are reclaimed by Cas::Gc once unreachable").
- Notes: still no `SYSTEM RECLAIM` / DROP-nudge hook, no `bytes_pending_reclaim` metric surfaced in `system.*` (grep in the CAS tree returns only precommit-reclaim events, `CasRefStalePrecommitsReclaimed` at `Pool/CasRefLedger.cpp:54`). Operational surprise unchanged.

### LC-2 (Med — crash between catalog drop and `dropNamespace` → permanent orphan namespace)

- Anchor: `ContentAddressedMetadataStorage.cpp` — `listNamespaces` is exposed (`ContentAddressedMetadataStorage.cpp:1472`) but not called by any reconciler that would compare pool namespaces against the ClickHouse catalog. `Gc/CasOrphanManifestSweep.{h,cpp}` still scopes strictly to "one writer build prefix under `cas/manifests/<ns>/`" (`CasOrphanManifestSweep.h:12-19` "One writer build prefix … the canonical `<epoch-hex>-<seq-hex>/` directory") — pre-precommit manifest debris only, not fully-committed orphaned refs at namespace granularity.
- Trigger: server crash after table `.sql` is removed and before `removeRecursive` finishes → the CAS namespace's refs are still live, no owning table exists to ever drop them.
- Notes: identical to original; a dedicated orphan-namespace sweep (catalog-vs-pool reconciliation) has not been added.

### LC-3 (Low — cross-pool DROP is per-server; correctly preserves shared blobs)

- Anchor: `ContentAddressedTransaction.cpp:1072` (`dropNamespace(liveNamespace(*uuid))` scoped to this server's namespace only).
- Notes: still holds, still by-design-correct.

### LC-4 (Info — TRUNCATE = drop all part refs, keep namespace; deferred reclaim)

- Anchor: same removeRecursive machinery; table namespace survives, per-ref drops apply.
- Notes: unchanged, informational.

### INT-1 (High — blob payload not re-verified against its content hash on read)

- Anchor: `Formats/CasBlobEnvelopeFormat.cpp:162-260` (`decodeEnvelopeHeader`) — envelope decode only validates JSON structure, magic (`type=cas_blob`), `compatibility_version`, pad zone, and ref-echo; there is no payload-hash field in the current JSON envelope at all, and no `logical_hash`/`payload_digest` verification anywhere in the read path.
- Trigger: silent S3 payload bit-rot or truncation inside the payload region is undetected by CAS.
- Evidence: grep over `src/Disks/…/ContentAddressed/` for `verifyPayload|payload.*mismatch|content.*hash.*mismatch|rehash` returns **zero** matches. `CasBlobHashingWriteBuffer.{h,cpp}` produces the digest at write time; nothing consumes it as an integrity check on read.
- Notes: **worsened** in one respect vs. the original write-up: the earlier binary envelope at least carried `logical_hash` in the header (even if not checked on read); the current JSON envelope does not persist a payload hash in the envelope itself (identity lives in the object key + `.meta`), so any read-time verification would require an extra fetch of the `.meta` sibling. The original recommendation ("optional read-time verify") is not implemented; fsck (`Tools/CasFsck.h:16-160`) still only classifies presence/reachability, never re-hashes payloads.

### INT-2 (Med — dedup trusts the hash; collision or mis-key silently shares wrong bytes)

- Anchor: `Primitives/CasBlobDigest.h:38-96` — three algorithms supported: `CityHash128`, `XXH3_128`, `Sha256`.
- Notes: **partially mitigated** — `Sha256` is now an available `blob_hash` (parsed at `parseBlobHashAlgo`), so operators concerned with collision resistance can opt in. But default remains a non-cryptographic hash for existing pools (`BlobRef::algo` default `= BlobHashAlgo::CityHash128` at `CasBlobDigest.h:209`), and there is still no read-time verify (INT-1) that would catch a collision or mis-key. Verdict: still-present at default settings; opt-out is possible.

### INT-3 (Med — fsck Dangling = already-lost data; no auto-repair; no forced cadence)

- Anchor: `Tools/CasFsck.h:27-73` (`FsckClass::Dangling` = "reachable from a live ref but the object is MISSING — INV-NO-LOSS violation"); no re-fetch-from-replica helper in `Tools/CasFsck.cpp`, no scheduler in `Gc/CasGcScheduler.{h,cpp}` invoking fsck on a cadence.
- Notes: unchanged. Fsck remains detector-only.

### INT-4 (Low — no proactive scrubbing)

- Anchor: `Gc/CasGcScheduler.h` schedules the GC/dedup housekeeping loop only; grep for `scrub|bitrot|bit_rot` in the CAS tree — zero matches.
- Notes: unchanged.

### MVCC-1 (Med — R1/X1 storage-dangle window is the real MVCC exposure)

- Anchor: `Gc/CasGc.cpp:367` (`e.reason = "R1: heartbeat classification (live/terminated/fenced mounts)"`) — R1 is still named as a live classification in GC; no reader-side CAS-level pin on a blob (only MergeTree `old_parts_lifetime` on the part).
- Trigger: aggressive GC + long-running query + part turning Outdated mid-query → ranged GET on deleted object → fail-loud query error.
- Notes: still-present; still fail-loud, not wrong-results.

### MVCC-3 (Low — FINAL / parallel-replicas / patch-apply-on-read unverified on CAS)

- Anchor: no test hooks; the CAS tree has no code that specialises for `FINAL` / parallel-replica reads. Grep for `FINAL|parallel.*replica|patch.*apply` in the CAS subtree returns matches only inside GC / ref-protocol comments (unrelated senses of the word).
- Notes: unchanged.

## Findings fixed / no longer reproducible

### RPL-4 (Med → **✅ fixed** — `to_detached` relink is now enabled; `FETCH PARTITION` can relink)

- Anchor for the fix: `src/Storages/MergeTree/DataPartsExchange.cpp:693-725` (`Service::sendPartFromDisk` — relink offer now gated on `allow_ca_relink` alone; the `try_zero_copy && !to_detached` gate is explicitly removed) and `DataPartsExchange.cpp:1388-1451` (`Fetcher::relinkPartToDisk` now takes `to_detached` and stages under the `detached/` parent).
- Evidence quote (`DataPartsExchange.cpp:700-704`):
  > "The gate used to be `try_zero_copy && !to_detached`, and BOTH halves were accidents of that same brake — `try_zero_copy` because the fallback re-requests with it false, and `!to_detached` because the relink path staged at the ACTIVE part path and ignored `to_detached`. `to_detached` is now a parameter of `relinkPartToDisk` (it stages under the `detached/` parent), and `try_zero_copy` goes back to meaning real zero-copy only."
- Notes: the FETCH PARTITION perf cliff called out in RPL-4 is closed for the same-pool case.

## New findings (not in original audit)

### NEW-tier1-1 (Med) — publish-then-confirm mount-fence rule-6 ordering trap

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedExchange.h:21-27` (`CasConfirmAnswer` doc comment).
- Trigger: any caller that treats `CasConfirmAnswer::No` (as opposed to only `Yes`) as authoritative — e.g. "skip the retry, part is gone" — makes the mount-fence ordering wrong (rule 6 is evaluated LAST inside `confirmExactRef`, so a fenced mount that has already lost its right to speak for the namespace still answers `No` for a token that does not match its last-known row).
- Evidence quote (`ContentAddressedExchange.h:20-26`):
  > "ONLY `Yes` AUTHORIZES ANYTHING. `No` and `Unknown` are one outcome for every caller … Any code that ever treats `No` as authoritative knowledge (say, to skip a retry or to conclude the part is gone) makes that ordering wrong and must hoist rule 6 above the row comparison first."
- Notes: a landmine for future changes to the fetch fallback logic; enforced only by a comment. A static assertion or a helper that collapses `No`/`Unknown` into a single `NotProven` enum in the calling code would prevent regression.

### NEW-tier1-2 (Med) — envelope format schema change loses persisted `logical_hash`, breaking any future opportunistic read-verify

- Anchor: `Formats/CasBlobEnvelopeFormat.cpp:87-160` (`encodeEnvelopeHeader`) and `:162-260` (`decodeEnvelopeHeader`).
- Trigger: the new JSON envelope schema deliberately excludes the payload hash from the envelope (fields present: `type`, `v`, `tag`, `bld`, `ts`, `by`, `op`, `ch`, `ref`) — the content hash lives only in the object key path (`blobs/<algo>/<shard>/<hex>`) and the `.meta` sibling. This means an "opportunistic read-time verify" (INT-1 remediation) cannot be a pure envelope-parse operation any more; it requires an extra fetch of `.meta` or a compare-against-object-key derivation that opens its own trust question (the key can be trusted only insofar as the requester itself supplied it — a MITM'd path resolution is out of scope but the check is no longer self-contained).
- Notes: increases the cost of ever closing INT-1. If the header were extended to echo the payload digest (or its short-form), read-time verify becomes O(payload) with no extra RTT. Not urgent, but recommend adding a `pd` (payload-digest) field to a bumped envelope version and gate a strict-verify setting on it.

### NEW-tier1-3 (Low) — `gc_enabled=false` has no operational guardrails vs. LC-1

- Anchor: `ContentAddressedSettings.cpp:72` (`DECLARE(Bool, gc_enabled, true, "Run the background GC scheduler on this disk", 0)`).
- Trigger: an operator can flip `gc_enabled=false` on a live pool (staging / freeze scenarios); combined with LC-1, any DROP / TRUNCATE / part-drop during that window silently accumulates unrecoverable S3 bytes with **no** warning at DROP time and **no** counter surfacing pending-reclaim size.
- Notes: recommend either (a) refuse `DROP TABLE` when `gc_enabled=false` unless `--force-leak-ok`, or (b) emit a warning and expose a `system.disks`-level pending-reclaim column. Neither exists today.

## By-design / N/A / info

- **RPL-1** (`✅ still-sound-by-design`): relink contract remains fail-closed on identity (pool_uuid equality, sender identity non-authoritative, revalidation in `promote`). Publish-then-confirm STRENGTHENS RPL-1: an unproven source now degrades to a byte fetch instead of a bare adopt. Anchor: `ContentAddressedExchange.h:15-100`, `DataPartsExchange.cpp:1388-1451`.
- **MVCC-2** (`⚪ info — no wrong-results anomaly`): unchanged. Immutability + content-address preserves "read committed bytes or fail loudly". No new snapshot machinery.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| RPL-1 | Info | 📐 by-design (strengthened) | `ContentAddressedExchange.h:15-100`; `DataPartsExchange.cpp:1388-1451` |
| RPL-2 | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:991-1073` |
| RPL-3 | Med | 🔴 still-present (better defended) | `DataPartsExchange.cpp:1381-1600`; `Pool/CasRefLedger.cpp` `confirmExactRef` |
| RPL-4 | Med | ✅ fixed | `DataPartsExchange.cpp:693-725, 1388-1451` |
| RPL-5 | Low | 🔴 still-present (untested) | CAS tree grep: `quorum\|cloneReplica\|SYNC.*REPLICA` = 0 matches |
| LC-1 | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1032-1074`; `ContentAddressedSettings.cpp:72` |
| LC-2 | Med | 🔴 still-present | `Gc/CasOrphanManifestSweep.h:12-19`; `ContentAddressedMetadataStorage.cpp:1472` |
| LC-3 | Low | 📐 by-design (correct) | `ContentAddressedTransaction.cpp:1072` |
| LC-4 | Info | ⚪ info | `ContentAddressedTransaction.cpp:1068-1073` |
| INT-1 | High | 🔴 still-present (arguably worse — envelope now lacks payload hash field) | `Formats/CasBlobEnvelopeFormat.cpp:162-260`; `Tools/CasFsck.h:16-160` |
| INT-2 | Med | 🔴 still-present (partially mitigated by SHA-256 opt-in) | `Primitives/CasBlobDigest.h:38-96, 209` |
| INT-3 | Med | 🔴 still-present | `Tools/CasFsck.h:27-73` |
| INT-4 | Low | 🔴 still-present | CAS tree grep: `scrub\|bitrot` = 0 matches |
| MVCC-1 | Med | 🔴 still-present | `Gc/CasGc.cpp:367` |
| MVCC-2 | Info | ⚪ info | (semantic property, unchanged) |
| MVCC-3 | Low | 🔴 still-present (untested) | CAS tree grep: `FINAL\|parallel.*replica` in relevant sense = 0 matches |
| NEW-tier1-1 | — | 🟡 needs-fix | `ContentAddressedExchange.h:21-27` |
| NEW-tier1-2 | — | 🟡 needs-fix (blocker for closing INT-1) | `Formats/CasBlobEnvelopeFormat.cpp:87-260` |
| NEW-tier1-3 | — | 🛠 will-fix | `ContentAddressedSettings.cpp:72` |

## Counts

- Original Tier1 findings: 16.
- 🔴 still-present: 12 (RPL-2, RPL-3, RPL-5, LC-1, LC-2, INT-1, INT-2, INT-3, INT-4, MVCC-1, MVCC-3 — plus INT-2 partially mitigated).
- ✅ fixed: 1 (RPL-4).
- 📐 by-design / correct: 2 (RPL-1, LC-3).
- ⚪ info: 2 (LC-4, MVCC-2).
- NEW findings: 3 (NEW-tier1-1, NEW-tier1-2, NEW-tier1-3).
