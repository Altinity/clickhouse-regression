from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *
from helpers.common import check_clickhouse_version


@TestScenario
def select_concurrent(self):
    """Checking basic selects with `FINAL` clause equal to force_select_final select."""
    with Given("I create queries with and without `FINAL`."):
        query = define(
            "count() query with and without FINAL",
            "SELECT count() FROM {name} {final} FORMAT JSONEachRow;",
        )

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

    for table in tables:
        with When(f"{table.name}"):
            with When("I execute concurrent select queries"):
                concurrent_queries(
                    statement=query.format(name=table.name, final=""),
                    parallel_selects=2,
                )
                concurrent_queries(
                    statement=query.format(
                        final=f"{' FINAL' if table.final_modifier_available else ''}",
                        name=table.name,
                    ),
                    parallel_selects=2,
                )
                concurrent_queries(
                    statement=query.format(final=f"", name=table.name),
                    parallel_selects=2,
                    final=1,
                )
                join()


@TestModule
@Requirements()
@Name("force modifier concurrent")
def feature(self):
    """Tests for cases when the partitioning limit is exceeded."""
    if check_clickhouse_version("<22.11")(self):
        skip(
            reason="force_select_final is only supported on ClickHouse version >= 22.11"
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
