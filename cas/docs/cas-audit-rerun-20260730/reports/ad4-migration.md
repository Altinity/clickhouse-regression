# ad4-migration — re-run 2026-07-30

## Scope in current code

- CAS root walked (files scanned for migration-relevant hooks): `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/**`
  - `Backend/CasObjectStorageBackend.cpp`, `Pool/CasPartWriteTxn.cpp`, `Pool/CasPool.cpp`,
    `Parts/PartFolderAccess.cpp`, `ContentAddressedTransaction.cpp`,
    `ContentAddressedMetadataStorage.cpp`, `Formats/CasBlobEnvelopeFormat.{h,cpp}`.
- Adjacent CAS integration hooks:
  - `src/Storages/MergeTree/MergeTreeData.cpp` (partition-command gating, RESTORE tx wrap, `movePartitionToShard`)
  - `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp` (`clonePart` CA-aware branch)
  - `src/Storages/MergeTree/MergeTreePartsMover.cpp` (calls `clonePart` on cross-disk MOVE)
  - `src/Storages/MergeTree/DataPartsExchange.cpp` (fetch-by-relink, `to_detached` handling)
- Scope focus (per user): onto-CAS / off-CAS migration, verify-vs-hash on landing, provenance,
  CAS-041 (cross-disk MOVE + no relink on CAS→CAS same-pool), CAS-210 (dedup on landing without verify).

## Findings still present

**MIG-1 (Med — no in-place conversion; migration is always a full data rewrite)** — 🔴 still-present
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/README.md` (CAS is a
  `metadata_type`), `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartPathParser.{h,cpp}`
  (content-addressed key layout, no plain→CAS metadata mapper).
- Trigger: any onto-CAS/off-CAS migration.
- Evidence: no `metadata_type` conversion utility exists in the CAS tree; every landing path streams
  bytes through the writer. `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:748` (`copyDirectoryContentIntoTransaction`
  streams source bytes into the destination CA transaction).
- Notes: unchanged — a metadata flip fast-path was never in scope for this PR.

**MIG-2 (Med — cross-disk MOVE onto/off CAS still uses byte-copy `clonePart`; explicitly unverified)** — 🔴 still-present
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:6740-6743` — the in-code note is verbatim:
  > `NOTE: MOVE_PARTITION also admits cross-disk MOVE ... TO DISK/VOLUME (this check cannot distinguish
  > the destination); that uses the byte-copy clonePart path (NOT the corrupting per-file hardlink), but
  > only same-disk MOVE ... TO TABLE is verified here — cross-disk is a follow-up to verify.`
- Anchor: `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:735-758` — the CA-aware `clonePart`
  branch wraps `copyDirectoryContentIntoTransaction` in ONE disk transaction. This handles the
  per-file-autocommit hazard, but it is still byte-streamed reads (via `src_disk.readFile`) into
  a fresh CAS write path on the destination.
- Anchor: `src/Storages/MergeTree/MergeTreePartsMover.cpp:275-282` — calls `clonePart` (or, on zero-copy disks,
  `tryToFetchIfShared`); no CAS-aware branch, no same-pool test.
- Trigger: `ALTER TABLE ... MOVE PARTITION ... TO DISK/VOLUME` where source or destination is CAS,
  including CAS→CAS same-pool.
- Evidence: `Grep 'isSamePool|getPoolUUID' src/Storages/MergeTree/MergeTreePartsMover.*` returns nothing.
  The mover has zero awareness of CAS pool identity.
- Notes: the "cross-disk is a follow-up to verify" comment is unchanged since the original audit; no
  test/integration lands the verification.

