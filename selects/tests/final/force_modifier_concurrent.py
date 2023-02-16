from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *
from helpers.common import check_clickhouse_version
from selects.tests.select_steps import *
from selects.tests.concurrent_query_steps import *


@TestScenario
def select_sanity_concurrent(self):
    """Sanity test for concurrent queries with inserts, deletes and updates."""

    with Given("I chose tables for testing"):
        tables = define(
            "tables",
            [
                table
                for table in self.context.tables
                if table.name.endswith("core")
                and (
                    table.name.startswith("ReplacingMergeTree_table")
                    or table.name.startswith("MergeTree_table")
                )
            ],
            encoder=lambda tables: ", ".join([table.name for table in tables]),
        )

    with And("I choose 'SELECT' steps for loop testing"):
        statements = [select_count_query, select_limit_query, select_limit_by_query, select_group_by_query,
                      select_distinct_query, select_prewhere_query, select_where_query]

    for table in tables:
        with When(f"{table.name}"):
            with When("I execute concurrent select, insert, delete, update queries"):
                for statement in statements:
                    for i in range(2):
                        By(
                            f"{select_count_query.name} loop iteration {i}",
                            test=statement,
                            parallel=True,
                        )(
                            name=table.name,
                            final_manual=True,
                            final_force=1,
                            final_modifier_available=table.final_modifier_available,
                        )

                By(
                    f"{select_count_query.name} manual 1",
                    test=select_count_query,
                    parallel=True,
                )(
                    name=table.name,
                    final_manual=False,
                    final_force=1,
                    final_modifier_available=table.final_modifier_available,
                )

                By(
                    f"{select_limit_query.name} manual 1",
                    test=select_limit_query,
                    parallel=True,
                )(
                    name=table.name,
                    final_manual=False,
                    final_force=0,
                    final_modifier_available=table.final_modifier_available,
                )

                By(
                    f"{select_count_query.name} manual 2",
                    test=select_count_query,
                    parallel=True,
                )(
                    name=table.name,
                    final_manual=True,
                    final_force=0,
                    final_modifier_available=table.final_modifier_available,
                )

                By(f"inserts,updates deletes", test=concurrent_queries, parallel=True,)(
                    table_name=table.name,
                    parallel_runs=1,
                    parallel_selects=1,
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

            join()

    with Then("I check data consistency in tested tables"):
        for table in tables:
            with When(f"{table.name}"):
                By(select_count_query.name, test=select_count_query, parallel=False)(
                    name=table.name,
                    final_manual=False,
                    final_force=1,
                    final_modifier_available=table.final_modifier_available,
                    check_results=True,
                    final_manual_check=True,
                    final_force_check=1,
                )

                By(select_count_query.name, test=select_count_query, parallel=False)(
                    name=table.name,
                    final_modifier_available=table.final_modifier_available,
                    check_results=True,
                )

                By(f"{select_count_query.name} negative", test=select_count_query, parallel=False)(
                    name=table.name,
                    final_manual=False,
                    final_force=0,
                    final_modifier_available=table.final_modifier_available,
                    check_results=True,
                    final_manual_check=False,
                    final_force_check=1,
                    negative=True
                )


@TestModule
@Requirements()
@Name("force modifier concurrent")
def feature(self):
    """Concurrent queries tests for force select final."""
    if check_clickhouse_version("<22.11")(self):
        skip(
            reason="force_select_final is only supported on ClickHouse version >= 22.11"
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
