from testflows.core import *
from testflows.asserts import error

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from helpers.common import getuid


@TestScenario
def alter_column(self, minio_root_user, minio_root_password, node=None):
    """Check that ALTER TABLE ADD COLUMN, DROP COLUMN, RENAME COLUMN are
    not supported for Iceberg tables."""

    if node is None:
        node = self.context.node

    with Given("get table with Iceberg engine"):
        iceberg_table_name = iceberg_engine.get_iceberg_table_name(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("try to add new column to ClickHouse table with Iceberg engine"):
        exitcode = 48
        message = "DB::Exception: Alter of type 'ADD_COLUMN' is not supported by storage Iceberg"
        node.query(
            f"ALTER TABLE {iceberg_table_name} ADD COLUMN new_column UInt64",
            exitcode=exitcode,
            message=message,
        )

    with And("try to drop column from ClickHouse table with Iceberg engine"):
        exitcode = 48
        message = "DB::Exception: Alter of type 'DROP_COLUMN' is not supported by storage Iceberg"
        node.query(
            f"ALTER TABLE {iceberg_table_name} DROP COLUMN long_col",
            exitcode=exitcode,
            message=message,
        )

    with And("try to rename column in ClickHouse table with Iceberg engine"):
        exitcode = 48
        message = "DB::Exception: Alter of type 'RENAME_COLUMN' is not supported by storage Iceberg"
        node.query(
            f"ALTER TABLE {iceberg_table_name} RENAME COLUMN long_col TO new_col",
            exitcode=exitcode,
            message=message,
        )

    with And("try to clear column in ClickHouse table with Iceberg engine"):
        exitcode = 48
        message = "DB::Exception: Alter of type 'DROP_COLUMN' is not supported by storage Iceberg"
        node.query(
            f"ALTER TABLE {iceberg_table_name} CLEAR COLUMN long_col",
            exitcode=exitcode,
            message=message,
        )

    with And("try to modify column in ClickHouse table with Iceberg engine"):
        exitcode = 48
        message = "DB::Exception: Alter of type 'MODIFY_COLUMN' is not supported by storage Iceberg"
        node.query(
            f"ALTER TABLE {iceberg_table_name} MODIFY COLUMN long_col UInt64",
            exitcode=exitcode,
            message=message,
        )

    with And(
        "try to use MODIFY COLUMN MODIFY SETTINGS on ClickHouse table with Iceberg engine"
    ):
        exitcode = 48
        message = "DB::Exception: Alter of type 'MODIFY_COLUMN' is not supported by storage Iceberg"
        node.query(
            f"ALTER TABLE {iceberg_table_name} MODIFY COLUMN long_col MODIFY SETTING max_compress_block_size = 1048576",
            exitcode=exitcode,
            message=message,
        )

    with And(
        "try to use MODIFY COLUMN RESET SETTINGS on ClickHouse table with Iceberg engine"
    ):
        exitcode = 48
        message = "DB::Exception: Alter of type 'MODIFY_COLUMN' is not supported by storage Iceberg"
        node.query(
            f"ALTER TABLE {iceberg_table_name} MODIFY COLUMN long_col RESET SETTING max_compress_block_size",
            exitcode=exitcode,
            message=message,
        )


@TestScenario
def alter_partitions(self, minio_root_user, minio_root_password, node=None):
    """Check that ALTER TABLE ADD PARTITION, DROP PARTITION, DROP PARTITION are
    not supported for Iceberg tables."""

    if node is None:
        node = self.context.node

    with Given("get table with Iceberg engine"):
        iceberg_table_name = get_iceberg_table_name(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("expected exitcode and message for partitioning"):
        exitcode = 48
        message = "DB::Exception: Table engine IcebergS3 doesn't support partitioning. (NOT_IMPLEMENTED)"
        message2 = "DB::Exception: Table engine Iceberg doesn't support partitioning. (NOT_IMPLEMENTED)"

    with Then("try to use DROP PARTITION/PART on ClickHouse table with Iceberg engine"):
        output1 = node.query(
            f"ALTER TABLE {iceberg_table_name} DROP PARTITION ALL",
            no_checks=True,
        )
        assert output1.exitcode == exitcode, error()
        assert message in output1.output or message2 in output1.output, error()

        output2 = node.query(
            f"ALTER TABLE {iceberg_table_name} DROP PART '1'",
            no_checks=True,
        )
        assert output2.exitcode == exitcode, error()
        assert message in output2.output or message2 in output2.output, error()

    with And(
        "try to use DETACH PARTITION/PART from ClickHouse table with Iceberg engine"
    ):
        output1 = node.query(
            f"ALTER TABLE {iceberg_table_name} DETACH PARTITION 'all_2_2_0'",
            no_checks=True,
        )
        assert output1.exitcode == exitcode, error()
        assert message in output1.output or message2 in output1.output, error()

        output2 = node.query(
            f"ALTER TABLE {iceberg_table_name} DETACH PART 'all_2_2_0'",
            no_checks=True,
        )
        assert output2.exitcode == exitcode, error()
        assert message in output2.output or message2 in output2.output, error()

    with And(
        "try to DROP DETACHED PARTITION/PART from ClickHouse table with Iceberg engine"
    ):
        output1 = node.query(
            f"ALTER TABLE {iceberg_table_name} DROP DETACHED PARTITION ALL",
            no_checks=True,
        )
        assert output1.exitcode == exitcode, error()
        assert message in output1.output or message2 in output1.output, error()

        output2 = node.query(
            f"ALTER TABLE {iceberg_table_name} DROP DETACHED PART '1'",
            no_checks=True,
        )
        assert output2.exitcode == exitcode, error()
        assert message in output2.output or message2 in output2.output, error()

    with And("try to FORGET PARTITION from ClickHouse table with Iceberg engine"):
        output = node.query(
            f"ALTER TABLE {iceberg_table_name} FORGET PARTITION 'all_2_2_0'",
            no_checks=True,
        )
        assert output.exitcode == exitcode, error()
        assert message in output.output or message2 in output.output, error()

    with And("try to ATTACH PARTITION/PART to ClickHouse table with Iceberg engine"):
        output1 = node.query(
            f"ALTER TABLE {iceberg_table_name} ATTACH PARTITION 'all_2_2_0'",
            no_checks=True,
        )
        assert output1.exitcode == exitcode, error()
        assert message in output1.output or message2 in output1.output, error()

        output2 = node.query(
            f"ALTER TABLE {iceberg_table_name} ATTACH PART 'all_2_2_0'",
            no_checks=True,
        )
        assert output2.exitcode == exitcode, error()
        assert message in output2.output or message2 in output2.output, error()

    with And("try to REPLACE PARTITION in ClickHouse table with Iceberg engine"):
        output = node.query(
            f"ALTER TABLE {iceberg_table_name} REPLACE PARTITION 'all_2_2_0' FROM some_table",
            no_checks=True,
        )
        assert output.exitcode == exitcode, error()
        assert message in output.output or message2 in output.output, error()

    with And("try to MOVE PARTITION in ClickHouse table with Iceberg engine"):
        output = node.query(
            f"ALTER TABLE {iceberg_table_name} MOVE PARTITION 'all_2_2_0' TO TABLE some_table",
            no_checks=True,
        )
        assert output.exitcode == exitcode, error()
        assert message in output.output or message2 in output.output, error()

    with And("try to FREEZE PARTITION in ClickHouse table with Iceberg engine"):
        node.query(
            f"ALTER TABLE {iceberg_table_name} FREEZE PARTITION 'all_2_2_0'",
            no_checks=True,
        )
        assert output.exitcode == exitcode, error()
        assert message in output.output or message2 in output.output, error()

    with And("try to UNFREEZE PARTITION in ClickHouse table with Iceberg engine"):
        output = node.query(
            f"ALTER TABLE {iceberg_table_name} UNFREEZE PARTITION 'all_2_2_0' WITH NAME 'backup_name'",
            no_checks=True,
        )
        assert output.exitcode == exitcode, error()
        assert message in output.output or message2 in output.output, error()

    with And("try to FETCH PARTITION|PART in ClickHouse table with Iceberg engine"):
        output1 = node.query(
            f"ALTER TABLE {iceberg_table_name} FETCH PARTITION 'all_2_2_0' FROM 'some_path'",
            no_checks=True,
        )
        assert output1.exitcode == exitcode, error()
        assert message in output1.output or message2 in output1.output, error()

        output2 = node.query(
            f"ALTER TABLE {iceberg_table_name} FETCH PART 'all_2_2_0' FROM 'some_path'",
            no_checks=True,
        )
        assert output2.exitcode == exitcode, error()
        assert message in output2.output or message2 in output2.output, error()

    with And(
        "try to MOVE PARTITION|PART TO DISK in ClickHouse table with Iceberg engine"
    ):
        output1 = node.query(
            f"ALTER TABLE {iceberg_table_name} MOVE PARTITION 'all_2_2_0' TO DISK 'some_disk_name'",
            no_checks=True,
        )
        assert output1.exitcode == exitcode, error()
        assert message in output1.output or message2 in output1.output, error()

        output2 = node.query(
            f"ALTER TABLE {iceberg_table_name} MOVE PART 'all_2_2_0' TO DISK 'some_disk_name'",
            no_checks=True,
        )
        assert output2.exitcode == exitcode, error()
        assert message in output2.output or message2 in output2.output, error()

    with And("try to UPDATE PARTITION in ClickHouse table with Iceberg engine"):
        exitcode = 48
        message = "DB::Exception: Table engine IcebergS3 doesn't support mutations. (NOT_IMPLEMENTED)"
        message2 = "DB::Exception: Table engine Iceberg doesn't support mutations. (NOT_IMPLEMENTED)"
        output = node.query(
            f"ALTER TABLE {iceberg_table_name} UPDATE x = x + 1 IN PARTITION 2 WHERE p = 2;",
            no_checks=True,
        )
        assert output.exitcode == exitcode, error()
        assert message in output.output or message2 in output.output, error()

    with And("try to DELETE IN PARTITION in ClickHouse table with Iceberg engine"):
        exitcode = 48
        message = "DB::Exception: Table engine IcebergS3 doesn't support mutations. (NOT_IMPLEMENTED)"
        message2 = "DB::Exception: Table engine Iceberg doesn't support mutations. (NOT_IMPLEMENTED)"
        node.query(
            f"ALTER TABLE {iceberg_table_name} DELETE IN PARTITION 2 WHERE p = 2;",
            no_checks=True,
        )
        assert output.exitcode == exitcode, error()
        assert message in output.output or message2 in output.output, error()

    with And(
        "try to CLEAR COLUMN IN PARTITION in ClickHouse table with Iceberg engine"
    ):
        exitcode = 48
        message = "DB::Exception: Alter of type 'DROP_COLUMN' is not supported by storage Iceberg"
        node.query(
            f"ALTER TABLE {iceberg_table_name} CLEAR COLUMN long_col IN PARTITION 'all_2_2_0'",
            exitcode=exitcode,
            message=message,
        )


@TestScenario
def alter_comment_columns(self, minio_root_user, minio_root_password, node=None):
    """Check that COMMENT COLUMN works for Iceberg tables."""

    if node is None:
        node = self.context.node

    with Given("get table with Iceberg engine"):
        iceberg_table_name = get_iceberg_table_name(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("comment columns in ClickHouse table with Iceberg engine"):
        comment = f"comment_{getuid()}"
        exitcode = 48
        message = "DB::Exception: Iceberg: alterTable() is not supported."
        node.query(
            f"ALTER TABLE {iceberg_table_name} COMMENT COLUMN long_col '{comment}'",
            exitcode=exitcode,
            message=message,
        )

    with And("try to remove comment"):
        exitcode = 36
        message = "DB::Exception: Column `long_col` doesn't have COMMENT, cannot remove it. (BAD_ARGUMENTS)"
        node.query(
            f"ALTER TABLE {iceberg_table_name} MODIFY COLUMN IF EXISTS long_col REMOVE COMMENT",
            exitcode=exitcode,
            message=message,
        )


@TestScenario
def alter_delete(self, minio_root_user, minio_root_password, node=None):
    """Check that DELETE FROM TABLE is not supported for Iceberg tables."""

    if node is None:
        node = self.context.node

    with Given("get table with Iceberg engine"):
        iceberg_table_name = get_iceberg_table_name(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("try to DELETE FROM ClickHouse table with Iceberg engine"):
        exitcode = 48
        message = "DB::Exception: Table engine IcebergS3 doesn't support mutations. (NOT_IMPLEMENTED)"
        message2 = "DB::Exception: Table engine Iceberg doesn't support mutations. (NOT_IMPLEMENTED)"
        output = node.query(
            f"ALTER TABLE {iceberg_table_name} DELETE WHERE string_col LIKE '%hello%'",
            no_checks=True,
        )
        assert message in output.output or message2 in output.output, error()
        assert output.exitcode == exitcode, error()


@TestScenario
def alter_settings(self, minio_root_user, minio_root_password, node=None):
    """Check that settings manipulation is not supported for Iceberg tables."""

    if node is None:
        node = self.context.node

    with Given("get table with Iceberg engine"):
        iceberg_table_name = get_iceberg_table_name(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("try to modify settings in ClickHouse table with Iceberg engine"):
        exitcode1 = 48
        message1 = "DB::Exception: Alter of type 'MODIFY_SETTING' is not supported by storage Iceberg"

        exitcode2 = 36
        message2 = "DB::Exception: Cannot alter settings, because table engine doesn't support settings changes. (BAD_ARGUMENTS)"

        output = node.query(
            f"ALTER TABLE {iceberg_table_name} MODIFY SETTING max_part_loading_threads=8, max_parts_in_total=50000",
            no_checks=True,
        )
        assert (output.exitcode == exitcode1 and message1 in output.output) or (
            output.exitcode == exitcode2 and message2 in output.output
        ), error()


@TestScenario
def alter_order_by(self, minio_root_user, minio_root_password, node=None):
    """Check that ORDER BY is not supported for Iceberg tables."""

    if node is None:
        node = self.context.node

    with Given("get table with Iceberg engine"):
        iceberg_table_name = get_iceberg_table_name(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("try to use ORDER BY in ClickHouse table with Iceberg engine"):
        exitcode = 48
        message = "DB::Exception: Received from localhost:9000. DB::Exception: Alter of type 'MODIFY_ORDER_BY' is not supported by storage Iceberg"
        node.query(
            f"ALTER TABLE {iceberg_table_name} MODIFY ORDER BY long_col",
            exitcode=exitcode,
            message=message,
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=alter_column)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=alter_comment_columns)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=alter_partitions)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=alter_settings)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=alter_delete)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=alter_order_by)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
