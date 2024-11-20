import time

from testflows.core import *
from testflows.asserts import snapshot, values, error
from helpers.common import getuid


def hits_queries():
    queries = [
        "SELECT COUNT(*) FROM hits;",
        "SELECT COUNT(*) FROM hits WHERE AdvEngineID <> 0;",
        "SELECT SUM(AdvEngineID), COUNT(*), AVG(ResolutionWidth) FROM hits;",
        "SELECT AVG(UserID) FROM hits;",
        "SELECT COUNT(DISTINCT UserID) FROM hits;",
        "SELECT COUNT(DISTINCT SearchPhrase) FROM hits;",
        "SELECT MIN(EventDate), MAX(EventDate) FROM hits;",
        "SELECT AdvEngineID, COUNT(*) FROM hits WHERE AdvEngineID <> 0 GROUP BY AdvEngineID ORDER BY COUNT(*) DESC;",
        "SELECT RegionID, COUNT(DISTINCT UserID) AS u FROM hits GROUP BY RegionID ORDER BY u DESC LIMIT 10;",
        "SELECT RegionID, SUM(AdvEngineID), COUNT(*) AS c, AVG(ResolutionWidth), COUNT(DISTINCT UserID) FROM hits GROUP BY RegionID ORDER BY c DESC LIMIT 10;",
        "SELECT MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM hits WHERE MobilePhoneModel <> '' GROUP BY MobilePhoneModel ORDER BY u DESC LIMIT 10;",
        "SELECT MobilePhone, MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM hits WHERE MobilePhoneModel <> '' GROUP BY MobilePhone, MobilePhoneModel ORDER BY u DESC LIMIT 10;",
        "SELECT SearchPhrase, COUNT(*) AS c FROM hits WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10;",
        "SELECT SearchPhrase, COUNT(DISTINCT UserID) AS u FROM hits WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY u DESC LIMIT 10;",
        "SELECT SearchEngineID, SearchPhrase, COUNT(*) AS c FROM hits WHERE SearchPhrase <> '' GROUP BY SearchEngineID, SearchPhrase ORDER BY c DESC LIMIT 10;",
        "SELECT UserID, COUNT(*) FROM hits GROUP BY UserID ORDER BY COUNT(*) DESC LIMIT 10;",
        "SELECT UserID, SearchPhrase, COUNT(*) FROM hits GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10;",
        "SELECT UserID, SearchPhrase, COUNT(*) FROM hits GROUP BY UserID, SearchPhrase LIMIT 10;",
        "SELECT UserID, extract(minute FROM EventTime) AS m, SearchPhrase, COUNT(*) FROM hits GROUP BY UserID, m, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10;",
        "SELECT UserID FROM hits WHERE UserID = 435090932899640449;",
        "SELECT COUNT(*) FROM hits WHERE URL LIKE '%google%';",
        "SELECT SearchPhrase, MIN(URL), COUNT(*) AS c FROM hits WHERE URL LIKE '%google%' AND SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10;",
        "SELECT SearchPhrase, MIN(URL), MIN(Title), COUNT(*) AS c, COUNT(DISTINCT UserID) FROM hits WHERE Title LIKE '%Google%' AND URL NOT LIKE '%.google.%' AND SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10;",
        "SELECT * FROM hits WHERE URL LIKE '%google%' ORDER BY EventTime LIMIT 10;",
        "SELECT SearchPhrase FROM hits WHERE SearchPhrase <> '' ORDER BY EventTime LIMIT 10;",
        "SELECT SearchPhrase FROM hits WHERE SearchPhrase <> '' ORDER BY SearchPhrase LIMIT 10;",
        "SELECT SearchPhrase FROM hits WHERE SearchPhrase <> '' ORDER BY EventTime, SearchPhrase LIMIT 10;",
        "SELECT CounterID, AVG(length(URL)) AS l, COUNT(*) AS c FROM hits WHERE URL <> '' GROUP BY CounterID HAVING COUNT(*) > 100000 ORDER BY l DESC LIMIT 25;",
        "SELECT REGEXP_REPLACE(Referer, '^https?://(?:www\\.)?([^/]+)/.*$', '\\1') AS k, AVG(length(Referer)) AS l, COUNT(*) AS c, MIN(Referer) FROM hits WHERE Referer <> '' GROUP BY k HAVING COUNT(*) > 100000 ORDER BY l DESC LIMIT 25;",
        "SELECT SUM(ResolutionWidth), SUM(ResolutionWidth + 1), SUM(ResolutionWidth + 2), SUM(ResolutionWidth + 3), SUM(ResolutionWidth + 4), SUM(ResolutionWidth + 5), SUM(ResolutionWidth + 6), SUM(ResolutionWidth + 7), SUM(ResolutionWidth + 8), SUM(ResolutionWidth + 9), SUM(ResolutionWidth + 10), SUM(ResolutionWidth + 11), SUM(ResolutionWidth + 12), SUM(ResolutionWidth + 13), SUM(ResolutionWidth + 14), SUM(ResolutionWidth + 15), SUM(ResolutionWidth + 16), SUM(ResolutionWidth + 17), SUM(ResolutionWidth + 18), SUM(ResolutionWidth + 19), SUM(ResolutionWidth + 20), SUM(ResolutionWidth + 21), SUM(ResolutionWidth + 22), SUM(ResolutionWidth + 23), SUM(ResolutionWidth + 24), SUM(ResolutionWidth + 25), SUM(ResolutionWidth + 26), SUM(ResolutionWidth + 27), SUM(ResolutionWidth + 28), SUM(ResolutionWidth + 29), SUM(ResolutionWidth + 30), SUM(ResolutionWidth + 31), SUM(ResolutionWidth + 32), SUM(ResolutionWidth + 33), SUM(ResolutionWidth + 34), SUM(ResolutionWidth + 35), SUM(ResolutionWidth + 36), SUM(ResolutionWidth + 37), SUM(ResolutionWidth + 38), SUM(ResolutionWidth + 39), SUM(ResolutionWidth + 40), SUM(ResolutionWidth + 41), SUM(ResolutionWidth + 42), SUM(ResolutionWidth + 43), SUM(ResolutionWidth + 44), SUM(ResolutionWidth + 45), SUM(ResolutionWidth + 46), SUM(ResolutionWidth + 47), SUM(ResolutionWidth + 48), SUM(ResolutionWidth + 49), SUM(ResolutionWidth + 50), SUM(ResolutionWidth + 51), SUM(ResolutionWidth + 52), SUM(ResolutionWidth + 53), SUM(ResolutionWidth + 54), SUM(ResolutionWidth + 55), SUM(ResolutionWidth + 56), SUM(ResolutionWidth + 57), SUM(ResolutionWidth + 58), SUM(ResolutionWidth + 59), SUM(ResolutionWidth + 60), SUM(ResolutionWidth + 61), SUM(ResolutionWidth + 62), SUM(ResolutionWidth + 63), SUM(ResolutionWidth + 64), SUM(ResolutionWidth + 65), SUM(ResolutionWidth + 66), SUM(ResolutionWidth + 67), SUM(ResolutionWidth + 68), SUM(ResolutionWidth + 69), SUM(ResolutionWidth + 70), SUM(ResolutionWidth + 71), SUM(ResolutionWidth + 72), SUM(ResolutionWidth + 73), SUM(ResolutionWidth + 74), SUM(ResolutionWidth + 75), SUM(ResolutionWidth + 76), SUM(ResolutionWidth + 77), SUM(ResolutionWidth + 78), SUM(ResolutionWidth + 79), SUM(ResolutionWidth + 80), SUM(ResolutionWidth + 81), SUM(ResolutionWidth + 82), SUM(ResolutionWidth + 83), SUM(ResolutionWidth + 84), SUM(ResolutionWidth + 85), SUM(ResolutionWidth + 86), SUM(ResolutionWidth + 87), SUM(ResolutionWidth + 88), SUM(ResolutionWidth + 89) FROM hits;",
        "SELECT SearchEngineID, ClientIP, COUNT(*) AS c, SUM(IsRefresh), AVG(ResolutionWidth) FROM hits WHERE SearchPhrase <> '' GROUP BY SearchEngineID, ClientIP ORDER BY c DESC LIMIT 10;",
        "SELECT WatchID, ClientIP, COUNT(*) AS c, SUM(IsRefresh), AVG(ResolutionWidth) FROM hits WHERE SearchPhrase <> '' GROUP BY WatchID, ClientIP ORDER BY c DESC LIMIT 10;",
        "SELECT WatchID, ClientIP, COUNT(*) AS c, SUM(IsRefresh), AVG(ResolutionWidth) FROM hits GROUP BY WatchID, ClientIP ORDER BY c DESC LIMIT 10;",
        "SELECT URL, COUNT(*) AS c FROM hits GROUP BY URL ORDER BY c DESC LIMIT 10;",
        "SELECT 1, URL, COUNT(*) AS c FROM hits GROUP BY 1, URL ORDER BY c DESC LIMIT 10;",
        "SELECT ClientIP, ClientIP - 1, ClientIP - 2, ClientIP - 3, COUNT(*) AS c FROM hits GROUP BY ClientIP, ClientIP - 1, ClientIP - 2, ClientIP - 3 ORDER BY c DESC LIMIT 10;",
        "SELECT URL, COUNT(*) AS PageViews FROM hits WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND DontCountHits = 0 AND IsRefresh = 0 AND URL <> '' GROUP BY URL ORDER BY PageViews DESC LIMIT 10;",
        "SELECT Title, COUNT(*) AS PageViews FROM hits WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND DontCountHits = 0 AND IsRefresh = 0 AND Title <> '' GROUP BY Title ORDER BY PageViews DESC LIMIT 10;",
        "SELECT URL, COUNT(*) AS PageViews FROM hits WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND IsRefresh = 0 AND IsLink <> 0 AND IsDownload = 0 GROUP BY URL ORDER BY PageViews DESC LIMIT 10 OFFSET 1000;",
        "SELECT TraficSourceID, SearchEngineID, AdvEngineID, CASE WHEN (SearchEngineID = 0 AND AdvEngineID = 0) THEN Referer ELSE '' END AS Src, URL AS Dst, COUNT(*) AS PageViews FROM hits WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND IsRefresh = 0 GROUP BY TraficSourceID, SearchEngineID, AdvEngineID, Src, Dst ORDER BY PageViews DESC LIMIT 10 OFFSET 1000;",
        "SELECT URLHash, EventDate, COUNT(*) AS PageViews FROM hits WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND IsRefresh = 0 AND TraficSourceID IN (-1, 6) AND RefererHash = 3594120000172545465 GROUP BY URLHash, EventDate ORDER BY PageViews DESC LIMIT 10 OFFSET 100;",
        "SELECT WindowClientWidth, WindowClientHeight, COUNT(*) AS PageViews FROM hits WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND IsRefresh = 0 AND DontCountHits = 0 AND URLHash = 2868770270353813622 GROUP BY WindowClientWidth, WindowClientHeight ORDER BY PageViews DESC LIMIT 10 OFFSET 10000;",
        "SELECT DATE_TRUNC('minute', EventTime) AS M, COUNT(*) AS PageViews FROM hits WHERE CounterID = 62 AND EventDate >= '2013-07-14' AND EventDate <= '2013-07-15' AND IsRefresh = 0 AND DontCountHits = 0 GROUP BY DATE_TRUNC('minute', EventTime) ORDER BY DATE_TRUNC('minute', EventTime) LIMIT 10 OFFSET 1000;",
    ]

    return queries


