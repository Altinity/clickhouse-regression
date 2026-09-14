# bc2-writebuffer-spill — re-run 2026-07-30

Re-verification of the BC-2 write-buffer / temp-file spill audit against the current PR HEAD
(`/Volumes/workspace/ClickHouse`, branch `cas-audit-20260730`, tracks `altinity/cas-gc-rebuild`).
Original findings BC2-1 … BC2-6 (rolled up into `CAS-038` "temp un-fsynced & not verified vs
key" and `CAS-096` "scratch-FS full late, temp uniqueness random-only"). Static reasoning only.

## Scope in current code

- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.h` — declarations
  of `CaContentWriteBuffer` (Local + S3-staging ctors) and `CaInlineWriteBuffer` (lines ~283–418).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp` —
  bodies (`CaContentWriteBuffer` ctor/dtor/nextImpl/finalizeImpl/cancelImpl/removeTempFile/sync,
  lines 1739–1914), `writeFile` blob-vs-inline dispatch (lines 793–974), `stageBlobPartFile`
  (702–721), `uploadPendingBlobs` (256–311), `cleanupPendingTempFiles` (165–210), the S3 staging
  header helper `buildS3StagingBlobHeader` (723–746).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Primitives/CasBlobHashingWriteBuffer.{h,cpp}`
  — the pluggable `IBlobHashingWriteBuffer` that wraps the sink for `CityHash128` / `XXH3_128` / `Sha256`.
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp` — the
  actual upload primitive `uploadFromSource` / `streamIfAbsent` (lines 553–625), showing what is
  and is not verified about the streamed payload.

Structural changes since the original audit:

1. The hash algorithm is now selected per-pool (`writeAlgo() ∈ {CityHash128, XXH3_128, Sha256}`)
   and the streaming buffer is built by `Cas::makeBlobHashingWriteBuffer`. The Local ctor path
   is byte-for-byte compatible for `CityHash128`.
2. A **second constructor** on `CaContentWriteBuffer` supports **S3-native staging**: the buffer
   streams directly into a caller-supplied S3 sink at a staging key, prefixed with an unhashed
   `envelope_header` (CABL header carrying a fresh `incarnation_tag`). Promote is a server-side
   copy at commit — no local temp file, no round-trip through the scratch FS on this path.
3. `stageBlobPartFile` records a `PartStaging::PendingBlob{ref, staging_key, size, backend}`
   where `backend ∈ {Local, S3}`. The upload (`uploadPendingBlobs` → `fanOutBlobUploads` →
   `uploadFromSource`) picks the primitive: for Local it re-reads the temp file via `copyData`
   and streams into `putIfAbsentStream`; for S3 it uses `promoteStaged` (server-side copy).

The single-blob upload primitive verifies **only** `written == source.size` after `write_payload`
(`CasPartWriteTxn.cpp:600–602`); nothing re-hashes the streamed bytes against `ref`.

## Findings still present

### CAS-038 (BC2-1 + BC2-2 combined) — Uploaded blob is still never re-verified against its content-hash key, and the scratch temp file is still not `fsync`ed on `finalize`

- **Anchor (Local path, un-verified upload)**: `src/Disks/.../Pool/CasPartWriteTxn.cpp:594–602`
  (`streamIfAbsent` in `uploadFromSource`) — the S3 PUT streams header + `source.write_payload(out)`
  and checks only `written == source.size`; no hash recompute.
- **Anchor (Local path, `write_payload` re-reads temp)**: `ContentAddressedTransaction.cpp:293–298`
  in `uploadPendingBlobs`:

  ```cpp
  source.write_payload = [staging_key](WriteBuffer & out)
  {
      ReadBufferFromFile in(staging_key);
      copyData(in, out);
  };
  ```

  This is exactly the "read the unverified temp file and PUT it" pattern the original audit
  flagged. Nothing between the hash (done inside `CaContentWriteBuffer::finalizeImpl`) and the
  eventual PUT re-hashes those bytes.
- **Anchor (fsync absent)**: `ContentAddressedTransaction.cpp:1819–1837`
  (`CaContentWriteBuffer::finalizeImpl`) — the sequence is `next(); size=count();
  hash=hashing->getHashHex(); hashing->finalize(); (fence check for S3); sink->finalize();
  on_finalized(hash_hex, size, temp_path);`. `finalize()` flushes to the OS but does **not**
  call `fsync`. A separate `sync()` method exists (line 1869) that forwards to `sink->sync()`,
  but it is not invoked from `finalizeImpl`, and no caller invokes it between finalize and the
  post-precommit re-read. The `WriteBufferFromFile` sink is opened with default flags (`flags=-1`,
  no `O_SYNC`, no `O_DIRECT` — line 1757), so bytes live in the page cache until evicted.
- **Trigger**: any scratch-FS-level corruption / short-write / silent bit flip / page-cache loss
  between the moment `getHashHex` folds bytes into the digest and the moment `copyData` reads
  the file back for PUT. `hashing->getHashHex()` returns the digest of the *submitted* bytes;
  `sink->finalize()` after it only flushes what those bytes reached in the OS. The uploaded
  object is keyed by the pre-flush hash but the bytes uploaded are whatever the re-read produces.
- **Evidence quote** (from the code, `CaContentWriteBuffer::finalizeImpl`):

  ```43:56:… (paraphrasing lines 1819–1846)
  next();
  const size_t size = count();
  const std::string hash_hex = hashing->getHashHex();   // hash of bytes SUBMITTED
  hashing->finalize();
  if (check_fence_before_finalize) check_fence_before_finalize();  // S3-only fence recheck
  sink->finalize();                                    // OS flush; NOT fsync
  if (on_finalized) { on_finalized(hash_hex, size, temp_path); temp_ownership_transferred = true; }
  ```

- **Notes**:
  - The write path uses **CityHash128 / XXH3_128 / SHA-256** now (via `IBlobHashingWriteBuffer`),
    not just CityHash128. For `Sha256` in particular the original audit's implicit "cheap
    mitigation" (rehash on upload) is genuinely cheap; the Local-mode `write_payload` closure at
    line 293–298 could re-wrap the `ReadBufferFromFile` in a `HashingReadBuffer` and compare
    against `pb.ref` before returning. It doesn't.
  - The `S3`-staging Local-mode analogue (`server_side_copy_from`) does NOT go through a re-read
    at all — it's a server-side S3 copy — so BC2-1 does not apply to that path (see "By-design"
    below). But **the vast majority of installs will still run Local mode**: S3 staging is off by
    default and additionally gated on a mount-time conditional-copy capability probe
    (`writeFile` at line 873: `stagingBackend() == Cas::StagingBackend::S3 &&
    conditionalCopySupported()`). Under the default configuration, BC2-1 and BC2-2 apply in full.
  - The read path still does not re-verify at GET either (BC-5 / INT-1 territory), so this
    integrity gap is not compensated downstream.
  - `check_fence_before_finalize` (rev.7 [C2], line 1834) helps the *fence-generation* liveness
    invariant, not integrity.

