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


def payload_table_checksum(node, table_name):
    """Checksum that also covers the ``payload`` column contents."""
    return node.query(
        f"SELECT count(), sum(i), groupBitXor(i), "
        f"groupBitXor(cityHash64(payload)) FROM {table_name}"
    ).output.strip()


def table_row_count(node, table_name):
    """Return integer row count for the table."""
    return int(node.query(f"SELECT count() FROM {table_name}").output.strip())
