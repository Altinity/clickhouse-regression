## ad1-hash-determinism

- **NEW-AD1-1 (Low — `blob_hash_allow_new` semantics are dedup-fracturing by design).** Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPoolMeta.cpp:75-101`. Trigger: an operator flips `<blob_hash_allow_new>1</blob_hash_allow_new>` and reopens with a different algo. The pool CAS-unions the new algo into `algos_used`, but from that point on **new writes and old writes of byte-identical content live at different keys** (`blobs/ch128/S/<hex>` vs `blobs/sha256/S/<hex>`, per `CasLayout.cpp:36`). This is the intended safety behavior (never overwrite), but it means the *dedup ratio degrades permanently* for the affected content, and there is no operator warning in the code path — the change of algo mid-life is a silent dedup fork event that only shows up in `system.parts.bytes_on_disk` vs physical bytes. Severity is Low because it's opt-in and correctness-preserving; it deserves a doc/warn.
- **NEW-AD1-2 (Info — `payload_digest` is hardcoded to CityHash128 regardless of pool algo).** Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp:306-317` (`computePayloadDigest` calls `CityHash_v1_0_2::CityHash128`). By comment (`CasPartManifestFormat.h:95-100`) `payload_digest` is *integrity/debug only*, "never a key, never dedup, never in-degree", so this is not a correctness issue — but a sha256-configured pool still has one internal integrity check (manifest self-digest) that is non-cryptographic. Worth noting as a scope caveat when someone reasons "sha256 pool ⇒ all CAS hashes are crypto".
- **NEW-AD1-3 (Info — CAS-025 fix incidentally lands here).** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp:293-301` now re-computes `payload_digest` on `decodePartManifest` and throws `CORRUPTED_DATA` on mismatch. Original AD1 audit predates this; it belongs to `bc4-protobuf-decode` / integrity family, but I record the anchor here because it appeared while grepping for hash-verification sites.

---

## ad2-deletion-erasure

- **NEW-ad2-1 (High for compliance) — `isBucketVersioningEnabled()` unknown → mount proceeds.**
  - Anchor: `Backend/CasObjectStorageBackend.cpp:61-75`.
  - Trigger: on a bucket where `GetBucketVersioning` errors (permissions denied) or the backend has
    no answer, CAS logs a WARNING and mounts. If versioning is in fact ON, every future
    `deleteExact` becomes a delete-marker (`Gc/CasGc.cpp:519`) and reclaim silently stops.
  - Rationale for elevating: for a regulated deployment the correct default is fail-closed on
    "unknown", not "assume off". The comment at `:64-68` acknowledges the design choice explicitly.

- **NEW-ad2-2 (Med) — versioning precondition is GCS-only; S3 versioning / object-lock / CRR /
  soft-delete not checked.**
  - Anchor: `Backend/CasObjectStorageBackend.cpp:57-58` (`if (mode != Mode::Native || native_token_type != TokenType::Generation) return;`).
  - Trigger: mount CAS over an S3 bucket with versioning, MFA-delete, object-lock retention,
    lifecycle rules that transition-to-Glacier before expiring, or CRR to a bucket CAS never
    deletes. `checkPoolPreconditions` returns immediately without touching any of these. The GC-side
    "delete marker created" log warning (`Gc/CasGc.cpp:519`) is the only after-the-fact signal.
  - Effect: the original AD-2 caveat "physical erasure depends on backend DELETE semantics" (ERASE-5)
    is now partly enforced for one dialect and left completely unenforced for the more common one.

- **NEW-ad2-3 (Med) — no post-`deleteExact` verification anywhere in the pipeline.**
  - Anchor: `Backend/CasBackend.h:102-132` (`DeleteOutcome`, `created_delete_marker`); no
    HEAD-after-DELETE is performed in `Gc/CasGc.cpp` around the `deleteExact` sites
    (`Tools/CasDecommission.cpp:57,81` are the only other `deleteExact` calls; neither re-heads).
  - Trigger: any object-store that acknowledges DELETE but retains the object (soft-delete window,
    replicated-copy retention). CAS marks the blob reclaimed and drops it from `blobIndegree`; no
    later fsck notices the survivor because the ref side is gone.
  - Effect: compliance-grade "prove erased" cannot be assembled from the outcomes CAS records; the
    tool asked for in the original AD-2 §3 remains impossible to build on top of the current API.

- **NEW-ad2-4 (Med) — `SYSTEM CONTENT ADDRESSED FORGET` explicitly documents "erasure NOT verified".**
  - Anchor: `Pool/CasPool.cpp:135,328-332,755,966` and `ContentAddressedMetadataStorage.cpp:926-929,1046,1140-1160`.
  - Evidence quote (`Pool/CasPool.cpp:332`):
    > "decommissioned by SYSTEM CONTENT ADDRESSED FORGET — erasure was NOT verified; if this was a"
  - Notes: The operator's only advertised "make this pool go away" verb is spec'd, in the code
    itself, as a non-erasure assertion. A compliance auditor reading these strings has no
    alternative primitive to point at. Reinforces ERASE-1/ERASE-2/ERASE-5 as a contractual gap.

- **NEW-ad2-5 (Low) — `gc_snap_generations_to_keep` retention floor is uncapped by wall-clock.**
  - Anchor: `Pool/CasPool.h:79-84`, `Gc/CasGc.cpp:762,2319`.
  - Trigger: a CAS pool with very-slow GC rounds retains the last N snap generations even if each
    generation is weeks old. The metadata about reclaimed subjects (ERASE-4) can therefore live
    much longer than "3 rounds" implies.
  - Effect: minor amplification of ERASE-4; strictly a documentation / metric gap.

---

## ad3-day2-dr-runbook

- **NEW-ad3-1 (Low — SQL fsck cannot bound its runtime).**
  `Cas::runFsck` accepts a `deadline` and a `partial_on_deadline` flag
  (`CasFsck.h:148-150`), but `runContentAddressedFsck` in
  `InterpreterSystemQuery.cpp:2524-2551` never plumbs the query-level
  `max_execution_time` / an explicit `DEADLINE '...'` clause into it.
  Result: an operator running `SYSTEM CONTENT ADDRESSED FSCK` against a
  large / slow pool has no way to say "give me what you have after
  10 min"; the scan runs to completion or throws `TIMEOUT_EXCEEDED`
  from `checkDeadline` (`CasFsck.cpp:43-48`). Anchor:
  `InterpreterSystemQuery.cpp:2537` (`runFsckNow(false)` — no
  `deadline`).

- **NEW-ad3-2 (Low — `SYSTEM CONTENT ADDRESSED GC STOP` truthfully-but-misleadingly reports `is_leader`).**
  The comment at `InterpreterSystemQuery.cpp:1018-1023` explains that
  after GC is stopped, an explicit `GC RUN` can still transiently set
  `is_leader=1` on the disk — and `system.content_addressed_mounts.is_leader`
  will show that until a peer steals the lease. This is documented and
  intentional but is a Day-2 footgun: dashboards keyed on
  `is_leader AND NOT gc_running` will see a phantom leader window
  during operator-initiated GC RUNs after a STOP.

- **NEW-ad3-3 (Low — `SYSTEM CONTENT ADDRESSED FORGET` explicitly does not verify erasure).**
  `InterpreterSystemQuery.cpp:2570-2575` — the log line spells out
  "erasure NOT verified. The disk stays registered and answers store-class
  access with a typed error". Combined with CAS-093 (fsck cannot
  repair) and CAS-084 (MPU orphans), a `FORGET` on a disk with in-flight
  writes / orphaned MPUs leaves cleanup entirely to whatever bucket
  lifecycle rule the operator remembered to configure. Worth a runbook
  note that `FORGET` is an *assertion*, not a *reclamation*.

- **NEW-ad3-4 (Info — `Nullable` peer-row columns in `content_addressed_mounts` are a good pattern to keep).**
  `StorageSystemContentAddressedMounts.cpp:194-210` deliberately writes
  `NULL` for `is_leader` / `pending_reclaim` / `last_success_age_seconds` /
  `wedged_namespace_count` on rows describing *other servers*' mounts.
  This prevents the "peer B is GC leader" misread the comment calls out
  — worth codifying as a pattern for future per-disk/per-node CAS views
  (relates to CAS-101 quirks).

---

## ad4-migration

- **NEW-MIG-1 (Med — CAS-041 explicit sub-case: CAS → CAS same-pool MOVE does NOT relink; it byte-copies through streaming reads+writes).**
  - Anchor: `src/Storages/MergeTree/MergeTreePartsMover.cpp:223-282` (no `getPoolUUID` / pool-identity
    branch); `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:735-758` (CA-aware `clonePart` runs
    `copyDirectoryContentIntoTransaction` — a streamed read from src + streamed write to dst, not a
    manifest-level relink).
  - Trigger: `ALTER TABLE ... MOVE PARTITION ... TO DISK d2` where both `d1` and `d2` are CAS disks
    that share the same pool (same `pool_uuid`).
  - Why new: the wire-protocol fetch path (`DataPartsExchange.cpp`) DOES gate on `receiver_pool_uuid ==
    sender.getPoolUUID()` and relink instead of byte-fetching. The equivalent optimization is
    **missing** on the local cross-disk MOVE path. Cost impact: same-pool CAS→CAS MOVE re-uploads
    every blob body, then dedups on landing via HEAD-first (`CasPartWriteTxn.cpp:186-214`). The dedup
    HEAD hit avoids the body PUT, but the source disk is still fully read and the request cost is
    per-blob HEAD × N blobs, plus manifest re-encode/publish. A same-pool relink (publish new ref
    pointing at existing manifest+blobs) would be O(1) manifest-copy. This is a direct instance of
    CAS-041 in the local MOVE path.
  - Severity: Med (cost/latency cliff, not a correctness issue; dedup on landing saves storage but
    not read/HEAD I/O).

- **NEW-MIG-2 (Med — CAS-210 confirmed: HEAD-first "dedup on landing" trusts backend object identity by NAME only; no body re-hash verify).**
  - Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp:189-212`.
    On a HEAD hit, the writer calls `observeAndAdmit(ObjectKind::Blob, logical_ref, key, hr)` and
    admits the existing object as its own without a body GET or hash re-verify.
  - Evidence quote (line 190-201):
    > `const HeadResult hr = store->backend().head(key);`
    > `if (hr.exists) { ... const BlobDepRecord dep = observeAndAdmit(...); return ... HeadHit; }`
  - Trigger: any migration/write where the target blob key already exists (dedup case) — the primary
    upside of onto-CAS migration.
  - Threat model: the writer computed `logical_ref` from its own bytes (`write-mint site` — see
    `CasPartWriteTxn.cpp:165-168` comment: "the caller already produced the full `BlobRef` pair (algo
    + digest)"). If the existing S3 object under `key` was silently mutated (LIFE-1/LIFE-2/LIFE-5-like
    scenario) or was written by a buggy earlier build under the same key but different bytes, the new
    writer will **adopt the corrupt object without ever reading it**. INV-NO-LOSS is respected (a ref
    exists), but the ref points at bytes the writer never validated.
  - Note the header of `uploadBlobDetached` (line 172-176) itself says:
    > "The source is RE-READABLE ... it can be invoked MULTIPLE times ... so we never materialize the
    > whole blob into memory here. The byte count is verified against `source.size` at each streaming
    > write site (via the sink buffer's `count()`), not by a full pre-materialization"
    The byte COUNT is verified; the byte CONTENT is not — neither on the write side (streamed
    without in-flight hash) nor on the HEAD-hit adoption side.
  - Severity: Med — the dedup HEAD-hit trust is load-bearing for INV-1 (the "content-addressed" claim),
    but the trust is only as strong as the assumption that no other writer/lifecycle rule ever put wrong
    bytes under a CAS key. AD-2 (deletion-erasure), LIFE-1/LIFE-2/LIFE-5 (bucket-feature) and any
    format-version-bump-with-key-collision would all silently propagate through this path.

- **NEW-MIG-3 (Med — provenance envelope field is present but NOT driven by the operation kind; every fresh CAS write hardcodes `ProvenanceOp::Insert`).**
  - Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:148-155`:
    ```cpp
    st.build = metadata_storage.store()->beginPartWrite(
        Cas::PartWriteInfo{.intended_ref = ...,
                       .intended_namespace = r.ns, .op = Cas::ProvenanceOp::Insert});
    ```
    Every part-write transaction is opened with `op = Insert`, regardless of whether the caller is
    `INSERT SELECT` (migration), a merge output, a mutation output, MOVE-landing, or RESTORE-landing.
  - Anchor: `ProvenanceOp` enum values (`CasBlobEnvelopeFormat.h:43`) include `Merge`, `Mutation`,
    `Attach`, `Repack`, `Other` — but only `Insert`, `Other`, and `Attach` are ever emitted from the
    production CAS code:
    - `Attach` — `ContentAddressedMetadataStorage.cpp:2205` (attach path).
    - `Other` — `ContentAddressedTransaction.cpp:381, 741` (repoint/relink cases) and
      `Parts/PartFolderAccess.cpp:531` (`publishEntries` in cross-ref republish).
    - `Insert` — the only fresh-write value (line 154).
  - Trigger: any migration or merge/mutation write; the `op` blob-envelope field is factually wrong
    for merges, mutations, MOVE-landings, and RESTORE-landings (all recorded as `Insert`).
  - Impact: the provenance field advertised in `CasBlobEnvelopeFormat.cpp:117-121` (`ts`, `by`, `op`,
    `ch`) is only trustworthy for `Attach` and `Other`; the `Insert` label is the default and gives no
    real signal about migration origin. Tools like `CasInspect` (which decode the field —
    `CasInspect.cpp:394-399`) present operator-visible data that is not fidelity-checked. Static
    audits that rely on `op` to distinguish "migrated from outside CAS" vs "originally created inside
    CAS" cannot use this field.
  - Severity: Med — not a correctness bug (bytes are still content-addressed), but a
    diagnostic/attestation gap directly relevant to the migration audit (was the point of adding the
    enum in the first place).

- **NEW-MIG-4 (Low — off-CAS MOVE reads never re-verify blob against manifest/BLAKE hash — INT-1 exposure at migration boundary is symmetric with NEW-MIG-2).**
  - Anchor: same as MIG-6 anchor (`DataPartStorageOnDiskBase.cpp:707-710` streamed copy loop), plus
    the CAS backend's plain ranged GET path (`CasObjectStorageBackend.cpp` — no
    verify-after-read hook).
  - Note: this is a **strengthening** of MIG-6 in the original audit. The new bit is that the CAS
    write-side finding NEW-MIG-2 makes the read-side blind-copy strictly worse for chains: corruption
    admitted at write time (NEW-MIG-2) propagates unchecked at off-CAS migration read time
    (NEW-MIG-4).
  - Severity: Low (as MIG-6). MergeTree-level `checksums.txt` and `CHECK TABLE` still catch it, but
    only if the operator opts in.

---

## ad5-resource-exhaustion

- **NEW-ad5-1 (Med — the manifest write path is hard fail-closed only; no smoothing at all near the caps).** `Pool/CasPartWriteTxn.cpp:824-872` enforces `kMaxManifestEntries = 1_048_576`, `kMaxManifestInlineBytesTotal = 16 MiB`, `kMaxLargestInlineEntryBytes = 1 MiB`, `kMaxManifestEncodedBytes = 256 MiB` as unconditional `LIMIT_EXCEEDED` throws. The original AD-5 recommended a governor + surfaced distance-to-hard-limit metric so an operator could see the wedge coming; the current design has **neither** the ≤ 1 s soft-limit backpressure nor a "distance-to-cap" metric. Under sustained churn, the first sign of trouble is a failed write, not a warned-and-throttled one. Severity: Med (scalability / DoS ergonomics).
  - Anchor: `Pool/CasPartWriteTxn.cpp:824-872` (`stageManifest`) — no soft-limit path; `Pool/CasPool.h:174` (`snapshot_log_bytes_threshold = 1 MiB`) is a snapshot-publish trigger, not a mutation-side warning.

- **NEW-ad5-2 (Low — `enforceRefTableCacheBudget` LRU-evicts a namespace's cached state; a hot table churning enough to force re-hydration under memory pressure pays repeated recovery cost.)** `Pool/CasRefLedger.cpp:762-810` walks all cached tables and evicts the LRU non-`keep_ns` entries until the total is ≤ `ref_table_cache_bytes` (default 256 MiB, `Pool/CasPool.h:204`). At extreme multi-tenancy (many active namespaces, each with large committed / owned_manifests state), this can become a re-recovery hot loop: table evicted → next touch triggers `stateFromSnapshot` + tail replay + `materializeCommitted` (`Pool/CasRefLedger.cpp:560-577`), which is O(N) per table. Not a leak, but a soft scale cliff distinct from the original RES-3.
  - Anchor: `Pool/CasRefLedger.cpp:762-810` (eviction loop) + `560-577` (materialize cost).

- **NEW-ad5-3 (Low — `RefLog` / `RefSnapshot` seal-decode ceilings are 64 MiB decompressed, and this is enforced at decode, but the encode-side complete-table admission uses the same 64 MiB budget with only `kRefAdmissionSafetyMargin` headroom, i.e. essentially zero real slack.)** `Formats/CasFormat.cpp:98-99` gives the RefLog and RefSnapshot 64 MiB decompressed decode ceilings; `Pool/CasRefLedger.cpp:572-577` pre-subtracts `4 + ns.size() + kRefAdmissionSafetyMargin` and clamps to zero. A namespace with a very long name plus a snapshot right at the budget can be admissible on the encode side yet fail at decode on the next mount if any per-field overhead grew after encode (e.g., codec change bumping framing). Belt-and-suspenders concern, low severity, but worth logging because the encode / decode budgets are the exact same number.
  - Anchor: `Formats/CasFormat.cpp:98-99` + `Formats/CasRefSnapshotFormat.h:67` (`ref_snapshot_max_bytes = ref_removal_max_bytes`) + `Pool/CasRefLedger.cpp:572-577`.

---

## ad6-s3-lifecycle-cross-region

- **NEW-AD6-1 (Low)** — GCS-versioning precondition treats "cannot verify" as fail-open by design, but the log level is `LOG_WARNING` inside `checkPoolPreconditions`, which many operators filter out at aggregation. Anchor: `Backend/CasObjectStorageBackend.cpp:69-74`. Trigger: mount on a GCS bucket where `GetBucketVersioning` fails (permissions, custom endpoint). Suggested hardening: promote to `LOG_ERROR` plus surface in `system.content_addressed_mounts` so the ambiguous case is visible to operators. This narrows CAS-011 rather than adds a new failure mode, but was not called out in the original AD-6 write-up.
- **NEW-AD6-2 (Info)** — `Pool/CasPool.cpp:1327` bakes the "S3 strongly consistent since 2021" assumption in a comment, without a runtime capability check or a documented supported-backends matrix (RustFS is explicitly listed as unverified in the same comment). Anchor: `Pool/CasPool.cpp:1321-1330` (`listNamespaces`). Not a bug per se, but the contract on which CAS-087 depends is asserted in a comment only.

---

## ad7-protocol-skew

- **NEW-ad7-1: `assertEOF` after `readStringBinary(sender_manifest_bytes)` will hard-fail any future v2-with-trailer sender talking to this exact v2 receiver.** Severity: Info. Anchor: `src/Storages/MergeTree/DataPartsExchange.cpp:936-937`.
  - Trigger: a future `part_manifest_v3` framing that adds a trailing field will require a cookie-value bump to `"part_manifest_v3"`; otherwise this receiver's `assertEOF` will throw on the extra bytes.
  - Notes: not a bug — it is the *intended* forward-incompat behavior (SKEW-1 hardening's inverse: any future framing addition MUST bump the cookie). Worth documenting in the wire-contract text alongside `CA_RELINK_COOKIE_VALUE`. The header comment on `CA_RELINK_COOKIE_VALUE` (`:122-128`) partially covers this; making the assertEOF-implies-cookie-bump requirement explicit would help future authors.

- **NEW-ad7-2: Cookie-value gate happens BEFORE the pool-uuid re-check, but AFTER `ca_relink` cookie parse — an empty cookie value on the wire is silently treated as "no relink" rather than as a malformed offer.** Severity: Info. Anchor: `DataPartsExchange.cpp:889-890`.
  - Trigger: a future sender bug that emits an empty cookie value would fall through to the byte fetch silently rather than logging the anomaly.
  - Notes: safe fallback direction, but obscures a diagnosable sender bug. Non-actionable.

- **NEW-ad7-3: `locate()` does not read the envelope's own `header_len` before ranging — soft coupling to pool_meta's `blob_header_len` invariant.** Severity: Info (was CAS-024 severity CORRECTNESS; the invariant is enforced elsewhere, so this is a note about the coupling, not a live bug). Anchor: `src/.../Pool/CasManifestReader.cpp:144-168`.
  - Trigger: any future code path that permits an envelope's `header_len` to disagree with `PoolMeta::blob_header_len` (e.g., a live blob_header_len rotation, or a foreign object that survived a `Replaced` verdict rejection) would silently misread payload offsets on the ranged path — the envelope decoder derives `header_len` from '\n' but `locate()` skips the envelope entirely.
  - Recommendation (defense-in-depth, not required today): assert `header.header_len == meta.blob_header_len` where a full envelope read already happens (adopt, GC observe), OR let `locate()` optionally verify via a 1-byte over-read of the pad terminator on first read of a blob.

---

## bc1-offset-overflow

- **NEW-bc1-1** — `Low` — `decodeEnvelopeHeader` discards `object_size` but the payload extent still depends on `object_size >= h.header_len`, which is **not checked here**.
  - Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasBlobEnvelopeFormat.cpp:162` (parameter `uint64_t /*object_size*/`) + `CasBlobEnvelopeFormat.h:88-95` (comment: "payload length is derived downstream as `object_size - header_len`").
  - Trigger: a corrupt/truncated object whose real `object_size < h.header_len` yields a size_t-underflow when a caller computes `object_size - header_len` for the payload length. The envelope decoder no longer sees `object_size` (it's `/*object_size*/`-commented out), so the invariant is enforced only at each *caller* site — a documentation invariant, not a local one. Cheap fix: pass `object_size` through and assert `object_size >= h.header_len` inside `decodeEnvelopeHeader` before returning, so the invariant is guaranteed at the single decode point instead of being scattered.
  - Severity rationale: fail-loud in practice (any downstream ranged read will fail against the real S3 size), but the invariant lives in a comment rather than a check — a mild regression in "local guard" hygiene compared to the old `header_len + logical_size == object_size` explicit assertion.

- **NEW-bc1-2** — `Info` — `getBlobViewPlan`'s `StoredObject(..., location.offset + location.length)` and `readBlobPayload`'s identical expression are duplicated; the second is not covered by the plan's would-be validation if BC1-4 is ever tightened.
  - Anchor: `.../ContentAddressedMetadataStorage.cpp:1915` and `:1930`.
  - Trigger: two independent sites compute `offset + length` for the object read-until size; adding a size check in `getBlobViewPlan` alone would still leave `readBlobPayload` computing the same unchecked sum on any direct call path (currently there's only one live caller of `readBlobPayload`, but it's public on the class).
  - Notes: purely a hygiene/DRY note — factor `location.readEnd()` on `BlobLocation` with a single overflow-guarded add.

---

## bc2-writebuffer-spill

- **NEW-BC2-7 (Low, integrity/inline overflow — `SCOPE_EXIT`-only cleanup covers throw but not
  a survivor if `stageBlobPartFile` succeeds and a **later** transaction step then throws)**.
  Anchor: `ContentAddressedTransaction.cpp:952–972`. The inline-overflow branch writes an
  ad-hoc `WriteBufferFromFile tmp(temp_path)` in a local scope, then calls
  `stageBlobPartFile(route, ref, bytes.size(), temp_path, StagingBackend::Local)`, then flips
  the `staged` sentinel to `true` inside the `SCOPE_EXIT` clause. The `SCOPE_EXIT` only removes
  the file when `!staged`. Once `stageBlobPartFile` has recorded the temp path into
  `PartStaging::pending_blobs`, the file's later lifetime is `cleanupPendingTempFiles`. That is
  correct on the happy path AND on the abort path (both branches of
  `cleanupPendingTempFiles` unlink for `StagingBackend::Local`). But note the file has **no
  fsync** either (`WriteBufferFromFile tmp(...); ... tmp.finalize()` — implied). If the same
  BC2-2 page-cache-loss hazard hits the inline-overflow blob (rare — the trigger is a >
  `INLINE_CAP` "inline-candidate" file, so typically small kilobyte-scale), the same silent
  key-vs-bytes divergence applies. Severity: low, but the site was not called out in the
  original audit (which focused on `CaContentWriteBuffer`).

- **NEW-BC2-8 (Low, integrity/S3-staging — envelope header pre-write is not covered by the
  streaming-size sanity check).** Anchor:
  `ContentAddressedTransaction.cpp:1793–1794` and `Pool/CasPartWriteTxn.cpp:594–602`. In S3
  staging mode the buffer emits `envelope_header` directly to the sink (bypassing `hashing`)
  BEFORE the payload starts. If the caller-supplied `WriteBufferFromFileBase` sink accepts the
  header but silently short-writes it (a specific S3 client bug), the staging object holds a
  truncated header + full payload; `promoteStaged` still copies the object verbatim, and
  decode-time header validation fails **at read time**, not at write time. The Local-mode
  upload has the analogous belt-and-suspenders check
  (`written == source.size`, `CasPartWriteTxn.cpp:600`) but that check applies only to the
  payload portion; the header pre-write in the S3-staging constructor has no equivalent guard.
  This is closer to defense-in-depth than a genuine bug — no reasonable
  `WriteBufferFromFileBase` short-writes silently — but it is a code-shape difference from the
  Local path and could paper over an S3-side integration bug.

- **NEW-BC2-9 (Info — inline-overflow bounded but still holds full bytes in memory before
  spill).** Anchor: `ContentAddressedTransaction.cpp:920–971`. Same shape as BC2-6 in the
  original audit, retained in current code. Included here because the actual line numbers /
  code shape changed (a `SCOPE_EXIT`-guarded temp-file spill) and the safety net is still
  post-hoc (the buffer materializes the entire candidate in `std::string accumulated` first,
  then re-emits via a fresh `WriteBufferFromFile` in `writeFile`). A caller misrouting a large
  file to the inline path still pays the full in-memory cost before the streaming spill.

---

## bc4-protobuf-decode

- **NEW-bc4-protobuf-decode-1 (Info)** — `Backend/CasBackend.h:219` has a stale doc comment referring to
  the deleted `RunFileReader`. Harmless, but a rename to "record-stream reader" would keep the docstring
  aligned with the current `SourceEdgeRunReader` / `CasRecordStreamFormat` naming.
- **NEW-bc4-protobuf-decode-2 (Info)** — `ShardCoverage::classification` is decoded as an unvalidated
  `uint8_t` (`Formats/CasFoldSealFormat.cpp:189`). No consumer branches on it today (see CAS-077 above),
  so this is *cosmetic*, but the persisted byte is documented at `CasFoldSealFormat.h:32–36` as having
  four defined values (0/1/2/4); a `switch`-based decoder that rejects unknown values would enforce the
  documented invariant and would be forward-safe if a future consumer starts branching. Severity: Info.

---

## bc7-blocking-io-locks

- **NEW-BC7-1 (Med)** — Asymmetric fix: replicated write paths use the `renameParts()` off-lock publish, but plain-MergeTree paths (`MergeTreeSink.cpp:379`, `MutatePlainMergeTreeTask.cpp:134`, `MergePlainMergeTreeTask.cpp:160`) still publish under `DataPartsLock`. Plain MergeTree over CAS therefore keeps the full BC7-1 stall behavior. The blocking `FIXME` at `MergeTreeSink.cpp:369-378` states the covered-part-vs-merge-selection race prevents flipping `rename_in_transaction` to `true` without a deeper redesign. Anchor: `MergeTreeSink.cpp:369-380`.
- **NEW-BC7-2 (Low)** — Belt-and-suspenders duplication: after `renameParts()` (`MergeTreeData.cpp:8986-8988`) runs the publish loop, the identical `commitTransaction()` loop inside `commit()` (`MergeTreeData.cpp:9008-9010`) is guarded only by `hasActiveTransaction()`. If a future refactor adds a code path that populates `precommitted_parts` **without** going through `preparePartForCommit`'s `rename_in_transaction=true` branch (i.e. the transaction is still active at `commit()` time) that publish silently regresses back under `DataPartsLock`. The comment at `:8967-8971` names the loop "a safety net" — that safety net IS the on-lock publish, and there is no assertion preventing it. Anchor: `MergeTreeData.cpp:9008-9010`.

---

## codeonly-line

- **NEW-codeonly-line-1** (Low / hardening) — Non-cryptographic checksum still trusted on run objects, now under `CityHash128`-of-object-body — `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasRecordStreamFormat.cpp:210-219` (`sourceEdgeRunChecksum`). The change from CRC32C to chained CityHash128 does not close the "forgeable, pool-participant can plant a valid run" class (`CityHash128` is not cryptographic either); combined with `CAS-004` (no intra-pool authz) the trust boundary is unchanged. This is really an amplifier of an existing high-severity finding, but it is worth calling out that the code comment "Use the same chained CityHash128 and default block size as the reader" doubles the audit's `BUILD-1` / `CAS-037` concern (a `DBMS_DEFAULT_HASHING_BLOCK_SIZE` change now silently forks *two* independent hash chains, not one).
- **NEW-codeonly-line-2** (Info / hardening) — Envelope pad-zone now enforces "must be ASCII space up to '\n'" — `CasBlobEnvelopeFormat.cpp:230-248`. Reads any non-space byte as `CORRUPTED_DATA`. Verified-correct and load-bearing. This is a real *improvement* over the old envelope (which allowed arbitrary TLV in the pad zone with a writer-controlled critical flag), and closes the smuggling side of the old `ENV-3` finding. Recorded so it can be added to the OK list.
- **NEW-codeonly-line-3** (Low / info) — `PartWriteTxn::adoptEvidence` records the sender-supplied `entry.blob_size` in `deps[entry.ref]` and then verifies **only that a blob exists** in `promote` — the mismatch with `CAS-025`'s new `payload_digest` verification is subtle: `payload_digest` verifies the manifest's *canonical encoding* (including `blob_size`), so if the sender's manifest passes decode, its `blob_size` fields are pinned to what the sender computed — but the receiver still adopts them without cross-checking against the pool's canonical blob envelope. Same net gap as MW-1; called out because `CAS-025`'s fix does NOT close this. See MW-1 (`CAS-031`) above.
- **NEW-codeonly-line-4** (Info) — `checkNamespace` is now *also* called on operator-supplied `server_root_id`-derived subpaths via a wide surface (`refsNamespacePrefix`, `manifestNamespacePrefix`, `namespaceFileKey`, `namespaceFilesPrefix`) — so the missing `.`/`..` guard (LAY-1) is unchanged in scope, but the number of code sites depending on it silently accepting benign namespaces (via `escapeForFileName`) has grown. No new hazard, but the "unenforced external invariant" the audit called out is now load-bearing across more call sites; fixing LAY-1 has correspondingly larger safety return.

---

---

## datatype-agnosticism

- **NEW-datatype-agnosticism-1** — informational, agnosticism-preserving:
  The original audit's Layer 1 quote used the fields `UInt128 blob_hash{}`. In current code the
  hash + algorithm are packed into a single `BlobRef ref` (`src/.../Formats/CasPartManifestFormat.h:54`),
  and `blobKey` renders the algo as its own key segment (`CasLayout.cpp:36`). This is a
  wire-format refinement (multi-algorithm-per-pool support), **not** a data-type coupling: the
  algorithm axis is over hash functions (city128, sha256, …), not column types. Agnosticism is
  preserved.

- **NEW-datatype-agnosticism-2** — informational:
  The original audit's edge-case table noted that mutable per-part files
  (`uuid.txt`/`txn_version.txt`/`metadata_version.txt`) were "kept out of the content manifest
  (stored per-ref) — independent of column types." Current code has **removed** that special case.
  `src/.../ContentAddressedTransaction.cpp:844-850`:
  > "The former mutable-per-part-file branch (uuid.txt/metadata_version.txt/txn_version.txt
  > staging directly into a separate mutable payload) is DELETED here — these three names fall
  > through to the ordinary content path below like any other tree file. There is no filename left
  > to special-case: `kMutablePerPartFiles`/`isMutablePerPartFile` predicate itself is gone too …"
  Impact on agnosticism: **strengthens it** — one fewer name-based branch. All part files now flow
  through the same content path regardless of whether they carry column data or per-part
  bookkeeping.

- **NEW-datatype-agnosticism-3** — informational, worth naming so future auditors don't mistake
  it for type coupling:
  The **only** place CAS inspects a file's name to alter behavior is
  `Cas::partFileMustStayBlob` (`src/.../ContentAddressedTransaction.cpp:65-73`, declared in
  `ContentAddressedTransaction.h:243`):
  ```
  bool partFileMustStayBlob(std::string_view file_name)
  {
      if (file_name == "primary.idx")
          return true;
      for (std::string_view suffix : {".bin", ".mrk", ".mrk2", ".mrk3", ".cmrk", ".cmrk2", ".cmrk3"})
          if (hasSuffix(file_name, suffix))
              return true;
      return false;
  }
  ```
  This is a **structural** MergeTree-file-shape predicate ("is this a column-data or marks file?"
  → must not be inlined, must go to a content blob so ranged reads keep column-read selectivity),
  applied uniformly to **every** column type. It does not branch on Int vs String vs JSON vs
  Variant vs Dynamic vs QBit vs Geo: every serialization emits `<escaped_name>.bin` + marks, and
  the predicate treats them identically. Documented explicitly at
  `ContentAddressedTransaction.h:239-242`:
  > "Part files that must NOT be inlined into the tree: per-column data (`.bin`) and marks
  > (`.mrk*`/`.cmrk*`) … Everything else (the small eager metadata files) is an inline candidate."
  Not a type dependency — call it out here only to preempt future reviewers finding a suffix list
  and reading it as one.

---

## jepsen-anomaly

- **NEW-jepsen-1** — *Post-write fence-loss surfaces as `Unresolved`, never
  `Committed`; but the durable object may exist and be visible to other mounts.*
  Severity: **Med (observability / operability).**
  Anchor: `Backend/CasRequestControl.cpp:361-365, 421-425, 487-489, 515-517,
  568-570, 596-598`.
  Trigger: a paused / superseded writer whose PUT lands after `fence_ok` starts
  returning false — the local return is `CasWriteOutcome::Unresolved` +
  `ProfileEvents::CasConditionalWriteFenceLostPostWrite` bump, but the OBJECT is
  durable on S3 and visible to any future reader that shares the key (all mounts
  of this pool). This is silently indistinguishable from CAS-002's zombie-write
  outcome on the storage plane. There is no compensating "unlink-what-you-just-put"
  step; the fence-lost writer just discards the outcome. Callers see Unresolved
  and typically retry against the fresh incarnation; the fresh incarnation then
  observes the zombie's byte-identical body via content-token dedup (no harm) OR a
  DIFFERENT body (silent divergence). *Recommended*: on FenceLostPostWrite, log the
  key and body-hash for post-incident audit; consider a best-effort DELETE against
  the exact token that would be a no-op if the object is unwritten.

- **NEW-jepsen-2** — *`fenceGeneration` admission covers the durable-effect blob
  finalize path only for `ContentAddressedTransaction::writeFile`; the ref-append
  lane relies on `fence_ok_fn` (boolean) rather than a captured generation token.*
  Severity: **Low (soft-vs-hard fence).**
  Anchor: `Pool/CasPool.h:328-337` (`fenceGeneration()` / `checkFenceOrThrow`) —
  documented as used by "the durable-effect site outside `CasPlainObjects`, i.e.
  the S3-native staging-buffer finalize"; `CasRefLedger.cpp:145-165` uses only
  `fence_ok_fn` boolean.
  Trigger: a rapid trip-latch → arm cycle (self-remount) between the pre-check
  and the S3 response would flip `fence_ok_fn` back to true, so the post-check
  would incorrectly succeed under the wrong incarnation. `fenceGeneration()`
  discriminates incarnations; using it on the ref append lane would tighten the
  post-check invariant from "fence is OK now" to "fence is OK *at the same
  generation we admitted under*".

- **NEW-jepsen-3** — *X1/R1 reader pin gap surface is unchanged; the refactor added
  no reader-side coupling to GC's ack floor.*
  Severity: **Med-High** (already CAS-001; called out as a NEW meta-finding because
  during the refactor the write side gained an ack-floor / build-watermark mechanism
  which is not extended to readers).
  Anchor: `Pool/CasPool.h:289-306` (per-server watermark surface documented as
  "writable-Pool build watermark", not query lifetime). Reader path
  `ContentAddressedMetadataStorage.cpp:1886-1933` never touches
  `renewWatermarkOnce` / `minActive`.
  Trigger: any deferred blob GET on a shared/cross-node read path (e.g.
  RESTORE from a snapshot, distributed SELECT, `FETCH` copy) is exposed to a
  concurrent GC delete round. The infrastructure exists (ack floor, exact-token
  delete gates); extending it with a "reader min-manifest-ref pin" folded into
  the union used by `graduateForDelete` is a clean fix but was not made.

---

## read-protocol

- **NEW-read-1 (Med, liveness)** — `readManifestShared` HEAD-GET race window
  amplifies dangle. Anchor `Pool/CasManifestReader.cpp:65-90`: the HEAD at
  `l.65` and the GET at `l.87` are separate backend round-trips. A GC that
  deletes the manifest object between them surfaces as
  `"manifest at {} vanished between head and get — INV-NO-DANGLE"` (`l.89-90`,
  `FILE_DOESNT_EXIST`). Fail-loud, so this is a **liveness** issue, not a
  correctness one — but it is a same-manifest instance of the CAS-001 class
  applied to *manifests* (not just blobs), previously not called out for the
  manifest object itself.
- **NEW-read-2 (Low, coverage)** — Retained-view age policy uses wall-clock
  `now_ms_fn()` (`PartFolderAccess.cpp:203`) subtracted from
  `cached->validatedAtMs()`. On backward wall-clock movement (NTP step) the
  freshness gate can either extend indefinitely (past > now) or refuse every
  cached view. Same J3 clock-skew class as CAS-030 but on a purely
  read-serving cache; no correctness impact (a stale view has to re-prove
  against the fresh resolve), only a perf oscillation.
- **NEW-read-3 (Info)** — `CachedPartFolderAccess::buildView` single-flight
  drops leader exceptions onto every follower (`l.301: promise.set_exception`).
  This means one HEAD failure fans out to N `FILE_DOESNT_EXIST` errors for N
  coalesced readers. Correct semantically (they were asking the same
  question) but distinguishes coalesced from independent readers in error
  budgets / retry storms.

---

## security

- **NEW-security-1** — *`BlobHashAlgo` default is `CityHash128`.* Severity: **Med** (documentation
  + default-hardening). Anchor:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobDigest.h:207-214`
  (`BlobRef { BlobHashAlgo algo = BlobHashAlgo::CityHash128; ... }`);
  `parseBlobHashAlgo` (`CasBlobDigest.cpp:33-45`) allows `cityhash128 | xxh3-128 | sha256` but
  does not privilege `sha256`. Trigger: a pool created without an explicit `blob_hash = sha256`
  disk-config value inherits the non-crypto default. In a multi-trust-domain pool, this reverts
  CAS-003 to its original posture. Recommendation: when the pool spans trust domains, the
  disk-config parser should require an explicit `blob_hash` choice, warn on `cityhash128`, and
  document `sha256` as the recommended default; alternatively, flip the default to `xxh3-128` at
  minimum (which is at least not the audit's known-collidable target) and to `sha256` for shared
  pools.

- **NEW-security-2** — *`Xxh3128BlobHashingWriteBuffer::finalizeImpl` is not overridden;
  `getHashHex` calls `next()` but skips `finalize()`, and the class also lacks a `cancelImpl`.*
  Severity: **Low** (correctness / clean-shutdown). Anchor:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobHashingWriteBuffer.cpp:96-134`.
  Compare to `CityHash128BlobHashingWriteBuffer` (`:78-87`) which overrides both `finalizeImpl`
  and `cancelImpl` and forwards them to the nested `HashingWriteBuffer`. The XXH3 buffer relies on
  `BufferWithOwnMemory<IBlobHashingWriteBuffer>`'s inherited finalize path (which forwards to
  `sink` implicitly), but the sink is not finalized here explicitly on cancel — a mid-upload
  exception on the XXH3 path can leave the underlying sink dangling with data. Not a
  security-critical finding on its own but flagged because the write-buffer trio is a security
  chokepoint. Recommendation: mirror the `CityHash128BlobHashingWriteBuffer` finalize/cancel
  overrides across all three subclasses.

