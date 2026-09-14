# bc1-offset-overflow -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Formats/CasTextFormat.{h,cpp}`, `Formats/CasLayout.cpp` (`parseCanonicalU64`), `Formats/CasPartManifestFormat.cpp` (decode `sz`), `Formats/CasPoolMetaFormat.cpp`, `Formats/CasGcStateFormat.cpp`, `Formats/CasByteBudget.h`, `Pool/CasManifestReader.cpp` (`locate`), `Pool/CasPartWriteTxn.cpp` (`ensureBlobPresent` size checks), `ContentAddressedMetadataStorage.cpp` (`getBlobViewPlan`, `readBlobPayload`, `getLastModified`), `Gc/CasGc.cpp` (`newestFoldSealRef`, `probeGenerationForSeal`, rebuild `max_gen`), `src/IO/readIntText.h`, `src/IO/ReadBufferFromFileView.{h,cpp}`.
- Explicitly out of scope: write-protocol blob publish rewrite except the arithmetic on `offset`/`length`; mtime *semantics* (bc6) except the `published_at_ms` multiplication; `gc_shards` allocation-as-DoS (loud fail-closed, CAS-039).

## Findings
### bc1-1 -- `location.offset + location.length` still wraps; the read window collapses to EOF (Medium)
- Anchor: `ContentAddressedMetadataStorage.cpp:2062-2064,2076-2079` (`getBlobViewPlan`, `readBlobPayload`); `Pool/CasManifestReader.cpp:156-160` (`locate`); `Formats/CasPartManifestFormat.cpp:230,255` (decode `sz`); `src/IO/ReadBufferFromFileView.h:22` (`tryGetFileSize` = `right_bound - left_bound`) at ceee42c
- Trigger: a decoded blob entry whose `sz` is large enough that `blob_header_len + sz` wraps `uint64_t` (e.g. `sz = 2^64 - 100` with default `blob_header_len = 256`). The writer path cannot produce this: `ensureBlobPresent` derives logical size from the HEAD (`CasPartWriteTxn.cpp:337-351`). A forged or bit-flipped manifest that still passes `payload_digest` (unkeyed CityHash128 of the re-encode) can.
- Evidence: decode stores `e.blob_size = *sz` with no range check. `locate` sets `.offset = meta.blob_header_len`, `.length = entry.blob_size`. Both read sites compute `location.offset + location.length` four times and pass the sum to `StoredObject` and `ReadBufferFromFileView` with no overflow test and no `offset <= end` check. After wrap, `payload_end < payload_offset`; the file view's working buffer collapses and every read returns EOF. `tryGetFileSize()` underflows to a huge size. The failure is a silent empty/wrong read, not `CORRUPTED_DATA`. Same root as the CAS-037 residual Filimonov kept.
- Notes: same root as CAS-037. The previous High "wrapping defeats every decoder range gate" thesis is not re-raised: most range gates still see the wrapped value and refuse it (e.g. `validatePoolBlobHeaderLen` after a wrap-to-400 is the remaining readIntText residual, bc1-3). This finding is only the *read-window* wrap, which has no subsequent gate.

### bc1-2 -- GC generation listing still uses `std::stoull`; `-1` wraps `max_gen + 1` to 0 (Medium)
- Anchor: `Gc/CasGc.cpp:1354` and `:1404` (`newestFoldSealRef`); `:1485` (`probeGenerationForSeal`); `:3960` and `:3968` (rebuild `max_gen + 1`) at ceee42c
- Trigger: a single listed key `<prefix>/gc/gen/-1/...`. `std::stoull("-1")` does not throw; it returns `2^64-1`. The `catch (...) { return; }` therefore never fires.
- Evidence: `parseCanonicalU64` (`Formats/CasLayout.cpp:16-28`) rejects `-`, leading zeros, and overflow via `std::from_chars` and is the parser for layout keys. These three listing paths do not use it. Consequences: (a) rebuild sets `generation = max_gen + 1` which wraps to `0`, a value the fold-seal validators treat as the never-sealed sentinel; (b) `newestFoldSealRef`'s probes compute `listed_max_generation + above` which wrap to `0` and `1`, so the "seal above the listing maximum" check actually probes generation 1 — present in any pool that has sealed and not yet pruned — and throws the terminal "this pool must be recreated" verdict. The attempt component at `:1491` is protected by a `foldSealKey` re-render check; the generation components are not.
- Notes: same residual as CAS-037.

