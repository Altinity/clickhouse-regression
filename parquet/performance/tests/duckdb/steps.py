from testflows.core import *
from helpers.common import getuid
import time


@TestOutline
def outline(self, clickhouse_query: str, duckdb_query: str, step_name: str):
    clickhouse_node = self.context.clickhouse_node
    duckdb_node = self.context.duckdb_node
    duckdb_database = "db_" + getuid()

    start_time = time.time()
    clickhouse_node.query(clickhouse_query)
    clickhouse_run_time = time.time() - start_time
    metric(name="ClickHouse: " + step_name, value=clickhouse_run_time, units="s")

    start_time = time.time()
    duckdb_node.command(f"duckdb {duckdb_database} '{duckdb_query}'", exitcode=0)
    duckdb_run_time = time.time() - start_time
    metric(name="DuckDB: " + step_name, value=duckdb_run_time, units="s")


@TestStep
def query_0(self, filename: str):
    """Calculating the average count of rows per group, where each group is defined by a combination of Year and
    Month values from the table."""

    r = "SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM {filename} GROUP BY Year, Month);"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f'"/data1/{filename}"')

    outline(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        step_name="query_0",
    )


@TestStep
def query_1(self, filename: str):
    """Get the number of flights per day from the year 2000 to 2008."""

    query = (
        "SELECT DayOfWeek, count(*) AS c FROM {filename} WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER "
        "BY c DESC;"
    )

    clickhouse_query = query.format(filename=f"file({filename})")
    duckdb_query = query.format(filename=f'"/data1/{filename}"')

    outline(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        step_name="query_1",
    )


@TestStep
def query_2(self, filename: str):
    """Get the number of flights delayed by more than 10 minutes, grouped by the day of the week, for 2000-2008."""

    clickhouse_query = (
        f"SELECT DayOfWeek, count(*) AS c FROM file('{filename}') "
        f"WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;"
    )
    duckdb_query = (
        f'SELECT DayOfWeek, COUNT(*) AS c FROM "/data1/{filename}" '
        f"WHERE Year >= 2000 AND Year <= 2008 GROUP BY DayOfWeek ORDER BY c DESC;"
    )

    outline(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        step_name="query_2",
    )


@TestStep
def query_3(self, filename: str):
    """Get the number of delays by the airport for 2000-2008."""

    clickhouse_query = (
        f"SELECT Origin, count(*) AS c FROM file('{filename}') "
        f"WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;"
    )
    duckdb_query = (
        f'SELECT Origin, COUNT(*) AS c FROM "/data1/{filename}" '
        f"WHERE DepDelay > 10 AND Year >= 2000 AND Year <= 2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;"
    )

    outline(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        step_name="query_2",
    )


@TestStep
def query_4(self, filename: str):
    """Get the number of delays by carrier for 2007."""

    clickhouse_query = (
        f"SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('{filename}') "
        f"WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;"
    )
    duckdb_query = (
        f'SELECT IATA_CODE_Reporting_Airline AS Carrier, COUNT(*) AS count FROM "/data1/{filename}" '
        f"WHERE DepDelay > 10 AND Year = 2007 GROUP BY Carrier ORDER BY count DESC;"
    )

    outline(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        step_name="query_4",
    )


@TestStep
def query_5(self, filename: str):
    """Get the percentage of delays by carrier for 2007."""

    clickhouse_query = (
        f"SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('{filename}') WHERE "
        f"Year=2007 GROUP BY Carrier ORDER BY c3 DESC"
    )
    duckdb_query = (
        f"SELECT IATA_CODE_Reporting_Airline AS Carrier, AVG(CAST(DepDelay > 10 AS DECIMAL) * 100) AS c3 "
        f'FROM "/data1/{filename}" WHERE Year = 2007 GROUP BY Carrier ORDER BY c3 DESC;'
    )

    outline(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        step_name="query_5",
    )


@TestStep
def query_6(self, filename: str):
    """Get the percentage of delays by carrier for a broader range of years, 2000-2008."""

    clickhouse_query = (
        f"SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('{filename}') "
        f"WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;"
    )

    duckdb_query = (
        f"SELECT IATA_CODE_Reporting_Airline AS Carrier, AVG(CAST(DepDelay > 10 AS DECIMAL) * 100) AS c3 "
        f'FROM "/data1/{filename}" WHERE Year >= 2000 AND Year <= 2008 GROUP BY Carrier ORDER BY c3 DESC;'
    )

    outline(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        step_name="query_6",
    )


@TestStep
def query_7(self, filename: str):
    """Get the percentage of flights delayed for more than 10 minutes, by year."""

    clickhouse_query = f"SELECT Year, avg(DepDelay>10)*100 FROM file('{filename}') GROUP BY Year ORDER BY Year;"
    duckdb_query = f'SELECT Year, AVG(CAST(DepDelay > 10 AS DECIMAL) * 100) FROM "/data1/{filename}" GROUP BY Year ORDER BY Year;'

    outline(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        step_name="query_7",
    )


@TestStep
def query_8(self, filename: str):
    """Get the most popular destinations by the number of directly connected cities for various year ranges."""

    clickhouse_query = (
        f"SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('{filename}') "
        f"WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC LIMIT 10;"
    )
    duckdb_query = (
        f'SELECT DestCityName, COUNT(DISTINCT OriginCityName) AS u FROM "/data1/{filename}" WHERE Year >= '
        f"2000 AND Year <= 2010 GROUP BY DestCityName ORDER BY u DESC LIMIT 10;"
    )

    outline(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        step_name="query_8",
    )


@TestStep
def query_9(self, filename: str):
    """Group the data by the Year column, and calculate the count of rows in each year."""
    clickhouse_query = (
        f"SELECT Year, count(*) AS c1 FROM file('{filename}') GROUP BY Year;"
    )
    duckdb_query = (
        f'SELECT Year, COUNT(*) AS c1 FROM "/data1/{filename}" GROUP BY Year;'
    )

    outline(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        step_name="query_9",
    )


@TestScenario
def queries(self, filename):
    for step in loads(current_module(), Step):
        step(filename=filename)
