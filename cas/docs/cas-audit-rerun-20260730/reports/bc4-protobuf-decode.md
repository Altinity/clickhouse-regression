# bc4-protobuf-decode — re-run 2026-07-30

## Scope in current code

- Files/dirs walked: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/**` — full read of the codec surface:
  - `CasFormat.{h,cpp}` (traits table, compat gate, per-format `object_cap` / `line_cap`)
  - `CasTextFormat.{h,cpp}` (line reader, `JsonObjectReader`, `openObject` size-cap enforcement, header/trailer)
  - `CasBlobEnvelopeFormat.{h,cpp}` (blob envelope; former `logical_size`/`header_hash` surface)
  - `CasPartManifestFormat.{h,cpp}` (manifest; former duplicate-path check)
  - `CasRecordStreamFormat.{h,cpp}` (NDJSON record stream — replaces the removed `RunFileReader` binary format)
  - `CasFoldSealFormat.{h,cpp}` (fold seal; former `decodeFoldSeal` enum casts)
  - `CasServerRootFormats.{h,cpp}` (root-shard replacement: text/JSON singletons `owner` / `epoch` / `mount`)
  - `CasWireVocab.{h,cpp}`, `CasRefWireVocab.{h,cpp}` (word-based enum validation)
  - `CasBlobMetaFormat.{h,cpp}`, `CasGcStateFormat.{h,cpp}`, `CasGcOutcomesFormat.{h,cpp}`,
    `CasRefLogFormat.{h,cpp}`, `CasRefSnapshotFormat.{h,cpp}`, `CasPoolMetaFormat.{h,cpp}` (cross-checked)
  - `Formats/README.md` (evolution rules — explicitly: "no binary CAS formats and no protobuf dependency")
- Grep sweeps (whole CAS tree): `protobuf|proto3|ParseFromArray|ParseFromString|CodedOutputStream|SerializeToArray|
  ::Proto::` → **0 hits in production code** (README.md line explicitly states no protobuf). Also swept for
  `logical_size`, `header_hash`, `RunFileReader`, `klen`, `plen`, `prev_path`, `manifest_hard_limit`,
  `folded_token_type` → all removed from the format surface (only stale-comment residue remains in
  `Backend/CasBackend.h:219`).

## Findings still present

None from this audit's original CAS-### set. See "fixed" section.

## Findings fixed / no longer reproducible

- **CAS-026** — Protobuf `ParseFromArray` with unchecked size / OOM DoS.
  - Fix: the entire protobuf surface (`Cas::Proto::RootShardManifest`, `RootShardCodec.cpp`) is removed;
    the object inventory is text/JSON end-to-end. Every codec now enforces a per-format `object_cap`
    on the stored bytes *before* decode, and, for `Always`-compressed formats, on the declared zstd
    content size before decompression.
  - Fix anchor: `Formats/CasTextFormat.cpp:389` (raw-object cap) and `Formats/CasTextFormat.cpp:401`
    (declared decompressed size cap); trait table at `Formats/CasFormat.cpp:93–109`. Compat gate at
    `Formats/CasFormat.cpp:64–70` runs after the size cap gate.
- **CAS-027** — Additive protobuf fields dropped on re-encode by an older build → silent data loss.
  - Status: **by-design / documented**, not "fixed" in the strict sense. The mutable-object formats
    (`RefLog`, `RefSnapshot`, `PoolMeta`, `MountLease`, `GcState`, `BlobMeta`, envelope) use
    `KeyStrictness::Tolerant` and `JsonObjectReader::skipUnknown` silently drops unknown non-`!` keys
    (`Formats/CasTextFormat.cpp:245–256`). An old build that decodes, mutates in-struct, and re-encodes
    will lose additive fields. The rule is now explicit in `Formats/README.md:46–51`: additive change =
    "field is best-effort until the pool floor rises (an old writer's fresh re-encode drops it)".
    Deterministic write-once artifacts (`FoldSeal`, `RunFile`) are `KeyStrictness::Strict`
    (`Formats/CasFormat.cpp:101–102`) → unknown keys fail closed instead of dropping. The
    critical-extension safety net (`!`-prefixed keys → `UNKNOWN_FORMAT_VERSION`) is at
    `Formats/CasTextFormat.cpp:249–251`.
  - Evolution rule anchor: `Formats/README.md:46–51`.
- **CAS-028** — `RunFileReader::next()` OOB via unchecked `klen`/`plen` binary lengths.
  - Fix: `RunFileReader` (binary variable-length record with `klen`/`plen`) is deleted. The equivalent
    is `Formats/CasRecordStreamFormat.cpp` `SourceEdgeRunReader::next` (lines 228–304): each record is
    one NDJSON line read via `readLine(hashing, traitsFor(FormatId::RunFile).line_cap, "cas_run")`
    (`CasRecordStreamFormat.cpp:233`). `readLine` enforces the 4 KiB `line_cap`
    (`Formats/CasTextFormat.cpp:281–296`) and hard-fails on missing `\n`. There is no
    length-prefixed field over which an attacker can force a substr/OOB.
- **CAS-039** — Envelope `logical_size` uint64 wrap bypasses `header_len + logical_size == object_size`.
  - Fix: the envelope no longer carries `logical_size`. `Formats/CasBlobEnvelopeFormat.h:53–74`
    explicitly documents the field drop ("does not duplicate identity or unused integrity metadata …
    `header_hash` had no consumer once the CityHash64 check left the envelope"). The header is now a
    fixed-width JSON descriptor pad-verified to `blob_header_len-1` and `\n` at `blob_header_len-1`
    (`CasBlobEnvelopeFormat.cpp:230–248`); the payload length is derived downstream as
    `object_size - header_len` (`CasBlobEnvelopeFormat.h:86–89`), with no user-supplied length to
    overflow.
- **CAS-075** — Envelope `header_hash` (CityHash64) covers only the 94-B core, not TLVs.
  - Fix: `header_hash` is removed entirely (`CasBlobEnvelopeFormat.h:53–58`). No secondary "critical
    extension" hash relies on writer honesty; the descriptor is a single JSON object whose length is
    derived from the `\n` position and whose pad zone must be all ASCII spaces
    (`CasBlobEnvelopeFormat.cpp:230–248` — "no smuggling"). Critical extensions are enforced by the
    `!`-key gate in `JsonObjectReader::skipUnknown` (`Formats/CasTextFormat.cpp:249–251`).
- **CAS-077** — `decodeFoldSeal` casts `folded_token_type` / `classification` enums without validation.
  - Fix: `folded_token_type` is now decoded as a word by `tokenTypeFromWord(...)` at
    `Formats/CasFoldSealFormat.cpp:190` (validating decoder in `Formats/CasWireVocab.cpp`, throws
    `CORRUPTED_DATA` on unknown word). The sibling word decoder `nsCleanupStateFromWord`
    (`CasFoldSealFormat.cpp:32–37`) and record-kind gate (line 248) also fail closed. `ShardCoverage`
    `classification` is a `uint8_t` (`CasFoldSealFormat.h:39`), no longer an enum — it is written only
    from a fixed set {0,1,2,4} in `Gc/CasGc.cpp` (lines 1452, 1596, 1621, 2668, 2699) and never used as
    a branch condition anywhere (`rg 'classification (==|!=|<|>|&|\|)'` in the tree → 0 hits), so an
    unvalidated decoded byte cannot mis-drive any control flow. `decodeFoldSeal` also enforces
    `KeyStrictness::Strict` on both the meta line (`CasFoldSealFormat.cpp:139`) and every record line
    (line 154) → any unknown key is `CORRUPTED_DATA`.
- **CAS-115** — Manifest duplicate-path detection is adjacent-only (`prev_path` check).
  - Fix: manifest decode now enforces STRICT ascending order across the whole entry sequence
    (`Formats/CasPartManifestFormat.cpp:257–267`): `if (!m.entries.empty() && !(m.entries.back().path
    < e.path)) throw CORRUPTED_DATA(...)`. The comment explicitly explains why this catches
    non-adjacent duplicates: a forged entry `c` whose path equals earlier `a` still fails against its
    immediate predecessor `b` because `a<b`, so `c(=a) < b` and the strict `<` fails. Encode side is
    also stricter: `sorted[i]->path == sorted[i-1]->path` throws on encode
    (`CasPartManifestFormat.cpp:86–87`).

## New findings (not in original audit)

- **NEW-bc4-protobuf-decode-1 (Info)** — `Backend/CasBackend.h:219` has a stale doc comment referring to
  the deleted `RunFileReader`. Harmless, but a rename to "record-stream reader" would keep the docstring
  aligned with the current `SourceEdgeRunReader` / `CasRecordStreamFormat` naming.
- **NEW-bc4-protobuf-decode-2 (Info)** — `ShardCoverage::classification` is decoded as an unvalidated
  `uint8_t` (`Formats/CasFoldSealFormat.cpp:189`). No consumer branches on it today (see CAS-077 above),
  so this is *cosmetic*, but the persisted byte is documented at `CasFoldSealFormat.h:32–36` as having
  four defined values (0/1/2/4); a `switch`-based decoder that rejects unknown values would enforce the
  documented invariant and would be forward-safe if a future consumer starts branching. Severity: Info.

## By-design / N/A / info

- The B4 audit's original target (`RootShardCodec.cpp` protobuf surface) does not exist in the current
  tree. The functional equivalent — per-server-root singletons — is now three canonical text objects
  (`OwnerObject`, `ServerEpoch`, `MountLease`) with strict body-line + trailing-bytes checks and
  compat-gated readers (`Formats/CasServerRootFormats.cpp`). No protobuf runtime is linked.
- `Formats/README.md:9–13` explicitly commits to the text-only inventory. This is the authoritative
  contract for the batch and matches every codec in `Formats/`.
- The tolerant/strict split (`Formats/CasFormat.cpp:93–109` `KeyStrictness` column) intentionally makes
  write-once artifacts fail-closed on unknown keys while allowing mutable control objects to skip them
  for rolling upgrade. See CAS-027 for the residual "additive-drop on old-build re-encode" risk which
  is documented rather than eliminated.
- All formats hitting the decode path go through `openObject(FormatId, stored)`
  (`Formats/CasTextFormat.cpp:389 / 401`) which enforces `object_cap` **before** decompression /
  ParseX-equivalent parsing — the CAS-026 style unbounded-parse pattern cannot be reintroduced without
  bypassing `openObject`.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-026 | Med | ✅ fixed | `Formats/CasTextFormat.cpp:389,401` (`object_cap` pre-decode); no `ParseFromArray` in tree |
| CAS-027 | Med | 📐 by-design | `Formats/CasTextFormat.cpp:245–256` (`skipUnknown` on Tolerant); rule documented `Formats/README.md:46–51` |
| CAS-028 | Med | ✅ fixed | `Formats/CasRecordStreamFormat.cpp:228–304` (NDJSON `readLine` w/ `line_cap`); no `klen`/`plen` |
| CAS-039 | Med | ✅ fixed | `Formats/CasBlobEnvelopeFormat.h:53–74` (`logical_size` dropped); `CasBlobEnvelopeFormat.cpp:230–248` (pad-verify) |
| CAS-075 | Med | ✅ fixed | `Formats/CasBlobEnvelopeFormat.h:53–58` (`header_hash` removed); `!`-key gate `CasTextFormat.cpp:249–251` |
| CAS-077 | Low | ✅ fixed | `Formats/CasFoldSealFormat.cpp:190` (`tokenTypeFromWord`), `:32–37` (`nsCleanupStateFromWord`), Strict decode |
| CAS-115 | Med | ✅ fixed | `Formats/CasPartManifestFormat.cpp:257–267` (strict-ascending check catches non-adjacent duplicates) |

### Counts

- Findings still present: **0**
- Fixed / no longer reproducible: **6** (CAS-026, CAS-028, CAS-039, CAS-075, CAS-077, CAS-115)
- By-design / documented: **1** (CAS-027)
- New findings: **2** (both Info) — stale comment, unvalidated `classification` byte
