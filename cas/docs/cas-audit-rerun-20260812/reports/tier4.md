# tier4 (deep sweep: residual surfaces and blind spots) -- fresh audit 2026-08-12

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is (all CAS tests deleted). Static reasoning only; no build, no run.

## Scope and tier definition

Tier4 is the leftover-surface sweep: everything in the CAS tree that no other angle in this round owns. Region actually walked:

| Region | Files / anchors read |
| --- | --- |
| `Primitives/` | all 10 files (`CasTypes.h`, `CasBlobDigest.{h,cpp}`, `CasBlobHashingWriteBuffer.{h,cpp}`, `CasCodecUtil.h`, `CasXxh3Streamer.h`, `CasEvent.{h,cpp}`, `CasNamespaceLifeId.h`) |
| `Parts/` | `PartPathParser.{h,cpp}` in full; `PartFolderAccess.{h,cpp}` in full (view cache, in-flight dedup, explain journal, drop/rollback paths) |
| `Formats/` residuals | `CasByteBudget.h`, `CasLayout.{h,cpp}`, `CasWireVocab.{h,cpp}`, plus `CasFoldSealFormat.cpp` / `CasRefCatalogFormat.cpp:253-358` for the reservation math |
| Caches | part-folder view cache, dedup cache (`CasPool.cpp:165-213`), manifest decode cache entry points, `MetadataStorages/Cache/MetadataStorageFromCacheObjectStorage.cpp` |
| Instrumentation | all 156 CAS ProfileEvents: declaration set in `src/Common/ProfileEvents.cpp:759-914` vs. every increment site in the CAS tree |
| Blind spots | the 8 listed items, each with an explicit verdict below |
| Build wiring | `src/CMakeLists.txt:130-145` (what of the CAS tree is compiled into `dbms`) |

Cited, not re-derived (sibling-owned): view-cache weight is a constant 256 (`PartFolderAccess.cpp:128-131`); decode-cache token keying prevents warm hits; envelope offset from pool meta; emulated-mode token is filesystem mtime.

## Blind spots addressed

| Blind spot | Verdict | Anchor |
| --- | --- | --- |
| (1) `Mode::EmulatedSingleProcess` auto-selected for local object storage | **Confirmed gap** -- selection is purely `getType() == Local`, there is no config override in either direction, and the only guard against a shared/NFS pool path is a `LOG_INFO`. See tier4-13. | `ContentAddressedMetadataStorage.cpp:509-520` |
| (2) 264 uncalled `*ForTest` seams compiled into production classes | **Not reachable** from any non-test path: zero call sites outside the CAS tree (`rg` over `src/` excluding the CAS dir returns nothing), none is virtual/an override, none is exposed through settings, a `system` verb, or a factory. All fault-injection state is inert because the containers/`std::function`s default to empty. Two residual hazards are real and reported: production-path reads of that state (tier4-9) and one seam that drops a safety gate its production twin enforces (tier4-9). | `CasPool.h:169-427`, `ContentAddressedMetadataStorage.h:236-247`, `ContentAddressedMetadataStorage.cpp:277-283` |
| (3) `CasInspect` decoder completeness | **Confirmed gap** -- 8 of the 18 `FormatId`s have no decoder branch, including `PoolMeta` and `RefCatalog`. See tier4-2. | `Tools/CasInspect.cpp:517-576` vs `Formats/CasFormat.h:24-44` |
| (4) Settings validation coverage | **Partial.** Numeric ranges are effectively unvalidated (only `gc_interval_sec`/`gc_shards` are range-checked); every other `0` is either documented as "unbounded" or clamped at the consumer (`gc_meta_pool_size` -> `std::max(1, ...)` at `Gc/CasGc.cpp:315`), so no confirmed range bug. The confirmed defect is on the *key* side, not the value side: see tier4-5. | `ContentAddressedSettings.cpp:119-137`, `Gc/CasGc.cpp:314-317` |
| (5) Dead code (`ShardReducer` / `manifestCleanupShard`, `CasInMemoryBackend`, format change-point registry) | **Confirmed dead, and compiled into `dbms`.** See tier4-8. | `Gc/CasGcShardPlan.{h,cpp}`, `Backend/CasInMemoryBackend.{h,cpp}`, `Formats/CasFormat.cpp:19-45`, `src/CMakeLists.txt:135-142` |
| (6) Byte-budget reservation math | **Sound.** The fold seal is line-delimited (one JSON object per line, `CasFoldSealFormat.cpp:174-280`), so a per-row reservation measured as `encode(seal_with_1_row) - encode(empty_seal)` is exact per row with no separator underestimate. Widest-row probes saturate every field (`UINT64_MAX`, `UInt128::max`, `shard = gc_shards-1`), and the trailer's growth from 1 to 20 digits is covered exactly by the `digits10 == 19` pad in `foldSealFixedBytes()`. Both `addByteBudget`/`mulByteBudget` saturate instead of wrapping, and `object_cap == 0` is an explicit "disabled" sentinel. | `Formats/CasByteBudget.h:8-26`, `CasRefCatalogFormat.cpp:263-348` |
| (7) `PartPathParser` split cache | **Sound.** 8-slot thread-local round-robin over a pure function; every public entry point takes exactly one `splitCached` reference and never calls `splitCached` again while holding it, so no slot can be evicted under a live reference. `misses` is a diagnostic counter only. | `Parts/PartPathParser.cpp:35-64, 187-244` |
| (8) Read-only / `TruthAbsent` admission matrix | **Sound.** `TruthAbsent` is returned only for `Probe`/`Remove` on a settled-vanished pool; `ContentRead`, `Write` and `Admin` fall through to `throwIfLifecycleTerminal()`, and `TransientNotLive` always throws the retryable error. Read-only is enforced at the single mutating entry point (`createTransaction`) plus every GC verb and the relink receiver, so the two gates compose. The one seam that skips it has no caller (tier4-9). | `ContentAddressedMetadataStorage.cpp:778-816, 846-850, 461, 491, 714, 1596` |

