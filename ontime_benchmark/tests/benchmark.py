from testflows.core import *

from s3.tests.common import *

import time
import textwrap
import datetime


@TestStep(Given)
def insert_ontime_data(self, from_year, to_year, table_name, node=None):
    """Insert data into ontime table from s3 disk with specified year"""

    if node is None:
        node = self.context.node

    node.query(
        f"INSERT INTO {table_name} SELECT * FROM ontime_data WHERE Year BETWEEN {from_year} AND {to_year}",
        timeout = 1200
    )


@TestStep(Given)
def fetch_ontime_data(self, from_year, to_year, node=None):
    """Download ontime data from s3 with specified year to a local table"""

    if node is None:
        node = self.context.node

    with Given("I create a table to store ontime data locally"):
        create_ontime_table(
            table_name="ontime_data",
            table_settings="""
            ENGINE = MergeTree()
            PARTITION BY Year
            ORDER BY (Year, Quarter, Month)
            SETTINGS index_granularity = 8192, storage_policy='default';
            """,
            node=node,
        )

    with And(
        f"I insert ontime data from s3 for {from_year}-{to_year} to the local table"
    ):
        node.query(
            f"INSERT INTO ontime_data "
            f"SELECT * FROM s3('https://clickhouse-public-datasets.s3.amazonaws.com/ontime/csv_by_year/{{{from_year}..{to_year}}}.csv.gz', CSVWithNames) "
            "SETTINGS receive_timeout=600, "
            "max_insert_threads=10, "  # This affects memory more than it affects performance
            "max_memory_usage=29500000000;",  # Runners have about this much available memory
            timeout=1200,
        )


@TestStep(Given)
def create_ontime_table(self, table_name, table_settings, node=None):
    if node is None:
        node = self.context.node

    minimal_table_create = f"""CREATE TABLE {table_name}
        (
            `Year`                            UInt16,
            `Quarter`                         UInt8,
            `Month`                           UInt8,
            `DayofMonth`                      UInt8,
            `DayOfWeek`                       UInt8,
            `FlightDate`                      Date,
            `IATA_CODE_Reporting_Airline`     LowCardinality(String),
            `Origin`                          FixedString(5),
            `OriginCityName`                  LowCardinality(String),
            `OriginState`                     FixedString(2),
            `DestCityName`                    LowCardinality(String),
            `DestState`                       FixedString(2),
            `DepDelay`                        Int32,
            `DepDel15`                        Int32,
            `ArrDelayMinutes`                 Int32,
        ) {table_settings}
    """

    full_table_create = f"""CREATE TABLE {table_name}
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
        ) {table_settings}
        """

    try:
        with When(f"I create {table_name} table with ontime data structure"):
            if (
                self.context.stress
                or self.context.storage == "minio"
                or check_clickhouse_version("<23")(self)
            ):
                node.query(textwrap.dedent(full_table_create), use_file=True)
            else:
                node.query(textwrap.dedent(minimal_table_create), use_file=True)

        yield

    finally:
        with Finally("I drop the table"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} SETTINGS receive_timeout=3600",
                timeout=3600,
            )


@TestOutline
def benchmark(
    self, table_name, table_settings, start_year, end_year, nodes=None, format=None
):
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

    with When("I create tables for the ontime dataset"):
        for i, node in enumerate(nodes):
            with Given(f"table on {node.name}"):
                node.restart()
                create_ontime_table(
                    table_name=table_name, table_settings=table_settings, node=node
                )

    with When("I insert ontime data into the testing table"):
        for retry in retries(timeout=60, delay=1):
            with retry:
                Step(
                    name=f"insert data from {start_year} to {end_year} into ontime table",
                    test=insert_ontime_data,
                )(from_year=start_year, to_year=end_year, table_name=table_name)

    start_time = time.time()

    for i in range(start_year, end_year):
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


@TestScenario
def default(self, start_year, end_year, format=None):
    """Simple benchmark queries for local hard disk with the ontime dataset."""
    table_settings = """
    ENGINE = MergeTree()
    PARTITION BY Year
    ORDER BY (Year, Quarter, Month, DayofMonth, FlightDate, IATA_CODE_Reporting_Airline)
    SETTINGS index_granularity = 8192, storage_policy='default';
    """
    benchmark(
        table_name="hard_disk",
        table_settings=table_settings,
        start_year=start_year,
        end_year=end_year,
        format=format,
    )


@TestScenario
def s3(self, start_year, end_year, format=None):
    """Simple benchmark queries for s3 with the ontime dataset."""
    table_settings = """
    ENGINE = MergeTree()
    PARTITION BY Year
    ORDER BY (Year, Quarter, Month, DayofMonth, FlightDate, IATA_CODE_Reporting_Airline)
    SETTINGS index_granularity = 8192, storage_policy='external';
    """
    benchmark(
        table_name="s3",
        table_settings=table_settings,
        start_year=start_year,
        end_year=end_year,
        format=format,
    )


@TestScenario
@Requirements()
def s3_tiered(self, start_year, end_year, format=None):
    """Simple benchmark queries for a tiered s3 table with the ontime dataset."""
    table_settings = """
    ENGINE = MergeTree()
    PARTITION BY Year
    ORDER BY (Year, Quarter, Month, DayofMonth, FlightDate, IATA_CODE_Reporting_Airline)
    TTL toStartOfYear(FlightDate) + interval 3 year to volume 'external'
    SETTINGS index_granularity = 8192, storage_policy='tiered';
    """
    benchmark(
        table_name="tiered",
        table_settings=table_settings,
        start_year=start_year,
        end_year=end_year,
        format=format,
    )


@TestScenario
def zero_copy_replication(self, start_year, end_year, format=None):
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

        mergetree_config(settings=settings)

    benchmark(
        table_name="zero_copy_replication",
        table_settings=table_settings,
        start_year=start_year,
        end_year=end_year,
        nodes=nodes,
        format=format,
    )


@TestFeature
@Name("queries")
def feature(self, format=None):
    """Benchmarks for S3."""

    with Given("Ontime dataset is downloaded from s3"):
        if self.context.stress:
            start_year = 1987
            end_year = 2015
        elif self.context.storage == "minio":
            start_year = 2007
            end_year = 2012
        else:
            start_year = 1999
            end_year = 2002

        fetch_ontime_data(from_year=start_year, to_year=end_year)

    for scenario in loads(current_module(), Scenario):
        scenario(format=format, start_year=start_year, end_year=end_year)
