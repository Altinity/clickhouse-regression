# ad1-hash-determinism -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is.
CAS root: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

Question: is the content address a deterministic, stable, portable function of the content?
Sub-questions examined statically: implemented algorithms and how they are selected/recorded
(`Pool/CasPoolMeta.cpp`, `Formats/CasPoolMetaFormat.cpp`, `Primitives/CasXxh3Streamer.h`,
`ContentAddressedSettings` `blob_hash` / `blob_hash_allow_new`); exactly which bytes each producer
hashes; endianness/platform dependence of the digest value and of its textual encoding; seeds and
salts; empty and very large inputs; streaming vs one-shot equivalence; digest truncation and
collision probability at scale; digest -> object-key derivation (`Formats/CasLayout`); what happens
when one key is occupied by content the writer did not produce; the dedup lookup path and its cache
keying; mixed-algorithm pools.

Code-only rule honoured: `docs/**` and comments were not used as evidence of intent; shipped strings
were. All CAS tests are deleted in this working tree, so no test was read as a specification.

Cited from sibling audits, not re-derived here:
- default `blob_hash` is the non-cryptographic `cityhash128` and reads never re-verify the body
  against the address;
- no re-hash happens when a body is re-uploaded (resurrect / promote of staged bytes);
- the local scratch staging file is never fsynced and never re-hashed.

Not verifiable in this tree: `contrib/xxHash` is an uninitialised submodule (pinned at
`bbb27a5efb85b92a0486cf361a8635715a53f6ba`), so the bundled xxHash version could not be read; the
XXH3 spec-stability argument below assumes the pin is >= 0.8.0.

## What is hashed, by whom

| producer | bytes hashed | algorithm source | anchor |
| --- | --- | --- | --- |
| fresh streaming write, local scratch staging | payload only; no envelope exists in the scratch file, the envelope is prepended at upload time | `store()->writeAlgo()` = pool config `blob_hash` | `ContentAddressedTransaction.cpp:600,625-635`; `ContentAddressedTransaction.cpp:1213-1237`; `Primitives/CasBlobHashingWriteBuffer.cpp:180-197` |
| fresh streaming write, S3 conditional-copy staging | payload only; the envelope header is written straight to the sink *before* the hashing buffer is layered on, and `HashingWriteBuffer`'s ctor flushes the sink so pre-existing bytes cannot enter the hash | `store()->writeAlgo()` | `ContentAddressedTransaction.cpp:602-622,1239-1260`; `IO/HashingWriteBuffer.h:73` |
| inline entry (<= 1 MiB, file not forced to blob) | payload only, one-shot | `store()->writeAlgo()` | `ContentAddressedTransaction.cpp:638-654`; `Pool/CasPartWriteTxn.cpp:72-75` |
| inline overflow (> 1 MiB `INLINE_CAP`) | payload only, one-shot, then staged as a blob | `store()->writeAlgo()` | `ContentAddressedTransaction.cpp:643-668` |
| retry of a fresh upload (`ABORTED` loop, up to 8 attempts) | payload re-streamed from `source.open()`; digest is **not** recomputed, the caller's `BlobRef` is reused | n/a (ref carried in) | `Pool/CasPartWriteTxn.cpp:177-191,394-403` |
| resurrect (occupied + condemned) | nothing hashed; body re-streamed from source or from the staged object after `ignore(blob_header_len)` | n/a (sibling: no re-hash) | `Pool/CasPartWriteTxn.cpp:453-475` |
| `promoteStaged` (server-side copy) | nothing hashed; the staged object's own envelope + payload are copied verbatim to the blob key | n/a | `Pool/CasPartWriteTxn.cpp:391-392`; `ContentAddressedTransaction.cpp:514-529` |
| head-hit / head-miss adopt / manifest-trust adopt | nothing hashed and nothing compared; the address is trusted and the *stored* object is adopted | n/a | `Pool/CasPartWriteTxn.cpp:149-175,240-305,442-450,478-486,675-695` |
| GC, fsck, gc-rebuild | never hash blob content; they only parse digests out of keys and edge records | n/a | `Tools/CasFsck.cpp` (no digest computation anywhere); `Gc/CasBlobInDegree.cpp:264-298` |
| part manifest (`payload_digest`, not a content address) | canonical re-encode of the manifest with `pd` zeroed, CityHash128 one-shot | hard-wired CityHash128 | `Formats/CasPartManifestFormat.cpp:272-279` |

