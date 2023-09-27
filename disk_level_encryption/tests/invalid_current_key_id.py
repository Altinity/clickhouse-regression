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


@TestScenario
def empty_current_key_id(self, node=None):
    """Check that server returns an error when the <current_key_id>
    parameter is empty when more than one key is defined.
    """
    disk_local = "/disk_local"
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        key_id_0 = KeyWithAttributes("key", {"id": "0"})
        key_id_1 = KeyWithAttributes("key", {"id": "1"})
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_0
        ] = "firstfirstfirstf"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_1
        ] = "secondsecondseco"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "current_key_id"
        ] = ""

    with And("I add invalid storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Syntax error", restart=True
        )


@TestScenario
def current_key_id_not_refer(self, node=None):
    """Check that server returns an error when the <current_key_id>
    parameter does not refer to previously defined key.
    """
    disk_local = "/disk_local"
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        key_id_0 = KeyWithAttributes("key", {"id": "0"})
        key_id_1 = KeyWithAttributes("key", {"id": "1"})
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_0
        ] = "firstfirstfirstf"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            key_id_1
        ] = "secondsecondseco"
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "current_key_id"
        ] = "2"

    with And("I add invalid storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Exception", restart=True
        )


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Multiple_CurrentKeyId_Invalid(
        "1.0"
    )
)
@Name("invalid current key id")
def feature(self, node="clickhouse1"):
    """Check that server returns errors when configuration file contains invalid current key id."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
