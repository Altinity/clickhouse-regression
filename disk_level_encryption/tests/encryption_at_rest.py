from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *

entries = {
    "storage_configuration": {
        "disks": [
            {"local": {"type": "local", "path": "/var/lib/clickhouse/"}},
            {
                "encrypted_local": {
                    "type": "encrypted",
                    "disk": "local",
                    "path": "encrypted/",
                    "key": "firstfirstfirstf",
                }
            },
        ],
        "policies": {"default": {"volumes": {"default": {"disk": "encrypted_local"}}}},
    }
}


@TestScenario
def corner_case_check(self, node=None):
    """Check a corner case regarding encrypted disks and optimize_read_in_order setting."""
    table_name = f"table_{getuid()}"

    if node is None:
        node = self.context.node

    with Given("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries, restart=True)

    with And("I create a table that uses encrypted disk"):
        node.query(
            f"""CREATE TABLE {table_name}
            (
            a UInt64,
            b String(150)
            )
            ENGINE = MergeTree()
            ORDER BY (a, b)"""
        )

    with When("I insert data into the table"):
        node.query(
            f"INSERT INTO {table_name} SELECT * FROM generateRandom('a UInt64, b FixedString(150)') LIMIT 75000;"
        )

    with Then("I select with the optimize_read_in_order setting."):
        node.query(
            f"select * from {table_name} order by a, b SETTINGS optimize_read_in_order=1 FORMAT Null;"
        )


@TestFeature
@Name("encryption at rest")
def feature(self, node="clickhouse1"):
    """Check a corner case regarding encrypted disks and optimize_read_in_order setting."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=corner_case_check)
