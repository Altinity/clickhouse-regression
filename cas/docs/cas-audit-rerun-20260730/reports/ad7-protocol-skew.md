# ad7-protocol-skew — re-run 2026-07-30

Scope: protocol skew / wire-vocab pinning on the CAS relink live wire (`DataPartsExchange` cookies + `PartManifest` payload). Static reasoning only. Findings anchored in current PR HEAD (`/Volumes/workspace/ClickHouse`, branch `cas-audit-20260730`).

## Scope in current code

- `src/Storages/MergeTree/DataPartsExchange.cpp` (relink sender/receiver framing; only CAS-adjacent hooks read).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedExchange.h` (relink wire contract).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp` (`prepareAdoptFromManifest`).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp` (`decodePartManifest`, path hygiene, canonical order).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.cpp` (`checkCompatibility`, `traitsFor`).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasBlobEnvelopeFormat.cpp` (`encodeEnvelopeHeader`, `decodeEnvelopeHeader`; note: decoder derives `header_len` from '\n', encoder pads to caller-passed `blob_header_len`).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPoolMetaFormat.cpp` (`validatePoolBlobHeaderLen`, `kMinBlobHeaderLen`).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPool.cpp` (`probePoolLifecycleGate` — pool identity compares `pool_id` + `blob_header_len`).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasManifestReader.cpp` (`locate()` uses `meta.blob_header_len`).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp` (`adoptEvidence` — tokenless dep, no HEAD).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartFolderAccess.cpp` (`prepareEntries`).

## Findings still present

None of the original SKEW-mapped findings (CAS-054, CAS-024, CAS-036, CAS-031, CAS-209) reproduce in their originally-reported form. See "fixed / no longer reproducible" below. One residual observation is downgraded but noted.

## Findings fixed / no longer reproducible

- **CAS-054 (SKEW-1/5/6) — Relink cookie value not validated ✅ FIXED.** The receiver now compares the cookie value against `CA_RELINK_COOKIE_VALUE` exactly and bails to a byte fetch on any mismatch, before consuming further stream bytes. The cookie value was also bumped to `"part_manifest_v2"` to disambiguate the now-trailing-field-free framing from `v1`.
  - Anchor: `src/Storages/MergeTree/DataPartsExchange.cpp:128` (`constexpr auto CA_RELINK_COOKIE_VALUE = "part_manifest_v2";`) and `:916-924` (mismatch → `LOG_INFO(... falling back to a byte fetch); return fall_back_to_byte_fetch();`).
  - Payload framing is also simplified in v2: only `writeStringBinary(sender_manifest_bytes, *in); assertEOF(*in);` — the bare trailing `Int32 metadata_version` from v1 is gone (`metadata_version.txt` is now an ordinary manifest entry). This eliminates the SKEW-6 "bare `Int32` trailer" hazard entirely.
  - Anchor: `src/Storages/MergeTree/DataPartsExchange.cpp:935-937`.

- **CAS-024 (STORE-2) — `locate()` uses fixed `blob_header_len` — mitigated by authoritative pool + envelope self-check ✅ FIXED-IN-EFFECT.** `CasManifestReader::locate` still uses `meta.blob_header_len` as `offset` (`src/.../Pool/CasManifestReader.cpp:158`), but three independent gates now close the "config drift / mixed-version writers" trigger:
  1. `blob_header_len` is written into `_pool_meta` at creation and is authoritative on reopen; `probePoolLifecycleGate` compares `fresh.blob_header_len == expected_blob_header_len` and declares `Replaced` on mismatch (`src/.../Pool/CasPool.cpp:123`). Local config drift cannot silently repoint the pool.
  2. All blob writers pass the pool's `meta.blob_header_len` into `encodeEnvelopeHeader`, which stamps `header.header_len` and pads to exactly that length (`src/.../Formats/CasBlobEnvelopeFormat.cpp:158`, callers at `Pool/CasPartWriteTxn.cpp:340,459,707,729`, `ContentAddressedTransaction.cpp:617,745`). There is no write path that would produce an envelope with a header_len differing from the pool's value.
  3. `decodeEnvelopeHeader` DERIVES `header_len` from the '\n' terminator rather than trusting a wire field, and rejects any non-space byte in the pad zone (`src/.../Formats/CasBlobEnvelopeFormat.cpp:230-248`). A pool_meta / envelope disagreement would fail-closed on any tool path that reads the envelope; the ranged-read path in `locate()` is skipped-over-envelope by construction and stays consistent as long as gate 1 holds.
  - Residual: `locate()` still does not read the envelope's own `header_len` before ranging; the reliance on gate 1 is a soft coupling. Not a new finding — same design surface as before, now bounded.