### CAS-096 (BC2-3) — Scratch-FS-full still fails late; no pre-flight check; sizing still undocumented

- **Anchor (temp file open)**: `ContentAddressedTransaction.cpp:1749–1763`
  (`CaContentWriteBuffer` Local ctor). `fs::create_directories(temp_dir)` then
  `std::make_unique<WriteBufferFromFile>(temp_path, …)`. No `statvfs`, no `space()`, no size
  hint check against a configured minimum.
- **Anchor (writeFile dispatch)**: `ContentAddressedTransaction.cpp:904–914`. The buffer is
  handed back to the caller unconditionally; a full scratch FS will only surface when a later
  `next()`/`finalize()` hits `ENOSPC`.
- **Anchor (metadata storage)**: `ContentAddressedMetadataStorage.h:381`
  `const std::string & scratchPath() const { return local_scratch_path; }` — still just a
  configured path; no capacity contract, no `min_free_bytes` setting, no runbook.
- **Trigger**: large INSERT with `staging_backend != s3` (default), all wide-part columns spill
  simultaneously to `scratchPath()`. First writer to hit `ENOSPC` throws mid-`finalize`.
- **Evidence quote** (`CaContentWriteBuffer` Local ctor, paraphrased from lines 1749–1763):

  ```
  fs::create_directories(temp_dir);
  temp_path = temp_dir + "/" + getRandomASCIIString(32) + ".tmp";
  sink = std::make_unique<WriteBufferFromFile>(temp_path, …);
  ```

  No preflight; no scratch-quota knob; no dedicated `SCRATCH_FS_FULL` error code
  (a plain write error propagates).
