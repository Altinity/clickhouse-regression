import json
import os
import re
import subprocess
import time

from testflows.core import *
from helpers.common import getuid
from parquet.performance.tests.datasets.nyc_taxi import create_parquet_file_nyc_taxi
from parquet.performance.tests.datasets.ontime import create_parquet_file
from parquet.performance.tests.datasets.hits import create_parquet_file_hits
from parquet.performance.tests.duckdb.reports import (
    write_to_csv,
    create_bar_chart,
    convert_to_markdown,
    create_directory_if_not_exists,
)
from parquet.performance.tests.duckdb.steps import *
from parquet.performance.tests.duckdb.steps_hits import *
from parquet.performance.tests.duckdb.steps_nyc_taxi import queries_nyc_taxi


def get_memory_usage(output):
    """Extract MemoryTracker values from the output of a ClickHouse query from print-profile-events."""

    output = output.stderr

    memory_tracker_usage_pattern = r"MemoryTrackerUsage:\s+(\d+)\s+\(gauge\)"
    memory_tracker_peak_usage_pattern = r"MemoryTrackerPeakUsage:\s+(\d+)\s+\(gauge\)"

    memory_tracker_usage = re.search(memory_tracker_usage_pattern, output)
    memory_tracker_peak_usage = re.search(memory_tracker_peak_usage_pattern, output)

    if memory_tracker_usage and memory_tracker_peak_usage:
        return {
            "MemoryTrackerUsage": int(memory_tracker_usage.group(1)),
            "MemoryTrackerPeakUsage": int(memory_tracker_peak_usage.group(1)),
        }
    else:
        return {"error": output}