## Findings

### tier4-1 -- 11 of the 156 CAS ProfileEvents can never fire; server-root I/O is counted as GC I/O (Medium)

- **Anchor:** `Backend/CasInstrumentedBackend.cpp:109-122` (`classifyCasNs`), event table `:81-107`, enum `Backend/CasInstrumentedBackend.h:9-17`, keys `Formats/CasLayout.h:208-231`, shipped descriptions `src/Common/ProfileEvents.cpp:844-854`.
- **Trigger:** any mount, heartbeat, epoch bump or lease renewal -- i.e. every CAS pool, always. `classifyCasNs` returns `Blob`, `Root`, `Manifest`, `Root`, `Gc`, `Other`; it never returns `CasNs::Server` (`rg 'CasNs::Server'` over `src/` matches nothing but the enum declaration). Server-root objects live at `<prefix>/gc/server-roots/<id>/{owner,epoch,mount}` (`CasLayout.h:208-231`), which contains `/gc/` and so takes the `Gc` branch at `:119`.
- **Consequence:** `CASServerPut`, `CASServerPutDeduplicated`, `CASServerOverwrite`, `CASServerCompareSwap`, `CASServerCompareSwapConflict`, `CASServerHead`, `CASServerHeadMiss`, `CASServerGet`, `CASServerGetStream`, `CASServerDelete`, `CASServerList` are permanently zero, while owner/epoch/mount traffic inflates the `CASGC*` family. The shipped description of `CASServerHeadMiss` -- "A non-zero value indicates missing server state" -- is an alert an operator can never receive; a lost-lease incident shows up as GC head misses instead.
- **Evidence:** code-only. Shipped `DECLARE`-equivalent description strings in `ProfileEvents.cpp:844-854` establish that a distinct server-object family was intended; the classifier has no branch that produces it.

### tier4-2 -- `cas-inspect` cannot decode 8 of the 18 CAS formats, including pool metadata and the ref catalog (Medium)

