from pandas import describe_option
from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *

from parquet.tests.steps.metadata_caching import *
from parquet.tests.steps.metadata_caching import settings as settings_for_select
from parquet.tests.steps.swarm import *
from alter.stress.tests.tc_netem import network_packet_delay

PATH1 = "location_1"
PATH2 = "location_2"


@TestStep(When)
def stop_swarm_1_node(self):
    """Stop clickhouse on node clickhouse-swarm-1"""

    node = self.context.swarm_nodes[0]
    node.stop_clickhouse(safe=False)


@TestStep(When)
def start_swarm_1_node(self):
    """Start clickhouse on node clickhouse-swarm-1"""

    node = self.context.swarm_nodes[0]
    node.start_clickhouse()


@TestStep(Given)
def select_parquet_from_iceberg_s3(
    self,
    node=None,
    statement="*",
    additional_settings=None,
    condition=None,
    cache_metadata=False,
    file_type="Parquet",
    path_glob="**",
):
    """Select metadata of the Parquet file from Iceberg on S3."""

    log_comment = "log_" + getuid()
    settings = f"optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}', use_hive_partitioning=1, object_storage_cluster='swarm', filesystem_cache_name = 'cache_for_s3', enable_filesystem_cache = 1"

    if node is None:
        node = self.context.node

    if cache_metadata:
        settings += ", input_format_parquet_use_metadata_cache=1"
    else:
        settings += ", input_format_parquet_use_metadata_cache=0"

    if additional_settings is not None:
        settings += f", {additional_settings}"

    if condition is None:
        condition = ""

    start_time = time.time()
    node.query(
        f"""SELECT {statement} FROM s3('{self.context.warehouse_uri}/{path_glob}/**.parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', {file_type}) {condition} SETTINGS {settings} FORMAT TabSeparated"""
    )
    execution_time = time.time() - start_time

    return execution_time, log_comment


@TestStep(Given)
def select_parquet_from_iceberg_s3_cluster_join(
    self,
    node=None,
    statement="*",
    additional_settings=None,
    condition=None,
    cache_metadata=False,
    file_type="Parquet",
    path_glob="**",
):
    """Select metadata of the Parquet file from Iceberg on S3."""

    log_comment = "log_" + getuid()
    settings = f"optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}', use_hive_partitioning=1, object_storage_cluster='swarm', filesystem_cache_name = 'cache_for_s3', enable_filesystem_cache = 1"

    if node is None:
        node = self.context.node

    if cache_metadata:
        settings += ", input_format_parquet_use_metadata_cache=1"
    else:
        settings += ", input_format_parquet_use_metadata_cache=0"

    if additional_settings is not None:
        settings += f", {additional_settings}"

    if condition is None:
        condition = ""

    start_time = time.time()
    node.query(
        f"""SELECT *, a.*, b.* FROM s3Cluster('swarm', 'http://minio:9000/warehouse/data/data/datetime_day=2019-08-09/**.parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', {file_type}) AS a FULL OUTER JOIN s3Cluster('swarm', 'http://minio:9000/warehouse/data/data/datetime_day=2019-08-07/**.parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', {file_type}) AS b ON a.bid = b.bid SETTINGS {settings} FORMAT TabSeparated
"""
    )

    execution_time = time.time() - start_time

    return execution_time, log_comment


@TestStep(Given)
def select_parquet_from_iceberg_s3_cluster(
    self,
    node=None,
    statement="*",
    additional_settings=None,
    condition=None,
    cache_metadata=False,
    file_type="Parquet",
    path_glob="**",
):
    """Select metadata of the Parquet file from Iceberg on s3Cluster."""

    log_comment = "log_" + getuid()
    settings = f"optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}', use_hive_partitioning=1, filesystem_cache_name = 'cache_for_s3', enable_filesystem_cache = 1"

    if node is None:
        node = self.context.node

    if cache_metadata:
        settings += ", input_format_parquet_use_metadata_cache=1"
    else:
        settings += ", input_format_parquet_use_metadata_cache=0"

    if additional_settings is not None:
        settings += f", {additional_settings}"

    if condition is None:
        condition = ""

    start_time = time.time()
    node.query(
        f"""SELECT {statement} FROM s3Cluster('swarm' ,'{self.context.warehouse_uri}/{path_glob}/**.parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', {file_type}) {condition} SETTINGS {settings} FORMAT TabSeparated"""
    )
    execution_time = time.time() - start_time

    return execution_time, log_comment


