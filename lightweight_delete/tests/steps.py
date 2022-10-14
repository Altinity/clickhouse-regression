from copy import deepcopy
import random

from helpers.common import *
from xml.sax.saxutils import escape as xml_escape


@TestStep
def create_acceptance_table_with_tiered_storage_ttl(
    self, storage_policy, table_name="acceptance_table", node=None, ttl_delete=False
):
    """Creating acceptance table with tiered storage ttl"""
    if node is None:
        node = self.context.node

    try:
        with Given(f"I have acceptance table with tiered storage ttl"):
            node.query(
                f"""CREATE TABLE {table_name} (
              Date DateTime,
              timestamp UInt32,
              version LowCardinality(String),
              remoteIP String,
              clientIP String,
              Id UInt64 DEFAULT CAST(0, 'UInt64'),
              originIds Array(UInt64),
              Ids Array(UInt64),
              str String,
              str_arr Array(String),
              a UInt8,
              b UInt16,
              c UInt16,
              int_arr Array(UInt32),
            )"""
                + """
            ENGINE = MergeTree()
            PARTITION BY (Date, timestamp)
            ORDER BY (Id, Ids[1], originIds[1], timestamp)
            TTL Date TO VOLUME 'volume0',
            Date + INTERVAL 1 HOUR TO VOLUME 'volume1'""" + ("""
            Date + INTERVAL 4 HOUR DELETE""" if ttl_delete else "") +
            f"""
            SETTINGS storage_policy = '{storage_policy}'
            ,merge_with_ttl_timeout = 1"""
            )

        yield

    finally:
        with Finally("I remove the table", flags=TE):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep
def create_acceptance_table_with_column_ttl(
    self, table_name="acceptance_table", node=None
):
    """Creating acceptance table with column ttl"""
    if node is None:
        node = self.context.node

    try:
        with Given(f"I have acceptance table with tiered storage ttl"):
            node.query(
                f"""CREATE TABLE {table_name} (
              Date DateTime,
              timestamp UInt32,
              version LowCardinality(String),
              remoteIP String,
              clientIP String,
              Id UInt64 DEFAULT CAST(0, 'UInt64'),
              originIds Array(UInt64),
              Ids Array(UInt64),
              str String,
              str_arr Array(String),
              a UInt8,
              b UInt16 DEFAULT 777 TTL Date + INTERVAL 1 HOUR,
              c UInt16,
              int_arr Array(UInt32),
            )"""
                + """
            ENGINE = MergeTree()
            PARTITION BY (Date, timestamp)
            ORDER BY (Id, Ids[1], originIds[1], timestamp)"""
            )

        yield

    finally:
        with Finally("I remove the table", flags=TE):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep(Given)
def create_directory(self, path, node=None):
    """Creating directory on node"""
    if node is None:
        node = self.context.node
    try:
        node.command(f"mkdir '{path}'", exitcode=0)
        yield path
    finally:
        with Finally("delete directory", description=f"{path}"):
            node.command(f"rm -rf '{path}'", exitcode=0)


@TestStep(Given)
def create_directories_multi_disk_volume(self, number_of_disks):
    with Given("I create local disk folders on the server"):
        for i in range(number_of_disks):
            create_directory(path=f"disk_local{i}/")


@TestStep(Given)
def add_config_multi_disk_volume(self, number_of_disks):
    entries = {
        "storage_configuration": {
            "disks": [],
            "policies": {"local": {"volumes": {"volume1": []}}},
        }
    }

    with Given("I set up parameters"):
        entries_in_this_test = deepcopy(entries)
        for i in range(number_of_disks):

            entries_in_this_test["storage_configuration"]["disks"].append(
                {f"local{i}": {"path": f"/disk_local{i}/"}}
            )

            entries_in_this_test["storage_configuration"]["policies"]["local"][
                "volumes"
            ]["volume1"].append({"disk": f"local{i}"})

    with And("I add storage configuration that uses disk"):
        add_disk_configuration(entries=entries_in_this_test, restart=True)


@TestStep(Given)
def add_disk_configuration(
    self, entries, xml_symbols=True, modify=False, restart=True, format=None, user=None
):
    """Create disk configuration file and add it to the server."""
    with By("converting config file content to xml"):
        config = create_xml_config_content(entries, "storage_conf.xml")
        if format is not None:
            for key, value in format.items():
                if xml_symbols:
                    config.content = config.content.replace(key, xml_escape(value))
                else:
                    config.content = config.content.replace(key, value)
    with And("adding xml config file to the server"):
        return add_config(config, restart=restart, modify=modify, user=user)


@TestStep(Given)
def insert_ontime_data(self, year, node=None):
    """Insert data into ontime table from s3 disk with specified year"""

    if node is None:
        node = self.context.node

    node.query(
        f"INSERT INTO ontime SELECT * FROM s3('https://clickhouse-public-datasets.s3.amazonaws.com/ontime/csv_by_year/{year}.csv.gz', CSVWithNames) SETTINGS max_insert_threads = 40;"
    )


@TestStep(Given)
def add_ontime_table(self, from_year=1990, to_year=1991, node=None):
    """Download ontime table into clickhouse dataset from s3 disk."""
    if node is None:
        node = self.context.node

    try:
        with Given(f"I have ontime table"):
            node.query(
                """CREATE TABLE `ontime`
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
  ORDER BY (Year, Quarter, Month, DayofMonth, FlightDate, IATA_CODE_Reporting_Airline);"""
            )
            with When("I insert data into the ontime table in parallel"):
                for year in range(from_year, to_year):
                    Step(
                        name="insert 1 year into ontime table",
                        test=insert_ontime_data,
                        parallel=True,
                    )(year=year)

                join()
        yield

    finally:
        with Finally("I remove the table", flags=TE):
            node.query(f"DROP TABLE IF EXISTS ontime SYNC")


