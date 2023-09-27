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
expected_output = '{"Id":1,"Value":"hello"}\n{"Id":2,"Value":"there"}\n{"Id":3,"Value":"hello"}\n{"Id":4,"Value":"there"}'


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_HexKeyConflict("1.0")
)
def hex_key_conflict(self, node=None):
    """Check that Clickhouse returns an error when both key_hex and key parameters are defined
    without id.
    """
    disk_local = "/disk_local"
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        key_hex_id_0 = "key_hex"
        key_id_0 = "key"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_hex_id_0
        ] = "efadfdfdfdfdfdfaefadfdfdfdfdfdfa"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_0
        ] = "secondsecondseco"

    with And("I add storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Exception", restart=True
        )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_HexKeyIdConflict(
        "1.0"
    )
)
def hex_key_id_conflict(self, node=None):
    """Check that Clickhouse returns an error when both key_hex and key parameters are defined
    with the same id.
    """
    disk_local = "/disk_local"
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        key_hex_id_0 = KeyWithAttributes("key_hex", {"id": "0"})
        key_id_0 = KeyWithAttributes("key", {"id": "0"})
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_hex_id_0
        ] = "efadfdfdfdfdfdfaefadfdfdfdfdfdfa"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_0
        ] = "secondsecondseco"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "current_key_id"
        ] = "0"

    with And("I add storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Exception", restart=True
        )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_Id_Invalid("1.0")
)
def invalid_key_id(self, node=None):
    """Check that Clickhouse returns an error when encryption key id is invalid."""
    disk_local = "/disk_local"
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        key_id_negative_1 = KeyWithAttributes("key", {"id": "-1"})
        key_id_0 = KeyWithAttributes("key", {"id": "0"})
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_negative_1
        ] = "firstfirstfirstf"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_0
        ] = "secondsecondseco"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "current_key_id"
        ] = "0"

    with And("I add storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Syntax error", restart=True
        )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_CurrentKeyId("1.0")
)
def parts_with_different_keys(self, node=None):
    """Check that ClickHouse support specifying current key id to use different encryption keys for different parts."""
    disk_local = "/disk_local"

    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        key_id_1 = KeyWithAttributes("key", {"id": "1"})
        key_id_0 = KeyWithAttributes("key", {"id": "0"})
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_1
        ] = "firstfirstfirstf"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_0
        ] = "secondsecondseco"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "current_key_id"
        ] = "0"

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy="local_encrypted")

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with And("I change current_key_id"):
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "current_key_id"
        ] = "1"
        add_encrypted_disk_configuration(
            modify=True, restart=True, entries=entries_in_this_test
        )

    with And("I insert data into the table second time"):
        values = "(3, 'hello'),(4, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()
    with And("I restart server"):
        node.restart()

    with And("I expect data didn't change after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_CurrentKeyId_Default(
        "1.0"
    )
)
def default_current_key_id(self, node=None):
    """Check that without specifying current key id it specified as 0."""
    disk_local = "/disk_local"

    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up invalid parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        key_id_1 = KeyWithAttributes("key", {"id": "1"})
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_1
        ] = "firstfirstfirstf"

    with And("I add storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, restart=True, message="Exception"
        )

    with And("I set up correct parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        key_id_0 = KeyWithAttributes("key", {"id": "0"})
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_0
        ] = "secondsecondseco"

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy="local_encrypted")

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == '{"Id":1,"Value":"hello"}\n{"Id":2,"Value":"there"}', error()

    with And("I restart server"):
        node.restart()

    with And("I expect data didn't change after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == '{"Id":1,"Value":"hello"}\n{"Id":2,"Value":"there"}', error()


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_MixedFormats("1.0")
)
def mixed_formats(self, node=None):
    """Check we can use different types of keys for different parts."""
    disk_local = "/disk_local"

    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        key_hex_id_1 = KeyWithAttributes("key_hex", {"id": "1"})
        key_id_0 = KeyWithAttributes("key", {"id": "0"})
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_hex_id_1
        ] = "efadfdfdfdfdfdfaefadfdfdfdfdfdfa"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_0
        ] = "secondsecondseco"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "current_key_id"
        ] = "0"

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy="local_encrypted")

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with And("I change current_key_id"):
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "current_key_id"
        ] = "1"
        add_encrypted_disk_configuration(
            modify=True, restart=True, entries=entries_in_this_test
        )

    with And("I insert data into the table second time"):
        values = "(3, 'hello'),(4, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()
    with And("I restart server"):
        node.restart()

    with And("I expect data didn't change after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestFeature
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple("1.0"))
@Name("multiple keys")
def feature(self, node="clickhouse1"):
    """Check that clickhouse supports multiple keys for encrypted disk."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
