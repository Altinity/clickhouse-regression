# ad7-protocol-skew -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is
(all CAS tests deleted). Read-only, static reasoning only. CAS root:
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

Subject: divergence between pool participants caused by **configuration, settings, or partial deployment**, not by build
version. Covered: every `ContentAddressedSettings` entry that can affect shared-pool semantics; validation of config
against the persisted `_pool_meta`; disk / storage-policy skew across replicas of one table (relink, fetch, replication
queue); `server_root_id` assignment, uniqueness, reuse, collision; the same table UUID under two pools; clock and cadence
skew between GC participants; ClickHouse-level settings that change CAS behaviour; config reload semantics.

Code-only rule honoured: `docs/**` and comments are not treated as intent; only shipped strings, exceptions and log text
are used as evidence of intended behaviour.

Cited, not re-reported (owned by the upgrade-compat sibling): format-generation stamping, the dead `changePoints`
registry, payload-digest recompute across a generation bump, and relink protocol 11 not covering CAS generation.
Cross-pool ATTACH/cross-disk ATTACH are tracked by the existing issue drafts and are out of scope here.

## Setting skew classification

`ContentAddressedSettings` is loaded per disk from the disk's config section (`ContentAddressedSettings.cpp:84-117`) and
never re-read afterwards. "Validated at mount?" means: compared against the pool-authoritative `_pool_meta` (or any other
pool-wide object) while opening the pool.

| setting | default | must match pool-wide? | validated at mount? | behavior on disagreement | anchor |
|---|---|---|---|---|---|
| `blob_hash` | `cityhash128` | **(a) yes, unless deliberately admitted** | yes — membership in `_pool_meta.algos_used` | throws `BAD_ARGUMENTS` with the admitted set and the `blob_hash_allow_new` hint | `CasPoolMeta.cpp:49-67, 100-104` |
| `blob_hash_allow_new` | `false` | **(a)** (one node flips pool-wide state) | n/a (it *is* the mutation switch) | silently and irreversibly appends the algo to `algos_used` and raises `min_reader_generation` | `CasPoolMeta.cpp:66-84` |
| `gc_shards` | `1` | **(a)** ("creation-time only" per the shipped string) | no comparison — pool value overwrites the config value | silently overridden, no log, no metric; first bootstrapper wins | `CasPool.cpp:351-354, 547-550` |
| `server_root_id` | *(required)* | **(a) must be unique per member** | owner anchor + mount slot (identity, not layout disjointness) | identical srid: fail-closed; *nested* srid: accepted and destructive (ad7-1) | `CasServerRoot.h:104-134`, `CasServerRoot.cpp:105-159` |
| `skip_access_check` | `false` | **(a) in effect** — it disables this node's only precondition proof | no | node mounts writable without proving its I/O path enforces preconditions; nothing records it | `CasPool.cpp:339-347`, `CasProbe.cpp:15-66` |
| `gc_enabled` | `true` | **(c) unclear** — pool needs ≥1 enabled member | no | if every member disables it, nothing reclaims; no pool-wide signal | `ContentAddressedMetadataStorage.cpp:610-617` |
| `gc_interval_sec` | `60` | **(c) unclear** — it sets both the round cadence and the lease-steal observation window | no | asymmetric steal of a healthy leader's GC lease (ad7-7) | `CasGcScheduler.cpp:41-43, 227`, `CasGc.cpp:3155-3186` |
| `gc_snapshot_generations_to_keep` | `3` | (b) may differ safely | no | leader-local prune floor; adopted/referenced generations are never pruned and `snap_pruned_through` is monotone | `CasGc.cpp:2456-2497` |
| `gc_round_*` budgets, `manifest_sweep_*`, `gc_meta_pool_size` | see `ContentAddressedSettings.cpp:40-49,57` | (b) | no | leader-local work caps; cursors persist, so progress is monotone across leaders | `CasGc.cpp:440-448` |
| `deduplication_cache_bytes`, `deduplication_head_first_min_bytes`, `manifest_decode_cache_bytes`, `part_folder_cache_*` | see `ContentAddressedSettings.cpp:36-37,52-54,56` | (b) | no | node-local caches only; dedup skips are re-proved by conditional writes | `CasPool.cpp:165-168`, `PartFolderAccess.cpp:140-147` |
| `part_folder_validate` | `always` | (b) | no | cache entries are keyed by the resolved (immutable) manifest id, so `never`/`age` only skip a re-read of immutable bytes | `PartFolderAccess.cpp:158-188` |
| `staging_backend` | `local` | (b) | no (a per-node conditional-copy probe decides fallback) | staging keys are per-member under `<pool>/staging/<srid>/`; falls back to local staging when copy is unconditional | `ContentAddressedMetadataStorage.cpp:596-608` |
| `scratch_path` | server data path | (b) node-local | no | node-local spill directory only | `MetadataStorageFactory.cpp:238` |
| `gcs_max_conditional_put_bytes` | 1 GiB | (b) | no | bounds this node's single-PUT conditional writes; an over-large value fails that node's own writes loudly | `ContentAddressedMetadataStorage.cpp:512`, `IO/WriteBufferFromS3.cpp:414` |
| `blob_header_len` | 256 (**not config-exposed**) | (a) | yes — pool meta is authoritative for all envelope reads/writes | cannot diverge by configuration; a foreign value marks the root "replaced" at remount | `CasPool.h:46`, `CasPool.cpp:113-117, 658` |
| mount lease TTL / renew cadence / `CasRequestBudget` | 30 s / 10 s / built-in (**not config-exposed**) | (a) | n/a | cannot diverge by configuration; internally cross-checked by `validateCasRequestBudget` | `CasPool.h:73-79`, `CasPool.cpp:399-402` |

