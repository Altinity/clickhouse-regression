from testflows.asserts import error
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *
from helpers.common import KeyWithAttributes

entries = {
    "storage_configuration": {
        "disks": [
            {"local": {"path": "/disk_local/"}},
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
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_ApplicationOfChanges("1.0")
)
def application_of_changes(self, node=None):
    """Check that CLickHouse only applies changes to the encrypted disk definition
    in the config.xml on server restart.
    """
    disk_local = "/disk_local"

    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = "secondsecondseco"

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy="local_encrypted")

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with And("I set up parameters without restart"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = "firstfirstfirstf"

    with And(
        "I add invalid storage configuration that uses encrypted disk without restart"
    ):
        add_encrypted_disk_configuration(
            entries=entries_in_this_test, modify=True, restart=False
        )

    with Then("I expect error when try to select from table"):
        r = node.query(
            f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow",
            exitcode=80,
            message="Exception:",
        )


@TestFeature
@Name("application of changes")
def feature(self, node="clickhouse1"):
    """Check that CLickHouse only applies changes to the encrypted disk definition
    in the config.xml on server restart.
    """
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