- **CAS-036 (BUILD-2) — `blob_header_len` floor 96 too small ✅ FIXED.** Floor is now 240 (a multiple of 8 comfortably above the 225-byte mandatory content computed at type maxima). Configuration below the floor throws `BAD_ARGUMENTS` at pool creation and `CORRUPTED_DATA` at pool-meta decode, not `LOGICAL_ERROR` at first write.
  - Anchor: `src/.../Formats/CasPoolMetaFormat.cpp:36` (`static constexpr uint64_t kMinBlobHeaderLen = 240;`), `:40-46` (`validatePoolBlobHeaderLen` gates `<240`, `% 8 != 0`, `> 16 KiB`).
  - Wired at pool creation via `PoolMeta::create` and at decode via `decodePoolMeta` (`Formats/CasPoolMetaFormat.cpp:159`).

- **CAS-031 (MW-1) — Relink receiver trusts sender-supplied `blob_size`/`path` 📐 BY-DESIGN, hardened.** `PartWriteTxn::adoptEvidence` still records the sender-supplied `entry.blob_size` verbatim with `adopted=true` (no HEAD/loadMeta): `deps[entry.ref] = BlobDepRecord{ObjectKind::Blob, std::nullopt, entry.blob_size, /*adopted=*/true};` (`src/.../Pool/CasPartWriteTxn.cpp:794`). The `entry.path` and `entry.blob_size` flow verbatim into `locate()` → ranged S3 GET (`CasManifestReader.cpp:158-160`). Interpreted correctly:
  - `entry.ref` (algo + digest) is the trust anchor; the blob key is derived from the digest (content-addressed), so a hostile/buggy sender cannot redirect the read to a different blob body it did not know the digest of. Digest hex width is validated at decode (`CasPartManifestFormat.cpp:241-245`).
  - Sender-supplied `path` is hygiene-checked at decode: rejects empty/absolute paths and any `""` / `.` / `..` segment (`CasPartManifestFormat.cpp:198-210`) and entries must be strictly-ascending / duplicate-free (`:257-267`). Traversal / duplicate-path forgery is closed.
  - Sender-supplied `blob_size` is not verified but has only two failure modes: (a) too small → truncated ranged read → downstream MergeTree decompression/checksum fails; (b) too large → over-read of the blob object → S3 range error or trailing garbage → downstream check fails. In both cases the manifest never promotes with silent misread of a *different blob's* payload because the object key is derived from the digest.
  - Design comment codifies the choice: "adopted leaves are TRUSTED via the durable manifest edge — NO per-file HEAD/loadMeta probe" (`CasPartWriteTxn.cpp:219`, `Pool/CasPartWriteTxn.h:175-182`) and "the ordinary ReplicatedMergeTree interserver trust" (`ContentAddressedExchange.h:220-224`, `ContentAddressedMetadataStorage.cpp:2169-2171`).
  - Verdict: the *silent wrong-length read* concern of CAS-031 is no longer a data-safety hole; it survives only as a "hostile sender can force a hard-fail" DoS-shaped issue and is explicitly a by-design trust decision equal to zero-copy replication.

- **CAS-209 (SKEW-2/3/4/7) — Relink is data-safe under version skew ✅ STILL HOLDS.** Confirmed on the current tree:
  - SKEW-2 (magic + format_version fail-closed): `decodePartManifest` calls `expectHeaderLine(in, FormatId::PartManifest)` before any field, and `checkCompatibility(compatibility_version, ...)` throws `UNKNOWN_FORMAT_VERSION` for any compatibility version `> G_BUILD` (`src/.../Formats/CasFormat.cpp:64-70`; `CasPartManifestFormat.cpp:129`). Also applies to `decodeEnvelopeHeader` via the `"v"` key (`CasBlobEnvelopeFormat.cpp:187`).
  - SKEW-3 (publish-nothing on abort): `prepareEntries` catches on failure and calls `abandonBuildBestEffort` before rethrowing (`PartFolderAccess.cpp:488-493`); `prepareAdoptFromManifest` maps `ABORTED`/`NETWORK_ERROR` to `MechanismFallbackAllowed` with `out = nullptr` (`ContentAddressedMetadataStorage.cpp:2208-2220`). Handle destruction is a backstop (`ICaPreparedRelink` docs, `ContentAddressedExchange.h:113-133`).
  - SKEW-4 (old sender/new receiver): if the sender never sets the relink cookie, `ca_relink.empty()` is true and the receiver falls straight through to the byte path (`DataPartsExchange.cpp:889-890`). No skew surface.
  - SKEW-7 (base replication versioning orthogonal): `REPLICATION_PROTOCOL_VERSION_WITH_CA_CONFIRM = 11` gates the OFFER of relink on the sender side (`DataPartsExchange.cpp:404`), and the server negotiates `min(client, 11)` in the `server_protocol_version` cookie (`:327`). Old base replication paths are unchanged. Same-sender fallback carries the explicit `allow_ca_relink=false` recursion brake (`:913, :1008`).