- **Notes**:
  - Same as original — this is a low-severity operational-ergonomics issue, not a correctness
    bug. Fail-closed behavior is preserved (build fails, commit does not run).
  - The **inline-overflow spill path** shares the same shortcoming: line 957–961 does
    `create_directories(scratchPath())` then opens `WriteBufferFromFile(temp_path)` with no
    capacity check. Same anchor class of hazard, wider footprint.

### CAS-096 (BC2-4) — Temp-file uniqueness still relies on `getRandomASCIIString(32)`; still no PID/counter

- **Anchor (Local blob spill)**: `ContentAddressedTransaction.cpp:1750`
  `temp_path = temp_dir + "/" + getRandomASCIIString(32) + ".tmp";`
- **Anchor (inline overflow)**: `ContentAddressedTransaction.cpp:958–959`
  `temp_path = scratchPath() + "/inline_overflow_" + getRandomASCIIString(32) + ".tmp";`
- **Anchor (S3-staging key, extended footprint of the same weakness)**:
  `ContentAddressedTransaction.cpp:875`
  `const std::string staging_key = metadata_storage.stagingKeyPrefix() + "/" + getRandomASCIIString(32) + ".tmp";`
  — the same "32 random ASCII chars" scheme is now also the uniqueness token for the S3
  staging object key. A collision here would put two concurrent builds into the SAME S3 key
  under `WriteMode::Rewrite`; the promote reads one of them by that shared name. Same class of
  silent-corruption vector, now with an off-node blast radius.
- **Trigger**: two concurrent `CaContentWriteBuffer` constructions (either Local or S3) whose
  32-char random suffix collides due to a poorly-seeded / non-thread-safe RNG. Two builds write
  the same file/key, one wins, the other's blob hash names bytes it did not contribute.
- **Evidence quote**: exact `getRandomASCIIString(32)` call sites listed above; no
  process-identity or monotonic-counter component included in either the Local temp path or
  the S3 staging key.
- **Notes**:
  - `getRandomASCIIString` is ClickHouse's thread-local RNG-backed helper; a birthday-argument
    calculation on 32 chars of `[0-9A-Za-z]` (base 62) yields collision probability ~10⁻³² for
    modest concurrency — negligible **iff** the RNG is well-seeded and thread-safe. This is
    still an *assumed* invariant, not enforced by construction.
  - A `pid + monotonic counter` concatenation (or a UUIDv7) would make collision impossible
    without changing the file-name shape.
  - Same guidance as original; new blast radius (S3 staging key) elevates the reasoning weight
    even though the raw probability is unchanged.

## Findings fixed / no longer reproducible

None fixed. The current code retains every hazard flagged in the original audit and inherits
the same shortcomings on the new S3-native staging path (for CAS-096 uniqueness), while
correctly sidestepping BC2-1/BC2-2 in server-side-copy staging mode (see By-design).

## New findings (not in original audit)

