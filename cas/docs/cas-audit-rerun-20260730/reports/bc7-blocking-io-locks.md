# bc7-blocking-io-under-locks — re-run 2026-07-30

## Scope in current code

- CAS source: `/Volumes/workspace/ClickHouse` @ `cas-audit-20260730` (HEAD `834c9517f56`).
- CAS commit path: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp`.
- MergeTree integration:
  - `src/Storages/MergeTree/MergeTreeData.cpp` — `Transaction::renameParts` (:8962), `Transaction::commit` (:8991, :8997), `preparePartForCommit` (:5499), `renameTempPartAndReplaceImpl` (:5564).
  - `src/Storages/MergeTree/MergeTreeSink.cpp` — plain-MergeTree INSERT commit (:342).
  - `src/Storages/MergeTree/ReplicatedMergeTreeSink.cpp` — Replicated INSERT commit (:995, :1011).
  - `src/Storages/MergeTree/MergeTreeDataMergerMutator.cpp` — merge commit (:525, :528).
  - `src/Storages/MergeTree/MutateFromLogEntryTask.cpp` — replicated mutation commit (:265, :283).
  - `src/Storages/MergeTree/MutatePlainMergeTreeTask.cpp` — plain mutation commit (:134).
  - `src/Storages/MergeTree/MergePlainMergeTreeTask.cpp` — plain-MergeTree merge commit (:160).

## Call-chain trace (current code)

**`Transaction::commit()` under `DataPartsLock`** — `MergeTreeData.cpp:8991-9010`:

```8991:9010:src/Storages/MergeTree/MergeTreeData.cpp
MergeTreeData::DataPartsVector MergeTreeData::Transaction::commit()
{
    auto lock = data.lockParts();
    return commit(lock);
}