@TestStep(Given)
def create_acceptance_table(
    self, storage_policy=None, table_name="acceptance_table", node=None
):
    """Creating acceptance table."""
    if node is None:
        node = self.context.node
    try:
        with Given(f"I have acceptance table"):
            node.query(
                f"""CREATE TABLE {table_name} (
              Date DateTime,
              timestamp UInt32,
              version LowCardinality(String),
              remoteIP String,
              clientIP String,
              Id UInt64 DEFAULT CAST(0, 'UInt64'),
              originIds Array(UInt64),
              Ids Array(UInt64),
              str String,
              str_arr Array(String),
              a UInt8,
              b UInt16,
              c UInt16,
              int_arr Array(UInt32),
            )"""
                + """
            ENGINE = MergeTree()
            PARTITION BY (Date, timestamp)
            ORDER BY (Id, Ids[1], originIds[1], timestamp)"""
                + (
                    ""
                    if storage_policy is None
                    else f"""
            SETTINGS storage_policy = '{storage_policy}'"""
                )
            )

        yield

    finally:
        with Finally("I remove the table", flags=TE):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep(Given)
def insert_into_acceptance_table(
    self, table_name="acceptance_table", rows_number=100, node=None
):
    """Insert into acceptance table rows_number random rows."""
    if node is None:
        node = self.context.node

    node.query(
        f"""insert into {table_name} select (now() - 30*60*(Date%10)), 1,
              version,remoteIP,clientIP,
              (Id % 10), [(originIds[1] % 10)],[(Ids[1] % 10)],
              str, str_arr,
              a, b,
              c,[(int_arr[1] % 10)]
              from generateRandom('Date UInt16,
              timestamp UInt32,
              version String,
              remoteIP String,
              clientIP String,
              serverIP String,
              Id UInt64,
              originIds Array(UInt64),
              Ids Array(UInt64),
              str String,
              str_arr Array(String),
              a UInt8,
              b UInt16,
              c UInt16,
              int_arr Array(UInt32)', 1, 1, 1) limit {rows_number}"""
    )


@TestStep(Given)
def create_partitioned_table(
    self,
    table_name,
    extra_table_col="",
    cluster="",
    engine="MergeTree",
    partition="PARTITION BY id",
    order="ORDER BY id",
    settings="",
    node=None,
    options="",
):
    """Create a partitioned table."""
    if node is None:
        node = self.context.node

    try:
        with Given(f"I have a table {table_name}"):
            node.query(
                f"CREATE TABLE {table_name} {cluster} (id Int64, x Int64{extra_table_col})"
                f" Engine = {engine} {partition} {order} {options} {settings}"
            )

        yield

    finally:
        with Finally("I remove the table", flags=TE):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep(When)
def create_replacing_merge_tree_table(
    self, table_name, node=None, settings="", options=""
):
    """Create replacing merge tree table."""

    create_partitioned_table(
        table_name=table_name,
        engine="ReplacingMergeTree()",
        node=node,
        settings=settings,
        options=options,
    )


@TestStep(When)
def create_summing_merge_tree_table(
    self, table_name, node=None, settings="", options=""
):
    """Create summing merge tree table."""

    create_partitioned_table(
        table_name=table_name,
        engine="SummingMergeTree(x)",
        node=node,
        settings=settings,
        options=options,
    )


@TestStep(When)
def create_aggregating_merge_tree_table(
    self, table_name, node=None, settings="", options=""
):
    """Create aggregating merge tree table."""

    create_partitioned_table(
        table_name=table_name,
        engine="AggregatingMergeTree()",
        node=node,
        settings=settings,
        options=options,
    )


@TestStep(When)
def create_collapsing_merge_tree_table(
    self, table_name, node=None, settings="", options=""
):
    """Create collapsing merge tree table."""

    create_partitioned_table(
        table_name=table_name,
        extra_table_col=" ,Sign Int8",
        engine="CollapsingMergeTree(Sign)",
        node=node,
        settings=settings,
        options=options,
    )


@TestStep(When)
def create_versioned_collapsing_merge_tree_table(
    self, table_name, node=None, settings="", options=""
):
    """Create versioned collapsing merge tree table."""

    create_partitioned_table(
        table_name=table_name,
        extra_table_col=" ,Sign Int8",
        engine="VersionedCollapsingMergeTree(Sign, id)",
        node=node,
        settings=settings,
        options=options,
    )


@TestStep(When)
def create_graphite_merge_tree_table(
    self, table_name, node=None, settings="", options=""
):
    """Create graphite merge tree table."""

    create_partitioned_table(
        table_name=table_name,
        extra_table_col=" ,Path String, Time DateTime, Value Int64, Timestamp Int64",
        engine="GraphiteMergeTree('graphite_rollup_example')",
        node=node,
        settings=settings,
        options=options,
    )


@TestStep(When)
def create_replicated_table(self, table_name):
    """Create replicated table with 3 replicas."""

    with Given(
        "I create replicated table on cluster",
        description="""
            Using the following cluster configuration containing 1 shard with 3 replicas:
                shard0: 
                    replica0: clickhouse1
                    replica1: clickhouse2
                    replica2: clickhouse3
            """,
    ):
        for i, name in enumerate(self.context.cluster.nodes["clickhouse"]):
            node = self.context.cluster.node(name)
            self.context.node = node
            create_partitioned_table(
                node=node,
                table_name=table_name,
                engine=f"ReplicatedMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica{i}')",
            )


@TestStep(When)
def create_replicated_replacing_merge_tree_table(self, table_name):
    """Create replicated table with 3 replicas."""

    with Given(
        "I create replicated replacing merge tree table on cluster",
        description="""
            Using the following cluster configuration containing 1 shard with 3 replicas:
                shard0: 
                    replica0: clickhouse1
                    replica1: clickhouse2
                    replica2: clickhouse3
            """,
    ):
        for i, name in enumerate(self.context.cluster.nodes["clickhouse"]):
            node = self.context.cluster.node(name)
            self.context.node = node
            create_partitioned_table(
                node=node,
                table_name=table_name,
                engine=f"ReplicatedReplacingMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica{i}')",
            )