- **Anchor:** `Tools/CasInspect.cpp:517-576`; format set `Formats/CasFormat.h:24-44`; key builders `CasLayout.h:157-251`.
- **Trigger:** run `cas-inspect` against `<prefix>/_pool_meta`, `<prefix>/cas/ref_catalog`, `<prefix>/gc/maintenance_state`, `<prefix>/gc/hb`, `<prefix>/gc/server-roots/<id>/owner`, `<prefix>/gc/server-roots/<id>/epoch`, or any `.../outcomes/<round>/<shard>` object. None matches a branch, so control reaches the terminal `throw` at `:573`.
- **Consequence:** the decoder covers `PartManifest`, `RefCkpt`, `RefSnapshot`, `RefLog`, `GcState`, `MountLease`, `FoldSeal`, `RunFile`, `BlobMeta` and the blob envelope, but not `PoolMeta`, `RefCatalog`, `GcMaintenanceState`, `GcOutcomes`, `Owner`, `ServerEpoch`, `GcHeartbeat`, `Roster`. The two most valuable objects in a day-2 incident -- pool identity/generation (`_pool_meta`) and the namespace catalog (`cas/ref_catalog`) -- are exactly the ones the tool refuses, so an operator must fall back to reading raw bytes. The shipped "recognized:" list in the exception at `:574-576` also advertises `retired`, for which no branch exists.
- **Evidence:** code-only; the over-claiming `recognized:` string is itself a shipped string.

### tier4-3 -- part-folder in-flight dedup is keyed by ref only, so a follower can be handed a view for a different manifest than it resolved (Medium)

- **Anchor:** `Parts/PartFolderAccess.cpp:237-252` (`inflight.find(key.cacheKey())`), map declaration `PartFolderAccess.h:189`, caller `PartFolderAccess.cpp:190-214`.
- **Trigger:** two concurrent `getView(key, Freshness::CachedForLoad)` calls on the same ref that straddle a commit/repoint of that ref. Thread A resolves manifest `M1` and becomes leader; thread B resolves `M2` (post-repoint) an instant later, finds A's entry keyed only by `ns\0ref`, and returns `future.get()` -- A's view of `M1`.
- **Consequence:** B reads file sizes, inline bytes and blob references out of the superseded manifest while believing it read `M2`; it then also stores that view under the shared cache key at `:198`, and its audit event at `:213` reports `M2` (`resolved.manifest_id`) although the bytes it served came from `M1`. Reads of a post-repoint part can therefore reference blobs the repoint made unreachable, and the CAS event log and the returned data disagree. Later `getView` calls do catch the staleness (the `manifestId() == resolved->manifest_id` guard at `:162`), so the window is one request per race, not permanent.
- **Evidence:** code-only. The cache-hit path validates the manifest id; the in-flight path is the only view-producing path with no such validation.

### tier4-4 -- dedup-savings counters are incremented before admission, then the body is uploaded anyway (Medium)

- **Anchor:** `Pool/CasPartWriteTxn.cpp:155-175` (`CASBlobHeadFirst` `:155`, `CASBlobBodyPutAvoided` `:159`, `CASBlobDeduplicationCacheHit` `:161`, `observeAndAdmit` `:164`, swallowed `ABORTED` `:169-173`, real upload `:178-191`).
- **Trigger:** head-first path where the HEAD proves the blob exists but `observeAndAdmit` throws `ABORTED` (the object is not admissible as evidence -- e.g. condemned or otherwise untrusted, requiring resurrection). The `catch` swallows `ABORTED` and falls through to `uploadFromSource`.
- **Consequence:** `CASBlobBodyPutAvoided` counts a body PUT that was *not* avoided, and `CASBlobDeduplicationCacheHit` counts a dedup hit that did not dedup -- while the same call also increments the real `CASBlobPut`/conditional-write events. Any "bytes saved by deduplication" figure computed from these events over-reports exactly in the condemned-blob case, which is the case an operator would be investigating.
- **Evidence:** code-only. The correct branch already exists and is used for the return value (`BlobUploadOutcome::DeduplicationCacheHit` is set only after admission succeeds at `:167`); the counters are simply raised earlier.

### tier4-5 -- the non-CAS config key allowlist is a fixed 18-entry set, so legitimate object-storage keys make the disk fail to load (Medium)

