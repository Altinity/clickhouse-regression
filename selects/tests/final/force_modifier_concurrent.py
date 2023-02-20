import tests.select_steps as select
from helpers.common import check_clickhouse_version
from tests.concurrent_query_steps import *
from tests.steps import *


@TestScenario
@Name("SELECT count() parallel")
def select_count_parallel(self):
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

    with And("I choose selects for testing"):
        selects = define(
            "Select statements",
            [
                select.count,
                select.count_final,
                select.count_ffinal,
                select.count_final_ffinal,
            ],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.count_result_check,
                select.count_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(tables=tables, selects=selects, iterations=10)

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT count() parallel inserts, deletes, updates")
def select_count_parallel_idu(self):
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

    with And("I choose selects, inserts, updates, deletes  for testing"):
        selects = define(
            "Select statements",
            [
                select.count,
                select.count_final,
                select.count_ffinal,
                select.count_final_ffinal,
            ],
        )
        inserts = define(
            "Insert statements",
            [insert],
        )
        updates = define(
            "Update statements",
            [update],
        )

        deletes = define(
            "Delete statements",
            [delete],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.count_result_check,
                select.count_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(
            tables=tables,
            selects=selects,
            inserts=inserts,
            deletes=deletes,
            updates=updates,
            iterations=10,
        )

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT LIMIT parallel")
def select_limit_parallel(self):
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

    with And("I choose selects for testing"):
        selects = define(
            "Select statements",
            [
                select.limit,
                select.limit_final,
                select.limit_ffinal,
                select.limit_final_ffinal,
            ],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.limit_result_check,
                select.limit_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(tables=tables, selects=selects, iterations=10)

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT LIMIT parallel inserts, deletes, updates")
def select_limit_parallel_idu(self):
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

    with And("I choose selects, inserts, updates, deletes  for testing"):
        selects = define(
            "Select statements",
            [
                select.limit,
                select.limit_final,
                select.limit_ffinal,
                select.limit_final_ffinal,
            ],
        )
        inserts = define(
            "Insert statements",
            [insert],
        )
        updates = define(
            "Update statements",
            [update],
        )

        deletes = define(
            "Delete statements",
            [delete],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.limit_result_check,
                select.limit_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(
            tables=tables,
            selects=selects,
            inserts=inserts,
            deletes=deletes,
            updates=updates,
            iterations=10,
        )

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT LIMIT BY parallel")
def select_limit_by_parallel(self):
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

    with And("I choose selects for testing"):
        selects = define(
            "Select statements",
            [
                select.limit_by,
                select.limit_by_final,
                select.limit_by_ffinal,
                select.limit_by_final_ffinal,
            ],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.limit_by_result_check,
                select.limit_by_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(tables=tables, selects=selects, iterations=10)

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT LIMIT BY parallel inserts, deletes, updates")
def select_limit_by_parallel_idu(self):
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

    with And("I choose selects, inserts, updates, deletes  for testing"):
        selects = define(
            "Select statements",
            [
                select.limit_by,
                select.limit_by_final,
                select.limit_by_ffinal,
                select.limit_by_final_ffinal,
            ],
        )
        inserts = define(
            "Insert statements",
            [insert],
        )
        updates = define(
            "Update statements",
            [update],
        )

        deletes = define(
            "Delete statements",
            [delete],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.limit_by_result_check,
                select.limit_by_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(
            tables=tables,
            selects=selects,
            inserts=inserts,
            deletes=deletes,
            updates=updates,
            iterations=10,
        )

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT GROUP BY parallel")
def select_group_by_parallel(self):
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

    with And("I choose selects for testing"):
        selects = define(
            "Select statements",
            [
                select.group_by,
                select.group_by_final,
                select.group_by_ffinal,
                select.group_by_final_ffinal,
            ],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.group_by_result_check,
                select.group_by_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(tables=tables, selects=selects, iterations=10)

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT GROUP BY parallel inserts, deletes, updates")
def select_group_by_parallel_idu(self):
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

    with And("I choose selects, inserts, updates, deletes  for testing"):
        selects = define(
            "Select statements",
            [
                select.group_by,
                select.group_by_final,
                select.group_by_ffinal,
                select.group_by_final_ffinal,
            ],
        )
        inserts = define(
            "Insert statements",
            [insert],
        )
        updates = define(
            "Update statements",
            [update],
        )

        deletes = define(
            "Delete statements",
            [delete],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.group_by_result_check,
                select.group_by_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(
            tables=tables,
            selects=selects,
            inserts=inserts,
            deletes=deletes,
            updates=updates,
            iterations=10,
        )

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT DISTINCT parallel")
def select_distinct_parallel(self):
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

    with And("I choose selects for testing"):
        selects = define(
            "Select statements",
            [
                select.distinct,
                select.distinct_final,
                select.distinct_ffinal,
                select.distinct_final_ffinal,
            ],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.distinct_result_check,
                select.distinct_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(tables=tables, selects=selects, iterations=10)

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT DISTINCT parallel inserts, deletes, updates")
def select_distinct_parallel_idu(self):
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

    with And("I choose selects, inserts, updates, deletes  for testing"):
        selects = define(
            "Select statements",
            [
                select.distinct,
                select.distinct_final,
                select.distinct_ffinal,
                select.distinct_final_ffinal,
            ],
        )
        inserts = define(
            "Insert statements",
            [insert],
        )
        updates = define(
            "Update statements",
            [update],
        )

        deletes = define(
            "Delete statements",
            [delete],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.distinct_result_check,
                select.distinct_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(
            tables=tables,
            selects=selects,
            inserts=inserts,
            deletes=deletes,
            updates=updates,
            iterations=10,
        )

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT PREWHERE parallel")
def select_prewhere_parallel(self):
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

    with And("I choose selects for testing"):
        selects = define(
            "Select statements",
            [
                select.prewhere,
                select.prewhere_final,
                select.prewhere_ffinal,
                select.prewhere_final_ffinal,
            ],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.prewhere_result_check,
                select.prewhere_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(tables=tables, selects=selects, iterations=10)

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT PREWHERE parallel inserts, deletes, updates")
def select_prewhere_parallel_idu(self):
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

    with And("I choose selects, inserts, updates, deletes for testing"):
        selects = define(
            "Select statements",
            [
                select.prewhere,
                select.prewhere_final,
                select.prewhere_ffinal,
                select.prewhere_final_ffinal,
            ],
        )
        inserts = define(
            "Insert statements",
            [insert],
        )
        updates = define(
            "Update statements",
            [update],
        )

        deletes = define(
            "Delete statements",
            [delete],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.prewhere_result_check,
                select.prewhere_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(
            tables=tables,
            selects=selects,
            inserts=inserts,
            deletes=deletes,
            updates=updates,
            iterations=10,
        )

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT WHERE parallel")
def select_where_parallel(self):
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

    with And("I choose selects for testing"):
        selects = define(
            "Select statements",
            [
                select.where,
                select.where_final,
                select.where_ffinal,
                select.where_final_ffinal,
            ],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.where_result_check,
                select.where_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(tables=tables, selects=selects, iterations=10)

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT WHERE parallel inserts, deletes, updates")
def select_where_parallel_idu(self):
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

    with And("I choose selects, inserts, updates, deletes for testing"):
        selects = define(
            "Select statements",
            [
                select.where,
                select.where_final,
                select.where_ffinal,
                select.where_final_ffinal,
            ],
        )
        inserts = define(
            "Insert statements",
            [insert],
        )
        updates = define(
            "Update statements",
            [update],
        )

        deletes = define(
            "Delete statements",
            [delete],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.where_result_check,
                select.where_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(
            tables=tables,
            selects=selects,
            inserts=inserts,
            deletes=deletes,
            updates=updates,
            iterations=10,
        )

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestScenario
@Name("SELECT all simple selects parallel")
def all_simple_selects_parallel(self):
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

    with And("I choose selects for testing"):
        selects = define(
            "Select statements",
            [
                select.prewhere,
                select.prewhere_final,
                select.prewhere_ffinal,
                select.prewhere_final_ffinal,
                select.count,
                select.count_final,
                select.count_ffinal,
                select.count_final_ffinal,
                select.limit,
                select.limit_final,
                select.limit_ffinal,
                select.limit_final_ffinal,
                select.limit_by,
                select.limit_by_final,
                select.limit_by_ffinal,
                select.limit_by_final_ffinal,
                select.group_by,
                select.group_by_final,
                select.group_by_ffinal,
                select.group_by_final_ffinal,
                select.where,
                select.where_final,
                select.where_ffinal,
                select.where_final_ffinal,
                select.distinct,
                select.distinct_final,
                select.distinct_ffinal,
                select.distinct_final_ffinal,
            ],
        )

    with And("I choose check selects for testing"):
        selects_check = define(
            "Select statements",
            [
                select.prewhere_result_check,
                select.prewhere_negative_result_check,
                select.where_result_check,
                select.where_negative_result_check,
                select.count_result_check,
                select.count_negative_result_check,
                select.limit_result_check,
                select.limit_negative_result_check,
                select.limit_by_result_check,
                select.limit_by_negative_result_check,
                select.group_by_result_check,
                select.group_by_negative_result_check,
                select.distinct_result_check,
                select.distinct_negative_result_check,
            ],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        parallel_outline(tables=tables, selects=selects, iterations=10)

    join()

    with Then("I check results"):
        parallel_outline(
            tables=tables, selects=selects_check, iterations=1, parallel_select=False
        )


@TestModule
@Requirements()
@Name("force modifier concurrent")
def feature(self):
    """Parallel queries tests for force select final."""
    if check_clickhouse_version("<22.11")(self):
        skip(
            reason="force_select_final is only supported on ClickHouse version >= 22.11"
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