## New findings (not in original audit)

- **NEW-ad7-1: `assertEOF` after `readStringBinary(sender_manifest_bytes)` will hard-fail any future v2-with-trailer sender talking to this exact v2 receiver.** Severity: Info. Anchor: `src/Storages/MergeTree/DataPartsExchange.cpp:936-937`.
  - Trigger: a future `part_manifest_v3` framing that adds a trailing field will require a cookie-value bump to `"part_manifest_v3"`; otherwise this receiver's `assertEOF` will throw on the extra bytes.
  - Notes: not a bug — it is the *intended* forward-incompat behavior (SKEW-1 hardening's inverse: any future framing addition MUST bump the cookie). Worth documenting in the wire-contract text alongside `CA_RELINK_COOKIE_VALUE`. The header comment on `CA_RELINK_COOKIE_VALUE` (`:122-128`) partially covers this; making the assertEOF-implies-cookie-bump requirement explicit would help future authors.

- **NEW-ad7-2: Cookie-value gate happens BEFORE the pool-uuid re-check, but AFTER `ca_relink` cookie parse — an empty cookie value on the wire is silently treated as "no relink" rather than as a malformed offer.** Severity: Info. Anchor: `DataPartsExchange.cpp:889-890`.
  - Trigger: a future sender bug that emits an empty cookie value would fall through to the byte fetch silently rather than logging the anomaly.
  - Notes: safe fallback direction, but obscures a diagnosable sender bug. Non-actionable.

- **NEW-ad7-3: `locate()` does not read the envelope's own `header_len` before ranging — soft coupling to pool_meta's `blob_header_len` invariant.** Severity: Info (was CAS-024 severity CORRECTNESS; the invariant is enforced elsewhere, so this is a note about the coupling, not a live bug). Anchor: `src/.../Pool/CasManifestReader.cpp:144-168`.
  - Trigger: any future code path that permits an envelope's `header_len` to disagree with `PoolMeta::blob_header_len` (e.g., a live blob_header_len rotation, or a foreign object that survived a `Replaced` verdict rejection) would silently misread payload offsets on the ranged path — the envelope decoder derives `header_len` from '\n' but `locate()` skips the envelope entirely.
  - Recommendation (defense-in-depth, not required today): assert `header.header_len == meta.blob_header_len` where a full envelope read already happens (adopt, GC observe), OR let `locate()` optionally verify via a 1-byte over-read of the pad terminator on first read of a blob.

## By-design / N/A / info

- The relink wire's design comment now explicitly lists what a `yes` confirm proves and does NOT prove ("What a `yes` does NOT prove"), covering the confirm handshake introduced in `_WITH_CA_CONFIRM = 11`. Not part of ad7's original scope but relevant to protocol-skew safety: a mid-upgrade client that advertises 11 but does not confirm cannot obtain a relink, because the sender gates the offer on `client_protocol_version >= 11` (`DataPartsExchange.cpp:404`).
- Path hygiene at the manifest edge (rejecting `..` / absolute / empty segments) is a new hardening over the original audit's baseline: the audit's SKEW notes did not cover manifest-path traversal; this closes an adjacent hazard.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-054 (SKEW-1/5/6) | Med | ✅ fixed | `DataPartsExchange.cpp:128, 916-924, 935-937` |
| CAS-024 (STORE-2) | Correctness | ✅ fixed-in-effect (soft-coupling residual) | `Pool/CasPool.cpp:123`; `CasManifestReader.cpp:158`; `CasBlobEnvelopeFormat.cpp:230-248` |
| CAS-036 (BUILD-2) | Config | ✅ fixed | `Formats/CasPoolMetaFormat.cpp:36-46` |
| CAS-031 (MW-1) | Integrity | 📐 by-design (digest anchor + path hygiene close silent-misread; blob_size trust survives as DoS-shape) | `Pool/CasPartWriteTxn.cpp:794`; `CasPartManifestFormat.cpp:198-267`; `ContentAddressedExchange.h:220-224` |
| CAS-209 (SKEW-2/3/4/7) | Info | ⚪ still holds | `Formats/CasFormat.cpp:64-70`; `PartFolderAccess.cpp:488-493`; `ContentAddressedMetadataStorage.cpp:2208-2220`; `DataPartsExchange.cpp:404, 889-890, 913` |
| NEW-ad7-1 | — | ⚪ info | `DataPartsExchange.cpp:936-937` |
| NEW-ad7-2 | — | ⚪ info | `DataPartsExchange.cpp:889-890` |
| NEW-ad7-3 | — | ⚪ info | `Pool/CasManifestReader.cpp:144-168` |

Counts: 5 original IDs re-verified — 3 fixed, 1 fixed-in-effect (soft residual), 1 by-design, 1 still-holds-info. 3 new info-level notes; **zero new still-present findings.**
