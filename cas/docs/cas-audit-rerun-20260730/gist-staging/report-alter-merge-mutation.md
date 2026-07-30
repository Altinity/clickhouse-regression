# alter-merge-mutation — re-run 2026-07-30

Static re-verification of the ALTER / merge / mutation / FINAL / replaceFile CAS audit against current PR HEAD (`/Volumes/workspace/ClickHouse`, branch `cas-audit-20260730`). Only CAS code (`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/**`) was inspected.

Original audit scoped: enumeration of every MergeTree ALTER + CAS-specific merge/mutation bug matrix (M1–M8) — no CAS-labelled findings of its own; the applicable risks were routed to CAS-020 (M1 n/a), CAS-021 (M4), CAS-001 (M5) and CAS-002 (M6). The five CAS-ids brought into re-scope by the user for this batch — **CAS-007, CAS-097, CAS-104, CAS-111, CAS-117** — originate from adjacent audits (G1, BC3-2/3, DEDUP-2, C-U4/B-6/TXN-3-codeonly, MVCC-3) but land on the ALTER/merge/mutation surface (delete-bitmap replaceFile churn, one-shot mutable-file update rollback, non-replicated dedup log durability, single-file `unlinkFile` fail-open, and FINAL/parallel-replica/patch-apply test-coverage).

## Scope in current code

- Files/dirs walked:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.h` / `.cpp`
    - `writeFile`, `tryCreateWriteBuffer`, `moveFile`, `moveDirectory`, `replaceFile`, `unlinkFile`, `createHardLink`, `removeDirectory`, `commit`, `publishStaging`, `partFileMustStayBlob`.
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.{h,cpp}`
    - `isContentAddressed`, `Route`, `liveNamespace`, `partAccess`, verbatim namespace-file dispatch.
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartPathParser.{h,cpp}`
    - part vs table-level classifier, `kDeduplicationLogsDirName`.
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasRefLedger.{h,cpp}` — `updateRefPublishedAt`, `dropRefIfMatches`, `repointRef` (cross-checked).
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPool.{h,cpp}` — `updateRefPublishedAt` façade.
- Cross-referenced: `Pool/CasPartWriteTxn.{h,cpp}` (evidence dep on hardlink), `Formats/CasLayout.h` (`deduplication_logs/` verbatim carve-out).

## Key architectural shift since the original audit

The original audit's PART 2 rested on a load-bearing premise: three per-part files (`uuid.txt`, `metadata_version.txt`, `txn_version.txt`) live in `RefPayload.mutable_files`, updated via a `updateRefPayload` one-shot that does not republish the manifest. **This premise is no longer true.** The mutable-per-part carve-out is DELETED:

```843:851:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    /// The former
    /// mutable-per-part-file branch (uuid.txt/metadata_version.txt/txn_version.txt staging directly
    /// into a separate mutable payload) is DELETED here — these three names fall through to the
    /// ordinary content path below like any other tree file. There is no filename left to special-case:
    /// `kMutablePerPartFiles`/`isMutablePerPartFile` predicate itself is gone too — there is no
    /// filename left to special-case. During part build these files land in the initial manifest with
    /// every other staged file; a standalone write on an already-committed part repoints.