- **NEW-BC2-7 (Low, integrity/inline overflow — `SCOPE_EXIT`-only cleanup covers throw but not
  a survivor if `stageBlobPartFile` succeeds and a **later** transaction step then throws)**.
  Anchor: `ContentAddressedTransaction.cpp:952–972`. The inline-overflow branch writes an
  ad-hoc `WriteBufferFromFile tmp(temp_path)` in a local scope, then calls
  `stageBlobPartFile(route, ref, bytes.size(), temp_path, StagingBackend::Local)`, then flips
  the `staged` sentinel to `true` inside the `SCOPE_EXIT` clause. The `SCOPE_EXIT` only removes
  the file when `!staged`. Once `stageBlobPartFile` has recorded the temp path into
  `PartStaging::pending_blobs`, the file's later lifetime is `cleanupPendingTempFiles`. That is
  correct on the happy path AND on the abort path (both branches of
  `cleanupPendingTempFiles` unlink for `StagingBackend::Local`). But note the file has **no
  fsync** either (`WriteBufferFromFile tmp(...); ... tmp.finalize()` — implied). If the same
  BC2-2 page-cache-loss hazard hits the inline-overflow blob (rare — the trigger is a >
  `INLINE_CAP` "inline-candidate" file, so typically small kilobyte-scale), the same silent
  key-vs-bytes divergence applies. Severity: low, but the site was not called out in the
  original audit (which focused on `CaContentWriteBuffer`).

- **NEW-BC2-8 (Low, integrity/S3-staging — envelope header pre-write is not covered by the
  streaming-size sanity check).** Anchor:
  `ContentAddressedTransaction.cpp:1793–1794` and `Pool/CasPartWriteTxn.cpp:594–602`. In S3
  staging mode the buffer emits `envelope_header` directly to the sink (bypassing `hashing`)
  BEFORE the payload starts. If the caller-supplied `WriteBufferFromFileBase` sink accepts the
  header but silently short-writes it (a specific S3 client bug), the staging object holds a
  truncated header + full payload; `promoteStaged` still copies the object verbatim, and
  decode-time header validation fails **at read time**, not at write time. The Local-mode
  upload has the analogous belt-and-suspenders check
  (`written == source.size`, `CasPartWriteTxn.cpp:600`) but that check applies only to the
  payload portion; the header pre-write in the S3-staging constructor has no equivalent guard.
  This is closer to defense-in-depth than a genuine bug — no reasonable
  `WriteBufferFromFileBase` short-writes silently — but it is a code-shape difference from the
  Local path and could paper over an S3-side integration bug.

- **NEW-BC2-9 (Info — inline-overflow bounded but still holds full bytes in memory before
  spill).** Anchor: `ContentAddressedTransaction.cpp:920–971`. Same shape as BC2-6 in the
  original audit, retained in current code. Included here because the actual line numbers /
  code shape changed (a `SCOPE_EXIT`-guarded temp-file spill) and the safety net is still
  post-hoc (the buffer materializes the entire candidate in `std::string accumulated` first,
  then re-emits via a fresh `WriteBufferFromFile` in `writeFile`). A caller misrouting a large
  file to the inline path still pays the full in-memory cost before the streaming spill.

## By-design / N/A / info

- **BC2-1 is BY-DESIGN N/A on the S3-native staging path.** The staging object IS the promote
  source: `uploadFromSource` on this branch executes `promoteStaged(*server_side_copy_from,
  key)` (server-side S3 copy — `CasPartWriteTxn.cpp:587–588`), never a client-side re-read.
  There is no window between "hash bytes in memory" and "PUT those bytes" — the bytes were
  streamed directly into the S3 sink while being hashed, and the promote just copies that
  object server-side. So on **S3 staging mode with `conditionalCopySupported()`**, BC2-1's
  attack surface disappears. BC2-2 also becomes moot on this path (no local file, no scratch
  page cache in the chain). Local mode remains the default and still has the gap.
