from testflows.core import *

from s3.tests.common import *


@TestOutline(Scenario)
def sanity(self, policy):
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
def aws_s3(self, uri):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume(uri=uri, disk_name="aws", policy_name="aws_external")

    Scenario(run=sanity, examples=Examples("policy", [("default",), ("aws_external",)]))


@TestFeature
@Name("sanity")
def minio(self, uri):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume(
            uri=uri, disk_name="minio", policy_name="minio_external"
        )

    Scenario(
        run=sanity, examples=Examples("policy", [("default",), ("minio_external",)])
    )


@TestFeature
@Name("sanity")
def gcs(self, uri):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume(uri=uri, disk_name="gcs", policy_name="gcs_external")

    Scenario(run=sanity, examples=Examples("policy", [("default",), ("gcs_external",)]))


@TestFeature
@Name("sanity")
def azure(self, uri):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume(
            uri=uri, disk_name="azure", policy_name="azure_external"
        )

    Scenario(
        run=sanity, examples=Examples("policy", [("default",), ("azure_external",)])
    )
