"""Byte-level corruption harness for the file-corruption feature.

Unlike :mod:`puffin` / :mod:`manifest`, which build structurally valid
files with exactly one well-formed defect, these helpers damage raw object
bytes — truncations, corrupted magic, hostile footer sizes, bit flips,
wholesale garbage — and restore the original bytes when the scenario ends,
so every case starts from a healthy chain.

Corruptors are pure functions ``bytes -> bytes``; randomized ones take an
explicit seed so a failure reproduces exactly.
"""

import random
import struct

from testflows.core import *

from iceberg.tests.deletion_vectors.steps import s3_objects

FLIP_SEED = 48  # SRS-048


@TestStep(Given)
def corrupted_object(self, key, data, original):
    """Replace the object at *key* with *data*; the original bytes are
    restored when the scenario ends, so corruption never leaks into the
    next case."""
    try:
        s3_objects.put_object_bytes(key, data)
        yield key
    finally:
        with Finally(f"restore the original object at {key.rsplit('/', 1)[-1]}"):
            s3_objects.put_object_bytes(key, original)


def empty(data):
    return b""


def truncate_to(size):
    def corruptor(data):
        return data[:size]

    return corruptor


def truncate_fraction(fraction):
    def corruptor(data):
        return data[: int(len(data) * fraction)]

    return corruptor


def corrupt_leading_magic(data):
    return b"XXXX" + data[4:]


def corrupt_trailing_magic(data):
    return data[:-4] + b"XXXX"


def drop_footer_trailer(data):
    """Cut into the fixed 12-byte footer trailer (size + flags + magic)."""
    return data[:-6]


def patch_footer_payload_size(value):
    """Overwrite the little-endian i32 FooterPayloadSize field."""

    def corruptor(data):
        return data[:-12] + struct.pack("<i", value) + data[-8:]

    return corruptor


def garbage_footer_payload(data):
    """Keep the declared payload size but replace the payload bytes, so the
    footer is located correctly and then fails to parse as JSON."""
    (size,) = struct.unpack("<I", data[-12:-8])
    return data[: len(data) - 12 - size] + b"X" * size + data[-12:]


def flip_byte(offset):
    def corruptor(data):
        return data[:offset] + bytes([data[offset] ^ 0x01]) + data[offset + 1 :]

    return corruptor


def flip_offsets(data_length, count, seed=FLIP_SEED):
    """Deterministic byte offsets spread across the file for flip cases."""
    return sorted(random.Random(seed).sample(range(data_length), count))


def random_bytes(seed=FLIP_SEED):
    def corruptor(data):
        return random.Random(seed).randbytes(len(data))

    return corruptor


def puffin_structural_cases(data):
    """name → corrupted bytes for every deterministic-failure Puffin case.

    Bit flips are not here: a flip can land in a non-load-bearing footer
    byte and legitimately leave the result correct, so flip cases use the
    correct-or-explicit-error assertion instead."""
    return {
        "empty object": empty(data),
        "truncated to the header magic": truncate_to(4)(data),
        "truncated mid blob": truncate_fraction(1 / 3)(data),
        "truncated mid footer": truncate_fraction(0.95)(data),
        "footer trailer cut short": drop_footer_trailer(data),
        "leading magic corrupted": corrupt_leading_magic(data),
        "trailing magic corrupted": corrupt_trailing_magic(data),
        "footer payload size zero": patch_footer_payload_size(0)(data),
        "footer payload size negative": patch_footer_payload_size(-1)(data),
        "footer payload size beyond the file": patch_footer_payload_size(
            len(data) + 1000
        )(data),
        "footer payload size above the cap": patch_footer_payload_size(32 * 1024**2)(
            data
        ),
        "footer payload is not JSON": garbage_footer_payload(data),
    }


def avro_structural_cases(data):
    """name → corrupted bytes for an Avro object container (manifest or
    manifest list). Only structural damage the Avro layer can detect —
    Avro carries no checksums, so in-block flips that still decode are
    out of reader scope (see the CorruptManifest requirement)."""
    return {
        "empty object": empty(data),
        "avro magic corrupted": b"XXXX" + data[4:],
        "header truncated": truncate_to(20)(data),
        "truncated mid data block": truncate_fraction(0.8)(data),
        "replaced with random bytes": random_bytes()(data),
    }