@TestOutline
def run_query(
    self,
    clickhouse_query: str,
    name: str,
):
    """Run the query on clickhouse and duckdb and collect the metrics of execution time for each.
    :param name: name of the query that is being run
    :param clickhouse_query: full query being run in ClickHouse
    :param duckdb_query: full query being run in DuckDB
    """

    clickhouse_node = self.context.clickhouse_node
    repeats = self.context.run_count

    with By("running the query on clickhouse", description=f"{clickhouse_query}"):
        clickhouse_times = []
        for _ in range(repeats):
            start_time = time.time()
            query = clickhouse_node.query(clickhouse_query)
            clickhouse_run_time = time.time() - start_time
            clickhouse_times.append(clickhouse_run_time)
        metric(name="clickhouse-" + name, value=min(clickhouse_times), units="s")

        with values() as that:
            assert that(
                snapshot(
                    query.output.strip(),
                    name=name
                    + "clickhouse"
                    + f"from_year_{self.context.from_year}"
                    + f"_to_year_{self.context.to_year}",
                )
            ), error()

    csv_result = (
        name,
        self.context.clickhouse_version,
        min(clickhouse_times),
        clickhouse_query,
    )

    for i in range(repeats):
        csv_result += (clickhouse_times[i],)

    self.context.query_results.append(csv_result)


