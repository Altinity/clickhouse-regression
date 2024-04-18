from testflows.core import *

from s3.tests.common import *
from s3.requirements import *


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path_Wildcard("1.0"))
def wildcard_performance(self):
    """Check the performance of using wildcards in s3 paths."""
    node = current().context.node
    uri = self.context.uri + "many_files/"
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key

    examples = [
        ("100", "one_file"),
        ("*", "star"),
        ("%3F", "question"),
        ("{220..250}", "range"),
        ("{1234,456,1982,200}", "nums"),
        ("{1234,456,1982,200,abc}", "nums_one_missing"),
    ]

    if self.context.storage == "minio":
        with Given("If using MinIO, clear objects on directory path to avoid error"):
            self.context.cluster.minio_client.remove_object(
                self.context.cluster.minio_bucket, "data"
            )

    with Given("I export to many S3 files"):
        for i in range(50):
            for j in range(5):
                node.query(
                    f"""INSERT INTO TABLE FUNCTION 
                    s3('{uri}partition_{{_partition_id}}/file_{j}.csv','{access_key_id}','{secret_access_key}','CSV','d UInt64') 
                    PARTITION BY d
                    SELECT * FROM numbers({i*1000}, 1000)"""
                )
        # pause('check minio')

    for wildcard, name in examples:
        with Example(name):
             with Then(f"""I query the data using the wildcard '{wildcard}'"""):
                t_start = time.time()
                r = node.query(
                    f"""SELECT * FROM s3('{uri}partition_{wildcard}/*', '{access_key_id}','{secret_access_key}', 'CSV', 'd UInt64')"""
                )
                metric(f"wildcard {name} ({wildcard})", time.time() - t_start, "s")
                assert r.output.strip() != "", error()


@TestOutline(Feature)
@Requirements(RQ_SRS_015_S3_TableFunction("1.0"))
def outline(self):
    """Test S3 and S3 compatible storage through storage disks."""

    for scenario in loads(current_module(), Scenario):
        with allow_s3_truncate(self.context.node):
            scenario()




@TestFeature
@Requirements(RQ_SRS_015_S3_AWS_TableFunction("1.0"))
@Name("table function")
def aws_s3(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "aws_s3"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    outline()

@TestFeature
@Requirements(RQ_SRS_015_S3_GCS_TableFunction("1.0"))
@Name("table function")
def gcs(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "gcs"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    outline()


@TestFeature
@Requirements(RQ_SRS_015_S3_MinIO_TableFunction("1.0"))
@Name("table function")
def minio(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "minio"
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    outline()
