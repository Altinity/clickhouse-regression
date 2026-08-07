# CAS → S3 dependency map

Static analysis of ClickHouse Content-Addressed Storage (CAS) object-storage usage, cross-checked with RustFS stress logs and `clickhouse-regression/cas` AD-6 audit notes.

**Sources**

- Code: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` (esp. `Backend/CasObjectStorageBackend.*`, `Backend/CasProbe.*`)
- S3 seam: `src/Disks/DiskObjectStorage/ObjectStorages/S3/S3ObjectStorage.cpp` (`removeObjectIfTokenMatches`, `copyObjectConditional`)
- RustFS: `/root/altinity-clickhouse/ClickHouse/ci/tmp/rustfs.log` (ERROR-only, stress CAS-S3 2026-07-30)
- Regression: `clickhouse-regression/cas/` (`cas_env/rustfs-service.yml`, `tests/sanity.py`, `docs/cas-audit-rerun-20260730/reports/ad6-s3-lifecycle-cross-region.md`)

**Backend note:** CAS requires a store that enforces conditional create/overwrite/delete. CI uses **RustFS**, not MinIO OSS (MinIO ignores `If-Match` on DELETE and fails the mount capability probe).

---

## Call graph

```
MergeTree / IDisk
  └─ ContentAddressedMetadataStorage / ContentAddressedTransaction
       ├─ [staging_backend=s3] IObjectStorage::writeObject
       │       └─ PutObject / CreateMPU / UploadPart / CompleteMPU (unconditional)
       ├─ [S3 staging promote] Backend::promoteStaged
       │       └─ copyObjectConditional → CopyObject + If-None-Match:*
       ├─ [local staging] scratch file → Backend::putIfAbsentStream
       ├─ PartWriteTxn / RefLedger / ServerRoot / GC / PlainObjects
       │       └─ Cas::Backend (ObjectStorageBackend)
       │            ├─ writeObject + WriteSettings(If-None-Match | If-Match)
       │            │     └─ PutObject | CreateMPU / UploadPart / CompleteMPU
       │            ├─ tryGetObjectMetadata / getObjectMetadata → HeadObject
       │            ├─ readObject (+ seek/range) → GetObject (Range)
       │            ├─ removeObjectIfTokenMatches → DeleteObject + If-Match
       │            ├─ iterate / listObjects → ListObjectsV2
       │            └─ resurrect → writeObject (unconditional Put/MPU)
       └─ [mount staging sweep / txn abort]
             └─ listObjects + removeObjectIfExists (unconditional Delete)
