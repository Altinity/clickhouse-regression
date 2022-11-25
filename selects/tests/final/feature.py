from testflows.core import *
from selects.requirements import *


@TestFeature
@Name("final")
def feature(self):
    """Check FINAL modifier."""
    # Feature(engines)
    # Feature(settings)
    Feature(run=load("selects.tests.final.engines", "feature"))
    Feature(run=load("selects.tests.final.table_setting", "feature"))
