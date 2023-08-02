from testflows.core import *

from s3.tests.common import *
from s3.requirements import *


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path("1.0"))
def empty_path(self):
    """Check that ClickHouse returns an error when the S3 table function path
    parameter is empty.
    """
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    node = current().context.node

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the table"):
            node.query(f"INSERT INTO {name} VALUES (427)")

        with Then(
            """When I export the data to S3 using the table function with
                  empty path parameter it should fail"""
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name}""",
                message="DB::Exception: Host is empty in S3 URI",
                exitcode=36,
            )

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path("1.0"))
def invalid_path(self):
    """Check that ClickHouse returns an error when the table function path
    parameter is invalid.
    """
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    node = current().context.node
    invalid_path = "https://invalid/path"

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the table"):
            node.query(f"INSERT INTO {name} VALUES (427)")

        with Then(
            """When I export the data to S3 using the table function with
                  invalid path parameter it should fail"""
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{invalid_path}', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name}""",
                message=f"DB::Exception: Bucket or key name are invalid in S3 URI",
                exitcode=36,
            )

    finally:
        with Finally("I drop the first table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestOutline(Scenario)
@Examples(
    "invalid_format",
    [("", Name("empty string")), ("not_a_format", Name("unknown format"))],
)
@Requirements(RQ_SRS_015_S3_TableFunction_Format("1.0"))
def invalid_format(self, invalid_format):
    """Check that ClickHouse returns an error when the table function format
    parameter is invalid.
    """
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the table"):
            node.query(f"INSERT INTO {name} VALUES (427)")

        with Then(
            """When I export the data to S3 using the table function with
                  invalid format parameter it should fail"""
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}invalid.csv', '{access_key_id}','{secret_access_key}', '{invalid_format}', 'd UInt64')
                SELECT * FROM {name}""",
                message="DB::Exception: Unknown format",
                exitcode=73,
            )

    finally:
        with Finally("I drop the first table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Structure("1.0"))
def empty_structure(self):
    """Check that ClickHouse returns an error when the table function structure
    parameter is empty.
    """
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the table"):
            node.query(f"INSERT INTO {name} VALUES (427)")

        with Then(
            """When I export the data to S3 using the table function with
                  empty structure parameter it should fail"""
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}invalid.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', '')
                SELECT * FROM {name}""",
                message="DB::Exception: Empty query",
                exitcode=62,
            )

    finally:
        with Finally("I drop the first table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Structure("1.0"))
def invalid_structure(self):
    """Check that ClickHouse returns an error when the table function structure
    parameter is invalid.
    """
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the table"):
            node.query(f"INSERT INTO {name} VALUES (427)")

        with Then(
            """When I export the data to S3 using the table function with
                  invalid structure parameter it should fail"""
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}invalid.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'not_a_structure')
                SELECT * FROM {name}""",
                message="DB::Exception: Syntax error",
                exitcode=62,
            )

    finally:
        with Finally("I drop the first table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Compression("1.0"))
def invalid_compression(self):
    """Check that ClickHouse returns an error when the table function compression
    parameter is invalid.
    """
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the table"):
            node.query(f"INSERT INTO {name} VALUES (427)")

        with Then(
            """When I export the data to S3 using the table function with
                  invalid compression parameter it should fail"""
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}invalid.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64', 'invalid_compression')
                SELECT * FROM {name}""",
                message="DB::Exception: Unknown compression method",
                exitcode=48,
            )

    finally:
        with Finally("I drop the first table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Credentials_Invalid("1.0"))
def invalid_credentials(self):
    """Check that ClickHouse throws an error when invalid bucket credentials
    are provided to the S3 table function.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = "invalid_id"
    secret_access_key = "invalid_key"
    uri = self.context.uri
    node = current().context.node
    expected = "DB::Exception:"
    
    with Given("I create a table"):
        node.query(
            f"""
            CREATE TABLE {name_table1} (
                d UInt64
            ) ENGINE = MergeTree()
            ORDER BY d"""
        )

    with And("I create a second table for comparison"):
        node.query(
            f"""
            CREATE TABLE {name_table2} (
                d UInt64
            ) ENGINE = MergeTree()
            ORDER BY d"""
        )

    with And(f"I store simple data in the first table {name_table1}"):
        node.query(f"INSERT INTO {name_table1} VALUES (427)")

    with When(
        """I export the data to S3 using the table function with invalid
               credentials, expecting failure"""
    ):
        node.query(
            f"""
            INSERT INTO FUNCTION
            s3('{uri}invalid.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
            SELECT * FROM {name_table1}""",
            message=expected,
            exitcode=243,
        )


@TestOutline(Feature)
@Requirements(RQ_SRS_015_S3_TableFunction("1.0"))
def outline(self):
    """Test S3 and S3 compatible storage through storage disks."""
    for scenario in loads(current_module(), Scenario):
        with allow_s3_truncate(self.context.node):
            scenario()


@TestFeature
@Requirements(RQ_SRS_015_S3_AWS_TableFunction("1.0"))
@Name("aws s3 invalid table function")
def aws_s3(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "aws_s3"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    outline()


@TestFeature
@Requirements(RQ_SRS_015_S3_GCS_TableFunction("1.0"))
@Name("gcs invalid table function")
def gcs(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "gcs"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    outline()


@TestFeature
@Requirements(RQ_SRS_015_S3_MinIO_TableFunction("1.0"))
@Name("minio invalid table function")
def minio(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "minio"
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    outline()
