# codeonly-line — re-run 2026-07-30

## Scope in current code

Line-level code-only re-verification of the original code-only audit's findings,
against the CAS tree at `/Volumes/workspace/ClickHouse/src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`
(branch `cas-audit-20260730` = PR #2073 head).

Files walked (the current-code home of every finding this audit tracks):

- `Formats/CasFormat.{h,cpp}` — replaces `CasFormat.cpp`; `FormatId::Roster` gap.
- `Formats/CasBlobEnvelopeFormat.{h,cpp}` — replaces `CasEnvelope.{h,cpp}`; whole envelope is now text/JSON.
- `Formats/CasPartManifestFormat.{h,cpp}` — replaces `CasManifestCodec.{h,cpp}`; text/JSON manifest with `payload_digest` verification.
- `Formats/CasRecordStreamFormat.{h,cpp}` — replaces `CasRunFile.{h,cpp}`; text/JSON records with `line_cap`, no `klen`/`plen`.
- `Formats/CasFoldSealFormat.{h,cpp}` — replaces `CasGenerationSeal.{h,cpp}`; text/JSON fold-seal.
- `Formats/CasGcStateFormat.{h,cpp}`, `Formats/CasGcOutcomesFormat.{h,cpp}` — replace `CasGcFormats.{h,cpp}`; text/JSON.
- `Formats/CasPoolMetaFormat.{h,cpp}` — replaces the protobuf pool-meta wire.
- `Formats/CasLayout.{h,cpp}` — home of `checkNamespace` / `mountpointObjectKey` / `namespaceFileKey`.
- `Pool/CasPoolMeta.cpp` — `PoolMeta::createOrValidate`.
- `Pool/CasServerRoot.cpp` — replaces `CasServerRoot.cpp`; mount lease / `allocateWriterEpoch`.
- `Pool/CasMountRuntime.{h,cpp}` — new home of `scheduleRemount` / `stopRemountThread` (replaces `CasStore` teardown).
- `Pool/CasManifestReader.cpp` — `locate` / `BlobLocation`.
- `Pool/CasPartWriteTxn.cpp` — `adoptEvidence`, `stageManifest`, `promote` (replaces `CasBuild`).
- `Gc/CasGc.cpp`, `Gc/CasGcScheduler.{h,cpp}` — `pulseHeartbeat`, `heartbeatLoop`, `acquireOrRenewLease`.
- `Gc/CasBlobInDegree.{h,cpp}` — GC blob-target sweep (was `CasBlobInDegree.cpp`).
- `Backend/CasObjectStorageBackend.{h,cpp}` — `get` (HEAD+GET), `checkPoolPreconditions` (versioning), conditional-write.
- `Backend/CasProbe.{h,cpp}` — capability probe.
- `Backend/CasInstrumentedBackend.{h,cpp}` — 66 profile events, `classifyCasNs`.
- `Parts/PartPathParser.cpp` — `looksLikePartDir`.
- `ContentAddressedMetadataStorage.{h,cpp}` — `prepareAdoptFromManifest`, `getStorageObjects`, staging probe.
- `ContentAddressedTransaction.{h,cpp}` — `unlinkFile`, `setLastModified`, `chmod`, `generateObjectKeyForPath`, `moveDirectory`, `truncateFile`.

The original audit's `CasStore.{h,cpp}` / `CasBuild.{h,cpp}` / `CasEnvelope.{h,cpp}` /
`CasManifestCodec.{h,cpp}` / `CasRunFile.{h,cpp}` / `CasRootShardCodec.{h,cpp}` /
`CasGenerationSeal.{h,cpp}` / `CasGcFormats.{h,cpp}` / `CasIds.h` / `CasToken.h` /
`CasManifestId.h` files no longer exist — the pool wire is now a text/JSON family
and Store has been split across `CasPool`, `CasMountRuntime`, `CasPartWriteTxn`,
`CasManifestReader`, `CasBlobUploadPool`, `CasRefLedger`. All findings below are
re-verified against the new files.

---

## Findings still present

### `CAS-076` (FMT-1) — `FormatId::Roster` defined but `traitsFor(Roster)` throws — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.cpp:35` (`changePoints`), `:93-109` (`TRAITS` table).
- Trigger: `Roster` is enumerated in `FormatId` (`CasFormat.h:49`) and included in the `changePoints` switch (:35), but the `TRAITS` array (:93-109) has no entry for it; any `traitsFor(FormatId::Roster)` throws `LOGICAL_ERROR: no traits for FormatId 9 (reserved?)`.
- Evidence quote:

```112:118:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.cpp
const FormatTraits & traitsFor(FormatId id)
{
    for (const FormatTraits & t : TRAITS)
        if (t.id == id)
            return t;
    throw Exception(ErrorCodes::LOGICAL_ERROR, "CasFormat: no traits for FormatId {} (reserved?)", static_cast<uint16_t>(id));
}
```

The header comment at `CasFormat.h:126` explicitly documents this: *"Throws `LOGICAL_ERROR` for `FormatId::Roster`, which is reserved and ..."*. Same latent shape as the old `magicFor(Roster)` throw — id is defined but no code can read/write it. Now `[BUG-latent]` rather than `[HARDENING]` because the format-registry layer above shifted, but no call path exercises Roster today.

### `CAS-077` (GS-1) — `decodeFoldSeal` still casts `classification` without range validation — 🔴 still-present (partial)

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFoldSealFormat.cpp:189`.
- Trigger: `cov.classification = static_cast<uint8_t>(r.readU64Number())` — a decoded value larger than `UINT8_MAX` is silently truncated (uint64 → uint8), with no range check.
- Evidence quote:

```186:199:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFoldSealFormat.cpp
            while (r.nextKey(key))
            {
                if (key == "key") map_key = r.readString();
                else if (key == "cls") cov.classification = static_cast<uint8_t>(r.readU64Number());
                else if (key == "tt") { tt = tokenTypeFromWord(r.readString(), "fold seal"); have_tt = true; }
                else if (key == "tv") tv = r.readString();
                else if (key == "lfe") cov.last_folded_ref_id.writer_epoch = r.readU64String();
                else if (key == "lfs") cov.last_folded_ref_id.ref_sequence = r.readU64String();
                else throw Exception(ErrorCodes::CORRUPTED_DATA, "CAS fold seal: unknown cov key '{}'", key);
            }
            if (!have_tt)
                throw Exception(ErrorCodes::CORRUPTED_DATA, "CAS fold seal: cov missing tt");
            cov.folded_token = Token{tv, tt};
            seal.per_ns_shard[map_key] = cov;
```

- Notes: `folded_token_type` (`tt`) now routes through `tokenTypeFromWord`, which fails closed on unknown — that half of the original GS-1 is **fixed**. The `classification` half remains: a corrupt fold seal can silently truncate to `uint8_t` and drive fold graduate/condemn decisions. Same "inconsistent fail-closed discipline" the original audit called out, at half the width. Fix is trivial: reject `> UINT8_MAX` before the cast.

### `CAS-074` (LAY-1) — `checkNamespace` still does not reject `.` / `..` segments — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasLayout.cpp:260-284` (`Layout::checkNamespace`).
- Trigger: A namespace segment equal to `.` or `..` passes the current empty / `_files` / `_manifests` check.
- Evidence quote:

```260:284:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasLayout.cpp
void Layout::checkNamespace(const RootNamespace & ns) const
{
    const String & s = ns.string();
    if (s.empty())
        throw DB::Exception(DB::ErrorCodes::BAD_ARGUMENTS, "CasLayout: namespace must be non-empty");

    size_t start = 0;
    while (true)
    {
        size_t end = s.find('/', start);
        const String segment = s.substr(start, end == String::npos ? String::npos : end - start);
        if (segment.empty())
            throw DB::Exception(DB::ErrorCodes::BAD_ARGUMENTS,
                "CasLayout: namespace '{}' has an empty segment (leading/trailing or doubled '/')", s);
        if (segment == "_files")
            throw DB::Exception(DB::ErrorCodes::BAD_ARGUMENTS,
                "CasLayout: namespace '{}' uses the reserved segment '_files'", s);
        if (segment == "_manifests")
            throw DB::Exception(DB::ErrorCodes::BAD_ARGUMENTS,
                "CasLayout: namespace '{}' uses the reserved segment '_manifests'", s);
        if (end == String::npos)
            break;
        start = end + 1;
    }
}
```

- Notes: `namespaceFileKey` (`CasLayout.h:179-189`) *does* reject `..` in the file-name part; the asymmetry the original audit flagged still exists. `mountpointObjectKey` (`CasLayout.h:229-235`) still checks only `/`-shape, no `..`. `CasPartManifestFormat.cpp:200-210` now rejects `..`/`.`/empty segments in an *entry* path — that closes the manifest-entry vector of the same class, but does not repair `checkNamespace`/`mountpointObjectKey` themselves. Path-traversal risk remains latent on a filesystem-style backend (safe only for literal-key object stores where `..` is a literal segment).

### `CAS-066` (PM-1) — `createOrValidate` silently ignores passed `blob_header_len` when pool exists — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPoolMeta.cpp:106-124`.
- Trigger: When `_pool_meta` is present, the passed `blob_header_len` argument is discarded — the persisted value is authoritative, and no compare/warn on mismatch.
- Evidence quote:

```117:124:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPoolMeta.cpp
    /// Present => the pool is authoritative; ignore the passed config's blob_header_len and run the
    /// flag-gated admission check rather than the old single-value fail-close.
    if (auto existing = backend.get(key))
    {
        PoolMeta pm = decodePoolMeta(existing->bytes);
        return admitOrValidate(backend, key, std::move(pm), existing->token, blob_hash_algo, allow_new);
    }
```

- Notes: Now called out explicitly in the comment ("ignore the passed config's blob_header_len"). Same operator config-footgun the audit flagged. `root_shards` is no longer a `PoolMeta` field in the current tree — it now lives in `GcState.gc_shards` (see `CasGc.cpp:3025`, `poolConfig().gc_shards`), which is set once at first-ever GC acquire; the same "silently ignore reconfiguration" hazard applies via a different path.

### `CAS-024` (STORE-2) — `locate()` still trusts pool-wide `blob_header_len`, never the blob's own envelope header_len — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasManifestReader.cpp:144-168`.
- Trigger: For every Blob entry, `locate` returns `offset = meta.blob_header_len` and `length = entry.blob_size` — the envelope header is never HEAD/GET'd or otherwise consulted for its own `header_len`.
- Evidence quote:

```144:168:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasManifestReader.cpp
BlobLocation CasManifestReader::locate(const ManifestEntry & entry) const
{
    /// A ranged read into the content object: the payload starts at a constant offset for blobs
    /// (the pool's fixed blob_header_len — no per-object header read). Inline carries no standalone
    /// object location (there is no Subtree placement on a part manifest).
    switch (entry.placement)
    {
        case EntryPlacement::Blob:
        {
            return BlobLocation{
                .key = layout.blobKey(entry.ref),
                .offset = meta.blob_header_len,
                .length = entry.blob_size,
            };
        }
```

- Notes: `CasBlobEnvelopeFormat.cpp:232` now explicitly *derives* `header_len` from the '\n' position at decode ("blob_header_len is never passed to decode") — so the envelope self-describes its own header length; the read path just does not use that information. Silent misread hazard the same as before: any blob written with a different `blob_header_len` (via config drift `CAS-066`, or a mixed-version writer, or envelope pad extension) is read at the wrong offset. Fix (either verify `envelope.header_len == meta.blob_header_len` at read, or use the envelope's own value) is unchanged in intent.

### `CAS-031` (MW-1) — Relink/adopt receiver still trusts sender `entry.blob_size`; only blob presence is revalidated — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp:781-796` (`PartWriteTxn::adoptEvidence`); `ContentAddressedMetadataStorage.cpp:2143-2221` (`prepareAdoptFromManifest`, comment at :2151-2153 explicitly says "we ignore the decoded ManifestRef, root_namespace_id and payload_digest, and use ONLY the entries").
- Trigger: `adoptEvidence` records `entry.blob_size` verbatim into `deps[entry.ref]`; nothing HEADs the envelope to confirm `envelope.header_len + payload == entry.blob_size + meta.blob_header_len`.
- Evidence quote:

```781:796:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp
void PartWriteTxn::adoptEvidence(const ManifestEntry & entry)
{
    requireAlive();

    /// W-EVIDENCE: record a TOKENLESS dependency — liveness evidence is the live source manifest, not a
    /// token. Inline entries reference no standalone object, so they record nothing. NO backend call
    /// (no HEAD, no GET, no PUT) — the caller already holds the resolved entry. Part manifests have only
    /// Inline / Blob placements (no Subtree): only blobs are content-addressed.
    if (entry.placement == EntryPlacement::Blob)
    {
        /// Carry `entry.ref` WHOLE (the pair, never re-derived) — this is what makes a
        /// mixed-algo manifest's entries each dep-track under their OWN algo. §4: adopted=true marks this a
        /// committed-source W-EVIDENCE dep, trusted at promote via the durable manifest edge (no probe).
        deps[entry.ref] = BlobDepRecord{ObjectKind::Blob, std::nullopt, entry.blob_size, /*adopted=*/true};
    }
}
```

- Notes: Comment now says the design deliberately trusts the durable manifest edge — matches the audit's "trusted-cluster" caveat. But combined with the `payload_digest` being *ignored* on the received manifest (`prepareAdoptFromManifest`, `ContentAddressedMetadataStorage.cpp:2151-2153`), a wrong `entry.blob_size` from a compromised/buggy sender still makes the receiver publish a manifest whose read window (`locate → BlobLocation.length = entry.blob_size`, `CasManifestReader.cpp:159`) walks past the real payload. Same chain as before (`CAS-031` → `CAS-024`), receiver-side. `entry.path` traversal is now closed by `CasPartManifestFormat.cpp:200-210`, so only the `blob_size` half of MW-1 remains open.

### `CAS-022` (TXN-2) — `moveDirectory` (RENAME TABLE) still non-atomic, no in-call compensation — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1200-1287` (`ContentAddressedTransaction::moveDirectory`); relevant span at :1212-1220.
- Trigger: The republish-then-drop-old-namespace loop is documented as re-drivable/idempotent but is not committed in a single durable step; a throw mid-loop leaves the table split across namespaces.
- Evidence quote:

```1212:1220:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    /// RENAME TABLE / cross-engine move: both endpoints are TABLE dirs. Republish every ref (live
    /// and folded-in `detached/`-prefixed refs) plus every verbatim file under the new table
    /// identity, then drop the old namespace (the blobs/trees are content-addressed and untouched).
    ///
    /// There is no native cross-namespace atomicity (object storage has no directory rename, unlike a
    /// non-CAS disk where RENAME TABLE is a single atomic directory rename). This is a best-effort
    /// multi-op move, but it is RE-DRIVABLE/IDEMPOTENT: `republishRef` no-ops when the source ref is
    /// already gone (resolveRef miss after a prior drive moved it), `putNamespaceFile` is
    /// idempotent, and dropNamespace is the terminal step.
```

- Notes: Documented as intended out-of-scope, but still the correctness gap the original audit called out — a non-retried DDL leaves a durable split state. No move-journal, no auto-re-drive.

### `CAS-112` (C-U6 / C-U7) — `chmod` and `generateObjectKeyForPath` still throw `NOT_IMPLEMENTED` — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:531-533` (`generateObjectKeyForPath`), `:1188-1191` (`chmod`), routed through `notYet` (:83-93).
- Trigger: Any consumer that expects a MergeTree disk to support `chmod` or `generateObjectKeyForPath` on a CAS-backed table hits `NOT_IMPLEMENTED`.
- Evidence quote:

```1188:1191:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
void ContentAddressedTransaction::chmod(const String &, mode_t)
{
    notYet("chmod");
}
```

- Notes: Latent (no MergeTree path calls them). Now with an explicit self-explanatory message body via `notYet` — an improvement, but the fail-closed shape and the CAS-112 finding are unchanged. `truncateFile` (`:1603-1608`) is similarly `NOT_IMPLEMENTED` (by design, blobs are immutable).

### `CAS-032` (SCHED-1) — Zombie leader's `pulseHeartbeat` still unconditionally overwrites `hb.owner` — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp:2989-3003`.
- Trigger: `pulseHeartbeat` reads `gc/hb`, sets `hb.owner = gc_id` unconditionally, `++hb.hb_seq`, CAS-puts. No re-check that `gc_id` is still the lease owner of `gc/state`.
- Evidence quote:

```2989:3003:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp
void Gc::pulseHeartbeat(Pool & store, UInt128 gc_id)
{
    const String key = store.layout().gcHbKey();
    const auto got = store.backend().get(key);
    GcHeartbeat hb;
    std::optional<Token> expected;
    if (got)
    {
        hb = decodeGcHeartbeat(got->bytes);
        expected = got->token;
    }
    hb.owner = gc_id;
    ++hb.hb_seq;
    store.backend().casPut(key, encodeGcHeartbeat(hb), expected);
}
```

- Notes: The scheduler's `heartbeatLoop` (`CasGcScheduler.cpp:339-`) still gates only on `i_am_leader` — see `:370` (`Cas::Gc::pulseHeartbeat(*store, gc_id)`). Exactly the pattern the original audit called out. Data-plane safety unchanged (CAS on `gc/state` fails a stolen round); the churn/false-steal hazard against B160 is unchanged.

### `CAS-030` (SR-1) — Mount-lease liveness still wall-clock based — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasServerRoot.cpp:217` (`allocateWriterEpoch` liveness read), :276 (`makeMountBody` `expires_at_ms = now_ms + ttl_ms`), :320+ (`claimMount`).
- Trigger: Wall-clock comparison across servers; NTP skew → premature reclaim or false unavailability.
- Evidence quote:

```206:217:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasServerRoot.cpp
                        /// Deliberately weaker than claimMount's reclaim gate (this file, ~:370-380),
                        /// which never trusts a bare wall-clock comparison alone (only gc_fenced /
                        /// ... (b) claimMount right after this still ...
                        const bool live = !surviving.gc_fenced && surviving.expires_at_ms > now_ms;
```

- Notes: Comment now spells out the layered defence (`claimMount` reclaim gate uses more than a bare wall-clock; token-guarded PUTs; fence-loss latched by keeper). Corruption still prevented; availability skew still latent. Matches the original audit's "confirmed at code" assessment.

### `CAS-080` (SR-2 / SR-3) — Fresh-mount pins GC heartbeat floor to 0 until first renew; `writer_epoch` no overflow guard — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasServerRoot.cpp:249-251` (`next_writer_epoch = next + 1`), `:266-` (`makeMountBody` leaves observation-time fields at their defaults).
- Trigger: Same as the original — a freshly-claimed mount body carries default-zero observation fields, and `next_writer_epoch` incrementing to `UINT64_MAX` has no overflow guard.
- Evidence quote:

```245:251:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasServerRoot.cpp
            if (current.next_writer_epoch == 0)
                current.next_writer_epoch = 1;
        }

        const uint64_t next = current.next_writer_epoch;
        new_state.next_writer_epoch = next + 1;
```

- Notes: `next + 1` still unguarded; reset-to-1 only guards the initial `== 0` case, not an eventual wrap. Unreachable in practice (2⁶⁴ mounts). Transient GC-floor stall on a fresh mount is the same pattern.

### `CAS-078` (PROBE-1) — Capability probe still fails on a shared prefix if two servers race the same `probe_prefix` — 🔴 still-present (call site now scopes it)

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasProbe.cpp:61-` (fresh-key `PutIfAbsent` → `PreconditionFailed` → `NOT_IMPLEMENTED`), call site `ContentAddressedMetadataStorage.cpp:788` (`probe_prefix = physicalKey(view.pool_prefix + "/staging/" + server_root_id + "/probe")`).
- Trigger: Concurrent servers reusing the same `server_root_id` collide on the probe.
- Evidence: The probe prefix is now derived from `server_root_id`, so probe races are constrained to the collision-of-`server_root_id` case (documented as operator-owned, `CAS-064`). The internal `PutIfAbsent` behavior at `CasProbe.cpp:61-67` is unchanged.
- Notes: Matches the audit's "Safe only if `probe_prefix` is unique per mount" — the call site now scopes it by `server_root_id`, but the underlying primitive fault is unchanged. Practically closed unless `server_root_id` is misconfigured; keep 🔴 for line-level completeness.

### `CAS-079` (OSB-1) — Non-atomic HEAD-then-GET remains — 🔴 still-present (now extensively documented as by-design)

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp:599-636` (`ObjectStorageBackend::get`).
- Trigger: HEAD returns `(size, token)`, then a separate GET; a concurrent overwrite of a mutable key straddles the pair.
- Evidence quote:

```612:622:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp
        /// A REPLACEMENT racing the same window (HEAD observes token A, GET reads the bytes of a
        /// subsequently-written incarnation B) is likewise not a hazard: HEAD strictly precedes GET, so
        /// the returned token is never NEWER than the returned bytes — a mixed pair is always
        /// (bytes_newer, token_older), never the reverse. Every consumer of this token uses it as a
        /// conditional precondition (`casPut`/`putOverwrite`/`deleteExact`), which fails closed EXACTLY
        /// in the mixed case, so a stale token costs a retry, never lets a caller act on a
        /// bytes/token pair that never coexisted. This also covers `known_size`: content-addressed blob
```

- Notes: The audit's "genuine read-inconsistency window" is unchanged at the primitive level, but the safety chain (token consumer → `PreconditionFailed` → retry) is now spelled out in code. The read-only-consumer sub-hazard the original called out ("any read-only decision on a mutable object") still exists (no callers documented to consume the pair without a subsequent CAS). Verdict split: 🔴 present at the primitive; ✅ effectively benign for every current consumer.

### `CAS-011` (OSB-3) — GCS versioning-inconclusive still fails OPEN — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp:55-84` (`ObjectStorageBackend::checkPoolPreconditions`).
- Trigger: `isBucketVersioningEnabled()` returns `std::nullopt` (permissions / unsupported) → warn + proceed as if versioning is off.
- Evidence quote:

```60:76:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp
    const auto versioned = object_storage->isBucketVersioningEnabled();
    if (!versioned.has_value())
    {
        LOG_WARNING(getLogger("CasObjectStorageBackend"),
            "CAS on GCS: could not VERIFY the bucket-versioning precondition (the versioning check "
            "request failed or is not supported by this backend) — proceeding on the assumption that "
            "bucket versioning is OFF. If versioning is actually enabled, token-exact DELETEs will "
            "archive noncurrent generations instead of reclaiming storage and GC will silently stop "
            "reclaiming space. Please verify the bucket's versioning setting manually.");
        return;
    }
```

- Notes: Same fail-open-on-unknown for a correctness-critical precondition. Deliberate, logged — unchanged.

### `CAS-073` (PPP-1) — `looksLikePartDir` still false-positives on non-Atomic table names ending in three numeric groups — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartPathParser.cpp:136-168`.
- Trigger: Any three-numeric-group tail (`_2024_01_01`) matches; on non-Atomic databases the right-to-left grammar routes table files as part files.
- Evidence quote:

```156:167:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartPathParser.cpp
    auto is_number = [](const std::string & s)
    {
        if (s.empty())
            return false;
        for (char c : s)
            if (c < '0' || c > '9')
                return false;
        return true;
    };

    const size_t n = groups.size();
    return is_number(groups[n - 1]) && is_number(groups[n - 2]) && is_number(groups[n - 3]);
```

- Notes: Byte-identical grammar. Atomic uuid-anchored paths still safe; non-Atomic exposure unchanged.

### `CAS-096` (BC2-6 part) — Scratch temp-file uniqueness still relies solely on random string (no PID/counter) — 🔴 still-present

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:875,959,1750` (`getRandomASCIIString(32)`).
- Trigger: All three CAS temp-file kinds (local scratch, staging key, inline-overflow spill) name themselves as `<prefix>/<getRandomASCIIString(32)>.tmp`. No PID/counter component; safe by birthday only.
- Evidence quote:

```875:875:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
            const std::string staging_key = metadata_storage.stagingKeyPrefix() + "/" + getRandomASCIIString(32) + ".tmp";
```

```1750:1750:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
    temp_path = temp_dir + "/" + getRandomASCIIString(32) + ".tmp";
```

- Notes: 32-char ASCII is astronomically safe by count; PID/counter is a belt-and-braces hardening, not a correctness fix. Verdict is 🔴 because the audit called this out as still-desired hardening; practically 📐 by-design.

### `CAS-099` (BC6-3) — `setLastModified` on a committed part remains an accept-and-ignore no-op — 🔴 still-present (now admission-gated)

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1180-1186`.
- Trigger: A caller "touching mtime to bump age" against a CAS-backed part still gets a silent no-op (the timestamp is discarded).
- Evidence quote:

```1180:1186:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp
void ContentAddressedTransaction::setLastModified(const std::string &, const Poco::Timestamp &)
{
    /// Timestamps are derived for content addressing (the publish stamp), so accept and ignore them -- but
    /// gate as a Write (previously-no-op site, rev.7 §1): never silently accept it on a Vanished/uncertain
    /// disk.
    metadata_storage.checkOpAdmitted(CasOpClass::Write);
}
```

- Notes: `checkOpAdmitted(Write)` now fails-loud on a Vanished/uncertain disk (an improvement — no more silent success on a broken disk), but on a healthy disk the semantic is unchanged: silently drop the requested timestamp. The `clearOldTemporaryDirectories` sub-finding of the audit's CAS-099 has no matching sink in the current tree (no method by that name on the CAS transaction/storage surface); on a live disk, GC is still the temporary-directory reclaimer.

### `CAS-027` (RSC-2) — Additive-field drop on re-encode by an older build still latent — 🔴 still-present (form has shifted)

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp:145-152` and every text/JSON decoder that uses `KeyStrictness::Tolerant + skipUnknown`.
- Trigger: A tolerant JSON decoder reads a newer additive key, silently skips it (`r.skipUnknown(key)`), and the write-side re-encodes only the fields the struct knows about — additive fields are lost on re-encode by an older build.
- Evidence quote:

```145:152:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp
        while (r.nextKey(key))
        {
            if (key == "me") me = r.readString();
            else if (key == "mb") mb = r.readU64String();
            else if (key == "mo") mo = r.readU64Number();
            else if (key == "ns") ns = r.readString();
            else if (key == "pd") pd = r.readHex128();
            else r.skipUnknown(key);
        }
```

- Notes: The whole codec family switched from protobuf to text/JSON, but the "read into struct → encode from struct" shape is preserved, so the additive-field-loss hazard is preserved. `payload_digest` verification on decode (see below, CAS-025 fixed) makes decode-then-re-encode by an older reader still verifiable — but the *older writer that mutates a control object then re-encodes* still drops newer additive fields. Same class of mixed-version control-plane data loss as before.

---

## Findings fixed / no longer reproducible

### `CAS-025` (MC-1) — ✅ FIXED

- `PartManifest.payload_digest` is now recomputed and compared on decode.
- Anchor for fix: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp:293-302`:

```293:302:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp
    /// Recompute and verify `payload_digest` last, over the fully-decoded body. `computePayloadDigest`
    /// builds its own probe copy with payload_digest zeroed before hashing (see below), so calling it
    /// directly here on `m` (whose payload_digest is whatever was read off the wire) is safe and
    /// matches encode's own computation exactly.
    const UInt128 expected_digest = computePayloadDigest(m);
    if (expected_digest != m.payload_digest)
        throw Exception(ErrorCodes::CORRUPTED_DATA,
            "PartManifest: payload_digest mismatch, expected {}, got {}",
            u128ToHex(expected_digest), u128ToHex(m.payload_digest));
```

- The audit's exact remediation ("verify `payload_digest` against `computePayloadDigest` when decoding a manifest read from storage") is what landed.

### `CAS-115` (MC-2) — ✅ FIXED

- The adjacent-only duplicate-path check the audit called "assumes sorted storage order" is now proven sufficient in code with an explicit worked example (`CasPartManifestFormat.cpp:257-267`): strict `<` against the immediate predecessor catches non-adjacent duplicates as well, because the intermediate ordering constraint fires on the forgery. Comment cites the exact scenario the audit constructed.

### `CAS-028` (RF-1) — ✅ FIXED

- The old `CasRunFile.cpp` is gone. The replacement (`CasRecordStreamFormat.cpp`) parses each record via `readLine(hashing, line_cap, "cas_run")` + `JsonObjectReader` — no `klen`/`plen` `operator[]`/`substr` arithmetic, all bounds checked in `readLine` and JSON parsing. The unchecked-record-loop hazard the audit anchored at `CasRunFile.cpp:435-459` has no counterpart in the new code.

### `CAS-026` (RSC-1) — ✅ FIXED

- All four protobuf decoders (`decodeRootShard`, `decodeGcState`, `decodeRetiredSet`, `decodeFoldSeal`, `decodeOutcomeLog`) are gone. The replacement text/JSON decoders route every object through `readLine(in, line_cap, ...)` (`CasCodecUtil.h` / `CasTextFormat.h`), and every format enforces an explicit `object_cap` from `CasFormat.cpp:93-108` (`FormatTraits.object_cap`). No `ParseFromArray` remains; the `static_cast<int>(data.size())` overflow class no longer applies.

### `CAS-039` (ENV-1) — ✅ FIXED

- The envelope no longer carries a numeric `logical_size` at all. `CasBlobEnvelopeFormat.cpp:230-248` derives `header_len` from the '\n' terminator position at decode, and there is no additive size-consistency check that could be bypassed by `uint64_t` wrap. The audit's exact remediation ("check `logical_size ≤ object_size` and `header_len ≤ object_size` before the addition") is superseded by simply not having the field.

### `CAS-075` (ENV-2 / ENV-3) — ✅ FIXED (form has changed; the specific hazard is gone)

- No more `header_hash` (CityHash64 over `[0,94)`). No more "critical extension" flag bit driven by writer honesty. The envelope is now text/JSON with `KeyStrictness::Tolerant`; unknown keys prefixed `!` (the frozen `UNKNOWN_FORMAT_VERSION` convention) are treated as critical by the JSON reader (`CasBlobEnvelopeFormat.cpp:217`, `r.skipUnknown(key)` on a `!`-prefixed key throws `UNKNOWN_FORMAT_VERSION`). The audit's two sub-findings ("header_hash covers only the 94-byte core"; "critical extension is writer-controlled") both no longer apply as-worded. NB: the underlying "any single bit flip inside the header pad zone survives" question is now addressed by the pad-verify sweep (`:230-248`).

### `CAS-023` (STORE-C1) — ✅ FIXED

- Teardown ordering now uses an explicit `remount_shutting_down` latch held under `remount_thread_mutex`, and every scheduling entry re-checks it under that lock BEFORE arming a new thread. Anchor for fix: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasMountRuntime.cpp:486-502` (`stopRemountThread`) and `:431-471` (`scheduleRemount`):

```486:502:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasMountRuntime.cpp
void CasMountRuntime::stopRemountThread()
{
    /// Refuse further recovery arming under the same mutex used by `scheduleRemount`, before joining.
    /// Thus a keeper callback racing with teardown cannot re-arm the recovery thread after the join.
    {
        std::lock_guard g(remount_thread_mutex);
        remount_shutting_down.store(true);
    }
    /// Stop recovery first; it could otherwise recreate the keeper while the heartbeat is being retired.
    remount_stop.store(true);
    remount_cv.notify_all();
    {
        std::lock_guard g(remount_thread_mutex);
        if (remount_thread.joinable())
            remount_thread.join();
    }
}
```

- The audit's exact fix ("stop `mount_keeper` before joining/destroying the remount machinery; or re-join `remount_thread` after `mount_keeper->stop()`") is realized through the shutting-down latch + double-checked lock pattern above. `Pool::scheduleRemountForTest()` and the callCount seam persist the observability the audit relied on.

### `CAS-111` (TXN-3) — ✅ FIXED

- `unlinkFile` of a committed content file is no longer a fail-open no-op. It now stages a `content_removed` mark that is resolved at `publishStaging` (republishes the manifest minus the removed paths). Anchor for fix: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1509-1601`, especially the invariant note at :1511-1531 and the mark itself at :1567 (`st.content_removed.insert(r->file);`). Comment at :1530-1531 explicitly says "this closes the file's former fail-open (a committed content file could never actually be deleted on its own)".

### `CAS-072` (GC-1) — 🟡 needs-repro (evidence not present line-level in the new tree)

- The old `runRegularRound` R5b hand-off code path lived in `CasGc.cpp` at :371-404 in the original audit. `CasGc.cpp` has been substantially refactored (2989-line file; `runOneRound`/related identifiers changed). A grep of the current tree for the specific hand-off pattern ("wholesale prune skipped-while-referenced" or a `snap_pruned_through` cursor advance) does not find the same call-site shape at the same line range; the routines have been renamed and split. This audit is line-only, so without a re-anchoring pass over `CasGc.cpp` (out of scope for this batch) I cannot cite a current-code file:line — flagged as 🟡 for the GC-specific audit batch to re-anchor.

---

## New findings (not in original audit)

- **NEW-codeonly-line-1** (Low / hardening) — Non-cryptographic checksum still trusted on run objects, now under `CityHash128`-of-object-body — `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasRecordStreamFormat.cpp:210-219` (`sourceEdgeRunChecksum`). The change from CRC32C to chained CityHash128 does not close the "forgeable, pool-participant can plant a valid run" class (`CityHash128` is not cryptographic either); combined with `CAS-004` (no intra-pool authz) the trust boundary is unchanged. This is really an amplifier of an existing high-severity finding, but it is worth calling out that the code comment "Use the same chained CityHash128 and default block size as the reader" doubles the audit's `BUILD-1` / `CAS-037` concern (a `DBMS_DEFAULT_HASHING_BLOCK_SIZE` change now silently forks *two* independent hash chains, not one).
- **NEW-codeonly-line-2** (Info / hardening) — Envelope pad-zone now enforces "must be ASCII space up to '\n'" — `CasBlobEnvelopeFormat.cpp:230-248`. Reads any non-space byte as `CORRUPTED_DATA`. Verified-correct and load-bearing. This is a real *improvement* over the old envelope (which allowed arbitrary TLV in the pad zone with a writer-controlled critical flag), and closes the smuggling side of the old `ENV-3` finding. Recorded so it can be added to the OK list.
- **NEW-codeonly-line-3** (Low / info) — `PartWriteTxn::adoptEvidence` records the sender-supplied `entry.blob_size` in `deps[entry.ref]` and then verifies **only that a blob exists** in `promote` — the mismatch with `CAS-025`'s new `payload_digest` verification is subtle: `payload_digest` verifies the manifest's *canonical encoding* (including `blob_size`), so if the sender's manifest passes decode, its `blob_size` fields are pinned to what the sender computed — but the receiver still adopts them without cross-checking against the pool's canonical blob envelope. Same net gap as MW-1; called out because `CAS-025`'s fix does NOT close this. See MW-1 (`CAS-031`) above.
- **NEW-codeonly-line-4** (Info) — `checkNamespace` is now *also* called on operator-supplied `server_root_id`-derived subpaths via a wide surface (`refsNamespacePrefix`, `manifestNamespacePrefix`, `namespaceFileKey`, `namespaceFilesPrefix`) — so the missing `.`/`..` guard (LAY-1) is unchanged in scope, but the number of code sites depending on it silently accepting benign namespaces (via `escapeForFileName`) has grown. No new hazard, but the "unenforced external invariant" the audit called out is now load-bearing across more call sites; fixing LAY-1 has correspondingly larger safety return.

---

## By-design / N/A / info

- `CAS-076` `FormatId::Roster` — kept in the `changePoints` switch, deliberately absent from `TRAITS`, documented at `CasFormat.h:126`. Header comment now explicitly says "reserved" — closer to `📐 by-design` than a defect, but the audit's "defined-but-magic-less" characterization is factually still true, so kept 🔴.
- `CAS-025` (MC-1) — reconfirmed fixed on the read side, and additionally on the receiver-relink path (relink receiver in `prepareAdoptFromManifest` still ignores `payload_digest` deliberately, but the LOCAL read path of every persisted manifest verifies it).
- `CAS-107` (endian / version-stability) — outside this audit's line-only scope; no new evidence line-level.
- INSTR-1 (`classifyCasNs` unanchored substring match) — verified still present in `CasInstrumentedBackend.cpp`, still `⚪ info`. No behavior change.
- `CAS-036` (BUILD-2, `blob_header_len` floor) — the floor is enforced by `validatePoolBlobHeaderLen` (`CasPoolMeta.cpp:111`); a value below the mandatory provenance-TLV need would still throw at *encode* rather than at pool-create, but the whole "critical-vs-diagnostic" provenance question has changed shape now that the envelope is text/JSON with a truncated `ref` and a numeric-key budget arithmetic (`CasBlobEnvelopeFormat.cpp:99-160`). Deferred to the write-protocol / bc-family audits for line-level re-anchoring.

---

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-024 (STORE-2) | Med | 🔴 still-present | `Pool/CasManifestReader.cpp:144-168` |
| CAS-023 (STORE-C1) | Med | ✅ fixed | `Pool/CasMountRuntime.cpp:486-502` (`remount_shutting_down` latch under `remount_thread_mutex`) |
| CAS-025 (MC-1) | Med | ✅ fixed | `Formats/CasPartManifestFormat.cpp:293-302` |
| CAS-026 (RSC-1) | Med | ✅ fixed | protobuf decoders replaced with text/JSON + `object_cap`; `Formats/CasFormat.cpp:93-108` (traits caps), `CasRecordStreamFormat.cpp` etc. |
| CAS-027 (RSC-2) | Med | 🔴 still-present | `Formats/CasPartManifestFormat.cpp:145-152` (`skipUnknown` + decode-to-struct → additive fields dropped on re-encode) |
| CAS-028 (RF-1) | Med | ✅ fixed | `Formats/CasRecordStreamFormat.cpp:228-304` (`readLine` + `JsonObjectReader`, bounded record parse) |
| CAS-030 (SR-1) | Med | 🔴 still-present | `Pool/CasServerRoot.cpp:217,276` |
| CAS-031 (MW-1) | Med | 🔴 still-present | `Pool/CasPartWriteTxn.cpp:781-796`; receiver at `ContentAddressedMetadataStorage.cpp:2143-2221` |
| CAS-032 (SCHED-1) | Med | 🔴 still-present | `Gc/CasGc.cpp:2989-3003` |
| CAS-022 (TXN-2) | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1200-1287` |
| CAS-039 (ENV-1) | Med | ✅ fixed | `Formats/CasBlobEnvelopeFormat.cpp` — no `logical_size` field remains |
| CAS-066 (PM-1) | Low | 🔴 still-present | `Pool/CasPoolMeta.cpp:117-124` |
| CAS-072 (GC-1) | Low | 🟡 needs-repro | `Gc/CasGc.cpp` refactored; original :371-404 no longer maps 1:1 |
| CAS-073 (PPP-1) | Low | 🔴 still-present | `Parts/PartPathParser.cpp:136-168` |
| CAS-074 (LAY-1) | Low | 🔴 still-present | `Formats/CasLayout.cpp:260-284` + `CasLayout.h:229-235` (`mountpointObjectKey`) |
| CAS-075 (ENV-2/3) | Low | ✅ fixed | Envelope rewritten as text/JSON with pad-zone enforcement `CasBlobEnvelopeFormat.cpp:230-248` |
| CAS-076 (FMT-1) | Low | 🔴 still-present | `Formats/CasFormat.cpp:112-118` (`traitsFor` throws for `FormatId::Roster`) |
| CAS-077 (GS-1) | Low | 🔴 still-present (partial) | `Formats/CasFoldSealFormat.cpp:189` (`cls` uint8 truncation cast); `tt` half fixed via `tokenTypeFromWord` |
| CAS-078 (PROBE-1) | Low | 🔴 still-present (scoped by call site) | `Backend/CasProbe.cpp:61-67`; call-site at `ContentAddressedMetadataStorage.cpp:788` |
| CAS-079 (OSB-1) | Low | 🔴 still-present (documented by-design) | `Backend/CasObjectStorageBackend.cpp:599-636` |
| CAS-011 (OSB-3) | Low/Med | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp:55-84` |
| CAS-080 (SR-2/3) | Low | 🔴 still-present | `Pool/CasServerRoot.cpp:245-251,266-276` |
| CAS-096 (BC2-6 part) | Low | 🔴 still-present | `ContentAddressedTransaction.cpp:875,959,1750` (no PID/counter) |
| CAS-099 (BC6-3) | Low | 🔴 still-present (now admission-gated) | `ContentAddressedTransaction.cpp:1180-1186` |
| CAS-111 (TXN-3) | Low | ✅ fixed | `ContentAddressedTransaction.cpp:1509-1601` (`content_removed` mark resolved at publish) |
| CAS-112 (C-U6/7) | Low | 🔴 still-present | `ContentAddressedTransaction.cpp:531-533,1188-1191` (`notYet("generateObjectKeyForPath"/"chmod")`) |
| CAS-115 (MC-2) | Low | ✅ fixed | `Formats/CasPartManifestFormat.cpp:257-267` (adjacent-only proven sufficient with worked-forgery comment) |
| NEW-codeonly-line-1 | new-Info | 🔴 amplifies CAS-037/CAS-003 | `Formats/CasRecordStreamFormat.cpp:210-219` |
| NEW-codeonly-line-2 | new-Info | ⚪ info (improvement) | `Formats/CasBlobEnvelopeFormat.cpp:230-248` |
| NEW-codeonly-line-3 | new-Info | 🔴 amplifies CAS-031 | `Pool/CasPartWriteTxn.cpp:781-796` |
| NEW-codeonly-line-4 | new-Info | ⚪ info | `Formats/CasLayout.cpp:260-284` (widened blast radius, same defect) |
