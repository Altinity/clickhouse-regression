from testflows.core import *
from testflows.asserts import error

from s3.tests.common import *


@TestOutline(Scenario)
def sanity(self, policy, server="clickhouse1"):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """
    name = "table_" + getuid()
    node = self.context.node

    def insert_data(number_of_mb, start=0):
        values = ",".join(
            f"({x})"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {name} VALUES {values}")

    def check_query(num, query, expected):
        with By(f"executing query {num}", description=query):
            r = node.query(query).output.strip()
            with Then(f"result should match the expected", description=expected):
                assert r == expected, error()

    try:
        with Given(f"I create table using storage policy {policy}"):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='{policy}'
            """
            )

        with When("I add data to the table"):
            with By("first inserting 1MB of data"):
                insert_data(1, 0)

            with And("another insert of 1MB of data"):
                insert_data(1, 1024 * 1024)

            with And("then doing a large insert of 10Mb of data"):
                insert_data(10, 1024 * 1024 * 2)

        with Then("I check simple queries"):
            check_query(0, f"SELECT COUNT() FROM {name}", expected="1572867")
            check_query(
                1, f"SELECT uniqExact(d) FROM {name} WHERE d < 10", expected="10"
            )
            check_query(
                2, f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1", expected="3407872"
            )
            check_query(3, f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1", expected="0")
            check_query(
                4,
                f"SELECT * FROM {name} WHERE d == 0 OR d == 1048578 OR d == 2097154 ORDER BY d",
                expected="0\n1048578\n2097154",
            )
            check_query(
                5, f"SELECT * FROM (SELECT d FROM {name} WHERE d == 1)", expected="1"
            )

    finally:
        with Finally("I drop the table if exists"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestFeature
@Name("aws s3 sanity")
def aws_s3(self, uri, key_id, access_key, node="clickhouse1"):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """
    self.context.node = self.context.cluster.node(node)

    with Given(
        """I have a disk configuration with a S3 storage disk, access id and keyprovided"""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "aws": {
                "type": "s3",
                "endpoint": f"{uri}",
                "access_key_id": f"{key_id}",
                "secret_access_key": f"{access_key}",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "aws_external": {"volumes": {"external": {"disk": "aws"}}},
        }

    with s3_storage(disks, policies, restart=True):
        Scenario(
            run=sanity, examples=Examples("policy", [("default",), ("aws_external",)])
        )


@TestFeature
@Name("minio sanity")
def minio(self, uri, key, secret, node="clickhouse1"):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """
    self.context.node = self.context.cluster.node(node)

    with Given("""I have a disk configuration with minio storage"""):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "minio": {
                "type": "s3",
                "endpoint": f"{uri}",
                "access_key_id": f"{key}",
                "secret_access_key": f"{secret}",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "minio_external": {"volumes": {"external": {"disk": "minio"}}},
        }

    with s3_storage(disks, policies, restart=True):
        Scenario(
            run=sanity, examples=Examples("policy", [("default",), ("minio_external",)])
        )
