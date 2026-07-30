# bc6-mtime-semantics — re-run 2026-07-30

Static re-verification of mtime semantics on CAS. Focus: CAS-048 (getLastModified inconsistency
publish/epoch/throw), CAS-099 (setLastModified no-op + clearOldTemporaryDirectories inert),
CAS-208 (TTL data-driven — verify unaffected).

## Scope in current code

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp`
  — `getLastModified` (1565–1595), `iterateDirectory` (1714–1725), `listDirectory` (1597–...),
  `isDirectoryEmpty` (1727–1746).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp`
  — `setLastModified` (1180–1186), `chmod` (1188–1191), `setReadOnly` (1193–1198).
- `src/.../ContentAddressed/Pool/CasPartWriteTxn.cpp` — `promote` (1050…) and
  `set_published_at.published_at_ms = nowMs()` (1240).
- `src/.../Pool/CasRefLedger.cpp` — `updateRefPublishedAt` (2842–2874).
- `src/.../Pool/CasRefProtocol.h` — `RefPayload.published_at_ms` (102, 112).
- `src/.../Parts/PartFolderAccess.cpp` — `republishRef` (506–534) and `repointRef` (536–592)
  (relink/rename path).

No mtime-consumer code lives inside CAS itself (TTL, `isOldPartDirectory`,
`clearOldTemporaryDirectories`, `ReplicatedMergeTreePartCheckThread`, `MergeTreePartsMover`
all live in `src/Storages/MergeTree/**`); this report reasons about CAS-side behavior only, at
the boundary exposed to those consumers.

## Findings still present

### CAS-048 — `getLastModified` inconsistent: publish-time / epoch(0) / throws

- Anchor: `src/.../ContentAddressed/ContentAddressedMetadataStorage.cpp:1565-1595`
  (`getLastModified`).
- Trigger: any caller that expects a stable "data age" mtime; observed effects are
  cross-replica divergence and post-relink reset.
- Evidence quote (verbatim):

```1574:1594:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp
    auto resolve_stamp = [&](const Route & r) -> Poco::Timestamp
    {
        auto resolved = partAccess()->resolve(r.refKey(), Cas::Freshness::CachedForLoad);
        if (!resolved)
            throw Exception(ErrorCodes::FILE_DOESNT_EXIST, "ContentAddressed: no ref for {}", path);
        if (resolved->published_at_ms == 0)
            return Poco::Timestamp(0);
        return Poco::Timestamp::fromEpochTime(static_cast<time_t>(resolved->published_at_ms / 1000));
    };

    if (auto p = Cas::parsePartFilePath(path))
    {
        auto r = route(*p);
        if (r && !r->ref.empty())
            return resolve_stamp(*r);
    }
    if (existsFile(path))
        return Poco::Timestamp(0);
    throw Exception(ErrorCodes::FILE_DOESNT_EXIST, "ContentAddressed: no object for {}", path);
```

- Notes: three-way semantics unchanged from the original audit — part paths report
  publish-wall-clock, verbatim files report epoch(0), unresolved paths throw
  `FILE_DOESNT_EXIST`. Cross-replica divergence is inherent: `published_at_ms` is stamped
  independently by each replica's own `promote` (see below), never propagated with the ref.
- Relink resets confirmed: `CasPartWriteTxn::promote` builds a `set_published_at` op with
  `nowMs()` on every promote, including the intended-repoint path.

```1236:1244:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp
            RefOp set_published_at;
            set_published_at.kind = RefOpKind::SetPublishedAt;
            set_published_at.ref_name = final_ref_name;
            set_published_at.expected_manifest_ref = id.ref;
            set_published_at.published_at_ms = nowMs();
            ops.push_back(set_published_at);
```

And `repointRef` funnels through `publishEntries` → same `promote`+`set_published_at` path
(`PartFolderAccess.cpp:536-592`), so every relink/republish restamps.

Verdict: 🔴 still-present (Med) — code unchanged relative to original BC6-1/BC6-2.

### CAS-099 — `setLastModified` is a no-op; `clearOldTemporaryDirectories` inert on CAS

- Anchor: `src/.../ContentAddressed/ContentAddressedTransaction.cpp:1180-1186`
  (`setLastModified`).
- Trigger: MergeTree "touch to refresh age" pattern or any code that mutates mtime on a
  directory to protect it from a sweep.
- Evidence quote:

```1180:1186:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
void ContentAddressedTransaction::setLastModified(const std::string &, const Poco::Timestamp &)
{
    /// Timestamps are derived for content addressing (the publish stamp), so accept and ignore them -- but
    /// gate as a Write (previously-no-op site, rev.7 §1): never silently accept it on a Vanished/uncertain
    /// disk.
    metadata_storage.checkOpAdmitted(CasOpClass::Write);
}
```

