from testflows.core import *
from testflows.asserts import error

from s3.tests.common import getuid, s3_storage
from s3.requirements import *


@TestStep(Given)
def create_file_on_node(self, path, content, node=None):
    """Create file on node.

    :param path: file path
    :param content: file content
    """
    if node is None:
        node = self.context.node
    try:
        with By(f"creating file {path}"):
            node.command(f"cat <<HEREDOC > {path}\n{content}\nHEREDOC", exitcode=0)
        yield path
    finally:
        with Finally(f"I remove {path}"):
            node.command(f"rm -rf {path}", exitcode=0)


@TestStep(Given)
def set_envs_on_node(self, envs, node=None):
    """Set environment variables on node.

    :param envs: dictionary of env variables key=value
    """
    if node is None:
        node = self.context.node
    try:
        with By("setting envs"):
            for key, value in envs.items():
                node.command(f"export {key}={value}", exitcode=0)
        yield
    finally:
        with Finally(f"I unset envs"):
            for key in envs:
                node.command(f"unset {key}", exitcode=0)


@TestScenario
def iam_mode_auth(self):
    """Check that we can configure ClickHouse to use
    IAM mode authentication for S3 AWS storage.
    """
    table_name = "table_" + getuid()
    node = self.context.node
    region = self.context.aws_s3_region
    bucket = self.context.aws_s3_bucket
    uri = f"https://s3.{region}.amazonaws.com/{bucket}/data"
    web_identity_token = self.context.aws_s3_web_identity_token
    web_identity_token_path = "/aws_web_identity_token"
    expected = "123456"

    with Given("I create web identity token file"):
        create_file_on_node(path=web_identity_token_path, content=web_identity_token)

    with And("I set AWS environment variables"):
        envs = {
            "AWS_DEFAULT_REGION": self.context.aws_s3_default_region,
            "AWS_REGION": self.context.aws_s3_region,
            "AWS_ROLE_ARN": self.context.aws_s3_arn,
            "AWS_WEB_IDENTITY_TOKEN_FILE": web_identity_token_path,
        }
        set_envs_on_node(envs=envs)

    with And(
        "I have a disk configuration with a S3 storage disk, access id and keyprovided"
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "aws": {
                "type": "s3",
                "endpoint": f"{uri}",
                "use_environment_credentials": "1",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "aws_external": {"volumes": {"external": {"disk": "aws"}}},
        }

    with s3_storage(disks, policies, restart=True, nodes=[node]):
        try:
            with Given(f"I create table using S3 storage policy external"):
                node.query(
                    f"""
                    CREATE TABLE {table_name} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    SETTINGS storage_policy='aws_external'
                """
                )

            with And("I store simple data in S3 to check import"):
                node.query(f"INSERT INTO {table_name} VALUES ({expected})")

            with Then("I check that select returns matching data"):
                r = node.query(f"SELECT * FROM {table_name}").output.strip()
                assert r == expected, error()
        finally:
            with Finally("I drip table that uses S3"):
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestFeature
@Name("iam mode")
def feature(self, node="clickhouse1"):
    """Run manual tests for AWS S3 IAM mode authentication."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
