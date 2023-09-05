from testflows.core import *
from helpers.common import getuid, check_clickhouse_version


@TestStep(Given)
def create_parquet_file_hits(
    self,
    first_number: int,
    last_number: int,
    threads: str,
    max_memory_usage: int,
    compression: str = None,
):
    """Prepare data in Parquet format using the hits dataset from
    https://datasets.clickhouse.com/hits_compatible/athena_partitioned/hits_%7B0..99%7D.parquet."""

    clickhouse_node = self.context.clickhouse_node
    table_name = "hits_" + getuid()
    parquet_file = "hits_parquet_" + getuid() + ".parquet"
    with Given(
        "I create a hits table in clickhouse and populate it with the ontime airlines dataset"
    ):
        clickhouse_node.query(
            f"""
            CREATE TABLE {table_name}
        (
            WatchID BIGINT NOT NULL,
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
            CLID INTEGER NOT NULL
        ) ENGINE = MergeTree ORDER BY tuple()
"""
        )

        clickhouse_node.query(
            f"INSERT INTO {table_name} SELECT * FROM s3('https://clickhouse-public-datasets.s3.amazonaws.com"
            f"/hits_compatible/athena_partitioned/hits_{{{first_number}..{last_number}}}.parquet') SETTINGS max_insert_threads = {threads}, "
            f"max_memory_usage={max_memory_usage};",
            progress=True,
            timeout=900,
        )

        insert_into_parquet = (
            f"SELECT * FROM {table_name} INTO OUTFILE '{parquet_file}' FORMAT Parquet SETTINGS "
            f"max_insert_threads = {threads}, max_memory_usage={max_memory_usage}"
        )

        if check_clickhouse_version(">=23.3")(self):
            insert_into_parquet += (
                f", output_format_parquet_compression_method='{compression}'"
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
