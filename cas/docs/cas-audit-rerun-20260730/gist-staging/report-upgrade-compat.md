# upgrade-compat — re-run 2026-07-30

Re-run of the CAS mixed-version / rolling-upgrade / on-S3 format compatibility audit against
the current PR HEAD at `/Volumes/workspace/ClickHouse` (branch `cas-audit-20260730`).

## Scope in current code

- Files/dirs walked (CAS-only):
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPoolMetaFormat.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasTextFormat.cpp`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/README.md`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPoolMeta.cpp`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedExchange.{h,cpp}`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasCodecUtil.h`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobDigest.h`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGcShardPlan.h`
  - `src/Disks/tests/gtest_cas_text_format.cpp`

Structural changes since the original audit that reshape the upgrade-compat landscape:

- The persisted-object family is now **entirely text/JSON** (see `Formats/README.md`). There are
  no `.proto` files anywhere under `ContentAddressed/**` and no protobuf dependency. The wire
  vocabulary lives in `CasWireVocab.*` / `CasRefWireVocab.*`, and the header line
  `{"type":"cas_<name>","v":N}` is the sole schema-version carrier.
- `G_BUILD` has advanced from `1` (original audit) to **`3`** (`CasFormat.h:28`). Two format
  generations were consumed (schema-3 mixed-algorithm settlement key; immutable `_log` / `_snap`
  ref objects).
- A new backward floor `kRefSnapshotLogGeneration = 3` (`CasFormat.h:33`) fails pool-meta
  decoding closed on any pool with `v < 3` (`CasPoolMetaFormat.cpp:109-113`), so downgrade past
  gen-3 is unconditionally blocked with an explicit "recreate the pool" error (correct
  fail-closed for pre-release).
- `PoolMeta` now carries `algos_used: std::vector<uint8_t>` (frozen sorted set of admitted
  `BlobHashAlgo` values, `CasPoolMetaFormat.h:29-31`) — this is the algo-identity pinning that
  CAS-037 asked for.
- The relink source token now has an explicit `car1` version tag with strict-decode gating
  (`ContentAddressedExchange.cpp:13, 152-153`) — this is the CAS-054 fix.
- On-wire integer byte order for CAS's own bytes-fields, keys, and shard-selectors is
  **explicit big-endian** everywhere (`u128ToBytesBE` / `u128FromBytesBE` in
  `Primitives/CasCodecUtil.h:22-45`; `CasBlobDigest.h:59, 76-86, 155-179`; `CasGcShardPlan.h:38-41`
  — with an in-source guard rail: "MUST stay an explicit big-endian read, never a native-endian
  memcpy (would silently reshard on an LE host)"). Any envelope / control field is either
  JSON-decimal or fixed-width lowercase hex. This materially changes the CAS-107 story.

## Findings still present

### CAS-009 — `compatibility_version` always stamped at `G_BUILD` (no write-down-to-floor)

- Anchor:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.cpp:57-62` —
    `currentCompatibilityVersion()` still returns `G_BUILD` unconditionally, with the same
    "Until roster-based write-down is implemented" comment. No roster, no change-point
    consultation.
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasTextFormat.cpp:260-269` —
    `writeHeaderLine` writes `"v": currentCompatibilityVersion()` (i.e. `G_BUILD`) on **every**
    text object header, for every `FormatId`.
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.cpp:22, 26-48` —
    `BASELINE = {{1, 1}}` and every class dispatches to `BASELINE`. So even though `G_BUILD = 3`,
    the change-point history is **still a single `{1,1}` row for every class** — no
    additive-vs-breaking distinction is recorded for the two generation bumps that happened
    (schema-3 key in gen-2; ref-log/snap in gen-3). A `changePoints()`-driven writer would have
    nothing older-than-`G_BUILD` to stamp anyway.
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPoolMeta.cpp:88, 147` —
    `min_reader_generation` is stamped at `G_BUILD` both on first mint and on any algo
    admission (so admitting a new algo permanently raises the floor to the current build's
    `G_BUILD`).
- Trigger: `G_BUILD` advanced past a previous release binary; a peer at the older `G_BUILD`
  opens or reads any freshly-written CAS object.
- Evidence quote (short):
  > "Until roster-based write-down is implemented, every object carries the current build as
  > its compatibility floor." — `CasFormat.cpp:59-61`
- Notes:
  - Original audit called this "latent while `G_BUILD = 1`." That mitigation is **gone**:
    `G_BUILD = 3` today. Any binary in the wild that shipped with `G_BUILD < 3` and reads a
    fresh object written by a current-PR binary will get `UNKNOWN_FORMAT_VERSION` on **every**
    object it hasn't already cached (`checkCompatibility`, `CasFormat.cpp:64-70`), even where
    the underlying change was additive.
  - There is a second, orthogonal fence: an older binary that tries to `decodePoolMeta` a
    current pool will fail on the backward-floor check
    (`CasPoolMetaFormat.cpp:109-113`: `header.v < kRefSnapshotLogGeneration`). So today a
    mixed cluster where one node is at `G_BUILD ≤ 2` and one at `G_BUILD = 3` can't even
    complete `Pool::open` on the older side. This is safe fail-closed but confirms the
    upgrade contract is "all nodes together, no downgrade past the floor."
  - No two-generation compatibility test exists (`rg -i 'rolling.upgrade|write.down.to.floor|two.generation|mixed.generation'` returns only source comments in
    `CasPoolMeta.cpp`, `CasFormat.h`, and `Formats/README.md`, no tests). Original recommendation
    "Add an explicit rolling-upgrade test" is not addressed.
  - `Formats/README.md:44-51` documents the intended contract explicitly: "Breaking change = `v`
    bump + `changePoints` + write-down-to-floor" — but `changePoints` has no non-baseline rows
    and `write-down-to-floor` is not implemented, so the contract is documentation-only.

Severity: **High** (was High/latent) — no longer latent post gen-1→gen-3 progression.
Status: 🔴 **still-present**, effectively worsened relative to the pre-release baseline the
original audit assumed. Safe (no misread, no corruption), but rolling upgrade across a format
generation is confirmed big-bang-only today.

### CAS-107 (residual, LE-only-guard subclaim) — no explicit LE/BE runtime guard

- Anchor:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasCodecUtil.h:22-45` —
    all UInt128 wire encoding is **explicit BE**, byte-loop shift-based (endian-neutral C++).
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobDigest.h:59, 76-86, 155-179` — same discipline for digests, with a source comment enforcing "never a native-endian memcpy" for shard-key derivation.
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGcShardPlan.h:38-41` —
    same.
- Trigger: a hypothetical big-endian ClickHouse build joining a pool. The explicit byte-loop
  shifts make CAS's own wire byte order architecture-invariant, so BE and LE builds would
  produce **the same wire UInt128 bytes**. However, the **content hash** (`CityHash128`)
  itself is still not guaranteed to produce identical output across endianness (see AD1-2
  original), and there is still no `static_assert(std::endian::native == std::endian::little)`
  or equivalent runtime refusal at pool-open.
- Evidence quote:
  > "MUST stay an explicit big-endian read, never a native-endian memcpy (would silently reshard
  > on an LE host)." — `CasBlobDigest.h:178-179`, `CasGcShardPlan.h:40-41`
- Notes: The BE-fork risk is materially narrower than the original audit assumed. The wire
  serialization is architecture-neutral by construction, so the residual gap is limited to the
  underlying `CityHash128` implementation itself (bundled `CityHash_v1_0_2` targets LE). Still no
  explicit LE-only invariant assert, but the scope shrank from "silent fork across every object"
  to "shard-mapping-safe wire, hash-function BE untested."

Severity: **Low** (unchanged). Status: 🔴 **still-present but scope-reduced** — explicit-BE wire
codec covers the shard-selector half; the CityHash-across-endianness half is unchanged.

### CAS-107 (residual, ManifestId-version-stable subclaim) — cannot re-verify statically

- Anchor: `Formats/CasPartManifestFormat.cpp` (whole file; the manifest is now text/JSON with
  hex `ManifestRef` fields).
- Trigger: rebuild "the same logical part" on two ClickHouse versions expecting bit-identical
  manifest bytes / ManifestId.
- Notes: The original AD1-5 claim was that `writer_version` / `G_BUILD` were embedded into the
  hashed manifest bytes, making ManifestId not version-stable. Post-text-format rewrite, the
  header line always stamps `"v":G_BUILD` (`CasTextFormat.cpp:266-267`), and text objects hash
  their canonical bytes — so **the same claim holds by construction**: any `G_BUILD` bump changes
  the header line, which changes the hashed bytes, which changes the ManifestId. Harmless
  (ManifestId is identity-scoped by design; blob keys are unaffected), consistent with the
  original AD1-5 finding.

Severity: **Info/Low** (unchanged, harmless). Status: 🔴 **still-present, harmless**.

### CAS-212 — Retired `FormatId` values / shapes rely on "pre-release, nothing deployed"

- Anchor:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.h:38-68` —
    `FormatId` enum. Retired values are 2, 3, 4, 6, 7, 10, 15 (grown from the original 2, 4, 7,
    10, 15 as ref-shard, condemned-state and watermark objects were retired). Each retired-value
    range carries an in-source comment ("Keep all three values unused." / "must never be
    reused."), but **there is no `static_assert`, no `changePoints()` reservation entry, and no
    test** that fails if a future commit reuses one of these values.
  - `src/Disks/tests/gtest_cas_text_format.cpp:39-58` — the completeness test iterates the live
    FormatIds only; retired values are neither enumerated nor negatively asserted.
- Trigger: a future commit gives one of the retired numeric ids to a new class → an old-object
  poisoned by the retired class shape is misinterpreted as the new class (magic-collision
  equivalent for text: matching `"type"` string alone would prevent this, so risk in practice
  is limited, but the numeric-id contract is unenforced).
- Evidence quote:
  > "Values 2, 3, and 4 are retired. […] Keep all three values unused." — `CasFormat.h:41-43`
- Notes: Discipline codified in comments only. Original recommendation "freeze the enum + retired-shape reservations with a comment/test at GA" — partially done (comments), test still missing.

Severity: **Info/Low** (unchanged). Status: 🔴 **still-present** (partial mitigation: strong
comments, no test).

### CAS-027 (analog under text formats) — additive tolerant-key re-encode drop

- Anchor:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasTextFormat.cpp:245-256`
    — `JsonObjectReader::skipUnknown` **skips** any tolerant unknown key on decode:
    `skipJSONField(in, key, jsonReadSettings())`. The value is discarded; it is not preserved
    across a subsequent re-encode by the same or a different build.
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/README.md:47-49` —
    documents the behavior explicitly:
    > "Additive change = new tolerant key, no `v` bump; on MUTABLE objects the field is
    > best-effort until the pool floor rises (an old writer's fresh re-encode drops it)."
- Trigger: gen-N writer adds tolerant additive key `k` to `cas_pool_meta` (or any mutable
  control object) without bumping `v`. A concurrent gen-(N-1) writer performs a fresh
  re-encode (e.g. admits a new algo, which rewrites `_pool_meta`, `CasPoolMeta.cpp:88-90,
  147-150`). The old build silently drops `k` → silent mixed-version control-plane data loss
  (identical semantics to original RSC-2 / BC4-2, but the vehicle is JSON tolerant-key skip
  instead of protobuf unknown-field skip).
- Evidence quote:
  > "the field is best-effort until the pool floor rises (an old writer's fresh re-encode
  > drops it)." — `Formats/README.md:48-49`
- Notes:
  - Original CAS-027 as literally worded ("protobuf additive-field re-encode loss") is
    **no longer applicable in that form** — no protobuf anywhere. The *semantic* issue survives
    verbatim under JSON tolerant-key skip, and the code owners have acknowledged it as
    by-design pending write-down-to-floor / floor-raise.
  - The upgrade contract narrows the exposure: once `min_reader_generation` is CAS-raised on
    algo admission (`CasPoolMeta.cpp:88`), an older-than-floor writer is fenced from the pool
    entirely and cannot perform the re-encode-and-drop. The residual window is exactly the
    "same `G_BUILD`, differing tolerant-key patch" case (e.g. tolerant additive key introduced
    without a `v` bump between two same-`G_BUILD` builds).

Severity: **High** (original: High) — degraded to "acknowledged by-design, floor-raise
mitigates once implemented." Status: 🔴 **still-present, acknowledged by-design** (README:44-51).

## Findings fixed / no longer reproducible

### CAS-037 — Content-hash algorithm now durably pinned in PoolMeta

- Anchor for the fix:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPoolMetaFormat.h:29-31`
    — `algos_used: std::vector<uint8_t>` (strictly increasing frozen set).
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPoolMetaFormat.cpp:81`
    — persisted `mrg`.
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPoolMeta.cpp:75-102, 144-160`
    — admission is explicit opt-in (`allow_new`), never silent; a new algo union raises
    `min_reader_generation` to `G_BUILD` in the SAME CAS write; on-mint stamps
    `algos_used = {config_algo}` and `min_reader_generation = G_BUILD`. Line 82-83:
    `if (!allow_new) throwNotAdmitted(pool, config_algo)` — the "future hash change forks the
    pool silently" path is closed.
- Verdict: ✅ **fixed** — precisely the fix the original audit recommended ("record + verify the
  dedup hash-algorithm identity in `PoolMeta`").

### CAS-054 — Relink cookie value now version-gated

- Anchor for the fix:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedExchange.cpp:11-17`
    — `constexpr std::string_view kTokenVersion = "car1";` (explicit versioned token shape).
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedExchange.cpp:152-153`
    — `if (count != segments.size() || segments[0] != kTokenVersion) return std::nullopt;`
    strict version-tag mismatch → refusal.
  - Same file, `encodeCasRelinkSourceToken` writes `kTokenVersion` as the first segment.
  - `ContentAddressedExchange.h:33-60` documents the wire-contract discipline.
- Verdict: ✅ **fixed** — original recommendation "Gate the exact cookie value now" implemented
  with a strict version tag, fixed field count, per-field size cap, control-character reject,
  and strict percent-decoding. A future v2 framing must change `kTokenVersion`, at which point
  a v1 receiver refuses the token cleanly.

### CAS-209 — Relink data-safe under version skew (verified-safe)

- Anchor:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedExchange.h:140-146`
    documents "the manifest's sender-specific identity ... is not authoritative: the receiver
    uses only the entries, adopts references [locally]". So the receiver never trusts sender
    ManifestRef/root_namespace_id/payload_digest; it revalidates blob presence and republishes
    a receiver-local manifest.
  - The cookie's version gate (see CAS-054 fix above) plus the manifest's own compat gate
    (`checkCompatibility` in `CasFormat.cpp:64-70`, applied when decoding the received
    manifest body) together guarantee any format-generation skew fails closed at the
    manifest level with `UNKNOWN_FORMAT_VERSION` before any byte publish — receiver falls back
    to full byte-fetch.
- Verdict: 📐 **by-design / verified-safe** (unchanged from the original AD-7 verdict).

## New findings (not in original audit)

- **NEW-upgrade-compat-1 (Med): `changePoints()` history stayed frozen at `{{1,1}}` across two
  `G_BUILD` bumps.** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.cpp:22, 26-48`.
  `G_BUILD` advanced from 1 to 3, but no class received a class-specific change-point array;
  every class still dispatches to `BASELINE = {{1, 1}}`. The `README.md:44-51` upgrade
  contract explicitly says "Breaking change = `v` bump + `changePoints` + write-down-to-floor",
  and the two `v` bumps that happened were treated as breaking (backward floor raised to 3),
  but the `changePoints` half of the contract was not exercised. Consequence: a future
  operator cannot inspect the format history to know which generations were additive vs
  breaking; the audit trail lives only in comments in `CasFormat.h:18-27`. Also, when
  write-down-to-floor is finally implemented, there is no ladder for it to consult — that
  work will need to backfill the ladder retroactively.

- **NEW-upgrade-compat-2 (Low): backward pool-meta floor is a hard `< 3` gate, no operator
  override.** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPoolMetaFormat.cpp:109-113` —
  `if (header.v < kRefSnapshotLogGeneration) throw` with message
  "CAS is pre-release — recreate the pool." Correct fail-closed pre-release, but the error is a
  raw throw with no operator escape hatch and no runbook link. Any test pool minted by an
  earlier CAS branch cannot be reopened by this build even in read-only observe mode
  (`openForDecommission` still calls `createOrValidate`, `CasPoolMeta.cpp:106-124`) — the
  observe path fails on the backward-floor check before it can inspect anything. Post-GA this
  must become a **versioned** upgrade path, not a "recreate the pool" throw. File under CAS-063
  (control-plane backup/restore runbook).

- **NEW-upgrade-compat-3 (Low): tolerant-key silent-drop has no per-generation "critical
  additive" mechanism.** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasTextFormat.cpp:245-256`.
  The `!`-prefix "critical key" convention (line 249-251) is the only way to make an unknown
  key fail closed; there is no way to add a new **tolerant** additive key that is
  "best-effort forever after floor-raise N" (a bump would need to promote the key to
  `!`-critical, at which point it becomes breaking). This makes the CAS-027-analog residual
  window (same `G_BUILD`, patch-level tolerant-key introduction) permanent within a
  generation. Consider a "min-generation-N tolerant key" mechanism, or document that all
  patch-level tolerant-key additions between released builds are explicitly best-effort.

- **NEW-upgrade-compat-4 (Info): pool-meta admission ratchets `min_reader_generation`
  irreversibly on any new-algo union.** `CasPoolMeta.cpp:75-102` (`admitOrValidate`) — line 88:
  `next.min_reader_generation = G_BUILD;` on every admission. This is correct (once a
  schema-3-bearing algo is present, older readers cannot decode the settlement key), but the
  ratchet fires on **any** new-algo admission regardless of whether the admitted algo requires
  schema-3 semantics. The union of two "gen-1-compatible" algos will still raise the floor to
  `G_BUILD = 3` and fence every gen-1 or gen-2 reader out of the pool. Fine as an over-fence
  today; worth revisiting if a `BlobHashAlgo` is ever added that is deliberately
  gen-1-compatible.

- **NEW-upgrade-compat-5 (Info): no LE-only build assertion.** No occurrence of
  `std::endian::native` / `__BYTE_ORDER__` / `static_assert` guarding LE-only in
  `MetadataStorages/ContentAddressed/**`. The explicit-BE wire codec covers CAS's own bytes,
  but the underlying `CityHash128` implementation is not audited BE-safe. Cheap one-liner:
  `static_assert(std::endian::native == std::endian::little, "CAS assumes LE host CityHash");`
  in `Primitives/CasBlobDigest.h` or `CasCodecUtil.h`.

## By-design / N/A / info

- 📐 **Same-generation, different patch** — identical `G_BUILD`, all objects mutually readable
  (unchanged from original). Verified: `CasTextFormat.cpp:260-269` stamps the same `v` value
  regardless of patch.
- 📐 **New reader, old objects (within `v ≥ 3`)** — `checkCompatibility` gate
  (`CasFormat.cpp:64-70`) refuses only `compatibility_version > G_BUILD`; older objects are
  read. Verified.
- 📐 **Downgrade across the pool-meta floor** — blocked by `CasPoolMetaFormat.cpp:109-113` (see
  NEW-upgrade-compat-2 for the residual runbook gap).
- 📐 **Config drift (`blob_header_len`, algo)** — pool-authoritative on reopen
  (`CasPoolMeta.cpp:116-124`), configured values ignored; hash-algo drift is now explicitly
  gated on `allow_new` (`CasPoolMeta.cpp:82-83`). Unchanged safe.
- ⚪ **No dedicated rolling-upgrade test.** Original recommendation not addressed. `rg -i
  'rolling.upgrade|two.generation|mixed.generation|write.down.to.floor'` returns only source
  comments, no tests. Tracked under CAS-009 test-gap in the master summary (T-G5).

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-009 (UPG1) | High (latent) | 🔴 still-present (worsened: no longer latent, `G_BUILD` moved 1→3) | `Formats/CasFormat.cpp:57-62`; `Formats/CasFormat.cpp:22, 26-48`; `Formats/CasTextFormat.cpp:260-269`; `Pool/CasPoolMeta.cpp:88, 147` |
| CAS-027 (RSC-2/BC4-2 analog) | High (COMPAT / DATA-LOSS) | 🔴 still-present, acknowledged by-design (protobuf gone; JSON tolerant-key skip has the same semantics) | `Formats/CasTextFormat.cpp:245-256`; `Formats/README.md:47-49` |
| CAS-037 (BUILD-1 / AD1-3) | Med (INTEGRITY/COMPAT) | ✅ fixed — algo pinned in PoolMeta with explicit `allow_new` opt-in | `Formats/CasPoolMetaFormat.h:29-31`; `Pool/CasPoolMeta.cpp:75-102, 144-160` |
| CAS-054 (SKEW-1/5/6) | Low-Med (COMPAT) | ✅ fixed — `kTokenVersion = "car1"` strict version-tag gate + fixed field count | `ContentAddressedExchange.cpp:11-17, 152-153` |
| CAS-107 (AD1-2, LE guard) | Low (COMPAT) | 🔴 still-present, scope-reduced (wire codec now explicit BE; only CityHash-across-endianness risk remains) | `Primitives/CasCodecUtil.h:22-45`; `Primitives/CasBlobDigest.h:59, 76-86, 155-179`; `Gc/CasGcShardPlan.h:38-41` |
| CAS-107 (AD1-5, ManifestId version-stability) | Info (COMPAT) | 🔴 still-present, harmless — `v` in header stamps `G_BUILD` into hashed bytes | `Formats/CasTextFormat.cpp:260-269`; `Formats/CasPartManifestFormat.cpp` (whole-file text encode) |
| CAS-209 (SKEW-2/3/4/7, RPL-1) | Info/by-design | 📐 by-design, still verified-safe (relink is byte-fetch on any decode/compat failure) | `ContentAddressedExchange.h:140-146`; `Formats/CasFormat.cpp:64-70` |
| CAS-212 (UPG2) | Info/Low | 🔴 still-present, partial mitigation — strong comments, no static_assert or negative test | `Formats/CasFormat.h:38-68`; `src/Disks/tests/gtest_cas_text_format.cpp:39-58` |

Counts:
- Original findings re-checked: **7** (CAS-009, CAS-027, CAS-037, CAS-054, CAS-107 [two subclaims], CAS-209, CAS-212).
- Still-present: **5** (CAS-009, CAS-027 as text-format analog, CAS-107 twice, CAS-212).
- Fixed: **2** (CAS-037, CAS-054).
- By-design / verified-safe: **1** (CAS-209).
- New findings this re-run: **5** (NEW-upgrade-compat-1..5).
