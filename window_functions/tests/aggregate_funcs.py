from tracemalloc import Snapshot
from testflows.core import *
from testflows.asserts import values, error, snapshot

from window_functions.requirements import *
from window_functions.tests.common import *


@TestOutline(Scenario)
@Examples(
    "func",
    [
        ("count(salary)",),
        ("min(salary)",),
        ("max(salary)",),
        ("sum(salary)",),
        ("avg(salary)",),
        ("any(salary)",),
        ("stddevPop(salary)",),
        ("stddevSamp(salary)",),
        ("varPop(salary)",),
        ("varSamp(salary)",),
        ("covarPop(salary, 2000)",),
        ("covarSamp(salary, 2000)",),
        ("anyHeavy(salary)",),
        ("anyLast(salary)",),
        ("argMin(salary, 5000)",),
        ("argMax(salary, 5000)",),
        ("avgWeighted(salary, 1)",),
        ("corr(salary, 0.5)",),
        ("topK(salary)",),
        ("topKWeighted(salary, 1)",),
        ("groupArray(salary)",),
        ("groupUniqArray(salary)",),
        ("groupArrayInsertAt(salary, 0)",),
        ("groupArrayMovingSum(salary)",),
        ("groupArrayMovingAvg(salary)",),
        ("groupArraySample(3, 1234)(salary)",),
        ("groupBitAnd(toUInt8(salary))",),
        ("groupBitOr(toUInt8(salary))",),
        ("groupBitXor(toUInt8(salary))",),
        ("groupBitmap(toUInt8(salary))",),
        # #("groupBitmapAnd",),
        # #("groupBitmapOr",),
        # #("groupBitmapXor",),
        ("sumWithOverflow(salary)",),
        ("deltaSum(salary)",),
        ("sumMap([5000], [salary])",),
        ("minMap([5000], [salary])",),
        ("maxMap([5000], [salary])",),
        # #("initializeAggregation",),
        ("skewPop(salary)",),
        ("skewSamp(salary)",),
        ("kurtPop(salary)",),
        ("kurtSamp(salary)",),
        ("uniq(salary)",),
        ("uniqExact(salary)",),
        ("uniqCombined(salary)",),
        ("uniqCombined64(salary)",),
        ("uniqHLL12(salary)",),
        ("quantile(salary)",),
        ("quantiles(0.5)(salary)",),
        ("quantileExact(salary)",),
        ("quantileExactWeighted(salary, 1)",),
        ("quantileTiming(salary)",),
        ("quantileTimingWeighted(salary, 1)",),
        ("quantileDeterministic(salary, 1234)",),
        ("quantileTDigest(salary)",),
        ("quantileTDigestWeighted(salary, 1)",),
        ("simpleLinearRegression(salary, empno)",),
        ("stochasticLinearRegression(salary, 1)",),
        ("stochasticLogisticRegression(salary, 1)",),
        # ("categoricalInformationValue(salary, 0)",),
        ("studentTTest(salary, 1)",),
        ("welchTTest(salary, 1)",),
        ("mannWhitneyUTest(salary, 1)",),
        ("median(salary)",),
        ("rankCorr(salary, 0.5)",),
    ],
)
def aggregate_funcs_over_rows_frame(self, func):
    """Checking aggregate funcs over rows frame."""
    snapshot_name = (
        "/window functions"
        + current()
        .name.replace(f"{sep}non distributed{sep}", ":")
        .replace(f"{sep}distributed{sep}", ":")
        .split("/window functions", 1)[-1]
    )

    if (
        func.startswith("studentTTest") or func.startswith("welchTTest")
    ) and check_clickhouse_version(">=22")(self):
        snapshot_name += "/version>=22"

    if (
        (func.startswith("simpleLinearRegression"))
        and check_clickhouse_version(">=24.3")(self)
        and check_current_cpu("aarch64")(self)
    ):
        snapshot_name += "/version>=24.3"

    execute_query(
        f"""
        SELECT {func} OVER (ORDER BY salary, empno ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS func
          FROM empsalary ORDER BY func DESC
        """,
        snapshot_name=snapshot_name,
    )


