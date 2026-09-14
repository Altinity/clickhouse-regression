# crash-consistency — re-run 2026-07-30

Re-run of `cas-crash-consistency-audit.md` against PR #2073 HEAD
(`/Volumes/workspace/ClickHouse` @ branch `cas-audit-20260730`). Static reasoning only.

## Scope in current code

Files/dirs walked (crash spine for each protocol step):

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.{h,cpp}` — commit loop
  (§2), `moveDirectory` (§3), `removeRecursive` (§4 catalog↔`dropNamespace` seam), `writeFile` verbatim-file path
  (§7 dedup-log).
- `Pool/CasRefProtocol.{h,cpp}` — the ref-log state machine, in particular the `owner_transition promote`
  precondition (§1 W1 fix), `AddPrecommit` precondition (§6 W-N2 window).
- `Pool/CasPartWriteTxn.{h,cpp}` — `precommitAdd`, `promote`, `uploadFromSource` (§5 hash-vs-bytes), idempotent
  re-drive guards.
- `Pool/CasRefLedger.{h,cpp}` — `dropRef`, `dropNamespace`, `_cleanup` marker gating.
- `Parts/PartFolderAccess.{h,cpp}` — `republishRef` (crash between publishEntries and dropRef), `dropRef` vs
  `dropRefIfPresent`.
- `Gc/CasGc.cpp` — post-CAS `handoff_reclaim` (§7 T0), `manifest_deletes` best-effort phase.
- `Gc/CasOrphanManifestSweep.{h,cpp}` — orphan-manifest reclaimer completeness.

Method: per multi-step operation (write, GC, mount, rename, DETACH/ATTACH), enumerate every intermediate
durable step and ask what the *next* Store::open / GC round / re-issue observes.

## Findings still present

### `CAS-021` — Multi-part `commit()` is not crash-durably atomic
- Anchor: `ContentAddressed/ContentAddressedTransaction.cpp:458-513` (`ContentAddressedTransaction::commit`)
- Trigger: transaction stages ≥2 parts; power-loss between publish of part *i* and part *i+1*.
- Evidence quote (`:460-462`):
  > "there is no multi-ref atomic publish, so a publish that throws after earlier parts already published
  > would leave a PARTIAL commit — some refs durably visible while the transaction reports failure"
- Notes: rollback lives in the `catch (...)` block (`:499`), not in a crash-durable log — matches DUR1. The
  `part_outcomes[i]` slot-write improvement is a code-quality refinement of the same rollback, still
  non-crash-durable. Rollback also elides `updateRefPublishedAt` mutations (comment `:471-472`), so a partial
  commit further diverges from the timestamp invariant.

### `CAS-022` — RENAME TABLE (`moveDirectory` cross-namespace) is a non-atomic multi-op with no durable move-journal
- Anchor: `ContentAddressed/ContentAddressedTransaction.cpp:1200-1249` (`moveDirectory`, RENAME-TABLE branch)
- Trigger: RENAME TABLE across DB engines / cross-namespace move; crash mid-`republishRef` loop or between
  the loop and the terminating `dropNamespace(from_ns)`.
- Evidence quote (`:1216-1224`):
  > "There is no native cross-namespace atomicity ... a mid-loop throw leaves the table SPLIT across the
  > two namespaces, but re-driving the SAME rename completes it ... There is no in-call compensation;
  > true atomicity would need a durable move-journal (deliberately out of scope — it would touch the
  > tested GC/journal layer). On partial failure we log loudly so the split state is diagnosable."
- Notes: The intent to remain out-of-scope is now explicit in the code comment (comment upgrade, no
  behavioral fix). Idempotent primitives (`republishRef` content-compares dst at `:520-529`; `dropNamespace`
  no-ops on absent; `putNamespaceFile` LWW) preserve re-drive completeness. **Still-present as originally
  characterized.**

### `CAS-035` — Presence-asserting closures misreport a lost-ACK-succeeded write as failure
- Anchor: `Pool/CasRefLedger.cpp:2801-2822` (`CasRefLedger::dropRef`)
- Trigger: `dropRef` ACK is lost; caller retries; the second attempt reads state fresh, sees the ref
  absent from `committed` (its own earlier drop landed), and throws typed `FILE_DOESNT_EXIST`.
- Evidence quote (`:2811-2814`):
  > "if (it == state.getCommitted().end()) ... `throw Exception(ErrorCodes::FILE_DOESNT_EXIST, "dropRef: no
  > such ref {} in namespace {}", ref_name, ns.string());`"
- Notes: Higher-level `CachedPartFolderAccess::dropRefIfPresent` (`PartFolderAccess.cpp:600-624`) catches the
  same `FILE_DOESNT_EXIST` and treats it as success. **The primitive still fails-loud on lost-ACK replay;
  the fix is at call-site policy, not at the source.** Same shape holds for `updateRefPublishedAt`
  (`CasRefLedger.cpp:2853-2856`). Any caller that does not route through `dropRefIfPresent` still
  observes the misreport (e.g. rollback in commit uses `dropRefIfMatches` — which handles concurrent repoint,
  but a lost-ACK on the same match throws `FILE_DOESNT_EXIST` semantics on the underlying `dropRef`).

### `CAS-038` — Local scratch temp file un-fsynced and never re-hashed against its key before upload
- Anchor: `ContentAddressed/ContentAddressedTransaction.cpp:1749-1765` (`CaContentWriteBuffer` ctor) and
  `:1819-1847` (`finalizeImpl`); upload at `Pool/CasPartWriteTxn.cpp:427-624` (`uploadFromSource`).
- Trigger: writer streams to a local temp file, hashing chain computes `hash_hex` on the byte stream; local
  file is `finalize()`-d without `fsync`; upload later re-reads the temp file to stream to S3. Local FS
  corruption / power-loss + partial page-cache flush between finalize and upload → uploaded bytes ≠ hashed
  bytes.
- Evidence quote (`:1837`): `sink->finalize();` — plain `WriteBufferFromFile::finalize()`, no `sync()` call
  and no re-hash between finalize and upload. `uploadFromSource` (`CasPartWriteTxn.cpp:598-602`) validates
  only streamed byte-*count*, not content: `"source streamed {} bytes, declared {}"`.
- Notes: matches original `BC2-1/BC2-2`. Pairs with CAS-005 (no read-side re-hash) — a compromised blob is
  never caught.

### `CAS-044` — Crash between catalog drop and `dropNamespace` → permanently orphaned namespace
- Anchor: `ContentAddressed/ContentAddressedTransaction.cpp:1032-1074` (`removeRecursive` table-dir branch)
  invokes `partAccess()->dropNamespace(...)` at `:1055,1064,1072`; `Pool/CasRefLedger.cpp:2890-2983`
  (`dropNamespace`).
- Trigger: MergeTree/Interpreter durably records "table dropped" in the catalog, but crashes before the
  transaction publishing `dropNamespace` becomes durable in the pool.
- Evidence quote (`Pool/CasRefLedger.cpp:2979-2982`):
  > "The writer performs NO physical deletion of ref-log/snapshot objects or verbatim namespace files
  > -- GC's namespace-cleanup item ... owns that reclaim, keyed off the durable `remove_namespace` this
  > call just appended. Until GC reclaims it, a dropped namespace's ref-log objects and verbatim files
  > remain as debris."
- Notes: No catalog-vs-pool reconcile on startup (no code path enumerates pool namespaces without a live
  catalog owner and drops them). The GC-side namespace cleanup only fires on a **durable** `remove_namespace`
  op — a namespace whose `remove_namespace` never landed is invisible to GC. **Still-present as originally
  characterized.**

### `CAS-072` — Post-CAS T0 hand-off crash strands a `gc/gen/<G>/` prefix
- Anchor: `Gc/CasGc.cpp:793-833` (`runRegularRound`, PHASE 14/18 `handoff_reclaim`)
- Trigger: round CAS commits (durable), then crash before `deletePrefixWholesale(layout.gcGenPrefix(g), ...)`
  fires. `snap_pruned_through` already advanced past `g`; the wholesale prune "NEVER revisits it".
- Evidence quote (`:801-803`):
  > "Best-effort: a crash between the CAS and here leaks the prefix to fsck (single-crash window, no
  > permanent leak — but note the cursor already advanced, so a plain retry will NOT re-attempt it; fsck
  > is the backstop)."
