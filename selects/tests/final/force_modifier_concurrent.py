import tests.select_steps as select
from helpers.common import check_clickhouse_version
from selects.requirements.automatic_final_modifier import *
from tests.steps import *


@TestScenario
@Name("SELECT count() parallel")
def select_count_parallel(self):
    """Scenario to check all `SELECT count()` combinations with/without `FINAL` and --final enabled/disabled
    in parallel doesn't break force select final"""

    selects = []

    with Given("I select count() query without FINAL and without --final"):
        selects.append(select.count)

    with And("I select count() query with FINAL clause"):
        selects.append(select.count_with_final_clause)

    with And("I select count() query with --final"):
        selects.append(select.count_with_force_final)

    with And("I select count() query with FINAL clause and with --final"):
        selects.append(select.count_with_final_clause_and_force_final)

    for table in self.context.tables:
        with Example(f"{table.name}", flags=TE):
            with When("I execute selects concurrently"):
                run_queries_in_parallel(table=table, selects=selects, iterations=10)

            join()

            with Then(
                "Compare results between count() query with `FINAL`  clause "
                "and count() query with --final setting enabled."
            ):
                select.count_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )

            with And(
                "Compare results between count() query with --final "
                "and count() query without `FINAL` and without --final."
            ):
                select.count_negative_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )


@TestScenario
@Name("SELECT count() parallel inserts, deletes, updates")
def select_count_parallel_idu(self):
    """Scenario to check all `SELECT count()` combinations with/without, final/force_final in parallel with
    inserts, updates and deletes doesn't break force select final"""

    selects = []

    with Given("I select count() query without FINAL and without --final"):
        selects.append(select.count)

    with And("I select count() query with FINAL clause"):
        selects.append(select.count_with_final_clause)

    with And("I select count() query with --final"):
        selects.append(select.count_with_force_final)

    with And("I select count() query with FINAL clause and with --final"):
        selects.append(select.count_with_final_clause_and_force_final)

    with Given("I select insert statement"):
        inserts = define(
            "Insert statements",
            [insert],
        )

    with Given("I select update statement"):
        updates = define(
            "Update statements",
            [update],
        )

    with And("I select delete statement"):
        deletes = define(
            "Delete statements",
            [delete],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        for table in self.context.tables:
            with Example(f"{table.name}", flags=TE):
                with When("I execute selects concurrently"):
                    run_queries_in_parallel(
                        table=table,
                        selects=selects,
                        inserts=inserts,
                        updates=updates,
                        deletes=deletes,
                        iterations=10,
                    )

                join()

                with Then(
                    "Compare results between count() query with `FINAL`  clause "
                    "and count() query with --final setting enabled."
                ):
                    select.count_result_check(
                        table=table.name,
                        final_modifier_available=table.final_modifier_available,
                    )

                with And(
                    "Compare results between count() query with --final "
                    "and count() query without `FINAL` and without --final."
                ):
                    select.count_negative_result_check(
                        table=table.name,
                        final_modifier_available=table.final_modifier_available,
                    )


@TestScenario
@Name("`SELECT column as new_column` parallel")
def select_as_parallel(self):
    """Scenario to check all `SELECT column as new_column` combinations with/without `FINAL` and --final enabled/disabled
    in parallel doesn't break force select final"""

    selects = []

    with Given(
        "I select `SELECT column as new_column` query without FINAL and without --final"
    ):
        selects.append(select.as_statement)

    with And("I select `SELECT column as new_column` query with FINAL clause"):
        selects.append(select.as_with_final_clause)

    with And("I select `SELECT column as new_column` query with --final"):
        selects.append(select.as_with_force_final)

    with And(
        "I select `SELECT column as new_column` query with FINAL clause and with --final"
    ):
        selects.append(select.as_with_final_clause_and_force_final)

    for table in self.context.tables:
        with Example(f"{table.name}", flags=TE):
            with When("I execute selects concurrently"):
                run_queries_in_parallel(table=table, selects=selects, iterations=10)

            join()

            with Then(
                "Compare results between `SELECT column as new_column` query with `FINAL`  clause "
                "and `SELECT column as new_column` query with --final setting enabled."
            ):
                select.as_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )

            with And(
                "Compare results between `SELECT column as new_column` query with --final "
                "and `SELECT column as new_column` query without `FINAL` and without --final."
            ):
                select.as_negative_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )


