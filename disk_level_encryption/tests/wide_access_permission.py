from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *
import os
from testflows.core import *
from testflows.asserts import error

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
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_AccessPermission_WideOrInvalid(
        "1.0"
    )
)
def wide_permission(self, node=None):
    """Check that ClickHouse returns an error if the configuration file which contains encryption keys
    has invalid or wide access permissions.
    """
    disk_local = "/disk_local"
    config_path = "/etc/clickhouse-server/config.d/encrypted_disk.xml"
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up  parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = "secondsecondseco"

    try:
        with And("I add storage configuration that uses encrypted disk"):
            add_encrypted_disk_configuration(
                entries=entries_in_this_test, modify=True, restart=True
            )

        with And("I change rights for encrypted_disk.xml"):
            node.command(f"chmod 777 {config_path}")

        with And("I try to stop server"):
            node.stop_clickhouse()

        with And("I try to start server process back up"):
            r = node.command(
                "clickhouse server --config-file=/etc/clickhouse-server/config.xml"
                " --log-file=/var/log/clickhouse-server/clickhouse-server.log"
                " --errorlog-file=/var/log/clickhouse-server/clickhouse-server.err.log"
                " --pidfile=/tmp/clickhouse-server.pid --daemon"
            )
        try:
            node.wait_clickhouse_healthy(timeout=30)
        except Exception:
            pass
        else:
            assert False, "Expected server not to start"
    finally:
        with Finally(f"I remove {name}"):
            node.command(f"rm -rf {config_path}", timeout=10, exitcode=0)
            node.restart_clickhouse()


@TestFeature
@Name("wide access permission")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse returns an error if the configuration file which contains encryption keys
    has invalid or wide access permissions.
    """
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
