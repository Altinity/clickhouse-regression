# bc4-protobuf-decode (structured decode hardening) -- fresh audit 2026-08-12

TARGET: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is.
CAS root: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` (`Formats/` = 39 files, 5,677 lines).
Method: static reasoning only. All anchors are `file:line` in the working tree. Paths below are relative to the CAS root unless noted.

## Scope (and why the protobuf angle was reframed)

Protobuf is gone from CAS. There is no `.proto`, no varint reader, no wire-tag dispatch: every persisted object is now self-describing text. The decode surface is:

- a **shared NDJSON layer** (`Formats/CasTextFormat.{h,cpp}`): `CasJsonWriter` (escaping writer), `JsonObjectReader` (per-line object reader with key strictness), `readLine`, `expectHeaderLine`, and `openObject`/`sealObject` (the zstd envelope);
- **17 format traits** (`Formats/CasFormat.cpp:100-119`) supplying per-format `line_cap`, `object_cap`, key strictness and compression policy;
- **per-format decoders**, each a hand-written `while (r.nextKey(key))` dispatch;
- two **binary-ish framings** that are not JSON: the fixed-width blob envelope pad zone (`CasBlobEnvelopeFormat.cpp`) and the part-manifest payload zone banner (`CasPartManifestFormat.cpp:243-258`);
- **key parsing** (`CasLayout.cpp`), which is a second, independent decoder for untrusted object-storage key names.

So the old protobuf question ("can a crafted wire message drive allocation or confuse field parsing?") maps onto: can a crafted *line* drive allocation, can a crafted *value* survive framing, and — the dominant class here — can an *absent* field silently become a dangerous default? The last one replaces protobuf's implicit-default hazard almost exactly, and it is where the real findings are.

Threat model: object-storage bytes are untrusted (the premise of a decode audit). CAS objects carry no per-object MAC; structural validation plus, for a few formats, a body-vs-key binding is the entire integrity story.

Cited, not re-derived (siblings): `Backend::get` materializes control objects fully before `object_cap` applies; the `JsonObjectReader` duplicate-key guard is a quadratic scan under the line cap; `readU64Number`/`readU64String` use `readIntText` with `DO_NOT_CHECK_OVERFLOW` so numbers wrap mod 2^64; strict formats misreport additive fields as corruption; blob-envelope version is checked only by `ca-inspect`.

## Shared decode layer

Audited in full. What holds:

- `readLine` (`CasTextFormat.cpp:271-286`) is EOF-safe and cap-bounded (worst case `line_cap + 1` bytes); it throws `CORRUPTED_DATA` on a line without terminator, so truncation at any byte offset is a clean corruption error rather than a short read.
- `JsonObjectReader::guarded` (`CasTextFormat.cpp:110-130`) funnels the six parse-failure error codes into `CORRUPTED_DATA` and lets `UNKNOWN_FORMAT_VERSION` through unchanged — the error taxonomy at the shared layer is deliberate and correct.
- `readHex128` (`CasTextFormat.cpp:181-191`) enforces exactly 32 lowercase hex chars before `unhexUInt`, so the fixed-width read cannot over-read.
- `CasJsonWriter::stringValue` (`CasTextFormat.cpp:58-107`) escapes `"`, `\`, every byte below 0x20, and U+2028/U+2029. I specifically looked for record injection and truncation: because `\n` and `"` are always escaped, **no string value can close its own record or inject a second NDJSON line**. Bytes 0x7F and 0x80-0xFF pass through unescaped, which can emit invalid UTF-8 but cannot break framing.
- `readFixedBytes` (`Primitives/CasCodecUtil.h:37-45`) checks `n > in.available()` *before* `String s(n, '\0')`. This is the one place where an untrusted length reaches an allocation, and it is correctly ordered — the obvious length-driven-OOM finding does not exist.
- `skipUnknown` (`CasTextFormat.cpp:236-247`) implements the `!`-prefixed critical-key rule before the strictness check, so a critical key is rejected even in a tolerant format.

What does not hold: `openObject` allocates a declared size before validating it (bc4-5); `readU64*` accept non-canonical numeric spellings while the key parser rejects them (bc4-7); and the layer offers **no "required field" helper at all**, which is the root cause of bc4-1, bc4-2 and bc4-8 — every decoder hand-rolls its own `saw_x` bookkeeping, and several simply forget.

## Per-format hardening table

`line_cap`/`object_cap` from `Formats/CasFormat.cpp:100-119`. "Digest" = does decode verify any checksum over the bytes. "Unknown fields" = behaviour on an unrecognised key. "Required" = are the semantically load-bearing fields mandatory.

| format | object cap | bounds / framing | digest | unknown fields | required fields | error type | anchor |
|---|---|---|---|---|---|---|---|
| CasTextFormat (shared) | per-trait | `readLine` cap-bounded, EOF-safe | n/a | strict throws / tolerant skips | n/a | CORRUPTED_DATA | `CasTextFormat.cpp:271` |
| CasRecordStreamFormat (`cas_run`) | **0 (none)** | 4 KiB lines, streamed; trailer count + no-bytes-after | **yes**, whole-file CityHash128 vs seal | Strict: throws | yes, incl. marker-conditional field rejection | CORRUPTED_DATA | `CasRecordStreamFormat.cpp:222-296` |
| CasBlobEnvelopeFormat | 256 B | pad zone scanned to `\n`, non-space rejected; `object_size` param **unused** | no | Tolerant | `type`,`v` only | CORRUPTED_DATA | `CasBlobEnvelopeFormat.cpp:146,214-229` |
| CasBlobMetaFormat | 1 MiB | body line + junk check | no | Tolerant | **`st` only** (bc4-2) | CORRUPTED_DATA | `CasBlobMetaFormat.cpp:66-83` |
| CasPartManifestFormat | 256 MiB | `readFixedBytes` bounded; banner raw + unescaped (bc4-1) | yes, re-encode `payload_digest` | Tolerant (not digest-covered) | yes | CORRUPTED_DATA | `CasPartManifestFormat.cpp:243-267` |
| CasPoolMetaFormat | 1 MiB | body + junk + trailing checks; `hln`/`alg` range-validated | no | Tolerant | `pid`,`gcs`; `hln` via validator | CORRUPTED_DATA / UNKNOWN_FORMAT_VERSION | `CasPoolMetaFormat.cpp:140-155` |
| CasRefCatalogFormat | 256 MiB | 4 KiB lines, trailer count, strict ascending ns, ns byte bound | no | Strict, explicit per-key throw | yes, incl. state/creator pairing | CORRUPTED_DATA | `CasRefCatalogFormat.cpp:187-248` |
| CasRefCkptFormat | 64 KiB | body + junk + trailing; paired-field rules | no | Strict | pairs enforced; `le` defaults | CORRUPTED_DATA | `CasRefCkptFormat.cpp:109-142` |
| CasRefLogFormat | 64 MiB | 64 MiB lines, trailer count, body-vs-key binding, budget recheck | no | Tolerant; **misplaced known keys silently dropped** (bc4-6) | `ns`,`we`,`rs`; per-op partial | CORRUPTED_DATA | `CasRefLogFormat.cpp:284-361` |
| CasRefSnapshotFormat | 64 MiB | trailer count, body-vs-key binding, ordering invariants | no | Tolerant; retired keys explicitly rejected | yes (`ns`,`we`,`rs`,`lc`, per-row) | CORRUPTED_DATA | `CasRefSnapshotFormat.cpp:173-255` |
| CasGcStateFormat | 1 MiB | body + junk + trailing | no | Tolerant | **`gcs` only** (bc4-1) | CORRUPTED_DATA | `CasGcStateFormat.cpp:50-67` |
| CasGcOutcomesFormat | 256 MiB | trailer count, junk checks | no | Tolerant | `ha`,`h`,`tt`; **`oc`/`k` optional** (bc4-8) | CORRUPTED_DATA | `CasGcOutcomesFormat.cpp:101-122` |
| CasGcMaintenanceStateFormat | 512 KiB | **checks `object_cap` itself** before parsing; cursor byte bound | no | Strict | `cur` | CORRUPTED_DATA | `CasGcMaintenanceStateFormat.cpp:34-63` |
| CasFoldSealFormat | 256 MiB | records: trailer count + junk; **meta line: no junk check, no required `g`** (bc4-3) | no | Strict per-record-kind | records yes, meta no | CORRUPTED_DATA | `CasFoldSealFormat.cpp:294-305` |
| CasServerRootFormats (owner/epoch/lease) | 1 MiB | body + junk + trailing | no | Tolerant | **identity only; `eat`/`fen` optional** (bc4-1) | CORRUPTED_DATA | `CasServerRootFormats.cpp:147-172` |
| CasWireVocab / CasRefWireVocab | n/a | exhaustive word→enum, no fallthrough default | n/a | throws on unknown word | `manifestRefFromFields` range-checks | CORRUPTED_DATA | `CasWireVocab.cpp:28-96` |
| CasLayout (key parser) | n/a | every `substr`/suffix strip length-guarded; `parseCanonicalU64` overflow-safe and canonical-only | n/a | returns `nullopt` | n/a | nullopt / CORRUPTED_DATA | `CasLayout.cpp:12-24,42-61` |
| CasByteBudget | n/a | saturating add/mul; **`cap == 0` means "unlimited"** | n/a | n/a | n/a | n/a | `CasByteBudget.h:18-26` |

## Findings

### bc4-1 -- Part-manifest payload-zone banner is written raw, so an encodable path makes a permanently undecodable manifest (High)

- **Anchor**: `Formats/CasPartManifestFormat.cpp:64-67` (`bannerFor`), `:106-110` (banner appended raw on encode), `:248-252` (banner compared against a single `readLine` on decode). Path validation exists **only** on the decode side (`:184-193`); `encodePartManifest` (`:71-113`) validates nothing but duplicate paths.
- **Crafted input**: a manifest entry whose inline path contains a newline, e.g. `data\nbin`. The decode-side path check splits on `/` and rejects only empty, `.` and `..` segments, so `data\nbin` is a legal single segment. On encode, `writeEntryRecord` escapes it correctly inside the JSON record (`data\\nbin`), but `bannerFor` splices it **unescaped** into the payload zone, emitting `==> data` / `bin il=5 <==` as two physical lines. The same effect is reachable with a path longer than the 64 KiB `line_cap`, which the encoder also does not bound.
- **Consequence**: the object is written successfully and then fails every subsequent read: `readLine` stops at the injected newline, `banner_line` is `"==> data"`, the expected banner is the full string, and decode throws `CORRUPTED_DATA: payload-zone banner mismatch`. The failure is before the `payload_digest` check, so the digest cannot distinguish it from real corruption. The part is unreadable and fsck reports it as corrupt, in a pool where nothing is actually corrupt. This is the one place in the whole format family where an untrusted value is emitted into framing without escaping, and the asymmetry (encoder permissive, decoder strict) turns it into write-side data loss rather than a rejected write.
- **Evidence**: `bannerFor` returns a plain `String` concatenation; `out.append(banner)` at `:107` bypasses `CasJsonWriter::stringValue`, which is the only escaping path in the codebase. Compare `writeEntryRecord` at `:46`, which does use `writeStringValue` for the same `e.path`.

### bc4-2 -- Blob meta requires only `st`, so `{"st":"condemned"}` decodes to condemn round 0 (Medium)

- **Anchor**: `Formats/CasBlobMetaFormat.cpp:66-81` — `saw_state` is the only presence flag; `cr` and `sz` fall through to the struct defaults (`condemn_round = 0`, `size = 0`).
- **Crafted input**: `{"type":"cas_blob_meta","v":9}\n{"st":"condemned"}\n` — 51 bytes, passes the header, the junk check and the trailing-bytes check.
- **Consequence**: the blob is seen as condemned at round 0. `Gc/CasBlobInDegree.cpp:394` graduates a candidate when `e.condemn_round < current_round`, which is true for every round above zero, so the two-phase condemn grace window is skipped on the first pass instead of after a real round boundary. `size = 0` simultaneously removes the blob from reclaimed-bytes accounting. A single truncated or hand-written `.meta` object therefore accelerates deletion of the blob it describes.
- **Evidence**: struct defaults at `Formats/CasBlobMetaFormat.h`; `writeCondemnedMeta` (`Gc/CasGc.cpp:89-92`) always emits all three fields, so a two-field object cannot come from this writer — it is either corruption or forgery, and decode accepts it either way.

### bc4-3 -- Mount lease and gc/state default their liveness fields to the least-safe value (High)

- **Anchor**: `Formats/CasServerRootFormats.cpp:147-169` — `decodeMountLease` requires only `su` and `we`; `eat` (`:163`), `ma` (`:164`) and `fen` (`:165`) are optional and default to `0`, `0`, `false`. Same shape in `Formats/CasGcStateFormat.cpp:50-63`, where `saw_gcs` is the only presence flag and `rnd`/`sg`/`spt`/`lo`/`ls` all default to zero.
- **Crafted input**: `{"type":"cas_mount_lease","v":9}\n{"su":"<32 lowercase hex>","we":"7"}\n`. For gc/state: `{"type":"cas_gc_state","v":9}\n{"gcs":1}\n`.
- **Consequence**: `Pool/CasServerRoot.cpp:200` decides liveness as `!surviving.gc_fenced && surviving.expires_at_ms > now_ms`. With `expires_at_ms` defaulted to 0 the lease of a **running** server is judged dead and reclaimable, and `gc_fenced` defaulting to `false` clears the GC fence that `:327`, `:345`, `:492`, `:664` and `:804` all key off. Both defaults point away from safety: the absent field grants exactly the permission the present field would have denied. For gc/state, `lease.seq` defaulting to 0 rewinds the GC lease generation (`Gc/CasGc.cpp:3143` `++next.lease.seq`, `:2347` compares owner+seq), so two GC instances can converge on generation 1, and `round`/`snap_generation` rewind to 0.
- **Evidence**: contrast `Formats/CasRefSnapshotFormat.cpp:173` and `Formats/CasRefCatalogFormat.cpp:201-238`, which do enforce presence and pairing for every load-bearing field. The shared layer provides no `require()` helper, so whether a field is mandatory is decided independently in each of 17 decoders.

### bc4-4 -- Fold-seal meta line has neither a required-field check nor the junk check every other format has (Medium)

- **Anchor**: `Formats/CasFoldSealFormat.cpp:294-305`. The meta block reads `g`/`pg` and closes without `if (!m.eof()) throw`, and without any `saw_g`. Every sibling decoder has that check: `CasPartManifestFormat.cpp:152`, `CasRefLogFormat.cpp:319`, `CasRefSnapshotFormat.cpp:175`, `CasPoolMetaFormat.cpp:144`, `CasGcStateFormat.cpp:66`.
- **Crafted input**: a fold seal whose second line is `{"g":"5","pg":"4"}xxxxxxxx` — the trailing bytes on that line are silently discarded. Separately, a seal whose meta line is `{}` decodes with `generation = 0` on any path that passes `expected_generation = nullopt`.
- **Consequence**: two byte-distinct fold seals decode identically, so a fold seal cannot be compared by bytes and any future byte-level integrity check would disagree with the decoder. The missing `g` is caught on the GC path (`:327` compares against `expected_generation`) but not by `Tools/CasInspect.cpp:562`, which renders generation 0 for an object that declares nothing — an operator reading `ca-inspect` output is told a specific generation that was never in the object.
- **Evidence**: the record loop at `:470` does have the junk check; only the meta block omits it, which reads as an oversight rather than a policy.

### bc4-5 -- Two of the four fold-seal decode entry points skip structural validation (Medium)

- **Anchor**: `Formats/CasFoldSealFormat.cpp:286` (two-arg overload, no validation) vs `:476-483` (four-arg overload, which calls `validateFoldSealStructure` with the layout and `gc_shards`). Production callers of the unvalidated overload: `Gc/CasOrphanManifestSweep.cpp:90` and `Tools/CasFsck.cpp:663`. The declaration at `Formats/CasFoldSealFormat.h:106` gives `expected_generation` a default argument, so the weaker overload is also the easier one to call.
- **Crafted input**: a seal carrying `{"k":"cnd","shard":18446744073709551615,"ct":0,"pt":0,"ocr":"0"}` or a `btr` record whose `key` is an arbitrary object key (`:433` reads it as a free-form `String` with no layout check). `shard` comes from `readU64Number`, which is unbounded here.
- **Consequence**: the same object is rejected on the GC adoption path and accepted by the orphan-manifest sweep and by fsck. The sweep and fsck then treat attacker-chosen strings as run keys and dereference them (`Tools/CasFsck.cpp:663` iterates `blob_target_runs` directly), and `condemned_summary` gains entries for shards outside `[0, gc_shards)`, which `Gc/CasGc.cpp:2555` reads when deciding whether condemned work remains.
- **Evidence**: `validateFoldSealStructure` is the only place shard bounds and run-key well-formedness are checked; it is reachable from `decodeFoldSeal(data, layout, gc_shards, ...)` and from `validateFoldSealForWrite` only.

### bc4-6 -- zstd `openObject` allocates the declared frame content size before decompressing (Medium)

- **Anchor**: `Formats/CasTextFormat.cpp:387-399`. `ZSTD_getFrameContentSize` is rejected only for `UNKNOWN`/`ERROR` and compared against `object_cap`; then `out.resize(content)` runs **before** `ZSTD_decompress`, and the `got != content` check happens after.
- **Crafted input**: a ~50-byte zstd frame whose header declares 256 MiB of content, stored under a `cas_part_manifest` or `cas_gc_outcomes` key (both `Always`-compressed with a 256 MiB cap; `cas_ref_log`/`cas_ref_snap` give 64 MiB). Decompression fails and the object is rejected — after the allocation.
- **Consequence**: roughly five-million-fold memory amplification per read request, zero-filled by `String::resize` so it is resident, not just reserved, and repeatable for every read of the object. Because the cap is per-format rather than per-request, concurrent readers of the same poisoned manifest multiply it. The declared size is attacker data being trusted for sizing before any evidence that the frame actually contains that much.
- **Evidence**: the raw branch at `:378` correctly checks the *actual* size; only the compressed branch trusts a declaration. Note the interaction with the sibling finding that `Backend::get` already materialised the stored bytes before `openObject` is called: the two allocations are additive.

### bc4-7 -- Blob envelope: the one self-describing identity field is silently truncatable on write and never read back (Medium)

- **Anchor**: `Formats/CasBlobEnvelopeFormat.cpp:74-87` (`writeEnvelopeRefField` stops appending when the escaped length would exceed the header budget, with no error) and `:146` (`decodeEnvelopeHeader`'s second parameter is unnamed — `uint64_t  ,` — so the `object_size` promised by the declaration at `Formats/CasBlobEnvelopeFormat.h:51` is discarded). The sole caller is `Tools/CasInspect.cpp:571`; the server read path takes its payload offset from pool metadata instead (`Pool/CasManifestReader.cpp:141`, `.offset = meta.blob_header_len`).
- **Crafted input**: any blob whose envelope `ref` was truncated at write time (a long intended ref under a 240-byte `blob_header_len`), or a forged envelope whose `ref`/`tag`/`bld` name a different object entirely.
- **Consequence**: `intended_ref` is a prefix of the real ref with no marker that truncation happened, so it can alias another ref; and since nothing on the read path ever decodes the envelope, neither the truncation nor an outright forgery is detectable at read time. `payloadOffset` (`Formats/CasBlobEnvelopeFormat.h:53-56`) returns `header.header_len`, which the server never obtains from the object — it comes from `PoolMeta`. A blob written under a different `blob_header_len` is therefore sliced at the wrong offset and its envelope JSON is returned as file content, with no decode error anywhere.
- **Evidence**: extends the sibling finding that the envelope *version* is checked only by `ca-inspect`; the new part is that the unused `object_size` parameter means even `ca-inspect` cannot bound `header_len` against the object, and that the write side truncates silently rather than refusing.

### bc4-8 -- Ref-log op records silently drop known-but-misplaced fields (Low)

- **Anchor**: `Formats/CasRefLogFormat.cpp:192-212`. For `NamespaceBirth`, `RemoveNamespace` and `EpochSeal` the switch body is a bare `break`, so `rn`, `ts`, `me`/`mb`/`mo` and both binding groups are parsed and discarded. `SetPublishedAt` likewise ignores any binding fields, and `OwnerTransition` ignores `rn`/`ts`.
- **Crafted input**: `{"op":"epoch_seal","rn":"a/b","ts":1,"nbk":"precommit","nrn":"x","nme":"1","nmb":"1","nmo":1}` inside an otherwise valid ref-log transaction.
- **Consequence**: two byte-distinct log objects decode to the same `RefLogTxn`. Ref-log objects carry no digest — the only binding is body `(ns, we, rs)` against the key (`:324`) — so the extra fields persist untouched in the durable log. A build that later gives those keys meaning for these op kinds would reinterpret already-committed history, and today they are a free covert channel inside a "strictly validated" record.
- **Evidence**: `CasRecordStreamFormat.cpp:287-288` does exactly the right thing for the analogous case, throwing `non-condemned record carries condemned fields`. The ref log, which is the more consequential format, does not.

### bc4-9 -- Bodies accept non-canonical numeric spellings that the key parser rejects (Low)

- **Anchor**: `Formats/CasTextFormat.cpp:193-215`. `readU64String` accepts anything `readIntText` accepts followed by EOF, and `readU64Number` does not even require non-emptiness. `readIntText` accepts a leading `+` (`src/IO/readIntText.h:55`) and unlimited leading zeros; it rejects `-` for unsigned types (`:82-90`), so that one direction is safe. Contrast `Formats/CasLayout.cpp:12-24`, where `parseCanonicalU64` rejects leading zeros, rejects non-digits, and uses `std::from_chars` so overflow returns `nullopt`.
- **Crafted input**: `{"we":"+7","rs":"0000000000000000000000007"}` in a ref-log meta line, or `{"n":+0}` as a trailer.
- **Consequence**: infinitely many byte encodings per logical object, in every format except `cas_part_manifest` (whose re-encode digest happens to catch it). Round-trip stability is therefore not a property of the family, which matters because it is the assumption behind comparing objects by bytes during recovery and behind the fold-seal reservation arithmetic. It also means the `DO_NOT_CHECK_OVERFLOW` wrap a sibling reported has no canonical-form backstop in the body reader, even though the key reader for the same values has one.
- **Evidence**: `readU32Number` (`:217-223`) range-checks against `uint32_t::max` *after* calling `readU64Number`, so its bound is only as good as the wrap-prone read beneath it — the check cannot see a value that already wrapped.

### bc4-10 -- GC outcome log does not require the outcome it exists to record (Low)

- **Anchor**: `Formats/CasGcOutcomesFormat.cpp:101-113` — presence is tracked for `ha`, `h` and `tt` only; `k` and `oc` fall through to the defaults `ObjectKind::Blob` and `OutcomeKind::Spared` (`Formats/CasGcOutcomesFormat.h:23,26`).
- **Crafted input**: `{"ha":"ch128","h":"<32 hex>","tt":"etag","tv":"x"}` as an outcome record.
- **Consequence**: the default is in the safe direction (`Spared`, not `Deleted`), so this is not a safety bug — but it silently rewrites history in the one artifact that exists to tell an operator what GC did. A record whose `oc` was lost to corruption reads back as "spared" with full confidence, and `Gc/CasGc.cpp:744` merges such a decoded log back into the object it re-publishes, making the rewrite durable.
- **Evidence**: `encodeOutcomeLog` (`:48-59`) always writes both keys, so their absence is never legitimate.

## Checked and sound

Confirmed non-issues, listed because each is the obvious place a decode audit would expect a bug:

- **Untrusted-length allocation**: `readFixedBytes` (`Primitives/CasCodecUtil.h:37-45`) bounds `n` by `in.available()` before constructing the string. The part-manifest inline-payload path (`CasPartManifestFormat.cpp:253`) is the only consumer, and `inline_lens` is pushed exactly once per entry (`:227`, `:233`) so `inline_lens[i]` at `:247` can never be out of range. No wrapped `il` can drive an allocation.
- **Record injection / truncation via string values**: impossible. `CasJsonWriter::stringValue` escapes `"`, `\` and every byte `< 0x20` including `\n`, plus U+2028/U+2029 (`CasTextFormat.cpp:76-94`). The only unescaped emission of untrusted data anywhere is the part-manifest banner, which is bc4-1.
- **Bounds on all `substr`/suffix arithmetic in `CasLayout.cpp`**: `:42` guards the `.meta` strip by size; `:61` requires `hex.size() >= 2` before `hex.substr(0, 2)`; `:74` matches hex width to the algorithm; `:218-227` fixes the ordinal field at six digits and range-checks the result. `parseCanonicalU64` is overflow-safe.
- **`cas_run` is the best-hardened format in the family**: whole-file CityHash128 verified against the fold seal's `RunRef.checksum` (`CasRecordStreamFormat.cpp:303-310`), strict keys, trailer count, `!hashing.eof()` after the trailer, `parseB` width-matching (`:57-74`), and explicit rejection of condemned fields on non-condemned rows. `Gc/CasBlobInDegree.cpp:557-575` verifies before returning, so a mismatch discards the candidate list via the exception rather than acting on it.
- **`cas_ref_snap` and `cas_ref_catalog`** enforce required fields, pairing rules, strict ascending order with no duplicates, canonical ref names, and the namespace admission byte bound — the model the other formats should follow.
- **Second escaper divergence is benign**: `CasBlobEnvelopeFormat.cpp:48-72` implements its own `escapedLen`/`appendEscaped` that omits the U+2028/U+2029 handling of the shared writer. Both still escape quotes, backslashes and control bytes, so the output remains valid JSON and no injection is reachable; the duplication is a maintenance hazard, not a defect.
- **`cas_gc_maintenance_state`** is the only decoder that enforces its own `object_cap` before parsing (`CasGcMaintenanceStateFormat.cpp:34-37`) and re-checks the cursor bound after decode. Worth generalising.
- **`traitsFor` / `traitsForType`** (`CasFormat.cpp:122-136`) have no fallthrough default; an unknown `FormatId` throws `LOGICAL_ERROR` and an unknown type string returns `nullptr`, which `sniffHeaderLine` handles as `nullopt`.
- **Vocabulary decoding** (`CasWireVocab.cpp`, `CasRefWireVocab.cpp`) is exhaustive word→enum with a throw on the unknown case; no integer is ever cast into an enum from untrusted input except `algos_used`, which `validatePoolAlgosUsed` (`CasPoolMetaFormat.cpp:32-51`) checks by round-tripping through `blobHashAlgoName`.

