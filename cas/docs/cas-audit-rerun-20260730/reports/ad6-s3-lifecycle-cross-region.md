# AD-6 S3 lifecycle / versioning / cross-region — re-run 2026-07-30

## Scope in current code

CAS source: `/Volumes/workspace/ClickHouse` @ branch `cas-audit-20260730` (tracks `altinity/cas-gc-rebuild`).
Root: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

Files/dirs walked:
- `Backend/CasObjectStorageBackend.{h,cpp}` — plain PUT/GET/HEAD/DELETE surface, `checkPoolPreconditions`, `checkConditionalWriteSingleAttemptSupport`.
- `Backend/CasProbe.{h,cpp}` — mount-time capability probe (invokes `checkPoolPreconditions`).
- `Backend/CasBackend.h`, `Backend/CasInMemoryBackend.*`, `Backend/CasInstrumentedBackend.h` — backend interface + emulated/instrumented shims.
- `Pool/CasPool.{h,cpp}` — mount, `Pool::open`, `readManifest*`, `listNamespaces` (S3 consistency assumption).
- `Pool/CasServerRoot.*`, `Pool/CasPlainObjects.*`, `Pool/CasPartWriteTxn.*` — conditional-PUT control plane and `deleteExact` callers.
- `Gc/CasGc.*`, `Gc/CasBlobInDegree.*` — GC reclaim path (uses `deleteExact` + `putIfAbsent`).
- `Parts/PartFolderAccess.{h,cpp}`, `ContentAddressedTransaction.{h,cpp}` — `Freshness::ForceFresh` policy and its manifest re-proof.
- `ContentAddressedSettings.cpp` — `part_folder_validate` setting.

Grep terms (only CAS internal matches found unless noted): `versioning`, `softDelete`, `ObjectLock`, `object_lock`, `lifecycle`, `Lifecycle`, `storage_class`, `StorageClass`, `WORM`, `Glacier`, `InvalidObjectState`, `force_fresh`/`ForceFresh`, `HEAD_then_GET`, `cross-region`, `CrossRegion`, `CopyObject`, `replicat*`. The words `lifecycle` and `Lifecycle` inside CAS refer exclusively to CAS's own `RefLifecycle` / `PoolLifecycle` enums, not S3 bucket lifecycle rules. No matches for `storage_class`/`StorageClass`, `ObjectLock`/`WORM`, `Glacier`/`InvalidObjectState`, or cross-region replication anywhere in the CAS tree.

## Findings still present

### CAS-011 — Bucket versioning / soft-delete precondition covers GCS only; fail-open on inconclusive; S3 versioning unchecked (LIFE-5 / OSC-2)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp:55-84` (`ObjectStorageBackend::checkPoolPreconditions`).
- Trigger: mount a CAS pool on any S3 bucket with versioning enabled, or on any bucket where `isBucketVersioningEnabled()` returns `std::nullopt` (permissions, S3-compatible store).
- Evidence quote (short):
  - `if (mode != Mode::Native || native_token_type != TokenType::Generation) return;` — S3 (ETag-token dialect) short-circuits with **no** versioning check.
  - `if (!versioned.has_value()) { LOG_WARNING(... "proceeding on the assumption that bucket versioning is OFF" ...); return; }` — inconclusive result fails **open** (mount proceeds with a log line).
- Notes: matches original LIFE-5 exactly — the gate is Native+Generation-only, and even there the "unknown" branch is fail-open, only warning. `Pool/CasPool.cpp:411-425` also documents that `skip_access_check` intentionally skips this probe, and calls out that skip "also covers GCS bucket-versioning/delete-marker" — reinforcing that versioning is the only precondition inspected, and only for GCS.

### CAS-016 — Lifecycle expiration deletes live blobs; no guard, no advertised bucket contract (LIFE-1)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp:55-84` (only precondition surface); no lifecycle inspection anywhere in the tree.
- Trigger: attach any bucket that has an S3/GCS expiration lifecycle rule (age-based transition to DELETE); CAS never checks or refuses.
- Evidence quote: no matches for `lifecycle`/`Lifecycle`/`Expiration`/`StorageClass` outside CAS's own `RefLifecycle`/`PoolLifecycle` enums. `checkPoolPreconditions` inspects only bucket versioning.
- Notes: LIFE-1 verdict unchanged — CAS still trusts the bucket to be a plain mutable KV store; an expiration rule silently violates INV-NO-LOSS. No `checkPoolPreconditions` extension. Documentation still absent (`README.md` under CAS does not list bucket-config prerequisites).