- Notes: matches original GC-1 verdict. `Cas::Fsck` remains the recovery path; not auto-reclaimed. Still-present.

### `CAS-082` — Lost-ACK replay double-appends journal events (now converted to a **fail-closed CORRUPTED_DATA** on retry)
- Anchor: `Pool/CasPartWriteTxn.cpp:995-1002` (`precommitAdd` closure idempotent-committed guard);
  `Pool/CasRefProtocol.cpp:190-208` (`AddPrecommit` precondition).
- Trigger: `precommitAdd` ACK is lost; caller retries. Fresh state read inside the append closure at
  `:995-1002` handles the case where a prior `promote` already installed a committed row (returns `{}`,
  idempotent no-op). But **if the earlier `precommitAdd` durably applied but promote did not**, the retry
  observes `state.getCommitted()` does not contain the ref, appends a fresh `AddPrecommit` op, and the state
  machine at `CasRefProtocol.cpp:192-194` throws `CORRUPTED_DATA` on `precommits.contains({...})`.
- Evidence quote (`CasRefProtocol.cpp:192-194`):
  > "if (precommits.contains({b.ref_name, b.manifest_ref})) throw ... 'add precommit already exists for this
  > exact manifest'"
- Notes: The set-idempotent journal-bloat behavior described in the original W-N2/J5 is gone — but the
  replacement is a **fail-CLOSED `CORRUPTED_DATA`** on the exact retry path. **Behavior evolved; still not
  a clean lost-ACK replay** (it now throws hard instead of silently bloating; either shape is a client-visible
  spurious failure, but the new shape is worse for the retry-after-crash story because the second attempt
  cannot make progress). See also new observation NEW-CRASH-2.

