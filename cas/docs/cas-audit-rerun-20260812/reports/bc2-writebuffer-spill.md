# bc2-writebuffer-spill -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is (all CAS tests deleted; base tests read via `git show`).

Audited surface: the write-buffer / staging / spill machinery for blob bodies --
`Primitives/CasBlobHashingWriteBuffer.{h,cpp}`, `Primitives/CasXxh3Streamer.h`,
`Cas::CaContentWriteBuffer` and `Cas::CaInlineWriteBuffer` (`ContentAddressedTransaction.{h,cpp}`),
the inline-vs-spill decision (`partFileMustStayBlob`, `INLINE_CAP`), the local scratch file lifecycle,
the upload/promote consumers (`Pool/CasPartWriteTxn.cpp`, `Backend/CasObjectStorageBackend.cpp`),
scratch configuration (`ContentAddressedSettings.cpp`, `MetadataStorages/MetadataStorageFactory.cpp`),
and the surrounding `WriteBuffer` contract (`src/IO/WriteBuffer.h`, `src/IO/HashingWriteBuffer.h`,
`src/IO/WriteBufferFromFile.h`, `src/IO/WriteBufferFromS3.cpp`).

Code-only rule observed: `docs/**` and comments were not used as evidence of intent; only shipped
strings, control flow, and configuration defaults.

Cited siblings (not re-derived here): local scratch staging is never swept at startup; there is no
re-hash on body re-upload; `Backend::resurrect` bypasses the request controller.

## Buffer/spill path as implemented   <- with anchors

Placement decision, per part file (`ContentAddressedTransaction.cpp`):

- `partFileMustStayBlob(file)` is a *name* test: exact `"primary.idx"`, or a suffix in
  `{.bin,.mrk,.mrk2,.mrk3,.cmrk,.cmrk2,.cmrk3}` -- `ContentAddressedTransaction.cpp:65-75`.
- Blob-classified files stream through `Cas::CaContentWriteBuffer` -- `ContentAddressedTransaction.cpp:598-636`.
- Everything else goes through `Cas::CaInlineWriteBuffer`, which accumulates the *entire* file in a
  `std::string` (`ContentAddressedTransaction.cpp:1336-1341`) and on finalize either inlines it into
  the manifest when `size <= INLINE_CAP` (1 MiB, `ContentAddressedTransaction.cpp:92`, decision at
  `:643`) or spills it to a scratch file `inline_overflow_<32 rand>.tmp` and stages it as a blob
  (`ContentAddressedTransaction.cpp:655-669`).
- `file` may be nested (`<proj>.proj/primary.idx`), because the parser joins all components below the
  part directory -- `Parts/PartPathParser.cpp:199-202`.

Blob path, two backends (`ContentAddressedTransaction.cpp:598-636`):

- `staging_backend=s3` *and* probed conditional-copy support: sink is an object-storage write buffer at
  `<pool>/staging/<server_root_id>/<32 rand>.tmp`, prefixed with an envelope header, plus a fence
  pre-check callback -- `:602-623`, header built at `:514-529`, prefix at
  `ContentAddressedMetadataStorage.cpp:852-855`.
- otherwise (default `staging_backend=local`, `ContentAddressedSettings.cpp:57`): sink is a local
  `WriteBufferFromFile` under `metadata_storage.scratchPath()` -- `:625-635`.

`CaContentWriteBuffer` internals (`ContentAddressedTransaction.cpp:1213-1323`):

- local ctor: `fs::create_directories(temp_dir)`, name `<temp_dir>/<32 rand>.tmp` (`getRandomASCIIString`,
  `thread_local_rng`, `[a-z]^32`), sink opened with `mode=0666`, no `O_EXCL` (flags `-1`) --
  `:1223-1235`, `WriteBufferFromFile.h:32-41`.
- own buffer size and sink buffer size are both `clampCasWriteBufferSize(...)`, capped at 256 MiB --
  `:1144-1149`, `:1220`, `:1228`.
