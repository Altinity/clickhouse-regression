import copy
from testflows.asserts import error
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *


@TestScenario
def default_path(self, node=None):
    """Check that without specifying path it specified as root of the disk"""
    node = self.context.node if node is None else node
    key_parameter_name = "key"
    key_value = "firstfirstfirstf"

    with Given("I create local disk folder on the server"):
        disk_local = "/disk_local"
        create_directory(path=disk_local)

    with And("I have the following entries for the configuration file"):
        wrong_entries = {
            "storage_configuration": {
                "disks": [
                    {"local": {"path": "$disk_local$/"}},
                    {
                        "encrypted_local": {
                            "type": "encrypted",
                            "disk": "local",
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
        add_encrypted_disk_configuration(
            entries=wrong_entries,
            format={
                "$disk_local$": disk_local,
                "$key_parameter_name$": key_parameter_name,
                "$key_value$": key_value,
            },
        )

    self.context.disk_path = disk_local
    self.context.policy = "local_encrypted"
    policy = self.context.policy

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy, partition_by_id=True)

    with Then("I restart server"):
        node.restart()

    with And("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == '{"Id":1,"Value":"hello"}\n{"Id":2,"Value":"there"}', error()

    with Then("I restart server"):
        node.restart()

    with Then("I recovery servery"):
        with Then("I move table on encrypted disk"):
            node.command("mkdir /disk_local/encrypted")
            node.command("mv /disk_local/store /disk_local/encrypted/")

        with By("I change configuration file"):
            correct_entries = copy.deepcopy(wrong_entries)
            correct_entries["storage_configuration"]["disks"][1]["encrypted_local"][
                "path"
            ] = "encrypted/"

            add_encrypted_disk_configuration(
                entries=correct_entries,
                restart=True,
                modify=True,
                format={
                    "$disk_local$": disk_local,
                    "$key_parameter_name$": key_parameter_name,
                    "$key_value$": key_value,
                },
            )

    with Then("I expect data is the same"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == '{"Id":1,"Value":"hello"}\n{"Id":2,"Value":"there"}', error()


@TestFeature
@Name("default path")
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_Default)
def feature(self, node="clickhouse1"):
    """Check ClickHouse support path which is not specified."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
