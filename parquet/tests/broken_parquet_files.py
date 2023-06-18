import os
from testflows import *
from testflows.core import *
from parquet.requirements import *
from helpers.common import *

error_message = "DB::Exception: Cannot extract table structure from Parquet format file."


@TestScenario
def read_broken_date(self):
    node = self.context.node

    with Given("I have a Parquet file with broken date value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet', 'broken_date.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )


@TestScenario
def read_broken_int(self):
    node = self.context.node

    with Given("I have a Parquet file with broken int value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet', 'broken_int.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )


@TestScenario
def read_broken_bigint(self):
    node = self.context.node

    with Given("I have a Parquet file with broken bigint value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet', 'broken_bigint.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )


@TestScenario
def read_broken_smallint(self):
    node = self.context.node

    with Given("I have a Parquet file with broken smallint value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet',
                                           'broken_smallint.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )


@TestScenario
def read_broken_tinyint(self):
    node = self.context.node

    with Given("I have a Parquet file with broken tinyint value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet',
                                           'broken_tinyint.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )


@TestScenario
def read_broken_uint(self):
    node = self.context.node

    with Given("I have a Parquet file with broken uint value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet',
                                           'broken_uinteger.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )


@TestScenario
def read_broken_ubigint(self):
    node = self.context.node

    with Given("I have a Parquet file with broken ubigint value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet',
                                           'broken_ubigint.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )


@TestScenario
def read_broken_usmallint(self):
    node = self.context.node

    with Given("I have a Parquet file with broken usmallint value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet',
                                           'broken_usmallint.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )

@TestScenario
def read_broken_utinyint(self):
    node = self.context.node

    with Given("I have a Parquet file with broken usmallint value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet',
                                           'broken_utinyint.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )

@TestScenario
def read_broken_timestamp_ms(self):
    node = self.context.node

    with Given("I have a Parquet file with broken timestamp (ms) value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet',
                                           'broken_timestamp_ms.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )


@TestScenario
def read_broken_timestamp(self):
    node = self.context.node

    with Given("I have a Parquet file with broken timestamp value"):
        broken_date_parquet = os.path.join(current_dir(), '..', 'test_files', 'broken_parquet',
                                           'broken_timestamp.parquet')

    with When("I try to import the broken Parquet file into the table"):
        node.query(
            f"""
            CREATE TABLE imported_from_parquet 
            ENGINE = MergeTree 
            ORDER BY tuple() AS SELECT * FROM file({broken_date_parquet}, Parquet)
            """,
            message=error_message,
            exitcode=636
        )


@TestFeature
@Name("broken parquet files")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues("1.0"))
def feature(self):
    """Check reading broken parquet files."""
    Scenario(run=read_broken_bigint)
    Scenario(run=read_broken_timestamp)
    Scenario(run=read_broken_timestamp_ms)
    Scenario(run=read_broken_utinyint)
    Scenario(run=read_broken_usmallint)
    Scenario(run=read_broken_ubigint)
    Scenario(run=read_broken_uint)
    Scenario(run=read_broken_tinyint)
    Scenario(run=read_broken_smallint)
    Scenario(run=read_broken_int)
    Scenario(run=read_broken_date)


feature()
