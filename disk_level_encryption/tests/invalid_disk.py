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
def disk_not_exist(self, policy=None, node=None):
    """Check that server returns an error when <disk> parameter он does not refer to a previously defined disk."""
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
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "disk"
        ] = "local7"

    with And("I add invalid storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Exception", restart=True
        )


@TestScenario
def parameter_is_empty(self, policy=None, node=None):
    """Check that server returns an error when <disk> parameter is empty in encrypted disk configuration."""
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
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "disk"
        ] = ""

    with And("I add invalid storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Exception", restart=True
        )


@TestScenario
def parameter_is_missing(self, policy=None, node=None):
    """Check that server returns an error when <disk> parameter is missing in encrypted disk configuration."""
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

    with And("I add invalid storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Exception", restart=True
        )


@TestFeature
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Disk_Invalid("1.0"))
@Name("invalid disk")
def feature(self, node="clickhouse1"):
    """Check that server returns errors when configuration file contains invalid disk in specifying encryption disk."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
