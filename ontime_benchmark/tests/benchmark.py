from testflows.core import *

from s3.tests.common import *

import time
import textwrap
import datetime


@TestStep(Given)
def insert_ontime_data(self, year, table_name, node=None):
    """Insert data into ontime table from s3 disk with specified year"""

    if node is None:
        node = self.context.node

    node.query(
        f"INSERT INTO {table_name} SELECT * FROM s3('https://clickhouse-public-datasets.s3.amazonaws.com/ontime/csv_by_year/{year}.csv.gz', CSVWithNames) SETTINGS max_insert_threads = 40;"
    )


@TestOutline
def benchmark(self, table_name, table_settings, nodes=None, format=None):
    """Outline to run benchmark queries for the ontime dataset."""
    if nodes is None:
        nodes = [current().context.node]

    def run_benchmark(num):
        start_time = time.time()
        nodes[0].query(queries[num])
        end_time = time.time()
        return end_time - start_time

    with Given("These benchmarking queries"):
        queries = [
            f"SELECT avg(c1) FROM ( SELECT Year, Month, count(*) AS c1 FROM {table_name} GROUP BY Year, Month)",
            f"SELECT DayOfWeek, count(*) AS c FROM {table_name} WHERE Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC",
            f"SELECT DayOfWeek, count(*) AS c FROM {table_name} WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY DayOfWeek ORDER BY c DESC",
            f"SELECT Origin, count(*) AS c FROM {table_name} WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Origin ORDER BY c DESC LIMIT 10",
            f"SELECT IATA_CODE_Reporting_Airline AS Carrier, count(*) FROM {table_name} WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC",
            f"SET joined_subquery_requires_alias = 0; SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM {table_name} WHERE Year=2007 GROUP BY Carrier ORDER BY c3 DESC;",
            f"SET joined_subquery_requires_alias = 0; SELECT IATA_CODE_Reporting_Airline AS Carrier, avg(DepDelay>10)*100 AS c3 FROM {table_name} WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier ORDER BY c3 DESC;",
            f"SET joined_subquery_requires_alias = 0; SELECT Year, avg(DepDelay>10)*100 FROM {table_name} GROUP BY Year ORDER BY Year;",
            f"SELECT DestCityName, uniqExact(OriginCityName) AS u FROM {table_name} WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC LIMIT 10",
            f"SELECT Year, count(*) AS c1 FROM {table_name} GROUP BY Year;",
            f"SELECT min(Year), max(Year), IATA_CODE_Reporting_Airline AS Carrier, count(*) AS cnt, sum(ArrDelayMinutes>30) AS flights_delayed, round(sum(ArrDelayMinutes>30)/count(*),2) AS rate FROM {table_name} WHERE DayOfWeek NOT IN (6,7) AND OriginState NOT IN ('AK', 'HI', 'PR', 'VI') AND DestState NOT IN ('AK', 'HI', 'PR', 'VI') AND FlightDate < '2010-01-01' GROUP by Carrier HAVING cnt>100000 and max(Year)>1990 ORDER by rate DESC LIMIT 1000;",
            f"SELECT avg(cnt) FROM (SELECT Year, Month, count(*) AS cnt FROM {table_name} WHERE DepDel15=1 GROUP BY Year, Month);",
            f"SELECT avg(c1) FROM (SELECT Year, Month, count(*) AS c1 FROM {table_name} GROUP BY Year, Month);",
            f"SELECT DestCityName, uniqExact(OriginCityName) AS u FROM {table_name} GROUP BY DestCityName ORDER BY u DESC LIMIT 10;",
            f"SELECT OriginCityName, DestCityName, count() AS c FROM {table_name} GROUP BY OriginCityName, DestCityName ORDER BY c DESC LIMIT 10;",
            f"SELECT OriginCityName, count() AS c FROM {table_name} GROUP BY OriginCityName ORDER BY c DESC LIMIT 10;",
        ]

    try:
        with When("I create a table for the ontime dataset"):
            for i, node in enumerate(nodes):
                with By(f"on {node.name}"):
                    node.restart()
                    node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")
                    node.query(
                        textwrap.dedent(
                            f"""
                        CREATE TABLE {table_name}
                        (
                            `Year`                            UInt16,
                            `Quarter`                         UInt8,
                            `Month`                           UInt8,
                            `DayofMonth`                      UInt8,
                            `DayOfWeek`                       UInt8,
                            `FlightDate`                      Date,
                            `Reporting_Airline`               LowCardinality(String),
                            `DOT_ID_Reporting_Airline`        Int32,
                            `IATA_CODE_Reporting_Airline`     LowCardinality(String),
                            `Tail_Number`                     LowCardinality(String),
                            `Flight_Number_Reporting_Airline` LowCardinality(String),
                            `OriginAirportID`                 Int32,
                            `OriginAirportSeqID`              Int32,
                            `OriginCityMarketID`              Int32,
                            `Origin`                          FixedString(5),
                            `OriginCityName`                  LowCardinality(String),
                            `OriginState`                     FixedString(2),
                            `OriginStateFips`                 FixedString(2),
                            `OriginStateName`                 LowCardinality(String),
                            `OriginWac`                       Int32,
                            `DestAirportID`                   Int32,
                            `DestAirportSeqID`                Int32,
                            `DestCityMarketID`                Int32,
                            `Dest`                            FixedString(5),
                            `DestCityName`                    LowCardinality(String),
                            `DestState`                       FixedString(2),
                            `DestStateFips`                   FixedString(2),
                            `DestStateName`                   LowCardinality(String),
                            `DestWac`                         Int32,
                            `CRSDepTime`                      Int32,
                            `DepTime`                         Int32,
                            `DepDelay`                        Int32,
                            `DepDelayMinutes`                 Int32,
                            `DepDel15`                        Int32,
                            `DepartureDelayGroups`            LowCardinality(String),
                            `DepTimeBlk`                      LowCardinality(String),
                            `TaxiOut`                         Int32,
                            `WheelsOff`                       LowCardinality(String),
                            `WheelsOn`                        LowCardinality(String),
                            `TaxiIn`                          Int32,
                            `CRSArrTime`                      Int32,
                            `ArrTime`                         Int32,
                            `ArrDelay`                        Int32,
                            `ArrDelayMinutes`                 Int32,
                            `ArrDel15`                        Int32,
                            `ArrivalDelayGroups`              LowCardinality(String),
                            `ArrTimeBlk`                      LowCardinality(String),
                            `Cancelled`                       Int8,
                            `CancellationCode`                FixedString(1),
                            `Diverted`                        Int8,
                            `CRSElapsedTime`                  Int32,
                            `ActualElapsedTime`               Int32,
                            `AirTime`                         Int32,
                            `Flights`                         Int32,
                            `Distance`                        Int32,
                            `DistanceGroup`                   Int8,
                            `CarrierDelay`                    Int32,
                            `WeatherDelay`                    Int32,
                            `NASDelay`                        Int32,
                            `SecurityDelay`                   Int32,
                            `LateAircraftDelay`               Int32,
                            `FirstDepTime`                    Int16,
                            `TotalAddGTime`                   Int16,
                            `LongestAddGTime`                 Int16,
                            `DivAirportLandings`              Int8,
                            `DivReachedDest`                  Int8,
                            `DivActualElapsedTime`            Int16,
                            `DivArrDelay`                     Int16,
                            `DivDistance`                     Int16,
                            `Div1Airport`                     LowCardinality(String),
                            `Div1AirportID`                   Int32,
                            `Div1AirportSeqID`                Int32,
                            `Div1WheelsOn`                    Int16,
                            `Div1TotalGTime`                  Int16,
                            `Div1LongestGTime`                Int16,
                            `Div1WheelsOff`                   Int16,
                            `Div1TailNum`                     LowCardinality(String),
                            `Div2Airport`                     LowCardinality(String),
                            `Div2AirportID`                   Int32,
                            `Div2AirportSeqID`                Int32,
                            `Div2WheelsOn`                    Int16,
                            `Div2TotalGTime`                  Int16,
                            `Div2LongestGTime`                Int16,
                            `Div2WheelsOff`                   Int16,
                            `Div2TailNum`                     LowCardinality(String),
                            `Div3Airport`                     LowCardinality(String),
                            `Div3AirportID`                   Int32,
                            `Div3AirportSeqID`                Int32,
                            `Div3WheelsOn`                    Int16,
                            `Div3TotalGTime`                  Int16,
                            `Div3LongestGTime`                Int16,
                            `Div3WheelsOff`                   Int16,
                            `Div3TailNum`                     LowCardinality(String),
                            `Div4Airport`                     LowCardinality(String),
                            `Div4AirportID`                   Int32,
                            `Div4AirportSeqID`                Int32,
                            `Div4WheelsOn`                    Int16,
                            `Div4TotalGTime`                  Int16,
                            `Div4LongestGTime`                Int16,
                            `Div4WheelsOff`                   Int16,
                            `Div4TailNum`                     LowCardinality(String),
                            `Div5Airport`                     LowCardinality(String),
                            `Div5AirportID`                   Int32,
                            `Div5AirportSeqID`                Int32,
                            `Div5WheelsOn`                    Int16,
                            `Div5TotalGTime`                  Int16,
                            `Div5LongestGTime`                Int16,
                            `Div5WheelsOff`                   Int16,
                            `Div5TailNum`                     LowCardinality(String)
                        ) {table_settings};
                        """
                        )
                    )

        with When("I insert data into the ontime table in parallel"):
            for year in range(1987, 2023):
                Step(
                    name="insert 1 year into ontime table",
                    test=insert_ontime_data,
                    parallel=True,
                )(year=year, table_name=table_name)

            join()

        start_time = time.time()

        for i in range(1987, 2023):
            with Scenario(f"loading year {i}"):
                if format:
                    filename = f"/tmp/ontime_{i}.{format.lower()}"
                    query_start_time = time.time()
                    nodes[0].command(
                        f"""clickhouse client --query="SELECT * FROM {table_name} WHERE Year={i} FORMAT {format}" > {filename}"""
                    )
                    metric(
                        f"Select time {i}",
                        units="seconds",
                        value=time.time() - query_start_time,
                    )
                    query_start_time = time.time()
                    nodes[0].command(
                        f"""cat {filename} | clickhouse client --query="INSERT INTO {table_name} FORMAT {format}" """
                    )
                    metric(
                        f"Insert time {i}",
                        units="seconds",
                        value=time.time() - query_start_time,
                    )
                else:
                    query_start_time = time.time()
                    nodes[0].query(
                        f"INSERT INTO {table_name} SELECT * FROM {table_name} WHERE Year={i}"
                    )
                    metric(
                        f"Insert time {i}",
                        units="seconds",
                        value=time.time() - query_start_time,
                    )

        end_time = time.time()
        metric("Insert time", units="seconds", value=end_time - start_time)

        for i in range(15):
            with Scenario(f"query {i}"):
                metric(f"Query {i} time", units="seconds", value=run_benchmark(i))

    finally:
        with Finally("I drop the table"):
            for node in nodes:
                with When(f"on {node}", flags=TE):
                    node.query(f"DROP TABLE IF EXISTS {table_name}", timeout=600)