- `nextImpl` forwards into the hashing buffer (`:1269-1274`); the hashing buffer updates the digest and
  writes to the sink (`CasBlobHashingWriteBuffer.cpp:106-114`, `:160-171`), or, for CityHash128, aliases
  the sink's own buffer (`CasBlobHashingWriteBuffer.cpp:39-64`, `HashingWriteBuffer.h:55-77`).
- `finalizeImpl` (`:1276-1295`): `next()`; `size = count()`; `hash_hex = hashing->getHashHex()`;
  `hashing->finalize()`; optional fence check; `sink->finalize()`; then `on_finalized(hash, size, temp_path)`
  and only then `temp_ownership_transferred = true`. No `sink->sync()` anywhere on this path.
- `cancelImpl` (`:1297-1305`) cancels hashing and sink and, for the local backend only, unlinks the scratch
  file; the destructor calls `cancel()` and unlinks if ownership was never transferred (`:1262-1267`).

Staging bookkeeping and consumption:

- `stageBlobPartFile` records `PendingBlob{ref, staging_key, size, backend}` and a manifest entry --
  `:497-512`, struct at `ContentAddressedTransaction.h:89`.
- Upload happens only at commit, inside `publishStaging` -> `uploadPendingBlobs`
  (`:264`, `:299`, `:208-242`); local staging is re-opened lazily as `ReadBufferFromFile(staging_key)`
  (`:230-233`).
- `fanOutBlobUploads` dedups by ref, cross-checks `declared_size == source.size`, and fans out on the
  blob upload pool -- `:1153-1210`.
- The upload/resurrect consumers stream the source and compare *byte counts only*:
  `CasPartWriteTxn.cpp:394-403`, `:469-471`; `CasObjectStorageBackend.cpp:827-830`, `:838-847`.
- Scratch/staging reclamation is transaction-scoped: `cleanupPendingTempFiles()` unlinks local scratch for
  every pending blob and removes S3 staging objects *only when committed* -- `:148-172`, called at
  `:103` (dtor), `:322`, `:350`.
- Scratch dir default is `<data path>/disks/<name>/cas_scratch/`, created at disk registration --
  `MetadataStorageFactory.cpp:233-238`; the only related setting is `scratch_path`
  (`ContentAddressedSettings.cpp:30`).

## Findings

### bc2-1 -- Local scratch spill is unreserved, unaccounted, uncapped, and held for the whole transaction (High)

- Anchor: `ContentAddressedTransaction.cpp:1223-1235` (scratch file creation), `:148-172`
  (reclamation), `:264` / `:299` (upload only at commit), `DiskObjectStorage.h:65-67`
  (`getTotalSpace/getAvailableSpace/getUnreservedSpace` all return `{}`), `ContentAddressedSettings.cpp:30-57`
  (no size/quota setting).
- Trigger: any INSERT/merge/mutation into a CAS disk with `staging_backend=local` (the default) whose part
  is larger than the free space of the filesystem holding `<data path>/disks/<name>/cas_scratch`. Because
  the local scratch file for a blob is unlinked only by `cleanupPendingTempFiles()` -- after *all* parts of
  the transaction have been published -- and never right after that blob's own upload, peak local usage is
  the full part size per in-flight transaction, times concurrency.
- Evidence: the write path performs no `IDisk::reserve`, no `TemporaryDataOnDisk`/`temporary_data_on_disk`
  registration, and no free-space probe before creating the scratch file (grep for
  `reserve|TemporaryDataOnDisk|statvfs` in `ContentAddressedTransaction.cpp` returns only
  `requests.reserve` at `:216`). MergeTree's own back-pressure cannot compensate: `DiskObjectStorage`
  reports unlimited space, so `reserve()` on a CAS disk always succeeds
  (`DiskObjectStorage.cpp:544-566`).