@TestScenario
@Name("`SELECT column as new_column` parallel inserts, deletes, updates")
def select_as_parallel_idu(self):
    """Scenario to check all `SELECT column as new_column` combinations with/without, final/force_final in parallel with
    inserts, updates and deletes doesn't break force select final"""

    selects = []

    with Given(
        "I select `SELECT column as new_column` query without FINAL and without --final"
    ):
        selects.append(select.as_statement)

    with And("I select `SELECT column as new_column` query with FINAL clause"):
        selects.append(select.as_with_final_clause)

    with And("I select `SELECT column as new_column` query with --final"):
        selects.append(select.as_with_force_final)

    with And(
        "I select `SELECT column as new_column` query with FINAL clause and with --final"
    ):
        selects.append(select.as_with_final_clause_and_force_final)

    with Given("I select insert statement"):
        inserts = define(
            "Insert statements",
            [insert],
        )

    with Given("I select update statement"):
        updates = define(
            "Update statements",
            [update],
        )

    with And("I select delete statement"):
        deletes = define(
            "Delete statements",
            [delete],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        for table in self.context.tables:
            with Example(f"{table.name}", flags=TE):
                with When("I execute selects concurrently"):
                    run_queries_in_parallel(
                        table=table,
                        selects=selects,
                        inserts=inserts,
                        updates=updates,
                        deletes=deletes,
                        iterations=10,
                    )

                join()

                with Then(
                    "Compare results between `SELECT column as new_column` query with `FINAL`  clause "
                    "and `SELECT column as new_column` query with --final setting enabled."
                ):
                    select.as_result_check(
                        table=table.name,
                        final_modifier_available=table.final_modifier_available,
                    )

                with And(
                    "Compare results between `SELECT column as new_column` query with --final "
                    "and `SELECT column as new_column` query without `FINAL` and without --final."
                ):
                    select.as_negative_result_check(
                        table=table.name,
                        final_modifier_available=table.final_modifier_available,
                    )


@TestScenario
@Name("SELECT DISTINCT parallel")
def select_distinct_parallel(self):
    """Scenario to check all `SELECT DISTINCT` combinations with/without `FINAL` and --final enabled/disabled
    in parallel doesn't break force select final"""

    selects = []

    with Given("I select `SELECT DISTINCT` query without FINAL and without --final"):
        selects.append(select.distinct)

    with And("I select `SELECT DISTINCT` query with FINAL clause"):
        selects.append(select.distinct_with_final_clause)

    with And("I select `SELECT DISTINCT` query with --final"):
        selects.append(select.distinct_with_force_final)

    with And("I select `SELECT DISTINCT` query with FINAL clause and with --final"):
        selects.append(select.distinct_with_final_clause_and_force_final)

    for table in self.context.tables:
        with Example(f"{table.name}", flags=TE):
            with When("I execute selects concurrently"):
                run_queries_in_parallel(table=table, selects=selects, iterations=10)

            join()

            with Then(
                "Compare results between `SELECT DISTINCT` query with `FINAL`  clause "
                "and `SELECT DISTINCT` query with --final setting enabled."
            ):
                select.distinct_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )

            with And(
                "Compare results between `SELECT DISTINCT` query with --final "
                "and `SELECT DISTINCT` query without `FINAL` and without --final."
            ):
                select.distinct_negative_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )


