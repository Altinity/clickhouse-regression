from testflows.asserts import error
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *

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
def missing_key(self, node=None):
    """Check that Clickhouse returns an error if any key that is needed for decryption is missing."""
    disk_local = "/disk_local"
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = "firstfirstfirstf"

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy="local_encrypted")

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with And("I change key"):
        del entries_in_this_test["storage_configuration"]["disks"][1][
            "encrypted_local"
        ]["key"]

    with Then("server should not start"):
        recover_entries = copy.deepcopy(entries)
        recover_entries["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = "firstfirstfirstf"
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test,
            recover_entries=recover_entries,
            message="Exception",
            restart=True,
        )

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestScenario
def changed_key(self, node=None):
    """Check that Clickhouse returns an error if any key that is needed for decryption is changed."""
    disk_local = "/disk_local"
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = "firstfirstfirstf"

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy="local_encrypted")

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with And("I change key"):
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = "secondsecondseco"

    with Then("server should not start"):
        recover_entries = copy.deepcopy(entries)
        recover_entries["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = "firstfirstfirstf"
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test,
            recover_entries=recover_entries,
            message="Exception",
            restart=True,
        )

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestFeature
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Missing("1.0"))
@Name("missing key")
def feature(self, node="clickhouse1"):
    """Check that clickhouse returns an error if key that is needed for decryption is absent."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
