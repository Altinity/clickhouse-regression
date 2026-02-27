from testflows.core import *
from testflows.asserts import error
import json
from .export_fields import (
    get_source_database,
    get_destination_table,
    get_partition_id,
    get_parts,
    get_parts_count,
    get_create_time,
    get_source_replica,
    get_transaction_id,
    get_parts_to_do,
    get_export_field,
)


@TestStep(Then)
def verify_export_fields_populated(self, source_table, s3_table_name):
    """Verify that all export fields are populated in system.replicated_partition_exports."""
    assert get_source_database(source_table=source_table).output.strip() != "", error()
    assert (
        get_destination_table(source_table=source_table).output.strip() == s3_table_name
    ), error()
    assert get_partition_id(source_table=source_table).output.strip() != "", error()
    assert get_parts(source_table=source_table).output.strip() != "", error()
    assert int(get_parts_count(source_table=source_table).output.strip()) > 0, error()
    assert get_create_time(source_table=source_table).output.strip() != "", error()
    assert get_source_replica(source_table=source_table).output.strip() != "", error()


@TestStep(Then)
def verify_export_status(self, source_table, status, expected_count_min=1):
    """Verify export status in system.replicated_partition_exports."""
    status_count = get_export_field(
        field_name="COUNT(*)",
        source_table=source_table,
        select_clause="COUNT(*)",
        where_clause=f"status = '{status}'",
    )
    assert int(status_count.output.strip()) >= expected_count_min, error()


@TestStep(Then)
def verify_parts_to_do_decreases(self, source_table, timeout=60, delay=2):
    """Verify that parts_to_do decreases as export progresses."""
    initial_count = int(get_parts_to_do(source_table=source_table).output.strip())
    assert initial_count > 0, error()

    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            current_count = int(
                get_parts_to_do(source_table=source_table).output.strip()
            )
            assert current_count < initial_count or current_count == 0, error()


@TestStep(Then)
def verify_exports_appear_in_table(self, source_table):
    """Verify that exports appear in system.replicated_partition_exports with PENDING status."""
    exports_count = get_export_field(
        field_name="COUNT(*)",
        source_table=source_table,
        select_clause="COUNT(*)",
        where_clause="status = 'PENDING'",
    )
    assert int(exports_count.output.strip()) > 0, error()


@TestStep(Then)
def verify_partition_ids_match(self, source_table, expected_partitions):
    """Verify that partition_ids in the table match expected partitions."""
    all_partition_ids = get_export_field(
        field_name="partition_id",
        source_table=source_table,
        select_clause="DISTINCT partition_id",
    )
    exported_partition_ids = set(
        pid.strip()
        for pid in all_partition_ids.output.strip().splitlines()
        if pid.strip()
    )

    assert len(exported_partition_ids) == len(expected_partitions), error()
    for partition in expected_partitions:
        assert partition in exported_partition_ids, error()


@TestStep(Given)
def get_expected_parts_from_table(self, source_table, node=None):
    """Get expected parts from source table system.parts."""
    if node is None:
        node = self.context.node

    from .export_operations import get_partitions

    partitions = get_partitions(table_name=source_table, node=node)
    expected_parts = set()
    for partition in partitions:
        parts_result = node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND partition_id = '{partition}' AND active = 1",
            exitcode=0,
            steps=True,
        )
        for part in parts_result.output.strip().splitlines():
            expected_parts.add(part.strip())

    return expected_parts


@TestStep(Then)
def verify_parts_array_matches(self, source_table, expected_parts):
    """Verify that parts array in the table matches expected parts."""
    all_parts_result = get_export_field(
        field_name="parts",
        source_table=source_table,
        select_clause="parts",
    )
    exported_parts_set = set()
    for line in all_parts_result.output.strip().splitlines():
        if line.strip():
            try:
                parts_array = json.loads(line.strip())
                if isinstance(parts_array, list):
                    exported_parts_set.update(parts_array)
            except (json.JSONDecodeError, ValueError):
                pass

    assert len(exported_parts_set) >= len(expected_parts), error()
    for part in expected_parts:
        assert part in exported_parts_set, error()


@TestStep(Then)
def verify_table_structure_has_fields(
    self, table_name="system.replicated_partition_exports", node=None
):
    """Verify that table structure contains all required fields."""
    if node is None:
        node = self.context.node

    structure_result = node.query(
        f"DESCRIBE TABLE {table_name}",
        exitcode=0,
        steps=True,
    )
    column_names = [
        line.split("\t")[0].strip()
        for line in structure_result.output.strip().splitlines()
        if line.strip()
    ]

    required_fields = [
        "database",
        "table",
        "destination_database",
        "destination_table",
        "create_time",
        "partition_id",
        "transaction_id",
        "query_id",
        "source_replica",
        "parts",
        "parts_count",
        "parts_to_do",
        "status",
        "exception_replica",
        "last_exception",
        "exception_part",
        "exception_count",
    ]

    alternative_names = {
        "database": ["source_database"],
        "table": ["source_table"],
    }

    missing_fields = []
    for field in required_fields:
        if field not in column_names:
            if field in alternative_names:
                found_alternative = any(
                    alt in column_names for alt in alternative_names[field]
                )
                if not found_alternative:
                    missing_fields.append(field)
            else:
                missing_fields.append(field)

    assert len(missing_fields) == 0, error(
        f"Missing required fields: {missing_fields}. Available columns: {column_names}"
    )


@TestStep(Then)
def verify_all_fields_populated(self, source_table, node=None, timeout=30, delay=2):
    """Verify that all required fields are populated after export."""
    if node is None:
        node = self.context.node

    for retry in retries(timeout=timeout, delay=delay):
        with retry:
            result = node.query(
                f"SELECT source_database, source_table, destination_database, destination_table, "
                f"create_time, partition_id, transaction_id, query_id, source_replica, "
                f"parts, parts_count, parts_to_do, status, exception_replica, "
                f"last_exception, exception_part, exception_count "
                f"FROM system.replicated_partition_exports "
                f"WHERE source_table = '{source_table}' LIMIT 1",
                exitcode=0,
                steps=True,
            )
            assert result.output.strip() != "", error(
                "Fields should be populated after export"
            )


@TestStep(Then)
def verify_transaction_id_populated(self, source_table):
    """Verify that transaction_id is populated for export operations."""
    assert get_transaction_id(source_table=source_table).output.strip() != "", error()


@TestStep(Then)
def verify_active_exports_limited(self, source_table, max_count):
    """Verify that the number of active exports is limited."""
    active_exports = get_export_field(
        field_name="COUNT(*)",
        source_table=source_table,
        select_clause="COUNT(*)",
        where_clause="status = 'PENDING' OR status = 'COMPLETED'",
    )
    active_count = int(active_exports.output.strip())
    assert active_count <= max_count, error()