def hits_queries(file_name, native_reader=False):
    table_schema = """WatchID BIGINT NOT NULL,
            JavaEnable SMALLINT NOT NULL,
            Title TEXT NOT NULL,
            GoodEvent SMALLINT NOT NULL,
            EventTime TIMESTAMP NOT NULL,
            EventDate Date NOT NULL,
            CounterID INTEGER NOT NULL,
            ClientIP INTEGER NOT NULL,
            RegionID INTEGER NOT NULL,
            UserID BIGINT NOT NULL,
            CounterClass SMALLINT NOT NULL,
            OS SMALLINT NOT NULL,
            UserAgent SMALLINT NOT NULL,
            URL TEXT NOT NULL,
            Referer TEXT NOT NULL,
            IsRefresh SMALLINT NOT NULL,
            RefererCategoryID SMALLINT NOT NULL,
            RefererRegionID INTEGER NOT NULL,
            URLCategoryID SMALLINT NOT NULL,
            URLRegionID INTEGER NOT NULL,
            ResolutionWidth SMALLINT NOT NULL,
            ResolutionHeight SMALLINT NOT NULL,
            ResolutionDepth SMALLINT NOT NULL,
            FlashMajor SMALLINT NOT NULL,
            FlashMinor SMALLINT NOT NULL,
            FlashMinor2 TEXT NOT NULL,
            NetMajor SMALLINT NOT NULL,
            NetMinor SMALLINT NOT NULL,
            UserAgentMajor SMALLINT NOT NULL,
            UserAgentMinor VARCHAR(255) NOT NULL,
            CookieEnable SMALLINT NOT NULL,
            JavascriptEnable SMALLINT NOT NULL,
            IsMobile SMALLINT NOT NULL,
            MobilePhone SMALLINT NOT NULL,
            MobilePhoneModel TEXT NOT NULL,
            Params TEXT NOT NULL,
            IPNetworkID INTEGER NOT NULL,
            TraficSourceID SMALLINT NOT NULL,
            SearchEngineID SMALLINT NOT NULL,
            SearchPhrase TEXT NOT NULL,
            AdvEngineID SMALLINT NOT NULL,
            IsArtifical SMALLINT NOT NULL,
            WindowClientWidth SMALLINT NOT NULL,
            WindowClientHeight SMALLINT NOT NULL,
            ClientTimeZone SMALLINT NOT NULL,
            ClientEventTime TIMESTAMP NOT NULL,
            SilverlightVersion1 SMALLINT NOT NULL,
            SilverlightVersion2 SMALLINT NOT NULL,
            SilverlightVersion3 INTEGER NOT NULL,
            SilverlightVersion4 SMALLINT NOT NULL,
            PageCharset TEXT NOT NULL,
            CodeVersion INTEGER NOT NULL,
            IsLink SMALLINT NOT NULL,
            IsDownload SMALLINT NOT NULL,
            IsNotBounce SMALLINT NOT NULL,
            FUniqID BIGINT NOT NULL,
            OriginalURL TEXT NOT NULL,
            HID INTEGER NOT NULL,
            IsOldCounter SMALLINT NOT NULL,
            IsEvent SMALLINT NOT NULL,
            IsParameter SMALLINT NOT NULL,
            DontCountHits SMALLINT NOT NULL,
            WithHash SMALLINT NOT NULL,
            HitColor CHAR NOT NULL,
            LocalEventTime TIMESTAMP NOT NULL,
            Age SMALLINT NOT NULL,
            Sex SMALLINT NOT NULL,
            Income SMALLINT NOT NULL,
            Interests SMALLINT NOT NULL,
            Robotness SMALLINT NOT NULL,
            RemoteIP INTEGER NOT NULL,
            WindowName INTEGER NOT NULL,
            OpenerName INTEGER NOT NULL,
            HistoryLength SMALLINT NOT NULL,
            BrowserLanguage TEXT NOT NULL,
            BrowserCountry TEXT NOT NULL,
            SocialNetwork TEXT NOT NULL,
            SocialAction TEXT NOT NULL,
            HTTPError SMALLINT NOT NULL,
            SendTiming INTEGER NOT NULL,
            DNSTiming INTEGER NOT NULL,
            ConnectTiming INTEGER NOT NULL,
            ResponseStartTiming INTEGER NOT NULL,
            ResponseEndTiming INTEGER NOT NULL,
            FetchTiming INTEGER NOT NULL,
            SocialSourceNetworkID SMALLINT NOT NULL,
            SocialSourcePage TEXT NOT NULL,
            ParamPrice BIGINT NOT NULL,
            ParamOrderID TEXT NOT NULL,
            ParamCurrency TEXT NOT NULL,
            ParamCurrencyID SMALLINT NOT NULL,
            OpenstatServiceName TEXT NOT NULL,
            OpenstatCampaignID TEXT NOT NULL,
            OpenstatAdID TEXT NOT NULL,
            OpenstatSourceID TEXT NOT NULL,
            UTMSource TEXT NOT NULL,
            UTMMedium TEXT NOT NULL,
            UTMCampaign TEXT NOT NULL,
            UTMContent TEXT NOT NULL,
            UTMTerm TEXT NOT NULL,
            FromTag TEXT NOT NULL,
            HasGCLID SMALLINT NOT NULL,
            RefererHash BIGINT NOT NULL,
            URLHash BIGINT NOT NULL,
            CLID INTEGER NOT NULL"""

    if native_reader:
        native_reader = "1"
    else:
        native_reader = "0"

    queries = [
        rf"SELECT COUNT(*) FROM file('{file_name}', Parquet, '{table_schema}') SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT COUNT(*) FROM file('{file_name}', Parquet, '{table_schema}') WHERE AdvEngineID <> 0 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SUM(AdvEngineID), COUNT(*), AVG(ResolutionWidth) FROM file('{file_name}', Parquet, '{table_schema}') SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT AVG(UserID) FROM file('{file_name}', Parquet, '{table_schema}') SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT COUNT(DISTINCT UserID) FROM file('{file_name}', Parquet, '{table_schema}') SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT COUNT(DISTINCT SearchPhrase) FROM file('{file_name}', Parquet, '{table_schema}') SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT MIN(EventDate), MAX(EventDate) FROM file('{file_name}', Parquet, '{table_schema}') SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT AdvEngineID, COUNT(*) FROM file('{file_name}', Parquet, '{table_schema}') WHERE AdvEngineID <> 0 GROUP BY AdvEngineID ORDER BY COUNT(*) DESC SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT RegionID, COUNT(DISTINCT UserID) AS u FROM file('{file_name}', Parquet, '{table_schema}') GROUP BY RegionID ORDER BY u DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT RegionID, SUM(AdvEngineID), COUNT(*) AS c, AVG(ResolutionWidth), COUNT(DISTINCT UserID) FROM file('{file_name}', Parquet, '{table_schema}') GROUP BY RegionID ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file('{file_name}', Parquet, '{table_schema}') WHERE MobilePhoneModel <> '' GROUP BY MobilePhoneModel ORDER BY u DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT MobilePhone, MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM file('{file_name}', Parquet, '{table_schema}') WHERE MobilePhoneModel <> '' GROUP BY MobilePhone, MobilePhoneModel ORDER BY u DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SearchPhrase, COUNT(*) AS c FROM file('{file_name}', Parquet, '{table_schema}') WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SearchPhrase, COUNT(DISTINCT UserID) AS u FROM file('{file_name}', Parquet, '{table_schema}') WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY u DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SearchEngineID, SearchPhrase, COUNT(*) AS c FROM file('{file_name}', Parquet, '{table_schema}') WHERE SearchPhrase <> '' GROUP BY SearchEngineID, SearchPhrase ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT UserID, COUNT(*) FROM file('{file_name}', Parquet, '{table_schema}') GROUP BY UserID ORDER BY COUNT(*) DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT UserID, SearchPhrase, COUNT(*) FROM file('{file_name}', Parquet, '{table_schema}') GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT UserID, SearchPhrase, COUNT(*) FROM file('{file_name}', Parquet, '{table_schema}') GROUP BY UserID, SearchPhrase LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT UserID, extract(minute FROM EventTime) AS m, SearchPhrase, COUNT(*) FROM file('{file_name}', Parquet, '{table_schema}') GROUP BY UserID, m, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT UserID FROM file('{file_name}', Parquet, '{table_schema}') WHERE UserID = 435090932899640449 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT COUNT(*) FROM file('{file_name}', Parquet, '{table_schema}') WHERE URL LIKE '%google%' SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SearchPhrase, MIN(URL), COUNT(*) AS c FROM file('{file_name}', Parquet, '{table_schema}') WHERE URL LIKE '%google%' AND SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SearchPhrase, MIN(URL), MIN(Title), COUNT(*) AS c, COUNT(DISTINCT UserID) FROM file('{file_name}', Parquet, '{table_schema}') WHERE Title LIKE '%Google%' AND URL NOT LIKE '%.google.%' AND SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT * FROM file('{file_name}', Parquet, '{table_schema}') WHERE URL LIKE '%google%' ORDER BY EventTime LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SearchPhrase FROM file('{file_name}', Parquet, '{table_schema}') WHERE SearchPhrase <> '' ORDER BY EventTime LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SearchPhrase FROM file('{file_name}', Parquet, '{table_schema}') WHERE SearchPhrase <> '' ORDER BY SearchPhrase LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SearchPhrase FROM file('{file_name}', Parquet, '{table_schema}') WHERE SearchPhrase <> '' ORDER BY EventTime, SearchPhrase LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT CounterID, AVG(length(URL)) AS l, COUNT(*) AS c FROM file('{file_name}', Parquet, '{table_schema}') WHERE URL <> '' GROUP BY CounterID HAVING COUNT(*) > 100000 ORDER BY l DESC LIMIT 25 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT REGEXP_REPLACE(Referer, '^https?://(?:www\\.)?([^/]+)/.*$', '\\1') AS k, AVG(length(Referer)) AS l, COUNT(*) AS c, MIN(Referer) FROM file('{file_name}', Parquet, '{table_schema}') WHERE Referer <> '' GROUP BY k HAVING COUNT(*) > 100000 ORDER BY l DESC LIMIT 25 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SUM(ResolutionWidth), SUM(ResolutionWidth + 1), SUM(ResolutionWidth + 2), SUM(ResolutionWidth + 3), SUM(ResolutionWidth + 4), SUM(ResolutionWidth + 5), SUM(ResolutionWidth + 6), SUM(ResolutionWidth + 7), SUM(ResolutionWidth + 8), SUM(ResolutionWidth + 9), SUM(ResolutionWidth + 10), SUM(ResolutionWidth + 11), SUM(ResolutionWidth + 12), SUM(ResolutionWidth + 13), SUM(ResolutionWidth + 14), SUM(ResolutionWidth + 15), SUM(ResolutionWidth + 16), SUM(ResolutionWidth + 17), SUM(ResolutionWidth + 18), SUM(ResolutionWidth + 19), SUM(ResolutionWidth + 20), SUM(ResolutionWidth + 21), SUM(ResolutionWidth + 22), SUM(ResolutionWidth + 23), SUM(ResolutionWidth + 24), SUM(ResolutionWidth + 25), SUM(ResolutionWidth + 26), SUM(ResolutionWidth + 27), SUM(ResolutionWidth + 28), SUM(ResolutionWidth + 29), SUM(ResolutionWidth + 30), SUM(ResolutionWidth + 31), SUM(ResolutionWidth + 32), SUM(ResolutionWidth + 33), SUM(ResolutionWidth + 34), SUM(ResolutionWidth + 35), SUM(ResolutionWidth + 36), SUM(ResolutionWidth + 37), SUM(ResolutionWidth + 38), SUM(ResolutionWidth + 39), SUM(ResolutionWidth + 40), SUM(ResolutionWidth + 41), SUM(ResolutionWidth + 42), SUM(ResolutionWidth + 43), SUM(ResolutionWidth + 44), SUM(ResolutionWidth + 45), SUM(ResolutionWidth + 46), SUM(ResolutionWidth + 47), SUM(ResolutionWidth + 48), SUM(ResolutionWidth + 49), SUM(ResolutionWidth + 50), SUM(ResolutionWidth + 51), SUM(ResolutionWidth + 52), SUM(ResolutionWidth + 53), SUM(ResolutionWidth + 54), SUM(ResolutionWidth + 55), SUM(ResolutionWidth + 56), SUM(ResolutionWidth + 57), SUM(ResolutionWidth + 58), SUM(ResolutionWidth + 59), SUM(ResolutionWidth + 60), SUM(ResolutionWidth + 61), SUM(ResolutionWidth + 62), SUM(ResolutionWidth + 63), SUM(ResolutionWidth + 64), SUM(ResolutionWidth + 65), SUM(ResolutionWidth + 66), SUM(ResolutionWidth + 67), SUM(ResolutionWidth + 68), SUM(ResolutionWidth + 69), SUM(ResolutionWidth + 70), SUM(ResolutionWidth + 71), SUM(ResolutionWidth + 72), SUM(ResolutionWidth + 73), SUM(ResolutionWidth + 74), SUM(ResolutionWidth + 75), SUM(ResolutionWidth + 76), SUM(ResolutionWidth + 77), SUM(ResolutionWidth + 78), SUM(ResolutionWidth + 79), SUM(ResolutionWidth + 80), SUM(ResolutionWidth + 81), SUM(ResolutionWidth + 82), SUM(ResolutionWidth + 83), SUM(ResolutionWidth + 84), SUM(ResolutionWidth + 85), SUM(ResolutionWidth + 86), SUM(ResolutionWidth + 87), SUM(ResolutionWidth + 88), SUM(ResolutionWidth + 89) FROM file('{file_name}', Parquet, '{table_schema}') SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT SearchEngineID, ClientIP, COUNT(*) AS c, SUM(IsRefresh), AVG(ResolutionWidth) FROM file('{file_name}', Parquet, '{table_schema}') WHERE SearchPhrase <> '' GROUP BY SearchEngineID, ClientIP ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT WatchID, ClientIP, COUNT(*) AS c, SUM(IsRefresh), AVG(ResolutionWidth) FROM file('{file_name}', Parquet, '{table_schema}') WHERE SearchPhrase <> '' GROUP BY WatchID, ClientIP ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT WatchID, ClientIP, COUNT(*) AS c, SUM(IsRefresh), AVG(ResolutionWidth) FROM file('{file_name}', Parquet, '{table_schema}') GROUP BY WatchID, ClientIP ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT URL, COUNT(*) AS c FROM file('{file_name}', Parquet, '{table_schema}') GROUP BY URL ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT 1, URL, COUNT(*) AS c FROM file('{file_name}', Parquet, '{table_schema}') GROUP BY 1, URL ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT ClientIP, ClientIP - 1, ClientIP - 2, ClientIP - 3, COUNT(*) AS c FROM file('{file_name}', Parquet, '{table_schema}') GROUP BY ClientIP, ClientIP - 1, ClientIP - 2, ClientIP - 3 ORDER BY c DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT URL, COUNT(*) AS PageViews FROM file('{file_name}', Parquet, '{table_schema}') WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND DontCountHits = 0 AND IsRefresh = 0 AND URL <> '' GROUP BY URL ORDER BY PageViews DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT Title, COUNT(*) AS PageViews FROM file('{file_name}', Parquet, '{table_schema}') WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND DontCountHits = 0 AND IsRefresh = 0 AND Title <> '' GROUP BY Title ORDER BY PageViews DESC LIMIT 10 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT URL, COUNT(*) AS PageViews FROM file('{file_name}', Parquet, '{table_schema}') WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND IsRefresh = 0 AND IsLink <> 0 AND IsDownload = 0 GROUP BY URL ORDER BY PageViews DESC LIMIT 10 OFFSET 1000 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT TraficSourceID, SearchEngineID, AdvEngineID, CASE WHEN (SearchEngineID = 0 AND AdvEngineID = 0) THEN Referer ELSE '' END AS Src, URL AS Dst, COUNT(*) AS PageViews FROM file('{file_name}', Parquet, '{table_schema}') WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND IsRefresh = 0 GROUP BY TraficSourceID, SearchEngineID, AdvEngineID, Src, Dst ORDER BY PageViews DESC LIMIT 10 OFFSET 1000 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT URLHash, EventDate, COUNT(*) AS PageViews FROM file('{file_name}', Parquet, '{table_schema}') WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND IsRefresh = 0 AND TraficSourceID IN (-1, 6) AND RefererHash = 3594120000172545465 GROUP BY URLHash, EventDate ORDER BY PageViews DESC LIMIT 10 OFFSET 100 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT WindowClientWidth, WindowClientHeight, COUNT(*) AS PageViews FROM file('{file_name}', Parquet, '{table_schema}') WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= '2013-07-31' AND IsRefresh = 0 AND DontCountHits = 0 AND URLHash = 2868770270353813622 GROUP BY WindowClientWidth, WindowClientHeight ORDER BY PageViews DESC LIMIT 10 OFFSET 10000 SETTINGS input_format_parquet_use_native_reader={native_reader};",
        rf"SELECT DATE_TRUNC('minute', EventTime) AS M, COUNT(*) AS PageViews FROM file('{file_name}', Parquet, '{table_schema}') WHERE CounterID = 62 AND EventDate >= '2013-07-14' AND EventDate <= '2013-07-15' AND IsRefresh = 0 AND DontCountHits = 0 GROUP BY DATE_TRUNC('minute', EventTime) ORDER BY DATE_TRUNC('minute', EventTime) LIMIT 10 OFFSET 1000 SETTINGS input_format_parquet_use_native_reader={native_reader};",
    ]

    return queries

