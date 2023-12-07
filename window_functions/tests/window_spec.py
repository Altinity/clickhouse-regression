from testflows.core import *
from window_functions.requirements import *
from window_functions.tests.common import *


@TestScenario
def partition_clause(self):
    """Check window specification that only contains partition clause."""
    expected = convert_output(
        """
     sum 
    -------
    7400
    7400
    14600
    14600
    14600
    25100
    25100
    25100
    25100
    25100
    """
    )

    execute_query(
        "SELECT sum(salary) OVER w AS sum FROM empsalary WINDOW w AS (PARTITION BY depname) ORDER BY sum",
        expected=expected,
    )


@TestScenario
def orderby_clause(self):
    """Check window specification that only contains order by clause."""
    expected = convert_output(
        """
     sum 
    -------
    25100
    25100
    25100
    25100
    25100
    32500
    32500
    47100
    47100
    47100
    """
    )

    execute_query(
        "SELECT sum(salary) OVER w AS sum FROM empsalary WINDOW w AS (ORDER BY depname) ORDER BY sum",
        expected=expected,
    )


@TestScenario
def frame_clause(self):
    """Check window specification that only contains frame clause."""
    expected = convert_output(
        """
     sum 
    -------
    3500
    3900
    4200
    4500
    4800
    4800
    5000
    5200
    5200
    6000
    """
    )

    execute_query(  
        "SELECT sum(salary) OVER w AS sum FROM empsalary WINDOW w AS (ORDER BY empno ROWS CURRENT ROW) ORDER BY sum",
        expected=expected,
    )


@TestScenario
def partition_with_order_by(self):
    """Check window specification that contains partition and order by clauses."""
    expected = convert_output(
        """
     sum 
    -------
    3500
    4200
    7400
    8700
    9600
    9600
    14600
    19100
    19100
    25100
    """
    )

    execute_query(
        "SELECT sum(salary) OVER w AS sum FROM empsalary WINDOW w AS (PARTITION BY depname ORDER BY salary) ORDER BY sum",
        expected=expected,
    )


@TestScenario
def partition_with_frame(self):
    """Check window specification that contains partition and frame clauses."""
    expected = convert_output(
        """
     sum 
    -------
    3500
    3900
    4200
    4500
    4800
    4800
    5000
    5200
    5200
    6000
    """
    )

    execute_query(
        "SELECT sum(salary) OVER w AS sum FROM empsalary  WINDOW w AS (PARTITION BY depname, empno ROWS 1 PRECEDING) ORDER BY sum",
        expected=expected,
    )


@TestScenario
def order_by_with_frame(self):
    """Check window specification that contains order by and frame clauses."""
    expected = convert_output(
        """
     sum 
    -------
    4200
    7400
    8500
    9100
    9600
    9700
    9800
    10200
    10400
    10500
    """
    )

    execute_query(
        "SELECT sum(salary) OVER w AS sum FROM empsalary WINDOW w AS (ORDER BY depname, empno ROWS 1 PRECEDING) ORDER BY sum",
        expected=expected,
    )


@TestScenario
def partition_with_order_by_and_frame(self):
    """Check window specification that contains all clauses."""
    expected = convert_output(
        """
     sum 
    -------
    3500
    4200
    4800
    7400
    8700
    9600
    9700
    9800
    10400
    11200
    """
    )

    execute_query(
        "SELECT sum(salary) OVER w AS sum FROM empsalary WINDOW w AS (PARTITION BY depname ORDER BY salary ROWS 1 PRECEDING) ORDER BY sum",
        expected=expected,
    )


@TestScenario
def empty(self):
    """Check defining an empty window specification."""
    expected = convert_output(
        """
     sum 
    -------
     47100
     47100
     47100
     47100
     47100
     47100
     47100
     47100
     47100
     47100
    """
    )

    execute_query(
        "SELECT sum(salary) OVER w AS sum FROM empsalary WINDOW w AS ()",
        expected=expected,
    )


@TestFeature
@Name("window spec")
@Requirements(RQ_SRS_019_ClickHouse_WindowFunctions_WindowSpec("1.0"))
def feature(self):
    """Check defining window specifications."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