@TestStep(When)
def create_replicated_summing_merge_tree_table(self, table_name):
    """Create replicated table with 3 replicas."""

    with Given(
        "I create replicated summing merge tree table on cluster",
        description="""
            Using the following cluster configuration containing 1 shard with 3 replicas:
                shard0: 
                    replica0: clickhouse1
                    replica1: clickhouse2
                    replica2: clickhouse3
            """,
    ):
        for i, name in enumerate(self.context.cluster.nodes["clickhouse"]):
            node = self.context.cluster.node(name)
            self.context.node = node
            create_partitioned_table(
                node=node,
                table_name=table_name,
                engine=f"ReplicatedSummingMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica{i}', x)",
            )


@TestStep(When)
def create_replicated_aggregating_merge_tree_table(self, table_name):
    """Create replicated table with 3 replicas."""

    with Given(
        "I create replicated aggregating merge tree table on cluster",
        description="""
            Using the following cluster configuration containing 1 shard with 3 replicas:
                shard0: 
                    replica0: clickhouse1
                    replica1: clickhouse2
                    replica2: clickhouse3
            """,
    ):
        for i, name in enumerate(self.context.cluster.nodes["clickhouse"]):
            node = self.context.cluster.node(name)
            self.context.node = node
            create_partitioned_table(
                node=node,
                table_name=table_name,
                engine=f"ReplicatedAggregatingMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica{i}')",
            )


@TestStep(When)
def create_replicated_collapsing_merge_tree_table(self, table_name):
    """Create replicated table with 3 replicas."""

    with Given(
        "I create replicated collapsing merge tree table on cluster",
        description="""
            Using the following cluster configuration containing 1 shard with 3 replicas:
                shard0: 
                    replica0: clickhouse1
                    replica1: clickhouse2
                    replica2: clickhouse3
            """,
    ):
        for i, name in enumerate(self.context.cluster.nodes["clickhouse"]):
            node = self.context.cluster.node(name)
            self.context.node = node
            create_partitioned_table(
                node=node,
                table_name=table_name,
                extra_table_col=" ,Sign Int8",
                engine=f"ReplicatedCollapsingMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica{i}', Sign)",
            )


@TestStep(When)
def create_replicated_versioned_collapsing_merge_tree_table(self, table_name):
    """Create replicated table with 3 replicas."""

    with Given(
        "I create replicated versioned collapsing merge tree table on cluster",
        description="""
            Using the following cluster configuration containing 1 shard with 3 replicas:
                shard0: 
                    replica0: clickhouse1
                    replica1: clickhouse2
                    replica2: clickhouse3
            """,
    ):
        for i, name in enumerate(self.context.cluster.nodes["clickhouse"]):
            node = self.context.cluster.node(name)
            self.context.node = node
            create_partitioned_table(
                node=node,
                table_name=table_name,
                extra_table_col=" ,Sign Int8",
                engine=f"ReplicatedVersionedCollapsingMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica{i}', Sign, id)",
            )


@TestStep(When)
def create_replicated_graphite_merge_tree_table(self, table_name):
    """Create replicated table with 3 replicas."""

    with Given(
        "I create replicated graphite merge tree table on cluster",
        description="""
            Using the following cluster configuration containing 1 shard with 3 replicas:
                shard0: 
                    replica0: clickhouse1
                    replica1: clickhouse2
                    replica2: clickhouse3
            """,
    ):
        for i, name in enumerate(self.context.cluster.nodes["clickhouse"]):
            node = self.context.cluster.node(name)
            self.context.node = node
            create_partitioned_table(
                table_name=table_name,
                extra_table_col=" ,Path String, Time DateTime, Value Int64, Timestamp Int64",
                engine=f"ReplicatedGraphiteMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica{i}', 'graphite_rollup_example')",
                node=node,
            )


@TestStep(When)
def insert(
    self,
    table_name,
    values=None,
    partitions=1,
    parts_per_partition=1,
    block_size=1000,
    no_checks=False,
    settings=[],
    node=None,
    table_engine=None,
):
    """Insert data having specified number of partitions and parts."""
    if node is None:
        node = self.context.node

    if table_engine is None:
        table_engine = self.context.table_engine

    if values is None:
        if table_engine in ("CollapsingMergeTree", "VersionedCollapsingMergeTree"):
            values = ",".join(
                f"({x},{y},1)"
                for x in range(partitions)
                for y in range(block_size * parts_per_partition)
            )

        elif table_engine == "GraphiteMergeTree":
            values = ",".join(
                f"({x},{y}, '1', toDateTime(10), 10, 10)"
                for x in range(partitions)
                for y in range(block_size * parts_per_partition)
            )
        else:
            values = ",".join(
                f"({x},{y})"
                for x in range(partitions)
                for y in range(block_size * parts_per_partition)
            )

    return node.query(
        f"INSERT INTO {table_name} VALUES {values}",
        settings=[("max_block_size", block_size)] + settings,
        no_checks=no_checks,
    )


@TestStep(When)
def insert_replicated(
    self,
    table_name,
    values=None,
    partitions=1,
    parts_per_partition=1,
    block_size=1000,
    settings=[],
    table_engine=None,
):
    """Insert data into replicated table."""

    if table_engine is None:
        table_engine = self.context.table_engine

    with When(f"I insert into table on clickhouse1 node"):
        name = "clickhouse1"
        self.context.node = node = self.context.cluster.node(name)
        with When(f"I insert into table on {name} node"):
            insert(
                table_name=table_name,
                values=values,
                partitions=partitions,
                parts_per_partition=parts_per_partition,
                block_size=block_size,
                table_engine=table_engine[10:],
                settings=[("insert_distributed_sync", "1")] + settings,
            )