@TestStep(Given)
def create_parquet_in_different_locations(self):
    """Create Parquet files in different locations."""

    return create_parquet_files_in_different_paths(path1=PATH1, path2=PATH2)


@TestStep(Given)
def create_parquet_in_different_locations_on_cluster(self):
    """Create Parquet files in different locations on a cluster."""

    return create_parquet_files_in_different_paths(
        path1=PATH1, path2=PATH2, cluster=self.context.cluster_name
    )


@TestStep(Given)
def create_multiple_parquet_files_with_common_datatypes_on_cluster(self):
    """Create multiple Parquet files with common data types on a cluster."""
    create_multiple_parquet_files_with_common_datatypes(
        cluster=self.context.cluster_name
    )


@TestStep(When)
def select_without_cache(self, file_name, statement="*"):
    """Select metadata of the Parquet file without caching the metadata."""
    parquet, without_cache = select_parquet_metadata_from_s3(
        file_name=file_name, statement=statement
    )

    return parquet, without_cache


@TestStep(When)
def select_with_cache(self, file_name, statement="*", log_comment=None):
    """Select metadata of the Parquet file with caching the metadata."""
    parquet, with_cache = select_parquet_metadata_from_s3(
        file_name=file_name, caching=True, statement=statement, log_comment=log_comment
    )

    return parquet, with_cache


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_ReadMetadataAfterCaching(
        "1.0"
    )
)
def parquet_metadata_format(self):
    """Check that a Parquet file can be created on S3."""
    log_comment = "test_" + getuid()

    with Given("I create a parquet file on s3"):
        files = create_multiple_parquet_files_with_all_datatypes(
            number_of_files=self.context.number_of_files
        )
    with When("I select metadata of the Parquet file without caching the metadata"):
        parquet, without_cache = select_without_cache(
            file_name=files[0], statement="COUNT(*)"
        )
    with And("I select metadata of the Parquet file with caching the metadata"):
        select_with_cache(file_name=files[0])
        parquet, with_cache = select_with_cache(
            file_name=files[0],
            log_comment=log_comment,
        )
    with Then("I check the number of hits in the metadata"):
        for retry in retries(count=10, delay=1):
            with retry:
                check_hits(log_comment=log_comment)

        assert (
            without_cache > with_cache
        ), f"query ran slower with caching without_cache={without_cache} with_cache={with_cache}"


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_ReadMetadataAfterCaching(
        "1.0"
    ),
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_S3Cluster(
        "1.0"
    ),
)
def parquet_metadata_format_on_cluster(self):
    """Check that a Parquet file can be created on S3."""
    log_comment = "test_" + getuid()
    node = self.context.node
    with Given("I create a parquet file on s3"):
        files = create_multiple_parquet_files_with_all_datatypes(
            number_of_files=self.context.number_of_files
        )
    with When("I select metadata of the Parquet file without caching the metadata"):
        parquet, without_cache = select_parquet_metadata_from_s3(file_name=files[0])
    with And("I select metadata of the Parquet file with caching the metadata"):
        select_parquet_metadata_from_s3(file_name=files[0], caching=True)
        parquet, with_cache = select_parquet_metadata_from_s3(
            file_name=files[0], log_comment=log_comment, caching=True
        )
    with Then("I check the number of hits in the metadata"):
        for retry in retries(count=10, delay=1):
            with retry:
                check_hits_on_cluster(log_comment=log_comment)

        assert (
            without_cache > with_cache
        ), f"query ran slower with caching without_cache={without_cache} with_cache={with_cache}"