@TestScenario
def default(self, format=None):
    """Simple benchmark queries for local hard disk with the ontime dataset."""
    table_settings = """
    ENGINE = MergeTree()
    PARTITION BY Year
    ORDER BY (Year, Quarter, Month, DayofMonth, FlightDate, IATA_CODE_Reporting_Airline)
    SETTINGS index_granularity = 8192, storage_policy='default';
    """
    benchmark(table_name="hard_disk", table_settings=table_settings, format=format)


@TestScenario
def s3(self, format=None):
    """Simple benchmark queries for s3 with the ontime dataset."""
    table_settings = """
    ENGINE = MergeTree()
    PARTITION BY Year
    ORDER BY (Year, Quarter, Month, DayofMonth, FlightDate, IATA_CODE_Reporting_Airline)
    SETTINGS index_granularity = 8192, storage_policy='external';
    """
    benchmark(table_name="s3", table_settings=table_settings, format=format)


@TestScenario
@Requirements()
def s3_tiered(self, format=None):
    """Simple benchmark queries for a tiered s3 table with the ontime dataset."""
    table_settings = """
    ENGINE = MergeTree()
    PARTITION BY Year
    ORDER BY (Year, Quarter, Month, DayofMonth, FlightDate, IATA_CODE_Reporting_Airline)
    TTL toStartOfYear(FlightDate) + interval 3 year to volume 'external'
    SETTINGS index_granularity = 8192, storage_policy='tiered';
    """
    benchmark(table_name="tiered", table_settings=table_settings, format=format)


@TestScenario
def zero_copy_replication(self, format=None):
    """Simple benchmark queries for zero copy replication with the ontime dataset."""
    nodes = self.context.nodes

    table_settings = """
        ENGINE = ReplicatedMergeTree('/clickhouse/zero_copy_replication_ontime', '{shard2}')
        PARTITION BY Year
        ORDER BY (Year, Quarter, Month, DayofMonth, FlightDate, IATA_CODE_Reporting_Airline)
        SETTINGS index_granularity = 8192, storage_policy='external';
        """

    with Given("I have merge tree configuration set to use zero copy replication"):
        if check_clickhouse_version(">=21.8")(self):
            settings = {"allow_remote_fs_zero_copy_replication": "1"}
        else:
            settings = {"allow_s3_zero_copy_replication": "1"}

    with mergetree_config(settings):
        benchmark(
            table_name="zero_copy_replication",
            table_settings=table_settings,
            nodes=nodes,
            format=format,
        )


@TestFeature
@Name("queries")
def feature(self, format=None):
    """Benchmarks for S3."""

    for scenario in loads(current_module(), Scenario):
        scenario(format=format)