## Findings

### ad7-1 -- Nested `server_root_id` is accepted, and decommission of the ancestor destroys a live descendant member (High)

- **Anchor**: `Pool/CasServerRoot.h:104-134` (validation); `Tools/CasDecommission.cpp:124-135` (victim namespace
  selection), `:186-202` (prefix deletions); `ContentAddressedMetadataStorage.cpp:607` +
  `Pool/CasServerRoot.cpp:1140-1163` (startup staging sweep); `Formats/CasLayout.h:233-241`.
- **Skew scenario**: `validateServerRootId` accepts `/` and rejects only empty/relative segments and the reserved
  segments `_files` and `_manifests`. Two nodes of one pool are configured with `server_root_id` = `prod` and
  `prod/2` (e.g. macro expansion `{cluster}` vs `{cluster}/{replica}` on different hosts, or one host later "narrowing"
  its id). Both mount successfully: the owner anchors and mount slots are distinct keys, and namespaces are
  `srid + "/" + <table path>` (`ContentAddressedTransaction.cpp:579, 1003-1004, 1117`), so nothing collides.
- **Consequence**: every ownership test for `prod` is a string-prefix test that also matches `prod/2`.
  `ca-decommission prod` selects catalog entries where `ns == "prod"` **or** `ns.starts_with("prod/")`
  (`CasDecommission.cpp:128`) and calls `dropNamespace` on each, then wholesale-deletes
  `roots/prod/` and `<pool>/staging/prod/` (`:198-202`) — i.e. it drops the *live* member `prod/2`'s refs and mountpoint
  objects while `prod/2` is mounted and writing. `openForDecommission` only checks the victim slot's own liveness
  (`CasPool.cpp:533-558`), so nothing notices the live descendant. The same prefix confusion makes node `prod`'s
  startup staging sweep (`staging/prod/` + `"/"`) delete node `prod/2`'s in-flight staged blobs, and makes
  `serverRootSubtreeEmpty("prod")` report the descendant's data as the ancestor's (`CasServerRoot.cpp:82-95`).
- **Evidence**: reserved-segment validation exists but covers only `_files`/`_manifests`; the slot control names
  (`owner`, `epoch`, `mount`) and the ownership-by-prefix assumption are unvalidated. No code path compares a new srid
  against the srids already registered under `gc/server-roots/` for prefix containment.

