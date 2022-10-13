from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *


@TestFeature
@Requirements()
@Name("s3")
def feature(self, node="clickhouse1"):
    """Run checks for clickhouse using Parquet format using s3 storage."""

    xfail('Not implemented.')

    node = self.context.cluster.node(node)

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=self.context.access_key_id,
        aws_secret_access_key=self.context.secret_access_key,
    )
    with TestScenario("Write to s3 table engine"):

        table_name = "table_" + getuid()

        with Given(
            "I have a disk configuration with a S3 storage disk, access id and key"
        ):
            default_s3_disk_and_volume()

        with Given("I have a table."):
            table(
                name=table_name,
                engine=f"s3({self.context.uri}{table_name}, {self.context.access_key}, {self.context.key_id})",
            )

        with When("I insert some data."):
            insert_test_data(name=table_name)

        with Then("I check the file."):
            check_aws_s3_file(s3_client=s3_client, file=table_name)

    with TestScenario("Read from s3 table engine"):

        table_name = "s3_table"

        with Given(
            "I have a disk configuration with a S3 storage disk, access id and key"
        ):
            default_s3_disk_and_volume()

        with And("There is parquet data on s3"):
            upload_parquet_to_aws_s3(s3_client=s3_client)

        with When("I attach table"):
            table(
                name=table_name,
                create="ATTACH",
                engine=f"s3({self.context.uri}s3_table/data.Parquet, {self.context.access_key}, {self.context.key_id})",
            )

        with Then("I check the table"):
            check_query(query=f"SELECT * FROM {table_name}")

    with TestScenario("Write to s3 table function"):

        table_name = "table_" + getuid()

        with Given(
            "I have a disk configuration with a S3 storage disk, access id and key"
        ):
            default_s3_disk_and_volume()

        with When("I insert some data into the s3 function."):
            node.query(
                f"""
                INSERT INTO FUNCTION s3({self.context.uri}{table_name}, {self.context.access_key}, {self.context.key_id}, Parquet)
                SELECT (1,2,3,4,5,6,7,8,9,10,11,'2022-01-01','2022-01-01 00:00:00','A','B',[1,2,3],(1,2,3), {{'a':1, 'b',2}})
                """
            )

        with Then("I check the file."):
            check_aws_s3_file(s3_client=s3_client, file=table_name)

    with TestScenario("Read from s3 table function"):

        table_name = "s3_table"

        with Given(
            "I have a disk configuration with a S3 storage disk, access id and key"
        ):
            default_s3_disk_and_volume()

        with And("There is parquet data on s3"):
            upload_parquet_to_aws_s3(s3_client=s3_client)

        with When("I attach table"):
            table(
                name=table_name,
                create="ATTACH",
                engine=f"s3({self.context.uri}s3_table/data.Parquet, {self.context.access_key}, {self.context.key_id})",
            )

        with Then("I check the table"):
            check_query(query=f"SELECT * FROM {table_name}")
