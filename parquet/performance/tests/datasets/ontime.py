from testflows.core import *
from helpers.common import getuid


@TestStep(Given)
def create_parquet_files(
    self,
    from_year: int,
    to_year: int,
    threads: str,
    max_memory_usage: int,
    compression: str = None,
):
    """Prepare data in Parquet format using the ontime airlines dataset
    https://clickhouse.com/docs/en/getting-started/example-datasets/ontime
    that contains 200M rows."""

    clickhouse_node = self.context.clickhouse_node
    table_name = "ontime_" + getuid()
    parquet_file = "ontime_parquet_" + getuid() + ".parquet"
    with Given(
        "I create an ontime table in clickhouse and populate it with the ontime airlines dataset"
    ):
        clickhouse_node.query(
            f"""
            CREATE TABLE `{table_name}`
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
        ) ENGINE = MergeTree
          ORDER BY (Year, Quarter, Month, DayofMonth, FlightDate, IATA_CODE_Reporting_Airline);
                """
        )

        clickhouse_node.query(
            f"INSERT INTO {table_name} SELECT * FROM s3('https://clickhouse-public-datasets.s3.amazonaws.com/ontime"
            f"/csv_by_year/{{{from_year}..{to_year}}}.csv.gz', CSVWithNames) SETTINGS max_insert_threads = {threads}, max_memory_usage={max_memory_usage};",
            progress=True,
            timeout=900,
        )

        insert_into_parquet = (
            f"SELECT * FROM {table_name} INTO OUTFILE '{parquet_file}' FORMAT Parquet SETTINGS "
            f"max_insert_threads = {threads}, max_memory_usage={max_memory_usage}"
        )

        if compression is not None:
            insert_into_parquet += (
                f", output_format_parquet_compression_method={compression}"
            )

        clickhouse_node.query(
            insert_into_parquet,
            timeout=1800,
        )

        clickhouse_node.command(
            f"mv {parquet_file} /var/lib/clickhouse/user_files", exitcode=0
        )

    yield parquet_file
    clickhouse_node.query(f"DROP TABLE {table_name}")
