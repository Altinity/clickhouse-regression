from lightweight_delete.tests.steps import *
from lightweight_delete.requirements import *
from disk_level_encryption.tests.steps import (
    create_directories_multi_volume_policy,
    add_config_multi_volume_policy,
    insert_into_table,
)


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_TTL("1.0"))
def concurrent_deletes_and_ttl(
    self,
    node=None,
):
    """Check clickhouse lightweight delete do not greatly slow down during tiered storage ttl on acceptance table."""

    if node is None:
        node = self.context.node

    table_name_1 = "acceptance_1"
    table_name_2 = "acceptance_2"

    with Given(
        "I have acceptance table that uses column ttl",
        description="""
        b UInt16 DEFAULT 777 TTL d + INTERVAL 1 HOUR'""",
    ):
        create_acceptance_table_with_column_ttl(table_name=table_name_2)

    with And("I have acceptance table without column ttl"):
        create_acceptance_table(table_name=table_name_1)

    with When("I insert data into both tables"):
        insert_into_acceptance_table(table_name=table_name_1, rows_number=100000)
        insert_into_acceptance_table(table_name=table_name_2, rows_number=100000)

    with When("I delete from acceptance tables and time it"):
        start = time.time()
        delete(table_name=table_name_1, condition="Id == 0")
        time_without_ttl = time.time() - start
        start = time.time()
        delete(table_name=table_name_2, condition="Id == 0")
        time_with_ttl = time.time() - start

    with Then("I check tiered storage ttl do not greatly slow down lightweight delete"):
        assert time_without_ttl * 5 > time_with_ttl, error()


@TestFeature
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_Performance_Acceptance_OnTimeDataset_DeleteQueryExecutionTime("1.0")
)
@Name("acceptance column ttl")
def feature(self, node="clickhouse1"):
    """Check clickhouse lightweight delete do not slow down during column ttl on acceptance table."""
    self.context.node = self.context.cluster.node(node)
    self.context.table_engine = "MergeTree"
    for scenario in loads(current_module(), Scenario):
        scenario()
