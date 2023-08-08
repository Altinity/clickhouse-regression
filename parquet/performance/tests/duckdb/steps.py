from testflows.core import *
from helpers.common import getuid


@TestOutline
def outline(self, query: str, database: str, query_name: str):
    clickhouse_node = self.context.clickhouse_node
    duckdb_node = self.context.duckdb_node
    duckdb_database = "db_" + getuid()


    if database == "clickhouse":
        clickhouse_node.query(query, use_file=True, file_output="tests")
    elif database == "duckdb":
        duckdb_node.command(f"duckdb {duckdb_database} '{query}'", exitcode=0)
    else:
        raise ValueError(f"Unexpected database: {database}")


@TestStep
def query_all(self, filename: str, database: str = "clickhouse"):
    query = f"SELECT * FROM {filename}"

    outline(query=query, database=database, query_name="query_all")


@TestStep
def query_0(self, filename: str, database: str = "clickhouse"):
    """Calculating the average count of rows per group, where each group is defined by a combination of Year and
    Month values from the ontime table."""

    query = f"SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM {filename} GROUP BY Year, Month);"

    outline(query=query, database=database, query_name="query_0")


@TestStep
def query_1(self, filename: str, database: str = "clickhouse"):
    """Get the number of flights per day from the year 2000 to 2008."""

    query = f"SELECT DayOfWeek, count(*) AS c FROM {filename} WHERE Year>=1950 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;"
    outline(query=query, database=database, query_name="query_1")


@TestStep
def query_2(self, filename: str, database: str = "clickhouse"):
    """Get the number of flights delayed by more than 10 minutes, grouped by the day of the week, for 2000-2008."""

    query = f"""
    SELECT DayOfWeek, count(*) AS c
    FROM "{filename}"
    WHERE Year>=2000 AND Year<=2008
    GROUP BY DayOfWeek
    ORDER BY c DESC;
"""
    outline(query=query, database=database, query_name="query_2")


@TestStep
def query_3(self, filename: str, database: str = "clickhouse"):
    """Get the number of delays by the airport for 2000-2008."""

    query = f"""
    SELECT Origin, count(*) AS c
    FROM "{filename}"
    WHERE DepDelay>10 AND Year>=2000 AND Year<=2008
    GROUP BY Origin
    ORDER BY c DESC
    LIMIT 10;
"""
    outline(query=query, database=database, query_name="query_3")


@TestStep
def query_4(self, filename: str, database: str = "clickhouse"):
    """Get the number of delays by carrier for 2007."""

    query = f"""SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM "{filename}" WHERE DepDelay>10 AND 
    Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;"""
    outline(query=query, database=database, query_name="query_4")


@TestStep
def query_5(self, filename: str, database: str = "clickhouse"):
    """Get the percentage of delays by carrier for 2007."""

    query = (
        f'SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM "{filename}" WHERE '
        f"Year=2007 GROUP BY Carrier ORDER BY c3 DESC"
    )
    outline(query=query, database=database, query_name="query_5")


@TestStep
def query_6(self, filename: str, database: str = "clickhouse"):
    """Get the previous request for a broader range of years, 2000-2008."""

    query = f"""
    SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3
    FROM "{filename}"
    WHERE Year>=2000 AND Year<=2008
    GROUP BY Carrier
    ORDER BY c3 DESC;
"""
    outline(query=query, database=database, query_name="query_6")


@TestStep
def query_7(self, filename: str, database: str = "clickhouse"):
    """Get the percentage of flights delayed for more than 10 minutes, by year."""

    query = f"""
    SELECT Year, avg(DepDelay>10)*100
    FROM "{filename}"
    GROUP BY Year
    ORDER BY Year;
"""
    outline(query=query, database=database, query_name="query_7")


@TestStep
def query_8(self, filename: str, database: str = "clickhouse"):
    """Get the most popular destinations by the number of directly connected cities for various year ranges."""

    query = f"""
    SELECT DestCityName, uniqExact(OriginCityName) AS u
    FROM "{filename}"
    WHERE Year >= 2000 and Year <= 2010
    GROUP BY DestCityName
    ORDER BY u DESC LIMIT 10;
"""
    outline(query=query, database=database, query_name="query_8")


@TestStep
def query_9(self, filename: str, database: str = "clickhouse"):
    query = f"""
    SELECT Year, count(*) AS c1
    FROM "{filename}"
    GROUP BY Year;
"""
    outline(query=query, database=database, query_name="query_9")


@TestStep
def query_10(self, filename: str, database: str = "clickhouse"):
    query = f"""
    SELECT
       min(Year), max(Year), IATA_CODE_Reporting_Airline AS Carrier, count(*) AS cnt,
       sum(ArrDelayMinutes>30) AS flights_delayed,
       round(sum(ArrDelayMinutes>30)/count(*),2) AS rate
    FROM "{filename}"
    WHERE
       DayOfWeek NOT IN (6,7) AND OriginState NOT IN ('AK', 'HI', 'PR', 'VI')
       AND DestState NOT IN ('AK', 'HI', 'PR', 'VI')
       AND FlightDate < '2010-01-01'
    GROUP by Carrier
    HAVING cnt>100000 and max(Year)>1990
    ORDER by rate DESC
    LIMIT 1000;
"""
    outline(query=query, database=database, query_name="query_10")
