# encryption -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `DiskEncrypted.{h,cpp}`, `DiskEncryptedTransaction.{h,cpp}`, `IDisk.h` defaults, `ContentAddressedTransaction.cpp` (autocommit blob refusal, S3 staging header, `publishBlob` consumer), `Backend/CasObjectStorageBackend.cpp:952` (`copyObject` for verbatim staged publication), `IO/S3/copyS3File.cpp` / `Client.cpp` (SSE-C extra_headers; no copy-source SSE-C), CAS subtree for any `encrypt` token (none), `Formats/CasPartManifestFormat.h`, `Formats/CasBlobEnvelopeFormat.h`, `system.cas_log` column set.
- Explicitly out of scope: inventing a supported encryption mode; hash-algorithm policy (sibling ad1/security).

Filimonov 2026-08-21 on CAS-059/CAS-060: CAS × `DiskEncrypted` is **out of scope and fails loud**. Confirm that, and note the missing fail-fast gate if still missing.

## Findings
### encryption-1 -- DiskEncrypted over CAS is still accepted at config and fails only at the first blob-class write; no fail-fast gate (Low)
- Anchor: `DiskEncrypted.cpp` `getDiskAndPathFromConfig` takes any delegate with no `isContentAddressed` check; `DiskEncrypted.h` does not override `isContentAddressed()` or `supportsAtomicFileWrites()` (`IDisk.h:477-480` defaults false); `use_fake_transaction` defaults true (`DiskEncrypted.cpp:329`); refusal at `ContentAddressedTransaction.cpp:791-796` (`NOT_IMPLEMENTED` autocommit of a `partFileMustStayBlob` file). The shipped `notYet` text still names "a layer that bypasses the content-addressed write path" (`:90-94`).
- Trigger: `<type>encrypted</type><disk>cas_disk</disk>` in a storage policy, then `INSERT` (or any `.bin`/`.mrk*` write).
- Evidence: startup access-check writes a non-part path and succeeds. MergeTree CAS hooks (`freeze` owned txn, relink, parent-transaction projections) stay off because the wrapper reports not content-addressed, while writes still land in `ContentAddressedTransaction`. The first column data file throws. Inline-eligible files can autocommit one manifest per file. This matches the settled "out of scope / fails loud" position. The only remaining product gap is a config-time or mount-time refusal.
- Notes: CAS-059. Not High: fail-closed, no silent corruption.

### encryption-2 -- SSE-C plus `staging_backend=s3` still uses server-side copy without copy-source customer-key headers (Medium)
- Anchor: `ContentAddressedTransaction.cpp:898-927` (S3 staging streams `[envelope][payload]`); `CasPartWriteTxn.cpp:397-402` (first publication after HEAD-absent uses `VerbatimStagedBlobPublication`); `CasObjectStorageBackend.cpp:938-956` (`object_storage->copyObject` / `ObjectStorageCopyMode::NativeOnly`). Repo-wide: no `x-amz-copy-source-server-side-encryption-customer-*` / `CopySourceSSECustomer` in `src`.
- Trigger: `server_side_encryption_customer_key_base64` on the CAS S3 endpoint and `cas_staging_backend=s3`, then INSERT a blob-class file.
- Evidence: SSE-C headers ride client `extra_headers` for ordinary GET/PUT. `copyObject` does not add copy-source SSE-C material. S3 rejects the copy; `publishBlob` propagates. Default `staging_backend` is local, so this is opt-in. Subsequent publications stream and are covered by extra_headers. `promoteStaged` / `copyObjectConditional` are gone; the residual is this one verbatim-copy arm.
- Notes: CAS-090 residual, narrowed to the new publish path.

## By-design / info / non-actionable
- **CAS × DiskEncrypted is out of scope.** Random IV per rewrite (`DiskEncryptedTransaction.cpp`) would destroy dedup if the wrapper ever succeeded. The combination is not wired (`isContentAddressed` not forwarded) and fails loud. Do not treat "dedup goes to zero" as a defect of a supported mode (CAS-060).
- SSE-S3 / SSE-KMS remain transparent: CAS hashes plaintext; ETag tokens still work.
- CAS metadata (manifests, ref log, catalog, envelope `intended_ref`, `system.cas_log`) is not client-encrypted. Under SSE the content address is a plaintext digest. Accepted for an out-of-scope encryption story; not a silent integrity break.
- Re-key of an immutable shared blob pool is impossible. Old keys must stay. No CAS re-key tool. Fail-loud if a fingerprint is removed.
- No CAS-native blob/manifest encryption exists (zero `encrypt` tokens under the CAS root).

## Closed-since-2026-08-12
- `promoteStaged` / `copyObjectConditional` symbols are gone (blob publish rewrite `940b1685bf9`). SSE-C breakage is no longer "every promote"; it is only the first-publication verbatim copy of an S3 staging object.

## Coverage
- Reviewed: wrapper capability surface and fail site; fake-transaction default; SSE-S3/KMS/SSE-C header wiring; new `publishBlob` copy arm; metadata plaintext inventory; re-key/immutability.
- N-A: CAS-native encryption (does not exist).
- Deferred: Azure/GCS SSE specifics beyond the shared object-storage interface.
