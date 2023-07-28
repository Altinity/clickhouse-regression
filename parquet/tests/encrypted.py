import os

from testflows.core import *
from parquet.requirements import *
from helpers.common import getuid


@TestOutline
def import_encrypted_file(self, file_name, error_message=None):
    node = self.context.node
    table_name = getuid()

    if error_message is None:
        message, code = ("Exception: IOError: Could not read encrypted metadata", 36)
    else:
        message, code = error_message

    with Given("I have an encrypted Parquet file"):
        import_file = os.path.join("encrypted", f"{file_name}")

    with When("I try to import the encrypted parquet file into the ClickHouse"):
        node.query(
            f"""
            CREATE TABLE {table_name}
            ENGINE = MergeTree
            ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
            """,
            message=message,
            exitcode=code,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Encryption_File("1.0"))
def column_and_metadata(self):
    """Checking that ClickHouse does not support importing Parquet files with encrypted columns and metadata."""
    import_encrypted_file(file_name="encrypt_columns_and_footer.parquet.encrypted")


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Encryption_Algorithms_AESGCM("1.0"))
def column_and_metadata_aad(self):
    """Checking that ClickHouse does not support importing Parquet files with AES GCM encrypted columns and metadata."""
    import_encrypted_file(file_name="encrypt_columns_and_footer_aad.parquet.encrypted")


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Encryption_Algorithms_AESGCMCTR("1.0"))
def column_and_metadata_ctr(self):
    """Checking that ClickHouse does not support importing Parquet files with AES CTR encrypted columns and metadata."""
    import_encrypted_file(file_name="encrypt_columns_and_footer_ctr.parquet.encrypted")


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Encryption_Parameters_Plaintext_Footer("1.0")
)
def column_and_plain_metadata(self):
    """Checking that ClickHouse does not support importing Parquet files with encrypted columns and plain text metadata."""
    import_encrypted_file(
        file_name="encrypt_columns_plaintext_footer.parquet.encrypted",
        error_message=("ParsingException: Error while reading Parquet data", 33),
    )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Encryption_File("1.0"))
def column_and_metadata_key(self):
    """Checking that ClickHouse does not support importing Parquet files with encrypted columns and metadata."""
    import_encrypted_file(file_name="external_key_material_java.parquet.encrypted")


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Encryption_File("1.0"))
def column_and_metadata_uniform(self):
    """Checking that ClickHouse does not support importing Parquet files with encrypted columns and metadata."""
    import_encrypted_file(file_name="uniform_encryption.parquet.encrypted")


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Encryption_File("1.0"))
def encrypted(self):
    """Check that when importing encrypted Parquet files without decryption the ClickHouse outputs an error."""
    Scenario(run=column_and_metadata)
    Scenario(run=column_and_metadata_aad)
    Scenario(run=column_and_metadata_ctr)
    Scenario(run=column_and_plain_metadata)
    Scenario(run=column_and_metadata_key)
    Scenario(run=column_and_metadata_uniform)


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Encryption_File("1.0"))
@Name("encrypted")
def feature(self, node="clickhouse1"):
    """Run checks for encrypted Parquet files."""
    self.context.node = self.context.cluster.node(node)

    Suite(run=encrypted)
