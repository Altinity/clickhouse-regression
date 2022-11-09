from lightweight_delete.tests.steps import *
from lightweight_delete.requirements import *
from disk_level_encryption.tests.steps import (
    create_directories_multi_volume_policy,
    add_config_multi_volume_policy,
    insert_into_table,
)

entries = {
    "storage_configuration": {
        "disks": [
            {
                "local00": {"path": "/disk_local00/"},
                "local01": {"path": "/disk_local01/"},
                "local10": {"path": "/disk_local10/"},
                "local11": {"path": "/disk_local11/"},
            }
        ],
        "policies": {
            "local_local0": {
                "volumes": {
                    "volume0": [{"disk": "local00"}],
                    "volume1": [{"disk": "local01"}],
                }
            },
            "local_local1": {
                "volumes": {
                    "volume0": [{"disk": "local10"}],
                    "volume1": [{"disk": "local11"}],
                }
            },
        },
    }
}


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_TTL("1.0"))
def delete_with_tiered_storage_ttl_move(
    self,
    number_of_volumes=2,
    numbers_of_disks=[2, 2],
    disks_types=[["local"], ["local"]],
    node=None,
):
    """Check clickhouse lightweight delete do not slow down during tiered storage ttl on acceptance table."""

    if node is None:
        node = self.context.node

    with Given("I create directories"):
        create_directories_multi_volume_policy(
            number_of_volumes=number_of_volumes, numbers_of_disks=numbers_of_disks
        )

    add_disk_configuration(entries=entries)

    table_name_1 = "acceptance_1"
    table_name_2 = "acceptance_2"

    with And(
        "I create acceptance table that uses tiered storage ttl",
        description="""
      TTL Date TO VOLUME 'volume0',
      Date + INTERVAL 1 HOUR TO VOLUME 'volume1'""",
    ):
        create_acceptance_table_with_tiered_storage_ttl(
            table_name=table_name_2,
            storage_policy="local_local1",
        )

    with And("I create acceptance table without tiered storage ttl"):
        create_acceptance_table(table_name=table_name_1, storage_policy="local_local0")

    with When("I insert data into both tables"):
        insert_into_acceptance_table(table_name=table_name_1, rows_number=100000)
        insert_into_acceptance_table(table_name=table_name_2, rows_number=100000)

    with When("I compute expected output"):
        expected_output = node.query(
            f"SELECT count(*) from {table_name_2} where not (Id = 0)"
        ).output

    with When("I delete from acceptance tables and time it"):
        start = time.time()
        delete(table_name=table_name_1, condition="Id == 0")
        time_without_ttl = time.time() - start
        start = time.time()
        delete(table_name=table_name_2, condition="Id == 0")
        time_with_ttl = time.time() - start

    with Then("I check tiered storage ttl do not greatly slow down lightweight delete"):
        assert time_without_ttl * 20 > time_with_ttl, error()

    with Then("I check rows are deleted"):
        r = node.query(f"SELECT count(*) from {table_name_2}").output
        assert r == expected_output, error()


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_TTL("1.0"))
def delete_with_tiered_storage_ttl_delete(
    self,
    number_of_volumes=2,
    numbers_of_disks=[2, 2],
    disks_types=[["local"], ["local"]],
    node=None,
):
    """Check clickhouse lightweight delete do not slow down during tiered storage ttl move and delete on acceptance table."""

    if node is None:
        node = self.context.node

    with Given("I create directories"):
        create_directories_multi_volume_policy(
            number_of_volumes=number_of_volumes, numbers_of_disks=numbers_of_disks
        )

    add_disk_configuration(entries=entries)

    table_name_1 = "acceptance_1"
    table_name_2 = "acceptance_2"

    with And(
        "I create acceptance table that uses tiered storage ttl with ttl delete",
        description="""
      TTL Date TO VOLUME 'volume0',
      Date + INTERVAL 1 HOUR TO VOLUME 'volume1'
      Date + INTERVAL 2 HOUR DELETE""",
    ):
        create_acceptance_table_with_tiered_storage_ttl(
            table_name=table_name_2,
            storage_policy="local_local1",
        )

    with And("I create acceptance table without tiered storage ttl"):
        create_acceptance_table(table_name=table_name_1, storage_policy="local_local0")

    with When("I insert data into both tables"):
        insert_into_acceptance_table(table_name=table_name_1, rows_number=100000)
        insert_into_acceptance_table(table_name=table_name_2, rows_number=100000)

    with When("I compute expected output"):
        expected_output = node.query(
            f"SELECT count(*) from {table_name_2} where not (Id = 0)"
        ).output

    with When("I delete from acceptance tables and time it"):
        start = time.time()
        delete(table_name=table_name_1, condition="Id == 0")
        time_without_ttl = time.time() - start
        start = time.time()
        delete(table_name=table_name_2, condition="Id == 0")
        time_with_ttl = time.time() - start

    with Then("I check tiered storage ttl do not greatly slow down lightweight delete"):
        assert time_without_ttl * 20 > time_with_ttl, error()

    with Then("I check rows are deleted"):
        r = node.query(f"SELECT count(*) from {table_name_2}").output
        assert r == expected_output, error()


@TestFeature
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_Performance_Acceptance_OnTimeDataset_DeleteQueryExecutionTime(
        "1.0"
    )
)
@Name("acceptance tiered storage ttl")
def feature(self, node="clickhouse1"):
    """Check clickhouse lightweight delete do not slow down during tiered storage ttl on acceptance table."""
    self.context.node = self.context.cluster.node(node)
    self.context.table_engine = "MergeTree"
    for scenario in loads(current_module(), Scenario):
        scenario()