```

`partFileMustStayBlob` retains ONLY the true-blob shortlist (`primary.idx`, `.bin`, `.mrk*`, `.cmrk*`); every other per-part file — including `metadata_version.txt`, `checksums.txt`, `columns.txt`, `count.txt`, `default_compression_codec.txt`, `serialization.json`, `ttl.txt`, `minmax_*.idx`, `partition.dat`, secondary-index `.idx*`, projection `.proj/*`, and the former mutable trio — travels through the ordinary inline/pending-blob content path. A standalone write on a COMMITTED ref goes through `publishStaging`'s **repoint** branch (`partAccess()->repointRef`), which reads the current view under `ForceFresh`, carries every unchanged committed entry forward, applies staged additions + `content_removed` marks, and publishes a fresh manifest via one `repointRef` call:

```362:381:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
            std::vector<Cas::ManifestEntry> merged;
            for (const auto & e : view->manifest()->entries)
                if (!st.content_removed.contains(e.path)
                    && std::none_of(st.entries.begin(), st.entries.end(),
                                     [&](const Cas::ManifestEntry & s) { return s.path == e.path; }))
                    merged.push_back(e);
            for (auto & s : st.entries)
                merged.push_back(std::move(s));
            ...
            const Cas::CommitOutcome oc = metadata_storage.partAccess()->repointRef({ns, ref}, std::move(merged), Cas::ProvenanceOp::Other);
```

The only surviving one-shot on a committed ref is `updateRefPublishedAt`, a typed mutator over the `RefPayload.published_at_ms` field (used by publish-timestamp refresh, not by any ALTER/merge/mutation write path):

```148:150:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasRefLedger.h
    void updateRefPublishedAt(const RootNamespace & ns, const String & ref_name,
```

Consequence: **every metadata-only ALTER that lands a per-part file write now performs a full manifest republish (repoint) per part.** For `ADD/DROP COLUMN`, `COMMENT`, TTL, ORDER BY, index/projection/statistics declarations, `MODIFY SETTING`, and any non-mutating ALTER that ends by bumping `metadata_version.txt` on every existing part, this multiplies request cost from one small mutable-field CAS-loop write per part → one full CABL manifest re-encode + `repointRef` per part. Cost is O(entries) per part in bytes of manifest encoding, and one `WriteRow(REPOINT)` per part in the ref ledger. On a wide part with thousands of columns this is a substantial per-part republish. Unchanged blobs are still zero-copy carried forward (no data upload), so the S3-object cost stays proportional to the manifest object only.

Merges, mutations, and partition ops are structurally unchanged from the original audit (new part name ⇒ new ref ⇒ initial-publish path, not repoint). `createHardLink` still records the tokenless W-EVIDENCE dep and stages the entry under the destination file name — the mutation copy-by-reference semantic is preserved:

```1173:1177:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    buildFor(*dst, dst_st).adoptEvidence(*src_entry);
    entry = *src_entry;
    entry.path = dst->file;
    std::erase_if(dst_st.entries, [&](const Cas::ManifestEntry & e) { return e.path == entry.path; });
    dst_st.entries.push_back(std::move(entry));
```

## Findings still present

### CAS-007 (Feature-gap / Perf) — UniqueKey / upsert delete-bitmap + SSTIndex hot-rewrite
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:65-73` (`partFileMustStayBlob`); `ContentAddressedTransaction.cpp:313-393` (`publishStaging` repoint branch).
- Trigger: UniqueKey / upsert MergeTree issues per-row-batch `replaceFile(delete_bitmap.tmp → delete_bitmap)` (and analogous SSTIndex file swaps) against a COMMITTED part. `replaceFile` drops the staged destination and delegates to `moveFile` (verbatim/staged-content path); on the committed-ref repoint branch this triggers a full manifest republish per swap. The mutable-per-part carve-out that would have absorbed such swaps into a one-shot mutator payload is deleted; there is no filename allowlist to opt these files back into a mutable slot.
- Evidence quote:

```1491:1507:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
void ContentAddressedTransaction::replaceFile(const std::string & path_from, const std::string & path_to)
{
    /// Write gate (rev.7 §1): refuse before dropping staged destination state on a Vanished/uncertain disk.
    metadata_storage.checkOpAdmitted(CasOpClass::Write);
    /// replaceFile = moveFile that overwrites the destination. Drop any staged destination state
    /// first, then delegate (the verbatim branch's putNamespaceFile already overwrites).
    ...
    moveFile(path_from, path_to);
}
```

- Notes: **Verdict unchanged — 🔴 still-present.** Correctness is not affected on standard MergeTree (no upsert engine in-tree exercises this), but any Altinity/upstream upsert engine layered on a CAS disk pays a per-swap whole-part manifest republish plus a `WriteRow(REPOINT)` in the ref ledger. Test coverage still absent. Ties CAS-111 below (both would be exercised by a surgical single-file overwrite path on a committed part).

### CAS-097 (Correctness) — one-shot mutable-file update rollback window
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:458-513` (`commit()`); `:313-393` (`publishStaging` repoint sub-branch).
- Trigger: a standalone write on a committed part (formerly `updateRefPayload(mutable_files)`) now goes through `repointRef` with a real `Cas::CommitOutcome` that IS wired into the `commit()` per-part `part_outcomes` slot and IS best-effort rolled back with `dropRefIfMatches` on any subsequent-part throw — BUT ONLY for slots whose `oc->created == true`. A repoint of an existing ref has `created=false` and is DELIBERATELY not rolled back:

```468:472:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    /// Fail-closed (CLAUDE.md): only refs that were ABSENT before we published them are rolled back. A
    /// ref that already existed is pre-existing data this commit must never destroy on its error path.
    /// Publishing over a live ref does not occur in the MergeTree write path (unique part names), but
    /// the rollback must not assume it. updateRefPublishedAt mutations (autocommit one-shots on a
    /// COMMITTED part) are individually durable by design and are deliberately NOT rolled back.
```

- Evidence quote:

```509:512:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
        for (const auto & oc : part_outcomes)
            if (oc && oc->created)
                metadata_storage.partAccess()->dropRefIfMatches({oc->ns, oc->ref}, oc->manifest_ref);
        throw;
```

- Notes: **🔴 still-present, semantics narrowed.** A metadata-only ALTER that touches parts A, B, C where A is a repoint (write on committed) will leave A's new manifest **durably visible** if B/C throw and the whole `commit()` reports failure. This is intentional (per-part repoint is individually durable, MergeTree tolerates a per-part metadata-version skew across parts because alter-conversions are applied lazily on read), but the transaction's rollback contract is asymmetric: initial-publish creates roll back; repoints do not. The remaining `updateRefPublishedAt` one-shot inherits the same posture: individually durable, not compensated. Ties BC3-2/3 (bc3-exception-safety re-run).

### CAS-104 (Correctness) — non-replicated dedup-log durability rides mutable-file commit
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartPathParser.h:72-75` (`kDeduplicationLogsDirName`); `ContentAddressedTransaction.cpp:800-824` (verbatim `putNamespaceFile` write buffer, read-modify-rewrite).
- Trigger: non-replicated MergeTree's per-shard dedup log (`deduplication_logs/deduplication_log_N.txt`) is routed as a table-level VERBATIM namespace file (parsed by `parseTableFilePath`, not `parsePartFilePath`). Each append: read existing bytes → concat → `putNamespaceFile` (CAS-loop conditional put keyed on the object token). A crash between the ordinary MergeTree commit of a fresh insert part and the dedup-log append leaves the part durable with no dedup entry ⇒ a retry of the same insert produces a duplicate part; CAS content-dedup collapses the identical blobs (no storage bloat) but the part count doubles until merge. The comment explicitly acknowledges the single-appender invariant this rests on:

```800:809:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    /// Non-part files are VERBATIM namespace files, durable on finalize (no commit involvement -
    /// the disk layer's autocommit contract for them rides exactly this). Append is serviced by
    /// read-modify-rewrite: the existing bytes are carried forward (the MVCC mutation-entry CSN
    /// append depends on this). The `carried` prefix below is read ONCE here, at buffer-open time, and
    /// frozen into the write callback; `casPutObject`'s CAS loop (invoked from the callback via
    /// `putNamespaceFile`/`putMountpointObject`) only re-reads the TOKEN on conflict, not this base
    /// content — see the single-appender invariant documented at `CasPlainObjects::casPutObject`. Safe
    /// only because the sole production appender (the mutation-entry CSN write) never has a second
    /// concurrent appender on the same key.
```

- Notes: **🔴 still-present, bounded.** Failure mode is unchanged from the original CAS-104: bounded duplicate part, absorbed by content-dedup at the blob layer, resolved by the next merge. No coordination between the ordinary part commit and the dedup-log RMW ⇒ a two-write window remains. Also latent second-appender hazard if a future codepath appends to `deduplication_logs/*` concurrently with the mutation-entry CSN writer: the frozen `carried` prefix would silently overwrite one appender's contribution.

### CAS-111 (Correctness) — single-file `unlinkFile` fail-open — **FIXED**
- Anchor for the fix: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1509-1601` (`unlinkFile`); resolution in `publishStaging` at `:338-392`.
- Behavior in current code: a `unlinkFile` on a COMMITTED content file no longer silently no-ops. Two cases:
  1. Same-transaction storm (fast-removal unlinks every file then `removeDirectory`): the whole part ref-drop supersedes the marks (marks cleared by `removeDirectory`), costing exactly one ref-drop.
  2. Lone surgical single-file unlink on a committed part (ATTACH's `removeVersionMetadata`, or a future backfill/repair delete): the transaction stages `st.content_removed.insert(r->file)`; `publishStaging`'s repoint branch merges the current view minus removed paths, republishes via `repointRef`. Non-existent target throws `FILE_DOESNT_EXIST` unless `if_exists=true`.

- Evidence quote:

```1520:1531:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    /// This is a load-bearing invariant; do not "fix" it with a blanket fail-closed assert:
    /// On a content-addressed disk a committed part is ONE atomic ref (its manifest tree); the removal
    ...
    /// A lone
    /// surgical unlink NOT followed by a ref-drop in the same transaction (ATTACH's
    /// `removeVersionMetadata`, a future backfill/repair delete) resolves to one repoint-remove —
    /// this closes the file's former fail-open (a committed content file could never actually be
    /// deleted on its own; this behavior now closes that earlier fail-open.
```

- Notes: **✅ fixed.** The `content_removed` mark + repoint plumbing directly closes the C-U4 / TXN-3 / B-6 gap the original CAS-111 flagged; the "future path that surgically deletes one committed file" the finding warned about would now actually take effect (and interact with CAS-007's `replaceFile` — see NEW-AMM-1 below).

### CAS-117 (Test-gap) — FINAL / parallel-replica reads / patch-apply-on-read untested under concurrent merge
- Anchor: whole subtree — no CAS-side handling for FINAL, parallel-replica reads, patch parts, `_row_exists`, or lightweight-update patch-apply is present. Grep on `FINAL|parallel_replica|patch_apply|patch_part|_row_exists|lightweight.?update` in `ContentAddressed/**` returns only unrelated matches (finalizeImpl, EVP_DigestFinal_ex, "Final" as an adjective in benchmark commentary).
- Trigger: unchanged — FINAL and parallel-replica reads issue many concurrent ranged GETs against pinned parts; lightweight-update patch-apply-on-read reads a patch part concurrently with a merge that produces the merged base part. Behavior is expected-correct-by-composition (blob GETs by content hash are idempotent + immutable; ref pin blocks GC-drop of the base part while a query holds a `PartFolderAccess` view), but there is no dedicated concurrency test in `Tools/` or under a CAS-labelled tests directory.
- Evidence quote (absence): no CAS references to FINAL/patch-apply.
- Notes: **🔴 still-present** as a test-coverage gap. Static reasoning unchanged from the original audit.

## Findings fixed / no longer reproducible

- **CAS-111** — see above; single-file surgical `unlinkFile` on a committed part is no longer fail-open. Fix anchor: `ContentAddressedTransaction.cpp:1520-1568` + repoint merge at `:362-381`.
- **M3 (mutable-file update is a one-shot, no manifest republish)** from the original audit is **no longer true** — but this is a design shift, not a bug fix; see "Key architectural shift" above and NEW-AMM-2 below.

## New findings (not in original audit)

### NEW-AMM-1 — Metadata-only ALTER now performs a full manifest republish per part (perf/scale)
- Severity: **Medium** (perf/scale; correctness intact).
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:843-851` (mutable-file carve-out deleted); `:338-392` (`publishStaging` repoint sub-branch).
- Trigger: any ALTER whose per-part effect is `metadata_version.txt` bump (ADD/DROP COLUMN, COMMENT, MODIFY SETTING, MODIFY TTL, ORDER BY, index/projection/statistics declaration, MODIFY SQL SECURITY, etc.). Old design absorbed the write into an O(small) `updateRefPayload` mutator over a mutable byte-blob field; new design performs a full manifest re-encode + `repointRef` per part in the table. Cost is **N-parts × O(manifest-size)** — for a wide table with thousands of columns and tens of thousands of parts, this is a materially heavier ALTER than the original audit implied ("clean fit for CAS").
- Notes: propose to route to a perf/observability item — add manifest-size and repoint counter to a `system.cas_*` table, and consider re-introducing a typed mutable slot for `metadata_version.txt` specifically (the only known write-hot mutable per-part file) if regression tests observe unacceptable ALTER latency.

### NEW-AMM-2 — Committed-repoint rollback asymmetry vs initial-publish rollback (correctness sharpening of CAS-097)
- Severity: **Low** (documented, but the exposure is broader than the original CAS-097 framing).
- Anchor: `ContentAddressedTransaction.cpp:468-472, :509-512`.
- Trigger: a multi-part metadata-only ALTER stages parts A (committed → repoint), B (committed → repoint), C (fresh → initial-publish). Publish loop succeeds for A, then throws in B (backend outage / conditional-copy conflict). Rollback drops C only if it published (created=true); A's repoint stays durable. On retry, A's `metadata_version.txt` reflects the intended new value; B does not. MergeTree tolerates this via lazy alter-conversion on read, but the transaction's success/failure signal is no longer a proxy for "either all parts observe the new metadata version or none do".
- Notes: this generalizes CAS-097 from the narrow "one-shot rollback window" to "repoint rollback intentionally absent". Recommend a documented user-visible note (design doc) and, if MergeTree ever grows a code path that relies on per-part metadata-version atomicity across the whole table (currently it does not), lift this into a High.

### NEW-AMM-3 — Verbatim `deduplication_logs/*` RMW second-appender hazard (correctness, latent)
- Severity: **Low** (latent — no current second appender).
- Anchor: `ContentAddressedTransaction.cpp:800-824` (verbatim namespace-file write buffer; `carried` prefix frozen at buffer-open); `Parts/PartPathParser.h:72-75` (`deduplication_logs/` reserved as a table-level subdirectory).
- Trigger: comment explicitly states "Safe only because the sole production appender ... never has a second concurrent appender on the same key." A future feature that appends to `deduplication_logs/*` from a background flusher concurrent with the mutation-entry CSN writer would deterministically lose one appender's bytes: both open a write buffer, both cache the same `carried` prefix, both `putNamespaceFile` with mutually-invalidating token conflict retries — but the retry re-reads only the token, not the base content. Not a fail-closed guard.
- Notes: land a fail-loud assertion (or a genuine RMW-under-lease primitive) before adding any second appender; also relevant to any future write concurrency on other verbatim table-level files (e.g. `format_version.txt`, MVCC mutation-entry CSN).

## By-design / N/A / info

- **M1 (W1 promote-overwrite leak on merge/mutation)** — new part names ⇒ initial publish, no ref overwrite. Original verdict "not reachable here" holds. ⚪ info.
- **M2 (copy-forward evidence dep vs GC)** — `createHardLink` still records `adoptEvidence` (tokenless W-EVIDENCE) on the source blob; `copyForwardFromCondemned` still exists in the write protocol. Verdict unchanged. ⚪ info.
- **M4 (partial-commit atomicity)** — inherits CAS-021 (BC3-1). See `bc3-exception-safety.md` re-run. ⚪ info (inherited).
- **M5 (reader vs merge/mutate cleanup)** — inherits CAS-001 (R1/X1). See `read-protocol.md` re-run. ⚪ info (inherited).
- **M6 (fencing on merge/mutate writes)** — inherits CAS-002 (J1 zombie-writer window). ⚪ info (inherited).
- **M7 (unchanged-part clone)** — `createHardLink` on every entry produces a new manifest with the same blob refs; `PartWriteTxn` deduplicates via HEAD-first + dedup cache. Content-identical part → same `logical_hash` chain → effectively free (one manifest object + one ref row). Verdict unchanged. ⚪ info.
- **M8 (RENAME COLUMN)** — the mutate-with-rename walk still translates to `createHardLink(old_name, new_name)` per file (mutation task on MergeTree side); the CAS entry.path is rewritten under the destination file name at `ContentAddressedTransaction.cpp:1154, :1175`. Verdict unchanged. ⚪ info.
- **Partition ops allow-list** — no CAS-side gate on ATTACH/REPLACE/DETACH/DROP/MOVE(same-disk)/FETCH/FREEZE. `moveDirectory` classifies part vs table-level shapes (`ContentAddressedTransaction.cpp:1200-1375`) and throws on unsupported shapes. Verdict unchanged (allow-listed / fail-closed). ⚪ info.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-007 | Feature-gap / Perf | 🔴 still-present | `ContentAddressedTransaction.cpp:65-73, :1491-1507` |
| CAS-097 | Correctness (Low) | 🔴 still-present (narrowed to repoint outcome slot; see NEW-AMM-2) | `ContentAddressedTransaction.cpp:468-472, :509-512` |
| CAS-104 | Correctness (Low) | 🔴 still-present (bounded; single-appender contract only) | `ContentAddressedTransaction.cpp:800-824`; `Parts/PartPathParser.h:72-75` |
| CAS-111 | Correctness (Low) | ✅ fixed | `ContentAddressedTransaction.cpp:1520-1568`, repoint at `:362-381` |
| CAS-117 | Test-gap | 🔴 still-present | no FINAL/patch-apply references in `ContentAddressed/**` |
| NEW-AMM-1 | — | 🛠 new (Perf, Med) | `ContentAddressedTransaction.cpp:843-851, :338-392` |
| NEW-AMM-2 | — | 🛠 new (Correctness, Low) | `ContentAddressedTransaction.cpp:468-472, :509-512` |
| NEW-AMM-3 | — | 🛠 new (Correctness, Low, latent) | `ContentAddressedTransaction.cpp:800-824` |
| M1, M2, M7, M8 | ✅ | ⚪ info (unchanged) | see per-row |
| M3 (original) | ✅ | ⚪ info — premise (mutable-file one-shot) no longer holds; see NEW-AMM-1 | `ContentAddressedTransaction.cpp:843-851` |
| M4/M5/M6 | ⚠ (inherited) | ⚪ info (inherited from CAS-021/CAS-001/CAS-002) | bc3-exception-safety.md / read-protocol.md re-runs |
