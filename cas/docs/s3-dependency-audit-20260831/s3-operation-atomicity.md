# Atomicity of S3 operations CAS uses

**Tree:** `antalya-26.6` @ `6e10e116421`  
Companion to [cas-s3-dependencies.md](cas-s3-dependencies.md). List pagination is covered separately in [listobjectsv2-atomicity.md](listobjectsv2-atomicity.md).

**Definition used here:** an operation is **atomic** if observers never see a partial body and a failed attempt leaves the previous incarnation (or absence) unchanged. **Multi-request sequences** can still be atomic at the S3 object if they have a single commit point (e.g. `CompleteMultipartUpload`). Sequences of distinct keys, or HEAD-then-mutate on one key, are **not** one atomic S3 operation.

---

## Summary

| S3 operation | Single HTTP? | Object-level atomic? | CAS uses conditions? | Residual non-atomicity |
|--------------|--------------|----------------------|----------------------|------------------------|
| `PutObject` (conditional) | Yes | Yes, **if** store enforces If-Match / If-None-Match | Yes (control plane) | Transparent retries forbidden (SingleAttempt) |
| `PutObject` (unconditional) | Yes | Yes (replace) | Blobs / staging | Lost-ACK retry may write twice (accepted for blobs) |
| `CreateMPU` / `UploadPart` / `CompleteMPU` | **No** (3+) | Destination appears only at **Complete** | Never on GCS conditionals; blobs may MPU | Incomplete MPU not visible as the key; parts leak until Abort |
| `AbortMultipartUpload` | Yes | Yes (cancels in-flight upload) | n/a | Best-effort; leak if abort fails |
| `DeleteObject` + `If-Match` | Yes | Yes, **if** store enforces If-Match | Yes (GC) | Versioning → delete marker (not reclaim) |
| `DeleteObject` unconditional | Yes | Yes for current version | Staging only | Same versioning caveat |
| `DeleteObjects` (batch) | One HTTP, many keys | **Not** all-or-nothing across keys | **Not used** by CAS GC | — |
| `HeadObject` | Yes | One observation | n/a | Observation is immediately stale |
| `GetObject` / Range | Yes | One incarnation's bytes for that request | n/a | **HEAD-then-GET** is two requests (see below) |
| `CopyObject` (small) | Yes | Typically yes | **No** (post-#2159) | Unconditional overwrite of dest |
| `CopyObject` via MPU-copy | **No** | Dest visible after Complete | No | Same as MPU |
| `GetBucketVersioning` | Yes | Read of bucket config | GCS mount only | S3 dialect never calls it |
| `ListObjectsV2` | One page yes | Page ≠ prefix snapshot | n/a | See list report |

---

## 1. Conditional `PutObject` (`putIfAbsent` / `putOverwrite` / `casPut`)

**Commit point:** one HTTP PUT. Success → new incarnation + token from response ETag (or GCS generation). 412 / lost If-Match → `PreconditionFailed` / `Conflict`; object unchanged.

**CAS hardening:**

```779:795:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp
WriteSettings ObjectStorageBackend::conditionalWriteSettings() const
{
    WriteSettings ws;
    ws.object_storage_request_mode = ObjectStorageRequestMode::NativeConditional;
    if (native_token_type == TokenType::Generation)
        ws.s3_force_single_part_upload = true;
    ...
    ws.s3_max_unexpected_write_error_retries_override = 1;
    ws.object_storage_retry_profile = ObjectStorageRetryProfile::SingleAttempt;
```

Why this matters for atomicity:

- A **retried** conditional PUT after an unknown result can commit twice or commit after the lease expired. SingleAttempt + `CasRequestController` (resolve-before-reissue) is the protocol.
- **GCS CompleteMPU ignores preconditions.** Forcing single-PUT keeps the condition on the same request that commits the bytes. Control objects are small; blobs are **not** sent on this path.

**If the store ignores If-Match / If-None-Match:** the operation is still “atomic overwrite” in the S3 sense (one new body), but it is **not** CAS. Probe refuses the mount.

**Side effect:** 412 is a normal outcome, not an error. Treating 412 as success would tear the control plane.

---

## 2. Unconditional blob `PutObject` / MPU (`publishBlob` Streaming)

**Commit point:**

- Single-part: `PutObject` finalize
- Multipart: `CompleteMultipartUpload` — parts are invisible as `destination_key` until then
- Size mismatch or exception → `cancel()` → `AbortMultipartUpload`; “nothing published” (`CasObjectStorageBackend.cpp:923–932`)

**Not atomic with the preceding HEAD.** `ensureBlobPresent` HEADs, then may publish:

```327:331:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp
    constexpr int max_publication_attempts = 8;
    for (int attempt = 0; attempt < max_publication_attempts; ++attempt)
    {
        ...
        const HeadResult head = store->backend().head(key);
```

Two writers can both see absence and both PUT. **Accepted:** content-addressed key + fresh `incarnation_tag`. The last Complete wins; refs still name the hash.

**Side effects:**

- Lost ACK after Complete + retry → second unconditional PUT (new envelope). Safe for readers of the hash; exact-token GC of the *previous* envelope no longer matches (by design).
- Incomplete MPU left behind if Abort fails → bucket fill, not wrong reads.

---

## 3. `CopyObject` (S3 staging verbatim publish)

**Commit point:** native `CopyObject`, or MPU-copy Complete for large objects (`copyS3File.cpp`).

**Unconditional** after #2159. `object_storage_copy_mode = NativeOnly` — if native copy is disabled, publish throws; **no** read/write fallback (`CasObjectStorageBackend.cpp:944–956`). That fallback would have been a non-atomic client-side copy onto a live key.

**Not atomic with** the staging `writeObject` (different key) or the HEAD of the destination.

**Side effect:** destination can be overwritten. Safe only because blob keys are content hashes and envelopes rotate. Must never be used for control-plane keys.

---

## 4. `DeleteObject` + `If-Match` (`deleteExact`)

**Commit point:** one HTTP DELETE with `If-Match` / GCS generation (`S3ObjectStorage.cpp:508–516`).

Outcomes: Removed / TokenMismatch (412, object intact) / NotFound.

**Atomicity:** one incarnation is removed or not. There is no “half-deleted” body.

**Not atomic with LIST+HEAD.** GC lists, then deletes by token. If the object was republished, token mismatches and the new incarnation stays. That is the safety property.

**Versioning:** a successful DELETE on a versioned bucket can create a **delete marker** while old bytes remain. Probe step 8 rejects `created_delete_marker` on the probe key. GCS `checkPoolPreconditions` refuses Enabled **and** unverifiable versioning. **S3 ETag dialect still does not call `GetBucketVersioning`.**

---

## 5. Unconditional `DeleteObject` (staging)

Used only under `staging/<server_root_id>/` and txn abort of those keys.

**Atomic per key.** The **sweep** (list all, then delete each) is a non-atomic sequence. Fail-open on LIST error (`sweepOwnMountStaging`). Staging keys are not referenced by manifests after commit cleanup; leftover keys are leaked bytes, not live data.

---

## 6. `HeadObject`

**Atomic as an observation** of one incarnation at one time. Immediately stale.

CAS uses HEAD as:

- blob publish/adopt gate (mandatory)
- token source for later CAS/delete
- ForceFresh / sentinel

**Side effect of a stale HEAD:** extra publish (waste) or adopt of a body that GC is about to condemn (then meta/CAS retries). Not silent data loss if `deleteExact` stays token-exact.

---

## 7. `GetObject` and HEAD-then-GET

A single GetObject/Range is one observation.

**`Backend::get` / `getStream` on Native S3 always HEAD then GET** (`CasObjectStorageBackend.cpp:565–601`):

- Delete between HEAD and GET → `nullopt` (absent)
- Replacement between HEAD and GET → **older token + newer bytes**
- Comment argues this is fail-closed: the token is used as a later If-Match; a mixed pair cannot commit a CAS/delete of bytes that never coexisted with that token
- Mutable objects must use materialized `get`, not `getStream` (bytes can change under an open stream)

**Blob payload reads** on the MergeTree path go through the disk `readObject` stack (not always this HEAD-then-GET seam). Write-once blob bodies are byte-identical across republish except the envelope; readers that hash/decode the payload still see the same logical bytes.

**Side effect:** Glacier / archive → `InvalidObjectState` surfaces as a query exception; no `RestoreObject`.

---

## 8. `GetBucketVersioning`

One read of bucket configuration. Atomic as a read. Used only for **GCS Generation** mounts. Inconclusive or Enabled → refuse mount (fail-closed). S3-compatible ETag mounts skip it.

---

## 9. Sequences that look like one operation (they are not)

| Sequence | Requests | Atomic as a unit? | CAS handling |
|----------|----------|-------------------|--------------|
| HEAD blob + publishBlob | 2+ | No | Accepted race; fresh envelope |
| HEAD + GET (`Backend::get`) | 2 | No | Token/bytes mixed pair fail-closed on later CAS |
| LIST + GET + deleteExact | 3+ | No | Token mismatch leaves object |
| Staging PUT + CopyObject + delete staging | 3+ | No | Dest overwrite accepted; staging delete best-effort |
| `casPut` after local fence check | 2+ (fence is local) | No | TOCTOU on fence vs PUT (control-plane residual; token is the S3 atomic) |
| Multipart upload | 2+N+1 | Dest atomic at Complete | Abort on size mismatch |

---

## Confirmed findings

### ATOM-1 — Control-plane atomicity is entirely store-enforced conditional PUT/DELETE

- **Impact:** If RustFS/AWS-compatible store stops honoring If-Match on PUT or DELETE, CAS will silently lose fencing and GC safety. Probe covers this at **mount**, not continuously.
- **Anchor:** `CasProbe.h:10–22`, `conditionalWriteSettings`, `removeObjectIfTokenMatches`
- **Why defect-class:** not a missing CAS API; it is a **runtime dependency**. MinIO OSS is already rejected.
- **Fix direction:** keep probe; optional periodic re-probe; soak Delete If-Match under GC load.
- **Regression:** capability probe + integration `test_cas_s3`.

### ATOM-2 — S3 versioning still unchecked at mount (ETag dialect)

- **Impact:** Versioned AWS/RustFS bucket: `deleteExact` can “succeed” via delete markers; GC stops reclaiming; versions accumulate.
- **Anchor:** `CasObjectStorageBackend.cpp:56–59` (`if (mode != Native \|\| native_token_type != Generation) return;`)
- **Trigger:** enable bucket versioning on an S3 CAS pool
- **Why defect:** probe step 8 only sees the probe key; a bucket that starts versioning later, or whose delete-marker behavior differs for other prefixes, is unguarded. Same class as CAS-011.
- **Fix direction:** run `GetBucketVersioning` for ETag dialect too; fail closed on Enabled / unverifiable (as GCS already does).
- **Regression:** mount against a versioned RustFS/MinIO-compatible bucket must refuse.

### ATOM-3 — HEAD-then-GET is non-atomic (handled, but observable)

- **Impact:** extra retries; not silent commit of a mixed pair **if** callers only use the token as If-Match. A caller that trusted token as “these exact bytes” without re-validating would be wrong — decode caches depend on token⇒content (`CasBackend.h:226–236`).
- **Anchor:** `CasObjectStorageBackend.cpp:573–588`
- **Why noted:** documented invariant, not a new bug. Residual: weak/recycled ETags would poison caches; probe does not test token non-reuse.

### Not confirmed as defects

- Unconditional blob overwrite after racing HEAD — **by design** in #2159.
- Unconditional staging `CopyObject` overwrite — **by design**; NativeOnly fail-closed.
- Multi-page LIST — **by design** as hint; see list report.

---

## Fault-category matrix (logical)

| Category | Status | Outcome |
|----------|--------|---------|
| Conditional PUT ignored | Executed (static + probe contract) | Mount fail-closed if probe runs; silent clobber if skipped |
| Conditional DELETE ignored | Executed | Same; MinIO known fail |
| MPU Complete drops conditions | Executed | GCS: forced single-PUT; S3 blobs: conditions not used |
| Lost ACK on unconditional blob PUT | Executed | Double publish accepted |
| HEAD/GET split | Executed | Fail-closed for CAS/delete |
| Versioning / delete markers | Executed | GCS gated; S3 not gated at preconditions |
| Object Lock / lifecycle / Glacier | Executed (absence of checks) | Unguarded; AD-6 still applies |
| List pagination holes | Executed | See list report |
| Batch DeleteObjects for GC | Not Applicable | Not used |
| `copyObjectConditional` | Not Applicable | Removed in #2159 |