### ad7-2 -- Relink trusts `pool_id` equality as proof of "same bucket", and adopts blob dependencies without any presence check (High)

- **Anchor**: `DataPartsExchange.cpp:313-330` (sender gate is `receiver_pool_uuid == ca_meta->getPoolUUID()`),
  `:780-787` (receiver gate is the same equality); `ContentAddressedMetadataStorage.cpp:587`
  (`pool_uuid = hex(poolMeta().pool_id)`), `:1592-1636` (`prepareAdoptFromManifest`);
  `Pool/CasPartWriteTxn.cpp:478-486` (`adoptEvidence` records the dep with no HEAD), `:228-232` (`isTrustedAdopt`),
  `:676-695` (promote accepts an untokened adopted dep, emitting only `manifest-trust`); `CasPoolMeta.cpp:24-29, 111-119`
  (`pool_id` is a random 128-bit mint).
- **Skew scenario**: the bucket (or just the pool prefix) is copied — a DR restore, a `aws s3 sync` clone into a second
  bucket, a staging copy of production. The clone carries the same `_pool_meta`, hence the same `pool_id`, hence the same
  advertised `cas_pool_uuid`. Replica A's disk points at the original bucket, replica B's disk at the clone (different
  `endpoint`/`path`, same `server_root_id` space). They are two *physically distinct* pools that are
  indistinguishable to the relink handshake.
- **Consequence**: A offers a relink, B accepts it, decodes the transferred manifest and calls `adoptEvidence` for every
  blob leaf. `adoptEvidence` only records `BlobDepRecord{..., adopted=true}`; `promote` requires a dep that is either
  tokened (observed) or "trusted adopt", and the trusted-adopt branch performs no `head`/`get`. The only body check in
  `promote` is for the *manifest* object that B staged itself (`CasPartWriteTxn.cpp:642-651`). B therefore commits a ref
  whose part manifest points at blob keys that were only ever written to A's bucket — any blob that A wrote after the
  clone (or that the clone lost) is missing. Failure surfaces later as read errors on B, and B's GC treats the manifest
  as live evidence, so nothing self-heals. The protocol-11 confirm (`:162-223`) only proves that *A* still holds the
  manifest it offered; it cannot prove presence in B's bucket.
- **Evidence**: nothing binds `pool_id` to the endpoint, bucket, or key prefix — it is minted from
  `thread_local_rng()` and copied verbatim with the objects. The receiver's own guard (`:781`) compares only the uuid,
  and its log text ("reservation landed outside the advertised pool") shows the check is about *which local disk*, not
  about physical pool identity.

### ad7-3 -- No CAS setting can be changed by config reload, and the ignore is silent; a removed CAS disk keeps its mount (Medium)

- **Anchor**: `MetadataStorages/IMetadataStorage.h:340-343` (default no-op `applyNewSettings`) and the absence of any
  override in `ContentAddressedMetadataStorage.h/.cpp`; `DiskObjectStorage.cpp:961-987` (forwards to the metadata
  storage); `DiskSelector.cpp:176-183` (existing disks are only `applyNewSettings`-ed, never recreated), `:192-219`
  (a disk that disappeared from config only produces a warning).
- **Skew scenario**: an operator raises `gc_shards`, switches `blob_hash`, disables `gc_enabled`, tightens a GC budget,
  or changes `server_root_id` in `storage_configuration`, then runs `SYSTEM RELOAD CONFIG`. The reload succeeds; every
  CAS setting is dropped on the floor because the CAS metadata storage does not implement `applyNewSettings` and the
  disk object is never rebuilt. There is no warning, no `changed`-detection, and no system table exposing the *effective*
  CAS settings, so the on-disk config and the running behaviour diverge until the next restart — across a fleet, nodes
  restarted at different times run different effective settings from identical config files.
- **Consequence**: config-vs-runtime skew is undetectable by inspection; the operator believes a pool-wide change
  landed. Symmetrically, deleting a CAS disk from the config (the natural way to move a member to another host) leaves
  the pool mounted and its lease renewing until restart, so the intended successor either fails closed as a live
  double-start or is refused as a foreign owner.