@TestScenario
def get_row_count(self, filename: str):
    """Calculating and uploading the row count of the parquet file into the CSV."""
    clickhouse_node = self.context.clickhouse_node

    with Given("I select the number of rows from the parquet file"):
        rows = clickhouse_node.query(f"SELECT count() FROM file({filename})")
    self.context.row_count.append(rows.output.strip())


@TestStep
def query_0(self, filename: str, database: str):
    """Calculating the average count of rows per group, where each group is defined by a combination of Year and
    Month values from the table."""

    clickhouse_query = f"SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM file('{filename}') GROUP BY Year, Month ORDER BY Year ASC, Month ASC);"
    duckdb_query = f'SELECT avg(c1) FROM(SELECT Year, Month, count(*) AS c1 FROM "/data1/{filename}" GROUP BY Year, Month ORDER BY Year ASC, Month ASC);'

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_0",
        database=database,
    )


@TestStep
def query_1(self, filename: str, database: str):
    """Get the number of flights per day from the year 2000 to 2008."""

    clickhouse_query = (
        f"SELECT DayOfWeek, count(*) AS c FROM file('{filename}') WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER "
        "BY c DESC;"
    )

    duckdb_query = f'SELECT DayOfWeek, count(*) AS c FROM "/data1/{filename}" WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;'

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_1",
        database=database,
    )


