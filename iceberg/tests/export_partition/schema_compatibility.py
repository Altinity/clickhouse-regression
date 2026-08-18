"""Create-time source vs destination schema compatibility for EXPORT PARTITION.

Unlike :mod:`schema_evolution` (ALTER between exports), this module builds
the two tables with intentionally diverging schemas up front and checks
whether ``EXPORT PARTITION`` accepts or rejects the pair.

Coverage is a single filtered 6-axis matrix (max 2^6 = 64 cells):

* ``present`` — focus column on both sides, or missing on one side
* ``name_same`` / ``type_same`` / ``position_same`` / ``default_same``
* ``in_partition_key`` — focus column owns the ``PARTITION BY`` term

When ``present`` is false, name/type/position/default are meaningless and
those cells are dropped; the case is expanded across ``missing_side``
(source | destination) instead. Renamed partition-key columns with a
shared identity ``PARTITION BY`` are also dropped as nonsensical on
Iceberg destinations.

``export_merge_tree_part_schema_mismatch_mode`` (Altinity/ClickHouse#2111)
is not an axis here; re-add it once that PR is merged alongside #2134.

Nested Tuple/Array/Map partition-key layout cases from
Altinity/ClickHouse#2134 are left to follow-up coverage (e.g. datatypes).
"""

from dataclasses import dataclass

from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_SchemaCompatibility_CreateTimeSchemas,
    RQ_Iceberg_ExportPartition_SchemaCompatibility_PartitionKeyNameAndPosition,
)
from helpers.common import getuid