Three algorithms are implemented (`ch128` = CityHash128, `xxh3` = XXH3-128, `sha256`), selected by
the per-disk setting `blob_hash` (default `cityhash128`) and recorded in `_pool_meta.alg` as a sorted,
duplicate-free set (`Primitives/CasBlobDigest.h:26-31`, `Primitives/CasBlobDigest.cpp:20-45`,
`ContentAddressedSettings.cpp:33-34`, `Formats/CasPoolMetaFormat.cpp:32-51,53-82`). A pool may hold
several algorithms at once; the key namespaces them (`blobs/<algo>/<hh>/<hex>`,
`Formats/CasLayout.cpp:28-31` + `Formats/CasLayout.h:264-270`), and GC refuses blob entries whose
algorithm is not admitted by `_pool_meta` (`Gc/CasGc.cpp:981-985`).

## Findings

### ad1-1 -- an occupied content address is resolved by existence alone; the writer computes the stored object's length and then discards it (High)

- **Anchor**: `Pool/CasPartWriteTxn.cpp:250-305` (`observeAndAdmit`: `logical_size = hr.size - header_len` at :257, returned as the dep at :304, never compared to anything); callers at `Pool/CasPartWriteTxn.cpp:149-175` (head-first branch, `req.source.size` is in scope and unused for verification), `:442`, `:449`, and the commit-time trust path `:675-695`. The only size cross-check in the whole write path is producer-side (`ContentAddressedTransaction.cpp:1152-1172` compares `declared_size` against `source.size`, i.e. two local numbers) and `:399-402` (bytes actually streamed vs declared).
- **Trigger**: any object already present at `blobs/<algo>/<hh>/<hex>` whose payload is not the writer's payload. Two concrete routes: (a) a digest collision — with the default `cityhash128` an adversarial collision is cheap and reads never re-verify (sibling `codeonly-line` / hash-strength result), and a crafted pair need not even have equal length; (b) a foreign or half-written body left at that key by an earlier writer or by external tooling, since nothing else in the pool ties a key to its bytes. `deduplication_head_first_min_bytes` defaults to 1 MiB (`ContentAddressedSettings.cpp:37`), so for every blob >= 1 MiB this existence-only path is the *default* path, not an edge case.
- **Consequence**: the writer returns success with `BlobUploadOutcome::HeadHit` / `HeadMissAdopted`, `dedupCacheAdd` caches the ref as present (`Pool/CasPartWriteTxn.cpp:165`), and the manifest entry keeps the *locally measured* size (`ContentAddressedTransaction.cpp:509`) while the stored object holds different bytes of a possibly different length. Readers then slice `[header_len, header_len + manifest sz)` out of a foreign object (`Pool/CasManifestReader.cpp:142`) and get silent wrong data, or a short read if the foreign body is shorter. Nothing fails closed: the single cheapest discriminator the code already has in hand — the stored logical length vs the writer's own declared length — is computed and dropped. A one-line `logical_size != source.size -> throw` would convert an unbounded silent-corruption class into a loud, retryable failure.
- **Evidence**: `observeAndAdmit` derives `logical_size` purely to build the dep record and to backfill a `Clean` meta marker for it (`:287-292`); its only guard is `hr.size < header_len` (`:253-256`). `uploadBlobDetached` passes `req.source` into the head-first branch but uses it only for the size threshold (`:150-152`). `mergeBlobUploadResults` compares dep records against each other, never against the source (`:196-226`).

### ad1-2 -- admitting a second hash algorithm rewrites the pool's reader floor to the admitting build's generation, locking older builds out of the whole pool (Medium)