@TestStep
def query_2(self, filename: str, database: str):
    """Get the number of flights delayed by more than 10 minutes, grouped by the day of the week, for 2000-2008."""

    clickhouse_query = (
        f"SELECT DayOfWeek, count(*) AS c FROM file('{filename}') "
        f"WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC;"
    )
    duckdb_query = (
        f'SELECT DayOfWeek, COUNT(*) AS c FROM "/data1/{filename}" '
        f"WHERE Year >= 2000 AND Year <= 2008 GROUP BY DayOfWeek ORDER BY c DESC;"
    )

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_2",
        database=database,
    )


@TestStep
def query_3(self, filename: str, database: str):
    """Get the number of delays by the airport for 2000-2008."""

    clickhouse_query = (
        f"SELECT Origin, count(*) AS c FROM file('{filename}') "
        f"WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;"
    )
    duckdb_query = (
        f'SELECT Origin, COUNT(*) AS c FROM "/data1/{filename}" '
        f"WHERE DepDelay > 10 AND Year >= 2000 AND Year <= 2008 GROUP BY Origin ORDER BY c DESC LIMIT 10;"
    )

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_3",
        database=database,
    )


@TestStep
def query_4(self, filename: str, database: str):
    """Get the number of delays by carrier for 2007."""

    clickhouse_query = (
        f"SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM file('{filename}') "
        f"WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC;"
    )
    duckdb_query = (
        f'SELECT IATA_CODE_Reporting_Airline AS Carrier, COUNT(*) AS count FROM "/data1/{filename}" '
        f"WHERE DepDelay > 10 AND Year = 2007 GROUP BY Carrier ORDER BY count DESC;"
    )

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_4",
        database=database,
    )


