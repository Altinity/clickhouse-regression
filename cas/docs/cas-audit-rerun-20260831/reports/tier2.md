# tier2 -- fresh audit 2026-08-31

## Scope
Tier2 in this re-run is the **admin verb** surface: FREEZE, ATTACH PARTITION FROM, DROP POOL MEMBER, GC REBUILD, RELOAD CONFIG.

- Files/dirs examined: `DataPartStorageOnDiskBase.cpp` (`freeze`, `freezeRemote`), `MergeTreeData.cpp` (`freezePartitionsByMatcher`, `cloneAndLoadDataPart`), `Backup.cpp`, `ContentAddressedMetadataStorage.cpp` (`shadowNamespace`, `isDirectoryEmpty`, `applyNewSettings` absence), `Pool/CasServerRoot.h` (`validateServerRootId`), `Tools/CasDecommission.cpp`, `Pool/CasPool.cpp` (`openForDecommission`), `programs/disks/CommandCaGcRebuild.cpp` / `CommandCaDropMember.cpp`, `IMetadataStorage.h:365-368`, `DiskObjectStorage.cpp:978-984`.
- Explicitly out of scope: happy-path INSERT/SELECT (tier1); GC round internals except the REBUILD entry point.

## Findings
### tier2-1 -- repeated FREEZE WITH NAME merges shadow refs instead of DIRECTORY_ALREADY_EXISTS (Medium)
- Anchor: see alter-merge-mutation-3. `isDirectoryEmpty` true for part dirs; `publishStaging` merge/repoint.
- Trigger: `ALTER TABLE t FREEZE WITH NAME 'b'` twice.
- Evidence: second freeze is accepted and unions snapshots. UNFREEZE drops the union. Same residual as CAS-086.
- Notes: CAS-086.

### tier2-2 -- nested `server_root_id` `a/b` is valid; DROP POOL MEMBER on `a` selects `a/b` (Medium)
- Anchor: `CasServerRoot.h:76-105` (`validateServerRootId` allows `/` between non-empty segments); `CasDecommission.cpp:146-151` (`victim_srid + "/"` prefix plus exact `victim_srid`).
- Trigger: two members configured as `a` and `a/b` (validation accepts both). `SYSTEM CAS DROP POOL MEMBER` / `clickhouse-disks cas-drop-member` on `a`.
- Evidence: ownership is path-prefix. Dropping `a` lists and tears down namespaces rooted at `a/b`. Live member data becomes decommission debris. Requires an operator-chosen nested id, but the validator is the gate that should have refused it. Same root cause as CAS-007.
- Notes: CAS-007.

### tier2-3 -- SYSTEM RELOAD CONFIG does not apply any `cas_*` setting (Medium)
- Anchor: `IMetadataStorage.h:365-368` default empty `applyNewSettings`; `ContentAddressedMetadataStorage.h` has no override; `DiskObjectStorage.cpp:978-984` calls `metadata_storage->applyNewSettings` then returns. Settings are ctor-captured (`ContentAddressedMetadataStorage.cpp:297-299`).
- Trigger: change `cas_gc_interval_sec` / cache budgets / `cas_part_folder_validate` and `SYSTEM RELOAD CONFIG`.
- Evidence: no CAS setting is re-read. Removing the disk from config leaves the mount lease renewing until restart (generic disk warning only). Same root cause as CAS-107.
- Notes: CAS-107.

### tier2-4 -- offline `cas-gc-rebuild` has no mount-lease interlock against a live writer (Low)
- Anchor: `programs/disks/CommandCaGcRebuild.cpp:54-65` (requires `isReadOnly()`, then `Gc::rebuildBaseline` writes `gc/state`). Help text says never run against a disk a live server has mounted; nothing checks for a live mount lease in the bucket.
- Trigger: operator runs `clickhouse-disks cas-gc-rebuild` with `<readonly>true</readonly>` on the same prefix a live server is writing.
- Evidence: the readonly open avoids claiming a *second* writer mount, but rebuild still CASes `gc/state`. A concurrent live GC round can race that CAS. Server-side `SYSTEM CAS GC REBUILD` holds the GC lease (not this finding). Same residual as CAS-004.
- Notes: CAS-004.

## By-design / info / non-actionable
- `ATTACH PARTITION FROM` / `freezeRemote`: now one dest transaction (`84b30f6b0d9`). Cross-disk attach is no longer a confirmed blocker.
- FREEZE/UNFREEZE namespaces include `server_root_id` (`335802a938f`). Cross-server UNFREEZE of another replica's freeze is closed.
- `cas-drop-member` requires a read-only disk open (`CommandCaDropMember.cpp:49`) so the tool does not claim the live mount.

## Closed-since-2026-08-12
- CAS-058 ATTACH-from-other-disk (`freezeRemote` txn).
- CAS-001 FREEZE isolation (`server_root_id` in shadow namespace).

## Coverage
- Reviewed: FREEZE/UNFREEZE, ATTACH/REPLACE FROM, DROP POOL MEMBER / cas-drop-member, GC REBUILD SQL vs clickhouse-disks, RELOAD CONFIG.
- N-A: INSERT/SELECT/merge.
- Deferred: runtime attach of two replicas after the freezeRemote fix (static only).