### CAS-017 — Object Lock / WORM / retention breaks CAS mutable control plane; unguarded (LIFE-2)
- Anchor: same as CAS-016 — `Backend/CasObjectStorageBackend.cpp:55-84`. Mutable control-plane writers unchanged: `Pool/CasServerRoot.cpp:575-645` (`casPut` overwrite of root-shards with PreconditionFailed re-read), `Gc/CasGc.cpp:673` and `Gc/CasBlobInDegree.cpp:343` (`putIfAbsent` on `gc/state`/in-degree keys), `Pool/CasPartWriteTxn.cpp:508-612` (`putOverwrite` of condemned/staged keys).
- Trigger: bucket configured with S3 Object Lock (compliance or governance mode) or a retention policy covering CAS's `roots/`, `cas/gc/`, `cas/refs/…/_log` prefixes.
- Evidence quote: zero matches for `ObjectLock`, `object_lock`, `WORM`, `retention` (compliance sense) in the CAS tree; `checkPoolPreconditions` does not query `GetObjectLockConfiguration` / `GetBucketObjectLockConfiguration`.
- Notes: same fundamental incompatibility as originally described; conditional overwrites of root-shards and `gc/state` will be denied by an Object Lock bucket, halting writes and GC. Still not detected at mount.

### CAS-051 — Cross-region replication accumulates un-GC'd shadow bucket; DR failover token-incoherent (LIFE-4)
- Anchor: whole-tree observation. All writes go through `ObjectStorageBackend::put*/copyObjectConditional/deleteExact` in `Backend/CasObjectStorageBackend.cpp`; `deleteExact` targets the source bucket only. Nothing acknowledges a replica bucket.
- Trigger: enable S3 CRR/GRR on the CAS bucket; then either measure the replica or fail over to it.
- Evidence quote: no CAS code refers to cross-region, delete-marker replication, or any per-bucket ETag/token remapping. `Pool/CasServerRoot.cpp` root-shard `casPut` conditions are keyed on ETag/generation returned by the primary bucket only.
- Notes: LIFE-4 unchanged. The shadow-bucket accumulation (delete-only-in-source) and the token/ETag incoherence on failover (ETags differ per bucket; `casPut` If-Match preconditions will not match on the replica) both remain latent. No documentation, no `checkPoolPreconditions` extension.

### CAS-052 — Glacier / IA / Deep-Archive tier transition breaks reads; no restore-and-retry (LIFE-3)
- Anchor: read path in `Pool/CasManifestReader.cpp:56` (`readManifestShared`) and blob read path via `ObjectStorageBackend::get*`/`readObjectRanged` in `Backend/CasObjectStorageBackend.cpp` (no `InvalidObjectState` handling anywhere in the CAS tree).
- Trigger: any bucket policy that transitions CAS blobs (or worse, control-plane objects) to Glacier / Deep Archive / Glacier Instant-not / Intelligent-Tiering Archive.
- Evidence quote: no matches for `Glacier`, `InvalidObjectState`, `restore`, `RestoreObject` in the CAS tree.
- Notes: same as LIFE-3 — a ranged GET on an archived object returns `InvalidObjectState` and CAS's read path surfaces the exception to the query, no async restore is initiated. `deleteExact` still works (delete is permitted on Glacier), so the failure mode is read-only breakage of cold partitions.

### CAS-087 — ForceFresh assumes strong-consistency; on eventually-consistent backends it can still serve stale (F-N3)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartFolderAccess.cpp:166-215` (`getView` → `resolve` + `readManifestShared`), `src/Disks/.../Pool/CasPool.cpp:1326-1328` (documented assumption "S3: strongly consistent since 2021. RustFS: to confirm in soak."), `src/Disks/.../Pool/CasManifestReader.cpp:56` (mandatory HEAD-then-GET path).
- Trigger: run CAS against an S3-compatible object store that does not (yet) provide read-after-write LIST + strong read-after-write on overwrites — e.g. RustFS pre-verification, MinIO gateway topologies, or any custom S3-compatible layer with async replication in front.
- Evidence quote: `Consistency requirement: the backend must give read-your-writes LIST enumeration. InMemoryBackend: guaranteed (in-memory map). S3: strongly consistent since 2021. RustFS: to confirm in soak.` — the assumption is declared, not enforced. `ForceFresh` performs a HEAD + manifest read but does not retry on a stale HEAD/GET pair (`PartFolderAccess.cpp:267-270`: "Fresh modes do not coalesce: each `ForceFresh`/`StrictValidate` call owns its mandatory HEAD.").
- Notes: severity is now conditional. For real AWS S3 (strongly consistent since Dec 2020) F-N3 is a non-issue. For any non-AWS S3-compatible store the original finding still stands: no HEAD/GET re-issue on stale, no cross-endpoint retry. Downgraded to backend-conditional but not fixed.

