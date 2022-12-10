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

    final_test_modules = ["modifier", "force_modifier"]

    with Given("I have set of populated tables"):
        create_and_populate_core_tables()
        add_system_tables()
        create_and_populate_distributed_tables()
        all_types = ["normal", "materialized", "live"]
        for table in self.context.tables:
            if not (
                table.name.startswith("system")
                or table.name.startswith("distr")
                or table.name.endswith("view")
            ):
                for type in all_types:
                    self.context.tables.append(
                        create_view(
                            type=type,
                            core_table=table.name,
                            final_modifier_available=table.final_modifier_available,
                        )
                    )

    for module in final_test_modules:
        try:
            case = load_module(f"final.{module}")
        except ModuleNotFoundError:
            xfail(reason=f"{module} tests are not implemented")
            continue

        for feature in loads(case, Feature):
            feature()
