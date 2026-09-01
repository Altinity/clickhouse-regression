# CAS S3 dependency and atomicity audit

**Date:** 2026-08-31  
**ClickHouse tree:** `antalya-26.6` @ `6e10e116421`  
**Includes:** [Altinity/ClickHouse#2159](https://github.com/Altinity/ClickHouse/pull/2159) (`a49d9ed16df`, merged 2026-08-26)  
**Method:** static analysis of `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` plus S3 seam.

This folder is the post-#2159 rewrite of the July 2026 inventory. The previous `cas/docs/cas-s3-dependencies.md` described APIs that **no longer exist** (`putIfAbsentStream`, `promoteStaged`, `resurrect`, `copyObjectConditional`, `probeConditionalCopy`).

## Documents

| File | Contents |
|------|----------|
| [cas-s3-dependencies.md](cas-s3-dependencies.md) | Current S3 APIs CAS depends on, callers, side effects |
| [listobjectsv2-atomicity.md](listobjectsv2-atomicity.md) | Every `ListObjectsV2` / `Backend::list` site; which walks are multi-request |
| [s3-operation-atomicity.md](s3-operation-atomicity.md) | Atomicity of Put / Head / Get / Delete / Copy / MPU |

The same inventory is also published at [`../cas-s3-dependencies.md`](../cas-s3-dependencies.md) so the existing GitHub path stays current.

## What #2159 changed for S3

Blob bodies are published **unconditionally** after a **mandatory HEAD**. Conditional S3 is still required for the control plane (manifests, ref-log, leases, GC state, catalog, blob freshness metadata, exact-token delete).

Removed from the CAS S3 surface:

- `Backend::putIfAbsentStream`
- `Backend::promoteStaged`
- `Backend::resurrect`
- `CasRequestController::conditionalCreateControlled`
- `IObjectStorage::copyObjectConditional`
- `probeConditionalCopy` / `conditional_copy_supported`

Added / newly central:

- `Backend::publishBlob` — streaming `PutObject`/MPU or unconditional native `CopyObject`
- Mandatory `HeadObject` before every blob publish/adopt decision

## Scope limits

- No new runtime soak was executed for this rewrite.
- ClickHouse CI pins `rustfs/rustfs:1.0.0-rc.3`; `clickhouse-regression/cas` still pins `1.0.0-beta.12`.
