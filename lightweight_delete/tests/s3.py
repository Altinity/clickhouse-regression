from lightweight_delete.requirements import *
from lightweight_delete.tests.steps import *
from s3.tests.common import start_minio


entries = {
    "storage_configuration": {
        "disks": [
            {
                "disk_s3": {
                    "type": "s3",
                    "endpoint": "http://minio:9001/root/data/",
                    "access_key_id": "minio",
                    "secret_access_key": "minio123",
                }
            },
        ],
        "policies": {"s3": {"volumes": {"external_volume": {"disk": "disk_s3"}}}},
    }
}


@TestScenario
def s3(self, node=None):
    """Check that clickhouse support using DELETE on S3 disks."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I add configuration file"):
        add_disk_configuration(entries=entries, restart=True)

    with When("I create a table that uses s3 disk"):
        create_table(table_name=table_name, settings=f"SETTINGS storage_policy = 's3'")

    with When("I insert data into the table"):
        insert(
            table_name=table_name, partitions=5, parts_per_partition=1, block_size=100
        )

    with And("I check that data is successfully inserted"):
        r = node.query(f"SELECT count(*) FROM {table_name}")
        assert r.output == "500", error()

    with And("I check table stored on s3 disk"):
        r = node.query(
            f"SELECT DISTINCT disk_name FROM system.parts "
            f"WHERE table = '{table_name}'"
        )

        assert r.output == "disk_s3", error()

    with Then("I delete from table stored on s3 disk"):
        delete(table_name=table_name, condition="x<50")

    with Then("I expect data is successfully deleted"):
        r = node.query(f"SELECT count(*) FROM {table_name}")
        assert r.output == "250", error()
        r = node.query(f"SELECT count(*) FROM {table_name} WHERE x < 50")
        assert r.output == "0", error()


@TestFeature
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_S3Disks("1.0"))
@Name("s3")
def feature(self, node="clickhouse1"):
    """Check that clickhouse support using DELETE on S3 disks."""
    self.context.node = self.context.cluster.node(node)
    self.context.table_engine = "MergeTree"
    for scenario in loads(current_module(), Scenario):
        scenario()
