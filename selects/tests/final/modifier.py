from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *


@TestFeature
@Name("modifier")
def feature(self):
    """Check 'FINAL' modifier setting."""
    xfail("not implemented")
    for scenario in loads(current_module(), Scenario):
        scenario()