from iceberg.tests.export_partition.steps.casting import (
    _lossy_cast_rejection_expectation,
)
from iceberg.tests.export_partition.steps.common import (
    create_export_source_table,
    first_partition_id,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.export_status import (
    count_partition_export_rows,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    select_from_destination,
)


BAD_ARGUMENTS = 36
NUMBER_OF_COLUMNS_DOESNT_MATCH = 20

FOCUS_SRC_NAME = "c"
FOCUS_DST_NAME = "d"
SPACER_NAME = "z"
PAYLOAD_NAME = "id"
YEAR_NAME = "year"


@dataclass(frozen=True)
class SchemaCase:
    present: bool
    name_same: bool
    type_same: bool
    position_same: bool
    default_same: bool
    in_partition_key: bool
    # When ``present`` is False: which table is missing the focus column.
    missing_side: str | None = None


@dataclass(frozen=True)
class ExpectReject:
    exitcode: int
    message: str


@dataclass(frozen=True)
class BuiltSchema:
    src_columns: str
    dst_columns: str
    partition_by: str
    values: str
    row_count: int
    read_columns: str


def _iter_schema_cases():
    """Yield meaningful cells of the 6-axis product."""
    for (
        present,
        name_same,
        type_same,
        position_same,
        default_same,
        in_partition_key,
    ) in product(
        (True, False),
        (True, False),
        (True, False),
        (True, False),
        (True, False),
        (True, False),
    ):
        if not present:
            # Absent column has no name/type/position/default relation.
            if not (name_same and type_same and position_same and default_same):
                continue
            # Both sides need the partition-key column for a shared PARTITION BY.
            if in_partition_key:
                continue
            for missing_side in ("source", "destination"):
                yield SchemaCase(
                    present=False,
                    name_same=True,
                    type_same=True,
                    position_same=True,
                    default_same=True,
                    in_partition_key=False,
                    missing_side=missing_side,
                )
            continue

        # Renaming only the partition-key column cannot keep a shared
        # identity ``PARTITION BY <name>`` on Iceberg destinations.
        if in_partition_key and not name_same:
            continue

        yield SchemaCase(
            present=True,
            name_same=name_same,
            type_same=type_same,
            position_same=position_same,
            default_same=default_same,
            in_partition_key=in_partition_key,
            missing_side=None,
        )


def _col(name, type_name, default=None):
    clause = f"{name} {type_name}"
    if default is not None:
        clause += f" DEFAULT {default}"
    return clause


def _focus_types(type_same):
    """Return ``(source_type, dest_type)``. Different => lossy Int64→Int32."""
    if type_same:
        return "Int32", "Int32"
    return "Int64", "Int32"


def _focus_names(name_same):
    if name_same:
        return FOCUS_SRC_NAME, FOCUS_SRC_NAME
    return FOCUS_SRC_NAME, FOCUS_DST_NAME


def _focus_defaults(default_same):
    """Different defaults: source has DEFAULT 1, destination has none.

    Avoids depending on IcebergS3 accepting DEFAULT in CREATE TABLE.
    """
    if default_same:
        return None, None
    return 1, None


def _build_schemas(case: SchemaCase) -> BuiltSchema:
    """Materialise DDL / VALUES for one matrix cell."""
    src_focus, dst_focus = _focus_names(case.name_same)
    src_type, dst_type = _focus_types(case.type_same)
    src_default, dst_default = _focus_defaults(case.default_same)

    if not case.present:
        shared = [_col(PAYLOAD_NAME, "Int64"), _col(YEAR_NAME, "Int32")]
        focus = _col(FOCUS_SRC_NAME, "Int32")
        if case.missing_side == "destination":
            src_columns = f"{shared[0]}, {shared[1]}, {focus}"
            dst_columns = f"{shared[0]}, {shared[1]}"
            values = "(1, 2020, 7), (2, 2020, 8)"
        else:
            src_columns = f"{shared[0]}, {shared[1]}"
            dst_columns = f"{shared[0]}, {shared[1]}, {focus}"
            values = "(1, 2020), (2, 2020)"
        return BuiltSchema(
            src_columns=src_columns,
            dst_columns=dst_columns,
            partition_by=YEAR_NAME,
            values=values,
            row_count=2,
            read_columns=f"{PAYLOAD_NAME}, {YEAR_NAME}",
        )

    src_focus_col = _col(src_focus, src_type, src_default)
    dst_focus_col = _col(dst_focus, dst_type, dst_default)
    spacer = _col(SPACER_NAME, "Int32")
    payload = _col(PAYLOAD_NAME, "Int64")
    year = _col(YEAR_NAME, "Int32")

    if case.in_partition_key:
        # Two-column layout mirrors Altinity/ClickHouse#2134:
        # focus is the partition key; spacer is the other column.
        if case.position_same:
            src_cols = [src_focus_col, spacer]
            dst_cols = [dst_focus_col, spacer]
        else:
            src_cols = [src_focus_col, spacer]
            dst_cols = [spacer, dst_focus_col]
        return BuiltSchema(
            src_columns=", ".join(src_cols),
            dst_columns=", ".join(dst_cols),
            partition_by=src_focus,
            values="(1, 10), (1, 20)",
            row_count=2,
            read_columns=f"{src_focus}, {SPACER_NAME}",
        )

    # Non-PK focus: year is the partition key and stays last on both sides.
    if case.position_same:
        src_cols = [payload, src_focus_col, spacer, year]
        dst_cols = [payload, dst_focus_col, spacer, year]
    else:
        src_cols = [payload, src_focus_col, spacer, year]
        dst_cols = [payload, spacer, dst_focus_col, year]
    return BuiltSchema(
        src_columns=", ".join(src_cols),
        dst_columns=", ".join(dst_cols),
        partition_by=YEAR_NAME,
        values="(1, 7, 10, 2020), (2, 8, 20, 2020)",
        row_count=2,
        read_columns=f"{PAYLOAD_NAME}, {YEAR_NAME}",
    )


def _expect_outcome(case: SchemaCase, test):
    """Return ``None`` for accept, or :class:`ExpectReject` for sync rejection."""
    if not case.present:
        return ExpectReject(NUMBER_OF_COLUMNS_DOESNT_MATCH, "NUMBER_OF_COLUMNS")

    if case.in_partition_key and not case.position_same:
        return ExpectReject(BAD_ARGUMENTS, "partition key column")

    if not case.type_same:
        exitcode, message = _lossy_cast_rejection_expectation(test)
        return ExpectReject(exitcode, message)

    return None


def _schema_compatibility_examples():
    rows = []
    for case in _iter_schema_cases():
        rows.append(
            (
                case.present,
                case.name_same,
                case.type_same,
                case.position_same,
                case.default_same,
                case.in_partition_key,
                case.missing_side,
            )
        )
    return rows


@TestOutline(Scenario)
@Name("schema compatibility matrix")
@Examples(
    "present, name_same, type_same, position_same, default_same, "
    "in_partition_key, missing_side",
    _schema_compatibility_examples(),
)
def schema_compatibility_matrix(
    self,
    present,
    name_same,
    type_same,
    position_same,
    default_same,
    in_partition_key,
    missing_side,
):
    """One filtered cell of the create-time schema compatibility matrix."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    case = SchemaCase(
        present=present,
        name_same=name_same,
        type_same=type_same,
        position_same=position_same,
        default_same=default_same,
        in_partition_key=in_partition_key,
        missing_side=missing_side,
    )
    built = _build_schemas(case)
    source_table = f"mt_{getuid()}"
    expected = _expect_outcome(case, self)

    with Given(f"create source with columns {built.src_columns!r}"):
        create_export_source_table(
            table_name=source_table,
            columns=built.src_columns,
            partition_by=built.partition_by,
        )

    with And("insert seed rows"):
        insert_data(table_name=source_table, values=built.values)

    with And(f"create Iceberg destination with columns {built.dst_columns!r}"):
        destination = create_iceberg_destination(
            columns=built.dst_columns,
            partition_by=built.partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("look up partition id"):
        partition_id = first_partition_id(table_name=source_table)

    if expected is not None:
        with Then(f"EXPORT PARTITION is rejected ({expected.message})"):
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id=partition_id,
                extra_settings=None,
                exitcode=expected.exitcode,
                message=expected.message,
                wait_for_completion=False,
            )

        with And("no export status row is recorded"):
            count = count_partition_export_rows(
                source_table=source_table,
                partition_id=partition_id,
                destination=destination,
            )
            assert count == 0, error(
                f"Expected no status row after rejection, got {count}"
            )

        with And("destination remains empty"):
            assert_destination_row_count(
                destination=destination,
                expected=0,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
        return

    with When("EXPORT PARTITION"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id=partition_id,
        )

    with Then("destination receives the exported rows"):
        assert_destination_row_count(
            destination=destination,
            expected=built.row_count,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("stable same-name columns are readable"):
        result = select_from_destination(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns=built.read_columns,
            order_by=built.read_columns.split(",")[0].strip(),
            format="TabSeparated",
        )
        assert result.output.strip(), error("Expected non-empty destination readback")


@TestFeature
@Requirements(
    RQ_Iceberg_ExportPartition_SchemaCompatibility_CreateTimeSchemas("1.0"),
    RQ_Iceberg_ExportPartition_SchemaCompatibility_PartitionKeyNameAndPosition("1.0"),
)
@Name("schema compatibility")
def feature(self, minio_root_user, minio_root_password):
    """Create-time source/destination schema permutations for EXPORT PARTITION."""
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    Scenario(run=schema_compatibility_matrix)
