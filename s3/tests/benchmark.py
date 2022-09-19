from testflows.core import *

from s3.tests.common import *

import time
import textwrap
import datetime


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
            f"SELECT Carrier, count(*) FROM {table_name} WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier ORDER BY count(*) DESC",
            f"SET joined_subquery_requires_alias = 0; SELECT Carrier, c, c2, c*100/c2 as c3 FROM ( SELECT Carrier, count(*) AS c FROM {table_name} WHERE DepDelay>10 AND Year=2007 GROUP BY Carrier) JOIN ( SELECT Carrier, count(*) AS c2 FROM {table_name} WHERE Year=2007 GROUP BY Carrier) USING Carrier ORDER BY c3 DESC;",
            f"SET joined_subquery_requires_alias = 0; SELECT Carrier, c, c2, c*100/c2 as c3 FROM ( SELECT Carrier, count(*) AS c FROM {table_name} WHERE DepDelay>10 AND Year>=2000 AND Year<=2008 GROUP BY Carrier) JOIN ( SELECT Carrier, count(*) AS c2 FROM {table_name} WHERE Year>=2000 AND Year<=2008 GROUP BY Carrier) USING Carrier ORDER BY c3 DESC;",
            f"SET joined_subquery_requires_alias = 0; SELECT Year, c1/c2 FROM ( select Year, count(*)*100 as c1 from {table_name} WHERE DepDelay>10 GROUP BY Year) JOIN ( select Year, count(*) as c2 from {table_name} GROUP BY Year) USING (Year) ORDER BY Year;",
            f"SELECT DestCityName, uniqExact(OriginCityName) AS u FROM {table_name} WHERE Year >= 2000 and Year <= 2010 GROUP BY DestCityName ORDER BY u DESC LIMIT 10",
            f"SELECT Year, count(*) AS c1 FROM {table_name} GROUP BY Year;",
            f"SELECT min(Year), max(Year), Carrier, count(*) AS cnt, sum(ArrDelayMinutes>30) AS flights_delayed, round(sum(ArrDelayMinutes>30)/count(*),2) AS rate FROM {table_name} WHERE DayOfWeek NOT IN (6,7) AND OriginState NOT IN ('AK', 'HI', 'PR', 'VI') AND DestState NOT IN ('AK', 'HI', 'PR', 'VI') AND FlightDate < '2010-01-01' GROUP by Carrier HAVING cnt>100000 and max(Year)>1990 ORDER by rate DESC LIMIT 1000"
            # f"SELECT count() FROM hard_disk WHERE NOT ignore(*)"
        ]

    try:
        with When("I create a table for the ontime dataset"):
            for i, node in enumerate(nodes):
                with By(f"on {node}"):
                    node.restart()
                    node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")
                    node.query(
                        textwrap.dedent(
                            f"""
                        CREATE TABLE {table_name} (
                          Year UInt16,
                          Quarter UInt8,
                          Month UInt8,
                          DayofMonth UInt8,
                          DayOfWeek UInt8,
                          FlightDate Date,
                          UniqueCarrier FixedString(7),
                          AirlineID Int32,
                          Carrier FixedString(2),
                          TailNum String,
                          FlightNum String,
                          OriginAirportID Int32,
                          OriginAirportSeqID Int32,
                          OriginCityMarketID Int32,
                          Origin FixedString(5),
                          OriginCityName String,
                          OriginState FixedString(2),
                          OriginStateFips String,
                          OriginStateName String,
                          OriginWac Int32,
                          DestAirportID Int32,
                          DestAirportSeqID Int32,
                          DestCityMarketID Int32,
                          Dest FixedString(5),
                          DestCityName String,
                          DestState FixedString(2),
                          DestStateFips String,
                          DestStateName String,
                          DestWac Int32,
                          CRSDepTime Int32,
                          DepTime Int32,
                          DepDelay Int32,
                          DepDelayMinutes Int32,
                          DepDel15 Int32,
                          DepartureDelayGroups String,
                          DepTimeBlk String,
                          TaxiOut Int32,
                          WheelsOff Int32,
                          WheelsOn Int32,
                          TaxiIn Int32,
                          CRSArrTime Int32,
                          ArrTime Int32,
                          ArrDelay Int32,
                          ArrDelayMinutes Int32,
                          ArrDel15 Int32,
                          ArrivalDelayGroups Int32,
                          ArrTimeBlk String,
                          Cancelled UInt8,
                          CancellationCode FixedString(1),
                          Diverted UInt8,
                          CRSElapsedTime Int32,
                          ActualElapsedTime Int32,
                          AirTime Int32,
                          Flights Int32,
                          Distance Int32,
                          DistanceGroup UInt8,
                          CarrierDelay Int32,
                          WeatherDelay Int32,
                          NASDelay Int32,
                          SecurityDelay Int32,
                          LateAircraftDelay Int32,
                          FirstDepTime String,
                          TotalAddGTime String,
                          LongestAddGTime String,
                          DivAirportLandings String,
                          DivReachedDest String,
                          DivActualElapsedTime String,
                          DivArrDelay String,
                          DivDistance String,
                          Div1Airport String,
                          Div1AirportID Int32,
                          Div1AirportSeqID Int32,
                          Div1WheelsOn String,
                          Div1TotalGTime String,
                          Div1LongestGTime String,
                          Div1WheelsOff String,
                          Div1TailNum String,
                          Div2Airport String,
                          Div2AirportID Int32,
                          Div2AirportSeqID Int32,
                          Div2WheelsOn String,
                          Div2TotalGTime String,
                          Div2LongestGTime String,
                          Div2WheelsOff String,
                          Div2TailNum String,
                          Div3Airport String,
                          Div3AirportID Int32,
                          Div3AirportSeqID Int32,
                          Div3WheelsOn String,
                          Div3TotalGTime String,
                          Div3LongestGTime String,
                          Div3WheelsOff String,
                          Div3TailNum String,
                          Div4Airport String,
                          Div4AirportID Int32,
                          Div4AirportSeqID Int32,
                          Div4WheelsOn String,
                          Div4TotalGTime String,
                          Div4LongestGTime String,
                          Div4WheelsOff String,
                          Div4TailNum String,
                          Div5Airport String,
                          Div5AirportID Int32,
                          Div5AirportSeqID Int32,
                          Div5WheelsOn String,
                          Div5TotalGTime String,
                          Div5LongestGTime String,
                          Div5WheelsOff String,
                          Div5TailNum String
                        ) {table_settings};
                    """
                        )
                    )

        start_time = time.time()

        for i in range(2006, 2018):
            with Scenario(f"loading year {i}"):
                if format:
                    filename = f"/tmp/ontime_{i}.{format.lower()}"
                    query_start_time = time.time()
                    nodes[0].command(
                        f"""clickhouse client --query="SELECT * FROM datasets.ontime WHERE Year={i} FORMAT {format}" > {filename}"""
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
                        f"INSERT INTO {table_name} SELECT * FROM datasets.ontime WHERE Year={i}"
                    )
                    metric(
                        f"Insert time {i}",
                        units="seconds",
                        value=time.time() - query_start_time,
                    )

        end_time = time.time()
        metric("Insert time", units="seconds", value=end_time - start_time)

        for i in range(11):
            with Scenario(f"query {i}"):
                metric(f"Query {i} time", units="seconds", value=run_benchmark(i))

    finally:
        with Finally("I drop the table"):
            for node in nodes:
                with When(f"on {node}", flags=TE):
                    node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestScenario
def default(self, format=None):
    """Simple benchmark queries for local hard disk with the ontime dataset."""
    table_settings = """
    ENGINE = MergeTree()
    PARTITION BY Year
    ORDER BY (Carrier, FlightDate)
    SETTINGS index_granularity = 8192, storage_policy='default';
    """
    benchmark(table_name="hard_disk", table_settings=table_settings, format=format)


@TestScenario
def s3(self, format=None):
    """Simple benchmark queries for s3 with the ontime dataset."""
    table_settings = """
    ENGINE = MergeTree()
    PARTITION BY Year
    ORDER BY (Carrier, FlightDate)
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
    ORDER BY (Carrier, FlightDate)
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
        ORDER BY (Carrier, FlightDate)
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
    Scenario(run=default)
    # for scenario in loads(current_module(), Scenario):
    #     scenario(format=format)
