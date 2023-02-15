from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *
from helpers.common import check_clickhouse_version
# from selects.tests.final.force_modifier import *


@TestScenario
def select_concurrent(self):
    """Concurent count queries."""

    with Given("I exclude auxiliary and unsupported tables by the current test"):
        tables = define(
            "tables",
            [
                table
                for table in self.context.tables
                if table.name.endswith("core")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    # for table in tables:
    #     with When(f"{table.name}"):
    #         with When("I execute concurrent select queries"):
    #             By("selecting data", test=select_count, parallel=True)()


@TestModule
@Requirements()
@Name("force modifier concurrent")
def feature(self):
    """Concurrent queries tests for force select final."""
    xfail("doesn't ready")
    if check_clickhouse_version("<22.11")(self):
        skip(
            reason="force_select_final is only supported on ClickHouse version >= 22.11"
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