@TestStep(When)
def delete(
    self,
    table_name,
    condition,
    use_alter_delete=False,
    optimize=True,
    no_checks=False,
    check=False,
    delay=0,
    settings=[("mutations_sync", 2)],
    node=None,
    multiple=False,
):
    """Delete rows from table that match the condition."""
    if node is None:
        node = self.context.node

    if use_alter_delete or self.context.use_alter_delete:
        if multiple:
            command = ";".join(
                [f"ALTER TABLE {table_name} DELETE WHERE {i}" for i in condition]
            )
        else:
            command = f"ALTER TABLE {table_name} DELETE WHERE {condition}"
        r = node.query(command, no_checks=no_checks, settings=settings)
        if check:
            for attempt in retries(delay=0.1, timeout=600):
                with attempt:
                    with Then("I check rows are deleted"):
                        check_result = node.query(
                            f"SELECT count() FROM {table_name} WHERE {condition}"
                        )
                        assert check_result.output == "0", error()
        if delay:
            time.sleep(delay)
        return r
    # FIXME: change to DELETE when there is actual implementation
    if multiple:
        command = ";".join([f"DELETE FROM {table_name} WHERE {i}" for i in condition])
    else:
        command = f"DELETE FROM {table_name} WHERE {condition}"
    r = node.query(command, no_checks=no_checks, settings=settings)
    if check:
        for attempt in retries(delay=0.1, timeout=30):
            with attempt:
                with Then("I check rows are deleted"):
                    check_result = node.query(
                        f"SELECT count() FROM {table_name} WHERE {condition}"
                    )
                    assert check_result.output == "0", error()
    if delay:
        time.sleep(delay)
    return r


@TestStep(When)
def optimize_table(self, table_name, final=True, node=None):
    """Force merging of some (final=False) or all parts (final=True)
    by calling OPTIMIZE TABLE.
    """
    if node is None:
        node = self.context.node

    query = f"OPTIMIZE TABLE {table_name}"
    if final:
        query += " FINAL"

    return node.query(query)


@TestStep(Given)
def stop_merges(self, node=None):
    """Stop merges."""
    if node is None:
        node = self.context.node
    try:
        node.query("SYSTEM STOP MERGES")
        yield
    finally:
        with Finally("I restart merges"):
            node.query("SYSTEM START MERGES")


@TestStep
def delete_odd(
    self, num_partitions, table_name, settings=[("mutations_sync", 2)], node=None
):
    """Delete all odd `x` rows in all partitions."""
    for i in range(num_partitions):
        delete(
            table_name=table_name,
            condition=f" (id = {i}) AND (x % 2 = 0)",
            delay=random.random() / 10,
            settings=settings,
            node=node,
        )


@TestStep
def alter_detach_partition(
    self, table_name, partition_expr="7", node=None, settings=[("mutations_sync", 2)], quote=True,
):
    if node is None:
        node = self.context.node

    if quote:
        node.query(
            f"ALTER TABLE {table_name} DETACH PARTITION '{partition_expr}'",
            settings=settings,
        )
    else:
        node.query(
            f"ALTER TABLE {table_name} DETACH PARTITION {partition_expr}",
            settings=settings,
        )

@TestStep
def alter_drop_partition(
    self, table_name, partition_expr="10", node=None, settings=[("mutations_sync", 2)], quote=True,
):
    if node is None:
        node = self.context.node

    if quote:
        node.query(
            f"ALTER TABLE {table_name} DROP PARTITION '{partition_expr}'", settings=settings
        )
    else:
        node.query(
            f"ALTER TABLE {table_name} DROP PARTITION {partition_expr}", settings=settings
        )

@TestStep
def alter_drop_detached_partition(
    self, table_name, partition_expr, node=None, settings=[("mutations_sync", 2)], quote=True,
):
    if node is None:
        node = self.context.node

    if quote:
        node.query(
            f"ALTER TABLE {table_name} DROP DETACHED PARTITION '{partition_expr}'",
            settings=settings,
        )
    else:
        node.query(
            f"ALTER TABLE {table_name} DROP DETACHED PARTITION {partition_expr}",
            settings=settings,
        )

@TestStep
def alter_attach_partition(
    self, table_name, partition_expr="7", node=None, settings=[("mutations_sync", 2)], quote=True,
):
    if node is None:
        node = self.context.node

    if quote:
        node.query(
            f"ALTER TABLE {table_name} ATTACH PARTITION '{partition_expr}'",
            settings=settings,
        )
    else:
        node.query(
            f"ALTER TABLE {table_name} ATTACH PARTITION {partition_expr}",
            settings=settings,
        )

@TestStep
def alter_replace_partition(
    self,
    table_name_2,
    table_name_1,
    partition_expr,
    node=None,
    settings=[("mutations_sync", 2)], quote=True,
):
    if node is None:
        node = self.context.node

    if quote:
        node.query(
            f"ALTER TABLE {table_name_2} REPLACE PARTITION '{partition_expr}' FROM {table_name_1}",
            settings=settings,
        )
    else:
        node.query(
            f"ALTER TABLE {table_name_2} REPLACE PARTITION {partition_expr} FROM {table_name_1}",
            settings=settings,
        )

@TestStep
def alter_fetch_partition(
    self, table_name, partition_expr, path, node=None, settings=[("mutations_sync", 2)], quote=True,
):
    if node is None:
        node = self.context.node

    if quote:
        node.query(
            f"ALTER TABLE {table_name} FETCH PARTITION '{partition_expr}' FROM '{path}'",
            settings=settings,
        )
    else:
        node.query(
            f"ALTER TABLE {table_name} FETCH PARTITION {partition_expr} FROM '{path}'",
            settings=settings,
        )