## Coverage

Read in full: `CasTextFormat.{h,cpp}`, `CasFormat.{h,cpp}`, `CasByteBudget.h`, `CasRecordStreamFormat.cpp`, `CasPartManifestFormat.cpp`, `CasBlobEnvelopeFormat.{h,cpp}`, `CasPoolMetaFormat.cpp`, `CasWireVocab.cpp`, `CasGcStateFormat.cpp`, `CasGcOutcomesFormat.{h,cpp}`, `CasGcMaintenanceStateFormat.cpp`, `CasBlobMetaFormat.cpp`, `CasServerRootFormats.cpp`, `Primitives/CasCodecUtil.h`.
Decode halves read: `CasFoldSealFormat.cpp:250-490`, `CasRefLogFormat.cpp:120-399`, `CasRefCatalogFormat.cpp:100-360`, `CasRefSnapshotFormat.cpp:138-286`, `CasRefCkptFormat.cpp:85-146`, `CasLayout.cpp:1-240`.
Consumers traced to establish consequences: `Pool/CasServerRoot.cpp` (lease liveness), `Pool/CasManifestReader.cpp` (payload offset), `Gc/CasBlobInDegree.cpp` (condemn graduation, run verification), `Gc/CasGc.cpp` (lease generation, outcome merge, condemned summary), `Gc/CasOrphanManifestSweep.cpp` and `Tools/CasFsck.cpp` (fold-seal overload choice), `Tools/CasInspect.cpp` (sole envelope decoder), `src/IO/readIntText.h` (sign and canonical-form behaviour).
Not read: encode halves of the large ref/fold formats beyond what was needed for encode/decode asymmetry, `CasLayout.cpp:240-321`, `CasLayout.h` key builders, and the `Tools/` renderers. No CAS tests exist in this working tree, so nothing here is corroborated by execution — all claims are static.
