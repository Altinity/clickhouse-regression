"""Pure-Python Puffin file and deletion-vector blob builder.

Implements just enough of two formats to build both valid and deliberately
hostile inputs for the error-handling requirements:

* the `Puffin file format <https://iceberg.apache.org/puffin-spec/>`_::

      Magic Blob₁ ... Blobₙ Footer
      Footer = Magic FooterPayload FooterPayloadSize(LE u32) Flags(4) Magic

  where FooterPayload is the FileMetadata JSON (uncompressed here);

* the Iceberg v3 ``deletion-vector-v1`` blob layout::

      len(BE u32, of magic+vector) | magic D1 D3 39 64 | vector | crc(BE u32)

  where ``vector`` is a 64-bit roaring bitmap in the "portable" format
  (LE u64 bucket count, then per bucket: LE u32 high key + standard 32-bit
  roaring serialization) and ``crc`` is CRC-32 of magic+vector.

Every builder takes override knobs so a single defect (wrong magic, bad CRC,
truncated bitmap, unsorted keys, ...) can be injected while the rest of the
file stays valid — a query must fail for exactly the injected reason.
"""

import json
import struct
import zlib

PUFFIN_MAGIC = b"PFA1"
DV_MAGIC = bytes([0xD1, 0xD3, 0x39, 0x64])
DV_BLOB_TYPE = "deletion-vector-v1"
# Iceberg's reserved _pos field id — compliant writers declare a DV blob as
# computed over the row-position column
DV_POSITION_FIELD_ID = 2147483645

SERIAL_COOKIE_NO_RUNCONTAINER = 12346
SERIAL_COOKIE = 12347  # run-container format
ARRAY_CONTAINER_MAX_CARDINALITY = 4096
BITSET_CONTAINER_SIZE = 8192  # 1024 x u64
NO_OFFSET_THRESHOLD = 4  # run format omits the offset header below this


def _array_body(values):
    return b"".join(struct.pack("<H", value) for value in values)


def _bitset_body(values):
    words = [0] * 1024
    for value in values:
        words[value >> 6] |= 1 << (value & 63)
    return struct.pack("<1024Q", *words)


def _runs_of(values):
    """Sorted values → list of (start, length) runs."""
    runs = []
    for value in values:
        if runs and value == runs[-1][0] + runs[-1][1]:
            runs[-1][1] += 1
        else:
            runs.append([value, 1])
    return runs


def _run_body(runs):
    return struct.pack("<H", len(runs)) + b"".join(
        struct.pack("<HH", start, length - 1) for start, length in runs
    )


def build_bitmap32(values, cardinality_overrides=None, container_order=None):
    """Serialize a 32-bit roaring bitmap in the no-run portable format.

    The portable format infers a container's type from its declared
    cardinality, so the body follows the same rule the reader applies:
    array (sorted u16 values) up to 4096 values per 16-bit chunk, bitset
    (8 KiB fixed) above.

    Args:
        values: iterable of uint32 values.
        cardinality_overrides: optional dict {container_key: fake_cardinality}
            to declare a cardinality different from the stored values
            (containers extending past the blob, internal-validation errors).
        container_order: optional explicit list of container keys to control
            the descriptive-header order (unsorted containers).
    """
    containers = {}
    for value in values:
        containers.setdefault(value >> 16, []).append(value & 0xFFFF)

    keys = container_order if container_order is not None else sorted(containers)

    header = struct.pack("<II", SERIAL_COOKIE_NO_RUNCONTAINER, len(keys))
    descriptive = b""
    bodies = []
    for key in keys:
        container_values = sorted(containers[key])
        cardinality = len(container_values)
        if cardinality_overrides and key in cardinality_overrides:
            cardinality = cardinality_overrides[key]
        descriptive += struct.pack("<HH", key, (cardinality - 1) & 0xFFFF)
        if len(container_values) > ARRAY_CONTAINER_MAX_CARDINALITY:
            bodies.append(_bitset_body(container_values))
        else:
            bodies.append(_array_body(container_values))

    offset_header = b""
    offset = len(header) + len(descriptive) + 4 * len(keys)
    for body in bodies:
        offset_header += struct.pack("<I", offset)
        offset += len(body)

    return header + descriptive + offset_header + b"".join(bodies)


