# Object stores and CAS

A writable CAS disk mounts only if the store passes `runCapabilityProbe` (`CasProbe.cpp`). A failed check throws `NOT_IMPLEMENTED` and the disk stays unmounted.

Status here means that probe, not general S3 compatibility.

| Status | Meaning |
|---|---|
| supported | The ClickHouse client speaks this store's conditional API, and the behavior matches the probe. |
| not supported | A required call is missing or ignored. The probe will refuse the mount. |
| probably not supported | Built on a backend this suite already refused. The store itself has not been probed. |
| not known | Docs describe the headers, or the store is S3-compatible underneath, but the probe has not been confirmed against a live endpoint. |

## What the probe checks

| Call | Pass condition |
|---|---|
| `PutObject` `If-None-Match: *` | Succeeds only when the key is absent. A second create returns 412 and leaves the bytes unchanged. |
| `PutObject` `If-Match: <current etag>` | Succeeds, and the new ETag differs from the old one. |
| `PutObject` `If-Match: <stale etag>` | 412, current bytes unchanged. |
| `DeleteObject` `If-Match: <stale etag>` | 412, and the object is still readable. Stores that ignore `If-Match` on delete fail here. |
| `DeleteObject` `If-Match: <current etag>` | The object is gone, and the response is not a versioning delete marker. |
| `ListObjects` under the probe prefix | The key is visible after the write and absent after the delete. |

Bucket versioning must never have been enabled. Suspending it still mints delete markers, and the probe refuses those.

`DeleteObjects` (batch delete) is optional. Garbage collection falls back to one delete per key.

GCS is a separate dialect. The token is a generation, not an S3 ETag, and conditional writes are a single `PUT` because multipart completion does not enforce the precondition. The disk needs `http_client=gcs_hmac`.

`DeleteObject` `If-Match` is implemented only on `S3ObjectStorage`. `AzureObjectStorage` does not override `removeObjectIfTokenMatches`, so the default throws `NOT_IMPLEMENTED`.

The API map is in [cas-s3-dependencies.md](cas-s3-dependencies.md).

## Stores

`Tried` is yes when the row was checked against a live endpoint or this suite. `not known` means the docs describe the headers, but a live probe has not confirmed them.

| Store | Status | Tried | Notes |
|---|---|---|---|
| AWS S3 | supported | yes | General-purpose bucket, versioning off. `PutObject` accepts `If-Match` and `If-None-Match: *`. `DeleteObject` accepts `If-Match` and returns 412 on a mismatch. |
| Google Cloud Storage | supported | yes | S3-compatible endpoint plus `http_client=gcs_hmac`. Versioning off. Generation tokens, not AWS ETags. |
| RustFS | supported | yes | The CAS suite mounts this as its local store. A CAS disk comes up, so the probe is passing. |
| MinIO AIStor | supported | yes | Single-node `quay.io/minio/aistor/minio:latest` in this suite, region `us-east-1`. MinIO's enterprise server, not NVIDIA AIStore. The CAS suite mounts the disk; sanity, metrics, and alter pass. |
| SeaweedFS | supported | yes | `chrislusf/seaweedfs:latest` (4.48) in this suite, region `us-east-1`, bucket versioning off. Quoted `PutObject` `If-None-Match: *` and `If-Match`, and `DeleteObject` `If-Match`, return 412 on a mismatch and leave the object unchanged. The CAS suite mounts the disk; sanity, metrics, and alter pass. |
| Ceph RGW | not supported | yes | Cannot be used with CAS until [tracker.ceph.com/issues/64439](https://tracker.ceph.com/issues/64439) is fixed in a release. ClickHouse sends a quoted ETag. Reef 18.2.2 (this suite's picoceph image) stores the ETag unquoted and `prepare_atomic_modification` compares the raw `If-Match` header with `strncmp`, so a correct overwrite returns 412 and the probe refuses the mount. The same comparison is in Squid 19.2.3 and Tentacle 20.2.0. Ceph `main` unquotes the header in `check_preconditions`; that change is not in a release. |
| IDrive e2 | not supported | yes | Live probe on `https://s3.eu-central-1.idrivee2.com`, region `eu-central-1`, bucket versioning off. `PutObject` `If-None-Match: *` and `If-Match` behave as required. `DeleteObject` `If-Match` is ignored: a stale ETag still returns 204 and removes the object. The suite refuses the mount with `CasProbe: remove with a stale incarnation was not rejected — backend does not enforce conditional deletes`. |
| Tigris | not supported | yes | Live probe on `https://t3.storage.dev`, region `auto`, bucket versioning off. `PutObject` `If-None-Match: *` and `If-Match` behave as required. `DeleteObject` `If-Match` is ignored: a stale ETag still returns 204 and removes the object. The suite refuses the mount with `CasProbe: remove with a stale incarnation was not rejected — backend does not enforce conditional deletes`. |
| Wasabi | not supported | yes | Live probe on `https://s3.eu-central-2.wasabisys.com` (`WasabiS3/8.1.333`), bucket versioning off. `PutObject` ignores `If-None-Match: *` and `If-Match`: a second create and a stale ETag both return 200 and overwrite the object. `DeleteObject` `If-Match` is ignored: a stale ETag returns 204 and removes the object. The suite refuses the mount with `CasProbe: create on an existing key was not rejected — backend does not enforce conditional create`. |
| MinIO (community) | not supported | yes | Conditional `PUT` exists. `DeleteObject` ignores `If-Match` and deletes anyway. The project closed that as not a community feature ([minio/minio#21677](https://github.com/minio/minio/issues/21677)) and pointed it at AIStor. |
| Akamai Object Storage (Linode) | probably not supported | no | Ceph RGW underneath. Released Ceph fails the probe until [tracker.ceph.com/issues/64439](https://tracker.ceph.com/issues/64439) is in a release, so an Akamai bucket is expected to fail the same way. This endpoint has not been probed. |
| Hetzner Object Storage | probably not supported | no | Ceph RGW underneath. Released Ceph fails the probe until [tracker.ceph.com/issues/64439](https://tracker.ceph.com/issues/64439) is in a release, so a Hetzner bucket is expected to fail the same way. This endpoint has not been probed. |
| OVHcloud Object Storage | not known | no | Requires a paid Public Cloud project. Docs list `If-Match` and `If-None-Match: *` on `PutObject`, and `If-Match` on `DeleteObject`, with 412 when the ETag does not match. Versioning still inserts a delete marker; a CAS bucket must stay unversioned. |
| Scaleway Object Storage | not known | no | The console asks for payment details before a bucket can be created, so this endpoint has not been probed. Docs list `PutObject` `If-Match` and `If-None-Match`. `DeleteObject` is documented without `If-Match`. |
| Azure Blob | not supported | no | `AzureObjectStorage` does not implement conditional delete. The probe fails before any Azure precondition is tested. |
| Backblaze B2 | not supported | no | Conditional `PUT` returns `501 Not Implemented`. `DeleteObject` without a version id inserts a delete marker. |
| Cloudflare R2 | not supported | no | `PutObject` `If-Match` and `If-None-Match` are supported. `DeleteObject` `If-Match` is not in the S3 compatibility table. R2's `x-amz-if-match-last-modified-time` is not what ClickHouse sends. A stale `If-Match` delete would remove the object. |
| DigitalOcean Spaces | not supported | no | The Spaces API reference lists supported headers per call. `PutObject` omits `If-Match` and `If-None-Match`. `DeleteObject` lists only `x-amz-expected-bucket-owner`. |
| Garage | not supported | no | `DeleteObject` inserts a delete marker and does not read `If-Match`. The probe refuses delete markers. |