@TestStep
def alter_move_partition(
    self,
    table_name_1,
    table_name_2,
    partition_expr,
    node=None,
    settings=[("mutations_sync", 2)], quote=True,
):
    if node is None:
        node = self.context.node

    if quote:
        node.query(
            f"ALTER TABLE {table_name_1} MOVE PARTITION '{partition_expr}' to TABLE {table_name_2}",
            settings=settings,
        )
    else:
        node.query(
            f"ALTER TABLE {table_name_1} MOVE PARTITION {partition_expr} to TABLE {table_name_2}",
            settings=settings,
        )

@TestStep
def alter_freeze_partition(
    self, table_name, partition_expr="9", node=None, settings=[("mutations_sync", 2)], quote=True,
):
    if node is None:
        node = self.context.node

    if quote:
        node.query(
            f"ALTER TABLE {table_name} FREEZE PARTITION '{partition_expr}'",
            settings=settings,
        )
    else:
        node.query(
            f"ALTER TABLE {table_name} FREEZE PARTITION {partition_expr}",
            settings=settings,
        )

@TestStep
def alter_unfreeze_partition(
    self, table_name, partition_expr="9", node=None, settings=[("mutations_sync", 2)], quote=True,
):
    if node is None:
        node = self.context.node

    if quote:
        node.query(
            f"ALTER TABLE {table_name} UNFREEZE PARTITION '{partition_expr}' WITH NAME 'backup_name'",
            settings=settings,
        )
    else:
        node.query(
            f"ALTER TABLE {table_name} UNFREEZE PARTITION {partition_expr} WITH NAME 'backup_name'",
            settings=settings,
        )

@TestStep
def alter_update_in_partition(
    self,
    table_name,
    update_expr="x=10",
    partition_expr="WHERE true",
    node=None,
    settings=[("mutations_sync", 2)],
):
    if node is None:
        node = self.context.node

    node.query(
        f"ALTER TABLE {table_name} UPDATE {update_expr} {partition_expr}",
        settings=settings,
    )


@TestStep
def alter_delete_in_partition(
    self,
    table_name,
    partition_expr="11",
    where_expr="WHERE x > -1",
    node=None,
    settings=[("mutations_sync", 2)], quote=True,
):
    if node is None:
        node = self.context.node

    if quote:
        node.query(
            f"ALTER TABLE {table_name} DELETE IN PARTITION '{partition_expr}' {where_expr}",
            settings=settings,
        )
    else:
        node.query(
            f"ALTER TABLE {table_name} DELETE IN PARTITION {partition_expr} {where_expr}",
            settings=settings,
        )

@TestStep
def alter_add_column(
    self,
    table_name,
    column_name="qkrq",
    column_type="Int32",
    default_expr="",
    node=None,
    settings=[("mutations_sync", 2)],
):
    if node is None:
        node = self.context.node

    node.query(
        f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type} {default_expr} FIRST ",
        settings=settings,
    )


@TestStep
def alter_drop_column(
    self, table_name, column_name="qkrq", node=None, settings=[("mutations_sync", 2)],
):
    if node is None:
        node = self.context.node

    node.query(
        f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name}",
        settings=settings,
    )


@TestStep
def alter_clear_column(
    self,
    table_name,
    column_name="qkrq",
    partition_expr="",
    node=None,
    settings=[("mutations_sync", 2)],
):
    if node is None:
        node = self.context.node

    node.query(
        f"ALTER TABLE {table_name} CLEAR COLUMN IF EXISTS {column_name} {partition_expr}",
        settings=settings,
    )


@TestStep
def alter_comment_column(
    self,
    table_name,
    column_name="x",
    column_comment="some comment",
    node=None,
    settings=[("mutations_sync", 2)],
):
    if node is None:
        node = self.context.node

    node.query(
        f"ALTER TABLE {table_name} COMMENT COLUMN {column_name} '{column_comment}'",
        settings=settings,
    )


@TestStep
def alter_modify_column(
    self,
    table_name,
    column_name="qkrq",
    column_type="Int32",
    default_expr="DEFAULT 48",
    node=None,
    settings=[("mutations_sync", 2)]
):
    if node is None:
        node = self.context.node

    node.query(
        f"ALTER TABLE {table_name} MODIFY COLUMN IF EXISTS {column_name} {column_type} {default_expr}",
        settings=settings,
    )


@TestStep(Then)
def detach_partition_after_delete_in_the_table(
    self,
    table_name,
    partitions=10,
    partition_expr="3",
    nodes=["clickhouse1"],
    node=None,
):
    """Check that detach partition after lightweight delete perform correctly when table already exists."""

    if node is None:
        node = self.context.node

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0 or id = {partition_expr})"
        ).output

    with Then("I delete odd rows from the table"):
        delete_odd(num_partitions=partitions, table_name=table_name)

    with Then("I detach third partition"):
        alter_detach_partition(
            table_name=table_name, partition_expr=partition_expr, node=node
        )

    with Then("I check that data is deleted from all nodes"):
        for name in nodes:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully deleted on {name} node"):
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == output, error()


@TestStep(Then)
def drop_partition_after_delete_in_the_table(
    self,
    table_name,
    partitions=10,
    partition_expr="3",
    nodes=["clickhouse1"],
    node=None,
):
    """Check that drop partition after lightweight delete perform correctly when table already exists."""
    if node is None:
        node = self.context.node

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0 or id = {partition_expr})"
        ).output

    with Then("I delete odd rows from the table"):
        delete_odd(num_partitions=partitions, table_name=table_name)

    with Then("I drop third partition"):
        alter_drop_partition(
            table_name=table_name, partition_expr=partition_expr, node=node
        )

    with Then("I check that data is deleted from all nodes"):
        for name in nodes:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully deleted on {name} node"):
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == output, error()


