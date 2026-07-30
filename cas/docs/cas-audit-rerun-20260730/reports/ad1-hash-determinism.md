# ad1-hash-determinism — re-run 2026-07-30

## Scope in current code

- CAS source tree: `/Volumes/workspace/ClickHouse` @ branch `cas-audit-20260730` (HEAD `834c9517f56`).
- Files/dirs walked (CAS-only):
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobDigest.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobHashingWriteBuffer.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasXxh3Streamer.h`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasCodecUtil.h`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPoolMeta.cpp`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPool.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPoolMetaFormat.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasBlobEnvelopeFormat.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasLayout.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasWireVocab.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasRecordStreamFormat.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasBlobInDegree.{h,cpp}`, `Gc/CasGcShardPlan.h`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedSettings.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.{h,cpp}`

## Findings still present

### CAS-003 — Non-cryptographic content hash + reads never re-verify (partial)

- **Status:** 🟡 partially mitigated / still present in weakest form.
- **Anchor (no read-time re-hash):** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp:77`
  - Evidence: `/// The core otherwise never re-hashes payloads; any copy-forward re-verification must use this convention.`
- **Anchor (no read-time re-hash, second confirmation):** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.h:291`
  - Evidence: `` `CityHash128` stays the thin ... function the wiring defines; the core never re-hashes payloads). ``
- **Anchor (CityHash still default):** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedSettings.cpp:74`
  - Evidence: `DECLARE(String, blob_hash, "cityhash128", "Pool blob content-hash function (cityhash128 | xxh3-128 | sha256); fixed at pool creation", 0)`
- **Trigger:** cross-tenant collision on a shared pool (blob poisoning per SEC-1/INT-2) → wrong bytes served silently, because the read path performs no content-hash re-verification against `logical_hash` at any layer of the CAS core.
- **Mitigation delta since original audit (NEW):** the pool now supports selectable content-hash algorithms `{CityHash128, XXH3_128, Sha256}` via `Cas::BlobHashAlgo`. An operator that wants *cryptographic* collision resistance can set `<blob_hash>sha256</blob_hash>` on the disk config, and the whole write path routes through `Sha256BlobHashingWriteBuffer` (`CasBlobHashingWriteBuffer.cpp:142-196`) and `blobHashHexOneShot` (`:242-255`).
- **Notes:** the *dedup non-verification on read* half of CAS-003 is unchanged — no anchor exists that re-hashes blob payload against its key on the read path. The "non-crypto" half is now *configurable-away* (sha256 opt-in), but the shipped default is still CityHash128, so a stock deployment retains the original CAS-003 exposure.

### CAS-107 — BE would silently fork dedup; manifest bytes not version-stable (partial)

- **Status:** 🟡 partial — BE half still present; manifest-version half is by design + weakened.
- **Anchor (no LE guard):** repo-wide search for `static_assert.*endian` / `__BYTE_ORDER__` / `little_endian_only` in the CAS tree returns **no matches**. There is no explicit fail-closed check that the running host is little-endian.
- **Countervailing evidence (why silent-fork risk is bounded):** every wire integer conversion in CAS is now an **explicit** BE reader/writer, not a `memcpy` of a native-endian value:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasCodecUtil.h:18-40` (BE-only `UInt128` wire form; throws on wrong width)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobDigest.h:76-95` (`fromU128` / `toU128` are hand-rolled BE loops)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobDigest.h:177-186` (`shardOf` explicit BE u64; comment: "changing the byte order would silently remap shards on little-endian hosts and break compatibility with the 128-bit hash mapping")
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGcShardPlan.h:38-41` (comment: "MUST stay an explicit big-endian read, never a native-endian memcpy (would silently reshard on an LE host).")
- **Residual risk:** the *hash-primitive implementations themselves* — `CityHash_v1_0_2::CityHash128`, xxhash `XXH3_128bits`, OpenSSL `EVP_sha256` — are what actually produce the content key. CityHash's canonical implementation guarantees cross-endian identical output only when built with a byte-swap on BE hosts; CH's bundled `CityHash_v1_0_2` targets LE, and CAS still relies on that at `CasBlobHashingWriteBuffer.cpp:47-90` and `CasPartManifestFormat.cpp:315`. No CAS-side static or runtime guard rejects a BE host at mount time.
- **Trigger:** a hypothetical BE peer joining a live pool would compute a different key for identical bytes → silent dedup fork / relink false-negatives (never false positives; no data corruption).
- **Manifest-version-stability half:** `PartManifest` still embeds `ManifestRef` (`writer_epoch`, `build_sequence`, `manifest_ordinal`) + `root_namespace_id` into the encoded bytes (`CasPartManifestFormat.cpp:94-102`). This is identity-scoped by design (AD1-4). The `payload_digest` is computed via `CityHash128` on the deterministic encoding (`CasPartManifestFormat.cpp:306-317`) — stable for identical bodies. `writer_version` / `format_version` are **no longer** embedded in the encoded manifest bytes: `CasBlobEnvelopeFormat.h:58` states "envelope drops writer_version"; a single `v` header line remains the sole version field (`Formats/README.md:46`). So the original AD1-5 concern (manifest bytes vary with CH version) is **weakened**: only the top-line `v` differs across CH generations, not a full set of version fields inside the body.

