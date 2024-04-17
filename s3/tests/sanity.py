from testflows.core import *

from s3.tests.common import *


@TestOutline(Scenario)
def sanity(self, policy, server="clickhouse1"):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """
    name = "table_" + getuid()
    node = self.context.node

    with Given(f"I create table using storage policy {policy}"):
        simple_table(node=node, name=name, policy=policy)

    with When("I add data to the table"):
        standard_inserts(node=node, table_name=name)

    with Then("I check simple queries"):
        standard_selects(node=node, table_name=name)


@TestFeature
@Name("sanity")
def aws_s3(self, uri, key_id, access_key, node="clickhouse1"):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """
    self.context.node = self.context.cluster.node(node)

    with Given(
        """I have a disk configuration with a S3 storage disk, access id and key provided"""
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
        if self.context.object_storage_mode == "vfs":
            disks["aws"]["allow_vfs"] = "1"

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "aws_external": {"volumes": {"external": {"disk": "aws"}}},
        }

    with And("I enable the disk and policy config"):
        s3_storage(disks=disks, policies=policies, restart=True)

    Scenario(run=sanity, examples=Examples("policy", [("default",), ("aws_external",)]))


@TestFeature
@Name("sanity")
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
        if self.context.object_storage_mode == "vfs":
            disks["minio"]["allow_vfs"] = "1"

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "minio_external": {"volumes": {"external": {"disk": "minio"}}},
        }

    with And("I enable the disk and policy config"):
        s3_storage(disks=disks, policies=policies, restart=True)

    Scenario(
        run=sanity, examples=Examples("policy", [("default",), ("minio_external",)])
    )