@TestStep(Then)
def attach_partition_after_delete_in_the_table(
    self,
    table_name,
    partitions=10,
    partition_expr="3",
    nodes=["clickhouse1"],
    node=None,
):
    """Check that attach partition after lightweight delete perform correctly when table already exists."""
    if node is None:
        node = self.context.node

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0 and id != {partition_expr})"
        ).output

    with When("I detach partition"):
        alter_detach_partition(
            table_name=table_name, partition_expr=partition_expr, node=node
        )

    with Then("I delete odd rows from the table"):
        delete_odd(num_partitions=partitions, table_name=table_name)

    with Then("I attach third partition"):
        alter_attach_partition(
            table_name=table_name, partition_expr=partition_expr, node=node
        )

    with Then("I check that data is deleted from all nodes"):
        for name in nodes:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully deleted on {name} node"):
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == output, error()


@TestStep(Then)
def freeze_partition_after_delete_in_the_table(
    self,
    table_name,
    partitions=10,
    partition_expr="3",
    nodes=["clickhouse1"],
    node=None,
):
    """Check that freeze partition after lightweight delete perform correctly when table already exists."""
    if node is None:
        node = self.context.node

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0)"
        ).output

    with Then("I delete odd rows from the table"):
        delete_odd(num_partitions=partitions, table_name=table_name)

    with Then("I freeze third partition"):
        alter_freeze_partition(
            table_name=table_name, partition_expr=partition_expr, node=node
        )

    with Then("I check that data is deleted from all nodes"):
        for name in nodes:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully deleted on {name} node"):
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == output, error()


@TestStep(Then)
def unfreeze_partition_after_delete_in_the_table(
    self,
    table_name,
    partitions=10,
    partition_expr="3",
    nodes=["clickhouse1"],
    node=None,
):
    """Check that unfreeze partition after lightweight delete perform correctly when table already exists."""
    if node is None:
        node = self.context.node

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0)"
        ).output

    with Then("I freeze third partition"):
        alter_freeze_partition(
            table_name=table_name, partition_expr=partition_expr, node=node
        )

    with Then("I delete odd rows from the table"):
        delete_odd(num_partitions=partitions, table_name=table_name)

    with Then("I unfreeze third partition"):
        alter_unfreeze_partition(
            table_name=table_name, partition_expr=partition_expr, node=node
        )

    with Then("I check that data is deleted from all nodes"):
        for name in nodes:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully deleted on {name} node"):
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == output, error()


@TestStep(Then)
def add_column_after_delete_in_the_table(
    self,
    table_name,
    partitions=10,
    column_name="added_column",
    column_type="UInt32",
    default_expr="DEFAULT 7",
    output="500",
    nodes=["clickhouse1"],
    node=None,
):
    """Check that add column after lightweight delete perform correctly when table already exists."""
    if node is None:
        node = self.context.node

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0)"
        ).output

    with When("I delete odd rows from the table"):
        delete_odd(num_partitions=partitions, table_name=table_name)

    with And("I add column", description="name=added_column type=UInt32 default=7"):
        alter_add_column(
            table_name=table_name,
            column_name=column_name,
            column_type=column_type,
            default_expr=default_expr,
            node=node,
        )

    with Then("I check that data is deleted from all nodes"):
        for name in nodes:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully deleted on {name} node"):
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == output, error()


@TestStep(Then)
def drop_column_after_delete_in_the_table(
    self, table_name, partitions=10, column_name="x", nodes=["clickhouse1"], node=None
):
    """Check that drop column after lightweight delete perform correctly when table already exists."""
    if node is None:
        node = self.context.node

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0)"
        ).output

    with When("I delete odd rows from the table"):
        delete_odd(num_partitions=partitions, table_name=table_name)

    with And("I drop column", description="name=x"):
        alter_drop_column(table_name=table_name, column_name=column_name, node=node)

    with Then("I check that data is deleted from all nodes"):
        for name in nodes:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully deleted on {name} node"):
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == output, error()


@TestStep(Then)
def clear_column_after_delete_in_the_table(
    self, table_name, partitions=10, column_name="x", nodes=["clickhouse1"], node=None
):
    """Check that clear column after lightweight delete perform correctly when table already exists."""
    if node is None:
        node = self.context.node

    with When("I compute expected output"):
        output1 = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0 or id != 0)"
        ).output
        output2 = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0)"
        ).output

    with When("I delete odd rows from the table"):
        delete_odd(num_partitions=partitions, table_name=table_name)

    with And("I clear column", description="name=x"):
        alter_clear_column(
            table_name=table_name,
            column_name=column_name,
            partition_expr="IN PARTITION 0",
            node=node,
        )

    with Then("I check that data is deleted from all nodes"):
        for name in nodes:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully deleted on {name} node"):
                r = node.query(f"SELECT count() FROM {table_name} where x=0")
                assert r.output == output1, error()
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == output2, error()


@TestStep(Then)
def modify_column_after_delete_in_the_table(
    self,
    table_name,
    partitions=10,
    column_name="x",
    column_type="String",
    default_expr="DEFAULT '777'",
    nodes=["clickhouse1"],
    node=None,
):
    """Check that modify column after lightweight delete perform correctly when table already exists."""
    if node is None:
        node = self.context.node

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0)"
        ).output

    with When("I delete odd rows from the table"):
        delete_odd(num_partitions=partitions, table_name=table_name)

    with And(
        "I modify column",
        description=f"name={column_name}, type={column_type}, {default_expr}",
    ):
        alter_modify_column(
            table_name=table_name,
            column_name=column_name,
            column_type=column_type,
            default_expr=default_expr,
            node=node,
        )

    with Then("I check that data is deleted from all nodes"):
        for name in nodes:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully deleted on {name} node"):
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == output, error()