@TestStep(Given)
def clear_filesystem_and_flush_cache(self):
    """Clear filesystem cache and flush cache."""
    subprocess.run("sync", shell=True)
    subprocess.run("echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null", shell=True)
    note("Filesystem cache cleared and flushed.")


@TestStep(Given)
def clickhouse_local(self, query, statistics=False):
    """Run a query locally."""
    query_args = [self.context.clickhouse_binary, "--multiquery"]

    if statistics:
        query_args.append("--print-profile-events")

    result = subprocess.run(
        query_args,
        input=query,
        text=True,
        capture_output=True,
    )

    # Assert that the exit code is 0
    # assert (
    #     result.returncode == 0
    # ), f"ClickHouse local {query} failed with exit code {result.returncode}. Error: {result.stderr}"

    note(f"query: {result.stdout}")

    if not statistics:
        return result.stdout
    else:
        return result.stdout, get_memory_usage(result)


@TestStep(Given)
def download_hits_dataset(self, filename):
    """Download the hits dataset."""
    if os.path.exists(filename):
        note(f"The file '{filename}' already exists. Skipping download.")
        return
    note(f"Downloading the hits dataset to '{filename}'...")
    subprocess.run(
        f"wget -O {filename} https://datasets.clickhouse.com/hits_compatible/hits.parquet",
        shell=True,
        check=True,
    )


