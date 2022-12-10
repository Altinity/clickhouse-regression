from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *


@TestFeature
@Name("modifier")
def feature(self):
    """Check force_final_modifier setting."""
    for scenario in loads(current_module(), Scenario):
        scenario()