MergeTreeData::DataPartsVector MergeTreeData::Transaction::commit(DataPartsLock & acquired_parts_lock)
{
    ...
    for (const auto & part : precommitted_parts)
        if (part->getDataPartStorage().hasActiveTransaction())
            part->getDataPartStorage().commitTransaction();
```

**`Transaction::renameParts()` — the mitigation** — `MergeTreeData.cpp:8962-8988`. Runs BEFORE `commit()` and OUTSIDE `DataPartsLock`. Comment explicitly documents the intent:

```8976:8988:src/Storages/MergeTree/MergeTreeData.cpp
    /// also keeps the disk commit (network I/O on object storages) off the data_parts lock, which
    /// Transaction::commit holds.
    for (const auto & part_need_rename : precommitted_parts_need_rename)
    {
        ...
        part_need_rename->renameTo(part_need_rename->name, true);
    }
    precommitted_parts_need_rename.clear();

    for (const auto & part : precommitted_parts)
        if (part->getDataPartStorage().hasActiveTransaction())
            part->getDataPartStorage().commitTransaction();
```

After `renameParts()` runs, `hasActiveTransaction()` is false, so the identical loop inside `commit()` (:9008-9010) becomes a **no-op** for those parts. Publication is done off-lock.

**Whether `renameParts()` runs depends on `rename_in_transaction`** — plumbed through `preparePartForCommit` (`MergeTreeData.cpp:5499-5521`):

```5510:5520:src/Storages/MergeTree/MergeTreeData.cpp
    chassert(!(!need_rename && rename_in_transaction));

    if (need_rename && !rename_in_transaction)
        part->renameTo(part->name, true);       // INLINE, under DataPartsLock

    LOG_TEST(log, "preparePartForCommit: inserting {} into data_parts_indexes", part->getNameWithState());
    data_parts_indexes.insert(part);
    if (rename_in_transaction)
        out_transaction.addPart(part, need_rename);
    else
        out_transaction.addPart(part, /* need_rename= */ false);
```

- `rename_in_transaction=true` → rename deferred to `renameParts()` off-lock → CAS publish off-lock. ✅
- `rename_in_transaction=false` → `renameTo` runs **inline under the lock** (`preparePartForCommit` is invoked from `renameTempPartAnd*` variants which hold `DataPartsLock`). CAS `moveDirectory` (staged tmp→final) is metadata-only, but the subsequent `commitTransaction()` at `MergeTreeData.cpp:9010` (still under the lock) fires the entire CAS `publishStaging` — blob PUTs, precommit, promote, ref CAS with retries.

**Call-site inventory of `rename_in_transaction`:**

Off-lock (uses renameParts mitigation) — `true`:

- `ReplicatedMergeTreeSink.cpp:995` — replicated INSERT.
- `MergeTreeDataMergerMutator.cpp:525` — merges, common path.
- `MutateFromLogEntryTask.cpp:265` — replicated mutation.
- `StorageReplicatedMergeTree.cpp:2581, 3421, 5661, 9299, 11294` — replicated fetch/replace/attach.
- `StorageMergeTree.cpp:2294, 3007, 3017` — replace/move.

On-lock (CAS commit stays under `DataPartsLock`) — `false`:

- `MergeTreeSink.cpp:379` — **plain-MergeTree INSERT** (explicit comment at :369-378 states rename must stay under the lock to avoid a covered-part race with concurrent merge selection):

```369:380:src/Storages/MergeTree/MergeTreeSink.cpp
        /// FIXME: renames for MergeTree should be done under the same lock
        /// to avoid removing extra covered parts after merge.
        ...
        /// Hence, for now rename_in_transaction is false.
        storage.renameTempPartAndAdd(part, transaction, lock, /*rename_in_transaction=*/ false);
        transaction.commit(lock);
```

- `MutatePlainMergeTreeTask.cpp:134` — plain mutation.
- `StorageMergeTree.cpp:2631, 2851, 3201` — attach/replace/etc.
- `StorageReplicatedMergeTree.cpp:9580` — cross-table move destination.
- `MergeTreeData.cpp:5885` — internal `renameTempPartAndAdd` (all covered removed).

**CAS side** — `ContentAddressedTransaction::commit()` runs the full durable-publish loop:

```435:520:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
void ContentAddressedTransaction::commit(const TransactionCommitOptionsVariant &)
{
    ...
    try
    {
        for (size_t i = 0; i < ordered.size(); ++i)
            publishStaging(ordered[i].ns, ordered[i].ref, *ordered[i].st, part_outcomes[i]);
    }
```

`publishStaging` (`:313`) is where blob PUTs + precommit + promote + ref `casPut` (with CAS-conflict/throttle retries) happen.

**RENAME TABLE / DROP** — `ContentAddressedTransaction::moveDirectory` (:1200) and `::removeRecursive` (:1032) mutate durable refs **immediately at call time** (not staged for commit):

```1200:1210:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
void ContentAddressedTransaction::moveDirectory(const std::string & path_from, const std::string & path_to)
{
    /// Write gate (rev.7 §1): mutates durable refs immediately -- throw before touching them on a
    /// Vanished/uncertain disk.
    metadata_storage.checkOpAdmitted(CasOpClass::Write);
    /// Same call-time-durability-plus-compensation contract as `removeDirectory` above: this mutates
    /// durable refs immediately rather than staging an intent for commit; see the contract note there.
```

Table-level RENAME (`:1225-1250`) synchronously `republishRef` / `putNamespaceFile` / `dropNamespace` — synchronous S3 CAS — while DDL holds the table's structure lock.

## Findings still present

**BC7-1 (High)** — CAS durable publish runs under `DataPartsLock` for callers with `rename_in_transaction=false`.
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:8993` (`lockParts()` in `Transaction::commit`) → `:9008-9010` (`commitTransaction()` under the lock) → `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:435` (`publishStaging` loop, blob PUTs + precommit + promote + ref CAS with retries).
- Trigger: plain-MergeTree INSERT (`MergeTreeSink.cpp:379-380`), plain mutation (`MutatePlainMergeTreeTask.cpp:134`), attach/replace paths listed above. `preparePartForCommit` runs `part->renameTo` inline under the lock (`MergeTreeData.cpp:5513`), and `commitTransaction` on that part still has `hasActiveTransaction()==true` at `MergeTreeData.cpp:9008-9010` → full CAS publish under the lock.
- Evidence: `MergeTreeSink.cpp:369-380` explicitly wires `rename_in_transaction=false` and does `renameTempPartAndAdd` + `transaction.commit(lock)` inside the `lockParts()` scope, with a `FIXME` comment stating this cannot be changed without fixing the covered-part-vs-merge race.
- **Partial fix present, not universal**: the `renameParts()` mitigation (`MergeTreeData.cpp:8962-8988`, `off the data_parts lock` per its own comment) covers the `rename_in_transaction=true` callers (Replicated INSERT, merges, replicated mutations, replace/fetch/attach). The plain-MergeTree write path is still under the lock.
- Verdict: 🔴 still-present (partially fixed vs. original audit).

**BC7-2 (Med)** — Flat-combining `mutateShard` queue + shard CAS retries stack under the held lock.
- Anchor: `ContentAddressedTransaction.cpp:497` (`publishStaging` per-part loop is serial) → shard `casPut` in `partAccess()->publish(...)` / `dropRefIfMatches` (`RefLedger`/`RootShardCodec`).
- Trigger: multiple concurrent plain-MergeTree INSERTs on the same table (same shard) — each takes `DataPartsLock`, does its publish under the lock, and its publish waits behind the shard's flat-combining batch and each shard `casPut` retry.
- Evidence: `commit` at `ContentAddressedTransaction.cpp:485-497` publishes parts SERIALLY inside one commit; even within one commit fan-out is bounded to blob uploads (`fanOutBlobUploads`), not manifest/ref CAS. No change from original.
- Verdict: 🔴 still-present (only relevant to the BC7-1 on-lock callers).

**BC7-3 (Med)** — Merge/mutation commits: publish is now off-lock via `renameParts()` for the **replicated** path (`MergeTreeDataMergerMutator.cpp:525-528` uses `rename_in_transaction=true` then `out_transaction.renameParts()`), but **plain-MergeTree** merges/mutations still enter `commit()` on-lock:
  - Plain merge: `MergePlainMergeTreeTask.cpp:160` calls `transaction.commit()` — no prior `renameParts()`; `commit()` acquires the lock and calls `commitTransaction()` (S3 publish) under it.
  - Plain mutation: `MutatePlainMergeTreeTask.cpp:134-135` uses `rename_in_transaction=false` then `transaction.commit(lock)` under an explicit `lockParts()` scope.
- Anchor: `MergePlainMergeTreeTask.cpp:160`, `MutatePlainMergeTreeTask.cpp:134-135`.
- Consequence: on plain-MergeTree, the CAS publish holds `DataPartsLock` and `currently_merging_mutating_parts` remains occupied until the S3 CAS retries finish → merge-throughput drag under S3 throttling. Unchanged from original.
- Verdict: 🔴 still-present for plain-MergeTree; ✅ fixed for replicated (renameParts moved off-lock).

**BC7-4 (Med)** — DROP/DETACH/RENAME issue synchronous S3 CAS under DDL locks.
- Anchor: `ContentAddressedTransaction.cpp:1032` (`removeRecursive` — `dropNamespace`/`dropRefIfPresent` are call-time durable, not staged) and `:1200-1250` (`moveDirectory` for table→table RENAME issues synchronous `republishRef`/`putNamespaceFile`/`dropNamespace`).
- Trigger: `DROP TABLE`/`DETACH`/`RENAME TABLE` while the DDL holds the storage/structure lock.
- Evidence: comments at `ContentAddressedTransaction.cpp:1202-1206` and `:1211-1224` explicitly state these mutate durable refs immediately (RENAME is a non-atomic multi-op with no in-call compensation — TXN-2 territory).
- Verdict: 🔴 still-present. Unchanged from original.

**BC7-5 (Low)** — Startup part-loading does S3 LIST/GET under loading synchronization. Enumeration APIs (`listRefs`/`listNamespaces`/manifest GET) are still synchronous network round-trips called during attach. No code-level change to move this off the loading path.
- Verdict: 🔴 still-present (no fix attempted; low-priority).

**BC7-6 (Info)** — Reads snapshot parts under the lock briefly then release ✅. `getDataPartsVectorForInternalUsage` / `getDataPartsForInternalUsage` continue to snapshot under `DataPartsLock` and release before doing blob GETs. No regression.
- Verdict: 📐 by-design / ⚪ info.

## Findings fixed / no longer reproducible

- **BC7-3 for replicated merges** — `MergeTreeDataMergerMutator::renameMergedTemporaryPart` (`:525-528`) now uses `rename_in_transaction=true` and calls `out_transaction.renameParts()` inside itself, moving the CAS publish off `DataPartsLock`. Anchor: `MergeTreeDataMergerMutator.cpp:525-528` + `MergeTreeData.cpp:8962-8988`.
- **BC7-1 for replicated INSERT** — `ReplicatedMergeTreeSink::commitPart` (`:995`, `:1011`) uses `rename_in_transaction=true` and calls `transaction.renameParts()` before `transaction.commit()`. CAS publish happens in `renameParts()` off-lock; `commit()` under the lock is a no-op for those parts. Anchor: `ReplicatedMergeTreeSink.cpp:995, 1011, 1025`.

## New findings (not in original audit)

- **NEW-BC7-1 (Med)** — Asymmetric fix: replicated write paths use the `renameParts()` off-lock publish, but plain-MergeTree paths (`MergeTreeSink.cpp:379`, `MutatePlainMergeTreeTask.cpp:134`, `MergePlainMergeTreeTask.cpp:160`) still publish under `DataPartsLock`. Plain MergeTree over CAS therefore keeps the full BC7-1 stall behavior. The blocking `FIXME` at `MergeTreeSink.cpp:369-378` states the covered-part-vs-merge-selection race prevents flipping `rename_in_transaction` to `true` without a deeper redesign. Anchor: `MergeTreeSink.cpp:369-380`.
- **NEW-BC7-2 (Low)** — Belt-and-suspenders duplication: after `renameParts()` (`MergeTreeData.cpp:8986-8988`) runs the publish loop, the identical `commitTransaction()` loop inside `commit()` (`MergeTreeData.cpp:9008-9010`) is guarded only by `hasActiveTransaction()`. If a future refactor adds a code path that populates `precommitted_parts` **without** going through `preparePartForCommit`'s `rename_in_transaction=true` branch (i.e. the transaction is still active at `commit()` time) that publish silently regresses back under `DataPartsLock`. The comment at `:8967-8971` names the loop "a safety net" — that safety net IS the on-lock publish, and there is no assertion preventing it. Anchor: `MergeTreeData.cpp:9008-9010`.

## By-design / N/A / info

- Comment at `MergeTreeData.cpp:8977-8978` explicitly acknowledges the design: "keeps the disk commit (network I/O on object storages) off the data_parts lock, which Transaction::commit holds." This is the direct fix directive from the original BC7 audit, applied to the replicated paths.
- `moveDirectory` staged-only shapes (tmp→final in the same ns/ref, projection re-key, cross-part rename with staged source) are pure in-memory overlay ops — no S3 I/O. Only committed-source renames or table→table RENAME issue synchronous CAS. Anchor: `ContentAddressedTransaction.cpp:1275-1370`.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| BC7-1 | High | 🔴 still-present (partially fixed: replicated off-lock; plain on-lock) | `MergeTreeSink.cpp:369-380`, `MergeTreeData.cpp:8993, 9008-9010`, `ContentAddressedTransaction.cpp:435-520` |
| BC7-2 | Med | 🔴 still-present (for on-lock callers) | `ContentAddressedTransaction.cpp:485-497` |
| BC7-3 | Med | 🔴 still-present for plain MergeTree; ✅ fixed for replicated | `MergePlainMergeTreeTask.cpp:160`, `MutatePlainMergeTreeTask.cpp:134-135`; fix: `MergeTreeDataMergerMutator.cpp:525-528` |
| BC7-4 | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1032, 1200-1250` |
| BC7-5 | Low | 🔴 still-present | (no code-level mitigation for loading-path S3 I/O) |
| BC7-6 | Info | 📐 by-design ✅ | reads snapshot-under-lock unchanged |
| NEW-BC7-1 | Med | 🟡 new | `MergeTreeSink.cpp:369-380` |
| NEW-BC7-2 | Low | ⚪ info | `MergeTreeData.cpp:9008-9010` |
