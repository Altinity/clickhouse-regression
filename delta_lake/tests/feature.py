from testflows.core import *


@TestFeature
def feature(self):
    """Delta Lake reads from RustFS and from the local Unity Catalog."""
    Feature(test=load("delta_lake.tests.sanity", "feature"))()
    Feature(test=load("delta_lake.tests.access", "feature"))()
    Feature(test=load("delta_lake.tests.schema", "feature"))()
