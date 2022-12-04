from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *
import sys

append_path(sys.path, "..")


@TestFeature
@Name("final")
def feature(self):
    """Check FINAL modifier."""
    self.context.tables = []

    final_test_modules = ["modifier", "force_modifier"]

    with Given("I have set of populated tables"):
        create_and_populate_tables()
        add_system_tables()

    with And("I test all tables with `FINAL` modifier queries"):
        for module in final_test_modules:
            try:
                case = load_module(f"final.{module}")
            except ModuleNotFoundError:
                xfail(reason=f"{module} tests are not implemented")
                continue

            for scenario in loads(case, Scenario):
                scenario()
