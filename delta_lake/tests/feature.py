from testflows.core import *


@TestFeature
def feature(self):
    """Delta Lake reads from RustFS and from the local Unity Catalog."""
    Feature(test=load("delta_lake.tests.sanity", "feature"))()
    Feature(test=load("delta_lake.tests.access", "feature"))()
    Feature(test=load("delta_lake.tests.schema", "feature"))()
    Feature(test=load("delta_lake.tests.snapshot", "feature"))()
    Feature(test=load("delta_lake.tests.unity", "feature"))()
    Feature(test=load("delta_lake.tests.writes", "feature"))()
    Feature(test=load("delta_lake.tests.partitions", "feature"))()
    Feature(test=load("delta_lake.tests.schema_evolution", "feature"))()
    Feature(test=load("delta_lake.tests.column_mapping", "feature"))()
    Feature(test=load("delta_lake.tests.deletes", "feature"))()
    Feature(test=load("delta_lake.tests.time_travel", "feature"))()
    Feature(test=load("delta_lake.tests.cdf", "feature"))()
    Feature(test=load("delta_lake.tests.checkpoint", "feature"))()
    Feature(test=load("delta_lake.tests.protocol", "feature"))()
    Feature(test=load("delta_lake.tests.create_table", "feature"))()
