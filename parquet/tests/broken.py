import os
from testflows import *
from testflows.core import *
from parquet.requirements import *
from helpers.common import *


def io_error_message(error):
    return (
        36,
        f"Exception: IOError: {error}: Cannot extract table structure from Parquet format file",
    )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Date("1.0"))
def read_broken_date(self):
    node = self.context.node
    exitcode, message = io_error_message("DATE can only annotate INT32")

    with Given("I have a Parquet file with broken date value"):
        broken_date_parquet = os.path.join("broken", "broken_date.parquet")

    with When("I try to import the broken Parquet file into the table"):
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
    node = self.context.node
    exitcode, message = io_error_message("INT_32 can only annotate INT32")

    with Given("I have a Parquet file with broken int value"):
        broken_date_parquet = os.path.join("broken", "broken_int.parquet")

    with When("I try to import the broken Parquet file into the table"):
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
    node = self.context.node
    exitcode, message = io_error_message("INT_64 can only annotate INT64")

    with Given("I have a Parquet file with broken bigint value"):
        broken_date_parquet = os.path.join("broken", "broken_bigint.parquet")

    with When("I try to import the broken Parquet file into the table"):
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
    node = self.context.node
    exitcode, message = io_error_message("INT_16 can only annotate INT32")

    with Given("I have a Parquet file with broken smallint value"):
        broken_date_parquet = os.path.join("broken", "broken_smallint.parquet")
    with When("I try to import the broken Parquet file into the table"):
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
    node = self.context.node
    exitcode, message = io_error_message("INT_8 can only annotate INT32")

    with Given("I have a Parquet file with broken tinyint value"):
        broken_date_parquet = os.path.join("broken", "broken_tinyint.parquet")

    with When("I try to import the broken Parquet file into the table"):
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
    node = self.context.node
    exitcode, message = io_error_message("UINT_32 can only annotate INT32")

    with Given("I have a Parquet file with broken uint value"):
        broken_date_parquet = os.path.join("broken", "broken_uinteger.parquet")

    with When("I try to import the broken Parquet file into the table"):
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
    node = self.context.node
    exitcode, message = io_error_message("UINT_64 can only annotate INT64")

    with Given("I have a Parquet file with broken ubigint value"):
        broken_date_parquet = os.path.join("broken", "broken_ubigint.parquet")

    with When("I try to import the broken Parquet file into the table"):
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
    node = self.context.node
    exitcode, message = io_error_message("UINT_16 can only annotate INT32")

    with Given("I have a Parquet file with broken usmallint value"):
        broken_date_parquet = os.path.join("broken", "broken_usmallint.parquet")

    with When("I try to import the broken Parquet file into the table"):
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
    node = self.context.node
    exitcode, message = io_error_message("UINT_8 can only annotate INT32")

    with Given("I have a Parquet file with broken usmallint value"):
        broken_date_parquet = os.path.join("broken", "broken_utinyint.parquet")

    with When("I try to import the broken Parquet file into the table"):
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
    RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimestampMS("1.0")
)
def read_broken_timestamp_ms(self):
    node = self.context.node
    exitcode, message = io_error_message("TIMESTAMP_MILLIS can only annotate INT64")

    with Given("I have a Parquet file with broken timestamp (ms) value"):
        broken_date_parquet = os.path.join("broken", "broken_timestamp_ms.parquet")

    with When("I try to import the broken Parquet file into the table"):
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
    RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimestampUS("1.0")
)
def read_broken_timestamp_us(self):
    node = self.context.node
    exitcode, message = io_error_message("TIMESTAMP_MICROS can only annotate INT64")

    with Given("I have a Parquet file with broken timestamp (us) value"):
        broken_date_parquet = os.path.join("broken", "broken_timestamp.parquet")

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{broken_date_parquet}', Parquet)
            """,
            message=message,
            exitcode=exitcode,
        )


@TestFeature
@Name("broken")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values("1.0"))
def feature(self, node="clickhouse1"):
    """Check reading broken parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