@TestStep(Then)
def comment_column_after_delete_in_the_table(
    self,
    table_name,
    partitions=10,
    column_name="x",
    column_comment="hello",
    nodes=["clickhouse1"],
    node=None,
):
    """Check that comment column after lightweight delete perform correctly when table already exists."""

    if node is None:
        node = self.context.node

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM {table_name} WHERE NOT(x % 2 == 0)"
        ).output

    with When("I delete odd rows from the table"):
        delete_odd(num_partitions=partitions, table_name=table_name)

    with And("I comment column", description="name=x, type=String, DEFAULT '777'"):
        alter_comment_column(
            table_name=table_name,
            column_name=column_name,
            column_comment=column_comment,
            node=node,
        )

    with Then("I check that data is deleted from all nodes"):
        for name in nodes:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully deleted on {name} node"):
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == output, error()


@TestStep
def delete_in_loop(self, table_name, condition, partitions=10, node=None):
    """Delete in loop by partitions."""
    for partition in range(partitions):
        delete(
            table_name=table_name,
            condition=condition + f" AND id = {partition}",
            node=node,
        )


@TestStep(When)
def create_and_check_replicated_table(
    self, table_name, partitions=10, parts_per_partition=1, block_size=100
):
    """Create replicated table with 3 replicas and insert into it."""
    create_replicated_table(table_name=table_name)

    with Then("I expect i can select from replicated table on any node"):
        for name in self.context.cluster.nodes["clickhouse"]:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully inserted on {name} node"):
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert r.output == str(partitions * block_size), error()


@TestStep
def clear_update_in_loop(
    self, table_name, column_name, iterations=10, delay=0.6, node=None
):
    """Run clear column update column statements in a loop."""
    for i in range(iterations):
        alter_clear_column(table_name=table_name, column_name=column_name, node=node)
        time.sleep(delay / 2)
        alter_update_in_partition(
            table_name=table_name, update_expr=f"{column_name} = 777", node=node
        )
        time.sleep(delay / 2)


@TestStep
def modify_column_in_loop(
    self, table_name, column_name, iterations=10, delay=0.6, node=None
):
    """Run modify column statements in a loop."""
    for i in range(iterations):
        alter_modify_column(
            table_name=table_name,
            column_name=column_name,
            column_type="String",
            node=node,
        )
        time.sleep(delay / 2)
        alter_modify_column(
            table_name=table_name,
            column_name=column_name,
            column_type="Int32",
            node=node,
        )
        time.sleep(delay / 2)


@TestStep
def add_drop_column_in_loop(
    self,
    table_name,
    column_name,
    column_type,
    default_expr,
    iterations=10,
    delay=0.6,
    node=None,
):
    """Run add column drop column statements in a loop."""
    for i in range(iterations):
        alter_add_column(
            table_name=table_name,
            column_name=column_name,
            column_type=column_type,
            default_expr=default_expr,
            node=node,
        )
        time.sleep(delay / 2)
        alter_drop_column(table_name=table_name, column_name=column_name, node=node)
        time.sleep(delay / 2)


@TestStep
def attach_detach_in_loop(
    self, table_name, partition_expr, iterations=10, delay=0.6, node=None, quote=True
):
    """Run detach attach statements in a loop for given partition expression."""
    for i in range(iterations):
        alter_detach_partition(
            table_name=table_name, partition_expr=partition_expr, node=node, quote=quote
        )
        time.sleep(delay / 2)
        alter_attach_partition(
            table_name=table_name, partition_expr=partition_expr, node=node, quote=quote
        )
        time.sleep(delay / 2)


@TestStep(Then)
def check_query_on_all_nodes(self, query, output):
    """Run query on all nodes and compare its result with `output`"""
    for name in self.context.cluster.nodes["clickhouse"]:
        node = self.context.cluster.node(name)
        self.context.node = node
        with Then(f"I expect data is correct on {name} node"):
            r = node.query(query)
            assert r.output == output, error()


@TestStep(When)
def create_table(self, table_name, table_engine=None, settings="", options=""):
    """Create table with engine specifying."""
    if table_engine is None:
        table_engine = self.context.table_engine

    if table_engine == "MergeTree":
        create_partitioned_table(
            table_name=table_name, settings=settings, options=options
        )

    if table_engine == "ReplacingMergeTree":
        create_replacing_merge_tree_table(
            table_name=table_name, settings=settings, options=options
        )

    if table_engine == "SummingMergeTree":
        create_summing_merge_tree_table(
            table_name=table_name, settings=settings, options=options
        )

    if table_engine == "AggregatingMergeTree":
        create_aggregating_merge_tree_table(
            table_name=table_name, settings=settings, options=options
        )

    if table_engine == "CollapsingMergeTree":
        create_collapsing_merge_tree_table(
            table_name=table_name, settings=settings, options=options
        )

    if table_engine == "VersionedCollapsingMergeTree":
        create_versioned_collapsing_merge_tree_table(
            table_name=table_name, settings=settings, options=options
        )

    if table_engine == "GraphiteMergeTree":
        create_graphite_merge_tree_table(
            table_name=table_name, settings=settings, options=options
        )

    if table_engine == "ReplicatedMergeTree":
        create_replicated_table(table_name=table_name)

    if table_engine == "ReplicatedReplacingMergeTree":
        create_replicated_replacing_merge_tree_table(table_name=table_name)

    if table_engine == "ReplicatedSummingMergeTree":
        create_replicated_summing_merge_tree_table(table_name=table_name)

    if table_engine == "ReplicatedAggregatingMergeTree":
        create_replicated_aggregating_merge_tree_table(table_name=table_name)

    if table_engine == "ReplicatedCollapsingMergeTree":
        create_replicated_collapsing_merge_tree_table(table_name=table_name)

    if table_engine == "ReplicatedVersionedCollapsingMergeTree":
        create_replicated_versioned_collapsing_merge_tree_table(table_name=table_name)

    if table_engine == "ReplicatedGraphiteMergeTree":
        create_replicated_graphite_merge_tree_table(table_name=table_name)


