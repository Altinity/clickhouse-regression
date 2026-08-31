# security -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Formats/CasLayout.{h,cpp}` (`checkNamespace`, `isCleanRelativeNamespaceFileName`), `Pool/CasServerRoot.h` (`validateServerRootId`), `Pool/CasServerRoot.cpp` (`serverRootSubtreeEmpty`, claim/mount), `Tools/CasDecommission.cpp` (DROP POOL MEMBER ownership cut), `Primitives/CasBlobDigest.{h,cpp}`, `Primitives/CasBlobHashingWriteBuffer.cpp`, `Pool/CasPartWriteTxn.cpp` (publish/adopt, no re-hash), `ContentAddressedMetadataStorage.cpp` (`liveNamespace`, `shadowNamespace`, `ownsNamespace`, `readBlobPayload`), `ContentAddressedSettings.cpp` (`blob_hash` default), `src/Access/Common/AccessType.h`, `src/Interpreters/InterpreterSystemQuery.cpp` (SYSTEM CAS verbs + ON CLUSTER), `src/Storages/System/StorageSystemContentAddressedMounts.cpp`, `src/Interpreters/SystemLog.h` (`cas_log`, `cas_gc_log`), `src/Disks/DiskEncrypted.h` / `IDisk.h` (`isContentAddressed`), S3 `server_side_encryption_customer_key_base64` wiring.
- Explicitly out of scope: GC round protocol beyond decommission prefix matching; write/read protocol internals except hash-on-read and admit; `docs/en/antalya/cas/**` as evidence of intent.

Attacker models (same names as the 2026-08-12 angle): **P** bucket-credential peer; **U** SQL user without `SYSTEM CAS *`; **N** network/MITM on interserver HTTP; **O** operator of one node.

## Findings
### security-1 -- Nested `server_root_id` still selects another member's namespaces on DROP POOL MEMBER (Medium)
- Anchor: `Pool/CasServerRoot.h:76-106` (`validateServerRootId`) at ceee42c; `Tools/CasDecommission.cpp:146-151` (`victim_namespace_prefix = victim_srid + "/"`); `Pool/CasServerRoot.cpp:619-625` (`serverRootSubtreeEmpty` uses the same prefix rule).
- Trigger: configure two writable CAS disks on one pool with `cas_server_root_id` values `a` and `a/b` (both pass `validateServerRootId`). Run `SYSTEM CAS DROP POOL MEMBER 'a' FROM DISK …`. The catalog cut treats every life whose namespace is `a` or starts with `a/` as owned by the victim, so `a/b/store/…@cas@` is drained.
- Evidence: `validateServerRootId` rejects empty segments, `.`/`..`, `_files`, `_manifests`, and length > 255, but it still admits `/`. Live namespaces are `server_root_id + "/" + mirroredArchiveNamespace(…)`. Decommission then keeps a catalog row when `entry.ns == victim` **or** `entry.ns.starts_with(victim + "/")`. That slash only stops `a` from matching `a2`; it does not stop `a` from matching `a/b`. `ownsNamespace` uses the same prefix shape. Privilege is not the hole: the verb is behind `SYSTEM_CAS_DROP_POOL_MEMBER` (GLOBAL). The hole is the ownership predicate.
- Notes: same root cause as CAS-007 (Filimonov confirmed, P2). Not High: it needs an operator-configured nested pair, not an unprivileged trigger.