- Notes: on ENOSPC the individual write does fail closed (`WriteBufferFromFile` throws, `cancelImpl`
  unlinks), but the *victim* is the whole server-local data path shared with logs, other disks' caches, and
  every other spill user. Nothing bounds total scratch bytes across concurrent writers. Combined with the
  sibling finding that scratch is never swept at startup, a crash mid-transaction converts this transient
  peak into permanent occupancy.

### bc2-2 -- The staged body is never re-verified against the computed hash before upload; scratch is never fsynced (Medium)

- Anchor: `ContentAddressedTransaction.cpp:1276-1295` (hash computed in memory, no `sink->sync()`),
  `:230-233` (body re-opened from the scratch path at commit),
  `CasPartWriteTxn.cpp:394-403` (fresh upload: only `written != source.size` is checked),
  `CasPartWriteTxn.cpp:469-471` and `CasObjectStorageBackend.cpp:838-847` (resurrect: same, count only).
- Trigger: any divergence between the bytes hashed in memory and the bytes read back from the scratch file
  that preserves length -- page-cache/disk bit rot, a partial overwrite by anything else touching the
  scratch dir, or a future defect in the three-stage buffer chain. The blob is then published under a
  content-hash key that does not describe its bytes, which is the one invariant a content-addressed store
  cannot lose. Nothing on the write path ever reads the staged file back through a hasher.
- Evidence: the digest is finalized from the in-memory streamer state (`CasBlobHashingWriteBuffer.cpp:96-103`,
  `:143-155`, `:52-56`) before the sink is finalized; the file is closed without `fsync` (the only `sync()`
  entry point, `ContentAddressedTransaction.cpp:1313-1318`, is caller-driven and not invoked by
  `finalizeImpl`); the consumer's sole integrity gate is the byte counter.
- Notes: cite sibling "no re-hash on body re-upload" -- the same gap on the re-upload/resurrect path.
  Length-changing corruption *is* caught (see Checked and sound). Severity is Medium rather than High
  because the window is process-local and short-lived, but the failure is silent and permanent.

### bc2-3 -- Projection primary indexes and skip indexes take the fully-in-memory inline path (Medium)

- Anchor: `ContentAddressedTransaction.cpp:65-75` (`file_name == "primary.idx"` is an exact match; only
  `.bin`/`.mrk*` suffixes otherwise), `Parts/PartPathParser.cpp:199-202` (nested `file` names),
  `ContentAddressedTransaction.cpp:1336-1341` (unbounded `std::string` accumulation), `:643-669`
  (spill decided only *after* the whole file is already resident).
- Trigger: INSERT/merge on a table with a projection or a non-trivial skip index. The projection's index is
  written as `<part>/<proj>.proj/primary.idx`, which is not equal to `"primary.idx"`, and skip indexes are
  `skp_idx_*.idx` / `.idx2` -- none match `partFileMustStayBlob`. Each such file is buffered whole in RAM by
  `CaInlineWriteBuffer`, and if it exceeds 1 MiB it is then written out to scratch in a second full copy
  before being staged as a blob.
- Evidence: `CaInlineWriteBuffer::nextImpl` appends every flush to `accumulated` with no cap and no
  streaming sink; the `> INLINE_CAP` branch materializes `bytes` again through `WriteBufferFromFile`.
  The blob path streams; this path does not.
- Notes: usearch/vector-similarity, `set`, and text indexes are the realistic large cases; a wide-part
  projection index is unbounded in principle. Practical impact is memory-limit/OOM pressure proportional to
  the largest non-blob-classified file rather than to the buffer size. The same code path also runs on the
  namespace-file branch with a full `carried + bytes` copy for `WriteMode::Append`
  (`ContentAddressedTransaction.cpp:570-588`), doubling peak memory there.

### bc2-4 -- Inline-overflow scratch file leaks when the spill write itself fails (Low)

- Anchor: `ContentAddressedTransaction.cpp:655-669`. The file is created and written in the block at
  `:660-664`; the removal guard `SCOPE_EXIT({ if (!staged) ... remove(temp_path) ... })` is installed
  afterwards at `:665-666`.