- **BC2-5 (RAII cleanup) still ✅ correct.** `~CaContentWriteBuffer` (line 1801) calls
  `cancel()` and removes the temp file when ownership was not transferred. `cancelImpl`
  (line 1849) cancels the hashing chain and sink and only skips `removeTempFile` in the
  S3-staging branch (where the "temp_path" is a remote object key, correctly left for the
  mount-lease sweeper). The inline-overflow site uses `SCOPE_EXIT` for the `!staged` guard
  (line 971). `cleanupPendingTempFiles` (line 165) is called from both `commit()` (success)
  and the transaction dtor (failure). No temp-file leaks on any exception path traced.
- **BC2-6 (inline in-memory buffering) — same shape, retained (see NEW-BC2-9 above).**
- **New info: pluggable hash algorithm.** `Cas::makeBlobHashingWriteBuffer` (line 1764)
  makes the write path algorithm-parameterized. This is orthogonal to BC2-1 (still no
  re-verification) but relevant for a future fix: `blobHashHexOneShot` in
  `CasBlobHashingWriteBuffer.cpp:220` is already the exact primitive a Local-mode upload
  re-verification would use — a `HashingReadBuffer` re-hash of the temp file bytes just
  before `copyData` (or streamed in one pass via `HashingReadBuffer` chained into the sink).

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-038 (BC2-1) | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1819–1846` (finalize hands `hash_hex` and `temp_path` with no re-verify) + `Pool/CasPartWriteTxn.cpp:594–602` (upload verifies only size) + `ContentAddressedTransaction.cpp:293–298` (`copyData` re-reads temp) |
| CAS-038 (BC2-2) | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1819–1846` (`sink->finalize()` — no fsync) + `1749–1763` (default flags on `WriteBufferFromFile`) + `1869–1874` (`sync()` exists but is not called from `finalizeImpl`) |
| CAS-096 (BC2-3) | Low | 🔴 still-present | `ContentAddressedTransaction.cpp:1749`, `.cpp:904–914`, `ContentAddressedMetadataStorage.h:381` (no preflight FS-full check; `scratchPath()` capacity contract undocumented) |
| CAS-096 (BC2-4) | Low | 🔴 still-present | `ContentAddressedTransaction.cpp:1750` (Local), `.cpp:958–959` (inline overflow), `.cpp:875` (S3 staging key — new blast radius) — all `getRandomASCIIString(32)` |
| — (BC2-5) | Info | 📐 by-design ✅ | `ContentAddressedTransaction.cpp:1801–1810`, `1849–1861`, `165–210`, `.cpp:971` (SCOPE_EXIT); cleanup is complete |
| — (BC2-6) | Info | ⚪ info (see NEW-BC2-9) | `ContentAddressedTransaction.cpp:1881–1904` — same shape retained |
| NEW-BC2-7 | Low (new) | 🔴 new-finding | `ContentAddressedTransaction.cpp:952–972` (inline-overflow ad-hoc temp is written without fsync; same integrity gap on this less-trafficked path) |
| NEW-BC2-8 | Low (new) | 🔴 new-finding | `ContentAddressedTransaction.cpp:1793–1794` + `Pool/CasPartWriteTxn.cpp:587–602` (S3-staging envelope header pre-write has no short-write guard analogous to the payload size check) |
| NEW-BC2-9 | Info (new) | ⚪ info | `ContentAddressedTransaction.cpp:1892–1897`, `920–971` (inline-overflow bounded but still holds full bytes in memory before spill) |

## Counts

- Original findings re-verified: **6** (BC2-1 … BC2-6).
- Still-present: **4** (BC2-1, BC2-2, BC2-3, BC2-4).
- Fixed: **0**.
- By-design / info retained: **2** (BC2-5 ✅, BC2-6 info).
- New findings this run: **3** (NEW-BC2-7, NEW-BC2-8, NEW-BC2-9).
- CAS ids status: `CAS-038` = 🔴 still-present; `CAS-096` = 🔴 still-present.
