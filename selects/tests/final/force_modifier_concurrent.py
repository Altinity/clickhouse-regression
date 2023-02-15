from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *
from helpers.common import check_clickhouse_version
from selects.tests.final.statements import *


@TestScenario
def select_concurrent(self):
    """Concurent count queries."""

    with Given("I chose tables for testing"):
        tables = define(
            "tables",
            [
                table
                for table in self.context.tables
                if table.name.endswith("core")
                and table.name.startswith("ReplacingMergeTree_table")
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    with And("I choose statements for testing"):
        statements = define(
            "Select statements",
            [
                select_count_query,
                select_limit_query,
                select_limit_by_query,
                select_group_by_query,
                select_distinct_query,
                select_where_query,
            ],
        )

    for table in tables:
        with When(f"{table.name}"):
            with When("I execute concurrent select, insert, delete, update queries"):
                for statement in statements:
                    By(f"{statement}", test=concurrent_queries, parallel=True)(
                        statement=select_count_query,
                        table_name=table.name,
                        parallel_selects=500,
                        parallel_deletes=1,
                        first_delete_id=1,
                        last_delete_id=4,
                        parallel_updates=2,
                        first_update_id=1,
                        last_update_id=4,
                        parallel_inserts=10,
                        first_insert_id=1,
                        last_insert_id=4,
                    )


@TestModule
@Requirements()
@Name("force modifier concurrent")
def feature(self):
    """Concurrent queries tests for force select final."""
    # xfail("doesn't ready")
    if check_clickhouse_version("<22.11")(self):
        skip(
            reason="force_select_final is only supported on ClickHouse version >= 22.11"
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