**MIG-3 (Med — migration onto CAS + GC-deferred off-CAS source reclaim double-bills)** — 🔴 still-present
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp` (GC is the sole
  reclaim path; blobs persist until the next GC round advances `folded_cursor`).
- Anchor: `src/Storages/MergeTree/MergeTreePartsMover.cpp:328-...` — the `swapClonedPart` path drops
  the source ref through the normal detach/remove flow; on CAS the ref-drop schedules blob reclaim for GC,
  not eager delete.
- Trigger: any bulk MOVE onto/off CAS on a large table.
- Evidence: no reclaim-aware pacing / throttle couples migration rate to GC reclaim rate.

**MIG-4 (Med — mixed CAS + non-CAS storage policy inherits the CAS ALTER allowlist for the whole table)** — 🔴 still-present
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:6718-6753` — the CAS branch of the allowlist
  applies whenever ANY volume in the policy is CAS (per-disk check), so a partition currently on a
  non-CAS volume is still bound by the CAS supported-command list. Command list has grown since the
  original audit (now includes `FORGET_PARTITION`, `FREEZE_PARTITION`, `FREEZE_ALL_PARTITIONS`,
  `FETCH_PARTITION`), but the narrowing effect on `ALTER` surface remains — anything not on this list
  throws `SUPPORT_IS_DISABLED`.
- Trigger: adding a CAS volume to an existing storage policy of a non-CAS table.
- Evidence quote: `can_execute_alter_on_disk = std::ranges::contains(supported_commands, command.type);`
  (same file, per-disk loop).
- Notes: no mount-time warning or documentation guard.

**MIG-5 (Med — no bulk cross-replica warm-start / adopt-refs import)** — 🔴 still-present
- Anchor: `src/Storages/MergeTree/DataPartsExchange.cpp:693-725` — pool-UUID advertisement is
  per-part fetch only, no bulk-namespace import.
- Trigger: bringing up a new replica onto a shared CAS pool for a huge table.
- Evidence: `Grep 'listNamespaces|bulk.*import|adopt.*refs' src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/**` — no operator-facing adopt-all-refs primitive.
- **Partial mitigation since original audit:** `to_detached` fetch NOW relinks (was the RPL-4 hole).
  See `DataPartsExchange.cpp:702-704`:
  > `to_detached` is now a parameter of `relinkPartToDisk` (it stages under the `detached/` parent)
  Original audit called this "`FETCH PARTITION ... TO detached` never relinks (RPL-4)" — this specific
  sub-item is FIXED. The bulk warm-start finding otherwise stands.

**MIG-6 (Low — off-CAS migration reads via CAS read path with no payload re-verify (INT-1))** — 🔴 still-present
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp`
  — reads are plain ranged GETs; no BLAKE re-hash after read. Only the manifest/envelope headers are
  parsed on decode. INT-1 (no read-path payload re-verify) is inherited by any off-CAS migration.
- Anchor: `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:707-710` — off-CAS path does
  `src_disk.readFile(...)` → `copyData(*in, *out)`, no hash check between read and write.
- Trigger: `MOVE PARTITION ... TO DISK/VOLUME` from CAS to non-CAS (or any off-CAS `INSERT SELECT`).
- Notes: MergeTree part-level checksums (`checksums.txt`) provide indirect protection at part-load time,
  but nothing forces a re-verify at migration time.

**MIG-7 (Low — BACKUP/RESTORE migration inherits BAK-1 Atomic-DB requirement)** — 🔴 still-present
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:7508-7551` — RESTORE onto CAS is now
  wrapped in a single `disk->createTransaction()` (originally BAK-1's spelled-out fix; this is landed
  and correct for the whole-part-transaction requirement).
- Anchor: no Ordinary-DB guard in the CAS tree; `Grep 'Ordinary' src/Disks/.../ContentAddressed/**`
  finds only unrelated matches. The BAK-1 constraint that made `RESTORE` viable only for Atomic DBs
  (UUID-based table identity → stable CAS namespace) still exists as an unenforced precondition.
- Trigger: `RESTORE TABLE` into a database with `Ordinary` engine that targets a CAS storage policy.
- Notes: **partial improvement** — the whole-part `restore_tx` shape from the original audit landed
  (line 7510-7550). The Atomic-DB precondition is still not fail-closed at RESTORE time.