### `CAS-096` — Scratch-FS-full fails the insert late; no pre-flight sizing check
- Anchor: `ContentAddressed/ContentAddressedTransaction.cpp:1749-1765` (temp file created inside
  `CaContentWriteBuffer` ctor); no `space_available` / `df` probe on the scratch mount at
  `ContentAddressedSettings.{h,cpp}` or in `checkOpAdmitted`.
- Trigger: The scratch mount fills mid-write; `WriteBufferFromFile::nextImpl` throws `ENOSPC` deep inside a
  finalize path, aborting an insert that already completed most of its column streams.
- Evidence: no pre-flight `std::filesystem::space` / operator-facing sizing docs in this dir; every temp
  path is created inline at `:1749-1750,957-963`. Temp-file uniqueness still relies on a 32-char
  `getRandomASCIIString` (`:1750`, `:959`) — no PID/counter suffix — matching BC2-6.
- Notes: still-present.

### `CAS-104` — Non-replicated dedup-log crash mid-update
- Anchor: `ContentAddressed/ContentAddressedTransaction.cpp:809-836` (`writeFile` verbatim namespace-file
  branch); `Pool/CasRefLedger` verbatim-file storage via `putNamespaceFile`.
- Trigger: `writeFile` on `deduplication_logs/deduplication_log_N.txt` in Append mode reads existing bytes,
  concatenates the new record, and issues one `putNamespaceFile(ns, name, carried + bytes)`; crash between
  the local commit and this call → previous durable version remains, an INSERT block's dedup entry is lost
  → bounded duplicate part on retry.