```

Mount-time gates:

- Mandatory: `runCapabilityProbe` (fail-closed)
- Optional: `probeConditionalCopy` (if false → fall back to local staging; does not refuse mount)

---

## S3 APIs CAS depends on

| S3 API | CAS surface | Callers | Precondition | Intended effect | Side effect if broken | Sev | Evidence |
|--------|-------------|---------|--------------|-----------------|----------------------|-----|----------|
| `PutObject` (`If-None-Match: *`) | `Backend::putIfAbsent` / `putIfAbsentStream` | Blob upload, manifests, ref chunks, GC runs/outcomes, probe keys, mount claim | `If-None-Match: *` | Write-once create; 412 = lost race | Silent clobber of live content-addressed objects | **critical** | static + probe step 2 |
| `PutObject` (`If-Match: <etag>`) | `Backend::putOverwrite` / `casPut(expected)` | Mount lease renew/fence, ref catalog, pool meta, GC state/heartbeat, blob `.meta`, plain ns files, ckpt | `If-Match: <token>` | Token-CAS update of mutable control plane | Torn lease/GC/catalog; dual writers | **critical** | static + probe steps 2–3 |
| `PutObject` / MPU (unconditional) | `Backend::resurrect`; S3 staging `writeObject` | Condemned blob revive; `staging_backend=s3` temp objects | none | Re-upload / stage without conditions | Partial MPU left if finalize fails (needs Abort) | medium | static |
| `CreateMultipartUpload` / `UploadPart` / `CompleteMPU` | `WriteBufferFromS3` under `writeObject` | Large conditional creates (AWS dialect); staging/resurrect unconditionally | Conditions must survive CompleteMPU (AWS); GCS forces single-PUT | Large-object upload | GCS-like CompleteMPU dropping preconditions → overwrite; incomplete MPU leaks storage | **high** | static (GCS single-PUT force) |
| `AbortMultipartUpload` | `WriteBufferFromS3::cancel` before finalize | Failed staging / size-mismatch paths | none | Clean incomplete uploads | If abort unsupported → orphaned MPU parts; no abort-lifecycle gate at mount | medium | static; AD-6 |
| `DeleteObject` (`If-Match: <etag>`) | `Backend::deleteExact` → `removeObjectIfTokenMatches` | GC reclaim, orphan manifest sweep, namespace janitor, decommission, txn abort of failed uploads | `If-Match: <etag>` | Exact-token reclaim; 412 leaves object; no delete marker | Wrong-token delete succeeds → deletes wrong incarnation / live data after resurrect | **critical** | static + probe steps 4–6; `S3ObjectStorage.cpp` |
| `DeleteObject` (unconditional) | `removeObjectIfExists` | Mount staging sweep; txn abort of S3 staging keys only | none | Best-effort cleanup of temp keys | Must not be used for GC reclaim (would violate INV-NO-RETURN) | low | static |
| `DeleteObjects` (batch) | Available on `S3ObjectStorage`; **CAS GC does not use** | — | n/a | — | Accidental use would drop token-exact reclaim safety | info | static negative |
| `HeadObject` | `Backend::head` / `tryGetObjectMetadata` | Dedup, GC discover, orphan sweep, fsck, lease, ForceFresh, sentinel probe | none (ETag → Token) | Presence + size + generation/ETag | False presence/absence → wrong dedup or skipped reclaim | **high** | static + ForceFresh |
| `GetObject` (+ Range) | `Backend::get` / `getStream` / `readObject` | Blob payload reads, ref log/snapshot/ckpt, GC fold seals, manifests | none | Stable read of write-once blobs; ranged GC streams | Truncated/corrupt reads → bad GC; Glacier → `InvalidObjectState` unhandled | **high** | static; rustfs GetObject errors |
| `ListObjectsV2` | `Backend::list` / `iterate`; `listObjects` bypass for staging sweep | GC discover/fold, orphan sweep, janitor, fsck, decommission, emptiness checks, `listNamespaces` | pagination via `start_after` / continuation | Prefix enumeration reflecting creates/deletes | Incomplete list → orphans forever or false-empty unsafe reclaim | **high** | static; rustfs `list_path` errors |
| `CopyObject` (`If-None-Match: *`) | `Backend::promoteStaged` → `copyObjectConditional` | S3-native staging promote only (`staging_backend=s3` + `probeConditionalCopy`) | `If-None-Match: *`; `allow_native_copy` required | Server-side promote staging → content-hash key | If ignored → silent overwrite of live blob; fail-closed if native copy disabled | **critical** | static + `gtest_cas_s3_staging`; optional probe |
| `GetBucketVersioning` | `checkPoolPreconditions` (GCS Generation dialect only) | Mount-time for Native+Generation | n/a | Refuse versioned GCS buckets | S3 ETag dialect skips check; inconclusive → fail-open warn (CAS-011) | **high** | static AD-6; `CasObjectStorageBackend.cpp:55-84` |

---

## Not used (important negatives)

| API | Implication |
|-----|-------------|
| `CreateBucket` / `DeleteBucket` | Bucket/prefix must pre-exist |
| `PutObjectTagging` / `GetObjectTagging` | Available on `S3ObjectStorage`; CAS protocol does not use (`cas_owner` is a control object, not `x-amz-meta`) |
| SSE / checksum trailers | No CAS-specific handling; inherits client defaults if configured |
| `RestoreObject` / Glacier | Not handled; `InvalidObjectState` surfaces to query (CAS-052) |
| `GetObjectLockConfiguration` | Not checked; Object Lock breaks mutable control plane (CAS-017) |
| Lifecycle / StorageClass APIs | Not inspected; expiration deletes live blobs (CAS-016); no per-kind class (CAS-114) |

---

## Semantic assumptions

1. Conditional create/overwrite/delete are enforced (412 leaves the object unchanged).
2. ETag (or GCS generation) uniquely identifies the current incarnation.
3. Successful delete does not create a versioning delete marker.
4. Conditional HTTP is single-attempt; CAS owns retries via `CasRequestController`.
5. List eventually reflects mutations; pagination cursor = last key.
6. Native `CopyObject` is required for S3 staging (no silent read/write fallback).
7. Strong read-your-writes for `ForceFresh` / `listNamespaces` (AWS S3 yes; RustFS soak TBD).
8. Never GET a condemned blob to revive it (`INV-NO-RETURN`).

---

## RustFS log observations (stress CAS-S3)

Log: `ClickHouse/ci/tmp/rustfs.log` — **ERROR-level only** (8897 lines), not an access log. Stress job: `Stress test (amd_asan_ubsan, content_addressed s3 storage)` (2026-07-30); result included `No lost s3 keys` = OK.

| Signal | Count | Detail | CAS impact |
|--------|------:|--------|------------|
| Erasure decode failed during GetObject | 1626 | Bucket `test`, keys under `content_addressed_s3/blobs/ch128/…`; sample error `Io(Kind(BrokenPipe))`; hot keys retried 100–225× | Read path surfaces exception; availability risk under RustFS EC/decode flake |
| `list_path worker failed` | 172 | Dominant prefix `content_addressed_s3/cas/refs/` (130×); error `Io error: channel closed` | GC discover / `listNamespaces` / janitor can under-enumerate if not retried |
| HTTP transport failed | 2219 | Companion to decode/write pipeline failures | Retry amplification |

**Prefix classes in ERROR logs (approx.)**

| Prefix class | Count | Subsystem |
|--------------|------:|-----------|
| `blobs/ch128/…` | 3252 | Payload GetObject |
| `cas/refs/…` | 322 | Ref ledger List/Get |
| `roots/…` | 2 | Server root |

**Caveat:** Scanning the `rustfs` binary surfaces Put/Delete/MPU/Tagging/Copy API name strings — that is implementation surface, not proof of CAS traffic. Prefer ERROR object paths + the static call graph. Full verb histograms need access logging or ClickHouse `system.blob_storage_log` / ProfileEvents from a live run.

---

## Bucket-side effects (AD-6, still present)

From `docs/cas-audit-rerun-20260730/reports/ad6-s3-lifecycle-cross-region.md`:

| Finding | Bucket feature | Side effect on CAS | Sev | Status |
|---------|----------------|--------------------|-----|--------|
| CAS-011 | Versioning (S3 unchecked) | `deleteExact` may create delete markers; GC stops reclaiming | high | still present |
| CAS-016 | Lifecycle expiration | Deletes live blobs; INV-NO-LOSS broken silently | high | still present |
| CAS-017 | Object Lock / WORM | `putOverwrite` of roots/gc/refs denied → writes/GC halt | high | still present |
| CAS-051 | Cross-region replication | Shadow bucket grows; failover ETags incoherent for `If-Match` | medium | still present |
| CAS-052 | Glacier / archive tier | GetObject → `InvalidObjectState`; no `RestoreObject` | medium | still present |
| CAS-087 | Eventual consistency | `ForceFresh` may serve stale HEAD/GET on non-AWS stores | medium | RustFS TBD |
| CAS-114 | Default StorageClass | Control plane + blobs inherit bucket default equally | low | info |

---

## Test / config anchors

**In-tree (ClickHouse)**

- `Backend/CasProbe.h` — mandatory capability battery
- `src/Disks/tests/gtest_cas_s3_staging.cpp` — conditional copy contract
- `tests/integration/test_cas_s3`, `tests/integration/test_cas_gc_s3`
- `tests/config/config.d/cas_s3_storage_policy_for_merge_tree_by_default.xml`

**clickhouse-regression/cas**

- `cas_env/rustfs-service.yml` — RustFS `1.0.0-beta.12`
- `tests/sanity.py` — ReplicatedMergeTree on shared CAS pool + `mc find`
- `docs/cas-audit-rerun-20260730/reports/ad6-s3-lifecycle-cross-region.md`
- Jepsen stack under `cas/jepsen/`

---

## Follow-ups

1. Enable RustFS / ClickHouse access logging on a short CAS soak for real verb histograms (Put vs Head vs List vs Delete+If-Match rates).
2. Confirm RustFS enforces Delete `If-Match` under load (probe covers mount; soak should cover GC reclaim races).
3. Triage `list_path` channel-closed + GetObject `BrokenPipe`: store bug vs shutdown teardown vs CAS retry amplification.
4. Document supported bucket contract (no versioning, no lifecycle expire, no object-lock, no archive transition) — still missing per AD-6.