- **Anchor**: `Pool/CasPoolMeta.cpp:57-85`, specifically `next.min_reader_generation = G_BUILD;` at `:72`, committed by `casPut` at `:74`; enforcement on every reader at `Formats/CasPoolMetaFormat.cpp:152-155` ("pool requires reader generation {} but this build supports at most {}").
- **Trigger**: mount one disk with `blob_hash` set to a value not yet in `_pool_meta.alg` and `blob_hash_allow_new=1`. Admission runs during pool open (`Pool/CasPool.cpp:352,548`), so merely mounting is enough — no blob has to be written. Any other node or any rolled-back binary whose `G_BUILD` is lower than the admitting node's then fails to decode `_pool_meta` at all.
- **Consequence**: pool-wide mount failure for older readers, not merely inability to read blobs written under the new algorithm. The bump is unnecessary for that purpose: every pre-existing blob still lives under its old `blobs/<algo>/` namespace and remains fully readable by an older build, and the new algorithm's blobs are already self-describing via the key and the manifest's `ha` field (`Formats/CasPartManifestFormat.cpp:196-230`). `algos_used` is also append-only — there is no code path that removes an admitted algorithm — so the raised floor and the mixed-algorithm state are both irreversible.
- **Evidence**: the operator-facing string at `Pool/CasPoolMeta.cpp:52-54` presents `blob_hash_allow_new` purely as "admit a new algo into this pool" and says nothing about a reader-generation floor; the setting description at `ContentAddressedSettings.cpp:34` likewise says only "Explicit opt-in to admit a NEW hash algo". Nothing warns that the flag is a one-way compatibility gate on the entire pool.

### ad1-3 -- under the default algorithm, empty content hashes to the all-zero digest, which is also the sentinel fsck substitutes for an unparsable key (Low)

- **Anchor**: `IO/HashingWriteBuffer.h:21` (`state(0, 0)`), `:25-30` (`getHash()` returns the untouched seed when nothing was buffered) and `IO/HashingReadBuffer.h:24-32` (same for the one-shot path) — a zero-byte payload therefore yields the digest `00000000000000000000000000000000` for `ch128`. `Primitives/CasBlobDigest.h:41,145-152`: a default-constructed `BlobRef` is exactly `{CityHash128, all-zero digest}`. `Tools/CasFsck.cpp:751`: `layout.parseBlobKey(bkey).value_or(BlobRef{})`.
- **Trigger**: a zero-length file whose name forces blob placement — `primary.idx` or any `*.bin`/`*.mrk*`/`*.cmrk*` (`ContentAddressedTransaction.cpp:65-73,598`) — creates the legitimate blob `blobs/ch128/00/00000000000000000000000000000000`. Independently, any object under `<prefix>/blobs/` that `parseBlobKey` rejects (wrong hex length, unknown algo segment, shard/hex mismatch, debris from an aborted or foreign writer) reaches `:751` and is folded onto that same ref.
- **Consequence**: in the unreachable-blob classification loop the junk key inherits the empty blob's GC status. If the empty blob is unreferenced and present in the current GC snapshot, `in_run_hashes.contains(hash)` is true (`:764`) and the junk object is reported as `AwaitingGc` "expected" instead of `Unaccounted` — precisely the class whose note says persistent occurrences violate INV-2 and must be investigated (`:794-798`). fsck's headline signal for reachability-before-content violations can therefore be masked by an unrelated empty file. The same conflation reaches `retired_by_hash` (`:755`, additionally gated on a token match, so mostly benign) and `unref_edge_sources` (`:768`).
- **Evidence**: `xxh3` and `sha256` do not share this property (both produce a fixed non-zero digest for empty input), so the collision exists only for the *default* algorithm. Every other `parseBlobKey` call site in fsck correctly skips unparsable keys via `if (const std::optional<BlobRef> ref = ...)` (`:589-590`, `:650-651`, `:822-823`); `:751` is the lone `value_or` fallback.

### ad1-4 -- the xxh3 streamer resets the hash state before checking that the state was allocated, making its allocation guard unreachable (Low)