- **Evidence**: the setting descriptions ship runtime-sounding text ("Run the background GC scheduler on this disk",
  "Seconds between background GC rounds") with no indication that they are start-time only; the only setting the code
  itself marks as immutable is `gc_shards` ("creation-time only") and `blob_hash` ("fixed at pool creation").

### ad7-4 -- `gc_shards` disagreement is resolved by silently overwriting the node's configured value (Medium)

- **Anchor**: `CasPool.cpp:351-354` (`config.gc_shards = meta.gc_shards;`), identically at `:547-550`;
  `CasPoolMeta.cpp:89-127` (the existing-pool branch returns the stored `PoolMeta` and never compares
  `blob_header_len`/`gc_shards` against the caller's values); `ContentAddressedSettings.cpp:39, 123-126` (only
  `>= 1` is enforced).
- **Skew scenario**: a pool is bootstrapped by whichever member mounts first. If that member's disk section omits
  `gc_shards` (default 1) and the other members set `gc_shards=8` for scale-out, all of them run with 1. The reverse
  ordering is equally possible: whoever wins the bootstrap race fixes the value for the pool's lifetime.
- **Consequence**: an operator-visible setting has no effect and no diagnostic. Unlike `blob_hash` — where the mismatch
  is a loud `BAD_ARGUMENTS` naming the admitted set and the opt-in switch — `gc_shards` produces no exception, no
  warning log, and no metric; `system.disks`-style introspection reports the post-override value
  (`CasInspect.cpp:282` prints `poolConfig().gc_shards`). Reducer fan-out therefore stays at the accidental value while
  the config claims otherwise; the only cross-check that exists compares `gc/state` against the *already overridden*
  pool value (`CasGc.cpp:3135-3138`), so it can never fire on a config disagreement.
- **Evidence**: `PoolMeta::createOrValidate` validates the caller's `blob_header_len`/`gc_shards` for well-formedness
  before deciding, then discards them when the pool already exists — the "validate" half of the name only covers
  `algos_used`.

### ad7-5 -- Local-object-storage CAS silently degrades to in-process emulated conditional writes; two servers over a shared filesystem both mount (Medium)

- **Anchor**: `ContentAddressedMetadataStorage.cpp:509-520` (mode selection + `LOG_INFO` warning);
  `Backend/CasObjectStorageBackend.cpp:78-91` (`checkConditionalWriteSingleAttemptSupport` returns early for non-Native
  mode), `:440-465` and the `emu_mutex`-guarded conditional operations at `:491, 533, 560, 651, 687, 715, 763`.
- **Skew scenario**: two servers are configured with a `type=local`/`object_storage_type=local` CAS disk whose `path`
  resolves to the same shared filesystem (NFS/EFS/hostPath), with *different* `server_root_id` values — the ordinary
  way to add a second member. Because `ObjectStorageType::Local` selects `Mode::EmulatedSingleProcess`, each server
  emulates "conditional" PUT/CAS semantics in its own process memory (per-key token table under a process-local mutex).
  Distinct srids mean the owner-anchor and mount-slot exclusivity checks never see each other, so both mount writable.
- **Consequence**: every conditional write on a shared object — `gc/state`, `cas/ref_catalog`, ref logs/checkpoints,
  blob meta — is unconditional across processes. Lost updates on the catalog and the GC state are possible with no
  error, i.e. exactly the invariant CAS is built on is void. The only signal is one `LOG_INFO` at startup; nothing
  fails closed, even though the mount slots already carry `hostname` and `pid` (`CasServerRoot.cpp:254-265`) and a
  foreign-hostname check would be cheap.
