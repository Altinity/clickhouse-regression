from testflows.core import *

from s3.tests.common import *
from s3.requirements import *


@TestStep(Given)
def insert_to_s3_function_invalid(
    self,
    path,
    table_name,
    columns="d UInt64",
    compression=None,
    file_format="CSVWithNames",
    message=None,
    exitcode=None,
    timeout=60,
):
    """Write a table to a file in s3. File will be overwritten from an empty table during cleanup."""

    node = current().context.node

    query = f"INSERT INTO FUNCTION s3(s3_credentials, url='{path}', format='{file_format}', structure='{columns}'"

    if compression:
        query += f", compression_method='{compression}'"

    query += f") SELECT * FROM {table_name}"

    node.query(query, message=message, exitcode=exitcode, timeout=timeout)


@TestStep(When)
def insert_from_s3_function_invalid(
    self,
    filename,
    table_name,
    columns="d UInt64",
    compression=None,
    fmt=None,
    uri=None,
    message=None,
    exitcode=None,
    timeout=60,
):
    """Import data from a file in s3 to a table and catch fail."""
    uri = uri or self.context.uri
    node = current().context.node

    query = f"INSERT INTO {table_name} SELECT * FROM s3(s3_credentials, url='{uri}{filename}', format='CSVWithNames', structure='{columns}'"

    if compression:
        query += f", compression_method='{compression}'"

    query += ")"

    if fmt:
        query += f" FORMAT {fmt}"

    node.query(query, message=message, exitcode=exitcode, timeout=timeout)


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path("1.0"))
def empty_path(self):
    """Check that ClickHouse returns an error when the S3 table function path
    parameter is empty.
    """
    name = "table_" + getuid()
    node = current().context.node

    with Given("I create a table"):
        simple_table(node=node, name=name, policy="default")

    with And(f"I store simple data in the table"):
        node.query(f"INSERT INTO {name} VALUES (427)")

    with Then(
        """When I export the data to S3 using the table function with
                empty path parameter it should fail"""
    ):
        if check_clickhouse_version("<23")(self):
            message = "DB::Exception: Storage requires url"
        else:
            message = "DB::Exception: Host is empty in S3 URI"

        insert_to_s3_function_invalid(
            table_name=name,
            path="",
            message=message,
            exitcode=36,
        )


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path("1.0"))
def invalid_path(self):
    """Check that ClickHouse returns an error when the table function path
    parameter is invalid.
    """
    invalid_path = "https://invalid/path"

    with Then(
        """When I export the data to S3 using the table function with
                invalid path parameter it should fail"""
    ):
        if check_clickhouse_version("<24.9")(self):
            message = "DB::Exception: Bucket or key name are invalid in S3 URI"
            exitcode = 36
        else:
            message = "DB::NetException: Not found address of host"
            exitcode = 243

        insert_to_s3_function_invalid(
            table_name="numbers(10)",
            path=invalid_path,
            message=message,
            exitcode=exitcode,
            timeout=30,
        )


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path("1.0"))
def invalid_wildcard(self):
    """Check that ClickHouse returns an error when the wildcard in path is invalid."""

    table1_name = "table_" + getuid()
    table2_name = "table_" + getuid()
    node = current().context.node

    wildcard_invalid = define("wildcard_invalid", "{1,2}")

    if self.context.storage == "minio":
        with Given("If using MinIO, clear objects on directory path to avoid error"):
            self.context.cluster.minio_client.remove_object(
                self.context.cluster.minio_bucket, "data"
            )

    with Given("I create a table"):
        simple_table(node=node, name=table1_name, policy="default")

    with And("I create a second table for comparison"):
        simple_table(node=node, name=table2_name, policy="default")

    with And(f"I store simple data in the first table {table1_name}"):
        node.query(f"INSERT INTO {table1_name} VALUES (427)")

    with And("I export the data to my bucket"):
        insert_to_s3_function(filename="subdata1", table_name=table1_name)

    with Then(
        f"""I import the data from external storage into the second
            table {table2_name} using the invalid wildcard '{wildcard_invalid}' 
            and check output"""
    ):
        insert_from_s3_function_invalid(
            filename=f"subdata{wildcard_invalid}",
            table_name=table2_name,
            message="DB::Exception: Failed to get object info",
            exitcode=243,
        )


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path("1.0"))
def invalid_bucket(self):
    """Check that ClickHouse returns an error when the table function path
    parameter has invalid bucket.
    """
    invalid_path = self.context.uri.replace(self.context.bucket_name, "invalid-bucket")

    with Then(
        """When I export the data to S3 using the table function with
                invalid path parameter it should fail"""
    ):
        if (
            self.context.storage == "aws_s3"
            and check_clickhouse_version(">=23")(self)
            and check_clickhouse_version("<24.12")(self)
        ):
            exitcode = 36
        else:
            exitcode = 243

        insert_to_s3_function_invalid(
            table_name="numbers(10)",
            path=invalid_path,
            message="DB::Exception:",
            exitcode=exitcode,
            timeout=30,
        )


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path("1.0"))
def invalid_region(self):
    """Check that ClickHouse returns an error when the table function path
    parameter has invalid region.
    """
    if not hasattr(self.context, "region"):
        skip("Region is not set")

    invalid_path = self.context.uri.replace(self.context.region, "invalid-region")

    with Then(
        """When I export the data to S3 using the table function with
                invalid path parameter it should fail"""
    ):
        if check_clickhouse_version(">=24")(self):
            message = "DB::NetException: Not found address of host"
        else:
            message = "DB::Exception: Not found address of host"

        insert_to_s3_function_invalid(
            table_name="numbers(10)",
            path=invalid_path,
            message=message,
            exitcode=243,
            timeout=30,
        )


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
    uri = self.context.uri
    node = current().context.node

    with Given("I create a table"):
        simple_table(node=node, name=name, policy="default")

    with And(f"I store simple data in the table"):
        node.query(f"INSERT INTO {name} VALUES (427)")

    with Then(
        """When I export the data to S3 using the table function with
                invalid format parameter it should fail"""
    ):
        if check_clickhouse_version("<23")(self) and invalid_format == "":
            message = "DB::Exception: Storage requires format"
            exitcode = 36
        else:
            message = "DB::Exception: Unknown format"
            exitcode = 73

        insert_to_s3_function_invalid(
            table_name=name,
            path=f"{uri}invalid.csv",
            file_format=invalid_format,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Structure("1.0"))
