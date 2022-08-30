import time
from random import random
from testflows.asserts import error
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *
from helpers.common import add_group_on_node, add_user_on_node

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


@TestStep
def large_insert(self, table_name):
    node = self.context.node
    r = node.query(
        f"INSERT INTO {table_name} SELECT number % 10  AS ID, concat('hello', leftPad(toString(number), 6, '0')) AS Value FROM numbers(1,100000000)",
        no_checks=True,
    )
    assert r.exitcode != 0, error()
    assert "Exception" in r.output, error()


@TestStep
def many_inserts(self, table_name, timeout=30):
    node = self.context.node
    start_time = time.time()

    def time_left():
        left = timeout - (time.time() - start_time)
        if left <= 0:
            raise StopIteration
        return left

    exitcode = 0
    while True:
        try:
            time.sleep(min(random(), time_left()))
            r = node.query(f"INSERT INTO {table_name} VALUES (1,'1')", no_checks=True)
            if r.exitcode != 0:
                exitcode = r.exitcode
        except StopIteration:
            break
    assert exitcode != 0, error()


@TestStep
def changing_directory_rights(self, timeout=30, node=None):
    if node is None:
        node = self.context.node

    start_time = time.time()

    def time_left():
        left = timeout - (time.time() - start_time)
        if left <= 0:
            raise StopIteration
        return left

    while True:
        try:
            time.sleep(min(random(), time_left()))
            node.command("chmod -R 000 /disk_local", exitcode=0)
            try:
                time.sleep(min(random(), time_left()))
            finally:
                node.command("chmod -R 777 /disk_local", exitcode=0)
        except StopIteration:
            break


@TestScenario
def no_rights(self, node=None):
    """Check that ClickHouse returns an error if user has no rights to read or write to the path
    specified in the <path> parameter.
    """
    disk_local = "/disk_local"

    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I change rights for /disk_local"):
        node.command("chmod 000 /disk_local")

    with And("I set up  parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = "secondsecondseco"

    with And(
        "I add storage configuration that uses encrypted disk that uses directory without rights"
    ):
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Error", restart=False
        )


@TestScenario
def changing_rights_one_large_insert(self, node=None):
    """Check that ClickHouse returns an error if rights to read or write to the path is changed during insertion
    specified in the <path> parameter.
    """
    disk_local = "/disk_local"

    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    add_group_on_node(groupname="clickhouse")
    add_user_on_node(groupname="clickhouse", username="clickhouse")

    try:
        with Given("I stop clickhouse to start it from clickhouse user"):
            node.stop_clickhouse()

        with And("I change rights, now clickhouse can be started by user"):
            node.command("chmod -R 777 /etc")
            node.command("chmod -R 777 /var")
            node.command(f"chmod -R 777 {disk_local}")

        with Given("I start clickhouse server"):
            node.start_clickhouse(user="clickhouse")

        with And("I set up  parameters"):
            entries_in_this_test = copy.deepcopy(entries)
            entries_in_this_test["storage_configuration"]["disks"][1][
                "encrypted_local"
            ]["key"] = "secondsecondseco"

        with And("I add storage configuration that uses encrypted disk"):
            add_encrypted_disk_configuration(
                entries=entries_in_this_test, restart=True, user="clickhouse"
            )

        policy = self.context.policy = "local_encrypted"
        with And("I create table that uses encrypted disk"):
            table_name = create_table(policy=policy)

        with And("I insert data into table and change rights at the same moment"):
            Step(name="large insert", test=large_insert, parallel=True)(
                table_name=table_name
            )
            Step(
                name="changing rights", test=changing_directory_rights, parallel=True
            )()

    finally:
        with Finally("I stop clickhouse to start it from root"):
            node.stop_clickhouse()

        with Finally("I start clickhouse server back"):
            node.start_clickhouse()


@TestScenario
def changing_rights_many_small_inserts(self, node=None):
    """Check that ClickHouse returns an error if rights to read or write to the path is changed during insertion
    specified in the <path> parameter.
    """
    disk_local = "/disk_local"

    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    add_group_on_node(groupname="clickhouse")
    add_user_on_node(groupname="clickhouse", username="clickhouse")

    try:
        with Given("I stop clickhouse to start it from clickhouse user"):
            node.stop_clickhouse()

        with And("I change rights, now clickhouse can be started by user"):
            node.command("chmod -R 777 /etc")
            node.command("chmod -R 777 /var")
            node.command(f"chmod -R 777 {disk_local}")

        with Given("I start clickhouse server"):
            node.start_clickhouse(user="clickhouse")

        with And("I set up  parameters"):
            entries_in_this_test = copy.deepcopy(entries)
            entries_in_this_test["storage_configuration"]["disks"][1][
                "encrypted_local"
            ]["key"] = "secondsecondseco"

        with And("I add storage configuration that uses encrypted disk"):
            add_encrypted_disk_configuration(
                entries=entries_in_this_test, restart=True, user="clickhouse"
            )

        policy = self.context.policy = "local_encrypted"
        with And("I create table that uses encrypted disk"):
            table_name = create_table(policy=policy)

        with And("I insert data into table and change rights at the same moment"):
            Step(name="many inserts", test=many_inserts, parallel=True)(
                table_name=table_name
            )
            Step(
                name="changing rights", test=changing_directory_rights, parallel=True
            )()
    finally:
        with Finally("I stop clickhouse to start it from root"):
            node.stop_clickhouse()

        with Finally("I start clickhouse server back"):
            node.start_clickhouse()


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Path_NoAccessRights("1.0")
)
@Name("no rights")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse returns an error if user has no rights to read or write to the path
    specified in the <path> parameter.
    """
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