- **Anchor:** `ContentAddressedSettings.cpp:23-27` (`non_cas_keys`), loop `:94-99`.
- **Trigger:** declare a `content_addressed` disk over S3 and add any object-storage option outside the 18-entry allowlist -- e.g. `<connect_timeout_ms>`, `<max_connections>`, `<request_timeout_ms>`, `<server_side_encryption_customer_key_base64>`, `<skip_access_check>`-adjacent S3 keys, `<support_batch_delete>`. The key is not in `non_cas_keys`, so it is passed to `impl->set(key, ...)`, which throws for an unknown setting.
- **Consequence:** disk configuration is rejected at load with an "unknown setting" error naming a perfectly valid S3 option. The allowlist enumerates only the handful of keys the authors happened to use; every other object-storage knob is a landmine, and the failure mode is a server that will not start rather than a warning.
- **Evidence:** code-only. Note the same mechanism is what usefully catches CAS-setting typos -- the defect is that the two key spaces are separated by an enumeration of one of them rather than by asking the object-storage layer.

### tier4-6 -- part-folder view cache counters double-count and mix units (Low)

- **Anchor:** `Parts/PartFolderAccess.cpp:164-214`, `:271-278` (`eraseView`), `:564-573` (`dropNamespace`).
- **Trigger:** any `getView` that is not a cache hit; any `dropRef`/`promote` on a disk with `part_folder_cache_bytes = 0`.
- **Consequence:** (a) `CASPartFolderViewMisses` at `:207` is incremented on *every* non-hit path, so a validation mismatch also counts as a miss (`:168` then `:207`), an oversized bypass counts as both `CASPartFolderViewOversizedBypasses` and a miss (`:204` then `:207`), and `ForceFresh`/`StrictValidate` reads -- which either bypass the cache or never consult it -- are counted as misses too. `hits/(hits+misses)` therefore understates the cache. (b) `CASPartFolderViewInvalidations` at `:276` is incremented even when `view_cache` is null and even when nothing was cached, and it counts *one* invalidation for a whole-namespace purge at `:572` versus one per key at `:276` -- the same counter with two different units.
- **Evidence:** code-only; observability impact only, no correctness effect.

### tier4-7 -- the deferred `RefResolve` audit event is dropped on load-side cache hits only (Low)

- **Anchor:** `Parts/PartFolderAccess.cpp:152` (`ResolveAudit::Deferred`), hit-return `:164-166`, emit sites `:184` and `:213`.
- **Trigger:** any `getView(key, Freshness::CachedForLoad)` that hits the view cache.
- **Consequence:** the resolve is audited with `Deferred` (suppressing the emission inside `Pool::resolveRef`) and then never emitted, whereas the `ForceFresh` hit path (`:184`) and every miss path (`:213`) do emit. The CAS event log therefore contains `RefResolve` records for cold and force-fresh reads only, so an operator correlating reads against resolves in `ca_event_log` sees gaps proportional to cache hit rate.
- **Evidence:** code-only. Every other outcome of the same function emits; this is the single path where the deferral is never redeemed.

### tier4-8 -- three dead surfaces are compiled into the production binary (Low)

- **Anchor:** `Gc/CasGcShardPlan.h:24-40` / `.cpp:17-38` (`manifestCleanupShard`, `ShardReducer::{ctor,owns,reduce}`); `Backend/CasInMemoryBackend.{h,cpp}` (28 methods incl. `failNextCasPut`, `injectAmbiguousPutIfAbsent`, `setHoldDeletes`, `landPendingDelete`); `Formats/CasFormat.h:52-58` / `.cpp:19-45` (`FormatChangePoint`, `changePoints(FormatId)`); build wiring `src/CMakeLists.txt:135-142`.
- **Trigger:** none -- that is the finding. `rg` for each symbol across `src/` finds only its own declaration and definition; `add_headers_and_sources` pulls `Backend/`, `Gc/` and `Formats/` wholesale into `dbms`, so all of it links into `clickhouse-server`.
- **Consequence:** `ShardReducer::reduce` is a full blob-target reduction implementation with no caller, so the sharded-reducer design point is unexercised and unexercisable; `InMemoryBackend` puts a `Backend` implementation with deliberate fault injectors (`injectAmbiguousPutIfAbsent`, `failNextCasPut`, `setEnforceTokens(false)`) in the server binary with no production consumer; `changePoints()` means the per-format change-point table -- the one structure that would let a reader reason about which generation introduced a wire change -- is data with no consumer, so `checkCompatibility` cannot be using it. Each is a maintenance trap: it reads as live design but nothing constrains it to stay correct.
- **Evidence:** code-only.