### bc1-3 -- `readU64Number` still wraps mod 2^64 (Low)
- Anchor: `Formats/CasTextFormat.cpp:216-223` (`readU64Number`); `src/IO/readIntText.h:25` (default `DO_NOT_CHECK_OVERFLOW`) at ceee42c
- Trigger: a JSON number whose decimal spelling exceeds `2^64-1` (or is empty). The helper returns the wrapped value; `readU32Number` then compares the *already wrapped* u64 to `uint32::max`.
- Evidence: `parseCanonicalU64` and `ContentAddressedMetadataStorage.cpp:340-346` (age parse) already use `from_chars` and reject `-` / overflow. Only the JSON body readers still call wrapping `readIntText`. A wrap that lands *inside* a later range gate (e.g. `hln` wrapping to 400, which `validatePoolBlobHeaderLen` accepts) is the only remaining decoder-gate residual. Writer-produced objects never emit such spellings. Not the previous "every range gate is defeated" claim.
- Notes: CAS-037 residual, narrowed.

### bc1-4 -- `published_at_ms / 1000` is passed to `Poco::Timestamp::fromEpochTime` without a range check (Low)
- Anchor: `ContentAddressedMetadataStorage.cpp:1729-1732`; source field `Formats/CasRefSnapshotFormat.cpp:226` (`ts = r.readU64Number()`) at ceee42c
- Trigger: a ref snapshot/log row with `ts` large enough that `ts/1000 * 1e6` overflows signed `Int64` inside Poco.
- Evidence: decode stores `published_at_ms` with no upper bound. The write path only ever stamps `nowMs()` (`CasPartWriteTxn.cpp:919`). `getLastModified` is what MergeTree uses for column-modification display and some cleanup TTLs. A wrapped mtime is a wrong stamp, not data loss.
- Notes: same class as the previous published_at multiplication finding.

## By-design / info / non-actionable
- `gc_shards` still has no upper bound at decode or settings (`CasPoolMetaFormat.cpp:165-166`, `ContentAddressedSettings.cpp:226`). A huge value fails closed on `std::vector(gc_shards)` (`CasGc.cpp:3044,3975`). Loud allocation refusal, not silent wrap. CAS-039.
- Write-path size arithmetic is saturating-safe: `ensureBlobPresent` refuses `head.size < blob_header_len` before subtracting (`CasPartWriteTxn.cpp:337-351`); `retiredLogicalSize` does the same (`CasGc.cpp:257-265`).
- `parseCanonicalU64` is overflow-safe and canonical-only. The defect is that the three GC listing parsers do not call it.

## Closed-since-2026-08-12
- The High "every CAS numeric field silently wraps, defeating all decoder range gates" thesis is closed as overstated (Filimonov CAS-037). The helper still wraps; the gates are not uniformly defeated.
- `blob_header_len - 1` underflow in the envelope encoder remains latent: `validatePoolBlobHeaderLen` still pins `[240, 16384]` before any encode call.

## Coverage
- Reviewed: JSON u64 readers; manifest `sz` → `locate` → read-window sums; GC generation `stoull` + `+ 1` / `+ above`; `published_at_ms` → Poco; write-path header-len subtraction; `parseCanonicalU64` vs listing parsers.
- N-A: protobuf varint (gone; see bc4).
- Deferred: bulk of `CasRefLedger.cpp` arithmetic (pattern-swept only).
