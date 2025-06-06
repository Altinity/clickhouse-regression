from testflows.core import *
from helpers.common import check_clickhouse_version

from window_functions.requirements import *
from window_functions.tests.common import *


@TestScenario
def error_using_non_window_function(self):
    """Check that trying to use non window or aggregate function over a window
    returns an error.
    """
    exitcode = 63
    message = "DB::Exception: Unknown aggregate function numbers"

    if is_with_analyzer(node=self.context.node):
        exitcode = 63
        message = (
            "DB::Exception: Aggregate function with name 'numbers' does not exists."
        )
        if check_clickhouse_version(">=24.5")(self):
            exitcode = 63
            message = (
                "DB::Exception: Aggregate function with name 'numbers' does not exist."
            )

    sql = "SELECT numbers(1, 100) OVER () FROM empsalary FORMAT TabSeparated"

    with When("I execute query", description=sql):
        r = current().context.node.query(sql, exitcode=exitcode, message=message)


@TestScenario
def error_order_by_another_window_function(self):
    """Check that trying to order by another window function returns an error."""
    exitcode = 184
    message = "DB::Exception: Window function rank() OVER (ORDER BY rand() ASC) is found inside window definition in query"

    if is_with_analyzer(node=self.context.node):
        exitcode = 10
        message = "DB::Exception: Not found column rank() OVER"

    sql = "SELECT rank() OVER (ORDER BY rank() OVER (ORDER BY rand())) FORMAT TabSeparated"

    with When("I execute query", description=sql):
        r = current().context.node.query(sql, exitcode=exitcode, message=message)


@TestScenario
def error_window_function_in_where(self):
    """Check that trying to use window function in `WHERE` returns an error."""
    exitcode = 184
    message = "DB::Exception: Window function row_number() OVER (ORDER BY salary ASC) is found in WHERE in query"

    sql = "SELECT * FROM empsalary WHERE row_number() OVER (ORDER BY salary) < 10 FORMAT TabSeparated"

    with When("I execute query", description=sql):
        r = current().context.node.query(sql, exitcode=exitcode, message=message)


@TestScenario
def error_window_function_in_join(self):
    """Check that trying to use window function in `JOIN` returns an error."""
    note(self.context.clickhouse_version)

    if self.context.distributed:
        allow_distributed_product_mode()

    exitcode = 48 if check_clickhouse_version("<21.9")(self) else 147
    message = (
        "DB::Exception: JOIN ON inequalities are not supported"
        if check_clickhouse_version("<21.9")(self)
        else "DB::Exception: Cannot get JOIN keys from JOIN ON section"
    )
    if is_with_analyzer(node=self.context.node):
        exitcode = 184
        message = "DB::Exception: Window function row_number() OVER (ORDER BY salary ASC) is found in JOIN TREE in query."

    sql = "SELECT * FROM empsalary INNER JOIN tenk1 ON row_number() OVER (ORDER BY salary) < 10 FORMAT TabSeparated"

    with When(f"I execute query", description=sql):
        r = current().context.node.query(sql, exitcode=exitcode, message=message)


@TestScenario
def error_window_function_in_group_by(self):
    """Check that trying to use window function in `GROUP BY` returns an error."""
    exitcode = 47
    message = "DB::Exception: Unknown identifier"

    if is_with_analyzer(node=self.context.node):
        exitcode = 184
        message = "DB::Exception: Received from localhost:9000. DB::Exception: Window function row_number() OVER (ORDER BY salary ASC) is found in GROUP BY in query."

    sql = "SELECT rank() OVER (ORDER BY 1), count(*) FROM empsalary GROUP BY row_number() OVER (ORDER BY salary) < 10 FORMAT TabSeparated"

    with When("I execute query", description=sql):
        r = current().context.node.query(sql, exitcode=exitcode, message=message)


@TestScenario
def error_window_function_in_having(self):
    """Check that trying to use window function in `HAVING` returns an error."""
    exitcode = 184
    message = "DB::Exception: Window function row_number() OVER (ORDER BY salary ASC) is found in HAVING in query"

    sql = "SELECT rank() OVER (ORDER BY 1), count(*) FROM empsalary GROUP BY salary HAVING row_number() OVER (ORDER BY salary) < 10 FORMAT TabSeparated"

    with When("I execute query", description=sql):
        r = current().context.node.query(sql, exitcode=exitcode, message=message)


@TestScenario
def error_select_from_window(self):
    """Check that trying to use window function in `FROM` returns an error."""
    exitcode = 46
    message = "DB::Exception: Unknown table function rank"

    sql = "SELECT * FROM rank() OVER (ORDER BY rand()) FORMAT TabSeparated"

    with When("I execute query", description=sql):
        r = current().context.node.query(sql, exitcode=exitcode, message=message)


@TestScenario
def error_window_function_in_alter_delete_where(self):
    """Check that trying to use window function in `ALTER DELETE`'s `WHERE` clause returns an error."""
    if self.context.distributed:
        exitcode = 48
        message = "Exception: Table engine Distributed doesn't support mutations"
    elif check_clickhouse_version(">=23.1")(self):
        exitcode = 47
        message = "Exception: Unknown identifier: rank() OVER (ORDER BY rand() ASC)"
    else:
        exitcode = 184
        message = "DB::Exception: Window function rank() OVER (ORDER BY rand() ASC) is found in WHERE in query"

    sql = "ALTER TABLE empsalary DELETE WHERE (rank() OVER (ORDER BY rand())) > 10"

    with When("I execute query", description=sql):
        r = current().context.node.query(sql, exitcode=exitcode, message=message)


@TestScenario
def error_named_window_defined_twice(self):
    """Check that trying to define named window twice."""
    exitcode = 36
    message = "DB::Exception: Window 'w' is defined twice in the WINDOW clause"

    sql = "SELECT count(*) OVER w FROM tenk1 WINDOW w AS (ORDER BY unique1), w AS (ORDER BY unique1) FORMAT TabSeparated"

    with When("I execute query", description=sql):
        r = current().context.node.query(sql, exitcode=exitcode, message=message)


@TestScenario
def error_coma_between_partition_by_and_order_by_clause(self):
    """Check that trying to use a coma between partition by and order by clause."""
    exitcode = 62
    message = "DB::Exception: Syntax error"

    sql = "SELECT rank() OVER (PARTITION BY four, ORDER BY ten) FROM tenk1 FORMAT TabSeparated"

    with When("I execute query", description=sql):
        r = current().context.node.query(sql, exitcode=exitcode, message=message)


@TestFeature
@Name("errors")
def feature(self):
    """Check different error conditions."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
