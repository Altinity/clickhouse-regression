from lightweight_delete.tests.steps import *
from lightweight_delete.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_Performance_Acceptance_OnTimeDataset_ConcurrentSelectsAndDeletes(
        "1.0"
    )
)
def acceptance_concurrent_select_delete_execution_time(self, delete_query, node=None):
    """Check that clickhouse keeps reference dataset table usable while the delete reference queries
    are being executed concurrently with the select reference queries.
    No major degradation in query response time SHALL be seen.
    """
    if node is None:
        node = self.context.node

    with Given("I have acceptance table"):
        create_acceptance_table()
        insert_into_acceptance_table(rows_number=100000)

    with When("I perform select query and time it"):
        start_time = time.time()
        select_query_acceptance()
        execution_time = time.time() - start_time

    metric("execution_time", execution_time, "s")

    start_time = time.time()
    with Then("I perform concurrent select and delete"):
        Step(
            name="I perform select operation",
            test=select_query_acceptance,
            parallel=True,
        )()
        Step(name="I perform delete operation", test=delete_query, parallel=True)()
    execution_time_parallel = time.time() - start_time

    metric("execution_time_parallel", execution_time_parallel, "s")

    with Then("I check execution time does not change a lot"):
        assert 500 * execution_time > execution_time_parallel, error()


@TestScenario
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_Performance_Acceptance_OnTimeDataset_ConcurrentInsertsAndDeletes(
        "1.0"
    ),
)
def acceptance_concurrent_insert_delete_execution_time(self, delete_query, node=None):
    """Check that clickhouse is not slow down or lockup data ingestion into the reference dataset table
    when delete reference queries are executed concurrently with the insert reference queries.
    """
    if node is None:
        node = self.context.node

    with Given("I have acceptance table"):
        create_acceptance_table()
        insert_into_acceptance_table(rows_number=100000)

    with When("I perform insert query and time it"):
        start_time = time.time()
        insert_query_acceptance()
        execution_time = time.time() - start_time

    metric("execution_time", execution_time, "s")

    start_time = time.time()
    with Then("I perform concurrent insert and delete"):
        Step(
            name="I perform insert operation",
            test=insert_query_acceptance,
            parallel=True,
        )()
        Step(name="I perform delete operation", test=delete_query, parallel=True)()
    execution_time_parallel = time.time() - start_time

    metric("execution_time_parallel", execution_time_parallel, "s")

    with Then("I check execution time does not change a lot"):
        assert 100 * execution_time > execution_time_parallel, error()


@TestScenario
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_Performance_Acceptance_OnTimeDataset_DeleteQueryExecutionTime(
        "1.0"
    )
)
def acceptance_delete_execution_time(self, delete_query, node=None):
    """Check that clickhouse execute each query in the delete reference queries
    set against the reference dataset table within 2 sec.
    """

    if node is None:
        node = self.context.node

    with Given("I have acceptance table"):
        create_acceptance_table()
        insert_into_acceptance_table(rows_number=100000)

    with When("I perform delete operation"):
        start_time = time.time()
        delete_query()
        execution_time = time.time() - start_time

    metric("execution_time", execution_time, "s")

    with Then("I check delete execution time is less than 2 seconds"):
        assert execution_time < 10, error()


@TestScenario
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_Performance_Acceptance_OnTimeDataset_Inserts(
        "1.0"
    ),
)
def acceptance_insert_execution_time_after_delete(self, delete_query, node=None):
    """Check that clickhouse insert queries are not slow down after lightweight delete."""

    if node is None:
        node = self.context.node

    with Given("I have acceptance table"):
        create_acceptance_table()
        insert_into_acceptance_table(rows_number=100000)

    with When("I perform insert query and time it"):
        start_time = time.time()
        insert_query_acceptance()
        execution_time = time.time() - start_time

    metric("execution_time", execution_time, "s")

    with When("I perform delete operation"):
        delete_query()

    with When("I perform insert query on table with deleted rows and time it"):
        start_time = time.time()
        insert_query_acceptance()
        execution_time_after_delete = time.time() - start_time

    metric("execution_time_after_delete", execution_time_after_delete, "s")

    with Then("I check execution time does not change a lot"):
        assert execution_time * 2 > execution_time_after_delete, error()


@TestFeature
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_Performance_ConcurrentQueries("1.0")
)
@Name("acceptance")
def feature(self, node="clickhouse1"):
    """Check that clickhouse supports lightweight delete operations applied to acceptance dataset."""
    self.context.node = self.context.cluster.node(node)

    for (i, delete_query) in enumerate(
        [
            delete_query_1_acceptance,
            delete_query_2_acceptance,
            delete_query_3_acceptance,
        ]
    ):

        # with Given("I check ontime exists"):
        #     output = self.context.node.query("EXISTS ontime").output
        #     assert output == "1", error()

        with Feature(f"delete_query_{i}"):
            acceptance_concurrent_select_delete_execution_time(
                delete_query=delete_query
            )
            acceptance_concurrent_insert_delete_execution_time(
                delete_query=delete_query
            )
            acceptance_delete_execution_time(delete_query=delete_query)
            acceptance_insert_execution_time_after_delete(delete_query=delete_query)