@TestStep
def delete_query_1_ontime(self, settings=[], check=True, node=None):
    """Deleting All Rows In a Single Partition."""
    if node is None:
        node = self.context.node

    delete(table_name="ontime", condition="Year = 1990", settings=settings, check=check)


@TestStep
def delete_query_2_ontime(self, settings=[], check=True, node=None):
    """Delete All Rows In Various Partitions."""
    if node is None:
        node = self.context.node

    delete(table_name="ontime", condition="Year % 2 = 0", settings=settings, check=check)


@TestStep
def delete_query_3_ontime(self, settings=[], check=True, node=None):
    """Delete Some Rows In All Partitions (Large Granularity)."""
    if node is None:
        node = self.context.node

    delete(table_name="ontime", condition="Month = 2", settings=settings, check=check)


@TestStep
def delete_query_4_ontime(self, settings=[], check=True, node=None):
    """Delete Some Rows In All Partitions (Small Granularity)."""
    if node is None:
        node = self.context.node

    delete(table_name="ontime", condition="DayofMonth = 2", settings=settings, check=check)


@TestStep
def delete_query_5_ontime(self, settings=[], check=True, node=None):
    """Delete Some Rows In One Partition (Very Small Granularity)."""
    if node is None:
        node = self.context.node

    delete(table_name="ontime", condition="FlightDate = '2020-01-01'", settings=settings, check=check)


@TestStep
def delete_query_1_acceptance(self, settings=[], check=True, node=None):
    """Usable delete query 1."""
    if node is None:
        node = self.context.node

    delete(
        table_name="acceptance_table",
        condition="Id = 1 and has(Ids, 2)", settings=settings, check=check
    )


@TestStep
def delete_query_2_acceptance(self, settings=[], check=True, node=None):
    """Usable delete query 2."""
    if node is None:
        node = self.context.node

    delete(table_name="acceptance_table", condition="has(Ids, 1)", settings=settings, check=check)


@TestStep
def delete_query_3_acceptance(self, settings=[], check=True, node=None):
    """Usable delete query 1."""
    if node is None:
        node = self.context.node

    delete(table_name="acceptance_table", condition="has(int_arr, 1)", settings=settings, check=check)


@TestStep
def insert_query_ontime(self, number=3, node=None):
    """Insert into ontime table."""
    if node is None:
        node = self.context.node

    node.query(f"INSERT INTO ontime SELECT * FROM ontime WHERE Month = {number}")


@TestStep
def insert_query_acceptance(self, rows_number=1000, node=None):
    """Insert into acceptance_table table."""
    if node is None:
        node = self.context.node

    node.query(
        f"insert into acceptance_table select * from acceptance_table limit {rows_number}"
    )


@TestStep
def select_query_ontime(self, node=None):
    """Select from ontime table."""
    if node is None:
        node = self.context.node

    node.query(
        f"SELECT count(*) FROM (SELECT avg(c1) FROM (SELECT Year, Month, count(*) AS c1 FROM ontime GROUP BY Year, Month))"
    )


@TestStep
def select_query_acceptance(self, node=None):
    """Select from acceptance table."""
    if node is None:
        node = self.context.node

    node.query(
        f"SELECT count(*) FROM (SELECT * FROM acceptance_table where has(Ids, 1))"
    )


@TestStep(Given)
def create_view(self, view_type, view_name, condition, node=None):
    """Create view."""
    if node is None:
        node = self.context.node

    try:
        with Given("I create view"):
            if view_type == "LIVE":
                node.query(
                    f"CREATE {view_type} VIEW {view_name} as {condition}",
                    settings=[("allow_experimental_live_view", 1)],
                )
            elif view_type == "WINDOW":
                node.query(
                    f"CREATE {view_type} VIEW {view_name} as {condition}",
                    settings=[("allow_experimental_window_view", 1)],
                )
            else:
                node.query(f"CREATE {view_type} VIEW {view_name} as {condition}")

        yield
    finally:
        with Finally("I delete view"):
            node.query(f"DROP VIEW {view_name} SYNC")


@TestStep(Given)
def allow_experimental_lightweight_delete(self):
    """Enable lightweight delete setting."""
    setting = ("allow_experimental_lightweight_delete", 1)
    default_query_settings = None

    try:
        if check_clickhouse_version(">=22.3")(current()):
            with Given(
                "I add allow_experimental_lightweight_delete to the default query settings"
            ):
                default_query_settings = getsattr(
                    current().context, "default_query_settings", []
                )
                default_query_settings.append(setting)

        yield

    finally:
        if check_clickhouse_version(">=22.3")(current()):
            with Finally(
                "I remove allow_experimental_lightweight_delete from the default query settings"
            ):
                if default_query_settings:
                    try:
                        default_query_settings.pop(
                            default_query_settings.index(setting)
                        )
                    except ValueError:
                        pass


@TestStep
def inserts(self, table_name, inserts_number, delay=0):
    """A lot of inserts in cycle"""
    for i in range(inserts_number):
        insert(
            table_name=table_name, partitions=2, parts_per_partition=1, block_size=1000
        )
        time.sleep(delay)


@TestStep
def merges(self, table_name, merges_number, delay=0):
    """A lot of inserts in cycle"""
    for i in range(merges_number):
        optimize_table(table_name=table_name, final=True)
        time.sleep(delay)


@TestStep
def deletes(self, table_name, deletes_number, condition="id < 2", delay=0):
    """A lot of deletes in cycle"""
    for i in range(deletes_number):
        delete(table_name=table_name, condition=condition, settings=[])
        time.sleep(delay)
