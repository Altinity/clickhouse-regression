from lightweight_delete.requirements import *
from lightweight_delete.tests.steps import *

from testflows._core.flags import LAST_RETRY


entries = {
    "storage_configuration": {
        "disks": [
            {"jbod1": {"path": "/jbod1/", "keep_free_space_bytes": "1024"}},
        ],
        "policies": {"small_disk": {"volumes": {"volume1": {"disk": "jbod1"}}}},
    }
}


entries_for_tiered_storage = {
    "storage_configuration": {
        "disks": [
            {"jbod1": {"path": "/jbod1/"}},
            {"jbod2": {"path": "/jbod2/"}},
        ],
        "policies": {
            "small_disk": {
                "volumes": {"volume1": {"disk": "jbod1"}, "volume2": {"disk": "jbod2"}}
            }
        },
    }
}


@TestScenario
def lack_of_disk_space(self, node=None):
    """Check that clickhouse reserves space to avoid breaking in the middle by
    filling the disk and deleting inserted the data in loop until an error occurs and
    then check the state of the table stored on the disk.
    """

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I add configuration file"):
        add_disk_configuration(entries=entries, restart=True)

    with And("I create a table that uses small disk"):
        create_table(
            table_name=table_name, settings=f"SETTINGS storage_policy = 'small_disk'"
        )

    with When("I insert data into the table"):
        insert(
            table_name=table_name,
            partitions=5,
            parts_per_partition=1,
            block_size=1450000,
        )

    with And("I check disks used by the table"):
        r = node.query(
            f"SELECT DISTINCT disk_name FROM system.parts "
            f"WHERE table = '{table_name}' FORMAT TabSeparated"
        )

        assert r.output == "jbod1", error()

        r = node.query(
            f"SELECT sum(bytes_on_disk)/1024/1024 FROM system.parts "
            f"WHERE table = '{table_name}' and active = 1 FORMAT TabSeparated"
        )

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT count(*) FROM {table_name} FORMAT TabSeparated")
        assert r.output == "7250000", error()

    with Then("I perform delete and insert operation in the loop"):
        with Then("I perform delete operation"):
            i = 0
            while i < 100:
                r = delete(table_name=table_name, condition=f" id = 1", no_checks=True)
                if r.exitcode != 0:
                    i = 100
                else:
                    r = insert(
                        table_name=table_name,
                        partitions=1,
                        parts_per_partition=1,
                        block_size=1450000,
                        no_checks=True,
                    )
                    if r.exitcode != 0:
                        i = 100
                i += 1
        assert r.exitcode != 0, error()

    with Then("I check table state"):
        for attempt in retries(timeout=100, delay=1):
            with attempt:
                r = node.query(f"SELECT count(*) FROM {table_name} FORMAT TabSeparated")
                assert r.output in ("7250000", "5800000"), error()
                r = node.query(
                    f"SELECT count(*) FROM {table_name} WHERE id=0 FORMAT TabSeparated"
                )
                assert r.output in ("0", "1450000"), error()