- Evidence quote (`:800-808`):
  > "Non-part files are VERBATIM namespace files, durable on finalize (no commit involvement - the disk
  > layer's autocommit contract for them rides exactly this). Append is serviced by read-modify-rewrite:
  > the existing bytes are carried forward ... Safe only because the sole production appender ... never has
  > a second concurrent appender on the same key."
- Notes: single-PUT atomicity + bounded-duplicate impact matches original DEDUP-2 categorization. CAS's own
  content-dedup absorbs the duplicate part. Still-present at original severity (Low).

## Findings fixed / no longer reproducible

### `CAS-020` — `promote`-overwrite leak (W1) — **FIXED**
- Anchor of fix: `Pool/CasRefProtocol.cpp:243-273` (`applyOwnerTransition`, `Promote` case) and the spec at
  `Pool/CasRefProtocol.h:316-329`.
- Evidence quote (`CasRefProtocol.cpp:262-265`):
  > "if (committed.contains(b.ref_name)) throw Exception(ErrorCodes::CORRUPTED_DATA, 'promote {} would
  > silently displace a different already-committed manifest -- remove it with an explicit
  > owner_transition first', b.ref_name);"
- The `owner_transition promote` precondition now explicitly refuses to displace a different already-committed
  manifest under the same `ref_name`; the caller must emit an explicit `owner_transition(old=Committed,
  new=None)` op in the SAME transaction to evict the stale row before the promote binds the new one. This
  eliminates the unconditional `refs[R]=…` overwrite that the original audit identified as the only
  non-reclaimed orphan class. Reinforced at the rename lane by `republishRef`
  (`Parts/PartFolderAccess.cpp:520-529`), which content-compares an already-committed destination and
  refuses on mismatch (`ErrorCodes::ABORTED`, "rename/attach conflict").

## New findings (not in original audit)

### `NEW-CRASH-1` — Single-part `republishRef` crash between `publishEntries` and `dropRef` leaves a split observable state — Low–Med
- Anchor: `Parts/PartFolderAccess.cpp:506-534` (`CachedPartFolderAccess::republishRef`).
- Trigger: DETACH/ATTACH/merge-result-rename/`delete_tmp_` rename executes `moveDirectory` on a committed
  part, which routes to `republishRef(src, dst)` at `ContentAddressed/ContentAddressedTransaction.cpp:1370`.
  `republishRef` (`:531-532`) does `publishEntries(dst, ...)` then `dropRef(src)`. Power-loss between these
  two durable ops leaves **both** `src` and `dst` refs live.
- Observable: for a DETACH crash mid-move, the same part becomes visible in both the live and detached
  namespaces (or under both the source and destination names for a merge-result rename). Duplicate parts
  at startup; MergeTree deduplication only handles content-hash duplicates within the SAME part-set, not
  cross-namespace/name.
- Evidence quote: at `:531-532`, `publishEntries(dst, src_manifest->entries, Cas::ProvenanceOp::Other);
  dropRef(src);` — sequential durable ops with no journal linking them.
- Notes: This is the **fine-grained cousin of CAS-022** (which called out the RENAME-TABLE-level split).
  It has the same "re-drivable if re-issued" property (`republishRef` at `:520-529` correctly handles a
  present-dst-with-matching-content), but nothing auto-re-drives after a crash for the DETACH/ATTACH/merge
  paths — the caller (MergeTree) has its own recovery for merges (`rollbackPartsToTemporaryState`), but the
  ATTACH/DETACH crash-recovery is not statically obvious in this layer. Merits a targeted crash-drive test.

