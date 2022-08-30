from testflows.asserts import error
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *


@TestOutline
def invalid_path(self, path_parameter_name, path, message, node=None):
    """Check that clickhouse returns an error when disk path specified in
    configuration file is invalid.
    """
    node = self.context.node if node is None else node
    key_parameter_name = "key"
    key_value = "firstfirstfirstf"

    with Given("I create local disk folder on the server"):
        disk_local = "/disk_local"
        create_directory(path=disk_local)

    with And("I have the following entries for the configuration file"):
        entries = {
            "storage_configuration": {
                "disks": [
                    {"local": {"path": "$disk_local$/"}},
                    {
                        "encrypted_local": {
                            "type": "encrypted",
                            "disk": "local",
                            "$path_parameter_name$": "$path$",
                            "$key_parameter_name$": "$key_value$",
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
    with And("I add storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            message=message,
            entries=entries,
            format={
                "$disk_local$": disk_local,
                "$key_parameter_name$": key_parameter_name,
                "$key_value$": key_value,
                "$path_parameter_name$": path_parameter_name,
                "$path$": path,
            },
        )


@TestScenario
def invalid_path_without_forward_slash_in_the_end(self):
    """Check that Clickhouse returns an error when the forward slash
    is absent at the end of disk path.
    """
    invalid_path(
        path_parameter_name="path",
        path="encrypted",
        message="Exception: Disk path must ends with",
    )


@TestScenario
def invalid_long_path(self):
    """Check that Clickhouse returns an error when the disk path is too long."""
    invalid_path(path_parameter_name="path", path="1" * 1000 + "/", message="Exception")


@TestFeature
@Name("invalid path")
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_Invalid("1.0"))
def feature(self, node="clickhouse1"):
    """Check errors when specified path is invalid."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
