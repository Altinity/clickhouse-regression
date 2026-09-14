# bc6-mtime-semantics -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `ContentAddressedMetadataStorage.cpp` (`getLastModified`), `ContentAddressedTransaction.cpp` (`setLastModified`), `Pool/CasMountRuntime.cpp` (`bootMs`, `mayMutate`), `Pool/CasServerRoot.cpp` (`defaultBootMs`, renew deadlines), `Pool/CasRefLedger.cpp` (controller constructed with the same `boot_ms_fn`), `Backend/CasRequestControl.cpp`, `Backend/CasObjectStorageBackend.cpp` (`emuMintToken`, `emuPruneTokenState`), `Parts/PartFolderAccess.cpp` (validate age), `Pool/CasPartWriteTxn.cpp` (`nowMs` / `published_at_ms`).
- Explicitly out of scope: `published_at_ms` Poco multiplication overflow (bc1-4); idisk "non-part directory throws" contract (idisk-contract).

## Findings
### bc6-1 -- `getLastModified` still does not consult the manifest, so it dates files that do not exist (Medium)
- Anchor: `ContentAddressedMetadataStorage.cpp:1715-1740`; contrast `getFileSize` at `:1710-1712` at ceee42c
- Trigger: `disk->getLastModified("<part>/does_not_exist.bin")` on a CAS disk where `<part>` resolves to a committed ref.
- Evidence: `parsePartFilePath` + `route` succeed for any tail under a part directory. `resolve_stamp` only requires a non-empty ref (`:1738-1739`); it never asks the view whether `r->file` is present. `getFileSize` on the same path throws `FILE_DOESNT_EXIST`. In-tree effect: `MergeTreeDataPartWide::getColumnModificationTime` can return a timestamp for a checksums-named stream that is absent from the manifest, so `system.parts_columns.column_modification_time` is non-null for a missing file.
- Notes: same root as the previous bc6-1.

### bc6-2 -- `CLOCK_BOOTTIME` is used with no portability fallback (Low)
- Anchor: `Pool/CasMountRuntime.cpp:72-76`; `Pool/CasServerRoot.cpp:66-70` at ceee42c
- Trigger: a Darwin (or other non-Linux) build of this tree. `clock_gettime(CLOCK_BOOTTIME, &ts)` is unconditional; grep of `base/` and the CAS root finds no `#ifdef` / `CLOCK_MONOTONIC` fallback.
- Evidence: production CAS is Linux. Darwin is local-dev / CI-on-mac. If the libc lacks `CLOCK_BOOTTIME`, this is a compile or runtime failure of the mount fence clock, not a split-brain. Same residual as CAS-092.
- Notes: CAS-092. The previous "fence clock ≠ request clock" half is not a defect: `CasRefLedger` constructs `CasRequestController` with the same `boot_ms_fn` the fence uses (`CasRefLedger.cpp:224-227`). Renew deadlines and `mayMutate` (`CasMountRuntime.cpp:92-95`) both read `bootMsNow()`.

### bc6-3 -- emulated-mode token map can grow if wall clock goes backwards (Low)
- Anchor: `Backend/CasObjectStorageBackend.cpp:388-403` (`etagComfortablyInThePast`), `:437-462` (`emuPruneTokenState`), `:531-558` (`emuMintToken`) at ceee42c
- Trigger: `EmulatedSingleProcess` (local object storage; tests / single-process dev) plus a backward step of `system_clock` larger than the 2 s stale window, or a stuck-in-the-future etag.
- Evidence: prune requires `now_ns > etag_ns && (now_ns - etag_ns) >= EMU_TOKEN_STALE_AGE_NS`. A backward clock makes every candidate look young; the FIFO break at `:454` stops the sweep. The mtime-quantum `#N` disambiguator (`:542-551`) is present and closes the "coarse mtime yields a valid stale token" half of CAS-067. What remains is an in-process map leak, not a wrong admit. `EmulatedSingleProcess` is not a multi-server production mode.
- Notes: CAS-067 second half.

## By-design / info / non-actionable
- Part/file/projection/detached/moving/shadow stamps are the ref's `published_at_ms / 1000` (writer `nowMs()`, `system_clock`). All files in a part share one stamp. `setLastModified` is still a no-op (`ContentAddressedTransaction.cpp` write-gate only).
- Non-part existing files return epoch `Poco::Timestamp(0)`. Non-part missing paths throw.
- Fence vs request clocks are the same injectable `CLOCK_BOOTTIME` seam. Wall clock is used for `published_at_ms`, lease `expires_at_ms` (operator-facing), and emulated etag identity. That split is intentional: fence/request must include VM-suspend time; published_at is a DateTime.
- `old_parts_lifetime` / `grabOldParts` still use in-memory `remove_time`, not disk mtime.

## Closed-since-2026-08-12
- Emulated same-mtime-quantum token collision (CAS-067 first half): `emuMintToken` bumps a per-key disambiguator when a write lands in the same etag (`CasObjectStorageBackend.cpp:542-551`).
- "Fence and request use different clocks" (CAS-092 second half): refuted at HEAD; both use `boot_ms_fn` / `CLOCK_BOOTTIME`.

## Coverage
- Reviewed: `getLastModified` vs `getFileSize`; published_at source; fence/request/renew clocks; `CLOCK_BOOTTIME` portability; emulated token mint/prune; setLastModified.
- N-A: production multi-node emulated tokens (mode is single-process / tests).
- Deferred: FREEZE-with-same-name stamp merge (CAS-086 residual; not a clock bug).