def empty_structure(self):
    """Check that ClickHouse returns an error when the table function structure
    parameter is empty.
    """
    name = "table_" + getuid()
    uri = self.context.uri
    node = current().context.node

    with Given("I create a table"):
        simple_table(node=node, name=name, policy="default")

    with And(f"I store simple data in the table"):
        node.query(f"INSERT INTO {name} VALUES (427)")

    with Then(
        """When I export the data to S3 using the table function with
                empty structure parameter it should fail"""
    ):
        insert_to_s3_function_invalid(
            table_name=name,
            path=f"{uri}invalid.csv",
            columns="",
            message="DB::Exception: Empty query",
            exitcode=62,
        )


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

    with Given("I create a table"):
        simple_table(node=node, name=name, policy="default")

    with And(f"I store simple data in the table"):
        node.query(f"INSERT INTO {name} VALUES (427)")

    with Then(
        """When I export the data to S3 using the table function with
                invalid structure parameter it should fail"""
    ):
        insert_to_s3_function_invalid(
            table_name=name,
            path=f"{uri}invalid.csv",
            columns="not_a_structure",
            message="DB::Exception: Syntax error",
            exitcode=62,
        )


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

    with Given("I create a table"):
        simple_table(node=node, name=name, policy="default")

    with And(f"I store simple data in the table"):
        node.query(f"INSERT INTO {name} VALUES (427)")

    with Then(
        """When I export the data to S3 using the table function with
                invalid compression parameter it should fail"""
    ):
        insert_to_s3_function_invalid(
            table_name=name,
            path=f"{uri}invalid.csv",
            compression="invalid_compression",
            message="DB::Exception: Unknown compression method",
            exitcode=48,
        )


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
        simple_table(node=node, name=name_table1, policy="default")

    with And("I create a second table for comparison"):
        simple_table(node=node, name=name_table2, policy="default")

    with And(f"I store simple data in the first table {name_table1}"):
        node.query(f"INSERT INTO {name_table1} VALUES (427)")

    with When(
        """I export the data to S3 using the table function with invalid
               credentials, expecting failure"""
    ):
        query = f"INSERT INTO FUNCTION s3('{uri}invalid.csv', '{access_key_id}', '{secret_access_key}', 'CSV', 'd UInt64') SELECT * FROM {name_table1}"
        node.query(query, message=expected, exitcode=243)


@TestOutline(Feature)
@Requirements(RQ_SRS_015_S3_TableFunction_S3("1.0"))
def outline(self, uri):
    """Test S3 and S3 compatible storage through storage disks."""

    self.context.uri = uri

    with Given("I add S3 credentials configuration"):
        named_s3_credentials(
            access_key_id=self.context.access_key_id,
            secret_access_key=self.context.secret_access_key,
            restart=True,
        )

    for scenario in loads(current_module(), Scenario):
        with allow_s3_truncate(self.context.node):
            scenario()


@TestFeature
@Requirements(RQ_SRS_015_S3_AWS_TableFunction("1.0"))
@Name("invalid table function")
def aws_s3(self, uri):

    outline(uri=uri)


@TestFeature
@Requirements(RQ_SRS_015_S3_GCS_TableFunction("1.0"))
@Name("invalid table function")
def gcs(self, uri):

    outline(uri=uri)


@TestFeature
@Requirements(RQ_SRS_015_S3_MinIO_TableFunction("1.0"))
@Name("invalid table function")
def minio(self, uri):

    outline(uri=uri)
