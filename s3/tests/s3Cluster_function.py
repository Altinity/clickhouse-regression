from testflows.core import *

from s3.tests.common import *


@TestScenario
def sanity(self, policy, uri):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """
    name = "table_" + getuid()
    node = self.context.node

    with Given(f"I create table using storage policy {policy}"):
        simple_table(node=node, name=name, policy='default')

    with When("I add data to the table"):
        standard_inserts(node=node, table_name=name)

    with When("I upload data to s3 minio"):
        node.query(f"INSERT INTO FUNCTION s3('{uri}{name}', 'minio_user', 'minio123', 'CSVWithNames', 'd UInt64') SELECT * FROM {name}")

    with Then("I check simple queries"):
        standard_selects(node=node, table_name=f"s3('{uri}{name}', 'minio_user', 'minio123', 'CSVWithNames', 'd UInt64')")



@TestFeature
@Name("s3Cluster")
def minio(self, uri):
    """Check that S3 storage is working correctly by
    storing data using different S3 policies.
    """

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume(
            uri=uri, disk_name="minio", policy_name="minio_external"
        )

    Scenario(test=sanity)(policy="minio_external", uri=uri)