@TestScenario
@Name("SELECT DISTINCT parallel inserts, deletes, updates")
def select_distinct_parallel_idu(self):
    """Scenario to check all `SELECT DISTINCT` combinations with/without, final/force_final in parallel with
    inserts, updates and deletes doesn't break force select final"""

    selects = []

    with Given("I select `SELECT DISTINCT` query without FINAL and without --final"):
        selects.append(select.distinct)

    with And("I select `SELECT DISTINCT` query with FINAL clause"):
        selects.append(select.distinct_with_final_clause)

    with And("I select `SELECT DISTINCT` query with --final"):
        selects.append(select.distinct_with_force_final)

    with And("I select `SELECT DISTINCT` query with FINAL clause and with --final"):
        selects.append(select.distinct_with_final_clause_and_force_final)

    with Given("I select insert statement"):
        inserts = define(
            "Insert statements",
            [insert],
        )

    with Given("I select update statement"):
        updates = define(
            "Update statements",
            [update],
        )

    with And("I select delete statement"):
        deletes = define(
            "Delete statements",
            [delete],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        for table in self.context.tables:
            with Example(f"{table.name}", flags=TE):
                with When("I execute selects concurrently"):
                    run_queries_in_parallel(
                        table=table,
                        selects=selects,
                        inserts=inserts,
                        updates=updates,
                        deletes=deletes,
                        iterations=10,
                    )

                join()

                with Then(
                    "Compare results between `SELECT DISTINCT` query with `FINAL`  clause "
                    "and `SELECT DISTINCT` query with --final setting enabled."
                ):
                    select.distinct_result_check(
                        table=table.name,
                        final_modifier_available=table.final_modifier_available,
                    )

                with And(
                    "Compare results between `SELECT DISTINCT` query with --final "
                    "and `SELECT DISTINCT` query without `FINAL` and without --final."
                ):
                    select.distinct_negative_result_check(
                        table=table.name,
                        final_modifier_available=table.final_modifier_available,
                    )


@TestScenario
@Name("SELECT GROUP BY parallel")
def select_group_by_parallel(self):
    """Scenario to check all `SELECT GROUP BY` combinations with/without `FINAL` and --final enabled/disabled
    in parallel doesn't break force select final"""

    selects = []

    with Given("I select `SELECT GROUP BY` query without FINAL and without --final"):
        selects.append(select.group_by)

    with And("I select `SELECT GROUP BY` query with FINAL clause"):
        selects.append(select.group_by_with_final_clause)

    with And("I select `SELECT GROUP BY` query with --final"):
        selects.append(select.group_by_with_force_final)

    with And("I select `SELECT GROUP BY` query with FINAL clause and with --final"):
        selects.append(select.group_by_with_final_clause_and_force_final)

    for table in self.context.tables:
        with Example(f"{table.name}", flags=TE):
            with When("I execute selects concurrently"):
                run_queries_in_parallel(table=table, selects=selects, iterations=10)

            join()

            with Then(
                "Compare results between `SELECT GROUP BY` query with `FINAL`  clause "
                "and `SELECT GROUP BY` query with --final setting enabled."
            ):
                select.group_by_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )

            with And(
                "Compare results between `SELECT GROUP BY` query with --final "
                "and `SELECT GROUP BY` query without `FINAL` and without --final."
            ):
                select.group_by_negative_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )


@TestScenario
@Name("SELECT GROUP BY parallel inserts, deletes, updates")
def select_group_by_parallel_idu(self):
    """Scenario to check all `SELECT GROUP BY` combinations with/without, final/force_final in parallel with
    inserts, updates and deletes doesn't break force select final"""

    selects = []

    with Given("I select `SELECT GROUP BY` query without FINAL and without --final"):
        selects.append(select.group_by)

    with And("I select `SELECT GROUP BY` query with FINAL clause"):
        selects.append(select.group_by_with_final_clause)

    with And("I select `SELECT GROUP BY` query with --final"):
        selects.append(select.group_by_with_force_final)

    with And("I select `SELECT GROUP BY` query with FINAL clause and with --final"):
        selects.append(select.group_by_with_final_clause_and_force_final)

    with Given("I select insert statement"):
        inserts = define(
            "Insert statements",
            [insert],
        )

    with Given("I select update statement"):
        updates = define(
            "Update statements",
            [update],
        )

    with And("I select delete statement"):
        deletes = define(
            "Delete statements",
            [delete],
        )

    with When("I execute concurrent select, insert, delete, update queries"):
        for table in self.context.tables:
            with Example(f"{table.name}", flags=TE):
                with When("I execute selects concurrently"):
                    run_queries_in_parallel(
                        table=table,
                        selects=selects,
                        inserts=inserts,
                        updates=updates,
                        deletes=deletes,
                        iterations=10,
                    )

                join()

                with Then(
                    "Compare results between `SELECT GROUP BY` query with `FINAL`  clause "
                    "and `SELECT GROUP BY` query with --final setting enabled."
                ):
                    select.group_by_result_check(
                        table=table.name,
                        final_modifier_available=table.final_modifier_available,
                    )

                with And(
                    "Compare results between `SELECT GROUP BY` query with --final "
                    "and `SELECT GROUP BY` query without `FINAL` and without --final."
                ):
                    select.group_by_negative_result_check(
                        table=table.name,
                        final_modifier_available=table.final_modifier_available,
                    )