**MIG-8 (Info — onto-CAS dedup collapses duplicates on landing — a real migration upside)** — 🔴 still-present (as upside)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp:185-214`
  (HEAD-before-PUT dedup) and `CasPool.cpp:242-266` (dedup cache).
- Notes: unchanged — the dedup-on-landing property is realized as expected for INSERT SELECT and MOVE.

## Findings fixed / no longer reproducible

- **RPL-4 sub-item of MIG-5** — ✅ fixed. `FETCH PARTITION ... TO detached` on CAS now takes the
  relink path (`to_detached` threaded through `relinkPartToDisk`); anchor:
  `src/Storages/MergeTree/DataPartsExchange.cpp:700-704` (comment) and function signature at line 1389-1394
  (`bool to_detached` parameter).
- **BAK-1 whole-part transaction wrap** — ✅ fixed. Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:7508-7550`
  (whole-part `restore_tx` for CA disks; per-file autocommit rejection avoided).

None of the eight MIG-# findings are fully retired. RPL-4 (detached-fetch relink) and BAK-1
(whole-part restore) are the two upstream fixes visible in this scope; they were carried into MIG-5/MIG-7
as partial mitigations rather than a full retirement of the parent finding.

## New findings (not in original audit)

- **NEW-MIG-1 (Med — CAS-041 explicit sub-case: CAS → CAS same-pool MOVE does NOT relink; it byte-copies through streaming reads+writes).**
  - Anchor: `src/Storages/MergeTree/MergeTreePartsMover.cpp:223-282` (no `getPoolUUID` / pool-identity
    branch); `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:735-758` (CA-aware `clonePart` runs
    `copyDirectoryContentIntoTransaction` — a streamed read from src + streamed write to dst, not a
    manifest-level relink).
  - Trigger: `ALTER TABLE ... MOVE PARTITION ... TO DISK d2` where both `d1` and `d2` are CAS disks
    that share the same pool (same `pool_uuid`).
  - Why new: the wire-protocol fetch path (`DataPartsExchange.cpp`) DOES gate on `receiver_pool_uuid ==
    sender.getPoolUUID()` and relink instead of byte-fetching. The equivalent optimization is
    **missing** on the local cross-disk MOVE path. Cost impact: same-pool CAS→CAS MOVE re-uploads
    every blob body, then dedups on landing via HEAD-first (`CasPartWriteTxn.cpp:186-214`). The dedup
    HEAD hit avoids the body PUT, but the source disk is still fully read and the request cost is
    per-blob HEAD × N blobs, plus manifest re-encode/publish. A same-pool relink (publish new ref
    pointing at existing manifest+blobs) would be O(1) manifest-copy. This is a direct instance of
    CAS-041 in the local MOVE path.
  - Severity: Med (cost/latency cliff, not a correctness issue; dedup on landing saves storage but
    not read/HEAD I/O).

