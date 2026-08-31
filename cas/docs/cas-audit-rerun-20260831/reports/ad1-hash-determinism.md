# ad1-hash-determinism -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Pool/CasPartWriteTxn.{h,cpp}` (`ensureBlobPresent`, `putBlob`, `uploadBlobDetached`, `adoptEvidence`); `Backend/CasObjectStorageBackend.cpp` (`publishBlob`); `Pool/CasPoolMeta.cpp`; `Formats/CasPoolMetaFormat.{h,cpp}`; `Primitives/CasBlobDigest.{h,cpp}`; `Primitives/CasBlobHashingWriteBuffer.{h,cpp}`; `Primitives/CasXxh3Streamer.h`; `ContentAddressedSettings.cpp` (`cas_blob_hash`); `Formats/CasLayout.h` (`blobKey` / `parseBlobKey`); `Tools/CasFsck.cpp` (unreachable classification); `ContentAddressedTransaction.cpp` (hashing producers).
- Explicitly out of scope: cryptographic strength of the default algorithm (sibling); scratch-file durability (bc2); concurrency of two writers at one key (interleaving).

`observeAndAdmit`, `putIfAbsentStream`, `promoteStaged`, `conditionalCreateControlled`, and `copyObjectConditional` are absent at ceee42c. Blob publish is `ensureBlobPresent`: durable precommit required, mandatory `HEAD`, adopt a present non-condemned body whose logical size matches the source, else unconditional `publishBlob` under a fresh envelope.

## Findings
### ad1-1 -- empty cityhash128 content shares the all-zero digest that fsck substitutes for an unparsable blob key (Low)
- Anchor: `Primitives/CasBlobDigest.h:207-210` (`BlobRef` default `{CityHash128, zero digest}`); `Tools/CasFsck.cpp:949-953` (`layout.parseBlobKey(bkey).value_or(BlobRef{})`); CityHash empty payload is the untouched `(0,0)` seed (`IO/HashingWriteBuffer.h` `state(0,0)`).
- Trigger: a zero-length file forced to blob placement (`primary.idx`, empty `*.mrk*` / `*.bin`) under the default `cas_blob_hash=cityhash128`, plus any object under `blobs/` that `parseBlobKey` rejects.
- Evidence: the comment at `CasFsck.cpp:949-952` claims `BlobRef{}` "cannot match a real `retired_by_hash`/`in_run_hashes` entry" and therefore lands in `Unaccounted`. That is false for the default algorithm: the legitimate empty blob is exactly `blobs/ch128/00/000…0`. Other fsck sites skip unparsable keys (`:736`, `:811`, `:1038`); `:953` is the lone `value_or` fallback. A junk key then inherits the empty blob's GC class (`PendingGc` / `AwaitingGc` instead of `Unaccounted`). `xxh3` and `sha256` empty digests are non-zero, so the collision is default-algo only. Classification only; no data path uses this sentinel.
- Notes: same root cause as CAS-124. The HEAD-then-publish rewrite did not touch this line.

## By-design / info / non-actionable
- Hash is selectable (`cas_blob_hash` = `cityhash128` | `xxh3-128` | `sha256`, default cityhash128) and recorded in `_pool_meta.algos_used`. Keys namespace by algo (`blobs/<algo>/<hh>/<hex>`). Reads never re-hash. Settled as CAS-008.
- Presence-only admit remains, now with a logical-size gate. `ensureBlobPresent` (`CasPartWriteTxn.cpp:335-387`) HEADs, refuses `head.size < blob_header_len`, throws `CORRUPTED_DATA` if `logical_size != source.size` or meta size disagrees, then adopts a present non-condemned body without hashing it. Same-length foreign/colliding content is still reused. That is the dedup contract; the bucket credential is the trust boundary.
- Staged and re-uploaded bodies are not re-hashed. First absent publication may `VerbatimStagedBlobPublication` copy the staged object as-is (`:397-403`); later attempts stream `source.open()` under a new envelope (`:406-412`). `publishBlob` writes envelope + payload and checks streamed byte count only (`CasObjectStorageBackend.cpp:862-934`). Digest was computed once, on the local producer.
- Admitting a new algo CAS-unions it into `algos_used` and sets `min_reader_generation = G_BUILD` (`CasPoolMeta.cpp:87-90`). `G_BUILD` is 10 and equals `kMountWriteAttemptIdGeneration`; every pool this build can open already carries that floor (recreate-only). No additional lock-out today (CAS-013 residual, latent).
- `Xxh3Streamer` still resets before `valid()` (`CasXxh3Streamer.h:44`). `XXH3_128bits_reset` rejects NULL. Not a defect (CAS-125).

## Closed-since-2026-08-12
- Previous ad1-1 (High): writer computed stored logical size and discarded it. Closed by `940b1685bf9` + the size compare at `CasPartWriteTxn.cpp:345-351`. `observeAndAdmit` is gone.
- Previous ad1-4 (xxh3 null deref): not a bug at HEAD; xxHash guards NULL (CAS-125).
- Conditional blob create (`putIfAbsentStream` / `promoteStaged` / `If-None-Match` on CompleteMPU) is gone. Blob publication is unconditional `WriteMode::Rewrite` after mandatory HEAD.

## Coverage
- Reviewed: algorithm inventory and recording; hashed byte range for streaming / inline / staged-copy / adopt; HEAD-then-publish admit including size gate; empty-input vs fsck sentinel; mixed-algo keying; no re-hash of publish/copy.
- N-A: runtime digest-vs-reference computation (static only).
- Deferred: adversarial cityhash128 collision cost (hash-strength sibling).
