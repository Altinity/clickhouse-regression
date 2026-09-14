# CAS → S3 dependency map (post-#2159)

> **Rewritten 2026-08-31** against ClickHouse `antalya-26.6` @ `6e10e116421` (includes [PR #2159](https://github.com/Altinity/ClickHouse/pull/2159)).  
> The July 2026 version of this file listed APIs that were **removed** (`putIfAbsentStream`, `promoteStaged`, `resurrect`, `copyObjectConditional`).  
> Full atomicity reports: [`s3-dependency-audit-20260831/`](s3-dependency-audit-20260831/README.md).

Static analysis of ClickHouse Content-Addressed Storage.

**Code**

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` — `Backend/CasBackend.h`, `Backend/CasObjectStorageBackend.*`, `Backend/CasProbe.*`, `Pool/CasPartWriteTxn.cpp`
- S3 seam: `src/Disks/DiskObjectStorage/ObjectStorages/S3/S3ObjectStorage.cpp`

**Backend note:** Writable CAS requires a store that enforces **conditional create / overwrite / delete** for the control plane. CI uses **RustFS** (`1.0.0-rc.3` in ClickHouse compose), not MinIO OSS.

---

## Call graph

```
MergeTree / IDisk
  └─ ContentAddressedMetadataStorage / ContentAddressedTransaction
       ├─ [staging_backend=s3] IObjectStorage::writeObject
       │       └─ PutObject / CreateMPU / UploadPart / CompleteMPU  (unconditional)
       ├─ [S3 staging promote] Backend::publishBlob(VerbatimStaged)
       │       └─ copyObject (NativeOnly) → CopyObject / MPU-copy   (unconditional)
       ├─ [local staging] scratch → StreamingBlobPublication
       ├─ PartWriteTxn::ensureBlobPresent
       │       ├─ HeadObject (mandatory every attempt)
       │       └─ Backend::publishBlob(Streaming) → PutObject / MPU (unconditional)
       ├─ PartWriteTxn / RefLedger / ServerRoot / GC / PlainObjects / BlobMeta
       │       └─ Cas::Backend
       │            ├─ putIfAbsent / putOverwrite / casPut
       │            │     └─ PutObject + If-None-Match:* | If-Match   (SingleAttempt)
       │            ├─ HeadObject
       │            ├─ GetObject (+ range)
       │            ├─ deleteExact → DeleteObject + If-Match
       │            └─ list → ListObjectsV2
       └─ [mount staging sweep / txn abort]
             └─ listObjects + removeObjectIfExists
```

Mount-time: `runCapabilityProbe` is fail-closed. There is **no** conditional-copy probe after #2159. S3 staging requires native copy.

---

## Two protocols

**Blob bodies:** mandatory `HEAD`, then adopt or **unconditional** `publishBlob` (PUT/MPU or native Copy). Concurrent HEAD-miss PUTs are accepted (content hash + fresh envelope).

**Control plane:** token-conditional `putIfAbsent` / `putOverwrite` / `casPut` / `deleteExact` (manifests, ref-log, leases, GC state, catalog, blob `.meta`, exact-token reclaim). GCS conditionals are forced single-PUT.

---

## S3 APIs CAS depends on

| S3 API | CAS surface | Precondition | Intended effect | Side effect if broken | Sev | Atomic? |
|--------|-------------|--------------|-----------------|----------------------|-----|---------|
| `HeadObject` | `head`; mandatory blob HEAD | none | Presence + size + token | Wrong adopt / extra overwrite | high | One observation |
| `PutObject` (`If-None-Match: *`) | `putIfAbsent` / `casPut(nullopt)` | If-None-Match + SingleAttempt | Write-once control objects | Silent clobber of manifests/leases/GC | **critical** | Yes if store enforces |
| `PutObject` (`If-Match`) | `putOverwrite` / `casPut(token)` | If-Match + SingleAttempt | Token-CAS control plane | Torn fencing / dual writers | **critical** | Yes if store enforces |
| `PutObject` / MPU (unconditional) | `publishBlob(Streaming)`; staging write | none | Blob / staging publish | Lost-ACK double publish (accepted for blobs); MPU leak | medium | Dest visible at PUT/Complete |
| MPU create/part/complete | `WriteBufferFromS3`; large Copy | never on GCS conditionals | Large objects | Complete without conditions would break control plane — CAS avoids via single-PUT | high / medium | Atomic at Complete |
| `AbortMultipartUpload` | `cancel()` | none | Hide failed upload | Orphan parts if abort fails | medium | Yes |
| `DeleteObject` (`If-Match`) | `deleteExact` | If-Match | Exact-token GC | Deletes wrong incarnation | **critical** | Yes if store enforces |
| `DeleteObject` (unconditional) | staging sweep | none | Temp cleanup | Must not be used for GC | low | Per key; sweep is not atomic |
| `DeleteObjects` (batch) | **not used** for GC | n/a | — | Would drop token-exact reclaim | info | N/A |
| `GetObject` (+ Range) | `get` / disk read | none | Read one incarnation | HEAD-then-GET split; Glacier unhandled | high | GET yes; HEAD+GET no |
| `ListObjectsV2` | `Backend::list` / `listObjects` | pagination | Prefix hint | Holey/incomplete list | high | **Page only; not a snapshot** |
| `CopyObject` (unconditional) | `publishBlob(VerbatimStaged)` | NativeOnly | Staging → blob key | Overwrites dest (accepted for hash keys) | medium | Small copy yes; MPU-copy at Complete |
| `GetBucketVersioning` | GCS `checkPoolPreconditions` | n/a | Refuse versioned/unverifiable GCS | **S3 ETag dialect still skips** | high | Read of config |

Removed in #2159: `copyObjectConditional`, `putIfAbsentStream`, `promoteStaged`, `resurrect`, `probeConditionalCopy`.

---

## Not used

`CreateBucket` / `DeleteBucket`, object tagging as protocol, SSE/checksum CAS logic, `RestoreObject`, Object Lock APIs, Lifecycle / StorageClass APIs.

---

## Semantic assumptions

1. Control-plane conditionals are enforced (412 leaves the object unchanged).
2. Token uniquely identifies incarnation bytes (probe does not test token non-reuse).
3. Successful delete does not create a delete marker (probe step 8).
4. Conditional HTTP is single-attempt; CAS owns retries.
5. List is a **hint**, not a snapshot.
6. Native Copy required for S3 staging; no client-side fallback.
7. Blob overwrite after a racing HEAD miss is safe (hash key + new envelope).
8. Never GET a condemned blob to revive it.

---

## ListObjectsV2 (non-atomic usage)

Every production prefix walk that can exceed one S3 page is **two or more** `ListObjectsV2` requests. **No caller treats that as an atomic snapshot.**

- `forEachListedKey` (GC, fsck, decommission, bootstrap, orphan sweep) — multi-page by construction.
- `computeHeartbeatFloor` / `listMounts` / `listNamespaceFiles` — cursor loops.
- `sweepOwnMountStaging` — `listObjects(max_keys=0)` full walk, fail-open.
- Single-page: `prefixHasAnyKey` (limit=1), capability probe, janitor/orphan **one page per tick**.

Safety: rebuild (`newestFoldSealRef`) and bootstrap **fail closed** on a lying/incomplete list. Reclaim is `deleteExact`, not “listed ⇒ delete”. Missed keys **leak**, they must not **lose** live data.

Details: [s3-dependency-audit-20260831/listobjectsv2-atomicity.md](s3-dependency-audit-20260831/listobjectsv2-atomicity.md).

---

## Atomicity of other operations (short)

| Op | Atomic? |
|----|---------|
| Conditional PUT/DELETE | Yes **if** the store honors the condition (one HTTP commit) |
| Unconditional blob PUT/Copy | Object replace is atomic; **not** atomic with the preceding HEAD |
| MPU | Destination atomic at Complete; parts invisible before that |
| HEAD-then-GET | Two requests; mixed pair fail-closed on later If-Match |
| LIST+GET+deleteExact | Not one atomic op; token mismatch saves the new incarnation |

Details: [s3-dependency-audit-20260831/s3-operation-atomicity.md](s3-dependency-audit-20260831/s3-operation-atomicity.md).

**Still unguarded:** S3 (ETag) bucket versioning at `checkPoolPreconditions` (GCS is now fail-closed on Enabled **and** unverifiable). Lifecycle expire, Object Lock, CRR, Glacier — unchanged from AD-6.

---

## Follow-ups

1. Access log / `blob_storage_log` verb histogram on a post-#2159 soak.
2. Soak Delete `If-Match` vs concurrent `publishBlob` (new envelope).
3. Call `GetBucketVersioning` for the S3 ETag dialect (same fail-closed policy as GCS).
4. Align regression RustFS image with ClickHouse rc3.
5. Document the supported bucket contract (no versioning, no expire, no object-lock, no archive).