- Trigger: ENOSPC/EIO/EDQUOT inside `tmp.write(...)` or `tmp.finalize()` for a non-blob part file larger
  than 1 MiB. The exception escapes before any cleanup is registered and before `stageBlobPartFile` records
  a `PendingBlob`, so neither the `SCOPE_EXIT`, nor `cleanupPendingTempFiles()`, nor the transaction
  destructor knows the file exists.
- Evidence: cleanup of local scratch is driven exclusively by `PendingBlob` entries (`:148-172`), and the
  entry is only pushed at `:502` after the write completed.
- Notes: leaks a partially written `inline_overflow_*.tmp`; with the sibling finding that local scratch is
  never swept at startup, it is never reclaimed. Note also that this branch always uses *local* scratch even
  when `staging_backend=s3` is configured and supported, so an s3-staging deployment still accumulates local
  scratch debris.

### bc2-5 -- Aborted transactions intentionally retain S3 staging objects; the mount-time sweep is unfiltered (Low)

- Anchor: `ContentAddressedTransaction.cpp:159-168` -- S3 staging objects are removed only
  `else if (committed)`; `Pool/CasServerRoot.cpp:1140-1160` -- `sweepOwnMountStaging` deletes *every* object
  under `<pool>/staging/<server_root_id>/` with no age, ownership, or incarnation filter; invoked at
  `ContentAddressedMetadataStorage.cpp:607`.
- Trigger: (a) any failed/abandoned transaction leaves `<32 rand>.tmp` staging objects that persist until the
  next mount of that disk; (b) a second `ContentAddressedMetadataStorage` constructed for the same
  `server_root_id` (config reload / two disks configured with the same `server_root_id`) sweeps the staging
  objects of the first instance's in-flight writers.
- Evidence: the sweep loop is prefix-only and swallows per-object errors; the consumers of a vanished staging
  key throw (`CasPartWriteTxn.cpp:459-461` `FILE_DOESNT_EXIST`, and `promoteStaged` fails the conditional
  create), so case (b) is fail-closed rather than silent.
- Notes: `staging_backend=s3` is opt-in (`ContentAddressedSettings.cpp:57`), and multipart parts *are*
  aborted on cancel (`WriteBufferFromS3.cpp:241-245`), which bounds the billing exposure to completed
  staging objects only.

### bc2-6 -- Fence pre-check exists only on the S3 staging path (Low)

- Anchor: `ContentAddressedTransaction.cpp:607-622` (S3 path captures `fenceGeneration()` and passes
  `check_fence_before_finalize`) versus `:625-635` (local path passes no such callback);
  consumed at `:1285-1286`.
- Trigger: a writer whose mount fence was lost mid-write on the default local backend streams the entire
  body to scratch and only discovers the loss at commit, inside `stagingConditionalCreate`
  (`CasPartWriteTxn.cpp:406-419`).
- Evidence: the fence is still enforced before anything is published, so this is wasted work and delayed
  diagnostics, not a correctness gap.
- Notes: the asymmetry also means the two backends report the same operator error at different points in the
  INSERT lifecycle.

### bc2-7 -- Three full copies per byte and two clamp-sized buffers per open blob file (Low)

- Anchor: `ContentAddressedTransaction.cpp:1220` (own buffer = clamped `buf_size`), `:1226-1235` (sink buffer
  = clamped `buf_size` again), `:1144-1149` (`kMaxCasWriteBufferBytes = 256 MiB`), `:1269-1274`
  (`nextImpl` is a pure forward), `CasBlobHashingWriteBuffer.cpp:106-114` (copy into the hashing buffer,
  then into the sink).
