# ad6-s3-lifecycle-cross-region -- fresh audit 2026-08-12

## Scope

Static, code-only audit of the object-store environment CAS depends on and the bucket
configurations that break it. Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`,
branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is (all CAS tests deleted).

Read: `ContentAddressed/Backend/*` (13 files), plus the S3-specific code the backend binds to
(`ObjectStorages/IObjectStorage.h`, `ObjectStorages/S3/S3ObjectStorage.cpp`,
`IO/WriteBufferFromS3.cpp`, `IO/S3/Client.cpp`, `IO/S3/copyS3File.cpp`), and the CAS callers that
decide when the contract is checked (`Pool/CasPool.cpp`, `ContentAddressedMetadataStorage.cpp`,
`Gc/CasGc.cpp`, `Pool/CasPoolMeta.cpp`, `Pool/CasServerRoot.cpp`).

Docs and comments are not treated as evidence of intent; shipped strings are. All anchors are
`file:line` in the target tree.

Cited, not duplicated (siblings own these): versioning detection resting on a single
`created_delete_marker` signal that emulated and some S3-compatible backends never report;
`NoSuchKey` folded into `PreconditionFailed`
(`Backend/CasObjectStorageBackend.cpp:117-120`); `Mode::EmulatedSingleProcess` auto-selected for
local object storage (`ContentAddressedMetadataStorage.cpp:509-511`). This report only uses them
where a *bucket configuration* changes their blast radius.

## Required object-store contract

| Primitive | Required for | Checked at mount? | Anchor |
| --- | --- | --- | --- |
| Conditional PUT `If-None-Match: *` | every blob/manifest/ref create, `putIfAbsent`, `casPut(nullopt)` | Yes, single-PUT only, and only when the capability probe runs | `CasObjectStorageBackend.cpp:646-648`, `CasProbe.cpp:42-66` |
| Conditional PUT `If-Match: <token>` | ref/catalog/lease overwrite, `casPut(expected)` | Yes, single-PUT only | `CasObjectStorageBackend.cpp:682-684`, `CasProbe.cpp:68-95` |
| Conditional PUT on **multipart** (`CompleteMultipartUpload` honoring If-None-Match/If-Match) | any blob larger than the single-part threshold written via `putIfAbsentStream` | **No.** Probe payloads are 8-byte strings; never exercises MPU | `WriteBufferFromS3.cpp:648-657`, `CasProbe.cpp:42`, `CasObjectStorageBackend.cpp:658-673` |
| Conditional DELETE `If-Match: <token>` | all GC reclamation, lease release | Yes (wrong-token then right-token) | `S3ObjectStorage.cpp:479-512`, `CasProbe.cpp:139-196` |
| ETag / generation token stability across write→head→list | every CAS loop; tokens are the concurrency currency | Partially: probe asserts a *new* token on overwrite; list tokens asserted only implicitly | `CasObjectStorageBackend.cpp:62-72`, `CasProbe.cpp:88-90` |
| Delete visibility (no delete marker, no soft-delete tombstone) | GC actually reclaiming space | Only via `created_delete_marker`; plus an explicit `GetBucketVersioning` call **for generation-token stores only** | `CasProbe.cpp:175-183`, `CasObjectStorageBackend.cpp:53-76` |
| Read-after-write | every commit path | Yes | `CasProbe.cpp:48-53` |
| Strongly consistent LIST (list-after-write and list-after-delete) | GC fold, bootstrap residual scan, orphan sweep | Yes | `CasProbe.cpp:153-168`, `CasProbe.cpp:188-195` |
| `SingleAttempt` retry profile (no client-side retry of conditional writes) | ambiguity resolution correctness | Yes, and it is the one check that survives `skip_access_check` | `CasObjectStorageBackend.cpp:78-91`, `CasPool.cpp:344-347` |
| Server-side conditional copy | S3 staging promotion | Yes, behaviorally probed, falls back to local staging | `CasProbe.cpp:213-258`, `ContentAddressedMetadataStorage.cpp:595-608` |
| Object durability against out-of-band deletion (lifecycle, Object Lock expiry, soft-delete purge) | the entire content-addressed model | **No. Silently assumed.** | no `GetBucketLifecycleConfiguration` / `GetObjectLockConfiguration` call exists in the tree |
| Bucket identity / endpoint stability across a mount's lifetime | mount leases, GC state, token coherence | **No. Silently assumed.** | `CasPoolMeta.cpp:111-119` records no bucket, endpoint or region |
| Storage class readable without restore | every part read | **No. Silently assumed.** | no `RestoreObject` / `InvalidObjectState` handling anywhere |

Whole-contract caveat: the entire bootstrap+probe block is skipped for read-only mounts
(`CasPool.cpp:299`) and for `skip_access_check` (`CasPool.cpp:339-347`).

## Bucket-configuration hazard matrix

| Config | Effect on CAS | Detected? | Anchor |
| --- | --- | --- | --- |
| Versioning enabled (AWS S3, MinIO, any ETag-token store) | token-exact DELETE archives a noncurrent version; GC stops reclaiming, bucket grows forever | Only if the store reports `x-amz-delete-marker` on the probe DELETE. `isBucketVersioningEnabled()` is **not** consulted for ETag stores | `CasObjectStorageBackend.cpp:55-56`, `CasProbe.cpp:175-183` |
| Versioning enabled (GCS dialect) | same | Yes, refuses mount — unless the versioning query itself fails, then it proceeds | `CasObjectStorageBackend.cpp:58-75` |
| Versioning *suspended* | deletes still mint delete markers | Only via the same delete-marker signal (shipped string acknowledges this) | `CasProbe.cpp:180-183` |
| GCS soft-delete retention > 0 | deleted generations retained and billed; GC reclaims nothing | **No.** Only mentioned in a log/exception string as operator advice; never queried | `CasObjectStorageBackend.cpp:73-75` |
| Object Lock / WORM / retention | conditional DELETE returns AccessDenied; GC round throws every round; blobs never reclaimed | **No.** Raw `S3Exception` out of `removeObjectIfTokenMatches` | `S3ObjectStorage.cpp:509-511` |
| Bucket policy denying `s3:DeleteObject` | identical to Object Lock | **No** | same |
| Lifecycle expiration rule over the pool prefix | blobs/manifests/refs deleted out from under CAS; reads fail, GC sees phantom absences | **No. Fails open.** | no lifecycle query exists |
| Lifecycle abort-incomplete-MPU rule *absent* | leaked multipart parts accumulate and bill forever | **No**, and CAS never aborts orphaned MPUs itself | `WriteBufferFromS3.cpp:469-492` (abort only on the live object's own cancel path) |
| Transition to IA | works; higher per-request cost only | n/a | — |
| Transition to Glacier / Deep Archive | reads throw `InvalidObjectState`; **no restore-and-retry** anywhere | **No.** Not `NoSuchKey`, so it propagates as a hard read error; in probe paths it degrades to `Indeterminate` | `CasObjectStorageBackend.cpp:272-282`, `CasObjectStorageBackend.cpp:600-609` |
| Requester-pays | every request 403s (no `x-amz-request-payer` header is ever set) | Effectively fail-closed: the mount probe's first PUT fails | no `RequestPayer` anywhere in `src/` |
| SSE-S3 / SSE-KMS default encryption | benign: ETag is opaque to CAS, never used as a content hash (CAS hashes with its own xxh3/blob digest) | n/a — sound | `CasObjectStorageBackend.cpp:62-72` |
| `allow_native_copy=false` (or SSE-C blocking native copy) | conditional copy unavailable | Yes, probed behaviorally, degrades to local staging | `S3ObjectStorage.cpp:765-768`, `ContentAddressedMetadataStorage.cpp:600-604` |
| Cross-region replication (source or destination) | see ad6-7 | **No. Fails open.** | `CasPoolMeta.cpp:111-119` |
| Bucket behind a CDN/proxy with eventual LIST | bootstrap residual scan and GC fold read stale listings | Only the mount-time list-after-write/list-after-delete probe, which is a single-key, single-process check | `CasProbe.cpp:153-195` |

## Findings

### ad6-1 -- Bucket versioning is actively verified only for GCS-dialect clients; on AWS S3 and every S3-compatible store the check is skipped (High)

- **Anchor**: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp:53-56`; `src/Disks/DiskObjectStorage/ObjectStorages/S3/S3ObjectStorage.cpp:519-529`
- **Trigger**: mount a CAS pool on an AWS S3 (or MinIO/RustFS) bucket that has versioning enabled.
- **Consequence**: `checkPoolPreconditions()` returns at line 55-56 whenever
  `native_token_type != TokenType::Generation`, i.e. for every non-GCS store. The versioning
  precondition then rests entirely on the single `created_delete_marker` bit (sibling finding).
  Every GC delete archives a noncurrent version: the pool never reclaims space, and the
  constantly-rewritten ref/catalog/lease objects pile up a version per commit. The failure is
  silent and cumulative — the operator sees a bucket that grows without bound while GC reports
  successful deletes.
- **Evidence**: `S3ObjectStorage::isBucketVersioningEnabled()` (`S3ObjectStorage.cpp:519-529`)
  issues a plain `GetBucketVersioning` and works against any S3 endpoint; nothing about it is
  GCS-specific. The gate that suppresses it is the token type, not the store's ability to answer.
  The shipped exception text at `CasObjectStorageBackend.cpp:71-75` is itself scoped
  ("CAS on GCS: the bucket has object VERSIONING enabled"), confirming the check is wired to one
  provider only.

### ad6-2 -- The one versioning precondition that exists fails open when the query fails (High)

- **Anchor**: `Backend/CasObjectStorageBackend.cpp:58-67`
- **Trigger**: GCS-dialect mount where the caller's credentials lack
  `storage.buckets.get` (a very common least-privilege grant that still allows object read/write),
  or the endpoint does not implement `GetBucketVersioning`.
- **Consequence**: `isBucketVersioningEnabled()` returns `nullopt`, CAS logs a warning and
  **proceeds on the assumption that versioning is OFF**. A versioned bucket is then mounted
  writable. Downstream, the only remaining defense is the delete-marker probe, and if the store
  does not report the marker, GC silently stops reclaiming.
- **Evidence**: the shipped warning string at lines 61-66 states the fail-open decision verbatim
  ("proceeding on the assumption that bucket versioning is OFF ... Please verify the bucket's
  versioning setting manually"). `S3ObjectStorage.cpp:525-526` returns `nullopt` for *any*
  unsuccessful outcome, so AccessDenied and NotImplemented are indistinguishable from
  "not supported".

### ad6-3 -- `skip_access_check` removes every bucket-configuration defense, and the decommission remount hard-codes it (High)

- **Anchor**: `Pool/CasPool.cpp:339-347`; `Pool/CasPool.cpp:528`; `ContentAddressedSettings.cpp:35`
- **Trigger**: set `skip_access_check=true` on the disk (shipped description invites it:
  "Skip the boot-time capability probe (start now, fix later)"), or run any decommission remount.
- **Consequence**: `runCapabilityProbe` is not called, so **all** of the following are skipped:
  `checkPoolPreconditions()` (the GCS versioning query — it is only reachable from inside the
  probe, `CasProbe.cpp:36`), the delete-marker versioning detection, conditional-create /
  conditional-overwrite / conditional-delete enforcement, read-after-write, list-after-write and
  list-after-delete. Only `checkConditionalWriteSingleAttemptSupport()` survives
  (`CasPool.cpp:346`), which merely asks whether the *client* can be configured single-attempt —
  `S3ObjectStorage` answers `true` unconditionally (`S3ObjectStorage.h:166`), so it proves nothing
  about the bucket. A versioned, WORM-locked or lifecycle-managed bucket mounts writable with no
  complaint.
- **Evidence**: `CasPool.cpp:528` sets `config.skip_access_check = true` in the decommission
  path, so the recovery flow — precisely the flow that runs when the pool is already in trouble —
  never re-validates the store.

### ad6-4 -- The conditional-write contract is validated only for single-PUT and then assumed for multipart (High)

- **Anchor**: `IO/WriteBufferFromS3.cpp:409-416`; `Backend/CasObjectStorageBackend.cpp:632-636`; `Backend/CasProbe.cpp:42`
- **Trigger**: an S3-compatible store that accepts `If-None-Match` on `PutObject` but ignores it on
  `CompleteMultipartUpload`, plus any blob large enough to go multipart.
- **Consequence**: the mount probe writes 8-byte bodies, so it only ever exercises the single-PUT
  dialect; it then generalizes that result to `putIfAbsentStream`, which produces a real
  `WriteBufferFromS3` that will transparently switch to multipart. On a store where the
  precondition is dropped at `CompleteMultipartUpload`, the "conditional create" of a large blob is
  an unconditional overwrite — a lost update with no conflict reported to CAS.
- **Evidence**: the codebase already knows this failure mode exists and is real for at least one
  provider — the shipped exception at `WriteBufferFromS3.cpp:410-416` says "the target store
  enforces no preconditions on CompleteMultipartUpload (GCS, measured 2026-07-03) — refusing
  (silent-data-loss risk)". But that guard fires only if `s3_force_single_part_upload` is set, and
  CAS sets it exclusively when `native_token_type == TokenType::Generation`
  (`CasObjectStorageBackend.cpp:632-636`). For every ETag-token store the guard is disarmed and the
  behavior is never probed. `WriteBufferFromS3.cpp:653-657` does attach the headers to
  `CompleteMultipartUpload`, so CAS is relying on server-side enforcement it never measures.

### ad6-5 -- Provider dialect is declared by configuration, never detected (High)

- **Anchor**: `IO/S3/Client.cpp:1301-1307`; `ObjectStorages/S3/S3ObjectStorage.cpp:514-517`
- **Trigger**: point a CAS disk at `https://storage.googleapis.com/<bucket>` without setting
  `http_client` to `gcs_hmac` or `gcp_oauth`.
- **Consequence**: `gcs_conditional_dialect` stays false, so
  `conditionalOpsUseGenerationTokens()` is false, so CAS selects `TokenType::ETag` and
  simultaneously loses **three** GCS-specific protections: the bucket-versioning precondition
  (ad6-1), the single-PUT enforcement that prevents the known GCS multipart silent-overwrite
  (ad6-4), and the generation-ETag response override (`PocoHTTPClient.cpp:733-739`). A pure
  configuration typo therefore converts a fail-closed store into an unsafe one, at runtime, with no
  diagnostic.
- **Evidence**: `Client.cpp:1301-1307` is the only place `gcs_conditional_dialect` is ever set, and
  both branches key off a literal `http_client` string. There is no endpoint sniffing, no
  capability negotiation, and no cross-check between the declared dialect and observed server
  behavior.

### ad6-6 -- Lifecycle rules, Object Lock and storage-class transitions are not detected and fail open; Glacier reads have no restore-and-retry (High)

- **Anchor**: `Backend/CasObjectStorageBackend.cpp:272-282`; `Backend/CasObjectStorageBackend.cpp:588-609`; `ObjectStorages/S3/S3ObjectStorage.cpp:509-511`
- **Trigger**: any of — a lifecycle expiration rule whose prefix covers the CAS pool; a
  transition rule moving cold blobs to Glacier/Deep Archive; an Object Lock retention or a bucket
  policy denying DELETE.
- **Consequence**:
  - *Expiration*: blobs, manifests and ref objects vanish. `isObjectNotFound` maps `NoSuchKey` to
    "absent" (`:272-282`), so CAS treats an externally deleted blob exactly like a never-written
    one; reads fail at query time, and GC/fsck see phantom absences with no signal that the store,
    not CAS, removed them.
  - *Glacier*: the read raises `InvalidObjectState`, which is neither `NoSuchKey` nor
    `FILE_DOESNT_EXIST`, so it propagates as an opaque hard error. There is no `RestoreObject`
    call anywhere in the tree and no retry-after-restore. In `probeSentinelRaw` it lands in the
    `default:` arm at `:601-602` and becomes `Indeterminate`, which upstream callers treat as
    "cannot prove anything" — so a Glacier-tiered pool degrades into permanent indeterminacy
    rather than a nameable error.
  - *Object Lock / deny-DELETE*: `removeObjectIfTokenMatches` classifies only
    `PreconditionFailed` and NotFound (`S3ObjectStorage.cpp:503-507`) and rethrows everything else,
    so every GC round throws on its first reclamation and the pool never reclaims.
- **Evidence**: the tree contains no `GetBucketLifecycleConfiguration`,
  `GetObjectLockConfiguration`, `RestoreObject` or `InvalidObjectState` reference; the only
  storage-class code is the *write*-side `storage_class_name` setting
  (`IO/S3/copyS3File.cpp:146-148`, `WriteBufferFromS3.cpp:732-733`). This is **not detected and
  fails open**.

### ad6-7 -- Zero cross-region / replicated-bucket awareness; a failover to a replica bucket is undetectable (High)

- **Anchor**: `Pool/CasPoolMeta.cpp:111-119`; `Pool/CasPoolMeta.cpp:100-104`
- **Trigger**: DNS/endpoint failover of a CAS disk to a CRR destination bucket (or mounting a
  replica for "read scale-out"), or bidirectional replication configured over the pool prefix.
- **Consequence**: `_pool_meta` records only `pool_id`, `blob_header_len`, `gc_shards`,
  `min_reader_generation` and `algos_used` — no bucket, endpoint, region or replication identity.
  Since CRR copies `_pool_meta` verbatim, the replica presents the *same* `pool_id`, so
  `createOrValidate` (`:100-104`) validates cleanly and CAS mounts the replica believing it is the
  same pool. Consequences that follow directly from the code:
  - Mount leases are objects in the pool prefix, so a replicated lease is a *stale copy*: the
    replica's lease may look expired while the source writer is alive (replication lag), letting a
    second writer claim ownership — split brain with no fencing signal, because the fence is itself
    a replicated object.
  - Conditional writes on the replica succeed against stale tokens; ETags survive replication, so
    an `If-Match` that should conflict may match a stale generation.
  - Token-exact DELETEs are not replicated as data deletions unless delete-marker replication is
    enabled, so blobs GC'd on the source **survive in the replica** — the shadow copy is never
    GC'd, and if the pool later fails back, resurrected blobs re-enter the prefix without ref
    entries (indistinguishable from corruption to fsck).
  - GC state (`snap`/generation prefixes) is replicated asynchronously and partially, so a
    fold started against a source-side snapshot can be resumed against a partially-replicated one.
- **Evidence**: `rg` over the CAS tree finds no `region`/`replica`/`failover` concept; the only
  `region` occurrences are the S3 auth config key (`ContentAddressedSettings.cpp:25`) and an
  unrelated ref-ledger code-region string (`CasRefLedger.cpp:1543`). This is **not detected and
  fails open**.

### ad6-8 -- Post-mount versioning enablement aborts a GC round with LOGICAL_ERROR, after the delete has already happened (Medium)

- **Anchor**: `Gc/CasGc.cpp:611-617`
- **Trigger**: an operator enables versioning (or a compliance tool does) on a bucket already
  hosting a mounted CAS pool.
- **Consequence**: the check is performed on the *result* of `deleteExact`, i.e. after the delete
  marker was already created. The round then throws `LOGICAL_ERROR` mid-reclamation, leaving the
  fold's bookkeeping partially applied and repeating the same abort every round. There is no
  transition to a clean read-only/refuse state and no operator-facing "remount refused" path — the
  disk keeps serving writes while GC is permanently wedged.
- **Evidence**: the shipped message says "versioning is enabled on the pool (mis-provisioned; the
  capability probe must reject this)" — an explicit acknowledgment that this arm is a last-resort
  assertion whose primary defense is the mount probe that ad6-1/ad6-2/ad6-3 show can be absent.

### ad6-9 -- Throttling amplification: conditional writes lose client-side retry, and each throttled attempt costs an extra GET, un-jittered, up to 16 times (Medium)

- **Anchor**: `Backend/CasObjectStorageBackend.cpp:628-639`; `ObjectStorages/S3/S3ObjectStorage.cpp:895-913`; `Backend/CasRequestControl.cpp:43-53`, `:178-188`, `:290-302`; `Backend/CasRequestControl.h:84-93`
- **Trigger**: a bucket/prefix under S3 throttling (503 `SlowDown` / 429), e.g. during a large
  insert burst or a GC-heavy window.
- **Consequence**: conditional writes are issued through the single-attempt client
  (`cfg.retry_strategy.max_retries = 0`, `S3ObjectStorage.cpp:903-904`), so the SDK's adaptive
  backoff is deliberately removed. `classifyConditionalWriteResult` marks only
  malformed-request / entity-too-large / access-denied as `DefiniteFailure`
  (`CasRequestControl.cpp:48-49`); `SlowDown` therefore becomes `Unresolved`, which forces a
  resolution `GET` (`:290-292`, `:212-239`) before the next attempt. Per logical write, a throttled
  prefix sees up to `max_attempts=16` PUTs **and** 16 GETs (defaults at `CasRequestControl.h:84-93`),
  i.e. request-rate amplification of at least 2x precisely when the store is asking for less load.
  The backoff is capped-exponential with **no jitter** (`backoffBeforeAttempt`, `:178-188`), so
  concurrent writers and replicas retry in lockstep; and a budget with
  `retry_initial_backoff_ms = 0` is explicitly legal (`:182`, and
  `validateCasRequestBudget` only requires `initial <= max`, `:120-125`), which turns the loop into
  an unbackoffed 16-shot burst.
- **Evidence**: non-conditional traffic (reads, LIST, unconditional deletes) still goes through the
  retrying default client (`S3ObjectStorage.cpp:350-354`), so the amplification is specific to the
  conditional path — exactly the path that runs on every commit.

### ad6-10 -- AccessDenied on DELETE is unclassified, so WORM/policy-deny buckets surface as raw S3 exceptions (Medium)

- **Anchor**: `ObjectStorages/S3/S3ObjectStorage.cpp:503-511`; `Backend/CasRequestControl.cpp:43-53`
- **Trigger**: Object Lock retention, legal hold, or a bucket policy denying `s3:DeleteObject`.
- **Consequence**: `removeObjectIfTokenMatches` maps only `PreconditionFailed` → `TokenMismatch`
  and NotFound → `NotFound`; AccessDenied rethrows as `S3Exception`. `DeleteOutcome` has no
  "refused by policy" state, so no CAS caller can distinguish "the store will never let me delete
  this" from a transient failure. The `DefiniteFailure` classifier that does understand
  AccessDenied (`CasRequestControl.cpp:48`) is only applied on the *write* path, never to deletes.
  GC therefore retries a permanently-refused delete forever.
- **Evidence**: `classifyDeleteOutcome`/`deleteClassName` (`CasBackend.h:216-238`) enumerate exactly
  three classes — deleted / absent / replaced — with no policy-refusal class.

### ad6-11 -- Incomplete multipart uploads are residue CAS creates and never cleans (Medium)

- **Anchor**: `IO/WriteBufferFromS3.cpp:244-276`, `:313-317`, `:469-492`
- **Trigger**: server crash, SIGKILL, OOM-kill or container eviction while a large blob is being
  streamed by `putIfAbsentStream`.
- **Consequence**: `AbortMultipartUpload` is only ever issued from the live buffer's own
  cancel/destructor path (`:244`, `:269-276`, `:313-317`). If the process dies, the upload ID is
  lost and the parts are orphaned. Nothing in the tree ever calls `ListMultipartUploads`, so CAS
  GC and fsck are structurally blind to this residue — incomplete MPUs do not appear in
  `ListObjectsV2`, hence not in `Backend::list`, hence not in the bootstrap residual scan, the GC
  fold, or the orphan sweep. The storage is billed indefinitely unless the operator has an
  `AbortIncompleteMultipartUpload` lifecycle rule, which CAS neither requires, checks, nor
  documents in any shipped string.
- **Evidence**: a repository-wide search for `ListMultipartUploads` returns nothing.

### ad6-12 -- Capability-probe debris is deliberately excluded from the residual scan and never swept (Low)

- **Anchor**: `Backend/CasProbe.cpp:20-32`; `Backend/CasSentinelProbe.cpp:17-20`, `:43-44`
- **Trigger**: any probe cleanup that fails — which is exactly the case on the mis-provisioned
  buckets the probe exists to catch (deny-DELETE, WORM, versioning, throttling).
- **Consequence**: `cleanup()` is a best-effort `catch(...) {}` over `head` + `deleteExact`. The
  leftovers live at `<pool>/_probe/<random-u128>/{token,cas}`, and every mount attempt mints a
  fresh random uid (`CasPool.cpp:341-342`), so retries accumulate distinct debris. The bootstrap
  residual scan then explicitly `continue`s past anything under `_probe/`
  (`CasSentinelProbe.cpp:43-44`), so the debris is invisible to the one scan that would have
  reported it, and no other sweep targets that prefix.
- **Consequence, second order**: on a versioned bucket each leftover also carries the version
  history of the probe's own overwrite sequence.

### ad6-13 -- Staging residue is reclaimed only for one's own mount, silently, best-effort (Medium)

- **Anchor**: `Pool/CasServerRoot.cpp:1140-1168`; `ContentAddressedMetadataStorage.cpp:596-608`
- **Trigger**: a server that used S3 staging is retired, renamed (`server_root_id` change), or its
  sweep LIST is throttled at mount.
- **Consequence**: `sweepOwnMountStaging` lists exactly
  `<pool>/staging/<own server_root_id>/` and swallows every error, including the top-level LIST
  failure (`:1165-1167`). Staging objects belonging to any other `server_root_id` are never
  enumerated by anyone, and the sweep runs only when `staging_backend == S3 && !read_only &&
  copy_supported` (`ContentAddressedMetadataStorage.cpp:596-607`) — so flipping staging back to
  local, or losing conditional-copy support, strands the existing residue permanently.

## Checked and sound

- **Non-S3 stores fail closed at mount.** `supportsRetryProfile` defaults to accepting only
  `Default` (`IObjectStorage.h:369`) and only `S3ObjectStorage` overrides it
  (`S3ObjectStorage.h:166`), so Azure/HDFS/Web mounts are refused by
  `checkConditionalWriteSingleAttemptSupport` with an explicit message
  (`CasObjectStorageBackend.cpp:84-90`) — and this check survives `skip_access_check`
  (`CasPool.cpp:346`). Likewise `removeObjectIfTokenMatches` and `copyObjectConditional` throw
  `NOT_IMPLEMENTED` by default (`IObjectStorage.h:283-306`), so no non-S3 store can silently
  degrade into unconditional deletes.
- **Conditional copy is probed behaviorally, not declared.** `probeConditionalCopy`
  (`CasProbe.cpp:213-258`) performs a real copy, then a second copy that must be refused, and only
  then enables S3 staging; failure degrades cleanly to local staging with a log line
  (`ContentAddressedMetadataStorage.cpp:600-604`). `allow_native_copy=false` is rejected explicitly
  (`S3ObjectStorage.cpp:765-768`).
- **ETags are treated as opaque tokens, never as content hashes.** `tokenForHead`/`tokenForList`
  (`CasObjectStorageBackend.h:62-72`) wrap the ETag with a `TokenType` and comparison is exact
  equality; blob identity comes from CAS's own digest. SSE-KMS, SSE-C and multipart composite
  ETags are therefore harmless to dedup correctness.
- **Token type is fenced across modes.** `mintingTypeMatches` (`CasObjectStorageBackend.h:105`)
  rejects a token minted under a different dialect, so a pool that changes dialect between mounts
  conflicts rather than silently mis-compares.
- **Bootstrap over residual data fails closed.** An unlistable pool prefix yields
  `Indeterminate` and refuses to mint `_pool_meta` (`CasSentinelProbe.cpp:57-64`,
  `CasPool.cpp:331-336`) — the right behavior under throttling or partial-visibility buckets.
- **Requester-pays is effectively fail-closed.** No `x-amz-request-payer` header is emitted
  anywhere, so every request 403s and the mount probe's first PUT fails before any pool state is
  written.
- **`resurrect` validates before publishing.** Size mismatch aborts the upload and a missing
  object immediately after re-upload fails closed (`CasObjectStorageBackend.cpp:842-855`).

## Coverage

Fully read: `Backend/CasBackend.h`, `Backend/CasObjectStorageBackend.{h,cpp}`,
`Backend/CasRequestControl.{h,cpp}`, `Backend/CasProbe.{h,cpp}`, `Backend/CasSentinelProbe.{h,cpp}`,
`Backend/CasInstrumentedBackend.{h,cpp}` (ProfileEvents-only wrapper; no store-contract logic).
`Backend/CasInMemoryBackend.{h,cpp}` inspected only for its delete-marker simulation, which the
sibling report owns.

S3-specific code read: `S3ObjectStorage.cpp` conditional remove / versioning / conditional copy /
single-attempt client / write path / list path; `IObjectStorage.h` capability defaults;
`WriteBufferFromS3.cpp` conditional-header attachment, multipart create/complete/abort;
`IO/S3/Client.cpp` GCS-dialect selection; `IO/S3/copyS3File.cpp` `If-None-Match` plumbing and
storage-class handling.

CAS callers read for mount-time sequencing: `Pool/CasPool.cpp` (`open`, decommission remount),
`ContentAddressedMetadataStorage.cpp` (`openPoolView`, `startup`), `Pool/CasPoolMeta.cpp`,
`Pool/CasServerRoot.cpp` (staging sweep), `Gc/CasGc.cpp` (delete-marker assertion).

Not covered here (owned by siblings or out of scope): GC protocol internals, ref-ledger and
manifest formats, crash consistency, the emulated-mode token model beyond its interaction with
bucket configuration, and dynamic/runtime behavior of any kind — this audit is static reasoning
only, with no build, no execution and no test evidence available (all CAS tests are deleted in the
working tree).
