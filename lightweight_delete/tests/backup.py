from lightweight_delete.requirements import *
from lightweight_delete.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Backups_Mask("1.0"))
def backup(self, node=None):
    """Check that clickhouse keeps lightweight delete mask during backup."""

    with When("I have a table"):
        pass

    with When("I insert data into the table"):
        pass

    with When("I delete from the table"):
        pass

    with Then("I perform back up and check it works correctly"):
        pass


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Backups_BackupAfterLightweightDelete("1.0"))
def backup(self, node=None):
    """Check that clickhouse support using backups after lightweight delete."""

    with When("I have a table"):
        pass

    with When("I insert data into the table"):
        pass

    with When("I delete from the table"):
        pass

    with When("I optimize table final to finish lightweight delete"):
        pass

    with Then("I perform back up and check it works correctly"):
        pass


@TestFeature
@Name("disk space")
def feature(self, node="clickhouse1"):
    """Check that clickhouse support backups with lightweight delete."""
    self.context.node = self.context.cluster.node(node)
    self.context.table_engine = "MergeTree"
    for scenario in loads(current_module(), Scenario):
        scenario()