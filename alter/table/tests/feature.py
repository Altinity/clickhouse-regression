from testflows.core import *
from alter.table.requirements.replace_partition import *


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition("1.0"))
def feature(self, node="clickhouse1"):
    """Check that replace partition functionality works as expected."""
    self.context.node = self.context.cluster.node(node)
    pass