#
#
# @TestScenario
# @Name("SELECT LIMIT parallel")
# def select_limit_parallel(self):
#     """Scenario to check all `SELECT ... LIMIT` combinations with/without, final/force_final in parallel
#     doesn't break force select final"""
#
#     tables = table_selection()
#
#     with Given("I choose selects for testing"):
#         selects = define(
#             "Select statements",
#             [
#                 select.limit,
#                 select.limit_final,
#                 select.limit_ffinal,
#                 select.limit_final_ffinal,
#             ],
#         )
#
#     with And("I choose check selects for testing"):
#         selects_check = define(
#             "Select statements",
#             [
#                 select.limit_result_check,
#                 select.limit_negative_result_check,
#             ],
#         )
#
#     with When("I execute concurrent select, insert, delete, update queries"):
#         parallel_outline(tables=tables, selects=selects, iterations=10)
#
#     join()
#
#     with Then("I check results"):
#         parallel_outline(
#             tables=tables, selects=selects_check, iterations=1, parallel_select=False
#         )
#
#
# @TestScenario
# @Name("SELECT LIMIT parallel inserts, deletes, updates")
# def select_limit_parallel_idu(self):
#     """Scenario to check all `SELECT ... LIMIT` combinations with/without, final/force_final in parallel with
#     inserts, updates and deletes doesn't break force select final"""
#
#     tables = table_selection()
#
#     with Given("I choose selects, inserts, updates, deletes  for testing"):
#         selects = define(
#             "Select statements",
#             [
#                 select.limit,
#                 select.limit_final,
#                 select.limit_ffinal,
#                 select.limit_final_ffinal,
#             ],
#         )
#         inserts = define(
#             "Insert statements",
#             [insert],
#         )
#         updates = define(
#             "Update statements",
#             [update],
#         )
#
#         deletes = define(
#             "Delete statements",
#             [delete],
#         )
#
#     with And("I choose check selects for testing"):
#         selects_check = define(
#             "Select statements",
#             [
#                 select.limit_result_check,
#                 select.limit_negative_result_check,
#             ],
#         )
#
#     with When("I execute concurrent select, insert, delete, update queries"):
#         parallel_outline(
#             tables=tables,
#             selects=selects,
#             inserts=inserts,
#             deletes=deletes,
#             updates=updates,
#             iterations=10,
#         )
#
#     join()
#
#     with Then("I check results"):
#         parallel_outline(
#             tables=tables, selects=selects_check, iterations=1, parallel_select=False
#         )
#
#
# @TestScenario
# @Name("SELECT LIMIT BY parallel")
# def select_limit_by_parallel(self):
#     """Scenario to check all `SELECT ... LIMIT BY` combinations with/without, final/force_final in parallel
#     doesn't break force select final"""
#
#     tables = table_selection()
#
#     with Given("I choose selects for testing"):
#         selects = define(
#             "Select statements",
#             [
#                 select.limit_by,
#                 select.limit_by_final,
#                 select.limit_by_ffinal,
#                 select.limit_by_final_ffinal,
#             ],
#         )
#
#     with And("I choose check selects for testing"):
#         selects_check = define(
#             "Select statements",
#             [
#                 select.limit_by_result_check,
#                 select.limit_by_negative_result_check,
#             ],
#         )
#
#     with When("I execute concurrent select, insert, delete, update queries"):
#         parallel_outline(tables=tables, selects=selects, iterations=10)
#
#     join()
#
#     with Then("I check results"):
#         parallel_outline(
#             tables=tables, selects=selects_check, iterations=1, parallel_select=False
#         )
#
#
# @TestScenario
# @Name("SELECT LIMIT BY parallel inserts, deletes, updates")
# def select_limit_by_parallel_idu(self):
#     """Scenario to check all `SELECT ... LIMIT BY` combinations with/without, final/force_final in parallel with
#     inserts, updates and deletes doesn't break force select final"""
#
#     tables = table_selection()
#
#     with Given("I choose selects, inserts, updates, deletes  for testing"):
#         selects = define(
#             "Select statements",
#             [
#                 select.limit_by,
#                 select.limit_by_final,
#                 select.limit_by_ffinal,
#                 select.limit_by_final_ffinal,
#             ],
#         )
#         inserts = define(
#             "Insert statements",
#             [insert],
#         )
#         updates = define(
#             "Update statements",
#             [update],
#         )
#
#         deletes = define(
#             "Delete statements",
#             [delete],
#         )
#
#     with And("I choose check selects for testing"):
#         selects_check = define(
#             "Select statements",
#             [
#                 select.limit_by_result_check,
#                 select.limit_by_negative_result_check,
#             ],
#         )
#
#     with When("I execute concurrent select, insert, delete, update queries"):
#         parallel_outline(
#             tables=tables,
#             selects=selects,
#             inserts=inserts,
#             deletes=deletes,
#             updates=updates,
#             iterations=10,
#         )
#
#     join()
#
#     with Then("I check results"):
#         parallel_outline(
#             tables=tables, selects=selects_check, iterations=1, parallel_select=False
#         )
#
#
#
#
#
#
# @TestScenario
# @Name("SELECT PREWHERE parallel")
# def select_prewhere_parallel(self):
#     """Scenario to check all `SELECT ... PREWHERE` combinations with/without, final/force_final in parallel
#     doesn't break force select final"""
#
#     tables = table_selection()
#
#     with Given("I choose selects for testing"):
#         selects = define(
#             "Select statements",
#             [
#                 select.prewhere,
#                 select.prewhere_final,
#                 select.prewhere_ffinal,
#                 select.prewhere_final_ffinal,
#             ],
#         )
#
#     with And("I choose check selects for testing"):
#         selects_check = define(
#             "Select statements",
#             [
#                 select.prewhere_result_check,
#                 select.prewhere_negative_result_check,
#             ],
#         )
#
#     with When("I execute concurrent select, insert, delete, update queries"):
#         parallel_outline(tables=tables, selects=selects, iterations=10)
#
#     join()
#
#     with Then("I check results"):
#         parallel_outline(
#             tables=tables, selects=selects_check, iterations=1, parallel_select=False
#         )
#
#
# @TestScenario
# @Name("SELECT PREWHERE parallel inserts, deletes, updates")
# def select_prewhere_parallel_idu(self):
#     """Scenario to check all `SELECT PREWHERE` combinations with/without, final/force_final in parallel with
#     inserts, updates and deletes doesn't break force select final"""
#
#     tables = table_selection()
#
#     with Given("I choose selects, inserts, updates, deletes for testing"):
#         selects = define(
#             "Select statements",
#             [
#                 select.prewhere,
#                 select.prewhere_final,
#                 select.prewhere_ffinal,
#                 select.prewhere_final_ffinal,
#             ],
#         )
#         inserts = define(
#             "Insert statements",
#             [insert],
#         )
#         updates = define(
#             "Update statements",
#             [update],
#         )
#
#         deletes = define(
#             "Delete statements",
#             [delete],
#         )
#
#     with And("I choose check selects for testing"):
#         selects_check = define(
#             "Select statements",
#             [
#                 select.prewhere_result_check,
#                 select.prewhere_negative_result_check,
#             ],
#         )
#
#     with When("I execute concurrent select, insert, delete, update queries"):
#         parallel_outline(
#             tables=tables,
#             selects=selects,
#             inserts=inserts,
#             deletes=deletes,
#             updates=updates,
#             iterations=10,
#         )
#
#     join()
#
#     with Then("I check results"):
#         parallel_outline(
#             tables=tables, selects=selects_check, iterations=1, parallel_select=False
#         )
#
#
# @TestScenario
# @Name("SELECT WHERE parallel")
# def select_where_parallel(self):
#     """Scenario to check all `SELECT ... WHERE` combinations with/without, final/force_final in parallel
#     doesn't break force select final"""
#
#     tables = table_selection()
#
#     with Given("I choose selects for testing"):
#         selects = define(
#             "Select statements",
#             [
#                 select.where,
#                 select.where_final,
#                 select.where_ffinal,
#                 select.where_final_ffinal,
#             ],
#         )
#
#     with And("I choose check selects for testing"):
#         selects_check = define(
#             "Select statements",
#             [
#                 select.where_result_check,
#                 select.where_negative_result_check,
#             ],
#         )
#
#     with When("I execute concurrent select, insert, delete, update queries"):
#         parallel_outline(tables=tables, selects=selects, iterations=10)
#
#     join()
#
#     with Then("I check results"):
#         parallel_outline(
#             tables=tables, selects=selects_check, iterations=1, parallel_select=False
#         )
#
#
# @TestScenario
# @Name("SELECT WHERE parallel inserts, deletes, updates")
# def select_where_parallel_idu(self):
#     """Scenario to check all `SELECT WHERE` combinations with/without, final/force_final in parallel with
#     inserts, updates and deletes doesn't break force select final"""
#
#     tables = table_selection()
#
#     with Given("I choose selects, inserts, updates, deletes for testing"):
#         selects = define(
#             "Select statements",
#             [
#                 select.where,
#                 select.where_final,
#                 select.where_ffinal,
#                 select.where_final_ffinal,
#             ],
#         )
#         inserts = define(
#             "Insert statements",
#             [insert],
#         )
#         updates = define(
#             "Update statements",
#             [update],
#         )
#
#         deletes = define(
#             "Delete statements",
#             [delete],
#         )
#
#     with And("I choose check selects for testing"):
#         selects_check = define(
#             "Select statements",
#             [
#                 select.where_result_check,
#                 select.where_negative_result_check,
#             ],
#         )
#
#     with When("I execute concurrent select, insert, delete, update queries"):
#         parallel_outline(
#             tables=tables,
#             selects=selects,
#             inserts=inserts,
#             deletes=deletes,
#             updates=updates,
#             iterations=10,
#         )
#
#     join()
#
#     with Then("I check results"):
#         parallel_outline(
#             tables=tables, selects=selects_check, iterations=1, parallel_select=False
#         )
#