@TestStep(Given)
def get_clickhouse_version(self):
    """Get the ClickHouse version."""
    version = clickhouse_local(query="SELECT version();")

    return version


@TestStep(Given)
def create_parquet_file(self, table_name, parquet_file, threads=10, max_memory_usage=0):
    insert_into_parquet = (
        f"SELECT * FROM {table_name} INTO OUTFILE '{parquet_file}' FORMAT Parquet SETTINGS "
        f"max_insert_threads = {threads}, max_memory_usage={max_memory_usage};"
    )

    return insert_into_parquet


@TestScenario
def hits_dataset(self, repeats):
    """Check performance of ClickHouse parquet native reader using the hits dataset."""
    file_name = f"hits.parquet"
    results = {"native_reader": {}, "regular_reader": {}}
    with Given("I create a parquet file with the hits dataset"):
        # clickhouse_local(
        #     query=create_hits_dataset(table_name=table_name)
        #     + ";"
        #     + insert_data_hits(table_name=table_name)
        #     + create_parquet_file(
        #         table_name=table_name, parquet_file=f"{table_name}.parquet"
        #     )
        # )
        download_hits_dataset(filename=file_name)

    with When("I run queries against the parquet file with native parquet reader"):
        queries_with_native_reader = hits_queries(
            file_name=f"{file_name}", native_reader=True
        )

        for index, query in enumerate(queries_with_native_reader):
            for i in range(repeats):
                clear_filesystem_and_flush_cache()
                start_time = time.time()
                result, memory_used = clickhouse_local(query=query, statistics=True)
                clickhouse_run_time = time.time() - start_time

                if f"query_{index}" not in results["native_reader"]:
                    results["native_reader"][f"query_{index}"] = {
                        f"time_{i}": clickhouse_run_time,
                        f"memory_{i}": memory_used,
                    }
                else:
                    results["native_reader"][f"query_{index}"][
                        f"time_{i}"
                    ] = clickhouse_run_time
                    results["native_reader"][f"query_{index}"][
                        f"memory_{i}"
                    ] = memory_used

    with And("I run queries against the parquet file without native parquet reader"):
        queries_without_native_reader = hits_queries(
            file_name=f"{file_name}", native_reader=False
        )

        for index, query in enumerate(queries_without_native_reader):
            for i in range(repeats):
                clear_filesystem_and_flush_cache()
                start_time = time.time()
                result, memory_used = clickhouse_local(query=query, statistics=True)
                clickhouse_run_time = time.time() - start_time

                if f"query_{index}" not in results["regular_reader"]:
                    results["regular_reader"][f"query_{index}"] = {
                        f"time_{i}": clickhouse_run_time,
                        f"memory_{i}": memory_used,
                    }
                else:
                    results["regular_reader"][f"query_{index}"][
                        f"time_{i}"
                    ] = clickhouse_run_time
                    results["regular_reader"][f"query_{index}"][
                        f"memory_{i}"
                    ] = memory_used

    with Then("I write results into a JSON file"):
        clickhouse_version = get_clickhouse_version().strip()
        json_file_path = os.path.join(
            current_dir(),
            "..",
            "..",
            "results",
            "native_reader",
            "hits",
            f"{clickhouse_version}",
            "results.json",
        )

        # Ensure the directory exists
        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

        # Write the results dictionary to a JSON file
        with open(json_file_path, "w") as json_file:
            json.dump(results, json_file, indent=2)


@TestFeature
@Name("native reader")
def feature(self, repeats=3):
    """Check performance of ClickHouse parquet native reader."""
    Scenario(test=hits_dataset)(repeats=repeats)
