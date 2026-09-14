# bc4-protobuf-decode -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: whole `Formats/` tree (39 files); `Primitives/CasCodecUtil.h`; `Gc/CasOrphanManifestSweep.cpp` (undecodable skip); `Pool/CasPartWriteTxn.cpp` (`computePayloadDigest` call); grep for `protobuf`, `.proto`, `google::protobuf` under the CAS root and adjacent Disks/CAS hooks.
- Explicitly out of scope: `readU64Number` wrap (bc1); placement classifier (bc5).

Protobuf is gone. There is no `.proto`, no varint reader, no wire-tag dispatch anywhere under
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` (grep: no matches). Every persisted
CAS object is self-describing text (NDJSON / control line + payload zone). The protobuf fail-open
question is N/A. The rest of this report is the remaining text/NDJSON decoder surface that used to
be CAS-038 / CAS-040 / CAS-041.

## Findings
### bc4-1 -- outcome-log `oc` is still optional and defaults to `Spared` (Low)
- Anchor: `Formats/CasGcOutcomesFormat.cpp:109` (`else if (key == "oc")`); `Formats/CasGcOutcomesFormat.h:38` (`outcome = OutcomeKind::Spared`) at ceee42c
- Trigger: a record that has `ha`/`h`/`tt` but omits `oc`. Decode succeeds.
- Evidence: required-field check at `:113` is `have_ha && have_h && have_tt` only. A missing `oc` keeps the struct default `Spared`. Writer-produced logs always emit `oc`. Effect of a truncated/forged record is "this candidate was spared" (retention, not deletion). Cosmetic / fail-safe, not a delete accelerator.
- Notes: CAS-038 residual.

### bc4-2 -- `encodeGcState` has no write-side line-cap check (Low)
- Anchor: `Formats/CasGcStateFormat.cpp:19-36` (encode); `:43` (decode `readLine` with `line_cap`) at ceee42c
- Trigger: a `manifest_sweep_cursor` string long enough that the body line exceeds `traitsFor(GcState).line_cap` (64 KiB, `CasFormat.cpp:175`).
- Evidence: `encodeRefCatalog` refuses over-cap lines (`CasRefCatalogFormat.cpp:89-93`). `encodeGcState` writes the cursor with `writeStringValue` and does not call `fitsLineCap`. Decode then throws `CORRUPTED_DATA` ("line exceeds the …-byte cap"). Writer-produced cursors are object-store keys and stay small; the hole is encode/decode asymmetry, not a reachable wedge.
- Notes: CAS-038 residual.

### bc4-3 -- part-manifest `payload_digest` is still a canonical re-encode (Low)
- Anchor: `Formats/CasPartManifestFormat.cpp:301-309` (verify), `:314-324` (`computePayloadDigest` copies the manifest and calls `encodePartManifest`) at ceee42c
- Trigger: every successful `decodePartManifest`.
- Evidence: digest = CityHash128 of a deep-copied, `payload_digest`-zeroed re-encode. A foreign field is skipped under `KeyStrictness::Tolerant` (`:146`, `:232`) *before* the digest check, so an additive field does not produce `CORRUPTED_DATA` from the digest (the version gate still fires first on `v`). Cost: a full extra encode and two payload copies on every decode. The `Tolerant` policy is live, not dead, but it does not fail-open on unknown *critical* (`!`) keys (`skipUnknown` still rejects those).
- Notes: CAS-041 residual (cost + dormant Tolerant-vs-digest confusion). Not a fail-open.

## By-design / info / non-actionable
- **Protobuf N/A.** Confirmed by grep: no `protobuf` / `.proto` / `google::protobuf` under the CAS root. Decoder surface is `CasTextFormat` + per-format `while (r.nextKey)` dispatch.
- Blob-meta still requires only `st` (`CasBlobMetaFormat.cpp:87-88`); `cr`/`sz` default to 0. Writer always emits all three (`:50-54`). A two-field `{"st":"condemned"}` would graduate on the first GC pass. Bucket-credential forgery / truncation; loud only if later accounting disagrees. Not re-raised as Medium: same optional-field class Filimonov called cosmetic for CAS-038, and the writer is complete.
- Mount lease now requires `su`, `we`, *and* nonzero `write_attempt_id` (`CasServerRootFormats.cpp:178`). The old "identity-only, `eat`/`fen` optional" High is closed for the generation-10 floor. `eat`/`ma`/`fen` remain optional and default to 0/false; a lease missing `eat` looks already-expired to any wall-clock consumer. Writer always emits them.
- `gc/state` still requires only `gcs` (`CasGcStateFormat.cpp:64-67`); `rnd`/`sg`/… default to 0. An object `{"gcs":1}` decodes as never-sealed. Writer always emits the full set (`:26-33`).
- `readLine` is still EOF-safe and cap-bounded (`CasTextFormat.cpp:281-294`). Truncation is `CORRUPTED_DATA`, not a short read.
- `CasJsonWriter::stringValue` still escapes `"`, `\`, and every byte below 0x20, so a string value cannot close its own NDJSON line.

## Closed-since-2026-08-12
- CAS-040 / old bc4-1 (raw banner + newline in a projection path wedges GC): `bannerFor` now runs the path through `CasJsonWriter::stringValue` (`CasPartManifestFormat.cpp:65-78`). Encode and decode rebuild the same escaped banner. `2649bce42db` / `CasOrphanManifestSweep.cpp:879-896` skips an undecodable manifest, increments `undecodable`, and continues; it does not abort the pool-wide round.
- Protobuf decoder fail-open: N/A (symbol gone).

## Coverage
- Reviewed: protobuf absence; shared NDJSON layer; part-manifest banner/digest; gc/state and outcome-log required fields; orphan-sweep undecodable skip; mount-lease identity fields.
- N-A: protobuf wire decode (no `.proto`, no varint, no tag dispatch).
- Deferred: encode halves of the large ref/fold formats beyond encode/decode asymmetry needed for CAS-038/041.