## Findings fixed / no longer reproducible

### CAS-037 — Content-hash algorithm is an unversioned, unpinned pool contract

- **Status:** ✅ FIXED.
- **Anchor (algo persisted in PoolMeta):** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPoolMetaFormat.h:29-31`
  - Evidence: `` /// Every hash algorithm ever admitted, encoded as `static_cast<uint8_t>(BlobHashAlgo)`, in strictly /// increasing order. Admission only appends a new algorithm to this durable set. std::vector<uint8_t> algos_used; ``
- **Anchor (fail-closed admission check):** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPoolMeta.cpp:56-102` (`throwNotAdmitted`, `admitOrValidate`)
  - Evidence line 58-61: `"CAS pool blob_hash mismatch: pool has {{{}}}; config requests {}; set <blob_hash_allow_new>1</blob_hash_allow_new> to admit a new algo into this pool"` — a config with a hash algo not in the persisted `algos_used` set fails closed with `BAD_ARGUMENTS`.
- **Anchor (persisted set actually written):** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPoolMeta.cpp:148` (`pm.algos_used = {static_cast<uint8_t>(blob_hash_algo)};`) and `:86-90` (CAS-union under `allow_new`, with `min_reader_generation` raised in the same write).
- **Anchor (encode/decode round-trip):** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPoolMetaFormat.cpp:82-93` (encode as `"alg":"ch128,sha256"`), `:133-147` (decode), `:49-68` (`validatePoolAlgosUsed` — non-empty, all known, strictly sorted).
- **Anchor (opt-in flag for admitting a new algo):** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedSettings.cpp:75`
  - Evidence: `DECLARE(Bool, blob_hash_allow_new, false, "Explicit opt-in to admit a NEW hash algo into an existing pool's algos_used", 0)`
- **Anchor (blob path segment carries the algo):** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasLayout.h:80-81`, `CasLayout.cpp:36`
  - Evidence: `` return shardedKey("blobs/" + String(blobHashAlgoName(ref.algo)), blobHexOf(ref)); `` — a `ch128` blob and an `xxh3` blob of the same bytes live under different keys, so a future algo change cannot silently overwrite existing content.
- **Anchor (GC-time algo validation):** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp:950-970` — GC rejects any refresh whose ref algo is not admitted in the pool, using `blobHashAlgoName` which itself throws `BAD_ARGUMENTS` on an unknown byte.
- **Conclusion:** the hash algorithm is now a **persistent, versioned, fail-closed** pool contract. The original CAS-037 "silently forks dedup" scenario cannot occur without an explicit `blob_hash_allow_new=1` opt-in, which CAS-unions the new algo into `algos_used`, raises `min_reader_generation` to `G_BUILD`, and thereafter tags every new blob's object key with its algo segment so keys don't collide across algos. This is stronger than the recommendation in AD1-3 (which asked for a single "hash_algo_id" pin); the implementation actually supports **multi-algo pools** with per-blob algo tagging.

## New findings (not in original audit)

- **NEW-AD1-1 (Low — `blob_hash_allow_new` semantics are dedup-fracturing by design).** Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPoolMeta.cpp:75-101`. Trigger: an operator flips `<blob_hash_allow_new>1</blob_hash_allow_new>` and reopens with a different algo. The pool CAS-unions the new algo into `algos_used`, but from that point on **new writes and old writes of byte-identical content live at different keys** (`blobs/ch128/S/<hex>` vs `blobs/sha256/S/<hex>`, per `CasLayout.cpp:36`). This is the intended safety behavior (never overwrite), but it means the *dedup ratio degrades permanently* for the affected content, and there is no operator warning in the code path — the change of algo mid-life is a silent dedup fork event that only shows up in `system.parts.bytes_on_disk` vs physical bytes. Severity is Low because it's opt-in and correctness-preserving; it deserves a doc/warn.
- **NEW-AD1-2 (Info — `payload_digest` is hardcoded to CityHash128 regardless of pool algo).** Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp:306-317` (`computePayloadDigest` calls `CityHash_v1_0_2::CityHash128`). By comment (`CasPartManifestFormat.h:95-100`) `payload_digest` is *integrity/debug only*, "never a key, never dedup, never in-degree", so this is not a correctness issue — but a sha256-configured pool still has one internal integrity check (manifest self-digest) that is non-cryptographic. Worth noting as a scope caveat when someone reasons "sha256 pool ⇒ all CAS hashes are crypto".
- **NEW-AD1-3 (Info — CAS-025 fix incidentally lands here).** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp:293-301` now re-computes `payload_digest` on `decodePartManifest` and throws `CORRUPTED_DATA` on mismatch. Original AD1 audit predates this; it belongs to `bc4-protobuf-decode` / integrity family, but I record the anchor here because it appeared while grepping for hash-verification sites.