### tier4-9 -- production paths read and mutate test-only state, and one test seam drops a gate its production twin enforces (Low)

- **Anchor:** `Pool/CasRefCatalog.cpp:147` (file-scope `std::function<void()> create_namespace_step1_pre_read_hook_for_test;`), read+swap at `:152-156`, setter `:504`; `ContentAddressedMetadataStorage.h:236-247` (`shouldFailPromoteForTest`, `runAfterPromoteHookForTest`) invoked on the commit path at `ContentAddressedTransaction.cpp:276, 282, 301, 307`; `ContentAddressedMetadataStorage.cpp:277-283` (`runOneGcRoundForTest`) vs `:461-465` (`runGcRoundNow`).
- **Trigger:** (a) every namespace creation reads an unsynchronized process-global `std::function` -- unlike its sibling hooks it is not per-instance, so it would fire for an unrelated disk in the same server, and the `std::swap` at `:155` is racy against the setter. (b) every part commit calls `shouldFailPromoteForTest` and `runAfterPromoteHookForTest`, the latter *erasing* from a shared `std::unordered_map` member with no mutex, from arbitrary commit threads. (c) `runOneGcRoundForTest` runs a real mutating GC round and, unlike `runGcRoundNow`, omits both `checkNotReadOnly("GC round")` and the `gc_enabled` check.
- **Consequence:** benign today only because the containers are empty and nothing calls the seam -- an empty-map `find` is a safe concurrent read and the null `std::function` check never swaps. The residual risk is structural: a read-only CAS disk has a compiled-in method that performs writes, and the commit hot path is one non-empty map away from an unsynchronized `erase` race.
- **Evidence:** code-only.

### tier4-10 -- `Xxh3Streamer` dereferences a null state in its constructor, making the allocation-failure path dead (Low)

- **Anchor:** `Primitives/CasXxh3Streamer.h:17` (`Xxh3Streamer() : state(XXH3_createState()) { XXH3_128bits_reset(state); }`), `valid()` at `:24`, guard at `Primitives/CasBlobHashingWriteBuffer.cpp:87-88`.
- **Trigger:** `XXH3_createState()` returns null under memory pressure. The constructor immediately calls `XXH3_128bits_reset(state)`, which writes through the pointer, so the process faults before `Xxh3128BlobHashingWriteBuffer` ever reaches its `if (!state.valid())` check.
- **Consequence:** the `CANNOT_ALLOCATE_MEMORY` exception with its message "failed to allocate the xxh3 streaming state" is unreachable -- an OOM while opening an `xxh3` blob write becomes a segfault instead of a clean, retryable exception. Only affects pools configured with `blob_hash = xxh3-128`.
- **Evidence:** code-only; the guard's existence at `:87-88` is itself the evidence that a clean failure was intended.

### tier4-11 -- `cas-inspect` key dispatch falls through from the namespace-state branch and mis-decodes namespace files (Low)

- **Anchor:** `Tools/CasInspect.cpp:532-536` (branch returns *only* when `parseRefCkptKey` matches), `:558-559` (`ends_with("/mount")`), `:561-562` (`ends_with("/fold_seal")`).
- **Trigger:** inspect a namespace file key `<prefix>/cas/ns/state/<life>/_files/<name>` whose name ends in `mount` or `fold_seal` -- a table-level file the CAS layer stores verbatim under `_files/`.
- **Consequence:** the `namespaceStateRootPrefix()` branch is entered, `parseRefCkptKey` fails, and control falls through to the suffix-matching branches, so an arbitrary namespace file is decoded as a mount lease or a fold seal. The result is either a confidently wrong render or a `CORRUPTED_DATA` exception blamed on a healthy object -- both actively misleading during an incident.
- **Evidence:** code-only. The suffix tests at `:558` and `:561` are unanchored `ends_with` checks, whereas every other branch anchors on a layout prefix.

### tier4-12 -- `checkConditionalWriteSingleAttemptSupport` is Native-only and read-only mounts never reach it (Low)

