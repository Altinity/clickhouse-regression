# ad6-s3-lifecycle-cross-region -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Backend/CasObjectStorageBackend.cpp` (`checkPoolPreconditions`, `checkSkipAccessCheckSupport`, `publishBlob`); `Backend/CasProbe.cpp`; `Pool/CasPool.cpp` (probe vs `skip_access_check`); `Gc/CasGc.cpp:669-672` (delete-marker); `Pool/CasPoolMeta.cpp` (no bucket/endpoint in `_pool_meta`); `docs/en/antalya/cas/bucket-requirements.md`; `IO/WriteBufferFromS3.cpp` (If-None-Match on CompleteMPU — control path only); `IO/S3/Client.cpp` / `GCSConditionalDialect`.
- Explicitly out of scope: emulated-mode token model (ad7); MPU residue as erasure (ad2-4).

## Findings
### ad6-1 -- bucket versioning is queried only on the GCS generation dialect; AWS/S3-compatible mounts rely on the delete-marker probe (Medium)
- Anchor: `Backend/CasObjectStorageBackend.cpp:56-59` (early return unless `Mode::Native && TokenType::Generation`); `Gc/CasGc.cpp:669-672`.
- Trigger: versioned AWS/MinIO/RustFS bucket, or versioning enabled after mount.
- Evidence: `GetBucketVersioning` is skipped for ETag stores. The mount battery still exercises delete-marker behaviour when the probe runs. If the store does not report `created_delete_marker`, GC "successful" deletes archive versions. Post-mount enablement still throws `LOGICAL_ERROR` after the marker exists and wedges subsequent rounds.
- Notes: CAS-029 residual. GCS half is now fail-closed (see Closed).

### ad6-2 -- `skip_access_check` still disables the probe on ETag writable mounts (Medium)
- Anchor: `Pool/CasPool.cpp:459-486`; `CasObjectStorageBackend.cpp:92-103` (GCS-only refusal).
- Trigger: `skip_access_check=1` on AWS/S3-compatible CAS.
- Evidence: versioning delete-marker, conditional create/overwrite/delete, RAW/LAW/LAD are skipped. Single-attempt client check remains. GCS writable + skip now throws. Decommission hard-codes skip (`CasPool.cpp:829`) and does not call `checkSkipAccessCheckSupport`.
- Notes: CAS-030 residual.

### ad6-3 -- lifecycle expiration, Object Lock, and Glacier are not probed; Glacier has no restore path (Medium)
- Anchor: no `GetBucketLifecycleConfiguration` / `GetObjectLockConfiguration` / `RestoreObject` in the CAS or S3 CAS-callers; `docs/en/antalya/cas/bucket-requirements.md` documents versioning and GCS soft-delete, not lifecycle/WORM/Glacier.
- Trigger: expiration rule over the pool prefix; Object Lock / deny-DELETE; transition to Glacier.
- Evidence: expiration looks like `NoSuchKey` (absent). Glacier `InvalidObjectState` is a raw hard read error. Object Lock DELETE rethrows; GC retries forever. Fail-open for detection; Glacier/WORM fail loud. Soft-delete is documented as an operator precondition and is not queried.
- Notes: CAS-012 residual.

### ad6-4 -- CRR / replica-bucket failover is undetectable: `_pool_meta` carries no bucket identity (Medium)
- Anchor: `Pool/CasPoolMeta.cpp` (fields: `pool_id`, `blob_header_len`, `gc_shards`, `min_reader_generation`, `algos_used`).
- Trigger: mount a CRR destination, or DNS-failover the endpoint to a replica bucket.
- Evidence: the replica presents the same `pool_id`. Leases and `gc/state` are replicated objects. Harm requires writing the replica prefix (operator error). Undocumented "prefix belongs to CAS alone".
- Notes: CAS-032.

### ad6-5 -- GCS dialect is selected by `http_client`, not by endpoint (Medium)
- Anchor: `IO/S3/Client.cpp` sets `gcs_conditional_dialect` from `http_client` ∈ {`gcs_hmac`,`gcp_oauth`}; `CasObjectStorageBackend.cpp:48-49` (`conditionalOpsUseGenerationTokens()`).
- Trigger: `endpoint=https://storage.googleapis.com/...` without the GCS client setting.
- Evidence: CAS speaks ETag dialect against GCS, losing generation preconditions, the GCS versioning gate, and generation-token DELETE proof. Config typo; no sniff.
- Notes: protocol-skew overlap with ad7.

## By-design / info / non-actionable
- Blob publication after 940b168 is unconditional `WriteMode::Rewrite` (`publishBlob`, `:904-934`). `If-None-Match` on `CompleteMultipartUpload` is not used for blob bodies. Conditional MPU remains only for large *control* objects (`casPut` / `putIfAbsent`). Docs state this (`bucket-requirements.md:21-23`, `configuration.md:97`).
- GCS versioning query now fails the mount if unverifiable (`CasObjectStorageBackend.cpp:62-77`). Previous fail-open is closed.
- `skip_access_check` is refused on writable GCS (`:97-102`). Docs match (`configuration.md:94`).
- ETags are opaque tokens, not content hashes.
- Non-S3 stores fail closed on SingleAttempt (`:112-127`).

## Closed-since-2026-08-12
- Previous ad6-4 (High) "conditional create validated only for single-PUT, assumed for MPU" / CAS-031: **obsolete for blobs**. `putIfAbsentStream` is gone; `publishBlob` is unconditional. Confirm by grep: those symbols are absent under ContentAddressed.
- GCS versioning fail-open (previous ad6-2 High): now refuse if the query cannot answer.
- GCS `skip_access_check` (part of previous ad6-3): refused on writable generation-token mounts.

## Coverage
- Reviewed: versioning probe vs dialect; skip_access_check; lifecycle/WORM/Glacier; CRR identity; dialect selection; blob vs control MPU preconditions.
- N-A: requester-pays (no header → 403 at probe).
- Deferred: live GCS credentialed gate (docs: not yet run).