- **Anchor**: `Primitives/CasXxh3Streamer.h:17` — `Xxh3Streamer() : state(XXH3_createState()) { XXH3_128bits_reset(state); }`; the guard it is supposed to feed is `Primitives/CasBlobHashingWriteBuffer.cpp:87-88` (`if (!state.valid()) throw Exception(ErrorCodes::CANNOT_ALLOCATE_MEMORY, ...)`), and `valid()` is `Primitives/CasXxh3Streamer.h:24`.
- **Trigger**: `XXH3_createState()` returns `nullptr` (its documented failure mode is allocation failure) while a pool configured with `blob_hash=xxh3-128` opens a blob write buffer under memory pressure.
- **Consequence**: `XXH3_128bits_reset(nullptr)` dereferences the null state inside the constructor's body, so the process crashes before the member-initialisation of `Xxh3128BlobHashingWriteBuffer` completes and the `CANNOT_ALLOCATE_MEMORY` exception can be raised. The shipped diagnostic string "failed to allocate the xxh3 streaming state" is dead code.
- **Evidence**: the reset call is inside the ctor body of `Xxh3Streamer`, i.e. it runs during the base/member init of the write buffer at `CasBlobHashingWriteBuffer.cpp:84-86`, strictly before the `valid()` test at `:87`. No other call site tests `valid()`.

### ad1-5 -- the part manifest is parsed with tolerant unknown-key skipping, but its digest is recomputed by canonical re-encode, so any tolerated key is reported as corruption (Low)

- **Anchor**: `Formats/CasPartManifestFormat.cpp:127` and `:160` construct `JsonObjectReader` with `KeyStrictness::Tolerant`; `:303`/`:189-190` skip unknown keys; `:263-267` compares `computePayloadDigest(m)` against the decoded `pd` and throws `CORRUPTED_DATA` on mismatch; `:272-279` computes that digest by re-encoding the decoded struct with `encodePartManifest`, which can only emit the fields the struct models.
- **Trigger**: any future writer that adds a non-critical (non-`!`-prefixed) key to the descriptor line, an entry record, or the trailer — which is exactly what the tolerant reader plus the `!`-prefix critical-key convention (`Formats/CasTextFormat.cpp:236-247`, `Formats/CasBlobEnvelopeFormat.cpp:112-115`) is built to permit. In a mixed-version cluster the older reader hits this path on every manifest the newer writer produces.
- **Consequence**: the tolerant channel is unusable for part manifests, and the failure is misreported. The reader raises `CORRUPTED_DATA` "payload_digest mismatch" rather than an `UNKNOWN_FORMAT_VERSION`-style signal, so a pure forward-compatibility event is indistinguishable from real manifest corruption — the wrong verdict for an operator and for fsck's `recordUnchecked` accounting.
- **Evidence**: `computePayloadDigest` deliberately digests a re-encode rather than the received bytes (`probe.payload_digest = UInt128{}` then `encodePartManifest(probe)`), so the digest is a function of the *modelled* fields only. Contrast the envelope, which reaches the same goal safely by carrying no digest over its own tolerated keys.

## Collision analysis at scale

Digest width is used in full: `blobHashLenFor` returns 16 bytes for `ch128`/`xxh3` and 32 for
`sha256` (`Primitives/CasBlobDigest.cpp:20-31`), `DigestCodec::toHex` emits `2 * len` hex characters
(`Primitives/CasBlobDigest.h:85-89`), and `Layout::blobKey` puts the *entire* hex string in the leaf
name, with the 2-character shard segment being a duplicate of the first two hex characters rather
than a replacement for them (`Formats/CasLayout.cpp:28-31`, `Formats/CasLayout.h:264-270`,
round-trip checked at `Formats/CasLayout.cpp:56-84`). So there is no truncation, and the address
space is 2^128 (`ch128`, `xxh3`) or 2^256 (`sha256`). `DigestCodec::shardOf` folds the leading 8
bytes to a 64-bit value, but it is used for GC sharding only, never for key derivation.

Accidental-collision probability, birthday bound p ~= N^2 / 2^129 over distinct blobs in one pool at
128 bits:

| N (distinct blobs in a pool) | p(at least one collision) |
| --- | --- |
| 10^6 | 1.5e-27 |
| 10^9 | 1.5e-21 |
| 10^12 | 1.5e-15 |
| 10^15 | 1.5e-9 |
| 2.6e16 | ~1e-6 |

