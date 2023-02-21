from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *
import sys

append_path(sys.path, "..")


@TestModule
@Name("final")
def module(self):
    """Check FINAL modifier."""
    self.context.tables = []

    with Given("I have set of populated tables"):
        create_and_populate_all_tables()

    Feature(run=load("final.modifier", "feature"))
    Feature(run=load("final.force_modifier", "feature"))
    Feature(run=load("final.force_modifier_concurrent", "feature"))
    Feature(run=load("final.force_modifier_user_rights", "feature"))
