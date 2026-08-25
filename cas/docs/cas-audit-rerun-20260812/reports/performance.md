# performance -- fresh audit 2026-08-12

## Scope

Static audit of CPU, memory-copy and algorithmic efficiency of the CAS implementation itself.
Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base
`842f2b37b8f`, working tree as-is. CAS root
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` (all paths below are relative to
it unless stated otherwise). Code-only: comments and `docs/**` carry no weight; shipped defaults
from `ContentAddressedSettings.cpp` and `programs/server/config.xml` do.

Covered: hot-path complexity (ref resolution, manifest lookup, staging maps, dedup lookup, GC
in-degree fold, catalog ops), large-buffer/string copies, allocation churn per file and per
request, cache key shape / weighting / single-flight, NDJSON serialization cost per operation,
hashing count, per-file vs per-part scaling, the `benchmarks/` directory, ProfileEvents and audit
event overhead, and O(pool size) work on per-op paths.

Not covered here (owned by siblings, cited not duplicated): request-count and memory-ceiling
analysis (**ad5**), lock hold times and blocking I/O under locks (**bc7**). Cited as established
elsewhere and not re-argued: 4C+11 object-store requests per part commit with the `.meta` sidecar
being half the PUTs; the 16-thread process-global upload pool; `DataPartsLock` held across
publish; the ~42 commits/s ref-object cleanup ceiling; the view-cache weight constant; and the
payload-digest re-encode on every manifest decode.

Sanity note on where CPU actually matters: for an S3-backed pool a part commit costs 4C+11
round trips (tens to hundreds of ms), so per-part *text* handling (~100-200 us, quantified in
performance-8) is under 1% of commit latency. The findings ordered High below are the ones whose
cost is **not** bounded by per-part work: they scale with the size of the whole namespace (R
refs) or the whole pool (E edges), and they run on single-threaded background lanes.

## Hot-path complexity table

| operation | complexity | dominant cost | anchor |
| --- | --- | --- | --- |
| resolve ref -> part folder view (view-cache hit) | O(log R) + O(1) allocs | `resolve()` before the cache probe, `cacheKey()` String, audit event build | `Parts/PartFolderAccess.cpp:150-170` |
| file lookup inside a part (`existsFile`/`getFileSize`) | O(log F) binary search | `getView()` on every call | `Formats/CasPartManifestFormat.cpp:291-298` |
| manifest read, decode-cache **hit** | 1 HEAD round trip + O(1) | unconditional `backend.head()` before the cache probe | `Pool/CasManifestReader.cpp:56-78` |
| manifest read, decode-cache miss | O(F) parse + zstd inflate + full-buffer copy | ~12-16 allocations per entry, byte-at-a-time line reads | `Formats/CasTextFormat.cpp:271-286`, `373-381` |
| stage one file into a write txn | O(F) linear scan -> **O(F^2)** per part | `std::erase_if` over an unsorted `entries` vector per file | `ContentAddressedTransaction.cpp:510,652,810,827,930,1051,1064,1076` |
| `admits()` budget pre-check (release) | O(P) state copy + O(1) budget | `std::set` precommit deep copy; 2 throwaway row encodes per op | `Pool/CasRefProtocol.cpp:517-525`, `500-505` |
| `admits()` / `applyRefLogTxn` (sanitizer build) | **O(R)** per call | `debugAssertBodyCounters()` re-encodes every row | `Pool/CasRefProtocol.cpp:362-386,413-415,520-522` |
| apply one ref-log txn | O(P) + 2 throwaway encodes per op | encode-a-row-to-measure-its-length | `Pool/CasRefProtocol.cpp:215,227,242,254,263,283-286` |
| ref snapshot publish | **O(R)** every 256 txns -> O(R^2/256) cumulative | full-table NDJSON encode + zstd-3 + PUT | `Pool/CasRefLedger.cpp:2741-2745,2964,3000` |
| recover a namespace from a snapshot | 3x O(R) serialize/deserialize + 2R throwaway encodes | `stateFromSnapshot` encodes then decodes before use | `Pool/CasRefProtocol.cpp:331-360` |
| GC in-degree fold round | **O(E)** regardless of delta count D | re-read + re-write every edge; whole run materialized then copied | `Gc/CasBlobInDegree.cpp:484-555`, `345`, `549-552` |
| `zeroInDegree` scan | O(E), 2 String allocs per row | run decode | `Gc/CasBlobInDegree.cpp:557-572` |
| catalog namespace op | O(N) find + O(N) deep copy + full re-encode | `find_if` on a vector kept sorted by `lower_bound` | `Pool/CasRefCatalog.cpp:139-143,161-167` |
| dedup presence check | O(1) hash; 1 malloc per insert | `make_shared` of an empty struct | `Pool/CasPool.cpp:196-213` |
| every backend request | O(len(key)) x up to 5 | substring searches for metric bucketing | `Backend/CasInstrumentedBackend.cpp:109-121` |
| every audit event | O(1) with ~10 allocations, one global mutex | `CasEvent` build + single per-pool dispatcher mutex | `Pool/CasEventDispatcher.cpp:17-44` |

R = committed refs in a namespace (parts). F = files in a part. P = in-flight precommits.
E = (blob, source) edges in the pool. N = namespaces. C = columns/files per part.

## Findings

### performance-1 -- GC in-degree fold is O(all edges) per round, not O(changed edges) (High)

- **Anchor:** `Gc/CasBlobInDegree.cpp:484-555`; run buffer `345`; materialize-and-copy `549-552`;
  per-row decode `207-230`; prior cursor `54-102`.
- **Complexity:** O(E) reads + O(E) writes + O(E) allocations per fold round, independent of the
  number of edges that actually changed (D). The merge at `484` walks the union of the prior run
  cursor, the sorted deltas, and the retirements, and `writer.append` at `541` re-emits every
  still-active edge into a brand new run object; the whole new run is accumulated in a
  `WriteBufferFromOwnString` (`345`) and then copied again into `const String run_bytes = out.str()`
  (`549`), checksummed with a second full scan (`550`), and PUT whole (`552`).
- **Magnitude:** one edge exists per (blob, referencing part) pair, i.e. roughly per file per
  part. A 100k-part pool with 100 files per part is ~10M edges; at the ~37-byte record the run is
  ~370 MB, so each round rewrites and re-uploads ~370 MB and materializes it twice in RAM, even if
  a single edge changed since the previous round. Per iteration the loop performs 4-5 String
  constructions (see performance-9), so ~40-50M allocations per round. With the shipped
  `gc_interval_sec = 60` and `gc_shards = 1` (`ContentAddressedSettings.cpp:32,39`) that is one
  single-threaded lane sustaining ~6 MB/s of PUT and multiple seconds of pure allocator time
  every minute, growing linearly with pool size. Cross-reference ad5 for the memory ceiling of
  holding two copies of the run.
- **Trigger:** any pool large enough that E dwarfs D, which is the steady state of every
  long-lived pool: the fold cost is set by total pool size, while the useful work is set by the
  churn since the last round.
- **Evidence:** `gc_shards` defaults to 1 and is creation-time only
  (`ContentAddressedSettings.cpp:39`), so the fold cannot be widened after the fact on an existing
  pool; there is no delta/tiered run layout in the writer -- `emitRun` always writes a single
  complete run per shard (`551`, `.../0` ordinal) and the graduation/redelete budgets
  (`gc_round_graduation_budget`, `gc_round_redelete_budget`, both 5000) bound the *decision*
  cohort per round but not the fold scan.

### performance-2 -- Ref snapshot re-encodes the whole namespace every 256 transactions (High)

- **Anchor:** thresholds `Pool/CasRefProtocol.h:120-121` (`snapshot_log_count_threshold = 256`,
  `snapshot_log_bytes_threshold = 1 MiB`), decision `Pool/CasRefLedger.cpp:2741-2745`, state copy
  `2964`, encode + seal `3000`, encoder `Formats/CasRefSnapshotFormat.cpp:115-135`.
- **Complexity:** O(R) NDJSON encode plus zstd-3 compression plus a full-object PUT per snapshot,
  fired every 256 committed transactions or 1 MiB of tail -- a cadence that does not depend on R.
  Cumulative cost of filling a namespace to R refs is therefore O(R^2 / 256).
- **Magnitude:** a committed row is
  `{"k":"c","rn":"<part name>","me":"..","mb":"..","mo":N,"ts":N}` -- about 130 bytes for a
  realistic part name. At R = 100k refs the snapshot body is ~13 MB of text per publish, i.e.
  ~52 KB of encode per commit against ~300 bytes of actual log content: roughly 170x write
  amplification, and ~2x that at the 480k-row ceiling implied by
  `ref_snapshot_max_bytes = ref_removal_max_bytes = 64 MiB`
  (`Formats/CasRefSnapshotFormat.h:40`, `Formats/CasRefLogFormat.h:50`). Encoding is not vectorized
  -- each row costs ~10 `writeKey`/`writeStringValue` calls plus two canonical-name validations
  (`Formats/CasRefSnapshotFormat.cpp:53-67`) -- so a 32 MB snapshot is tens of ms of encode plus
  zstd-3 over 32 MB, on the publish lane, every 256 commits.
- **Trigger:** a namespace with many live parts under steady insert traffic. Worst at high R with
  small transactions, which is exactly the normal insert pattern.
- **Evidence:** there is no delta or tiered snapshot -- `publishSnapshot` always encodes the
  entire captured state (`3000`), and the tail thresholds are absolute constants rather than a
  function of `getCommitted().size()`. `candidate_state = rt->state` at `2964` copies the state
  under the state mutex first (cheap for `committed` thanks to `RefCowMap`, O(P) for the
  `std::set` precommits).

### performance-3 -- Row byte counts are obtained by fully re-serializing the row (Medium)

- **Anchor:** `Formats/CasRefSnapshotFormat.cpp:259-271` (`committedRowEncodedSize`,
  `precommitRowEncodedSize`), `Formats/CasRefLogFormat.cpp:376-385` (`removalOpEncodedSize`),
  callers `Pool/CasRefProtocol.cpp:215,227,242,254,263,283-286,345-346,355-356`, writer
  `Formats/CasTextFormat.h:19-22`.
- **Complexity:** O(len(row)) with a guaranteed heap allocation per call --
  `CasJsonWriter(256)` does `buf.reserve(256)` -- and every state mutation performs two of them
  (snapshot-size delta plus removal-size delta). `stateFromSnapshot` performs 2R of them
  (`345-346`, `355-356`) on top of encoding and then decoding the entire snapshot before using it
  (`333-334`), so installing a snapshot serializes the table three times.
- **Magnitude:** on the publish path this is small in absolute terms (a handful of us per txn),
  but it is pure waste: the byte count of a row whose fields are all in hand is computable
  arithmetically, and the encode additionally re-runs `checkCanonicalRefName` and
  `checkManifestRef` per call. On the recovery path at R = 100k this is 200k throwaway
  `CasJsonWriter` allocations plus a 13 MB encode and a 13 MB parse of a snapshot that was
  already in memory as a typed object.
- **Trigger:** every ref publish/drop/repoint (2 encodes per op) and every namespace recovery or
  remount (2R encodes plus a triple serialization).
- **Evidence:** `RefTableState` already maintains `snapshot_body_bytes` and `removal_body_bytes`
  incrementally, so the intent is clearly to avoid O(R) recomputation -- but each incremental
  update itself pays a full row encode, and `debugAssertBodyCounters` (performance-4) recomputes
  the whole thing anyway in sanitizer builds.

### performance-4 -- Sanitizer builds turn every txn apply and every admits() into an O(R) re-encode (Medium)

- **Anchor:** `Pool/CasRefProtocol.cpp:362-386` (`debugAssertBodyCounters`), called at `413-415`
  (`applyRefLogTxn`) and `520-522` (`admits`, on the scratch copy).
- **Complexity:** O(R) per call with 2R `CasJsonWriter` allocations, converting an O(P) publish
  step into an O(R) one. `admits()` is called per candidate op, so a batch of k ops costs O(kR).
- **Magnitude:** at R = 10k refs one `admits()` call performs ~20k throwaway row encodes; under
  ASan/TSan allocation costs are several times higher, putting a single budget pre-check in the
  multi-millisecond range and making publish throughput fall roughly linearly with namespace
  size. Note the loop at `368` also copies each map value: `for (const auto [name, row] :
  committed)` binds by value, so every iteration copies a `RefCommittedRow` including its
  `ref_name` String.
- **Trigger:** any sanitizer or debug build, which is where soak and correctness runs execute. All
  CAS tests are deleted in this working tree, so nothing currently exercises or measures this.
- **Evidence:** guarded by `DEBUG_OR_SANITIZER_BUILD`, so release builds are unaffected -- this is
  a test-throughput and timing-fidelity issue, not a production one, but it silently changes the
  interleavings a sanitizer soak can reach.

### performance-5 -- Staging entry list is an unsorted vector scanned linearly per file (Medium)

- **Anchor:** `ContentAddressedTransaction.cpp:510` (`writeFile` blob),
  `652` (inline), `810` and `827` (hardlink/copy), `930` (`moveDirectory`), `1051` and `1064`
  (`moveFile`/`replaceFile`), `1076-1078` (`unlinkFile`, an `any_of` immediately followed by an
  `erase_if` over the same predicate).
- **Complexity:** each staged file does an O(F) `std::erase_if` with a String comparison per
  element, so staging F files is O(F^2) comparisons; `unlinkFile` walks the vector twice.
- **Magnitude:** at F = 100 (a normal part) this is ~5k comparisons -- irrelevant. At F = 1000
  (wide tables, many projections, or a `moveDirectory` merging two large staging sets) it is ~500k
  String comparisons per part, single-digit milliseconds of CPU inside the transaction. The
  asymmetry is the point: the *read* side of the very same data is a proper binary search over a
  sorted vector (`Formats/CasPartManifestFormat.cpp:291-298`), and the encoder sorts the entries
  anyway (`Formats/CasPartManifestFormat.cpp:73-81`), so keeping the staging vector sorted (or
  indexing it by path) would remove the quadratic term for free.
- **Trigger:** parts with many files -- wide tables, many projections/secondary indices -- and
  `moveDirectory`, which re-scans the destination staging set once per source entry.
- **Evidence:** cost here scales with file count where the operation is logically per part; see
  performance-8 for the same per-file-vs-per-part pattern in the text formats.

### performance-6 -- Manifest decode cache cannot serve a read without a network round trip (Medium)

- **Anchor:** `Pool/CasManifestReader.cpp:56-78` -- `backend.head(key)` at `58`, cache probe at
  `76-78`; cache key includes the freshness token (`ManifestCacheKey{.manifest_id, .token}`,
  hash at `43-52`). View-side equivalent: `Parts/PartFolderAccess.cpp:152` calls `resolve()`
  before the view-cache probe at `158-170`.
- **Complexity:** O(1) CPU, but a mandatory one-RTT HEAD per manifest read regardless of cache
  state. The default `manifest_decode_cache_bytes = 128 MiB`
  (`ContentAddressedSettings.cpp:56`) therefore buys back the GET and the parse, never the
  latency.
- **Magnitude:** ~10-30 ms of S3 RTT per manifest read on a decode-cache hit. This is invisible
  when the *view* cache hits (`getView` returns at `166` before `buildView`), so the exposure is
  the window where the view cache has evicted an entry (`part_folder_cache_bytes = 64 MiB`,
  `part_folder_cache_max_entries = 10000`) but the manifest cache still holds the body -- i.e.
  precisely the large-table case the 128 MiB manifest budget exists to serve. Two refs sharing one
  manifest hit the same path.
- **Trigger:** more than 10k live part folders per disk, or a working set above 64 MiB of views,
  with manifests still resident in the 128 MiB decode cache.
- **Evidence:** the token-in-key design is what forces the HEAD, so this is a cache *key shape*
  cost, not an oversight: coherence is bought with a round trip on every hit. Request-count
  accounting for this HEAD belongs to ad5; the point here is that the second-tier cache's byte
  budget cannot translate into latency savings.

### performance-7 -- Audit events are built and funneled through one mutex on read/write hot paths, and the shipped config enables the sink by default (Medium)

- **Anchor:** `Pool/CasEventDispatcher.cpp:17-44` (single `std::mutex`, inline drain),
  gate `Primitives/CasEvent.h:55-63` (`hasEventSink()` only), event struct
  `Primitives/CasEvent.h:31-45` (7 Strings plus a `std::map<String, String> detail`), emitters on
  hot paths `Parts/PartFolderAccess.cpp:217-229` (every resolve),
  `Pool/CasManifestReader.cpp:61-71`, `Gc/CasGc.cpp:1297-1313` (per candidate blob), shipped
  default `programs/server/config.xml:1198-1207` (`<cas_log>` present and enabled).
- **Complexity:** O(1) per event, but with ~8-10 heap allocations (Strings plus red-black-tree
  nodes for `detail`) and a single per-pool mutex that every emitting thread must acquire; the
  first thread in also drains the queue inline, running the sink (a system-table insert) on
  whichever request thread happened to arrive.
- **Magnitude:** ~1-3 us per event uncontended and a hard serialization point under concurrency:
  every ref resolve on the read path and every blob put / precommit / GC observation on the write
  path passes through one lock. The gate is only "is a sink installed", not "is a log configured",
  so on a server with the shipped `config.xml` the full event is constructed for every operation.
- **Trigger:** normal read and write traffic on any server using the shipped config; worst with
  many concurrent part loads against one pool.
- **Evidence:** `EventEmitter::emit` checks `store.hasEventSink()` before building, which shows
  the intent to make the cost zero when auditing is off -- but the shipped `config.xml` declares
  `cas_log`, so the "off" path is not the default. Contrast the ProfileEvents path, which is a
  table lookup and an atomic increment (`Backend/CasInstrumentedBackend.cpp:81-127`) and is cheap.

### performance-8 -- NDJSON decode allocates per line and per key; per-part cost quantified (Low)

- **Anchor:** `Formats/CasTextFormat.cpp:271-286` (`readLine`: byte-at-a-time `push_back`, no
  `reserve`), `138-169` (`JsonObjectReader::nextKey`: linear `std::find` over `seen_keys` plus a
  String copy per key at `166`), `373-381` (`openObject` copies the whole object even when it is
  stored uncompressed), manifest decode loop `Formats/CasPartManifestFormat.cpp:116-160`.
- **Complexity:** O(bytes) with ~12-16 allocations per record: one line String grown by
  doubling (~3 reallocations for a 140-byte line), up to 6 `seen_keys` String copies plus vector
  growth, and the field Strings. `nextKey`'s duplicate check is O(k^2) in keys per object, but
  k <= 6 here so it is a constant, not a scaling risk.
- **Magnitude, per part:** a `blob`-placement entry line is
  `{"p":"<path>","pm":"blob",<blob ref fields>,"sz":N}`, roughly 95-140 bytes. A 100-file manifest
  is ~12-15 KB of text; decoding it costs ~1400 allocations and ~50-60 us, and the write path
  encodes the same buffer three times per commit (twice in `stageManifest`, once more when
  `promote` re-decodes and re-validates the digest -- the digest re-encode itself is the sibling
  finding, cited) plus one zstd seal. Total ~150-250 us of CPU per part commit for text handling,
  which is under 1% of a 4C+11-request commit against S3 but becomes the dominant cost for
  local/in-memory object stores. Inline entries append their full bodies into the manifest
  (`Formats/CasPartManifestFormat.cpp:102-111`), so a part with many small files pays this over
  the summed file contents, not over the entry count.
- **Magnitude, per namespace:** the same per-line cost applied to a snapshot of R rows
  (`Formats/CasRefSnapshotFormat.cpp:179-246`) is ~16 allocations per row -- ~1.6M allocations to
  decode a 100k-ref snapshot, ~8M at the 480k-row cap. This is the decode half of performance-2.
- **Trigger:** every manifest decode and every snapshot decode; severity rises with R, not with F.
- **Evidence:** the encode side reserves properly (`CasJsonWriter(256 + 128 * rows)`,
  `Formats/CasRefSnapshotFormat.cpp:119`), which shows the sizing discipline exists; the decode
  side has no equivalent (`readLine` starts from an empty String every call and the record-loop
  allocates a fresh `String line` per row).

### performance-9 -- GC fold re-encodes and re-parses merge keys every iteration (Low)

- **Anchor:** `Gc/CasBlobInDegree.cpp:486-502` -- `String key` declared inside the loop (`486`),
  delta key rebuilt at `491` and retirement key at `496` on **every** iteration even when `di`/`ri`
  have not advanced, then the just-built key is immediately parsed back into a `BlobRef` plus
  `source_id` at `502`. Codec: `264-273` (`key`: a `push_back` plus two String temporaries) and
  `275-298` (`parse`). Reader: `207-230` plus `60-61` (`String k; String p;` fresh per `advance`).
- **Complexity:** O(E) redundant String constructions where O(D) would do, plus an
  encode-then-parse round trip per iteration whose typed inputs (`scattered[di].ref`,
  `.source_id`) are already in hand.
- **Magnitude:** ~4-5 String constructions per merge iteration, of which 2-3 are pure waste; the
  33-byte key exceeds `std::string`'s small-buffer size, so most of these are real mallocs. At
  E = 10M that is tens of millions of avoidable allocations per fold round -- the allocation-churn
  component of performance-1.
- **Trigger:** every GC fold round; cost proportional to pool size.
- **Evidence:** the loop already tracks `di`/`ri` positions, so hoisting the two key encodes to
  the advance sites and comparing typed `(ref, source_id)` tuples instead of encoded bytes is a
  local change; the codec is only needed at run I/O boundaries.

### performance-10 -- Catalog lookups scan a vector that is deliberately kept sorted (Low)

- **Anchor:** `Pool/CasRefCatalog.cpp:139-143` (`findEntry` uses `std::find_if`), against
  insertion via `std::lower_bound` at `164-166`; callers at `161, 242, 264, 324, 338, 368, 406,
  450, 476, 522, 545`. Each `mutate` also does `RefCatalog next = cur;` (`163, 246, 412, 454,
  528`), a full deep copy of every entry, followed by a whole-catalog re-encode inside
  `casUpdateImpl`.
- **Complexity:** O(N) String comparisons per lookup where O(log N) is available; O(N) copy plus
  O(N) encode per mutation. `checkPublicationAdmittedOrThrow` (`543-550`) is on the write-admission
  path, so it pays the linear scan per publication batch.
- **Magnitude:** N is namespaces (tables x disks). At N = 1000 a lookup is ~1000 String compares
  (~10 us) and a mutation copies and re-encodes the whole catalog. Only DDL-frequency for the
  mutating callers, so Low; `checkPublicationAdmittedOrThrow` is the one hot caller and it is
  read-only.
- **Trigger:** many namespaces in one pool.
- **Evidence:** `RootNamespace::string()` returns by reference
  (`Primitives/CasTypes.h:40`), so the comparator does not allocate -- the cost is comparisons
  only. The catalog object cap (`checkCatalogObjectBytes`, `Formats/CasRefCatalogFormat.cpp:253`)
  bounds N in practice, which is why this stays Low.

### performance-11 -- Every backend request does up to five substring searches for metric bucketing (Low)

- **Anchor:** `Backend/CasInstrumentedBackend.cpp:109-121` (`classifyCasNs`), called from
  `putIfAbsentStream` at `160` and from the per-op instrumentation wrappers.
- **Complexity:** O(len(key)) per probe, up to five probes (`/blobs/`, `/cas/ns/`,
  `/cas/manifests/`, `/roots/`, `/gc/`) with `String::find`, on every put/get/head/delete/list.
- **Magnitude:** ~750 characters scanned per request for a ~150-character key; well under 1 us,
  versus milliseconds of network. Irrelevant for S3, measurable only for in-memory or local
  backends and for the GC fold's high-frequency small reads. The key was constructed by `Layout`
  from a known object kind, so the classification is recoverable without any string search.
- **Trigger:** high request rates against a low-latency backend.
- **Evidence:** the increment itself is a table index plus an atomic
  (`incrementCasEvent`, `124-127`) -- correctly cheap; only the classification is wasteful.

### performance-12 -- Dedup cache is keyed per file and under-weights its entries (Low)

- **Anchor:** `Pool/CasPool.h:464-471` (`DedupWeight` returns a constant 64,
  `CacheBase<BlobRef, DedupPresent, BlobRefHash, DedupWeight>`), `Pool/CasPool.cpp:165-168`
  (construction), `196-213` (`dedupCacheContains` / `dedupCacheAdd`, the latter doing
  `std::make_shared<DedupPresent>()` -- one heap allocation to record an empty presence marker).
  Defaults: `deduplication_cache_bytes = 64 MiB`,
  `deduplication_head_first_min_bytes = 1 MiB` (`ContentAddressedSettings.cpp:36-37`).
- **Complexity:** O(1) lookup. The scaling issue is the key: presence is tracked per blob, i.e.
  per *file*, so the cache's reach in parts is `64 MiB / 64 / F`.
- **Magnitude:** the declared weight of 64 bytes admits ~1M entries, while the real per-entry
  footprint (a 24-byte `BlobRef` key, a separately allocated `shared_ptr` control block plus
  payload, an LRU list node and a hash-map node) is closer to 120-150 bytes -- roughly 2x
  under-accounting; the memory-ceiling consequence is ad5's. The performance consequence is reach:
  1M entries covers only ~10k parts at 100 files per part, and past that the cache thrashes, at
  which point each miss costs a HEAD for blobs at or above 1 MiB, or an unconditional body PUT
  below it.
- **Trigger:** a pool whose live file count exceeds ~1M, or a re-attach/restore that streams more
  distinct blobs than the cache holds.
- **Evidence:** `deduplication_head_first_min_bytes = 1 MiB` means small files never probe before
  uploading, so for the common many-small-columns part the dedup cache is the only thing standing
  between a re-insert and a full re-upload of every file.

## Benchmarks present and what they miss

Present: exactly one benchmark target, `benchmarks/benchmark_cas_ref_protocol.cpp` (369 lines,
`CMakeLists.txt` links `ch_contrib::gbenchmark_all` plus `dbms`). Fourteen cases, most with
`->Range(100, 100000)->Complexity()`, so the intent to track asymptotics is explicit:

- text primitives: `BM_WriteJSONStringSafe`, `BM_RawBulkWriteSafe`, `BM_EncodeRefLogTxn`,
  `BM_MemcpyTxnBytes` (a memcpy baseline), `BM_SnapshotEncode`;
- ref-protocol state: `BM_Admits`, `BM_AdmitsAddPrecommit`, `BM_ApplyRefLogTxn`,
  `BM_FlushInstall`, `BM_FlushInstallUniqueOwner`, `BM_ReplayHistory`, `BM_ScratchCopy`;
- `RefCowMap`: `BM_MergedIteration`, `BM_Materialize`.

Fixtures use realistic key shapes (`kSafeKeyLikeString` at `19-20`, `part_<i>_20260719_0_1000_1`
at `44`), so string lengths are not understated.

What it misses, mapped to the findings above:

- **No decode benchmarks at all.** Only the *write* side of the text formats is measured
  (`BM_WriteJSONStringSafe`, `BM_SnapshotEncode`). `readLine`, `JsonObjectReader`,
  `decodeRefTableSnapshot`, `decodePartManifest` and `openObject` -- the read hot path and the
  per-line allocation churn of performance-8 -- are unmeasured.
- **No part manifest coverage.** `encodePartManifest`/`decodePartManifest`/`computePayloadDigest`
  do not appear, so the three-encodes-per-commit write path is unmeasured.
- **No GC fold benchmark.** `CasBlobInDegree`'s merge, the dominant CPU consumer of
  performance-1 and performance-9, has no benchmark and no complexity assertion.
- **No staging-path benchmark.** The O(F^2) `erase_if` pattern of performance-5 is not exercised;
  nothing scales F at all -- every benchmark scales R.
- **Precommits are always P = 1** (`makeSyntheticSnapshot` pushes exactly one precommit, line 50),
  so `BM_ScratchCopy` and `BM_Admits` measure the cheapest possible state copy and hide the
  `std::set` deep-copy term that grows with concurrent in-flight inserts.
- **No zstd, no cache, no backend.** `sealObject`/`openObject`, the dedup cache, the manifest
  decode cache, the part-folder view cache and single-flight, the event dispatcher, and everything
  behind `Backend` are absent; all fourteen cases run against in-memory state, so no benchmark can
  observe the HEAD-before-cache-probe of performance-6.
- **Release-mode only in effect.** Nothing measures the sanitizer-build blowup of performance-4,
  and with all CAS tests deleted in this tree nothing else does either.

## Checked and sound

- **Content is hashed exactly once.** Blob hashing is streaming, done while the body is written
  (`ContentAddressedTransaction.cpp:1236,1259` -> `nextImpl` at `1269-1274`, hex taken at `1281`),
  with per-algorithm streaming buffers (`Primitives/CasBlobHashingWriteBuffer.cpp:36-196`). No
  re-read-and-rehash of file bodies anywhere. Only *manifest* bytes get re-digested (the cited
  sibling finding).
- **File lookup inside a part is a binary search**, not a scan: `findEntry` and `entryRange` use
  `std::lower_bound` over entries the encoder guarantees sorted
  (`Formats/CasPartManifestFormat.cpp:291-311`, sort at `73-81`). `listChildren` correctly narrows
  to the prefix range before deduplicating names (`Parts/PartFolderAccess.cpp:105-120`).
- **Manifest bodies are shared, not copied, on the hot path.** `readManifestShared` returns
  `shared_ptr<const PartManifest>` and `PartFolderView` holds it by pointer
  (`Parts/PartFolderAccess.h:61,76`). The by-value `readManifest` (`Pool/CasManifestReader.cpp:128`)
  would deep-copy every entry, but its only caller is `Tools/CasFsck.cpp:160`.
- **View builds are single-flighted.** `buildView` deduplicates concurrent misses through a
  promise/future map keyed by the ref (`Parts/PartFolderAccess.cpp:237-268`), so a thundering herd
  on one part costs one manifest read.
- **`RefCowMap` does its job.** Copying a `RefTableState` shares the committed base map rather
  than deep-copying it, which is why per-txn state copies stay cheap; `BM_ScratchCopy` and
  `BM_MergedIteration` exist to keep it that way.
- **ProfileEvents accounting is cheap** -- a static 2-D table indexed by (namespace, op) and an
  atomic increment (`Backend/CasInstrumentedBackend.cpp:81-127`); no string formatting or map
  lookups in the increment path. Per-edge GC increments are on anomaly branches only
  (`Gc/CasBlobInDegree.cpp:520`), not per row.
- **No O(pool size) work found on a per-operation path.** The ref-table cache budget walk over all
  namespace slots (`Pool/CasRefLedger.cpp:1155-1167`) runs behind an
  already-recovered early exit rather than per publish; `Pool::isAlgoAdmitted` binary-searches a
  tiny sorted vector (`Pool/CasPool.cpp:171-176`).
- **Encoders reserve their output buffers** with a row-count-proportional hint
  (`Formats/CasRefSnapshotFormat.cpp:119`), so the O(R) encode of performance-2 is at least a
  single allocation rather than a doubling cascade.
- `traitsFor` is a linear scan over an 18-entry table (`Formats/CasFormat.cpp:122-128`) called per
  encode/decode: an enum comparison per entry, well under the noise floor. Not reported.

## Coverage

Static reading only -- nothing was built, run, profiled or benchmarked; all magnitudes are
arithmetic from shipped defaults and measured code shapes, and the allocation counts assume a
glibc-class allocator with a 15-byte `std::string` small-buffer.

Read in full or in relevant part: `Gc/CasBlobInDegree.cpp`, `Pool/CasRefProtocol.{h,cpp}`,
`Pool/CasRefLedger.cpp`, `Pool/CasRefCatalog.cpp`, `Pool/CasManifestReader.{h,cpp}`,
`Pool/CasPool.{h,cpp}`, `Pool/CasEventDispatcher.{h,cpp}`, `Pool/CasPartWriteTxn.cpp`,
`Pool/CasRefCowMap.{h,cpp}`, `Parts/PartFolderAccess.{h,cpp}`, `ContentAddressedTransaction.cpp`,
`ContentAddressedMetadataStorage.cpp`, `ContentAddressedSettings.cpp`,
`Formats/CasTextFormat.{h,cpp}`, `Formats/CasPartManifestFormat.{h,cpp}`,
`Formats/CasRefSnapshotFormat.{h,cpp}`, `Formats/CasRefLogFormat.{h,cpp}`, `Formats/CasFormat.cpp`,
`Backend/CasInstrumentedBackend.cpp`, `Primitives/CasEvent.{h,cpp}`, `Primitives/CasBlobDigest.h`,
`Primitives/CasBlobHashingWriteBuffer.cpp`, `Primitives/CasTypes.h`, `benchmarks/*`, and
`programs/server/config.xml` for the shipped `cas_log` default.

Deliberately shallow: `Gc/CasGc.cpp` beyond its per-candidate event emission (round structure and
budgets are ad5's), the S3/GCS backend implementations (request cost is ad5's), lock hold times
(bc7's), and `Tools/CasFsck.cpp` (offline tool, not a hot path).

Confidence: high on the complexity classes and anchors, which are read directly off the code.
Medium on absolute magnitudes, which depend on unmeasured allocator and zstd throughput and on
assumed pool shapes (R, F, E are stated explicitly wherever used). Not assessed: real cache hit
rates, actual GC round wall time, and whether any of these costs is visible above object-store
latency in a specific deployment -- all three need a running system.