- **Anchor:** `Backend/CasObjectStorageBackend.cpp:78-91`; mode selection `ContentAddressedMetadataStorage.cpp:509-511`.
- **Trigger:** a `content_addressed` disk over a non-Local, non-S3 object storage (e.g. Azure, HDFS): the type test at `:509` yields `Native`, but the storage cannot honour the `SingleAttempt` retry profile. The shipped message says "refusing to mount writable", and the check is only invoked on the writable path.
- **Consequence:** the refusal is correct for writable mounts, but a read-only mount of the same disk proceeds in `Native` mode and will interpret whatever the storage returns as ETag tokens. The failure is deferred from mount time to first conditional read/validation instead of being reported at configuration time.
- **Evidence:** code-only; the "should use EmulatedSingleProcess" advice in the shipped message at `:90` has no configuration expression -- see tier4-13.

### tier4-13 -- emulated single-process mode is chosen by storage type alone, with no override and only an INFO-level warning (Medium)

- **Anchor:** `ContentAddressedMetadataStorage.cpp:509-520`; the 29-setting list in `ContentAddressedSettings.cpp:29-59` contains no mode setting.
- **Trigger:** point two ClickHouse servers at one CAS pool over a `local` object storage whose path is a shared mount (NFS, a shared block device, a container bind-mount of the same host directory). Both servers independently select `EmulatedSingleProcess`, whose conditional operations are in-process only.
- **Consequence:** the CAS conditional-write and GC fencing invariants are enforced per process, so two servers can both "win" the same compare-and-swap; nothing detects it, and the code's own shipped log line says the invariants "would break silently". The only mitigation is that `LOG_INFO`, which is below most production log thresholds and is emitted once per pool view open. There is also no way to express the inverse -- the message at `CasObjectStorageBackend.cpp:90` advises "a non-S3 object storage should use EmulatedSingleProcess", but no setting can request it.
- **Evidence:** code-only; both the warning text at `:517-520` and the advice at `CasObjectStorageBackend.cpp:90` are shipped strings and establish that operators are expected to make this choice -- while the code makes it for them from `ObjectStorageType`.

## Checked and sound