@TestScenario
def lack_of_disk_space_tiered_storage(self, node=None):
    """Check that clickhouse reserves space to avoid breaking in the middle by
    filling the disk using delete and insert operations in loop until an error and
    then checking that table data in stored on two disks.
    Check that mutations can not be finished correctly because of lack of disk space.
    """

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I add configuration file"):
        add_disk_configuration(entries=entries_for_tiered_storage, restart=True)

    with And("I create a table that uses small disk"):
        create_table(
            table_name=table_name, settings=f"SETTINGS storage_policy = 'small_disk'"
        )

    partitions = 10
    parts_per_partition = 1
    block_size = 1_500_000
    if check_clickhouse_version(">=24.3")(self):
        block_size = 1_000_000

    with When("I insert data into the table"):
        insert(
            table_name=table_name,
            partitions=partitions,
            parts_per_partition=parts_per_partition,
            block_size=block_size,
        )

    with And("I check table takes up more than one disk"):
        r = node.query(
            f"SELECT DISTINCT disk_name FROM system.parts "
            f"WHERE table = '{table_name}' FORMAT TabSeparated"
        )
        assert set(r.output.strip().splitlines()) == {"jbod1", "jbod2"}, error()

        r = node.query(
            f"SELECT sum(bytes_on_disk)/1024/1024 FROM system.parts "
            f"WHERE table = '{table_name}' and active = 1 FORMAT TabSeparated"
        )
        node.query(
            f"select name, disk_name, partition from system.parts where table='{table_name}' and active FORMAT TabSeparated"
        )

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT count(*) FROM {table_name} FORMAT TabSeparated")
        assert r.output == f"{block_size*partitions}", error()

    with And("I perform delete insert operations in loop"):
        with Then("I perform delete operation"):
            i = 0
            while i < 100:
                r = delete(table_name=table_name, condition=f" id = 1", no_checks=True)
                if r.exitcode != 0:
                    i = 100
                else:
                    r = insert(
                        table_name=table_name,
                        partitions=1,
                        parts_per_partition=1,
                        block_size=block_size,
                        no_checks=True,
                        settings=[("insert_distributed_sync", "1")],
                    )
                    if r.exitcode != 0:
                        i = 100
                i += 1
        assert r.exitcode != 0, error()

    with And("I verify that only rows satisfying the condition were deleted"):
        for i in range(partitions):
            if i == 1:
                continue
            r = node.query(
                f"SELECT count(*) FROM {table_name} WHERE id={i} FORMAT TabSeparated"
            )
            assert r.output == f"{block_size}", error()

    with And("I check table state"):
        for attempt in retries(timeout=100, delay=5, initial_delay=30):
            with attempt:
                r = node.query(
                    f"SELECT count(*) FROM {table_name} WHERE id=0 FORMAT TabSeparated"
                )
                note(
                    f"Number of rows that should have been deleted from the table: {r.output}"
                )
                r = node.query(f"SELECT count(*) FROM {table_name} FORMAT TabSeparated")
                if attempt.kwargs["flags"] & LAST_RETRY:
                    assert r.output not in (
                        f"{block_size*partitions}",
                        f"{block_size*partitions-block_size}",
                    ), error()
                else:
                    assert r.output in (
                        f"{block_size*partitions}",
                        f"{block_size*partitions-block_size}",
                    ), error()


@TestScenario
def lightweight_delete_memory_consumption(self, node=None):

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I add configuration file"):
        add_disk_configuration(entries=entries, restart=True)

    with And("I create a table that uses small disk"):
        create_table(
            table_name=table_name, settings=f"SETTINGS storage_policy = 'small_disk'"
        )

    partitions = 10
    parts_per_partition = 1
    block_size = 150_000

    with When("I insert data into the table"):
        insert(
            table_name=table_name,
            partitions=partitions,
            parts_per_partition=parts_per_partition,
            block_size=block_size,
        )

    with And("I check how much memory is used"):
        r = node.query(
            f"SELECT sum(bytes_on_disk)/1024/1024 FROM system.parts "
            f"WHERE table = '{table_name}' and active = 1 FORMAT TabSeparated"
        )

    with And("I expect data is successfully inserted"):
        r = node.query(f"SELECT count(*) FROM {table_name} FORMAT TabSeparated")
        assert r.output == f"{block_size*partitions}", error()

    with And("I perform delete operations in loop"):
        with Then("I perform delete operation"):
            i = 0
            while i < 11:
                r = delete(
                    table_name=table_name, condition=f" id = {i}", no_checks=True
                )
                node.query(f"SELECT count(*) FROM {table_name} FORMAT TabSeparated")
                if r.exitcode != 0:
                    i = 100
                i += 1

    with Then("I expect data is successfully deleted"):
        r = node.query(f"SELECT count() FROM {table_name} FORMAT TabSeparated")
        assert r.output == "0", error()


@TestFeature
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_LackOfDiskSpace("1.0"))
@Name("lack of disk space")
def feature(self, node="clickhouse1"):
    """Check that clickhouse reserve space to avoid breaking in the middle."""
    self.context.node = self.context.cluster.node(node)
    self.context.table_engine = "MergeTree"
    for scenario in loads(current_module(), Scenario):
        scenario()