- **NEW-security-3** — *`_pool_meta` / `_manifests` / `_files` reserved-segment gate does not
  include the newer reserved prefixes in the `roots/` and `blobs/` trees.* Severity: **Low**
  (defense in depth). Anchor:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasLayout.cpp:274-279`
  rejects `_files` and `_manifests` in a namespace, but the `roots/`, `blobs/`, `cas/refs/`,
  `cas/manifests/`, `gc/` and `gc/server-roots/` trees now also carry reserved subtrees
  (e.g. `blobs/<algo>` — see `CasBlobDigest.h:45-47`, and `cas/refs/<ns>/…_log|_snap` — see
  `Formats/README.md:22-24`). `checkNamespace` only rejects two literal segment names.
  Trigger: an admin-controlled namespace that happens to be named `refs` or `manifests` collides
  with the control-plane prefix inside its own `roots/<ns>/…` layout when the layout code paths
  concatenate (it doesn't today, because the split is at the prefix level, but the gate is not
  future-proof against a re-layout). Recommendation: enumerate the reserved namespace segments
  from a single registry in `Formats/README.md` and drive `checkNamespace` from it.

- **NEW-security-4** — *`mountpointObjectKey` and `checkNamespace` accept single-character
  segments `.` and `..`.* (Sub-finding of CAS-074, called out separately for the mountpoint path.)
  Severity: **Low**. Anchor: `CasLayout.h:229-235`. Trigger: caller passes a key such as
  `srv1/../gc/state` — the current key builder yields `<prefix>/roots/srv1/../gc/state`. On an
  object store this is a distinct literal key (safe); on `LocalObjectStorage`
  (`src/Disks/DiskObjectStorage/ObjectStorages/Local/LocalObjectStorage.cpp` exists as a real
  backend option and is exercised by tests) or on any future path-normalizing wrapper this
  traverses into the control plane. Recommendation: add the same `..` / `.` per-segment scan that
  `namespaceFileKey` (`CasLayout.h:182-184`) already does. Trivial patch.

---

## test-coverage-fuzzing

- **NEW-TCF-1 (Med)** — no GCS-backed integration test despite
  `utils/ca-soak/docker-compose-gcs.yml` being present. All `tests/integration/test_cas*`
  and `test_content_addressed_*` suites are MinIO/S3-only. GCS
  precondition semantics (`x-goog-if-generation-match: 0`) live entirely in
  the ca-soak surface, without an integration-tests-level assertion.
  Anchor: absence across `tests/integration/test_c*a*s*/test.py`.
- **NEW-TCF-2 (Low)** — `ca-soak/scenarios/` is model/checker-oriented
  (see `cards`, `framework`) but has no explicit **MOVE / RESTORE /
  quorum** cards even though it has the multi-replica infra
  (`docker-compose-10replicas.yml`) that would make them cheap. The
  scenarios listed (`test_aborted_retry`, `test_chaos_schedule`,
  `test_mount_fence_retry`, `test_stale_edge_verdict`, etc.) target
  fence/retry surfaces, not lifecycle/replication.
- **NEW-TCF-3 (Info)** — `gtest_cas_ref_decode_bounds.cpp` exists and is a
  natural seed corpus for a `cas_ref_decode_fuzzer`: converting its
  hand-crafted malformed inputs into a libFuzzer corpus is the
  lowest-friction path to shipping the first CAS fuzz target. Same
  observation for `gtest_cas_envelope.cpp` and the format-battery
  (`cas_format_test_battery.h`, `gtest_cas_format_battery.cpp`).

---

## tier2

**NEW-tier2-1 (Low, cache/observability) — page memory cache key prefix disks-scopes CAS blob dedup.**
- Anchor: `src/Disks/DiskObjectStorage/DiskObjectStorage.cpp:893-902`.
  ```
  auto cache_path_prefix = fmt::format("{}:{}:", /*disk*/ name,
                                       magic_enum::enum_name(storage->getType()));
  ```
  The **memory page cache** key is prefixed by the disk `name`, so two CAS disks that share the same
  underlying pool and thus resolve to the **same blob key** do **not** share page-cache entries — the
  cross-file/cache dedup benefit from CACHE-1 applies only to the filesystem-cache stage (keyed on
  remote path). Minor observability/perf note; the filesystem cache dedup benefit (CACHE-1) is intact.
- Severity: Low (perf only; correctness unaffected).

**NEW-tier2-2 (Low, system-tables gap) — no CAS view of pool-level counters despite `CasFsck` numbers.**
- Anchor: `src/Disks/.../ContentAddressed/Tools/CasFsck.h:112-125` — `physical_bytes`,
  `referenced_logical_bytes`, `distinct_blobs`, `total_blob_refs`, `dedupRatio()` are all computed by
  fsck but there is no matching `StorageSystem*` entry in `src/Storages/System/`. Reinforces SYS-1 and
  makes the recommendation actionable: the numbers exist, they are simply not surfaced.
- Severity: Low (documentation/observability); would meaningfully improve operator sizing.

**NEW-tier2-3 (Low, TTL/tiering) — no move-path hook to short-circuit CAS→CAS same-pool moves.**
- Anchor: `src/Disks/.../ContentAddressed/ContentAddressedTransaction.cpp:1119-1128` (`createHardLink`
  gate requires two well-formed part-file paths in the same CAS metadata storage). Grep of
  `MetadataStorages/ContentAddressed/**` for `crossDisk|relinkAcross|cross_pool` returns no matches;
  the CAS-CAS same-pool fast path noted in the audit recommendations is still absent.
- Severity: Low (perf only; correctness is retained by the generic byte-copy path).

---

## tier3

- **NEW-tier3-1** (Low, feature-gap-with-safety-note) — `moveFile` on committed non-part files
  throws `LOGICAL_ERROR` when the source is not staged in this transaction. Anchor:
  `ContentAddressedTransaction.cpp:1488` — `"ContentAddressed: moveFile source not staged: {}"`.
  Trigger: any code path that reaches `moveFile` on a committed part-file rename (e.g. a future
  MergeTree change that reintroduces the `txn_version.txt` `.tmp` + `replaceFile` rename dance) —
  the branch comment (lines 1483-1487) explicitly documents it as "no live caller … retained only
  as a fail-loud guard". Correctness-safe (fails loudly), but the guard is coupled to a MergeTree
  invariant that CAS does not enforce; a future MergeTree refactor could regress silently until
  hit by MOVE/rename-heavy workloads.

- **NEW-tier3-2** (Low, robustness) — cross-namespace `moveDirectory` (RENAME TABLE) is
  documented as **best-effort, non-atomic, idempotent-on-retry** but has **no in-call
  compensation**. Anchor: `ContentAddressedTransaction.cpp:1215-1248`. Trigger: server crash
  mid-loop during a `RENAME TABLE` that spans a CAS pool ⇒ table is "SPLIT across namespaces"
  until the same RENAME is manually re-driven. Overlaps with MOVE PARTITION when the target is
  a cross-engine move that maps to a namespace move. In-code note admits: *"there is no in-call
  compensation; true atomicity would need a durable move-journal (deliberately out of scope)."*
  Same failure mode as the DUR1 partial-commit class, at RENAME-TABLE granularity — not called
  out in the original Tier3/Tier2 sections.

- **NEW-tier3-3** (Info) — Same-pool same-disk `moveDirectory` for part-dirs is a pure metadata
  `republishRef` (`ContentAddressedTransaction.cpp:1370`), i.e. genuinely O(1) copy-by-reference.
  Original audit did not enumerate this explicitly as a positive property (only noted it in
  passing for FREEZE); it is worth calling out that same-disk `MOVE PARTITION TO TABLE` is
  already relink-free on CAS today. This bounds the gap in TIER-1 (CAS-041) precisely to the
  **cross-disk** case.

---

## tier4

- **NEW-tier4-1 (Low, test-coverage)** — FETCH-to-detached relink correctness has code but
  no dedicated integration test. `ALTER TABLE ... FETCH PARTITION ... FROM ...` on CAS
  (which routes through `to_detached=true`) needs an integration test asserting that the
  received part lands as a relinked `detached/<name>` ref, not as a byte re-upload.
  Anchor for fix: `src/Storages/MergeTree/DataPartsExchange.cpp:697-704, 944` +
  `.../ContentAddressedExchange.h:50, 206-208`. Coverage gap: no test in
  `tests/integration/test_cas_*` currently pins B66b.

- **NEW-tier4-2 (Low, test-coverage)** — RENAME TABLE / cross-engine table move on CAS is
  best-effort non-atomic (documented at `ContentAddressedTransaction.cpp:1212-1248`), and
  the "SPLIT across namespaces" recovery path is idempotent by construction, but there is
  no integration test that injects a fault between the `republishRef` loop and
  `dropNamespace` and asserts idempotent re-drive. Given how many downstream properties
  hinge on this window (EXCHANGE TABLES composes two such halves), a dedicated fault-injection
  test would catch a future refactor that accidentally loses idempotency.

- **NEW-tier4-3 (Low, observability)** — A `CasBlobAdoptTrusted` ProfileEvent
  (`src/Common/ProfileEvents.cpp:900`) partially closes the original OBS-3 gap (relink
  hit-rate is now measurable at the "adoption" level), but there is still no counter
  distinguishing a **relink fetch** from a **byte fetch** in the replication log
  (`system.replicated_fetches` bytes-transferred remains the only signal). Not a regression;
  narrows OBS-3 from "no visibility" to "no per-fetch flag."

---

---

## upgrade-compat

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

---

## write-protocol

- **NEW-write-1** — `CaContentWriteBuffer::finalizeImpl` sets `temp_ownership_transferred = true` (line 1845) even after `on_finalized` throws in the tail of that lambda, because the flag is set *after* the callback. On S3-staging mode a callback throw (e.g. from `stageBlobPartFile` when the route parse throws under the `writeFile` closure) would leave `temp_ownership_transferred = false`; `~CaContentWriteBuffer()` then calls `cancel()` → `cancelImpl` (line 1849) — and for `is_s3_staging=true` the destructor deliberately *does not* delete the remote staging object (comment at line 1855–1858). So a fresh mount's staging-key becomes an orphan sweep target rather than being reclaimed on the failing txn, even though `cleanupPendingTempFiles` was never given the key. Severity `Low`, `LEAK / OBSERV`, anchor `ContentAddressedTransaction.cpp:1842–1846` combined with `165–207`. Reachable only if `on_finalized` itself throws after the sink is durable — narrow, but noted.

- **NEW-write-2** — `CaContentWriteBuffer::finalizeImpl` reports the payload size via `count()` (line 1822), which is the byte count of what THIS buffer forwarded to `hashing`. In S3-staging mode the envelope header is written directly to `sink` (line 1794) *bypassing* `hashing` and this outer buffer. Correct by design, but the reported `size` returned via `on_finalized(hash_hex, size, temp_path)` is the **payload-only** size — which `stageBlobPartFile` then persists as `entry.blob_size`. Downstream `tryReadFileInFlight` for S3 staging then builds a `ReadBufferFromFileView` windowed to `[header_len, header_len+size)` (line 617–622), which requires `header_len` to come from `poolMeta().blob_header_len` and not from a decoded envelope. If a mid-stream mount rotates `blob_header_len` (currently a pool-wide constant, `CasPoolMeta` guarded), the in-flight read of a pending blob would read from the wrong offset. Not currently exploitable (pool-meta `blob_header_len` is create-time constant per CAS-066), but a mixed-version writer scenario (`CAS-024`, `PoolMeta` drift) chains here. Severity `Low`, `CORRECTNESS / COMPAT`, anchor `ContentAddressedTransaction.cpp:617–622`. Flag for future defence: window on the decoded envelope's own `header_len`, not `PoolMeta`.

- **NEW-write-3** — `ContentAddressedTransaction::moveDirectory`'s RENAME-TABLE branch (`ContentAddressedTransaction.cpp:1231–1249`) does `for (const auto & [ref, _] : store->listRefs(from_ns))` and calls `republishRef(...)` per ref, then `putNamespaceFile` per verbatim file, then `dropNamespace(from_ns)`. There is no bounded budget on this loop and no chunking: a table with millions of parts stalls the entire user query for the whole loop, holding the disk transaction open (the containing `ContentAddressedTransaction` is not concurrent-safe). Comment at 1215–1223 openly notes the re-drivability but does not budget the loop. Severity `Low` (`LIVENESS / PERF`), anchor `ContentAddressedTransaction.cpp:1233–1238`. Chain with CAS-006 (S3 latency under DataPartsLock) and CAS-057 (LIST cost) for a full outage shape on RENAME TABLE of a very large table.

---