### CAS-114 — CAS sets no storage class; bucket default applies; per-object-kind policy absent (LIFE-6, LIFE-7)
- Anchor: `Backend/CasObjectStorageBackend.cpp` (all `put*` paths issue vanilla writes; no `StorageClass=…` set on WriteBuffer/WriteSettings). Grep confirms zero matches for `storage_class`/`StorageClass` in the CAS tree.
- Trigger: any bucket whose default storage class is not Standard (e.g. Intelligent-Tiering as default, or a lifecycle rule that transitions Standard → IA on age).
- Evidence quote: zero matches for `storage_class` / `StorageClass` under CAS. CAS objects inherit the bucket default with no per-object-kind override (control plane vs blobs treated identically).
- Notes: consistent with LIFE-7 info-level framing. Combined with LIFE-3 (CAS-052) the practical failure mode is quiet cost/latency skew today, and hard read breakage under an archive transition rule.

## Findings fixed / no longer reproducible

None. No new precondition check has been added (still Native+Generation-only versioning gate), no storage-class handling was introduced, no restore-and-retry logic was added, no cross-region awareness.

## New findings (not in original audit)

- **NEW-AD6-1 (Low)** — GCS-versioning precondition treats "cannot verify" as fail-open by design, but the log level is `LOG_WARNING` inside `checkPoolPreconditions`, which many operators filter out at aggregation. Anchor: `Backend/CasObjectStorageBackend.cpp:69-74`. Trigger: mount on a GCS bucket where `GetBucketVersioning` fails (permissions, custom endpoint). Suggested hardening: promote to `LOG_ERROR` plus surface in `system.content_addressed_mounts` so the ambiguous case is visible to operators. This narrows CAS-011 rather than adds a new failure mode, but was not called out in the original AD-6 write-up.
- **NEW-AD6-2 (Info)** — `Pool/CasPool.cpp:1327` bakes the "S3 strongly consistent since 2021" assumption in a comment, without a runtime capability check or a documented supported-backends matrix (RustFS is explicitly listed as unverified in the same comment). Anchor: `Pool/CasPool.cpp:1321-1330` (`listNamespaces`). Not a bug per se, but the contract on which CAS-087 depends is asserted in a comment only.

## By-design / N/A / info

- CAS's own `RefLifecycle` (`Pool/CasRefProtocol.h:187`) and `PoolLifecycle` (`Pool/CasPool.h:339-371`, `Pool/CasMountRuntime.*`) are internal enums; they are **not** related to S3 bucket lifecycle rules and are correctly out of scope for AD-6.
- Multipart abort: not directly verified in this audit; `checkPoolPreconditions` does not enforce or require an `abort-incomplete-multipart-upload` rule (LIFE-recommendation-only in the original audit).

## Verdict summary table

| CAS-id  | Old severity | Status         | Evidence anchor |
|---------|--------------|----------------|-----------------|
| CAS-011 | High         | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp:55-84` (Native+Generation-only; fail-open on inconclusive; S3 versioning not covered) |
| CAS-016 | High         | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp:55-84` (no lifecycle-rule inspection anywhere in CAS tree) |
| CAS-017 | High         | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp:55-84` + mutable control plane at `Pool/CasServerRoot.cpp:575-645`, `Gc/CasGc.cpp:673`, `Pool/CasPartWriteTxn.cpp:508-612` |
| CAS-051 | Med          | 🔴 still-present | Whole-tree: no cross-region/replica awareness; `Backend/CasObjectStorageBackend.cpp` deleteExact/promote path source-only |
| CAS-052 | Med          | 🔴 still-present | `Pool/CasManifestReader.cpp:56` + `Backend/CasObjectStorageBackend.cpp` (no `InvalidObjectState` / restore handling) |
| CAS-087 | Med          | 🟡 backend-conditional / still-present on non-AWS S3 | `Pool/CasPool.cpp:1326-1328` (assumption declared, not enforced); `Parts/PartFolderAccess.cpp:166-215` |
| CAS-114 | Low / Info   | ⚪ info (unchanged) | zero matches for `storage_class`/`StorageClass` in CAS tree; bucket default applies |
| NEW-AD6-1 | (new) Low  | 🛠 will-fix hint | `Backend/CasObjectStorageBackend.cpp:69-74` (LOG_WARNING on inconclusive versioning; no operator-visible surface) |
| NEW-AD6-2 | (new) Info | ⚪ info | `Pool/CasPool.cpp:1321-1330` (S3-consistency assumption asserted in comment only) |