| Surface | Why it is sound |
| --- | --- |
| ProfileEvents inventory | All 156 declared `CAS*` events have at least one increment site in the CAS tree; no orphan declarations. Increments in `InstrumentedBackend` all run *after* the inner call returns, so a throwing operation is never counted -- an undercount on failure, never a double count. |
| `putIfAbsent` / `casPut` / `head` branch selection | `PutOutcome` has exactly `{Done, PreconditionFailed}` and `CasOutcome` exactly `{Committed, Conflict}` (`Backend/CasBackend.h:56-66`), so the binary `? :` mappings at `CasInstrumentedBackend.h:81, 99, 74` are exhaustive and on the correct branch. (`putOverwrite` mapping a failed overwrite to `...CompareSwapConflict` at `:91` is a naming compromise, not a wrong branch.) |
| Fold-seal / catalog reservation math | See blind spot (6): exact per-row deltas on a line-delimited format, saturating arithmetic, saturated widest-row probes, trailer growth covered by the `digits10` pad. |
| `PartPathParser` split cache | See blind spot (7): pure function, no reference outlives a second lookup. |
| `DigestCodec` | Constructor asserts 16-or-32-byte width; `fromHex`/`fromBytesBE` validate length *and* every hex character before writing; `toHex`/`toBytesBE` assert the tail beyond `len` is zero, so a 16-byte digest can never leak 32-byte garbage. `shardOf` reads the first 8 bytes big-endian, well inside both widths. |
| `CasCodecUtil` canonical-name checks | `isCanonicalRefName` rejects empty, `\0`, `\`, empty segments (hence leading/trailing/doubled `/`), `.` and `..`; `checkManifestRef` enforces nonzero epoch/build and the ordinal range. `readFixedBytes` bounds against `in.available()`, which is exact for its only two callers (`CasPartManifestFormat.cpp:253-254`), both of which decode from a fully-buffered in-memory reader. |
| `CasWireVocab` | Every `*ToWord` has a `throw` after an exhaustive `switch` (so a corrupt enum cannot silently render), every `*FromWord` rejects unknown words with `CORRUPTED_DATA`, and `manifestRefFromFields` range-checks the ordinal before the narrowing `static_cast<uint32_t>`. |
| `CasLayout` key parsers | `parseBlobKey` cross-checks the shard directory against the first two hex digits and the hex length against the algorithm's digest width; `parseBlobTargetRunKey` requires canonical (no leading-zero) integers and literal `attempt`/`blob_target` segments; `checkNamespace` reserves `_files` and `_manifests`. Optional-vs-zero is handled correctly throughout (`if (!shard)` tests engagement, not the value). |
| Dedup cache recency | `CacheBase::contains` deliberately does not touch LRU recency (`LRUCachePolicy.h:151-154`), but `Pool::dedupCacheAdd` is called on the dedup-hit path (`CasPartWriteTxn.cpp:165`) as well as after a real upload (`:183`), and `set` on an existing key refreshes the entry -- so the cache does retain a reuse signal. Weight is a flat 64 bytes per `DedupPresent`, which is the honest cost of a presence bit. |
| `part_folder_validate` parsing and clock use | `always`/`never`/`age <n>` is fully validated with a shipped error listing the accepted forms; `age 0` degenerates to `always` plus one wasted lookup, not to "never validate". The freshness comparison `now_ms_fn() - validatedAtMs()` is unsigned, so a backward wall-clock step yields a huge value and forces *more* validation -- it fails safe in both directions. |
| `gc_meta_pool_size` | A configured `0` is clamped to 1 at `Gc/CasGc.cpp:315`, and `scheduleMetaJob` falls back to inline execution if scheduling throws, so the advisory meta pool cannot wedge a round. |
| `benchmarks/` | `benchmark_cas_ref_protocol.cpp` is behind `if (ENABLE_BENCHMARKS)` (`src/CMakeLists.txt:143-145`) and is not part of `dbms`; it links `dbms` rather than duplicating CAS logic, so it cannot drift into being a second implementation. |
| `MetadataStorageFromCacheObjectStorage` | Pure delegation for every CAS-relevant predicate, including `isContentAddressed()` at `:172-175`; it adds no metadata caching of its own in front of CAS, so a cached-object-storage wrapper cannot serve stale CAS metadata. |
| Admission matrix | See blind spot (8). |

## Coverage

| Item | Status |
| --- | --- |
| `Primitives/` (10 files, ~1.1 kLoC) | read in full |
| `Parts/PartPathParser.{h,cpp}`, `Parts/PartFolderAccess.{h,cpp}` (~1.2 kLoC) | read in full |
| `Formats/CasByteBudget.h`, `CasLayout.{h,cpp}`, `CasWireVocab.{h,cpp}` | read in full |
| `Formats/CasFoldSealFormat.cpp`, `CasRefCatalogFormat.cpp:230-358` | read for the reservation math |
| `Backend/CasInstrumentedBackend.{h,cpp}`, `CasObjectStorageBackend.cpp:30-170` | read in full / mode + precondition region |
| `Tools/CasInspect.cpp:460-577` | read (dispatch + run rendering) |
| `ContentAddressedSettings.cpp` | read in full |
| `ContentAddressedMetadataStorage.cpp` | read at `:240-290`, `:460-570`, `:770-856` |
| `Pool/CasPartWriteTxn.cpp:130-220`, `Pool/CasPool.cpp:160-215`, `Pool/CasRefCatalog.cpp:140-170` | read (upload/dedup/hook regions) |
| 156 CAS ProfileEvents | declaration set diffed against all increment sites tree-wide |
| `*ForTest` seams | all call sites and setters enumerated tree-wide; cross-checked for external references over all of `src/` |
| Dead-code candidates | each symbol grepped over all of `src/`; build inclusion confirmed in `src/CMakeLists.txt` |
| Not walked (sibling-owned) | `Gc/*` round protocol, `Pool/CasRefLedger.cpp` recovery/wedge logic, envelope/manifest decode internals, GC shard planning semantics, decode-cache token keying |

Findings: 13 (0 High, 6 Medium, 7 Low). Method: static reading and grep only -- no build, no execution, no checkout.
