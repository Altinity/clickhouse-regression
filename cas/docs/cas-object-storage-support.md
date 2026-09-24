# Object stores and CAS

A writable CAS disk mounts only if the store passes `runCapabilityProbe` (`CasProbe.cpp`). A failed check throws `NOT_IMPLEMENTED` and the disk stays unmounted.

Status here means that probe, not general S3 compatibility.

| Status | Meaning |
|---|---|
| supported | The ClickHouse client speaks this store's conditional API, and the behavior matches the probe. |
| not supported | A required call is missing or ignored. The probe will refuse the mount. |
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

`not known` includes stores whose docs describe the headers; a live probe has not confirmed them.

| Store | Status | Notes |
|---|---|---|
| AWS S3 | supported | General-purpose bucket, versioning off. `PutObject` accepts `If-Match` and `If-None-Match: *`. `DeleteObject` accepts `If-Match` and returns 412 on a mismatch. |
| Google Cloud Storage | supported | S3-compatible endpoint plus `http_client=gcs_hmac`. Versioning off. Generation tokens, not AWS ETags. |
| RustFS | supported | The CAS suite mounts this as its local store. A CAS disk comes up, so the probe is passing. |
| Akamai Object Storage (Linode) | not known | S3-compatible and Ceph-based. Public docs do not say whether `PutObject` or `DeleteObject` honor `If-Match` / `If-None-Match`. |
| Ceph RGW | not known | Conditional `PUT` (`If-Match` / `If-None-Match`) and `DeleteObject` `If-Match` returning 412 are documented, including IBM Storage Ceph. |
| Hetzner Object Storage | not known | Ceph underneath. Hetzner's supported-actions page does not mention these conditional headers. |
| IDrive e2 | not known | Documents `PutObject` `If-Match` and `If-None-Match: *`, with 412 and no write on failure. `DeleteObject` `If-Match` is not in that page. |
| MinIO AIStor | not known | MinIO's enterprise server, not NVIDIA AIStore. The AIStor compatibility page lists `If-Match` on `PutObject` and `DeleteObject`, and `If-None-Match` on `PutObject`. |
| OVHcloud Object Storage | not known | Docs list `If-Match` and `If-None-Match: *` on `PutObject`, and `If-Match` on `DeleteObject`, with 412 when the ETag does not match. Versioning still inserts a delete marker; a CAS bucket must stay unversioned. |
| Scaleway Object Storage | not known | Documents `PutObject` `If-Match` and `If-None-Match`. `DeleteObject` is documented without `If-Match`. |
| SeaweedFS | not known | Documented `If-None-Match: *` on `PUT` and `If-Match` on `PUT` and `DELETE`, with 412 on failure. |
| Tigris | not known | Docs describe `If-Match` (412 on `PUT` and `DELETE`) and `If-None-Match: *` for create-if-absent. |
| Wasabi | not known | Markets bit-compatibility with S3. The published API variation guide does not mention `If-Match` or `If-None-Match` on `PutObject` or `DeleteObject`. |
| Azure Blob | not supported | `AzureObjectStorage` does not implement conditional delete. The probe fails before any Azure precondition is tested. |
| Backblaze B2 | not supported | Conditional `PUT` returns `501 Not Implemented`. `DeleteObject` without a version id inserts a delete marker. |
| Cloudflare R2 | not supported | `PutObject` `If-Match` and `If-None-Match` are supported. `DeleteObject` `If-Match` is not in the S3 compatibility table. R2's `x-amz-if-match-last-modified-time` is not what ClickHouse sends. A stale `If-Match` delete would remove the object. |
| DigitalOcean Spaces | not supported | The Spaces API reference lists supported headers per call. `PutObject` omits `If-Match` and `If-None-Match`. `DeleteObject` lists only `x-amz-expected-bucket-owner`. |
| Garage | not supported | `DeleteObject` inserts a delete marker and does not read `If-Match`. The probe refuses delete markers. |
| MinIO (community) | not supported | Conditional `PUT` exists. `DeleteObject` ignores `If-Match` and deletes anyway. The project closed that as not a community feature ([minio/minio#21677](https://github.com/minio/minio/issues/21677)) and pointed it at AIStor. |