@TestScenario
def all_simple_selects_parallel(self):
    """Scenario to check all simple selects with all: combinations with/without `FINAL` and --final enabled/disabled
    in parallel doesn't break force select final"""

    for table in self.context.tables:
        with Example(f"{table.name}", flags=TE):
            with When(
                "I start all `SELECT count()` combinations with/without `FINAL` and --final enabled/disabled"
            ):
                select.count_all_combinations(table=table)

            with And(
                "I start all `SELECT column as new_column` combinations with/without `FINAL` "
                "and --final enabled/disabled"
            ):
                select.as_all_combinations(table=table)

            with And(
                "I start all `SELECT DISTINCT` combinations with/without `FINAL` "
                "and --final enabled/disabled"
            ):
                select.distinct_all_combinations(table=table)

            with And(
                "I start all `SELECT GROUP BY` combinations with/without `FINAL` "
                "and --final enabled/disabled"
            ):
                select.group_by_all_combinations(table=table)

            join()

            with Then(
                "Compare results all previous select types between query with `FINAL` clause "
                "and query with --final setting enabled."
            ):
                select.count_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )

                select.as_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )

                select.distinct_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )

                select.group_by_result_check(
                    table=table.name,
                    final_modifier_available=table.final_modifier_available,
                )


@TestModule
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Parallel("1.0")
)
@Name("force modifier concurrent")
def feature(self):
    """Parallel queries tests for force select final."""
    if check_clickhouse_version("<22.11")(self):
        skip(
            reason="force_select_final is only supported on ClickHouse version >= 22.11"
        )

    with Given("I choose only ReplacingMergeTree and MergeTree tables"):
        self.context.tables = define(
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

    for scenario in loads(current_module(), Scenario):
        scenario()