@TestScenario
def avg_with_nulls(self):
    """Check `avg` aggregate function using a window that contains NULLs."""
    expected = convert_output(
        """
         i |        avg
        ---+--------------------
         1 | 1.5
         2 | 2
         3 | \\N
         4 | \\N
    """
    )

    execute_query(
        """
        SELECT i, avg(v) OVER (ORDER BY i ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS avg
          FROM values('i Int32, v Nullable(Int32)', (1,1),(2,2),(3,NULL),(4,NULL))
        """,
        expected=expected,
    )


@TestScenario
def var_pop(self):
    """Check `var_pop` aggregate function ove a window."""
    expected = convert_output(
        """
            var_pop
    -----------------------
        21704
        13868.75
        11266.666666666666
        4225
        0
    """
    )

    execute_query(
        """
        SELECT VAR_POP(n) OVER (ORDER BY i ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS var_pop
          FROM values('i Int8, n Int32', (1,600),(2,470),(3,170),(4,430),(5,300)) ORDER BY var_pop DESC
        """,
        expected=expected,
    )


@TestScenario
def var_samp(self):
    """Check `var_samp` aggregate function ove a window."""
    expected = convert_output(
        """
          var_samp
    -----------------------
        27130
        18491.666666666668
        16900
        8450
        nan
    """
    )

    execute_query(
        """
        SELECT VAR_SAMP(n) OVER (ORDER BY i ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS var_samp
          FROM VALUES('i Int8, n Int16',(1,600),(2,470),(3,170),(4,430),(5,300)) ORDER BY var_samp DESC
        """,
        expected=expected,
    )


@TestScenario
def stddevpop(self):
    """Check `stddevPop` aggregate function ove a window."""
    expected = convert_output(
        """
             stddev_pop
    ---------------------
        147.32277488562318
        147.32277488562318
        117.76565713313877
        106.14455552060438
        65
        0
    """
    )

    execute_query(
        """
        SELECT stddevPop(n) OVER (ORDER BY i ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS stddev_pop
          FROM VALUES('i Int8, n Nullable(Int16)',(1,NULL),(2,600),(3,470),(4,170),(5,430),(6,300)) ORDER BY stddev_pop DESC
        """,
        expected=expected,
    )


@TestScenario
def stddevsamp(self):
    """Check `stddevSamp` aggregate function ove a window."""
    expected = convert_output(
        """
         stddev_samp
    ---------------------
        164.7118696390761
        164.7118696390761
        135.9840676942217
        130
        91.92388155425118
           nan
    """
    )

    execute_query(
        """
        SELECT stddevSamp(n) OVER (ORDER BY i ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS stddev_samp
          FROM VALUES('i Int8, n Nullable(Int16)',(1,NULL),(2,600),(3,470),(4,170),(5,430),(6,300)) ORDER BY stddev_samp DESC
        """,
        expected=expected,
    )


@TestScenario
def aggregate_function_recovers_from_nan(self):
    """Check that aggregate function can recover from `nan` value inside a window."""
    expected = convert_output(
        """
         a |  b  | sum
        ---+-----+-----
         1 |   1 |   1
         2 |   2 |   3
         3 | nan | nan
         4 |   3 | nan
         5 |   4 |   7
    """
    )

    execute_query(
        """
        SELECT a, b,
               SUM(b) OVER(ORDER BY a ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS sum
        FROM VALUES('a Int8, b Float64',(1,1),(2,2),(3,nan),(4,3),(5,4)) ORDER BY a
        """,
        expected=expected,
    )


@TestScenario
def bit_functions(self):
    """Check trying to use bitwise functions over a window."""
    expected = convert_output(
        """
     i | b | bool_and | bool_or
    ---+---+----------+---------
     1 | 1 | 1        | 1
     2 | 1 | 0        | 1
     3 | 0 | 0        | 0
     4 | 0 | 0        | 1
     5 | 1 | 1        | 1
    """
    )

    execute_query(
        """
        SELECT i, b, groupBitAnd(b) OVER w AS bool_and, groupBitOr(b) OVER w AS bool_or
          FROM VALUES('i Int8, b UInt8', (1,1), (2,1), (3,0), (4,0), (5,1))
          WINDOW w AS (ORDER BY i ROWS BETWEEN CURRENT ROW AND 1 FOLLOWING)
          ORDER BY i
        """,
        expected=expected,
    )


