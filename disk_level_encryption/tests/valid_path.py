from testflows.asserts import error
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *


@TestOutline
def valid_path(self, path_parameter_name, path, policy=None, node=None):
    """Check valid disk path."""
    node = self.context.node if node is None else node
    self.context.policy = "local_encrypted"
    policy = self.context.policy if policy is None else policy
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
        add_encrypted_disk_configuration(
            entries=entries,
            format={
                "$disk_local$": disk_local,
                "$key_parameter_name$": key_parameter_name,
                "$key_value$": key_value,
                "$path_parameter_name$": path_parameter_name,
                "$path$": path,
            },
        )

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy)

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == '{"Id":1,"Value":"hello"}\n{"Id":2,"Value":"there"}', error()


@TestScenario
def path_utf8(self):
    """Check disk path that contains UTF-8 characters."""
    valid_path(path_parameter_name="path", path="нпуёЁВПВ/")


@TestScenario
def path_ascii(self):
    """Check disk path that only contains ASCII characters."""
    valid_path(path_parameter_name="path", path="{~j=:;!/()*|^%@$/")


@TestScenario
def path_nested(self):
    """Check disk path that uses nested folders."""
    valid_path(path_parameter_name="path", path="foo/bar/zoo/")


@TestFeature
@Name("valid path")
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path("1.0"))
def feature(self, node="clickhouse1"):
    """Check valid disk paths."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
