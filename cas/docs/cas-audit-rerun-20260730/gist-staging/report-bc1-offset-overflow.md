# bc1-offset-overflow — re-run 2026-07-30

## Scope in current code

- Files/dirs walked:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp` (`getBlobViewPlan`, `readBlobPayload`, `getStorageObjects`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasBlobEnvelopeFormat.{h,cpp}` (envelope encode/decode — replaced the old `CasEnvelope.cpp`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasManifestReader.{h,cpp}` (`locate`, `BlobLocation`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPool.cpp` (`Pool::locate` forwarder)
  - `src/IO/ReadBufferFromFileView.{h,cpp}` (windowed read buffer — bounds/seek/resize)

## Findings still present

### `CAS-039` (BC1-1) — **FIXED**, see below

### `CAS-095` (merged BC1-2 / BC1-3 / BC1-4) — Fragile read-window arithmetic — 🔴 still-present (all three sub-patterns unchanged)

**BC1-2 — `resizeWorkingBuffer` size_t-underflow-then-signed-cast**
- Anchor: `src/IO/ReadBufferFromFileView.cpp:169-179` (`ReadBufferFromFileView::resizeWorkingBuffer`)
- Trigger: `working_buffer.size() < extra_bytes` — underflow relied on to yield a value `> 2^63` so the `Int64` cast turns negative and `std::max(., 0)` returns 0.
- Evidence quote:

```169:179:src/IO/ReadBufferFromFileView.cpp
void ReadBufferFromFileView::resizeWorkingBuffer()
{
    if (file_offset_of_buffer_end > getRightBound())
    {
        size_t extra_bytes = file_offset_of_buffer_end - getRightBound();
        size_t new_size = std::max(static_cast<Int64>(working_buffer.size() - extra_bytes), static_cast<Int64>(0));

        working_buffer.resize(new_size);
        file_offset_of_buffer_end = getRightBound();
    }
}
```
- Notes: byte-identical to the original audit's quote. A straightforward `size > extra ? size - extra : 0` remains an obviously-correct fix.

**BC1-3 — `SEEK_CUR` negative-offset underflow caught only by downstream impl bound check**
- Anchor: `src/IO/ReadBufferFromFileView.cpp:104-135` (`ReadBufferFromFileView::seek`)
- Trigger: `new_pos = current_position + off` with `new_pos` a `size_t` and `off` signed `off_t`; a negative `off` larger than `current_position` underflows to a huge value. Correctness rests on `impl->seek(huge, SEEK_SET)` returning the huge value (rejected by the following `[left_bound, right_bound]` check) rather than clamping/succeeding.
- Evidence quote:

```104:129:src/IO/ReadBufferFromFileView.cpp
off_t ReadBufferFromFileView::seek(off_t off, int whence)
{
    size_t new_pos = 0;
    size_t current_position = file_offset_of_buffer_end - (working_buffer.end() - pos);

    if (whence == SEEK_CUR)
        new_pos = current_position + off;
    else if (whence == SEEK_SET)
        new_pos = left_bound + off;
    ...
    if (static_cast<size_t>(result) < left_bound || static_cast<size_t>(result) > right_bound)
        throw Exception(ErrorCodes::SEEK_POSITION_OUT_OF_BOUND, ...);
```
- Notes: unchanged since the original audit; a local `if (off < 0 && static_cast<size_t>(-off) > current_position) throw ...` would make the guard local instead of implicit.

**BC1-4 — Blob view plan trusts manifest `length` (and now-constant offset) without validating vs real object size**
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasManifestReader.cpp:144-168` (`CasManifestReader::locate`) + `.../ContentAddressedMetadataStorage.cpp:1886-1921` (`getBlobViewPlan`) + `.../ContentAddressedMetadataStorage.cpp:1923-1933` (`readBlobPayload`).
- Trigger: `plan.payload_end = location.offset + location.length` and `StoredObject(..., location.offset + location.length)` are unguarded uint64 additions where `location.length = entry.blob_size` comes straight from the (untrusted) `ManifestEntry`; no HEAD-vs-plan cross-check.
- Evidence quotes:

```144:161:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasManifestReader.cpp
BlobLocation CasManifestReader::locate(const ManifestEntry & entry) const
{
    switch (entry.placement)
    {
        case EntryPlacement::Blob:
        {
            return BlobLocation{
                .key = layout.blobKey(entry.ref),
                .offset = meta.blob_header_len,
                .length = entry.blob_size,
            };
        }
```

```1907:1918:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp
    if (const auto * entry = view->findFile(r->file))
    {
        const auto location = snap.pool->locate(*entry);
        BlobViewPlan plan;
        ...
        plan.object = StoredObject(physicalKey(location.key), path, location.offset + location.length);
        plan.payload_offset = location.offset;
        plan.payload_end = location.offset + location.length;
        return plan;
    }
```
- Notes: the offset half of the original BC1-4 concern is *narrower* now — `location.offset` is the pool-wide constant `meta.blob_header_len` from `CasManifestReader::locate` (no longer a per-entry offset from the manifest). But `location.length` (== `entry.blob_size`) is still manifest-supplied, and the sum still goes to `StoredObject`/`ReadBufferFromFileView` without a real-object HEAD cross-check. A malformed manifest with an oversized `blob_size` still surfaces as a downstream S3 error rather than a crisp fail-closed at resolve time; the uint64 addition itself is unguarded (theoretical overflow with a hostile `blob_size ≈ UINT64_MAX`).

## Findings fixed / no longer reproducible

- `CAS-039` (BC1-1) — Envelope size-consistency check bypassable via `logical_size` uint64 overflow wrap — ✅ fixed by envelope redesign.
  - Anchor for fix: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasBlobEnvelopeFormat.cpp:162-251` (`decodeEnvelopeHeader`) and `.../CasBlobEnvelopeFormat.h:60-95` (`struct EnvelopeHeader`).
  - Reason: the envelope has been redesigned as a JSON header terminated by `'\n'` in a fixed pool-wide pad zone. There is **no `logical_size` field in the header** anymore; `header_len` is *derived* from the `'\n'` position:

```240:248:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasBlobEnvelopeFormat.cpp
        if (c == '\n')
        {
            h.header_len = static_cast<uint32_t>(in.count());
            break;
        }
        if (c != ' ')
            throw Exception(ErrorCodes::CORRUPTED_DATA,
                "CAS blob envelope: non-space byte 0x{:02x} in the header pad zone", ...);
```
  and `decodeEnvelopeHeader`'s signature explicitly discards the object size (`uint64_t /*object_size*/`) — there is no `header_len + logical_size == object_size` invariant left to bypass. The payload length is derived downstream as `object_size - header_len` (per `CasBlobEnvelopeFormat.h:88`), and the payload offset is a pool constant (`meta.blob_header_len`, `256` by default). A short/oversized object thus fails naturally against `blob_header_len` or against S3's real object size rather than through a signed check on an attacker-controlled `logical_size`. Also confirmed by `Pool/CasPartWriteTxn.cpp:345` (`logical_size = hr.size - header_len`, computed *from* the object size on the write side, not carried in the envelope) and by the explicit note in `ContentAddressedTransaction.cpp:726` ("minus the dropped `logical_size`/`logical_hash`").
  - `CAS-095`'s "plan trusts manifest offset/length vs real object size" concern narrows accordingly: `offset` is no longer a manifest field — it is `meta.blob_header_len` — so only `length` (= `entry.blob_size`) remains a manifest-trusted value.

## New findings (not in original audit)

- **NEW-bc1-1** — `Low` — `decodeEnvelopeHeader` discards `object_size` but the payload extent still depends on `object_size >= h.header_len`, which is **not checked here**.
  - Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasBlobEnvelopeFormat.cpp:162` (parameter `uint64_t /*object_size*/`) + `CasBlobEnvelopeFormat.h:88-95` (comment: "payload length is derived downstream as `object_size - header_len`").
  - Trigger: a corrupt/truncated object whose real `object_size < h.header_len` yields a size_t-underflow when a caller computes `object_size - header_len` for the payload length. The envelope decoder no longer sees `object_size` (it's `/*object_size*/`-commented out), so the invariant is enforced only at each *caller* site — a documentation invariant, not a local one. Cheap fix: pass `object_size` through and assert `object_size >= h.header_len` inside `decodeEnvelopeHeader` before returning, so the invariant is guaranteed at the single decode point instead of being scattered.
  - Severity rationale: fail-loud in practice (any downstream ranged read will fail against the real S3 size), but the invariant lives in a comment rather than a check — a mild regression in "local guard" hygiene compared to the old `header_len + logical_size == object_size` explicit assertion.

- **NEW-bc1-2** — `Info` — `getBlobViewPlan`'s `StoredObject(..., location.offset + location.length)` and `readBlobPayload`'s identical expression are duplicated; the second is not covered by the plan's would-be validation if BC1-4 is ever tightened.
  - Anchor: `.../ContentAddressedMetadataStorage.cpp:1915` and `:1930`.
  - Trigger: two independent sites compute `offset + length` for the object read-until size; adding a size check in `getBlobViewPlan` alone would still leave `readBlobPayload` computing the same unchecked sum on any direct call path (currently there's only one live caller of `readBlobPayload`, but it's public on the class).
  - Notes: purely a hygiene/DRY note — factor `location.readEnd()` on `BlobLocation` with a single overflow-guarded add.

## By-design / N/A / info

- **BC1-5** (Info in original) — FileView bound checks + exception-safe buffer-swap restore — still correct.
  - `setReadUntilPosition` still rejects `left_bound + position > right_bound` (`ReadBufferFromFileView.cpp:38-44`).
  - `seek` still rejects results outside `[left_bound, right_bound]` (`ReadBufferFromFileView.cpp:124-129`).
  - `executeWithOriginalBuffer` still restores the swap on exception with the explicit "serve wrong bytes" comment (`ReadBufferFromFileView.cpp:137-162`). ✅

- **BC1-6** (Info in original) — 64-bit-only arithmetic; no 32-bit truncation concern. Unchanged; all offset/size arithmetic remains `size_t`/`uint64_t`.

- The old `Cas::isPartFilePath` / `route()` / `poolAccess()` snapshot pattern in `getBlobViewPlan` is genuinely well-formed: one snapshot for both the manifest lookup and `pool->locate` avoids straddling mount generations (see `ContentAddressedMetadataStorage.cpp:1900-1903`). ✅

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-039 (BC1-1) | Med | ✅ fixed | `CasBlobEnvelopeFormat.cpp:162,240-248` — `logical_size` removed from envelope; `header_len` derived from `'\n'`; the size-consistency invariant it tried to enforce no longer exists (payload length = `object_size - header_len`). |
| CAS-095 / BC1-2 | Low | 🔴 still-present | `ReadBufferFromFileView.cpp:169-179` — size_t-underflow-then-signed-cast unchanged. |
| CAS-095 / BC1-3 | Low | 🔴 still-present | `ReadBufferFromFileView.cpp:104-129` — `SEEK_CUR` negative underflow caught only by downstream `[left_bound, right_bound]` check. |
| CAS-095 / BC1-4 | Low | 🔴 still-present (narrower) | `CasManifestReader.cpp:144-161` + `ContentAddressedMetadataStorage.cpp:1915-1917`,`:1930` — `location.length = entry.blob_size` (manifest-trusted) flows into unguarded `offset + length`; `offset` half is now a pool constant. |
| BC1-5 | Info | ✅ still correct | `ReadBufferFromFileView.cpp:38-44,124-129,137-162`. |
| BC1-6 | Info | ✅ still correct | 64-bit arithmetic throughout. |
| NEW-bc1-1 | Low | 🟡 new | `CasBlobEnvelopeFormat.cpp:162` + `CasBlobEnvelopeFormat.h:88-95` — `object_size >= h.header_len` invariant lives in a comment, not a local check. |
| NEW-bc1-2 | Info | ⚪ info | `ContentAddressedMetadataStorage.cpp:1915,1930` — `offset + length` duplicated across `getBlobViewPlan`/`readBlobPayload`. |