- Trigger: any blob write. `CaContentWriteBuffer`'s own buffer adds no function beyond forwarding to the
  hashing buffer, so every byte is memcpy'd into the outer buffer, into the 2 KiB hashing buffer
  (`DBMS_DEFAULT_HASHING_BLOCK_SIZE`, `HashingWriteBuffer.h:8`), and into the sink buffer. Peak resident
  buffer memory per concurrently open blob file is 2x the clamped `buf_size`, i.e. up to 512 MiB if
  `max_write_buffer_size` / `adaptive_write_buffer_initial_size` is configured large.
- Evidence: the CityHash128 variant avoids the third copy by aliasing the sink's buffer
  (`CasBlobHashingWriteBuffer.cpp:43-44`, `HashingWriteBuffer.h:72-76`); the XXH3 and SHA-256 variants do
  not. No buffer is pooled or reused across part files -- every `writeFile` allocates fresh.
- Notes: also means the hash streamer is fed in 2 KiB chunks, which is well below the XXH3/SHA-256 sweet spot.

## Checked and sound

- **XXH3 streamer lifetime.** `XXH3_createState()` failure is detected (`valid()` check throwing
  `CANNOT_ALLOCATE_MEMORY`, `CasBlobHashingWriteBuffer.cpp:87-88`), `XXH3_128bits_reset` on a null state
  returns an error without dereferencing, the state is freed in the destructor, and copy/assign are deleted
  (`CasXxh3Streamer.h:17-24`). `digest()` is const and does not consume the state, so `getHashHex()` is
  idempotent.
- **The digest covers exactly the body, never the envelope header.** On the S3 staging path the header is
  written to the sink in the ctor (`ContentAddressedTransaction.cpp:1256-1257`) *before*
  `makeBlobHashingWriteBuffer`, and `HashingWriteBuffer`'s ctor calls `out.next()` to flush pre-existing
  bytes (`HashingWriteBuffer.h:72`); the XXH3/SHA-256 variants only ever touch the sink from `nextImpl`.
- **No tail bytes escape the digest, and the recorded size matches.** All three `getHashHex()`
  implementations call `next()` first (`CasBlobHashingWriteBuffer.cpp:54`, `:98`, `:145`), and
  `finalizeImpl` takes `size = count()` after its own `next()` (`ContentAddressedTransaction.cpp:1278-1279`).
- **The sink is finalized exactly once, and after the fence check.** CityHash128's `finalizeImpl` calls
  `HashingWriteBuffer::finalize()`, whose default `finalizeImpl` is only `next()` (`WriteBuffer.h:132`); it
  does not finalize the wrapped sink. So the ordering at `:1283-1288` really is
  hash -> flush -> fence check -> sink finalize.
- **WriteBuffer contract / destructor-without-finalize.** `~CaContentWriteBuffer` calls `cancel()`
  (`:1262-1267`); `cancel()` is a no-op once finalized and `cancelImpl` is `noexcept` and only does
  best-effort `fs::remove` with an `error_code` (`:1307-1311`). Any exception thrown inside `finalizeImpl`
  -- including from `on_finalized` -- funnels through `finalize()`'s cancel path, so the scratch file is
  unlinked; `temp_ownership_transferred` is set only after `on_finalized` returns
  (`:1290-1294`), so there is no window in which the file is both orphaned and unowned.
- **Handoff race between `pending_blobs` and manifest entries.** If `stageBlobPartFile`'s `buildFor(...)`
  throws after the `pending_blobs.push_back` (`:502-503`), no manifest entry is created, and
  `uploadPendingBlobs` filters pending blobs against the referenced hashes (`:210-220`), so a scratch file
  already unlinked by `cancelImpl` is never opened for upload; the later `cleanupPendingTempFiles` remove of
  a missing path is `error_code`-swallowed.
- **Length-changing corruption/truncation of the staged body is caught, fail-closed.** Both the fresh-upload
  path (`CasPartWriteTxn.cpp:400-402`) and both resurrect modes
  (`CasObjectStorageBackend.cpp:827-830`, `:841-847`) compare streamed bytes against the declared size and
  throw before publishing, cancelling the sink; `fanOutBlobUploads` additionally rejects
  `declared_size != source.size` and conflicting sizes for one ref (`:1163-1177`).