### `NEW-CRASH-2` — Lost-ACK replay on `precommitAdd` between precommit and promote now throws `CORRUPTED_DATA` — Low
- Anchor: `Pool/CasRefProtocol.cpp:190-208` (`AddPrecommit` precondition) vs.
  `Pool/CasPartWriteTxn.cpp:970-1032` (`precommitAdd`'s closure).
- Trigger: `precommitAdd`'s durable append succeeds but its ACK is lost; caller retries. Fresh state read
  inside the closure at `:995-1002` observes the ref is NOT yet in `committed` (correct: only precommitted),
  fails the `id_staged_by_this_txn` guard OR falls through to append a fresh `AddPrecommit` op. The state
  machine then throws `CORRUPTED_DATA` at `CasRefProtocol.cpp:192-194` because the exact
  `(ref_name, manifest_ref)` pair is already in `precommits`.
- Notes: This upgrades the original CAS-082 "set-idempotent double-append = harmless journal bloat" to
  "fail-loud `CORRUPTED_DATA` on lost-ACK replay". Correct outcome for byzantine inputs (fails closed on a
  genuinely corrupted log), but a benign lost-ACK on a healthy pool now surfaces as `CORRUPTED_DATA` at the
  caller. Since `CORRUPTED_DATA` is typically retried at a higher level as a hard error (not a lost-ACK
  hint), the retry can propagate as an INSERT/mutation failure. Suggested mitigation: writer-side
  `resolveRef+precommitContains` idempotency check before re-appending the same `AddPrecommit` op (mirror
  the promote-side idempotent guard at `:1110-1117`).

## By-design / N/A / info

- Post-CAS `manifest_deletes` phase (`Gc/CasGc.cpp:835-843`) is best-effort by design: a crash there leaks
  manifest bodies to the orphan-manifest sweep (`Gc/CasOrphanManifestSweep.h:41-78`), which is the intended
  reclaimer. Matches original §1's "orphan-manifest sweep reclaims once the build is watermark-dead".
- The `_cleanup/<remove_txn_id>` marker gate on namespace recreation (`Pool/CasPartWriteTxn.cpp:1005-1021`)
  correctly deals with the "crash between remove_namespace durable and GC namespace-cleanup Completed"
  window by making recreation of the same namespace UUID wait for the marker, rather than allowing an
  ambiguous re-birth.
- Removed snapshot best-effort publish (`Pool/CasRefLedger.cpp:2970-2977`) is safely idempotent — a crash
  before it is compensated by GC namespace-cleanup republishing it.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-020 | Med | ✅ fixed | `Pool/CasRefProtocol.cpp:262-265`, `Parts/PartFolderAccess.cpp:520-529` |
| CAS-021 | Low–Med | 🔴 still-present | `ContentAddressedTransaction.cpp:458-513` |
| CAS-022 | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1200-1249` |
| CAS-035 | Med | 🔴 still-present (mitigated at call sites via `dropRefIfPresent`) | `Pool/CasRefLedger.cpp:2811-2814` |
| CAS-038 | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1749-1765,1819-1847`; `Pool/CasPartWriteTxn.cpp:598-602` |
| CAS-044 | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1032-1074`; `Pool/CasRefLedger.cpp:2979-2982` |
| CAS-072 | Low | 🔴 still-present (fsck backstop, by-design) | `Gc/CasGc.cpp:793-833` |
| CAS-082 | Low | 🔴 changed-shape (see NEW-CRASH-2) | `Pool/CasRefProtocol.cpp:192-194`, `CasPartWriteTxn.cpp:970-1032` |
| CAS-096 | Low | 🔴 still-present | `ContentAddressedTransaction.cpp:1749-1750,957-963` |
| CAS-104 | Low | 🔴 still-present (by-design bounded impact) | `ContentAddressedTransaction.cpp:809-836` |
| NEW-CRASH-1 | Low–Med | 🔴 new | `Parts/PartFolderAccess.cpp:506-534` |
| NEW-CRASH-2 | Low | 🔴 new | `Pool/CasRefProtocol.cpp:192-194` + `CasPartWriteTxn.cpp:970-1032` |

### Counts
- Still-present: 9 (CAS-021, CAS-022, CAS-035, CAS-038, CAS-044, CAS-072, CAS-082 [shape-changed], CAS-096, CAS-104)
- Fixed: 1 (CAS-020)
- New findings: 2 (NEW-CRASH-1, NEW-CRASH-2)