## By-design / info / non-actionable
- **Hash default is cityhash128; reads do not re-hash.** `ContentAddressedSettings.cpp:59` defaults `blob_hash` to `cityhash128`. `CasPartWriteTxn.cpp:97-102` states the core never re-hashes payloads; `ensureBlobPresent` adopts a present non-condemned body after HEAD + size check only (`:357-387`). `readBlobPayload` (`ContentAddressedMetadataStorage.cpp:2070-2079`) is a ranged GET. Selectable at pool creation (`cityhash128` | `xxh3-128` | `sha256`). Filimonov CAS-008: by design. Still true. No new reachability.
- **Intra-pool trust is the bucket credential.** Owner, epoch, mount lease, GC state, ref log, manifests, and blobs are unsigned objects in the shared prefix. Identity is field comparison (`claimOwnerOrThrow`, `claimMount`). Filimonov CAS-027: the bucket credential is the entire trust boundary. Still true. Relink adds no new ACL: `prepareAdoptFromManifest` (`ContentAddressedMetadataStorage.cpp:2285-2288`) states the interserver channel is the trust boundary, matching ordinary part fetch.
- **Blob keys are unsalted pool-global content hashes.** Layout is `blobs/<algo>/<shard>/<hex>`. That is dedup. Filimonov CAS-028: by design. `system.cas_log` can name hashes; it needs an explicit SELECT grant (same as other system logs).
- **`Layout::checkNamespace` still admits `.` and `..`.** `CasLayout.cpp:317-343` rejects empty / `_files` / `_manifests` only. `validateServerRootId` and manifest entry paths (`CasPartManifestFormat.cpp:206-218`) do reject `.`/`..`. Production namespaces are `validated-srid + "/" + store/<u3>/<uuid>@cas@` (Atomic) or an escaped FREEZE path. Filimonov CAS-091: no production reachability. Still no new producer that feeds `.`/`..` into `checkNamespace`. Residual only.
- **SYSTEM CAS privileges hold.** Seven GLOBAL types in `AccessType.h:355-361`. Each verb checks its own type in `InterpreterSystemQuery.cpp:1053-1089` and again in `getRequiredAccessForDDLOnCluster` (`:3276-3309`). `DROP POOL MEMBER` also requires a non-read-only CA disk (`:1096`).
- **System tables are ordinary SELECT surfaces.** `system.cas_mounts`, `system.cas_log`, `system.cas_gc_log` expose mount identity and audit rows, not credentials. Same class as `system.disks` / `system.clusters`. Filimonov CAS-132: not a privilege bypass.
- **CAS × DiskEncrypted is still unwired.** `DiskEncrypted` does not override `isContentAddressed` (`IDisk.h:477` default false). Filimonov CAS-059/060: out of scope; first part write fails loud. No silent mix.
- **SSE-C is an S3-layer key, not a CAS protocol.** CAS has no SSE-C-specific path. `cas_staging_backend=s3` requires native same-store copy (`ContentAddressedMetadataStorage.cpp:827-833`) and fails closed if the object store cannot copy. Residual of CAS-090: optional S3 staging plus SSE-C is a mount refusal or a provider-native copy, not a CAS integrity hole.

## Closed-since-2026-08-12
- Previous **security-1** (intra-pool High) and **security-2** (hash-default High) are still the same mechanisms; they are not defects at HEAD (Filimonov CAS-027 / CAS-008). Not closed by code — reclassified.
- Previous **security-6** (error strings leak layout to unprivileged SQL) does not hold: SYSTEM CAS verbs are GLOBAL; inline `disk()` needs the caller's own credentials. CAS-132.
- Privilege checks that the 2026-08-12 report treated as missing for ON CLUSTER are present (`getRequiredAccessForDDLOnCluster` lists all seven verbs).
- No code close of CAS-007 (nested srid). It is the finding above.

## Coverage
- Reviewed: hash/algo default and read-path verification; intra-pool authentication (absence); unsalted blob keys; `checkNamespace` vs `validateServerRootId` vs manifest-entry hygiene; SYSTEM CAS access types and check sites; `system.cas_mounts` / `cas_log` / `cas_gc_log`; DiskEncrypted `isContentAddressed`; SSE-C / S3 staging gate; decommission ownership prefix.
- N-A: network MITM of TLS-wrapped S3 (bucket TLS is outside CAS).
- Deferred: collision-cost measurement of CityHash128 (published properties only).