- **Evidence**: the shipped string states the constraint precisely ("safe ONLY for a single server. Do NOT share this
  pool path between multiple ClickHouse servers (e.g. a shared/NFS mount): the CAS/GC invariants would break silently"),
  and it is emitted at INFO with no enforcement.

### ad7-6 -- `skip_access_check` is a per-node opt-out of the only proof that *this node's* path enforces preconditions, and the opt-out is not recorded (Medium)

- **Anchor**: `CasPool.cpp:339-347` (probe on every writable open, or the reduced static check when skipped);
  `Backend/CasProbe.cpp:15-66` (the probe proves `checkPoolPreconditions`, conditional create rejection, and
  no-clobber-on-conflict against the real endpoint).
- **Skew scenario**: members of one pool reach the same bucket through different I/O configurations — a caching or
  rewriting S3 gateway, a compatibility endpoint, a different `http_client` — because `endpoint`, `http_client` and
  friends are explicitly excluded from CAS settings (`ContentAddressedSettings.cpp:23-27`) and are per-node anyway. One
  member sets `skip_access_check=1` (the shipped description invites it: "start now, fix later"). That member's only
  remaining check is `checkConditionalWriteSingleAttemptSupport`, which asserts a *build/object-storage-type* capability,
  not the endpoint's actual precondition enforcement.
- **Consequence**: a path that silently ignores `If-None-Match`/`If-Match` is admitted into a live pool; its
  "conditional" writes are unconditional, which breaks single-writer and CAS-token guarantees pool-wide. Because the
  skip is node-local config and is not persisted anywhere (no mount-slot flag, no `system.cas_mounts` column, no event),
  no operator or peer can tell that a member joined unproven.
- **Evidence**: the probe is deliberately re-run on every writable open (not only at bootstrap), which shows the
  intent is per-mount verification; `skip_access_check` removes it with no compensating record.

### ad7-7 -- GC lease-steal window is derived from the challenger's own `gc_interval_sec` while the incumbent's liveness evidence ticks at the incumbent's cadence (Medium)

- **Anchor**: `CasGcScheduler.cpp:41-43` (`hb_interval = own interval / 4`), `:227` (round cadence = own interval),
  `:247` (scheduled rounds allow stealing), `:299-308` (heartbeat pulses only while leader);
  `CasGc.cpp:3155-3186` (steal decision: steal unless the lease seq changed **or** the heartbeat advanced since *this*
  process's previous observation).
- **Skew scenario**: node A (leader) is configured `gc_interval_sec=3600`, so it pulses `gc/hb` every 900 s. Node B
  keeps the default 60 s. B's observation interval is one of its own ticks, so at nearly every tick B sees A's lease seq
  and `hb_seq` unchanged and concludes the incumbent is not renewing — while A is perfectly healthy and may be in the
  middle of a long round.
- **Consequence**: B steals the lease from a healthy leader; A's in-flight round then loses authority at its next
  guarded step and aborts (`CasGc.cpp:380-399, 2347-2352`, `throwCasWriteRetryLater` on lost authority at `:455-457`),
  wasting the round's work. Steady state is that the shortest-interval node owns GC regardless of operator intent, and
  each cadence change silently re-elects. The steal itself is CAS-token guarded, so this is a liveness/wasted-work
  defect rather than a corruption one — but the arithmetic has no floor tying the challenger's observation window to the
  incumbent's heartbeat period, which is the only thing that would make cadence skew safe.
- **Evidence**: the follower log text ("lease held by another mounter … investigate if no mounter is reclaiming")
  shows the design expects stealing to indicate a dead leader; nothing in `acquireOrRenewLease` reads or bounds the
  incumbent's cadence.

### ad7-8 -- One node's `blob_hash_allow_new` mutates pool-wide state, after which permanent algorithm divergence is invisible (Low)

- **Anchor**: `CasPoolMeta.cpp:57-85` (`admitOrValidate` appends the algo and sets `min_reader_generation = G_BUILD`);
  `ContentAddressedSettings.cpp:33-34`; `Pool/CasPool.cpp:262` (`writeAlgo()` is the node's configured algo);
  `Primitives/CasBlobDigest.h:145-152` (`BlobRef` carries its algo, so reads stay correct).
- **Skew scenario**: one member is reconfigured to `blob_hash=xxh3-128` with `blob_hash_allow_new=1` and restarted.
  The admission is a pool-wide, one-way mutation. Afterwards both `cityhash128` and `xxh3-128` are admitted forever, so
  a member that still writes `cityhash128` mounts cleanly and no check ever reports the disagreement again.
- **Consequence**: the same content written by two members produces two distinct blob objects, so cross-member
  deduplication silently stops for all new writes (storage and PUT volume roughly double for content written on both
  sides), and the pool's blob set is permanently mixed-algorithm. Reads are unaffected. The reader-floor half of this
  change (`min_reader_generation = G_BUILD`) is the upgrade-compat sibling's subject and is not re-analysed here.
- **Evidence**: `algos_used` has no removal path and no per-member record of who writes which algo; the mismatch
  exception (`CasPoolMeta.cpp:49-55`) can only fire before admission, never after.

### ad7-9 -- A receiver with two CAS pools in one policy advertises only the first pool, silently losing relink for the other (Low)

- **Anchor**: `DataPartsExchange.cpp:586-604` (when no disk is pre-selected, the first CAS disk in `data.getDisks()`
  order sets the single `cas_pool_uuid` query parameter), `:780-787` (a reservation landing on the other pool falls back
  to a byte fetch).
- **Skew scenario**: a storage policy contains two CAS disks belonging to different pools (a migration between pools, or
  a per-volume split). A fetch without a pre-selected disk advertises pool #1 only; if the sender holds the part in
  pool #2 — which the receiver can also reserve on — the sender declines the relink offer entirely.
- **Consequence**: the no-bytes-moved fast path is permanently unavailable for one of the two pools, silently, with the
  cost paid as full byte transfers on every fetch. Correctness is preserved (the mismatch path is explicitly handled and
  logged at INFO), which is why this is Low.
- **Evidence**: the protocol carries a single `cas_pool_uuid` value, and the receiver's own fallback log shows the
  chosen-disk/advertised-pool mismatch was anticipated but only as an error path, not as a multi-pool capability list.

## Checked and sound

- **Mount lease TTL, renew cadence and request budget cannot skew by configuration.** They are compile-time defaults in
  `PoolConfig` (`CasPool.h:73-79`) and are never populated from `ContentAddressedSettings`
  (`ContentAddressedMetadataStorage.cpp:543-568` sets no lease field). `validateCasRequestBudget` cross-checks
  attempt timeout and safety margin against the TTL at mount (`CasPool.cpp:399-402`, `CasRequestControl.cpp:98-133`).
- **Wall-clock skew between participants does not decide liveness.** The GC fence-out requires a mount slot's write
  token to be *unchanged* across observations separated by at least `ttl + ttl/20 + cadence` on the leader's own
  monotonic clock (`CasServerRoot.cpp:393-396, 455-552`); a renewing peer changes its token and resets the observation.
  Wall clock appears only in advisory log/report text and in `system.cas_mounts` state, which adds an explicit
  `ttl/2` skew margin (`StorageSystemContentAddressedMounts.cpp:144`, `CasServerRoot.cpp:638`). The double-start error
  message itself documents the one place wall clock is compared (`CasServerRoot.cpp:368-386`), and that path is guarded
  by the token-stability wait.
- **`blob_header_len` cannot diverge by configuration** (not exposed as a setting; pool meta is authoritative for
  envelope encode/decode at `CasPartWriteTxn.cpp:252, 324, 462` and `CasManifestReader.cpp:141`), and a root whose
  `_pool_meta` shows a different `pool_id`/`blob_header_len` is classified `VanishedReplaced` rather than adopted
  (`CasPool.cpp:93-131, 657-669`).
- **Zero-copy replication is excluded for CAS disks** (`DiskObjectStorage.h:51-55`), so a mixed pair (CAS replica +
  plain-S3 replica, or two CAS replicas on different pools) degrades to a byte fetch instead of exchanging remote
  metadata. This closes the otherwise-dangerous path where a CAS sender would be asked for local metadata files
  (`DataPartStorageOnDiskBase.cpp:359-398`) and, failing, could have had its healthy part reported broken.
- **Identical `server_root_id` on two live servers fails closed.** The owner anchor is keyed by server uuid and refuses
  foreign owners with actionable text (`CasServerRoot.cpp:105-159`); the mount slot refuses takeover across identities
  and, for the same uuid with a different epoch, requires a fence/clean-farewell/token-stability proof
  (`:298-366, 398-453`); a decommissioned root refuses to silently resume (`:68-79`).
- **Reads are safe in a mixed-hash pool**: `BlobRef` is self-describing (`CasBlobDigest.h:145-176`) and admitted algos
  are refreshed from pool meta (`CasPool.cpp:171-194`).
- **`part_folder_validate` may differ per node** without cross-node staleness: cached views are keyed by the resolved
  manifest id and are only reused when that id still matches, and manifests are immutable per id
  (`PartFolderAccess.cpp:149-215`).
- **`gc_snapshot_generations_to_keep` skew is retention-only**: the prune floor is `adopted - keep` with `keep >= 1`,
  generations referenced by the live seal are retained, and `snap_pruned_through` is monotone in `gc/state`
  (`CasGc.cpp:2456-2497`).
- **Inline/manifest caps and fold thresholds are compile-time constants** (`CasPartWriteTxn.cpp:511-533`,
  `PoolConfig` fold fields at `CasPool.h:64-68`), so they cannot skew between participants.
- **ClickHouse part-format thresholds do not change CAS semantics**: `min_bytes_for_wide_part` and siblings are
  replicated table settings and their validation path has no CAS branch (`MergeTreeData.cpp:4986-5031, 10479-10497`).
  The CAS partition-command gate (`MergeTreeData.cpp:6734-6757`) lists every `PartitionCommand::Type`
  (`PartitionCommands.h:20-35`), so it cannot wedge one replica's queue on a command another replica accepted.
  `BACKUP` with temporary hard links is refused loudly on CAS (`DataPartStorageOnDiskBase.cpp:417-422`).

## Coverage

Read in full or in the relevant part: `ContentAddressedSettings.{h,cpp}`, `ContentAddressedMetadataStorage.cpp`
(construction, `openPoolView`, `startup`, exchange surface), `Pool/CasPool.{h,cpp}` (`open`, `mountWritable`,
`openForDecommission`, `tryRemountOnce`), `Pool/CasPoolMeta.cpp`, `Formats/CasPoolMetaFormat.{h,cpp}`,
`Formats/CasLayout.h`, `Pool/CasServerRoot.{h,cpp}`, `Pool/CasPartWriteTxn.cpp` (dep/adopt/promote),
`Parts/PartFolderAccess.cpp` (view freshness, `prepareEntries`), `Gc/CasGcScheduler.cpp`, `Gc/CasGc.cpp`
(round setup, heartbeat floor, lease acquire/steal, generation prune), `Backend/CasProbe.cpp`,
`Backend/CasObjectStorageBackend.cpp` (mode/emulation), `Tools/CasDecommission.cpp`,
`Storages/MergeTree/DataPartsExchange.cpp` (relink offer/accept/confirm, zero-copy branch),
`DataPartStorageOnDiskBase.cpp`, `Disks/DiskObjectStorage/DiskObjectStorage.{h,cpp}`, `Disks/DiskSelector.cpp`,
`MergeTreeData.cpp` (CAS gates), `MergeTreeSettings.cpp` (part-format settings).

Not covered (gaps): any runtime or dynamic verification (static reasoning only, and all CAS tests are deleted in this
tree); Keeper/ZooKeeper-side divergence such as replication-queue entries whose execution depends on a per-replica disk
capability beyond the partition-command gate; SQL-created (`custom`) CAS disks and their lifecycle; encryption or cache
disk wrappers layered over CAS; the interaction of `MergeTree` per-replica `ATTACH`-time setting overrides with CAS;
proxy/endpoint-level dialect differences beyond what the capability probe asserts; and the sibling-owned areas cited in
Scope (format generation, relink generation coverage, cross-pool/cross-disk ATTACH).