- **NEW-MIG-2 (Med — CAS-210 confirmed: HEAD-first "dedup on landing" trusts backend object identity by NAME only; no body re-hash verify).**
  - Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp:189-212`.
    On a HEAD hit, the writer calls `observeAndAdmit(ObjectKind::Blob, logical_ref, key, hr)` and
    admits the existing object as its own without a body GET or hash re-verify.
  - Evidence quote (line 190-201):
    > `const HeadResult hr = store->backend().head(key);`
    > `if (hr.exists) { ... const BlobDepRecord dep = observeAndAdmit(...); return ... HeadHit; }`
  - Trigger: any migration/write where the target blob key already exists (dedup case) — the primary
    upside of onto-CAS migration.
  - Threat model: the writer computed `logical_ref` from its own bytes (`write-mint site` — see
    `CasPartWriteTxn.cpp:165-168` comment: "the caller already produced the full `BlobRef` pair (algo
    + digest)"). If the existing S3 object under `key` was silently mutated (LIFE-1/LIFE-2/LIFE-5-like
    scenario) or was written by a buggy earlier build under the same key but different bytes, the new
    writer will **adopt the corrupt object without ever reading it**. INV-NO-LOSS is respected (a ref
    exists), but the ref points at bytes the writer never validated.
  - Note the header of `uploadBlobDetached` (line 172-176) itself says:
    > "The source is RE-READABLE ... it can be invoked MULTIPLE times ... so we never materialize the
    > whole blob into memory here. The byte count is verified against `source.size` at each streaming
    > write site (via the sink buffer's `count()`), not by a full pre-materialization"
    The byte COUNT is verified; the byte CONTENT is not — neither on the write side (streamed
    without in-flight hash) nor on the HEAD-hit adoption side.
  - Severity: Med — the dedup HEAD-hit trust is load-bearing for INV-1 (the "content-addressed" claim),
    but the trust is only as strong as the assumption that no other writer/lifecycle rule ever put wrong
    bytes under a CAS key. AD-2 (deletion-erasure), LIFE-1/LIFE-2/LIFE-5 (bucket-feature) and any
    format-version-bump-with-key-collision would all silently propagate through this path.

- **NEW-MIG-3 (Med — provenance envelope field is present but NOT driven by the operation kind; every fresh CAS write hardcodes `ProvenanceOp::Insert`).**
  - Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:148-155`:
    ```cpp
    st.build = metadata_storage.store()->beginPartWrite(
        Cas::PartWriteInfo{.intended_ref = ...,
                       .intended_namespace = r.ns, .op = Cas::ProvenanceOp::Insert});
    ```
    Every part-write transaction is opened with `op = Insert`, regardless of whether the caller is
    `INSERT SELECT` (migration), a merge output, a mutation output, MOVE-landing, or RESTORE-landing.
  - Anchor: `ProvenanceOp` enum values (`CasBlobEnvelopeFormat.h:43`) include `Merge`, `Mutation`,
    `Attach`, `Repack`, `Other` — but only `Insert`, `Other`, and `Attach` are ever emitted from the
    production CAS code:
    - `Attach` — `ContentAddressedMetadataStorage.cpp:2205` (attach path).
    - `Other` — `ContentAddressedTransaction.cpp:381, 741` (repoint/relink cases) and
      `Parts/PartFolderAccess.cpp:531` (`publishEntries` in cross-ref republish).
    - `Insert` — the only fresh-write value (line 154).
  - Trigger: any migration or merge/mutation write; the `op` blob-envelope field is factually wrong
    for merges, mutations, MOVE-landings, and RESTORE-landings (all recorded as `Insert`).
  - Impact: the provenance field advertised in `CasBlobEnvelopeFormat.cpp:117-121` (`ts`, `by`, `op`,
    `ch`) is only trustworthy for `Attach` and `Other`; the `Insert` label is the default and gives no
    real signal about migration origin. Tools like `CasInspect` (which decode the field —
    `CasInspect.cpp:394-399`) present operator-visible data that is not fidelity-checked. Static
    audits that rely on `op` to distinguish "migrated from outside CAS" vs "originally created inside
    CAS" cannot use this field.
  - Severity: Med — not a correctness bug (bytes are still content-addressed), but a
    diagnostic/attestation gap directly relevant to the migration audit (was the point of adding the
    enum in the first place).

- **NEW-MIG-4 (Low — off-CAS MOVE reads never re-verify blob against manifest/BLAKE hash — INT-1 exposure at migration boundary is symmetric with NEW-MIG-2).**
  - Anchor: same as MIG-6 anchor (`DataPartStorageOnDiskBase.cpp:707-710` streamed copy loop), plus
    the CAS backend's plain ranged GET path (`CasObjectStorageBackend.cpp` — no
    verify-after-read hook).
  - Note: this is a **strengthening** of MIG-6 in the original audit. The new bit is that the CAS
    write-side finding NEW-MIG-2 makes the read-side blind-copy strictly worse for chains: corruption
    admitted at write time (NEW-MIG-2) propagates unchecked at off-CAS migration read time
    (NEW-MIG-4).
  - Severity: Low (as MIG-6). MergeTree-level `checksums.txt` and `CHECK TABLE` still catch it, but
    only if the operator opts in.

