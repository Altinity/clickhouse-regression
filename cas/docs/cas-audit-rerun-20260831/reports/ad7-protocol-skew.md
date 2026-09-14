# ad7-protocol-skew -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Pool/CasServerRoot.h` (`validateServerRootId`); `Tools/CasDecommission.cpp` (prefix ownership); `Formats/CasFormat.h` (`G_BUILD=10`); `Pool/CasPoolMeta.cpp` (algo admit + reader floor); `ContentAddressedSettings.cpp` (`cas_` prefix + unprefixed aliases); `ContentAddressedMetadataStorage.cpp:706-732` (mode by `ObjectStorageType::Local`); `Backend/CasObjectStorageBackend.cpp` (GCS versioning / skip); `Pool/CasPool.cpp` (`gc_shards` overwrite, `skip_access_check`); `IMetadataStorage.h` / `DiskSelector.cpp` (reload).
- Explicitly out of scope: format-generation recreate-only policy (upgrade-compat); cross-pool ATTACH (migration).

## Findings
### ad7-1 -- nested `server_root_id` is valid config and decommission is prefix-owned (Medium)
- Anchor: `Pool/CasServerRoot.h:76-105`; `Tools/CasDecommission.cpp:146-151`, `:220-242`; `Formats/CasLayout.h:389-431`.
- Trigger: members `prod` and `prod/2` on one pool. `SYSTEM CAS DROP POOL MEMBER 'prod'`.
- Evidence: `/` is allowed. Catalog selection and physical prefix deletes (`cas/manifests/<srid>/`, `staging/<srid>/`, `roots/<srid>/`, `gc/server-roots/<srid>/`) treat `prod/2` as under `prod`. Identical srid still fail-closes. Nested srid does not.
- Notes: CAS-007. Same root cause as ad2-1.

### ad7-2 -- GCS vs ETag dialect is a per-node config choice, not a pool property (Medium)
- Anchor: `IO/S3/Client.cpp` (`http_client`); `CasObjectStorageBackend.cpp:48-59`; `_pool_meta` has no dialect field.
- Trigger: one member `gcs_hmac`, another default S3 client, same bucket; or GCS endpoint without the GCS client.
- Evidence: token type is process-local (`mintingTypeMatches` rejects cross-dialect tokens on that process). A mis-declared member speaks the wrong precondition language. Mixed-dialect members of one pool are not compared at mount.
- Notes: overlaps ad6-5.

### ad7-3 -- unprefixed CAS setting names are still accepted; `cas_*` and bare forms can silently disagree across a fleet (Low)
- Anchor: `ContentAddressedSettings.cpp:49`, `:135-168`, `:210-217` (legacy names applied, `LOG_WARNING`); dual-set throws (`:146-151`). `skip_access_check` stays unprefixed (`:171-173`).
- Trigger: rolling restart while some hosts still use `gc_shards` and others `cas_gc_shards`, or both keys on one disk (loud).
- Evidence: docs call the unprefixed form transitional. Two spellings of the same setting on one disk fail closed. Mixed hosts with one spelling each apply the same value. Residual is the warning-only deprecation and the dual-name ops surface.

### ad7-4 -- emulated mode is chosen only by storage type; the shared-local-path warning is INFO (Low)
- Anchor: `ContentAddressedMetadataStorage.cpp:706-732`.
- Trigger: two servers, `object_storage_type=local`, same path, different `cas_server_root_id`.
- Evidence: `Mode::EmulatedSingleProcess` is automatic. Conditional ops are in-process. The shipped string says not to share the path; it is `LOG_INFO` so client tests do not see it. `EmulatedSingleProcess` is tests / local development. CAS-066.
- Notes: Filimonov: by design. Kept as Low because the only signal is INFO and there is no hostname cross-check.

### ad7-5 -- `cas_gc_shards` config disagreement is silent overwrite; docs say refuse (Low)
- Anchor: `Pool/CasPool.cpp:504`; `docs/en/antalya/cas/configuration.md:96`.
- Trigger: first mounter defaulted to 1; others set `cas_gc_shards=8`.
- Evidence: `_pool_meta` wins; no exception, no warning. Docs claim "a mismatching config is refused at mount". `blob_hash` mismatch is the loud pattern this does not follow.

### ad7-6 -- `skip_access_check` is per-node and unrecorded on ETag members (Medium)
- Anchor: `Pool/CasPool.cpp:459-486`; no mount-slot / `cas_mounts` flag.
- Trigger: one member sets skip, others do not; that member's path may ignore preconditions.
- Evidence: GCS writable refuses skip. ETag members can join unproven. Peers cannot see the skip.
- Notes: CAS-030 / ad4-5 / ad6-2 same gate, skew angle.

### ad7-7 -- CAS settings do not apply on `SYSTEM RELOAD CONFIG` (Medium)
- Anchor: no `ContentAddressedMetadataStorage::applyNewSettings`; `DiskSelector.cpp:180`.
- Trigger: fleet reload after a `cas_*` change; nodes restarted later diverge from nodes that only reloaded.
- Evidence: identical config files, different effective settings until restart. Same as ad4-4, skew angle.
- Notes: CAS-107.

## By-design / info / non-actionable
- Settings live under `cas_` (`917600b122b`). `non_cas_keys` is gone (CAS-106 closed).
- `G_BUILD=10` (`write_attempt_id` on mounts). Older pools recreate-only. Admitting a new hash algo sets `min_reader_generation = G_BUILD`; on this build that floor is already required.
- Identical `server_root_id` on two live servers fails closed.
- `blob_header_len` is not a disk setting; pool meta is authoritative.
- Mount lease TTL / request budget are compile-time and cross-checked.
- Relink `pool_uuid` equality without endpoint bind: CAS-002 / CAS-026 (manifest-trust). Not re-raised as High.

## Closed-since-2026-08-12
- `non_cas_keys` / unprefixed-only UNKNOWN_SETTING death (CAS-106): `cas_` prefix + legacy alias warning.
- GCS versioning fail-open and GCS `skip_access_check`: fail-closed / refused (`b69051a2d85` + later skip gate).

## Coverage
- Reviewed: nested srid; generation floor; GCS dialect selection; dual spelling; emulated-mode choice; gc_shards override; skip_access_check skew; reload.
- N-A: Keeper-side queue skew beyond the partition-command gate.
- Deferred: SQL `disk()` custom CAS lifecycle.
