# CAS → S3 dependency map (post-#2159)

Static analysis of ClickHouse Content-Addressed Storage on `antalya-26.6` @ `6e10e116421` (includes [PR #2159](https://github.com/Altinity/ClickHouse/pull/2159)).

**Code**

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` — especially `Backend/CasBackend.h`, `Backend/CasObjectStorageBackend.*`, `Backend/CasProbe.*`, `Pool/CasPartWriteTxn.cpp`
- S3 seam: `src/Disks/DiskObjectStorage/ObjectStorages/S3/S3ObjectStorage.cpp` (`removeObjectIfTokenMatches`, `copyObject`, `iterate` / `listObjects`)

**Related reports in this folder:** [ListObjectsV2 atomicity](listobjectsv2-atomicity.md), [other-op atomicity](s3-operation-atomicity.md).

**Backend note:** Writable CAS still requires a store that enforces **conditional create / overwrite / delete** for the control plane. CI uses **RustFS** (`1.0.0-rc.3` in ClickHouse compose), not MinIO OSS (MinIO ignores `If-Match` on DELETE and fails `runCapabilityProbe`).

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
       │       └─ Cas::Backend (ObjectStorageBackend) via CasRequestController when mutable
       │            ├─ putIfAbsent / putOverwrite / casPut
       │            │     └─ PutObject + If-None-Match:* | If-Match   (SingleAttempt, NativeConditional)
       │            ├─ tryGetObjectMetadata → HeadObject
       │            ├─ readObject (+ range) → GetObject
       │            ├─ deleteExact → DeleteObject + If-Match
       │            └─ list → iterate → ListObjectsV2
       └─ [mount staging sweep / txn abort]
             └─ listObjects + removeObjectIfExists  (unconditional Delete)
```

Mount-time gates (writable pool):

- Mandatory: `runCapabilityProbe` (fail-closed). Steps: store preconditions, SingleAttempt support, conditional create/overwrite, `casPut` chain, exact-token delete, list-after-write/delete, no delete marker.
- S3 staging: requires `supportsCopyMode(NativeOnly)`. There is **no** conditional-copy probe anymore.

---

## Two protocols

### Blob bodies (post-#2159)

`PartWriteTxn::ensureBlobPresent`:

1. Durable precommit first.
2. **HEAD** the content-hash key (every attempt; no presence cache).
3. If present, Clean (or missing meta), size matches → **adopt** (no PUT); optionally backfill freshness meta.
4. If absent or Condemned → publish the writer's own payload **unconditionally**:
   - first attempt + S3 staging object → `CopyObject` (verbatim)
   - else → streaming `PutObject`/MPU with a **fresh envelope** (`incarnation_tag`)
5. Reconcile blob `.meta` to `Clean` via **conditional** `putMetaIfAbsent` / `casMeta`.

Concurrent writers may both publish the same key after racing HEAD misses. That is accepted: the key fixes the logical payload, durable refs name the **content hash** (not an ETag), and a fresh envelope protects the winner from exact-token deletes already queued for a condemned predecessor.

`publishBlob` does **not** return an incarnation token.

### Control plane (unchanged class)

Manifests, ref-log chunks/seals/snapshots, mount leases, pool meta, ref catalog, GC state/heartbeat, checkpoints, blob freshness metadata, exact-token GC delete.

Uses token-conditional `putIfAbsent` / `putOverwrite` / `casPut` / `deleteExact`. Conditional HTTP is **SingleAttempt**; CAS owns retries via `CasRequestController` (mount-fence gated). GCS forces **single-part** PUT because CompleteMPU ignores preconditions.

---

## S3 APIs CAS depends on

| S3 API | CAS surface | Callers | Precondition | Intended effect | Side effect if broken | Sev | Evidence |
|--------|-------------|---------|--------------|-----------------|----------------------|-----|----------|
| `HeadObject` | `Backend::head`; mandatory blob HEAD | Blob adopt/publish, GC, fsck, lease, ForceFresh, probe | none (ETag/generation → Token) | Presence + size + incarnation token | False presence → skip publish / wrong adopt; false absence → extra unconditional overwrite | **high** | static; `CasPartWriteTxn.cpp:331` |
| `PutObject` (`If-None-Match: *`) | `Backend::putIfAbsent` / `casPut(nullopt)` | Manifests, ref chunks, GC artifacts, mount claim, probe, blob `.meta` create | `If-None-Match: *` + SingleAttempt + NativeConditional | Write-once create of control objects; 412 = lost race | Silent clobber of live manifests / leases / GC state | **critical** | static + probe steps 1–2, 5a |
| `PutObject` (`If-Match: <etag>`) | `Backend::putOverwrite` / `casPut(expected)` | Lease renew, catalog, pool meta, GC state, ckpt, blob `.meta` CAS | `If-Match` + SingleAttempt + NativeConditional | Token-CAS update | Torn fencing / dual writers on control plane | **critical** | static + probe steps 3–4, 5b–5d |
| `PutObject` / MPU (unconditional) | `Backend::publishBlob(Streaming)`; S3 staging `writeObject` | Blob bodies; staging temp keys | none | Publish / stage without conditions; MPU allowed | Lost ACK + retry may overwrite; incomplete MPU leaks until Abort | medium | static; by design for blobs |
| `CreateMultipartUpload` / `UploadPart` / `CompleteMPU` | `WriteBufferFromS3`; `copyS3File` for large copies | Large blobs; large verbatim copies | Conditions must **not** be used on MPU (GCS ignores them) | Large-object upload; destination visible only after Complete | Incomplete MPU storage leak; if a store applied conditions only on Complete and then dropped them, control-plane writes would overwrite — CAS avoids this by forcing single-PUT on GCS conditionals | **high** (control) / medium (blobs) | static |
| `AbortMultipartUpload` | `WriteBufferFromS3::cancel` | Size-mismatch / exception on `publishBlob` or staging | none | Do not make a partial object visible | Orphaned MPU parts if abort unsupported; no abort-lifecycle gate at mount | medium | static |
| `DeleteObject` (`If-Match`) | `Backend::deleteExact` → `removeObjectIfTokenMatches` | GC reclaim, orphan sweep, janitor, decommission, probe | `If-Match` + NativeConditional | Exact-token reclaim; 412 leaves object; no delete marker | Wrong-token delete succeeds → deletes live incarnation after republish | **critical** | static + probe steps 6–8 |
| `DeleteObject` (unconditional) | `removeObjectIfExists` | Staging sweep; txn abort of staging keys | none | Best-effort temp cleanup | Must not be used for GC reclaim | low | static |
| `DeleteObjects` (batch) | Available on `S3ObjectStorage`; **CAS GC does not use** | — | n/a | — | Accidental use would drop token-exact reclaim | info | static negative |
| `GetObject` (+ Range) | `Backend::get` / `getStream` / disk `readObject` | Control-plane reads (HEAD then GET); blob payload reads; GC streams | none | One incarnation's bytes | HEAD/GET split can pair older token with newer bytes — CAS treats that as retry, not commit; Glacier → `InvalidObjectState` unhandled | **high** | static; rustfs GetObject errors |
| `ListObjectsV2` | `Backend::list` → `iterate`; `listObjects` for staging sweep | GC, fsck, janitor, decommission, emptiness, probe, mounts table | paginated; cursor = last key | Prefix enumeration | Multi-page list is **not** a snapshot — see [listobjectsv2-atomicity.md](listobjectsv2-atomicity.md) | **high** | static; rustfs `list_path` errors |
| `CopyObject` (unconditional) | `publishBlob(VerbatimStaged)` | S3-native staging promote | none; `NativeOnly` (no read/write fallback) | Server-side copy staging → content-hash key | Can overwrite destination (accepted for content-addressed blobs). If native copy disabled, mount/publish fails closed | medium | static; `CasObjectStorageBackend.cpp:944–956` |
| `GetBucketVersioning` | `checkPoolPreconditions` | Writable GCS (Generation dialect) only | n/a | Refuse versioned **or unverifiable** GCS buckets | **S3 ETag dialect still skips this check** — versioning on AWS-compatible S3 is unguarded at mount (probe step 8 still rejects delete markers on the probe key) | **high** | `CasObjectStorageBackend.cpp:56–86` |

---

## Not used (important negatives)

| API | Implication |
|-----|-------------|
| `copyObjectConditional` / `If-None-Match` on Copy | **Removed in #2159.** Staging copy is unconditional. |
| `CreateBucket` / `DeleteBucket` | Bucket/prefix must pre-exist |
| Object tagging | Not part of the CAS protocol (`cas_owner` is a control object) |
| SSE / checksum trailers | No CAS-specific handling |
| `RestoreObject` / Glacier | Not handled |
| `GetObjectLockConfiguration` | Not checked |
| Lifecycle / StorageClass APIs | Not inspected |
| Batch conditional delete | Does not exist / not used |

---

## Semantic assumptions

1. Control-plane conditional create/overwrite/delete are **enforced** (412 leaves the object unchanged).
2. Token uniquely identifies the current incarnation's bytes (S3 ETag content-derived; GCS generation monotonic). Probe does **not** test token non-reuse across different contents.
3. Successful delete does not create a versioning delete marker (probe step 8).
4. Conditional HTTP is single-attempt; CAS owns retries (`CasRequestController`).
5. List is a **hint**, not a snapshot. Callers that need newest-ness or emptiness for safety add probes, HEAD checks, or fail closed on holes.
6. Native `CopyObject` is required for S3 staging; no silent client-side fallback.
7. Strong read-after-write for HEAD/GET of a key just written (AWS S3 yes; RustFS treated as required by the probe's list-after-write step).
8. Blob overwrite after a racing HEAD miss is safe because refs name hashes and envelopes rotate.
9. Never revive a condemned blob by reading the condemned body (`INV-NO-RETURN`); the writer republishes **its own** source.

---

## Bucket-side effects (still relevant)

| Finding | Bucket feature | Side effect on CAS | Sev | Status on this tree |
|---------|----------------|--------------------|-----|---------------------|
| CAS-011 | Versioning on **S3** (ETag dialect) | `deleteExact` may create delete markers; GC stops reclaiming | high | still present — GCS now fail-closed on Enabled **and** unverifiable; S3 still unchecked at `checkPoolPreconditions` |
| CAS-016 | Lifecycle expiration | Deletes live blobs; INV-NO-LOSS broken silently | high | still present |
| CAS-017 | Object Lock / WORM | Conditional overwrite of roots/gc/refs denied | high | still present |
| CAS-051 | Cross-region replication | Shadow bucket grows; failover ETags incoherent | medium | still present |
| CAS-052 | Glacier / archive | GetObject → `InvalidObjectState` | medium | still present |
| CAS-087 | Eventual consistency | Stale HEAD/GET/LIST on non-AWS stores | medium | probe checks list-after-write of one key only |
| CAS-114 | Default StorageClass | Control plane + blobs inherit bucket default | low | info |

**Improvement vs July 2026 AD-6:** GCS versioning probe is no longer fail-open on `std::nullopt`. It throws `NOT_IMPLEMENTED` and refuses the mount (`CasObjectStorageBackend.cpp:62–77`).

---

## Test / config anchors

**In-tree**

- `Backend/CasProbe.h` — mandatory capability battery (no copy probe)
- `tests/integration/test_cas_s3`, `test_cas_gc_s3`, `test_cas_gcs`, `test_cas_mount_renewal_retry`
- `tests/integration/compose/docker_compose_rustfs.yml` — `rustfs/rustfs:1.0.0-rc.3`
- `tests/config/config.d/cas_s3_storage_policy_for_merge_tree_by_default.xml`

**clickhouse-regression/cas**

- `cas_env/rustfs-service.yml` — still `rustfs/rustfs:1.0.0-beta.12` (drift vs ClickHouse CI)
- `tests/sanity.py`
- `docs/cas-audit-rerun-20260730/reports/ad6-s3-lifecycle-cross-region.md` (pre-#2159; GCS fail-open note is stale)