- Notes: since original audit, this is now **gated as a Write** via `checkOpAdmitted`
  (so it throws on a Vanished/uncertain disk instead of silently no-op'ing), but the
  functional behavior on a healthy disk is unchanged — the timestamp is accepted and
  discarded. The "silently fails" concern of BC6-3 stands on the healthy-disk path.
- Second half (`clearOldTemporaryDirectories` inert on CAS): still by-construction.
  Uncommitted tmp stagings have no ref, so `iterateDirectory` (1714-1725) — which lists
  refs via `listDirectory` — never enumerates them. Committed
  `delete_tmp_`/`tmp-fetch_` refs get publish-time stamps and are governed by GC, not the
  `temporary_directories_lifetime` sweep. No behavioral change in this build.

Verdict: 🔴 still-present (Low) — semantics unchanged; the added `checkOpAdmitted` gate is a
Vanished-disk hardening, not a fix for the "touch to refresh age silently fails" concern.

## Findings fixed / no longer reproducible

None. All three concerns (BC6-1, BC6-2, BC6-3/BC6-5) persist.

## By-design / N/A / info

### CAS-208 — TTL is data-driven, not mtime-driven → unaffected by synthetic mtime

- Anchor (CAS side): no CAS code participates in TTL evaluation; MergeTree's
  `IMergeTreeDataPart::getMinMaxTime` / TTL expression evaluation over row data live in
  `src/Storages/MergeTree/**` and consume column min/max, not
  `IMetadataStorage::getLastModified`.
- Evidence (CAS side, negative): a full grep of the CAS source tree
  (`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/**`) for `TTL|ttl` finds
  matches only in unrelated identifiers (e.g. `allow_stale` decode-TTL comments), never in
  a getLastModified consumer path. Confirms CAS's synthetic publish-time mtime cannot
  reach a TTL decision.

Verdict: 📐 by-design — TTL moves/deletes verified unaffected by CAS mtime semantics.

### BC6-6 — Movers / load paths tolerate publish-time mtime (bookkeeping only)

- Anchor: outside CAS (`MergeTreePartsMover`, load paths). CAS side simply returns the
  publish stamp; no CAS-owned regression.
- Verdict: ⚪ info — unchanged since original audit.

## New findings (not in original audit)

### NEW-bc6-1 — `getLastModified` uses `Freshness::CachedForLoad`; a just-repointed part on this node can transiently return the OLD publish stamp

- Anchor: `src/.../ContentAddressedMetadataStorage.cpp:1576`
  (`partAccess()->resolve(r.refKey(), Cas::Freshness::CachedForLoad)`).
- Severity: Low (adds a same-node freshness skew to BC6-1's cross-node divergence, but
  bounded by the decode-cache TTL and self-heals on next resolve).
- Trigger: an operator/tool queries `system.parts.modification_time` (or any consumer of
  `getLastModified`) on this same node immediately after a local `repointRef`
  (relink/republish). If the local decode cache still holds the pre-repoint
  `RefPayload`, the caller sees the *old* `published_at_ms`, not the just-stamped new
  one, until the cache entry TTLs out.
- Evidence: `getLastModified` calls `resolve(..., CachedForLoad)` unconditionally; other
  correctness-sensitive sites in CAS use `Freshness::ForceFresh` (see e.g.
  `repointRef` at `PartFolderAccess.cpp:555`). No mtime-consumer contract is broken by
  this because mtime already lacks strong semantics on CAS (per BC6-1/CAS-048), but it
  *widens* the observed inconsistency window and can confuse an operator debugging
  BC6-1 divergence by making the "own-replica" answer itself unstable.
- Notes: mitigation is either a `ForceFresh` upgrade on mtime queries, or explicit doc
  that `system.parts.modification_time` on CAS is best-effort and eventually consistent
  even on the writing replica.

### NEW-bc6-2 — Verbatim-file mtime returns `Poco::Timestamp(0)` before the `existsFile` check considers directories, so a **directory** path resolves via the "part" branch or throws — mtime for a `Cas::parsePartFilePath`-rejected directory is 1970

- Anchor: `src/.../ContentAddressedMetadataStorage.cpp:1585-1594`.
- Severity: Info / documentation gap.
- Trigger: any caller that passes a non-part directory path (e.g. a metadata-only or
  `deduplication_logs/…`-shaped directory that does not have a ref and does exist as a
  file/dir in the CAS view). If it fails `parsePartFilePath` and passes `existsFile`, it
  reports 1970; if it fails both, it throws.
- Notes: not new *behavior* — the audit called BC6-2 out — but the branch ordering means
  a caller cannot distinguish "verbatim file exists, mtime 1970" from "verbatim
  directory exists, mtime 1970" without knowing the path shape a priori. Recommend an
  explicit code comment naming which shapes hit which branch, given operator confusion
  is the whole point of BC6-2.

## Verdict summary table

| CAS-id  | Old sev | Status         | Evidence anchor                                                                              |
|---------|---------|----------------|----------------------------------------------------------------------------------------------|
| CAS-048 | Med     | 🔴 still-present | `ContentAddressedMetadataStorage.cpp:1565-1595`, publish stamp restamped at `CasPartWriteTxn.cpp:1240` |
| CAS-099 | Low     | 🔴 still-present | `ContentAddressedTransaction.cpp:1180-1186` (no-op body; only Vanished-disk gate added)      |
| CAS-208 | Info    | 📐 by-design     | Negative-grep: no `TTL` consumer of `getLastModified` in CAS tree                            |

### New findings

| ID | Sev | Anchor |
|---|---|---|
| NEW-bc6-1 | Low | `ContentAddressedMetadataStorage.cpp:1576` (`Freshness::CachedForLoad` on mtime read) |
| NEW-bc6-2 | Info | `ContentAddressedMetadataStorage.cpp:1585-1594` (branch-order documentation gap) |

## Counts

- Findings re-verified from original: **3** (CAS-048, CAS-099, CAS-208).
- Still-present: **2** (CAS-048 Med, CAS-099 Low).
- Fixed: **0**.
- By-design / info: **1** (CAS-208).
- New findings: **2** (NEW-bc6-1 Low, NEW-bc6-2 Info).