## By-design / N/A / info

- ⚪ info — `movePartitionToShard` still throws `NOT_IMPLEMENTED` for MergeTree, so cross-shard MOVE is
  N/A here (`MergeTreeData.cpp:7043-7046`).
- 📐 by-design — CAS being a `metadata_type` (not an on-disk overlay) precludes in-place conversion
  (MIG-1). Any fast-path would need a new namespace-import primitive.
- ⚪ info — the CA-aware `clonePart` transaction wrap (`DataPartStorageOnDiskBase.cpp:735-758`) is a
  **real fix** for the per-file-autocommit hazard called out in the original L1/L2 comments; it does
  not fix the cross-disk-verify or same-pool-relink gaps but it makes the cross-disk MOVE at least
  atomic at the destination.

## Verdict summary table

| CAS-id (MIG-#) | Old severity | Status | Evidence anchor |
|---|---|---|---|
| MIG-1 | Med | 🔴 still-present | no in-place converter in CAS tree; `MergeTreeData.cpp:6718-6753` supported list is data-movement only |
| MIG-2 | Med | 🔴 still-present | `MergeTreeData.cpp:6740-6743` comment unchanged; `MergeTreePartsMover.cpp` has no same-pool relink |
| MIG-3 | Med | 🔴 still-present | `Gc/CasGc.cpp` reclaim only via GC round; no throttle-coupled MOVE-to-GC pacing |
| MIG-4 | Med | 🔴 still-present | `MergeTreeData.cpp:6718-6753` per-disk allowlist applied to whole table |
| MIG-5 | Med | 🔴 still-present (partial mitigation) | `DataPartsExchange.cpp:693-725` per-part relink only; `to_detached` NOW relinks (RPL-4 fixed) |
| MIG-6 | Low | 🔴 still-present | `CasObjectStorageBackend.cpp` no BLAKE re-verify on read; `DataPartStorageOnDiskBase.cpp:707-710` plain streamed copy |
| MIG-7 | Low | 🔴 still-present (partial mitigation) | `MergeTreeData.cpp:7508-7550` restore_tx wrap landed; no Atomic-DB precondition check |
| MIG-8 | Info | 🔴 still-present (as upside) | `CasPartWriteTxn.cpp:185-214` HEAD-first dedup |
| NEW-MIG-1 | — | 🔴 new | CAS-041: CAS→CAS same-pool MOVE byte-copies; `MergeTreePartsMover.cpp:223-282` |
| NEW-MIG-2 | — | 🔴 new | CAS-210: HEAD-hit adopts existing object without body re-hash; `CasPartWriteTxn.cpp:189-212` |
| NEW-MIG-3 | — | 🔴 new | Provenance op hardcoded to `Insert` for every fresh write; `ContentAddressedTransaction.cpp:148-155` |
| NEW-MIG-4 | — | 🔴 new | Off-CAS MOVE read has no BLAKE re-verify at migration boundary; `DataPartStorageOnDiskBase.cpp:707-710` |

**Bottom-line delta vs original audit.** Two concrete mechanical fixes landed:
(1) `FETCH ... TO detached` now relinks (RPL-4 sub-item of MIG-5), (2) BACKUP/RESTORE onto CAS uses a
whole-part transaction (BAK-1 wrap). None of the eight MIG-# findings are fully retired, and four
**new** findings tighten the picture: CAS→CAS same-pool MOVE still byte-copies (CAS-041 confirmed in
its most concrete local form), dedup-on-landing trusts backend by name without body-hash re-verify
(CAS-210 confirmed at the exact HEAD-hit branch), the provenance envelope is not driven by the actual
op kind (every write is `Insert`), and off-CAS MOVE reads never re-verify hashes at the migration
boundary.