@TestCheck
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_S3Cluster(
        "1.0"
    )
)
def check_caching_metadata_on_multiple_nodes(
    self,
    create_parquet_files,
    additional_setting,
    statement,
    select,
    glob=None,
    condition=None,
):
    """Check to determine scenarios when metadata caching works on multiple node setup."""
    settings = random.choice(additional_setting)

    """Check to determine scenarios when metadata caching works on multiple node setup."""
    with Given("I create a parquet files on s3"):
        files = create_parquet_files()

        if glob is None:
            file_name = random.choice(files)
        else:
            file_name = glob

    with When("I select data from s3 before the metadata was cached"):
        if "join" in select.__name__:
            time_before_cache, _ = select(
                file_name1=files[0], file_name2=files[1], condition=condition
            )
        else:
            time_before_cache, _ = select(file_name=file_name, condition=condition)

    with And("I select data from s3 after the metadata was cached"):
        if "join" in select.__name__:
            time_after_cache, log_comment = select(
                file_name1=files[0],
                file_name2=files[1],
                additional_setting=settings,
                statement=statement,
                condition=condition,
            )
        else:
            time_after_cache, log_comment = select(
                file_name=file_name,
                additional_setting=settings,
                statement=statement,
                condition=condition,
            )

    with Then("I check the number of hits in the metadata"):
        check_hits_on_cluster(log_comment=log_comment)

        assert time_after_cache < time_before_cache, (
            f"query ran slower with caching time_before_cache={time_before_cache}s"
            f"time_after_cache={time_after_cache}s"
        )


@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_AllSettings("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_HivePartitioning(
        "1.0"
    ),
)
@TestSketch(Scenario)
def parquet_s3_caching(self):
    """Check to determine scenarios when metadata caching works and is useful."""

    statements = either(*["*", "COUNT(*)", "COUNT(DISTINCT *)"])
    conditions = either(*[None])
    selects = either(
        *[
            select_parquet_with_metadata_caching_from_cluster,
            select_parquet_with_metadata_caching_with_join,
        ]
    )

    create_parquet = either(
        *[
            create_parquet_in_different_locations_on_cluster,
            create_multiple_parquet_files_with_common_datatypes_on_cluster,
            create_parquet_file_with_bloom_filter,
            create_parquet_file_with_hive_partition,
        ]
    )

    glob = either(*[None, "**.Parquet", "**.incorrect"])

    check_caching_metadata_on_multiple_nodes(
        create_parquet_files=create_parquet,
        additional_setting=settings_for_select,
        statement=statements,
        glob=glob,
        select=selects,
        condition=conditions,
    )


@TestCheck
def check_swarm_parquet(
    self, select, additional_settings, condition, statement, file_type, path_glob
):
    """Check to determine scenarios when metadata caching works on a swarm setup."""
    setting = random.choice(additional_settings)

    with Given(
        "I select data from the parquet file without using metadata caching",
        description=f"""additional setting for a query: {setting}, select function: {select.__name__}, condition: {condition}""",
    ):
        if file_type == "ParquetMetadata" and statement != "*":
            skip()
        initial_execution_time, log = select(
            node=self.context.swarm_initiator,
            cache_metadata=False,
            additional_settings=setting,
            statement=statement,
            condition=condition,
            file_type=file_type,
            path_glob=path_glob,
        )
    with When("I select the data from parquet in iceberg"):
        if file_type == "ParquetMetadata" and statement != "*":
            skip()
        select(
            node=self.context.swarm_initiator,
            cache_metadata=True,
            additional_settings=setting,
            statement=statement,
            condition=condition,
            file_type=file_type,
            path_glob=path_glob,
        )
        execution_time, log = select(
            node=self.context.swarm_initiator,
            cache_metadata=True,
            additional_settings=setting,
            statement=statement,
            condition=condition,
            file_type=file_type,
            path_glob=path_glob,
        )
    with Then("I check that the metadata was cached"):
        if file_type == "ParquetMetadata" and statement != "*":
            skip()
        check_hits_on_cluster(
            log_comment=log,
            initiator_node=self.context.swarm_initiator,
            other_nodes=self.context.swarm_nodes,
        )
    with And("I check that the query ran faster with caching"):
        if file_type == "ParquetMetadata" and statement != "*":
            skip()
        assert (
            initial_execution_time > execution_time
        ), f"query ran slower with caching initial_execution_time={initial_execution_time}s execution_time={execution_time}s"


