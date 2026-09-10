"""Checksum helpers for CAS table / partition agreement."""


def partition_checksum(node, table_name, partition):
    """Stable checksum for one partition's contents."""
    return node.query(
        f"SELECT count(), sum(i), groupBitXor(i) "
        f"FROM {table_name} WHERE p = {partition}"
    ).output.strip()


def table_checksum(node, table_name):
    """Stable checksum for the whole table."""
    return node.query(
        f"SELECT count(), sum(i), groupBitXor(i), arraySort(groupUniqArray(p)) "
        f"FROM {table_name}"
    ).output.strip()


def table_checksum_components(node, table_name):
    """Checksum of a table as numbers: (count, sum(i), xor(i), partitions)."""
    row = node.query(
        f"SELECT count(), sum(i), groupBitXor(i), arraySort(groupUniqArray(p)) "
        f"FROM {table_name}"
    ).output.strip()
    count, total, checksum, partitions = row.split("\t")
    listed = partitions.strip("[]")
    return (
        int(count),
        int(total or 0),
        int(checksum or 0),
        tuple(int(p) for p in listed.split(",") if p.strip()),
    )


def merge_checksum_components(components):
    """Combine per-shard checksum components into one cluster-wide checksum."""
    total_count = 0
    total_sum = 0
    total_checksum = 0
    partitions = set()
    for count, total, checksum, shard_partitions in components:
        total_count += count
        total_sum += total
        total_checksum ^= checksum
        partitions.update(shard_partitions)
    return total_count, total_sum, total_checksum, tuple(sorted(partitions))


def payload_table_checksum(node, table_name):
    """Checksum that also covers the ``payload`` column contents."""
    return node.query(
        f"SELECT count(), sum(i), groupBitXor(i), "
        f"groupBitXor(cityHash64(payload)) FROM {table_name}"
    ).output.strip()


def table_row_count(node, table_name):
    """Return integer row count for the table."""
    return int(node.query(f"SELECT count() FROM {table_name}").output.strip())
