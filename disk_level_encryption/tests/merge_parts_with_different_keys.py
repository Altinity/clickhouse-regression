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


@TestOutline
def merge_parts_with_different_encryption_keys(
    self, number_of_keys, should_not_work=False, number_of_key_to_delete=None, node=None
):
    """Check that clickhouse supports merging parts with different encryption keys on encrypted disk."""
    disk_local = "/disk_local"

    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    with And("I set up parameters"):
        key_id = [
            KeyWithAttributes("key", {"id": f"{i}"}) for i in range(number_of_keys)
        ]
        entries_in_this_test = copy.deepcopy(entries)
        for i in range(number_of_keys):
            entries_in_this_test["storage_configuration"]["disks"][1][
                "encrypted_local"
            ][key_id[i]] = (f"{i}" * 16)[0:16]
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "current_key_id"
        ] = "0"

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy="local_encrypted")

    with When("I insert data into the table each part with unique key"):
        for i in range(number_of_keys):
            with Step("I change configuration"):
                entries_in_this_test["storage_configuration"]["disks"][1][
                    "encrypted_local"
                ]["current_key_id"] = f"{i}"
                add_encrypted_disk_configuration(
                    modify=True, restart=True, entries=entries_in_this_test
                )
            with Step("I insert data"):
                values = "(1, 'hello'),(2, 'there')"
                insert_into_table(name=table_name, values=values)

    with And("I compute expected output"):
        expected_output = (
            "\n".join(['{"Id":1,"Value":"hello"}'] * number_of_keys)
            + "\n"
            + "\n".join(['{"Id":2,"Value":"there"}'] * number_of_keys)
        )

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with And("I restart server"):
        node.restart()

    with And("I expect data didn't change after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with And("I optimize table"):
        r = node.query(f"OPTIMIZE TABLE {table_name} FINAL")

    with And("I restart server second time"):
        node.restart()

    with And("I expect data didn't change after optimize"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with And("I expect that table have only one part"):
        r = node.query(
            f"SELECT count() FROM system.parts WHERE table =  '{table_name}' and active = 1 FORMAT JSONEachRow"
        )
        assert r.output == '{"count()":"1"}', error()

    if number_of_key_to_delete is not None:
        with And("I change configuration file"):
            del entries_in_this_test["storage_configuration"]["disks"][1][
                "encrypted_local"
            ][key_id[number_of_key_to_delete]]
            if should_not_work:
                add_invalid_encrypted_disk_configuration(
                    message="Exception", restart=True, entries=entries_in_this_test
                )
            else:
                add_encrypted_disk_configuration(
                    modify=True, restart=True, entries=entries_in_this_test
                )
                with And("I expect data didn't change after key deleting"):
                    r = node.query(
                        f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow"
                    )
                    assert r.output == expected_output, error()


@TestScenario
def merge_parts_with_different_encryption_keys_five_keys(self, node=None):
    """Check that clickhouse supports merging parts with different encryption keys on encrypted disk
    with five keys without deleting keys after merge.
    """
    merge_parts_with_different_encryption_keys(number_of_keys=5, node=node)


@TestScenario
@Requirements()
def optimize_table_a_lot_of_keys(self, node=None):
    """Check that clickhouse supports merging parts with big
    amount of different encryption keys on encrypted disk.
    """
    merge_parts_with_different_encryption_keys(number_of_keys=100, node=node)


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_MergingWithDifferentKeys(
        "1.0"
    ),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_PartsWithDifferentKeys("1.0"),
)
@Name("merge parts")
def feature(self, node="clickhouse1"):
    """Check that clickhouse supports optimize table for encrypted disk."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
