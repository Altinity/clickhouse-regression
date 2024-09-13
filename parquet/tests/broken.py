import os

from testflows import *
from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.outline import import_export


@TestStep(Given)
def io_error_message(self, error):
    exitcode = 124 if check_clickhouse_version("<=22.4")(self) else 36
    message = (
        f"Exception: Cannot extract table structure from Parquet format file. Error: IOError: {error}"
        if check_clickhouse_version("<=22.4")(self)
        else f"Exception: IOError: {error}: Cannot extract table structure from Parquet format file"
    )
    return (
        exitcode,
        message,
    )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Date("1.0"))
def read_broken_date(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken date values."""
    node = self.context.node

    with Given("I have a Parquet file with broken date value"):
        broken_date_parquet = os.path.join("broken", "broken_date.parquet")

    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(error="DATE can only annotate INT32")

        node.query(
            f"""
            CREATE TABLE imported_from_parquet
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Int("1.0"))
def read_broken_int(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken int values."""
    node = self.context.node

    with Given("I have a Parquet file with broken int value"):
        broken_date_parquet = os.path.join("broken", "broken_int.parquet")

    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(error="INT_32 can only annotate INT32")

        node.query(
            f"""
            CREATE TABLE imported_from_parquet
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_BigInt("1.0"))
def read_broken_bigint(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken bigint values."""
    node = self.context.node

    with Given("I have a Parquet file with broken bigint value"):
        broken_date_parquet = os.path.join("broken", "broken_bigint.parquet")

    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(error="INT_64 can only annotate INT64")

        node.query(
            f"""CREATE TABLE imported_from_parquet
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_SmallInt("1.0")
)
def read_broken_smallint(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken smallint values."""
    node = self.context.node

    with Given("I have a Parquet file with broken smallint value"):
        broken_date_parquet = os.path.join("broken", "broken_smallint.parquet")
    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(error="INT_16 can only annotate INT32")

        node.query(
            f"""
            CREATE TABLE imported_from_parquet
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TinyInt("1.0"))
def read_broken_tinyint(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken tinyint values."""
    node = self.context.node

    with Given("I have a Parquet file with broken tinyint value"):
        broken_date_parquet = os.path.join("broken", "broken_tinyint.parquet")

    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(error="INT_8 can only annotate INT32")

        node.query(
            f"""
            CREATE TABLE imported_from_parquet
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_UInt("1.0"))
def read_broken_uint(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken date values."""
    node = self.context.node

    with Given("I have a Parquet file with broken uint value"):
        broken_date_parquet = os.path.join("broken", "broken_uinteger.parquet")

    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(error="UINT_32 can only annotate INT32")

        node.query(
            f"""
            CREATE TABLE imported_from_parquet
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_UBigInt("1.0"))
def read_broken_ubigint(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken Ubigint values."""
    node = self.context.node

    with Given("I have a Parquet file with broken ubigint value"):
        broken_date_parquet = os.path.join("broken", "broken_ubigint.parquet")

    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(error="UINT_64 can only annotate INT64")

        node.query(
            f"""
            CREATE TABLE imported_from_parquet
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_USmallInt("1.0")
)
def read_broken_usmallint(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken Usmallint values."""
    node = self.context.node

    with Given("I have a Parquet file with broken usmallint value"):
        broken_date_parquet = os.path.join("broken", "broken_usmallint.parquet")

    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(error="UINT_16 can only annotate INT32")

        node.query(
            f"""
            CREATE TABLE imported_from_parquet
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_UTinyInt("1.0")
)
def read_broken_utinyint(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken Utinyint values."""
    node = self.context.node
    table_name = "table_" + getuid()

    with Given("I have a Parquet file with broken usmallint value"):
        broken_date_parquet = os.path.join("broken", "broken_utinyint.parquet")

    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(error="UINT_8 can only annotate INT32")

        node.query(
            f"""
            CREATE TABLE {table_name}
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimestampMS("1.0")
)
def read_broken_timestamp_ms(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken timestamp (ms) values."""
    node = self.context.node
    table_name = "table_" + getuid()

    with Given("I have a Parquet file with broken timestamp (ms) value"):
        broken_date_parquet = os.path.join("broken", "broken_timestamp_ms.parquet")

    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(
            error="TIMESTAMP_MILLIS can only annotate INT64"
        )

        node.query(
            f"""
            CREATE TABLE {table_name}
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimestampUS("1.0")
)
def read_broken_timestamp_us(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with broken timestamp (us) values."""
    node = self.context.node
    table_name = "table_" + getuid()

    with Given("I have a Parquet file with broken timestamp (us) value"):
        broken_date_parquet = os.path.join("broken", "broken_timestamp.parquet")

    with When("I try to import the broken Parquet file into the table"):
        exitcode, message = io_error_message(
            error="TIMESTAMP_MICROS can only annotate INT64"
        )

        node.query(
            f"""
            CREATE TABLE {table_name}
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_File("1.0"))
def file(self):
    """Check that ClickHouse outputs an error when trying to import a broken Parquet file with broken file."""
    node = self.context.node
    table_name = "table_" + getuid()

    with Given("I have a broken Parquet file generated via arrow library"):
        broken_date_parquet = os.path.join("broken", "broken-arrow.parquet")

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE {table_name}
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message="DB::Exception: Received",
            exitcode=33,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_String("1.0"))
def string(self):
    """Check that ClickHouse outputs an error when trying to import a Parquet file with invalid string value."""
    with Given(r"I have a Parquet file with TREL\xC3 as a string value"):
        broken_date_parquet = os.path.join("broken", "invalid.parquet")
    snapshot_name = (
        "invalid_string_1_structure_22.3"
        if check_clickhouse_version("<=22.4")(self)
        else "invalid_string_1_structure"
    )

    import_export(snapshot_name=snapshot_name, import_file=broken_date_parquet)


@TestFeature
@Name("broken")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values("1.0"))
def feature(self, node="clickhouse1"):
    """Check reading Parquet files with broken values."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "broken"

    for scenario in loads(current_module(), Scenario):
        scenario()
