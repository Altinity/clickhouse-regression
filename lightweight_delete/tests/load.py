from lightweight_delete.requirements import *
from lightweight_delete.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Load_Merges("1.0"))
def load_merges(self, node=None):
    """Check that clickhouse perform correctly with concurrent lightweight delete and a lot of merges."""
    with When("I have a table"):
        pass

    with When("I insert data into the table"):
        pass

    with When("I perform a lot of merges and deletes in parallel"):
        pass

    with Then("I check data is correctly inserted and deleted"):
        pass


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Load_Insert("1.0"))
def load_inserts(self, node=None):
    """Check that clickhouse perform correctly with high insert pressure and lightweight delete."""

    if node is None:
        node = self.context.node

    with When("I have a table"):
        pass

    with When("I insert data into the table"):
        pass

    with When("I perform a lot of inserts and deletes in parallel"):
        pass

    with Then("I check data is correctly inserted and deleted"):
        pass


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Load_ExcessiveMutations("1.0"))
def load_excessive_mutations(self, node=None):
    """Check that clickhouse do not create excessive mutations during lightweight delete operations."""

    if node is None:
        node = self.context.node

    with When("I have a table"):
        pass

    with When("I insert data into the table"):
        pass

    with When("I perform a lot of deletes"):
        pass

    with Then("I check clickhouse did not create a lot of mutations"):
        pass


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Load_ExcessiveMutations("1.0"))
def load_zookeeper(self, node=None):
    """Check that clickhouse do not create huge transactions in zookeeper during lightweight delete operations."""

    if node is None:
        node = self.context.node

    with When("I have replicated table"):
        pass

    with When("I insert data into the first node table and wait data is inserted on the second node"):
        pass

    with When("I perform a lot of deletes"):
        pass

    with Then("I check clickhouse do not create a lot of transactions in zookeeper"):
        pass


@TestFeature
@Name("load")
def feature(self, node="clickhouse1"):
    """Check that clickhouse perform correctly with high load."""
    self.context.node = self.context.cluster.node(node)
    self.context.table_engine = "MergeTree"
    for scenario in loads(current_module(), Scenario):
        scenario()