Even a pool holding 10^10 blobs sits near 1.5e-19, so accidental collisions are not the risk at any
realistic scale; the digest width is amply sized. The exposure is entirely adversarial: `ch128`
(the default) and `xxh3` are both non-cryptographic and make no collision-resistance claim, so the
relevant cost is that of *crafting* a pair, not of stumbling on one — see the sibling result for the
hash-strength argument and for the fact that reads never re-verify. Only `sha256` gives a
cryptographic guarantee, and it additionally requires an SSL build or the write fails closed with
`SUPPORT_IS_DISABLED` (`Primitives/CasBlobHashingWriteBuffer.cpp:188-194,217-226`). What ad1-1 adds
is that when a crafted or foreign body does occupy an address, the pool reuses it silently rather
than failing closed, and the differing-length case — the easy half of the crafting problem — is
detectable with data the code already holds.

## Checked and sound

- **Streaming vs one-shot equivalence, all three algorithms.** For `ch128` the digest depends on the
  2048-byte block partitioning, but `IHashingBuffer::calculateHash` re-normalises arbitrary chunk
  boundaries into whole `block_size` blocks plus one remainder (`IO/HashingWriteBuffer.cpp:11-49`),
  and both the write path (`HashingWriteBuffer`, default `DBMS_DEFAULT_HASHING_BLOCK_SIZE`) and the
  one-shot path (`HashingReadBuffer`, same default) use the same constant
  (`IO/HashingWriteBuffer.h:8,20,68-70`; `IO/HashingReadBuffer.h:16`). `xxh3` and `sha256` stream
  through boundary-independent incremental APIs (`CasBlobHashingWriteBuffer.cpp:106-114,160-171`).
  So the same bytes hash identically whether they arrive inline, via scratch staging, or via S3
  staging, and whatever the write-buffer size. Caveat: nothing pins the block size — no explicit
  argument and no static assertion — so a future producer constructing either buffer with a
  non-default `block_size` would silently fork the `ch128` address space.
- **Endianness and platform portability of the digest and its encoding.** CityHash byte-swaps its
  word loads on big-endian targets (`contrib/cityhash102/src/city.cc:41-62,90-94`), and its hex
  encoding writes `high64` then `low64` explicitly (`base/base/hex.h:189-208`). The `xxh3` path goes
  through `UInt128{low, high}`, whose `initializer_list` constructor places limbs via
  `_impl::little(i)` (`base/base/wide_integer_impl.h:1288-1301,308-314`), and `wide::integer` hex
  conversion branches on `std::endian::native` (`base/base/hex.h:135-141`); XXH3 itself is defined
  to be byte-order independent. `sha256` is hexed byte-wise. `BlobDigest::fromU128`/`toU128` use
  shifts, not `memcpy` (`Primitives/CasBlobDigest.h:46-60`). No `reinterpret_cast` of a scalar into
  the digest bytes exists on any producing path. Encoding is lower-case hex everywhere
  (`getHexUIntLowercase`, `hexString`), and `fromHex` rejects wrong lengths and non-hex characters
  (`Primitives/CasBlobDigest.h:91-108`).
- **Seeds and salts are constants, not derived from anything variable.** CityHash chains from the
  fixed seed `(0, 0)` (`IO/HashingWriteBuffer.h:21,76`); XXH3 uses `XXH3_128bits_reset`, i.e. the
  default secret with no custom seed (`Primitives/CasXxh3Streamer.h:17,39-44`); SHA-256 has none.
  Nothing mixes in `pool_id`, `server_id`, `build_id`, path, size, or timestamp.
- **The envelope is excluded from the hash on every producing path.** The S3 staging constructor
  writes the header to the raw sink before layering the hashing buffer, and `HashingWriteBuffer`'s
  constructor flushes the sink precisely so earlier bytes cannot enter the hash
  (`ContentAddressedTransaction.cpp:1256-1259`; `IO/HashingWriteBuffer.h:73`); the scratch path
  never puts a header in the temp file at all (`ContentAddressedTransaction.cpp:1223-1236`,
  header added at upload `Pool/CasPartWriteTxn.cpp:394-398`). The header's variable-length pad and
  its budget-truncated `ref` field (`Formats/CasBlobEnvelopeFormat.cpp:74-87,119-144`) therefore
  cannot perturb the address. The payload boundary is a single pool-wide constant
  (`_pool_meta.hln`, validated to `>= 240`, a multiple of 8, `<= 16384`,
  `Formats/CasPoolMetaFormat.cpp:19-30`), used identically by writers, `observeAndAdmit`, resurrect
  and readers.