@TestSketch(Scenario)
@Flags(TE)
def swarm_combinations(self):
    """Combinations of tests for metadata caching on a swarm setup."""
    conditions = either(
        *[
            "WHERE datetime < '2017-09-12 10:35:00.000000'",  # Should skip all files as the datetime is out of min/max range
            "WHERE datetime = '2019-09-12 10:35:00.000000'",
            "WHERE datetime = toDateTime('2019-09-12 10:35:00.000000')",
            "WHERE toYYYYMMDD(datetime) = 20190912",
            "WHERE datetime IN ('2019-09-12 10:35:00.000000', '2019-09-14 10:35:00.000000', '2019-09-16 10:35:00.000000')",
            "WHERE toString(datetime) LIKE '2019-09-12%'",
        ]
    )

    statements = either(*["*", "COUNT(*)", "COUNT(DISTINCT *)", "toDate(datetime)"])

    selects = either(
        *[
            select_parquet_from_iceberg_s3_cluster,
            select_parquet_from_iceberg_s3,
            select_parquet_from_iceberg_s3_cluster_join,
        ]
    )

    file_type = either(*["Parquet", "ParquetMetadata"])
    path_glob = either(*["**", "datetime_day=2019-08-17"])

    check_swarm_parquet(
        select=selects,
        additional_settings=settings_for_select,
        condition=conditions,
        statement=statements,
        file_type=file_type,
        path_glob=path_glob,
    )


@TestScenario
def one_node_disconnects(self):
    """Scenario when in a swarm cluster one node disconnects, and we check that we need to cache the parquet metadata again on that node when it recovers."""
    initiator_node = self.context.swarm_initiator
    disconnect_node = self.context.swarm_nodes[0]

    with Given("I cache metadata from a parquet file"):
        select_parquet_from_iceberg_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )
        _, log = select_parquet_from_iceberg_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )

    with When("I check that the metadata was cached"):
        check_hits_on_cluster(log_comment=log, initiator_node=initiator_node)

    with And("I stop the connection to one of the swarm nodes"):
        stop_swarm_1_node()
        start_swarm_1_node()

    with Then("I check that the metadata was cached again"):
        _, log2 = select_parquet_from_iceberg_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )

    with And("I validate that the metadata is not cached"):
        hits = check_hits(log_comment=log2, node=disconnect_node, assertion=False)

        assert hits == 0, f"metadata was cached on the disconnected node hits={hits}"

        _, log3 = select_parquet_from_iceberg_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )

        check_hits(log_comment=log2, node=disconnect_node)


@TestSuite
def distributed(self):
    """Tests for parquet metadata caching on a distributed setup with replicated cluster of 3 nodes."""
    Scenario(run=parquet_s3_caching)


@TestSuite
def swarm(self):
    """Tests for parquet metadata caching on a swarm setup, where clickhouse-antalya is an initiator node and clickhouse-swarm-1 and clickhouse-swarm-2 are swarm nodes on a cluster."""
    Scenario(run=swarm_combinations)
    Scenario(run=one_node_disconnects)


@TestFeature
@Name("s3 metadata caching")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage("1.0"))
def feature(self, node="clickhouse1", number_of_files=15, partitions_for_swarm=1000):
    """Tests for parquet metadata caching for object storage."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_list = [
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]

    self.context.swarm_initiator = self.context.cluster.node("clickhouse-antalya")
    self.context.swarm_nodes = [
        self.context.cluster.node("clickhouse-swarm-1"),
        self.context.cluster.node("clickhouse-swarm-2"),
    ]

    self.context.cluster_name = "replicated_cluster"
    self.context.number_of_files = number_of_files
    self.context.compression_type = "NONE"
    self.context.node = self.context.cluster.node(node)

    # Scenario(run=parquet_metadata_format)
    # Scenario(run=parquet_s3_caching)

    with Given("I setup iceberg catalog"):
        catalog = setup_iceberg()

    with And("I create a partitioned parquet file in iceberg"):
        create_parquet_partitioned_by_datetime(
            catalog=catalog, number_of_partitions=partitions_for_swarm
        )

    Scenario(run=swarm)
