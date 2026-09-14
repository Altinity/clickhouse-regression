# New findings (compact)

| ID | Sev | Title |
|---|---|---|
| NEW-AD1-1 | Low | `blob_hash_allow_new` semantics are dedup-fracturing by design. |
| NEW-AD1-2 | Info | `payload_digest` is hardcoded to CityHash128 regardless of pool algo. |
| NEW-AD1-3 | Info | CAS-025 fix incidentally lands here. `Formats/CasPartManifestFormat.cpp:293-301` now re-computes `payload_digest` on `decodePartManifest` and throws `CORRUPTED_DATA` on mismatch. Original AD1 audit predates this; belongs to `bc4-protobuf-decode` / integrity family. |
| NEW-ad2-1 | High for compliance | `isBucketVersioningEnabled()` unknown → mount proceeds. |
| NEW-ad2-2 | Med | versioning precondition is GCS-only; S3 versioning / object-lock / CRR / soft-delete not checked. |
| NEW-ad2-3 | Med | no post-`deleteExact` verification anywhere in the pipeline. |
| NEW-ad2-4 | Med | `SYSTEM CONTENT ADDRESSED FORGET` explicitly documents "erasure NOT verified". |
| NEW-ad2-5 | Low | `gc_snap_generations_to_keep` retention floor is uncapped by wall-clock. |
| NEW-ad3-1 | Low | SQL fsck cannot bound its runtime. `Cas::runFsck` accepts a `deadline` and a `partial_on_deadline` flag (`CasFsck.h:148-150`), but `runContentAddressedFsck` in `InterpreterSystemQuery.cpp:2524-2551` never plumbs the query-level `max_execution_time` / an explicit `DEADLINE '...'` clause into it. An operator running `SYSTEM CONTENT ADDRESSED FSCK` against a large / slow pool has no way to say "give me what you have after 10 min"; the scan runs to completion or throws `TIMEOUT_EXCEEDED` from `checkDeadline` (`CasFsck.cpp:43-48`). |
| NEW-ad3-2 | Low | `SYSTEM CONTENT ADDRESSED GC STOP` truthfully-but-misleadingly reports `is_leader`. |
| NEW-ad3-3 | Low | `SYSTEM CONTENT ADDRESSED FORGET` explicitly does not verify erasure. |
| NEW-ad3-4 | Info | `Nullable` peer-row columns in `content_addressed_mounts` are a good pattern to keep. |
| NEW-MIG-1 | Med | CAS-041 explicit sub-case: CAS → CAS same-pool MOVE does NOT relink; it byte-copies through streaming reads+writes. |
| NEW-MIG-2 | Med | CAS-210 confirmed: HEAD-first "dedup on landing" trusts backend object identity by NAME only; no body re-hash verify. |
| NEW-MIG-3 | Med | provenance envelope field is present but NOT driven by the operation kind; every fresh CAS write hardcodes `ProvenanceOp::Insert`. |
| NEW-MIG-4 | Low | off-CAS MOVE reads never re-verify blob against manifest/BLAKE hash — INT-1 exposure at migration boundary is symmetric with NEW-MIG-2. |
| NEW-ad5-1 | Med | the manifest write path is hard fail-closed only; no smoothing at all near the caps. |
| NEW-ad5-2 | Low | `enforceRefTableCacheBudget` LRU-evicts a namespace's cached state; a hot table churning enough to force re-hydration under memory pressure pays repeated recovery cost. |
| NEW-ad5-3 | Low | `RefLog` / `RefSnapshot` seal-decode ceilings are 64 MiB decompressed and enforced at decode, but the encode-side complete-table admission uses the same 64 MiB budget with only `kRefAdmissionSafetyMargin` headroom — essentially zero real slack. |
| NEW-AD6-1 | Low | GCS-versioning precondition treats "cannot verify" as fail-open by design, but the log level is `LOG_WARNING` inside `checkPoolPreconditions`, which many operators filter out at aggregation. |
| NEW-AD6-2 | Info | `Pool/CasPool.cpp:1327` bakes the "S3 strongly consistent since 2021" assumption in a comment, without a runtime capability check or a documented supported-backends matrix (RustFS is explicitly listed as unverified in the same comment). |
| NEW-ad7-1 | Info | `assertEOF` after `readStringBinary(sender_manifest_bytes)` will hard-fail any future v2-with-trailer sender talking to this exact v2 receiver. |
| NEW-ad7-2 | Info | Cookie-value gate happens BEFORE the pool-uuid re-check, but AFTER `ca_relink` cookie parse — an empty cookie value on the wire is silently treated as "no relink" rather than as a malformed offer. |
| NEW-ad7-3 | Info | `locate()` does not read the envelope's own `header_len` before ranging — soft coupling to pool_meta's `blob_header_len` invariant. |
| NEW-bc1-1 | Low | `decodeEnvelopeHeader` discards `object_size` but the payload extent still depends on `object_size >= h.header_len`, which is **not checked here**. |
| NEW-bc1-2 | Info | `getBlobViewPlan`'s `StoredObject(..., location.offset + location.length)` and `readBlobPayload`'s identical expression are duplicated. |
| NEW-BC2-7 | Low | `SCOPE_EXIT`-only cleanup covers throw but not a survivor if `stageBlobPartFile` succeeds and a later transaction step throws (inline-overflow branch). |
| NEW-BC2-8 | Low | envelope header pre-write is not covered by the streaming-size sanity check in S3 staging. |
| NEW-BC2-9 | Info | inline-overflow bounded but still holds full bytes in memory before spill. |
| NEW-bc4-protobuf-decode-1 | Info | `Backend/CasBackend.h:219` has a stale doc comment referring to the deleted `RunFileReader`. |
| NEW-bc4-protobuf-decode-2 | Info | `ShardCoverage::classification` is decoded as an unvalidated `uint8_t` (`Formats/CasFoldSealFormat.cpp:189`). |
| NEW-BC7-1 | Med | Asymmetric fix: replicated write paths use the `renameParts()` off-lock publish, but plain-MergeTree paths (`MergeTreeSink.cpp:379`, `MutatePlainMergeTreeTask.cpp:134`, `MergePlainMergeTreeTask.cpp:160`) still publish under `DataPartsLock`. |
| NEW-BC7-2 | Low | Belt-and-suspenders duplication: after `renameParts()` (`MergeTreeData.cpp:8986-8988`) runs the publish loop, the identical `commitTransaction()` loop inside `commit()` (`MergeTreeData.cpp:9008-9010`) is guarded only by `hasActiveTransaction()`. |
| NEW-codeonly-line-1 | Low | Non-cryptographic checksum still trusted on run objects, now under `CityHash128`-of-object-body — `Formats/CasRecordStreamFormat.cpp:210-219` (`sourceEdgeRunChecksum`). |
| NEW-codeonly-line-2 | Info | Envelope pad-zone now enforces "must be ASCII space up to '\n'" — `CasBlobEnvelopeFormat.cpp:230-248`. |
| NEW-codeonly-line-3 | Low | `PartWriteTxn::adoptEvidence` records the sender-supplied `entry.blob_size` in `deps[entry.ref]` and then verifies only that a blob exists in `promote`. |
| NEW-codeonly-line-4 | Info | `checkNamespace` is now also called on operator-supplied `server_root_id`-derived subpaths via a wide surface (`refsNamespacePrefix`, `manifestNamespacePrefix`, `namespaceFileKey`, `namespaceFilesPrefix`). |
| NEW-datatype-agnosticism-1 | Info | original audit's Layer 1 quote used `UInt128 blob_hash{}`. |
| NEW-datatype-agnosticism-2 | Info | original audit's edge-case table noted mutable per-part files (`uuid.txt`/`txn_version.txt`/`metadata_version.txt`) were kept out of the content manifest. |
| NEW-datatype-agnosticism-3 | Info | the only place CAS inspects a file's name to alter behavior is `Cas::partFileMustStayBlob` (`ContentAddressedTransaction.cpp:65-73`) which handles `primary.idx`/`.bin`/`.mrk*`/`.cmrk*`. |
| NEW-jepsen-1 | Med — observability/operability | Post-write fence-loss surfaces as `Unresolved`, never `Committed`; but the durable object may exist and be visible to other mounts. |
| NEW-jepsen-2 | Low — soft-vs-hard fence | `fenceGeneration` admission covers the durable-effect blob finalize path only for `ContentAddressedTransaction::writeFile`; the ref-append lane relies on `fence_ok_fn` (boolean) rather than a captured generation token. |
| NEW-jepsen-3 | Med-High | X1/R1 reader pin gap surface is unchanged; the refactor added no reader-side coupling to GC's ack floor. |
| NEW-read-1 | Med, liveness | `readManifestShared` HEAD-GET race window amplifies dangle. |
| NEW-read-2 | Low, coverage | Retained-view age policy uses wall-clock `now_ms_fn()` (`PartFolderAccess.cpp:203`) subtracted from `cached->validatedAtMs()`. |
| NEW-read-3 | Info | `CachedPartFolderAccess::buildView` single-flight drops leader exceptions onto every follower (`l.301: promise.set_exception`). |
| NEW-security-1 | Med — default-hardening | `BlobHashAlgo` default is `CityHash128`. |
| NEW-security-2 | Low — clean-shutdown | `Xxh3128BlobHashingWriteBuffer::finalizeImpl` is not overridden; `getHashHex` calls `next()` but skips `finalize()`, and the class also lacks a `cancelImpl`. |
| NEW-security-3 | Low — defense in depth | `_pool_meta` / `_manifests` / `_files` reserved-segment gate does not include the newer reserved prefixes in the `roots/` and `blobs/` trees. |
| NEW-security-4 | Low | `mountpointObjectKey` and `checkNamespace` accept single-character segments `.` and `..` (sub-finding of CAS-074, called out separately for the mountpoint path). |
| NEW-TCF-1 | Med | no GCS-backed integration test despite `utils/ca-soak/docker-compose-gcs.yml` being present. |
| NEW-TCF-2 | Low | `ca-soak/scenarios/` is model/checker-oriented but has no explicit **MOVE / RESTORE / quorum** cards even though it has multi-replica infra (`docker-compose-10replicas.yml`). |
| NEW-TCF-3 | Info | `gtest_cas_ref_decode_bounds.cpp` exists and is a natural seed corpus for a `cas_ref_decode_fuzzer`. |
| NEW-tier2-1 | Low, cache/observability | page memory cache key prefix disk-scopes CAS blob dedup. |
| NEW-tier2-2 | Low, system-tables gap | no CAS view of pool-level counters despite `CasFsck` numbers. |
| NEW-tier2-3 | Low, TTL/tiering | no move-path hook to short-circuit CAS→CAS same-pool moves. |
| NEW-tier3-1 | Low, feature-gap-with-safety-note | `moveFile` on committed non-part files throws `LOGICAL_ERROR` when the source is not staged in this transaction. |
| NEW-tier3-2 | Low, robustness | cross-namespace `moveDirectory` (RENAME TABLE) is documented as best-effort, non-atomic, idempotent-on-retry but has no in-call compensation. |
| NEW-tier3-3 | Info | Same-pool same-disk `moveDirectory` for part-dirs is a pure metadata `republishRef` (`ContentAddressedTransaction.cpp:1370`), i.e. |
| NEW-tier4-1 | Low, test-coverage | FETCH-to-detached relink correctness has code but no dedicated integration test. |
| NEW-tier4-2 | Low, test-coverage | RENAME TABLE / cross-engine table move on CAS is best-effort non-atomic and the "SPLIT across namespaces" recovery path is idempotent by construction, but no integration test injects a fault between the `republishRef` loop and `dropNamespace` and asserts idempotent re-drive. |
| NEW-tier4-3 | Low, observability | a `CasBlobAdoptTrusted` ProfileEvent (`src/Common/ProfileEvents.cpp:900`) partially closes the original OBS-3 gap (relink hit-rate is measurable at the "adoption" level), but there is still no counter distinguishing a **relink fetch** from a **byte fetch** in the replication log (`system.replicated_fetches` bytes-transferred remains the only signal). |
| NEW-upgrade-compat-1 | Med | `changePoints()` history stayed frozen at `{{1,1}}` across two `G_BUILD` bumps. |
| NEW-upgrade-compat-2 | Low | backward pool-meta floor is a hard `< 3` gate, no operator override. |
| NEW-upgrade-compat-3 | Low | tolerant-key silent-drop has no per-generation "critical additive" mechanism. |
| NEW-upgrade-compat-4 | Info | pool-meta admission ratchets `min_reader_generation` irreversibly on any new-algo union. |
| NEW-upgrade-compat-5 | Info | no LE-only build assertion. No occurrence of `std::endian::native` / `__BYTE_ORDER__` / `static_assert` guarding LE-only in `MetadataStorages/ContentAddressed/**`. Explicit-BE wire codec covers CAS's own bytes, but the underlying `CityHash128` implementation is not audited BE-safe. Cheap one-liner recommendation.** |
| NEW-write-1 | Low, LEAK/OBSERV | `CaContentWriteBuffer::finalizeImpl` sets `temp_ownership_transferred = true` (line 1845) even after `on_finalized` throws in the tail of that lambda, because the flag is set after the callback. |
| NEW-write-2 | Low, CORRECTNESS/COMPAT | `CaContentWriteBuffer::finalizeImpl` reports the payload size via `count()` (line 1822), which is the byte count of what THIS buffer forwarded to `hashing`. |
| NEW-write-3 | Low, LIVENESS/PERF | `ContentAddressedTransaction::moveDirectory`'s RENAME-TABLE branch (`:1231–1249`) does `for (const auto & [ref, _] : store->listRefs(from_ns))` and calls `republishRef(...)` per ref, then `putNamespaceFile` per verbatim file, then `dropNamespace(from_ns)`. |