- **Key derivation is injective in (algorithm, digest).** Distinct digests cannot share a key: the
  full hex is the leaf, the shard prefix is derived from it, the algorithm is its own path segment,
  and a blob leaf can never collide with a `.meta` sibling because hex contains no `.`.
- **Mixed-algorithm pools are represented consistently end to end.** Per-entry algorithm in the
  manifest (`Formats/CasPartManifestFormat.cpp:196-230`, `Formats/CasWireVocab.cpp:36-42`), an
  algorithm byte prefixed to every GC source-edge key with a per-algorithm length check
  (`Gc/CasBlobInDegree.cpp:264-298`), digest hex length validated against the algorithm on decode
  (`Formats/CasLayout.cpp:74-84`), and GC refusing unadmitted algorithms after one metadata refresh
  (`Gc/CasGc.cpp:981-985`). `_pool_meta.alg` is validated as strictly sorted and duplicate-free
  (`Formats/CasPoolMetaFormat.cpp:32-51`).
- **Empty and very large inputs.** Empty input is well-defined for all three algorithms (see ad1-3
  for the `ch128` zero-digest consequence); `observeAndAdmit` tolerates a zero logical size
  (`hr.size == header_len`). Large inputs are streamed with 64-bit lengths throughout; the `ch128`
  chain and the XXH3/SHA-256 incremental states have no size ceiling, and the manifest's own caps
  (`Pool/CasPartWriteTxn.cpp:52-55`) bound the metadata rather than the blob.
- **Digest-width guards exist but are assertion-only.** `DigestCodec::checkZeroTail`
  (`Primitives/CasBlobDigest.h:138-142`) and `checkZeroTailForAlgo`
  (`Gc/CasBlobInDegree.cpp:257-261`) use `chassert`, so in release builds a `BlobRef` carrying a
  32-byte digest under a 16-byte algorithm label would be silently truncated to 16 bytes by both
  `toHex` and the edge-key codec. I could not construct a path that produces such a `BlobRef`: every
  decoder validates the hex/byte length against the algorithm before building the ref, and the two
  producers derive the digest from an algorithm-matched hex string. Reported as a latent fragility,
  not a finding, for lack of a trigger.
- **The part manifest's own digest fails closed** on mismatch (`Formats/CasPartManifestFormat.cpp:263-267`),
  and duplicate entry paths are rejected at encode time (`:79-81`) — see ad1-5 for the
  forward-compatibility side effect of how that digest is computed.
- **The dedup cache cannot by itself substitute content.** It is per-`Pool` and keyed on the full
  `BlobRef` including the algorithm byte (`Pool/CasPool.cpp:165-168,196-213`;
  `Primitives/CasBlobDigest.h:154-162`), it stores presence only, and a hit merely elects the
  head-first strategy — the subsequent `head(key)` is what decides (`Pool/CasPartWriteTxn.cpp:149-175`).
  A stale positive after GC deletion degrades to a normal upload. The cache is thus not the weak
  link; the missing verification in the branch it selects is (ad1-1).

## Coverage

Covered: algorithm inventory, selection and recording; the exact hashed byte range for every
producer including the four non-hashing producers; envelope exclusion and payload-boundary
consistency; endianness and textual-encoding portability across all three algorithms and both
128-bit hex conventions; seed/salt constancy; empty and large inputs; streaming vs one-shot
equivalence with the block-size dependency made explicit; digest truncation (none) and the
collision arithmetic at 10^6..2.6e16 blobs; digest-to-key derivation and its injectivity;
one-key-two-contents handling; the dedup lookup path and its cache keying; mixed-algorithm pools
across manifest, key, GC edge and admission paths.

Not covered / boundaries: the cryptographic strength of the default algorithm and the absence of
read-time verification (sibling), re-hashing on body re-upload (sibling), scratch-file durability
(sibling). No dynamic verification was performed — no build, no execution, no digest was computed
against a reference implementation; the bundled xxHash version could not be read because the
submodule is not checked out in this working tree. The concurrency and crash-consistency aspects of
the adopt path are left to the interleaving and crash-consistency audits; ad1-1 is stated as a
single-writer, no-crash property.