@TestStep
def query_5(self, filename: str, database: str):
    """Get the percentage of delays by carrier for 2007."""

    clickhouse_query = (
        f"SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('{filename}') WHERE "
        f"Year=2007 GROUP BY Carrier ORDER BY c3 DESC"
    )
    duckdb_query = (
        f"SELECT IATA_CODE_Reporting_Airline AS Carrier, AVG(CAST(DepDelay > 10 AS DECIMAL) * 100) AS c3 "
        f'FROM "/data1/{filename}" WHERE Year = 2007 GROUP BY Carrier ORDER BY c3 DESC;'
    )

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_5",
        database=database,
    )


@TestStep
def query_6(self, filename: str, database: str):
    """Get the percentage of delays by carrier for a broader range of years, 2000-2008."""

    clickhouse_query = (
        f"SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM file('{filename}') "
        f"WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;"
    )

    duckdb_query = (
        f"SELECT IATA_CODE_Reporting_Airline AS Carrier, AVG(CAST(DepDelay > 10 AS DECIMAL) * 100) AS c3 "
        f'FROM "/data1/{filename}" WHERE Year >= 2000 AND Year <= 2008 GROUP BY Carrier ORDER BY c3 DESC;'
    )

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_6",
        database=database,
    )


@TestStep
def query_7(self, filename: str, database: str):
    """Get the percentage of flights delayed for more than 10 minutes, by year."""

    clickhouse_query = f"SELECT Year, avg(DepDelay>10)*100 FROM file('{filename}') GROUP BY Year ORDER BY Year;"
    duckdb_query = f'SELECT Year, AVG(CAST(DepDelay > 10 AS DECIMAL) * 100) FROM "/data1/{filename}" GROUP BY Year ORDER BY Year;'

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_7",
        database=database,
    )


@TestStep
def query_8(self, filename: str, database: str):
    """Get the most popular destinations by the number of directly connected cities for various year ranges."""

    clickhouse_query = (
        f"SELECT DestCityName, uniqExact(OriginCityName) AS u FROM file('{filename}') "
        f"WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC, DestCityName ASC LIMIT 10;"
    )
    duckdb_query = (
        f'SELECT DestCityName, COUNT(DISTINCT OriginCityName) AS u FROM "/data1/{filename}" WHERE Year >= '
        f"2000 AND Year <= 2010 GROUP BY DestCityName ORDER BY u DESC, DestCityName ASC LIMIT 10;;"
    )

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_8",
        database=database,
    )


@TestStep
def query_9(self, filename: str, database: str):
    """Group the data by the Year column, and calculate the count of rows in each year."""
    clickhouse_query = f"SELECT Year, count(*) AS c1 FROM file('{filename}') GROUP BY Year ORDER BY Year ASC;"
    duckdb_query = f'SELECT Year, COUNT(*) AS c1 FROM "/data1/{filename}" GROUP BY Year ORDER BY Year ASC;'

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_9",
        database=database,
    )


@TestSuite
def clickhouse(self, filename):
    for i, query in enumerate(queries()):
        run_query(
            clickhouse_query=query,
            name=f"query_{i}",
        )






@TestScenario
def queries(self, filename):
    """Save number of rows of th parquet file into a CSV file and run the set of queries on ClickHouse and DuckDB."""
    Feature(run=get_row_count(filename=filename))
    Feature(test=clickhouse)(filename=filename)
