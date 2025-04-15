from testflows.core import *
from hive_partitioning.tests.steps import *
from hive_partitioning.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_S3("1.0"),
)
def s3(self,uri, minio_root_user, minio_root_password, node=None):
    """Run generic writes test."""
    
    if node is None:
        node = self.context.node
    pause()
    with Given("I create table"):
        create_table(
            table_name="generic_s3",
            engine=f"S3(url = '{uri}', access_key_id = '{minio_root_user}', secret_access_key = '{minio_root_password}', format = 'CSV', compression_method='gzip', filename='generic_s3')",
            partition_by="d", 
            node=node
        )

    with When("I insert data into table"):
        insert_into_table_select(node=node, table_name="generic_s3", select_statement="SELECT 1", settings="")

    with Then("I check data in table"):
        check_select(select="SELECT * FROM generic_s3", expected_result="1", node=node)


@TestFeature
@Name("generic")
def feature(self, uri=None, minio_root_user=None, minio_root_password=None):
    """Run generic writes test."""
    if uri is None:
        uri = self.context.uri
    if minio_root_user is None:
        minio_root_user = self.context.root_user
    if minio_root_password is None:
        minio_root_password = self.context.root_password
        
    for scenario in loads(current_module(), Scenario):
        Feature(
            test=scenario,
        )(uri=uri, minio_root_user=minio_root_user, minio_root_password=minio_root_password)