from lightweight_delete.requirements import *
from lightweight_delete.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_DiskSpace("1.0"))
def disk_space(self, node=None):
    """Check that clickhouse does not greatly increase table size after lightweight delete."""

    with When("I have a table"):
        pass

    with When("I insert data into the table"):
        pass

    with When("I measure table size on disk"):
        pass

    # todo may be stop merges

    with When("I perform a lot of deletes"):
        pass

    with Then("I check table size on disk does not increased a lot"):
        pass


@TestFeature
@Name("disk space")
def feature(self, node="clickhouse1"):
    """Check that clickhouse does not greatly increase table size after lightweight delete."""
    self.context.node = self.context.cluster.node(node)
    self.context.table_engine = "MergeTree"
    for scenario in loads(current_module(), Scenario):
        scenario()