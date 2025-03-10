from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *

from parquet.tests.steps.metadata_caching import *
from alter.stress.tests.tc_netem import network_packet_delay

PATH1 = "location_1"
PATH2 = "location_2"


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


@TestStep(Given)
def create_a_file_with_bloom_filter(self):
    """Create a Parquet file with bloom filter."""
    pass


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
def parquet_metadata_format(self):
    """Check that a Parquet file can be created on S3."""
    log_comment = "test_" + getuid()
    node = self.context.node
    with Given("I create a parquet file on s3"):
        files = create_multiple_parquet_files_with_all_datatypes(number_of_files=15)
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
def parquet_metadata_format_on_cluster(self):
    """Check that a Parquet file can be created on S3."""
    log_comment = "test_" + getuid()
    node = self.context.node
    with Given("I create a parquet file on s3"):
        files = create_multiple_parquet_files_with_all_datatypes(number_of_files=15)
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
                check_hits(log_comment=log_comment)

        assert (
            without_cache > with_cache
        ), f"query ran slower with caching without_cache={without_cache} with_cache={with_cache}"


@TestCheck
def check_caching_metadata_on_multiple_nodes(
    self, create_parquet_files, additional_setting, statement, glob=None
):
    """Check to determine scenarios when metadata caching works on multiple node setup."""
    with Given("I create a parquet files on s3"):
        files = create_parquet_files()

        if glob is None:
            file_name = random.choice(files)
        else:
            file_name = glob

    with When("I select data from s3 before the metadata was cached"):
        time_before_cache, _ = select_parquet_with_metadata_caching_from_cluster(
            file_name=file_name
        )

    with And("I select data from s3 after the metadata was cached"):
        time_after_cache, log_comment = (
            select_parquet_with_metadata_caching_from_cluster(
                file_name=file_name,
                additional_setting=additional_setting,
                statement=statement,
            )
        )

    with Then("I check the number of hits in the metadata"):
        check_hits_on_cluster(log_comment=log_comment)

        assert time_after_cache < time_before_cache, (
            f"query ran slower with caching time_before_cache={time_before_cache}s"
            f"time_after_cache={time_after_cache}s"
        )


@TestSketch(Scenario)
def parquet_s3_caching(self):
    """Check to determine scenarios when metadata caching works and is useful."""
    settings = [
        None,
        "force_aggregation_in_order=1",
        "aggregation_memory_efficient_merge_threads=1",
        "allow_ddl=1",
        "allow_experimental_codecs=1",
    ]

    statements = ["*", "COUNT(*)"]

    create_parquet = [
        create_parquet_in_different_locations_on_cluster,
        create_multiple_parquet_files_with_common_datatypes_on_cluster,
        create_a_file_with_bloom_filter,
    ]


@TestFeature
@Name("s3 metadata caching")
def feature(self, node="clickhouse1"):
    """Tests for parquet metadata caching for object storage."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_list = [
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]
    self.cotext.cluster_name = "replicated_cluster"

    self.context.compression_type = "NONE"
    self.context.node = self.context.cluster.node(node)

    Scenario(run=parquet_metadata_format)
    Scenario(run=parquet_s3_caching)
