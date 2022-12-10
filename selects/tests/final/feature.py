from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *
import sys

append_path(sys.path, "..")


@TestModule
@Name("final")
def feature(self):
    """Check FINAL modifier."""
    self.context.tables = []

    final_test_modules = ["force_modifier"]

    with Given("I have set of populated tables"):
        create_and_populate_all_tables()

    for module in final_test_modules:
        try:
            case = load_module(f"final.{module}")
        except ModuleNotFoundError:
            xfail(reason=f"{module} tests are not implemented")
            continue

        for feature in loads(case, Feature):
            feature()