def build_bitmap32_with_runs(values):
    """Serialize a 32-bit roaring bitmap in the run-format portable layout
    (cookie 12347). Per container the body type follows the space rule real
    writers apply — run when it beats the alternative, else array or bitset
    by cardinality — so mixed-container bitmaps arise naturally from the
    value distribution."""
    containers = {}
    for value in values:
        containers.setdefault(value >> 16, []).append(value & 0xFFFF)

    keys = sorted(containers)
    count = len(keys)

    run_flags = bytearray((count + 7) // 8)
    descriptive = b""
    bodies = []
    for index, key in enumerate(keys):
        container_values = sorted(containers[key])
        cardinality = len(container_values)
        runs = _runs_of(container_values)
        run_size = 2 + 4 * len(runs)
        plain_size = (
            BITSET_CONTAINER_SIZE
            if cardinality > ARRAY_CONTAINER_MAX_CARDINALITY
            else 2 * cardinality
        )
        descriptive += struct.pack("<HH", key, cardinality - 1)
        if run_size < plain_size:
            run_flags[index // 8] |= 1 << (index % 8)
            bodies.append(_run_body(runs))
        elif cardinality > ARRAY_CONTAINER_MAX_CARDINALITY:
            bodies.append(_bitset_body(container_values))
        else:
            bodies.append(_array_body(container_values))

    data = struct.pack("<HH", SERIAL_COOKIE, count - 1) + bytes(run_flags) + descriptive
    if count >= NO_OFFSET_THRESHOLD:
        offset = len(data) + 4 * count
        for body in bodies:
            data += struct.pack("<I", offset)
            offset += len(body)
    return data + b"".join(bodies)


def build_roaring64(
    positions=None,
    buckets=None,
    bucket_count=None,
    truncate_at=None,
    trailing=b"",
):
    """Serialize a 64-bit roaring bitmap in the portable format.

    Args:
        positions: iterable of uint64 row positions (split into 32-bit
            buckets automatically). Mutually exclusive with *buckets*.
        buckets: explicit list of ``(high_key, bitmap32_bytes)`` pairs for
            full control (unsorted keys, hostile keys, corrupt containers).
        bucket_count: override the declared LE u64 bucket count.
        truncate_at: cut the serialized bitmap to this many bytes
            (truncation mid-key / mid-container).
        trailing: extra bytes appended after the last container.
    """
    if buckets is None:
        grouped = {}
        for position in positions or []:
            grouped.setdefault(position >> 32, []).append(position & 0xFFFFFFFF)
        buckets = [
            (high, build_bitmap32(values)) for high, values in sorted(grouped.items())
        ]

    count = bucket_count if bucket_count is not None else len(buckets)
    data = struct.pack("<Q", count)
    for high_key, bitmap in buckets:
        data += struct.pack("<I", high_key) + bitmap

    if truncate_at is not None:
        data = data[:truncate_at]

    return data + trailing


def build_dv_payload(
    positions=None,
    vector=None,
    magic=DV_MAGIC,
    combined_length=None,
    crc=None,
    raw=None,
):
    """Build the bytes of one ``deletion-vector-v1`` blob.

    Args:
        positions: row positions to delete (used when *vector* not given).
        vector: pre-serialized (possibly corrupt) 64-bit roaring bitmap.
        magic: 4-byte magic sequence (override to inject a wrong magic).
        combined_length: override the declared BE u32 length of magic+vector.
        crc: override the BE u32 CRC-32 of magic+vector.
        raw: return exactly these bytes (blob-too-small defects).
    """
    if raw is not None:
        return raw

    if vector is None:
        vector = build_roaring64(positions=positions or [])

    combined = magic + vector
    if combined_length is None:
        combined_length = len(combined)
    if crc is None:
        crc = zlib.crc32(combined) & 0xFFFFFFFF

    return struct.pack(">I", combined_length) + combined + struct.pack(">I", crc)


def build_puffin(
    blobs,
    file_properties=None,
    compress_footer=False,
    store_content_size=True,
    flags=None,
):
    """Build a complete Puffin file.

    Args:
        blobs: list of dicts with keys:
            ``payload`` (bytes, required),
            ``properties`` (blob properties, e.g. referenced-data-file,
            cardinality), ``type`` (default deletion-vector-v1),
            ``fields``, ``snapshot_id``, ``sequence_number``,
            ``compression_codec`` (added to metadata only when set),
            ``offset`` / ``length`` (override the footer-declared location).
        file_properties: optional file-level properties dict.
        compress_footer: LZ4-compress the FooterPayload (a single frame)
            and set the footer compression flag bit.
        store_content_size: whether the LZ4 frame declares its content size
            (the Puffin spec requires it; False builds the defect).
        flags: override the 4 footer flag bytes (unknown-flags defects).

    Returns:
        (file_bytes, blob_metadata_list) where each metadata entry carries
        the real ``offset`` and ``length`` of its payload for use in
        manifest entries (``content_offset`` / ``content_size_in_bytes``).
    """
    data = bytearray(PUFFIN_MAGIC)
    footer_blobs = []
    for blob in blobs:
        payload = blob["payload"]
        offset = len(data)
        data += payload
        metadata = {
            "type": blob.get("type", DV_BLOB_TYPE),
            "fields": blob.get("fields", [DV_POSITION_FIELD_ID]),
            # the Puffin spec requires -1 for deletion-vector-v1 blobs
            "snapshot-id": blob.get("snapshot_id", -1),
            "sequence-number": blob.get("sequence_number", -1),
            "offset": blob.get("offset", offset),
            "length": blob.get("length", len(payload)),
        }
        if blob.get("compression_codec") is not None:
            metadata["compression-codec"] = blob["compression_codec"]
        if blob.get("properties") is not None:
            metadata["properties"] = blob["properties"]
        footer_blobs.append(metadata)

    footer_payload = json.dumps(
        {"blobs": footer_blobs, "properties": file_properties or {}}
    ).encode("utf-8")

    if compress_footer:
        import lz4.frame

        footer_payload = lz4.frame.compress(
            footer_payload, store_size=store_content_size
        )
    if flags is None:
        # byte 0 bit 0: whether the footer payload is compressed
        flags = b"\x01\x00\x00\x00" if compress_footer else b"\x00\x00\x00\x00"

    data += PUFFIN_MAGIC
    data += footer_payload
    data += struct.pack("<I", len(footer_payload))
    data += flags
    data += PUFFIN_MAGIC

    return bytes(data), footer_blobs


def parse_puffin_footer(data):
    """Parse the FileMetadata JSON out of a Puffin file's footer."""
    assert data[:4] == PUFFIN_MAGIC, "not a Puffin file (bad leading magic)"
    assert data[-4:] == PUFFIN_MAGIC, "not a Puffin file (bad trailing magic)"
    payload_size = struct.unpack("<I", data[-12:-8])[0]
    payload = data[-12 - payload_size : -12]
    return json.loads(payload.decode("utf-8"))


def _parse_bitmap32(vector, cursor):
    """Parse one 32-bit roaring bitmap (any portable cookie and container
    type) at *cursor*; returns (values, cursor_after)."""
    (cookie16,) = struct.unpack_from("<H", vector, cursor)
    if cookie16 == SERIAL_COOKIE:
        (count_minus_1,) = struct.unpack_from("<H", vector, cursor + 2)
        container_count = count_minus_1 + 1
        run_flags = vector[cursor + 4 : cursor + 4 + (container_count + 7) // 8]
        cursor += 4 + len(run_flags)
        has_offsets = container_count >= NO_OFFSET_THRESHOLD
    else:
        cookie, container_count = struct.unpack_from("<II", vector, cursor)
        assert cookie == SERIAL_COOKIE_NO_RUNCONTAINER, "unsupported cookie"
        run_flags = b""
        cursor += 8
        has_offsets = True

    descriptive = [
        struct.unpack_from("<HH", vector, cursor + 4 * index)
        for index in range(container_count)
    ]
    cursor += 4 * container_count
    if has_offsets:
        cursor += 4 * container_count  # bodies are read sequentially anyway

    values = []
    for index, (key, cardinality_minus_1) in enumerate(descriptive):
        cardinality = cardinality_minus_1 + 1
        is_run = bool(run_flags) and run_flags[index // 8] & (1 << (index % 8))
        if is_run:
            (num_runs,) = struct.unpack_from("<H", vector, cursor)
            cursor += 2
            for _ in range(num_runs):
                start, length_minus_1 = struct.unpack_from("<HH", vector, cursor)
                cursor += 4
                for low in range(start, start + length_minus_1 + 1):
                    values.append((key << 16) | low)
        elif cardinality > ARRAY_CONTAINER_MAX_CARDINALITY:
            words = struct.unpack_from("<1024Q", vector, cursor)
            cursor += BITSET_CONTAINER_SIZE
            for word_index, word in enumerate(words):
                while word:
                    bit = (word & -word).bit_length() - 1
                    values.append((key << 16) | (word_index << 6) | bit)
                    word &= word - 1
        else:
            for _ in range(cardinality):
                (low,) = struct.unpack_from("<H", vector, cursor)
                cursor += 2
                values.append((key << 16) | low)
    return values, cursor


def dv_positions_of_payload(payload):
    """Decode row positions back out of a valid deletion-vector blob —
    array, bitset, and run containers alike (verification helper for
    round-trip checks and for inspecting writer-produced blobs)."""
    vector = payload[8:-4]
    (bucket_count,) = struct.unpack_from("<Q", vector, 0)
    cursor = 8
    positions = []
    for _ in range(bucket_count):
        (high_key,) = struct.unpack_from("<I", vector, cursor)
        cursor += 4
        values, cursor = _parse_bitmap32(vector, cursor)
        positions.extend((high_key << 32) | value for value in values)
    return positions
