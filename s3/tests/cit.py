import json
import tempfile
import random
from testflows.core import *

from s3.tests.common import *
from s3.requirements import *

import helpers.cluster


@TestOutline(Scenario)
@Requirements(RQ_SRS_015_S3_TableFunction_Syntax("1.0"))
@Examples(
    "maybe_auth positive",
    [
        ("", True, Name("empty auth")),
        ("'minio', 'minio123',", True, Name("minio auth")),
        ("'wrongid', 'wrongkey',", False, Name("invalid auth")),
    ],
)
def test_put(self, maybe_auth, positive):
    """Check that simple put operations via the S3 table function work with
    MinIO storage.
    """

    cluster = self.context.cluster
    bucket = cluster.minio_bucket if not maybe_auth else cluster.minio_restricted_bucket
    instance = self.context.node
    uri = self.context.uri + f"/{bucket}/test.csv"

    with Given("I set the query parameters and csv file values"):
        table_format = "column1 UInt32, column2 UInt32, column3 UInt32"
        values = "(1, 2, 3), (3, 2, 1), (78, 43, 45)"
        values_csv = "1,2,3\n3,2,1\n78,43,45\n"
        put_query = (
            "insert into table function s3('{}', {} 'CSV', '{}') values {}".format(
                uri, maybe_auth, table_format, values
            )
        )

    with Then("I insert simple data to MinIO"):
        try:
            run_query(instance=instance, query=put_query)
        except helpers.cluster.QueryRuntimeException:
            if positive:
                raise
        else:
            assert positive
            assert values_csv == get_s3_file_content(
                cluster=cluster, bucket=bucket, filename="test.csv"
            )


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Syntax("1.0"))
def test_empty_put(self, auth="'minio','minio123'"):
    """Check that an empty put operation via the S3 table function does not
    store any data.
    """

    cluster = self.context.cluster
    bucket = cluster.minio_bucket
    instance = self.context.node
    uri = self.context.uri + f"/{bucket}/empty_put_test.csv"

    try:
        with Given("I create an empty table"):
            table_format = "column1 UInt32, column2 UInt32, column3 UInt32"

            create_empty_table_query = """
                CREATE TABLE empty_table (
                {}
                ) ENGINE = Null()
            """.format(
                table_format
            )

            run_query(instance=instance, query=create_empty_table_query)

        with Then("I store empty data using the table function"):
            put_query = "insert into table function s3('{}', {}, 'CSV', '{}') select * from empty_table".format(
                uri, auth, table_format
            )

            try:
                run_query(instance=instance, query=put_query)

            except helpers.cluster.QueryRuntimeException as e:
                assert str(e).find("The specified key does not exist") != 0

    finally:
        with Finally("I remove the table if it was created"):
            delete_table_query = "DROP TABLE IF EXISTS empty_table SYNC"
            run_query(instance=instance, query=delete_table_query)


@TestOutline(Scenario)
@Requirements(RQ_SRS_015_S3_TableFunction_ReadFromFile("1.0"))
@Examples(
    "maybe_auth positive",
    [
        ("", True, Name("empty auth")),
        ("'minio', 'minio123',", True, Name("minio auth")),
        ("'wrongid', 'wrongkey',", False, Name("invalid auth")),
    ],
)
def test_put_csv(self, maybe_auth, positive):
    """Check that the S3 table function can be used to store data from a file."""

    cluster = self.context.cluster
    bucket = cluster.minio_bucket if not maybe_auth else cluster.minio_restricted_bucket
    instance = self.context.node
    uri = self.context.uri + f"/{bucket}/test_csv.csv"

    with Given("I store data in S3 from a csv file"):
        table_format = "column1 UInt32, column2 UInt32, column3 UInt32"
        put_query = (
            "insert into table function s3('{}', {} 'CSV', '{}') format CSV".format(
                uri, maybe_auth, table_format
            )
        )
        csv_data = "8,9,16\n11,18,13\n22,14,2"

    with Then("I check that the data returned from S3 matches the data in the file"):
        try:
            run_query(instance=instance, query=put_query, stdin=csv_data)
        except helpers.cluster.QueryRuntimeException:
            if positive:
                raise
        else:
            result = get_s3_file_content(
                cluster=cluster, bucket=bucket, filename="test_csv.csv"
            )
            if positive:
                assert csv_data + "\n" == get_s3_file_content(
                    cluster=cluster, bucket=bucket, filename="test_csv.csv"
                ), error()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Redirect("1.0"))
def test_put_get_with_redirect(self):
    """Check that the S3 table function works correctly when the specified URL
    causes a redirect.
    """

    cluster = self.context.cluster
    bucket = cluster.minio_bucket
    instance = self.context.node
    minio_redirect_uri = f"http://proxy1:8080/{bucket}/test.csv"

    with Given("I set up the query parameters"):
        table_format = "column1 UInt32, column2 UInt32, column3 UInt32"
        values = "(1, 1, 1), (1, 1, 1), (11, 11, 11)"
        values_csv = "1,1,1\n1,1,1\n11,11,11"
        query = "insert into table function s3('{}', 'CSV', '{}') values {}".format(
            minio_redirect_uri, table_format, values
        )

    with Then("I insert data at the target address 'proxy1'"):
        run_query(instance, query)

    with And("I check that the output matches expected values"):
        assert values_csv + "\n" == get_s3_file_content(cluster, bucket, "test.csv")

    with And("I make sure that the data returned from 'proxy1' matches"):
        query = "select *, column1*column2*column3 from s3('{}', 'CSV', '{}')".format(
            minio_redirect_uri, table_format
        )
        stdout = run_query(instance, query)

        assert list(map(str.split, stdout.splitlines())) == [
            ["1", "1", "1", "1"],
            ["1", "1", "1", "1"],
            ["11", "11", "11", "1331"],
        ]


@TestFeature
@Name("cit")
@Requirements()
def feature(self, uri, node="clickhouse1"):
    """Test ClickHouse integration tests."""
    cluster = self.context.cluster
    self.context.node = cluster.node(node)
    self.context.uri = uri

    bucket_read_write_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:GetBucketLocation",
                "Resource": "arn:aws:s3:::root",
            },
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:ListBucket",
                "Resource": "arn:aws:s3:::root",
            },
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::root/*",
            },
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:PutObject",
                "Resource": "arn:aws:s3:::root/*",
            },
        ],
    }

    minio_client = cluster.minio_client
    minio_client.set_bucket_policy(
        cluster.minio_bucket, json.dumps(bucket_read_write_policy)
    )

    cluster.minio_restricted_bucket = "{}-with-auth".format(cluster.minio_bucket)
    if minio_client.bucket_exists(cluster.minio_restricted_bucket):
        minio_client.remove_bucket(cluster.minio_restricted_bucket)

    minio_client.make_bucket(cluster.minio_restricted_bucket)

    for scenario in loads(current_module(), Scenario):
        with allow_s3_truncate(self.context.node):
            scenario()