- **Scratch name uniqueness and location.** 32 characters drawn from `[a-z]` (~150 bits) via the per-thread
  `thread_local_rng` (`Common/getRandomASCIIString.cpp:8-21`) makes collisions between concurrent writers a
  non-trigger; the default scratch dir is `<data path>/disks/<name>/cas_scratch/` under the server's own data
  path (`MetadataStorageFactory.cpp:236`), not a shared world-writable location, and relative configured
  values are anchored to the data path (`ContentAddressedSettings.cpp:103-110`). The explicit `mode 0666`
  (`ContentAddressedTransaction.cpp:1231`) is `WriteBufferFromFile`'s own default
  (`WriteBufferFromFile.h:37`) and is masked by umask, matching ClickHouse's convention for local data
  files; the absence of `O_EXCL` is not exploitable given the unpredictable name and non-shared directory.
- **Superseded writes to the same part file.** `std::erase_if` on `st.entries` replaces the manifest entry
  (`:510`, and `:652` on the inline path); the stale `PendingBlob` is skipped at upload by the
  referenced-hash filter and its scratch file is unlinked by `cleanupPendingTempFiles`.
- **Multipart abort on the S3 staging path.** `cancelImpl` calls `sink->cancel()`
  (`ContentAddressedTransaction.cpp:1301-1302`), and `WriteBufferFromS3::cancelImpl` aborts the multipart
  upload (`WriteBufferFromS3.cpp:241-245`, `:469-481`).
- **Append is rejected for part files** before any buffer is created
  (`ContentAddressedTransaction.cpp:536-537`), so the spill path never has to reconcile a carried prefix
  with a content hash.
- **Autocommit wrapper** wraps the same inner buffer and refuses part *content* files
  (`:539-555`), so the spill lifecycle is not duplicated by a second finalize path.

## Coverage

All 129 `src/Disks/tests/gtest_cas_*` files are deleted in the working tree. Directly relevant coverage at
base `842f2b37b8f`:

- `gtest_cas_blob_hasher.cpp` -- 5 tests: XXH3 streaming vs one-shot vs `blobHashHexOneShot`, CityHash128
  byte-identity with `HashingWriteBuffer`, algo name round-trip, SHA-256 golden vectors and
  streaming/passthrough. Covers the hashing primitive well; says nothing about the spill file.
- `gtest_cas_inline_placement.cpp` -- 2 tests: `ColumnAndMarkFilesStayBlob`,
  `EagerMetadataFilesAreInlineCandidates`. Neither exercises a nested (`<proj>.proj/...`) file name, which is
  exactly the bc2-3 gap.
- `gtest_cas_s3_staging.cpp` -- S3-mode `CaContentWriteBuffer` stream/finalize and cancel-skips-finalize,
  staging promote / adopt / resurrect, `SuccessfulCommitRemovesOrphanedS3StagingObject`, and
  `CASStagingSweeper.RemovesOnlyObjectsUnderGivenMountPrefix` (prefix scoping only -- no concurrent-mount or
  in-flight-object case, the bc2-5 gap).
- Stateless: `04285_cas_deduplication_window_inline_disk`, `04299_cas_projection_inline_disk` -- the latter
  does exercise projections on a CAS disk, but asserts query results only, not memory or scratch behaviour.

Uncovered at base, by inspection: local-scratch space accounting / ENOSPC behaviour and concurrent scratch
pressure (bc2-1); scratch fsync and any read-back verification of the staged body (bc2-2); inline-path
memory ceiling and nested-index classification (bc2-3); failure of the inline-overflow spill write (bc2-4);
retention of S3 staging objects across an aborted transaction plus an unfiltered same-prefix sweep (bc2-5);
local-path fence timing (bc2-6); buffer-count/copy amplification (bc2-7).

Static reasoning only -- nothing was built, run, or checked out.