@TestScenario
def sum(self):
    """Check calculation of sum over a window."""
    expected = convert_output(
        """
     sum_1 | ten | four
    -------+-----+------
         0 |   0 |    0
         0 |   0 |    0
         2 |   0 |    2
         3 |   1 |    3
         4 |   1 |    1
         5 |   1 |    1
         3 |   3 |    3
         0 |   4 |    0
         1 |   7 |    1
         1 |   9 |    1
    """
    )

    execute_query(
        "SELECT sum(four) OVER (PARTITION BY ten ORDER BY unique2) AS sum_1, ten, four FROM tenk1 WHERE unique2 < 10 ORDER BY ten, unique2",
        expected=expected,
    )


@TestScenario
def nested_aggregates(self):
    """Check using nested aggregates over a window."""
    expected = convert_output(
        """
     ten | two | gsum  |  wsum
    -----+-----+-------+--------
       0 |   0 | 45000 |  45000
       2 |   0 | 47000 |  92000
       4 |   0 | 49000 | 141000
       6 |   0 | 51000 | 192000
       8 |   0 | 53000 | 245000
       1 |   1 | 46000 |  46000
       3 |   1 | 48000 |  94000
       5 |   1 | 50000 | 144000
       7 |   1 | 52000 | 196000
       9 |   1 | 54000 | 250000
    """
    )

    execute_query(
        "SELECT ten, two, sum(hundred) AS gsum, sum(sum(hundred)) OVER (PARTITION BY two ORDER BY ten) AS wsum FROM tenk1 GROUP BY ten, two ORDER BY two, ten",
        expected=expected,
    )


@TestScenario
def aggregate_and_window_function_in_the_same_window(self):
    """Check using aggregate and window function in the same window."""
    expected = convert_output(
        """
      sum  | rank
    -------+------
      3900 |    1
      5000 |    1
      6000 |    1
      7400 |    2
     14600 |    2
     14600 |    2
     16400 |    2
     16400 |    2
     20900 |    4
     25100 |    5
    """
    )

    execute_query(
        "SELECT sum(salary) OVER w AS sum, rank() OVER w AS rank FROM empsalary WINDOW w AS (PARTITION BY depname ORDER BY salary DESC) ORDER BY sum, rank",
        expected=expected,
    )


@TestScenario
def ungrouped_aggregate_over_empty_row_set(self):
    """Check using window function with ungrouped aggregate over an empty row set."""
    expected = convert_output(
        """
    sum
    -----
       0
    """
    )

    execute_query(
        "SELECT SUM(COUNT(number)) OVER () AS sum FROM numbers(10) WHERE number=42",
        expected=expected,
    )


@TestScenario
def avgWeighted(self):
    """Check special case of using `avgWeighted` function with Decimal and mixed types
    when used over a window function.
    """
    with Example("decimal weight"):
        expected = convert_output(
            """
          avg
        -------
           nan
             1
             2
             3
             4
             5
             6
             7
             8
             9
        """
        )

        execute_query(
            "SELECT avgWeighted(a, toDecimal64(c, 9)) OVER (PARTITION BY c) AS avg FROM (SELECT number AS a, number AS c FROM numbers(10))",
            expected=expected,
        )

    with Example("decimal value and weight"):
        expected = convert_output(
            """
          avg
        -------
           nan
             1
             2
             3
             4
             5
             6
             7
             8
             9
        """
        )

        execute_query(
            "SELECT avgWeighted(toDecimal64(a, 4), toDecimal64(c, 9)) OVER (PARTITION BY c) AS avg FROM (SELECT number AS a, number AS c FROM numbers(10))",
            expected=expected,
        )

    with Example("float value and decimal weight from table"):
        expected = convert_output(
            """
          avg
        -------
          5000
          3900
          4800
          4800
          3500
          4200
          6000
          4500
          5200
          5200
        """
        )

        if check_clickhouse_version("<23.10")(self):
            execute_query(
                "SELECT avgWeighted(toFloat64(salary) + 0.02, toDecimal64(empno, 9)) OVER (PARTITION BY empno) AS avg FROM (SELECT * FROM empsalary ORDER BY empno)",
                expected=expected,
            )


@TestFeature
@Name("aggregate funcs")
@Requirements(RQ_SRS_019_ClickHouse_WindowFunctions_AggregateFunctions("1.0"))
def feature(self):
    """Check using aggregate functions over windows."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
