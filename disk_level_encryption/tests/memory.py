from testflows.asserts import error
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *
from helpers.common import KeyWithAttributes

entries = {
    "storage_configuration": {
        "disks": [
            {},
            {
                "encrypted_local": {
                    "type": "encrypted",
                    "disk": "local",
                    "path": "encrypted/",
                }
            },
        ],
        "policies": {
            "local_encrypted": {
                "volumes": {"encrypted_disk": {"disk": "encrypted_local"}}
            }
        },
    }
}
expected_output = '{"Id":1,"Value":"hello"}\n{"Id":2,"Value":"there"}'


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_Memory("1.0"))
def memory_disk(self, node=None):
    """Check that ClickHouse supports disk level encryption for memory disk."""
    disk_local = "/disk_local"

    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up correct parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][0]["memory"] = {
            "type": "memory"
        }
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "disk"
        ] = "memory"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = "secondsecondseco"

    try:
        with And("I add storage configuration that uses encrypted disk"):
            add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

        with And("I create a table that uses encrypted disk"):
            table_name = create_table(policy="local_encrypted")

        with When("I insert data into the table"):
            values = "(1, 'hello'),(2, 'there')"
            insert_into_table(name=table_name, values=values)

        with Then("I expect data is successfully inserted"):
            r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
            assert r.output == expected_output, error()
    finally:
        node.restart()


@TestFeature
@Name("memory disk")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse supports disk level encryption for memory disk."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