## By-design / N/A / info

- **AD1-1 (Info — blob dedup key deterministic + endian-safe on LE):** unchanged, still valid. Explicit BE byte-order everywhere on the wire (`CasCodecUtil.h:18-40`), CityHash/xxh3/sha256 all endian-fixed on LE ClickHouse targets.
- **AD1-4 (Info — ManifestId identity-scoped by design):** unchanged. `PartManifest` still embeds `ManifestRef` (`writer_epoch`, `build_sequence`, `manifest_ordinal`) and `root_namespace_id` (`CasPartManifestFormat.cpp:94-102`), so cross-replica manifest bytes still differ by construction. Blob-level dedup is unaffected.
- **AD1-6 (Info — file-name normalization deterministic):** unchanged. `escapeForFileName` (used for manifest entry paths and layout keys, see `CasLayout.h`) remains a pure deterministic transform; no locale dependence introduced.
- **AD1-7 (Low — deterministic ≠ collision-resistant):** now mitigable by choosing `blob_hash=sha256` at pool creation (`ContentAddressedSettings.cpp:74`, `CasBlobHashingWriteBuffer.cpp:142-196`). Default is still `cityhash128`, so the concern applies to any pool that does not explicitly opt in. Folded into CAS-003 above.

## Verdict summary table

| CAS-id  | Old severity | Status                                    | Evidence anchor                                                                                       |
|---------|--------------|-------------------------------------------|-------------------------------------------------------------------------------------------------------|
| CAS-003 | High         | 🟡 partially mitigated (still-present)    | `Pool/CasPartWriteTxn.cpp:77`; `ContentAddressedTransaction.h:291`; opt-in sha256 at `ContentAddressedSettings.cpp:74` |
| CAS-037 | Med          | ✅ fixed                                  | `Formats/CasPoolMetaFormat.h:29-31`; `Pool/CasPoolMeta.cpp:56-102, 148`; `Formats/CasLayout.cpp:36`   |
| CAS-107 | Low          | 🟡 still-present (BE half only; weakened) | no `static_assert`/BE guard in tree; explicit BE wire ops at `Primitives/CasCodecUtil.h:18-40`, `Primitives/CasBlobDigest.h:177-186`, `Gc/CasGcShardPlan.h:38-41` |

**Counts:** 3 scoped findings — 1 ✅ fixed (CAS-037), 2 🟡 still-present-with-mitigation (CAS-003 partial, CAS-107 partial); 3 new info/low findings (NEW-AD1-1..3).

**Headline delta since original audit:** the biggest AD1 recommendation (AD1-3 / CAS-037: pin the dedup hash-algo identity in `PoolMeta` and fail closed on mismatch) is **implemented and stronger than proposed** — multi-algo `algos_used` set, per-blob algo path segment, explicit `blob_hash_allow_new` opt-in, and `min_reader_generation` raised on admission. CAS-003 is no longer unfixable-by-config (sha256 is a supported opt-in) but the shipped default remains CityHash128 with no read-time re-verify, so the original exposure survives for out-of-the-box deployments. CAS-107 BE-fork risk is unchanged in principle but the code has become significantly more defensive: every wire integer read/write is now explicitly big-endian with comments flagging LE-only assumptions, which would at least make a BE port a *deliberate* effort rather than a silent one.
