import time
import datetime

from testflows.core import *

from helpers.queries import sync_replica

from s3.tests.common import *
from s3.requirements import *


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Global("1.0"))
def global_setting(self):
    """Check that ClickHouse replicated tables work correctly when the
    <allow_s3_zero_copy_replication> setting is set to 1 as a global merge
    tree engine setting with correct syntax.
    """
    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table on each node"):
        table_name = "zero_copy_replication_global_setting"
        for node in nodes:
            replicated_table(node=node, table_name=table_name)

    with When("I add data to the table"):
        standard_inserts(node=nodes[0], table_name=table_name)

    with Then("I check simple queries on the other node"):
        standard_selects(node=nodes[1], table_name=table_name)


@TestScenario
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DropReplica("1.0")
)
def drop_replica(self):
    """Check that a ClickHouse instance with a replicated table can be dropped
    and started again with no changes to the data in the table.
    """
    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table on each node"):
        table_name = "zero_copy_replication_drop"
        for node in nodes:
            replicated_table(
                node=node,
                table_name=table_name,
                settings=f"{self.context.zero_copy_replication_setting}=1",
            )

    with When("I add data to the table"):
        standard_inserts(node=nodes[0], table_name=table_name)

    with And("I stop the second node"):
        nodes[1].stop()

    with Then("I check simple queries on the first node"):
        standard_selects(node=nodes[0], table_name=table_name)

    with And("I start the second node"):
        nodes[1].start()

    with Then("I check simple queries on the second node"):
        standard_selects(node=nodes[1], table_name=table_name)


@TestScenario
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_AddReplica("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Global("1.0"),
)
def add_replica_global_setting(self):
    """
    Check that ClickHouse replicated tables work correctly when the
    zero_copy_replication setting is set  as a global merge
    tree engine setting.

    Check that additional replicas of a replicated table can be added:
    - with no changes to the data in the table.
    - without significantly increasing disk usage.
    """
    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings, restart=True)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table on the first node"):
        table_name = "zero_copy_replication_add"
        replicated_table(node=nodes[0], table_name=table_name)

    with When("I add data to the table"):
        standard_inserts(node=nodes[0], table_name=table_name)

    with And("I get the size of the s3 bucket"):
        size_after_inserts = get_bucket_size()

    with Given("I have a replicated table on the second node"):
        replicated_table(node=nodes[1], table_name=table_name)

    with Then("the additional replica should add 1 byte to the size of the s3 bucket"):
        check_bucket_size(expected_size=size_after_inserts + 1, tolerance=0)

    with And("I check simple queries on the first node"):
        standard_selects(node=nodes[0], table_name=table_name)

    with And("I check simple queries on the second node"):
        standard_selects(node=nodes[1], table_name=table_name)

    with And("I check the size of the s3 bucket one more time"):
        check_stable_bucket_size(expected_size=size_after_inserts + 1, tolerance=0)


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_AddReplica("1.0"))
def add_replica_local_setting(self):
    """
    Configure zero copy replication per table.
    Check that additional replicas of a replicated table can be added:
    - with no changes to the data in the table.
    - without significantly increasing disk usage.
    """
    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table on the first node"):
        table_name = "zero_copy_replication_add_local"
        replicated_table(
            node=nodes[0],
            table_name=table_name,
            settings=f"{self.context.zero_copy_replication_setting}=1",
        )

    with When("I add data to the table"):
        standard_inserts(node=nodes[0], table_name=table_name)

    with And("I get the size of the s3 bucket"):
        size_after_inserts = get_bucket_size()

    with Given("I have a replicated table on the second node"):
        replicated_table(
            node=nodes[1],
            table_name=table_name,
            settings=f"{self.context.zero_copy_replication_setting}=1",
        )

    with Then("the additional replica should add 1 byte to the size of the s3 bucket"):
        check_bucket_size(expected_size=size_after_inserts + 1, tolerance=0)

    with And("I check simple queries on the first node"):
        standard_selects(node=nodes[0], table_name=table_name)

    with And("I check simple queries on the second node"):
        standard_selects(node=nodes[1], table_name=table_name)

    with And("I check the size of the s3 bucket one more time"):
        check_stable_bucket_size(expected_size=size_after_inserts + 1, tolerance=0)


@TestScenario
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DropReplica("1.0")
)
def offline_alter_replica(self):
    """
    Check that when a ClickHouse instance with a replicated table is offline,
    the data in the table is changed, and then the instance is restarted, all
    data in its replicated table matches the updated data.
    """
    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table on each node"):
        table_name = "zero_copy_replication_drop_alter"
        for node in nodes:
            replicated_table(
                node=node,
                table_name=table_name,
                settings=f"{self.context.zero_copy_replication_setting}=1",
            )

    with When("I insert 1MB of data"):
        insert_data(node=nodes[0], number_of_mb=1, name=table_name)

    with And("I stop the other node"):
        nodes[1].stop()

    with And("another insert of 1MB of data"):
        insert_data(node=nodes[0], number_of_mb=1, start=1024 * 1024, name=table_name)

    with And("a large insert of 10Mb of data"):
        insert_data(
            node=nodes[0], number_of_mb=10, start=1024 * 1024 * 2, name=table_name
        )

    with And("I restart the other node"):
        nodes[1].start()

    with Then("I check simple queries on the other node"):
        standard_selects(node=nodes[1], table_name=table_name)


@TestScenario
@Tags("sanity")
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DropReplica("1.0")
)
def stale_alter_replica(self):
    """
    Similar to offline test, but under load.
    """

    table_name = "stale_replica"
    nodes = self.context.ch_nodes
    columns = "d UInt64, s String"
    insert_size = 100_000
    insert_time = 15

    with Given("I have an Event to control background inserts"):
        stop_background_inserts = Event()

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table on each node"):
        table_name = "zero_copy_replication_drop_alter"
        for node in nodes:
            replicated_table(
                node=node,
                table_name=table_name,
                columns=columns,
                settings=f"{self.context.zero_copy_replication_setting}=1",
            )

    with When("I stop node 2"):
        nodes[1].stop()

    When("I start inserts on node 1", test=repeat_until_stop, parallel=True)(
        stop_event=stop_background_inserts,
        func=lambda: insert_random(
            node=nodes[0], table_name=table_name, columns=columns, rows=insert_size
        ),
    )
    When("I start inserts on node 3", test=repeat_until_stop, parallel=True)(
        stop_event=stop_background_inserts,
        func=lambda: insert_random(
            node=nodes[2], table_name=table_name, columns=columns, rows=insert_size
        ),
    )

    with When(f"I wait {insert_time} seconds and I restart node 2"):
        time.sleep(insert_time)
        nodes[1].start()

    When("I start inserts on node 2", test=repeat_until_stop, parallel=True)(
        stop_event=stop_background_inserts,
        func=lambda: insert_random(
            node=nodes[1], table_name=table_name, columns=columns, rows=insert_size
        ),
    )

    with When("I tell node 2 to sync"):
        sync_replica(node=nodes[1], table_name=table_name, timeout=300)

    with When(f"I wait {insert_time} seconds and stop the inserts"):
        time.sleep(insert_time)
        stop_background_inserts.set()
        join()

    with Then("I check that the nodes are consistent"):
        check_consistency(nodes=nodes, table_name=table_name, sync_timeout=90)


@TestScenario
@Tags("sanity")
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DropReplica("1.0")
)
def add_remove_one_replica(self):
    """
    Test that no data is lost when a node is removed and added as a replica
    during inserts on other replicas.
    """

    table_name = "add_remove_one_replica"
    storage_policy = "external"
    parallel = False
    nodes = self.context.ch_nodes
    rows_per_insert = 1_000_000
    retry_settings = {
        "timeout": 120,
        "initial_delay": 5,
        "delay": 2,
    }

    if self.context.stress:
        rows_per_insert = 5_000_000
        retry_settings["timeout"] = 300
        retry_settings["delay"] = 5

    with Given("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table"):
        for node in nodes:
            replicated_table(
                node=node,
                table_name=table_name,
                policy=storage_policy,
                columns="d UInt64",
                settings=f"{self.context.zero_copy_replication_setting}=1",
            )

    When(
        "I start inserts on the second node",
        test=insert_random,
        parallel=parallel,
    )(
        node=nodes[1],
        table_name=table_name,
        columns="d UInt64",
        rows=rows_per_insert,
    )

    And(
        "I delete the replica on the third node",
        test=delete_replica,
        parallel=parallel,
    )(node=nodes[2], table_name=table_name)

    Given(
        "I replicate the table on the third node",
        test=replicated_table,
        parallel=parallel,
    )(
        node=nodes[2],
        table_name=table_name,
        settings=f"{self.context.zero_copy_replication_setting}=1",
    )

    When(
        "I start inserts on the first node",
        test=insert_random,
        parallel=parallel,
    )(
        node=nodes[0],
        table_name=table_name,
        columns="d UInt64",
        rows=rows_per_insert,
    )

    join()

    for node in nodes:
        with Then(f"I wait for {node.name} to sync by watching the row count"):
            retry(assert_row_count, **retry_settings)(
                node=node, table_name=table_name, rows=rows_per_insert * 2
            )


@TestScenario
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DropReplica("1.0")
)
def add_remove_replica_parallel(self):
    """
    Test that no data is lost when replicas are added and removed
    during inserts on other replicas.
    """

    table_name = "add_remove_replica_parallel"
    nodes = self.context.ch_nodes
    rows_per_insert = 1_000_000
    retry_settings = {
        "timeout": 120,
        "initial_delay": 5,
        "delay": 2,
    }

    if self.context.stress:
        rows_per_insert = 5_000_000
        retry_settings["timeout"] = 300
        retry_settings["delay"] = 5

    with Given("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table on one node"):
        replicated_table(
            node=nodes[0],
            table_name=table_name,
            columns="d UInt64",
            settings=f"{self.context.zero_copy_replication_setting}=1",
        )

    When(
        "I start parallel inserts on the first node",
        test=insert_random,
        parallel=True,
    )(
        node=nodes[0],
        table_name=table_name,
        columns="d UInt64",
        rows=rows_per_insert,
    )
    insert_sets = 1

    Given(
        "I replicate the table on the second node in parallel",
        test=replicated_table,
        parallel=True,
    )(
        node=nodes[1],
        table_name=table_name,
        settings=f"{self.context.zero_copy_replication_setting}=1",
    )

    join()

    with Then("I wait for the second node to sync by watching the row count"):
        retry(assert_row_count, **retry_settings)(
            node=nodes[1], table_name=table_name, rows=rows_per_insert
        )

    And(
        "I start parallel inserts on the second node",
        test=insert_random,
        parallel=True,
    )(
        node=nodes[1],
        table_name=table_name,
        columns="d UInt64",
        rows=rows_per_insert,
    )
    insert_sets += 1

    And(
        "I delete the replica on the first node",
        test=delete_replica,
        parallel=True,
    )(node=nodes[0], table_name=table_name)

    Given(
        "I replicate the table on the third node in parallel",
        test=replicated_table,
        parallel=True,
    )(
        node=nodes[2],
        table_name=table_name,
        settings=f"{self.context.zero_copy_replication_setting}=1",
    )

    When(
        "I continue with parallel inserts on the second node",
        test=insert_random,
        parallel=True,
    )(
        node=nodes[1],
        table_name=table_name,
        columns="d UInt64",
        rows=rows_per_insert,
    )
    insert_sets += 1

    join()

    with And("I wait for the third node to sync by watching the row count"):
        retry(assert_row_count, **retry_settings)(
            node=nodes[2], table_name=table_name, rows=rows_per_insert * insert_sets
        )

    with Then("I also check the row count on the second node"):
        assert_row_count(
            node=nodes[1], table_name=table_name, rows=rows_per_insert * insert_sets
        )

    Given(
        "I start parallel inserts on the second node in parallel",
        test=insert_random,
        parallel=True,
    )(
        node=nodes[1],
        table_name=table_name,
        columns="d UInt64",
        rows=rows_per_insert,
    )
    insert_sets += 1
    And(
        "I start parallel inserts on the third node in parallel",
        test=insert_random,
        parallel=True,
    )(
        node=nodes[2],
        table_name=table_name,
        columns="d UInt64",
        rows=rows_per_insert,
    )
    insert_sets += 1

    Given(
        "I replicate the table on the first node again in parallel",
        test=replicated_table,
        parallel=True,
    )(
        node=nodes[0],
        table_name=table_name,
        settings=f"{self.context.zero_copy_replication_setting}=1",
    )

    join()

    with Then("I wait for the first node to sync by watching the row count"):
        retry(assert_row_count, **retry_settings)(
            node=nodes[0], table_name=table_name, rows=rows_per_insert * insert_sets
        )

    with And("I check the row count on the other nodes"):
        assert_row_count(
            node=nodes[1], table_name=table_name, rows=rows_per_insert * insert_sets
        )
        assert_row_count(
            node=nodes[2], table_name=table_name, rows=rows_per_insert * insert_sets
        )


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Default("1.0"))
def default_value(self):
    """Check that the default value of <allow_s3_zero_copy_replication> is 0."""

    node = current().context.node
    default_value = "0"

    if check_clickhouse_version(">21.8")(self) and check_clickhouse_version("<22.8")(
        self
    ):
        default_value = "1"

    with Given("I restart the node to apply default configuration settings"):
        node.restart()

    with When("I get the value of allow_s3_zero_copy_replication"):
        allow_zero_copy = node.query(
            f"SELECT value FROM system.merge_tree_settings WHERE name = '{self.context.zero_copy_replication_setting}' FORMAT TabSeparated"
        ).output.strip()

    with Then(f"The value should be {default_value}"):
        assert allow_zero_copy == default_value, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Metadata("1.0"))
def metadata(self):
    """Check that metadata is created properly for data stored in a replicated
    table with the <allow_s3_zero_copy_replication> setting set to 1. This check
    will be performed by verifying that the second replica does not send any
    data to S3.
    """
    expected = 6306515

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table on each node"):
        table_name = "zero_copy_replication_metadata"
        for node in nodes:
            replicated_table(node=node, table_name=table_name)

    with And("I add data to the table"):
        standard_inserts(node=nodes[0], table_name=table_name)

    with Then(
        """The number of bytes written to S3 by the first
                node should be a very large number"""
    ):
        event = (
            "WriteBufferFromS3Bytes"
            if check_clickhouse_version(">=22.5")(self)
            or check_clickhouse_version("=22.3.8.40.altinitystable")(self)
            else "S3WriteBytes"
        )
        numBytes = int(
            nodes[0]
            .query(
                f"SELECT value FROM system.events WHERE event = '{event}' FORMAT TabSeparated"
            )
            .output.strip()
        )

        assert numBytes >= 0.95 * expected, error()
        assert numBytes <= 1.05 * expected, error()

    with And(
        """The number of bytes written to S3 by the second
                node should be very small, showing that the data was
                replicated with no copies"""
    ):
        event = (
            "WriteBufferFromS3Bytes"
            if check_clickhouse_version(">=22.5")(self)
            or check_clickhouse_version("=22.3.8.40.altinitystable")(self)
            else "S3WriteBytes"
        )
        numBytes = int(
            nodes[1]
            .query(
                f"SELECT value FROM system.events WHERE event = '{event}' FORMAT TabSeparated"
            )
            .output.strip()
        )

        assert numBytes < 100, error()


@TestOutline(Scenario)
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Alter("1.1"),
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_NoDataDuplication("1.0"),
)
@Examples("count", [[1], [10]])
def alter(self, count=10):
    """Check for data duplication when repeated alter commands are used."""
    table_name = f"zero_copy_replication_alter_repeat_{count}"

    def insert_data_pair(node, number_of_mb, start=0):
        values = ",".join(
            f"({x},1)"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {table_name} VALUES {values}")

    @TestStep(Then)
    def check_query(self, node, query, expected):
        with By(f"executing query", description=query):
            for attempt in retries(timeout=120, delay=5):
                with attempt:
                    with Then(
                        f"result should match the expected", description=expected
                    ):
                        r = node.query(query).output.strip()
                        assert r == expected, error()

    with Given("a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings.copy()
        settings["old_parts_lifetime"] = "1"
        mergetree_config(settings=settings, restart=True)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("a replicated table on each node"):
        for node in nodes:
            replicated_table(
                node=node, table_name=table_name, columns="d UInt64, sign Int8"
            )

    with When("data is added to the table"):
        with By("first inserting 1MB of data"):
            insert_data_pair(nodes[0], 1)

    with And("I get the size of the s3 bucket after insert"):
        size_after_insert = get_bucket_size()

    with Then("I check that the sign is 1 for the second node"):
        check_query(
            node=nodes[1],
            query=f"SELECT sign FROM {table_name} LIMIT 1 FORMAT TabSeparated",
            expected="1",
        )

    with And("I alter and check the size 10 times"):
        sign = 1
        for _ in range(count):
            sign *= -1
            with When(f"all sign values are changed to {sign}"):
                nodes[1].query(f"ALTER TABLE {table_name} UPDATE sign = {sign} WHERE 1")

            with Then(f"the sign should be {sign} for all nodes"):
                for node in nodes:
                    check_query(
                        node=node,
                        query=f"SELECT sign FROM {table_name} LIMIT 1 FORMAT TabSeparated",
                        expected=f"{sign}",
                    )

            with And("the data in S3 should be within 50% of the original amount"):
                for attempt in retries(timeout=60, delay=5):
                    with attempt:
                        current_size = get_bucket_size()
                        assert current_size < size_after_insert * 1.5, error(
                            "data in S3 has grown by more than 50%"
                        )


@TestScenario
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_NoDataDuplication("1.0")
)
def insert_multiple_replicas(self):
    """Check that data is not duplicated when data is inserted in multiple
    replicas of the same table. Check that each replica is updated correctly.
    """
    node = current().context.node
    expected = 6306510

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I get the size of the s3 bucket before adding data"):
        size_before = measure_buckets_before_and_after(delay=60, less_ok=True)

    with And("I have a replicated table on each node"):
        table_name = "zero_copy_replication_drop_alter"
        for node in nodes:
            replicated_table(
                node=node,
                table_name=table_name,
                settings=f"{self.context.zero_copy_replication_setting}=1",
            )

    with When("I insert 1MB of data"):
        insert_data(node=nodes[0], number_of_mb=1, name=table_name)

    with And("I insert of 1MB of data on the other node"):
        insert_data(node=nodes[1], number_of_mb=1, start=1024 * 1024, name=table_name)

    with And("a large insert of 10Mb of data on the first node"):
        insert_data(
            node=nodes[0], number_of_mb=10, start=1024 * 1024 * 2, name=table_name
        )

    with Then("I check simple queries on both nodes"):
        standard_selects(node=nodes[1], table_name=table_name)
        standard_selects(node=nodes[0], table_name=table_name)

    with And("the size of the s3 bucket should be within 1% of expected amount"):
        current_size = get_bucket_size()
        added_size = current_size - size_before
        note(
            f"Added size: {added_size}, current size: {current_size}, size before: {size_before}"
        )

        assert added_size >= expected * 0.99, error()
        assert added_size <= expected * 1.01, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Delete("1.1"))
def delete(self):
    """Check that when replicated tables are removed, they are not
    removed from S3 until all replicas are removed.
    """
    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I get the size of the s3 bucket before adding data"):
        size_before = measure_buckets_before_and_after(less_ok=True)

    with Given("I have a replicated table on each node"):
        table_name = "zero_copy_replication_delete"
        for node in nodes:
            replicated_table(
                node=node,
                table_name=table_name,
                settings=f"{self.context.zero_copy_replication_setting}=1",
            )

    with When("I add data to the table"):
        standard_inserts(node=nodes[0], table_name=table_name)

    with Then("the size of the s3 bucket should have grown"):
        size_after = get_bucket_size()
        assert size_after > size_before, error()

    with When("I drop the table on one node"):
        nodes[0].query(f"DROP TABLE IF EXISTS {table_name}")

    with Then("the size of the s3 bucket should be the same"):
        check_stable_bucket_size(expected_size=size_after, tolerance=0)

    with When("I drop the table on the other node"):
        nodes[1].query(f"DROP TABLE IF EXISTS {table_name} SYNC")

    with Then("the size of the s3 bucket should be the same as before adding data"):
        for attempt in retries(timeout=600, delay=15):
            with attempt:
                check_bucket_size(expected_size=size_before, tolerance=5)


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DeleteAll("1.0"))
def delete_all(self):
    """Check that when all replicas of a table are dropped, the data is deleted
    from S3.
    """
    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I get the size of the s3 bucket before adding data"):
        size_before = measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table on each node"):
        table_name = "zero_copy_replication_delete_all"
        for node in nodes:
            replicated_table(
                node=node,
                table_name=table_name,
                settings=f"{self.context.zero_copy_replication_setting}=1",
            )

    with When("I add data to the table"):
        standard_inserts(node=nodes[0], table_name=table_name)

    with Then("the size of the s3 bucket should have grown"):
        size_now = get_bucket_size()
        assert size_now > size_before, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_TTL_Move("1.0"))
def ttl_move(self):
    """Check that TTL moves work properly when <allow_s3_zero_copy_replication>
    parameter is set to 1.
    """
    table_name = "zero_copy_replication_ttl_move"

    def insert_data_time(node, number_of_mb, time, start=0):
        values = ",".join(
            f"({x},{time})"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {table_name} VALUES {values}")

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings.copy()
        settings["old_parts_lifetime"] = "1"
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And(
        "I get the size of the s3 bucket with the second prefix before adding data"
    ):
        measure_buckets_before_and_after(
            bucket_prefix=self.context.bucket_path + "/tiered"
        )

    try:
        with When("I create a replicated table on each node"):
            for i, node in enumerate(nodes):
                node.restart()
                node.query(
                    f"""
                    CREATE TABLE {table_name} (
                        d UInt64,
                        d1 DateTime
                    ) ENGINE = ReplicatedMergeTree('/clickhouse/{table_name}', '{i + 1}')
                    ORDER BY d
                    TTL d1 + interval 2 day to volume 'external'
                    SETTINGS storage_policy='tiered'
                """
                )

        with And("I add data to the table"):
            with By("first inserting 1MB of data"):
                tm = time.mktime(
                    (datetime.date.today() - datetime.timedelta(days=7)).timetuple()
                )
                insert_data_time(nodes[0], 1, tm, 0)

            with And("another insert of 1MB of data"):
                tm = time.mktime(
                    (datetime.date.today() - datetime.timedelta(days=3)).timetuple()
                )
                insert_data_time(nodes[0], 1, tm, 1024 * 1024)

            with And("a large insert of 10Mb of data"):
                tm = time.mktime(datetime.date.today().timetuple())
                insert_data_time(nodes[0], 10, tm, 1024 * 1024 * 2)

        with Then("I check simple queries on both nodes"):
            check_query_node(
                node=nodes[0],
                num=0,
                query=f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated",
                expected="1572867",
            )
            check_query_node(
                node=nodes[0],
                num=1,
                query=f"SELECT uniqExact(d) FROM {table_name} WHERE d < 10 FORMAT TabSeparated",
                expected="10",
            )
            check_query_node(
                node=nodes[0],
                num=2,
                query=f"SELECT d FROM {table_name} ORDER BY d DESC LIMIT 1 FORMAT TabSeparated",
                expected="3407872",
            )
            check_query_node(
                node=nodes[0],
                num=3,
                query=f"SELECT d FROM {table_name} ORDER BY d ASC LIMIT 1 FORMAT TabSeparated",
                expected="0",
            )
            check_query_node(
                node=nodes[1],
                num=0,
                query=f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated",
                expected="1572867",
            )
            check_query_node(
                node=nodes[1],
                num=1,
                query=f"SELECT uniqExact(d) FROM {table_name} WHERE d < 10 FORMAT TabSeparated",
                expected="10",
            )
            check_query_node(
                node=nodes[1],
                num=2,
                query=f"SELECT d FROM {table_name} ORDER BY d DESC LIMIT 1 FORMAT TabSeparated",
                expected="3407872",
            )
            check_query_node(
                node=nodes[1],
                num=3,
                query=f"SELECT d FROM {table_name} ORDER BY d ASC LIMIT 1 FORMAT TabSeparated",
                expected="0",
            )

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_TTL_Delete("1.0"))
def ttl_delete(self):
    """Check that TTL delete works properly when <allow_s3_zero_copy_replication>
    parameter is set to 1.
    """
    table_name = "zero_copy_replication_ttl_delete"

    def insert_data_time(node, number_of_mb, time, start=0):
        values = ",".join(
            f"({x},{time})"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {table_name} VALUES {values}")

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And(
        "I get the size of the s3 bucket with the second prefix before adding data"
    ):
        measure_buckets_before_and_after(
            bucket_prefix=self.context.bucket_path + "/tiered"
        )

    try:
        with When("I create a replicated table on each node"):
            for i, node in enumerate(nodes):
                node.restart()
                node.query(
                    f"""
                    CREATE TABLE {table_name} (
                        d UInt64,
                        d1 DateTime
                    ) ENGINE = ReplicatedMergeTree('/clickhouse/{table_name}', '{i + 1}')
                    ORDER BY d
                    TTL d1 + interval 2 day
                    SETTINGS storage_policy='tiered'
                """
                )

        with And("I add data to the table"):
            with By("first inserting 1MB of data"):
                tm = time.mktime(
                    (datetime.date.today() - datetime.timedelta(days=7)).timetuple()
                )
                insert_data_time(nodes[0], 1, tm, 0)

            with And("another insert of 1MB of data"):
                tm = time.mktime(
                    (datetime.date.today() - datetime.timedelta(days=7)).timetuple()
                )
                insert_data_time(nodes[0], 1, tm, 1024 * 1024)

            with And("a large insert of 10Mb of data"):
                tm = time.mktime(datetime.date.today().timetuple())
                insert_data_time(nodes[0], 10, tm, 1024 * 1024 * 2)

        with Then("I check simple queries on both nodes"):
            check_query_node(
                node=nodes[0],
                num=0,
                query=f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated",
                expected="1310721",
            )
            check_query_node(
                node=nodes[0],
                num=1,
                query=f"SELECT uniqExact(d) FROM {table_name} WHERE d < 10 FORMAT TabSeparated",
                expected="0",
            )
            check_query_node(
                node=nodes[0],
                num=2,
                query=f"SELECT d FROM {table_name} ORDER BY d DESC LIMIT 1 FORMAT TabSeparated",
                expected="3407872",
            )
            check_query_node(
                node=nodes[0],
                num=3,
                query=f"SELECT d FROM {table_name} ORDER BY d ASC LIMIT 1 FORMAT TabSeparated",
                expected="2097152",
            )
            check_query_node(
                node=nodes[1],
                num=0,
                query=f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated",
                expected="1310721",
            )
            check_query_node(
                node=nodes[1],
                num=1,
                query=f"SELECT uniqExact(d) FROM {table_name} WHERE d < 10 FORMAT TabSeparated",
                expected="0",
            )
            check_query_node(
                node=nodes[1],
                num=2,
                query=f"SELECT d FROM {table_name} ORDER BY d DESC LIMIT 1 FORMAT TabSeparated",
                expected="3407872",
            )
            check_query_node(
                node=nodes[1],
                num=3,
                query=f"SELECT d FROM {table_name} ORDER BY d ASC LIMIT 1 FORMAT TabSeparated",
                expected="2097152",
            )

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestOutline(Scenario)
@Examples(
    "source destination", [["replicated", "zero_copy"], ["zero_copy", "replicated"]]
)
def migration(self, source, destination):
    """Test migrating data between tables with and without zero copy replication."""

    node = self.context.node
    columns = "d UInt64"

    with Given("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(delay=15, less_ok=True)

    with And("I have a replicated table"):
        replicated_table_name = "migration_replicated_" + getuid()[:8]
        for node in self.context.ch_nodes:
            replicated_table(
                node=node, table_name=replicated_table_name, columns=columns
            )

    with And("I have a zero-copy table"):
        zero_copy_table_name = "migration_zero_copy_" + getuid()[:8]
        for node in self.context.ch_nodes:
            replicated_table(
                node=node,
                table_name=zero_copy_table_name,
                columns=columns,
                settings=f"{self.context.zero_copy_replication_setting}=1",
            )

    table_names = {
        "replicated": replicated_table_name,
        "zero_copy": zero_copy_table_name,
    }

    with When(f"I select {source} as the source table"):
        source_table_name = table_names[source]

    with And(f"I select {destination} as the destination table"):
        dest_table_name = table_names[destination]

    with And("I insert data to the source table"):
        insert_random(
            node=node, table_name=source_table_name, columns=columns, rows=1000000
        )

    with When("I copy the source table to the destination table"):
        node.query(f"INSERT INTO {dest_table_name} SELECT * from {source_table_name}")

    with And("I delete the source table"):
        delete_replica(node=node, table_name=source_table_name)

    with Then("the data should be in the destination table"):
        assert_row_count(node=node, table_name=dest_table_name, rows=1000000)


@TestScenario
def bad_detached_part(self):
    """
    Test that a bad detached part on one replica does not affect the other replica.
    """

    node = current().context.node
    table_name = "detach_table"

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = {
            self.context.zero_copy_replication_setting: "1",
        }
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    with And("I have a replicated table on each node"):
        for node in nodes:
            replicated_table(
                node=node, table_name=table_name, settings="min_bytes_for_wide_part=0"
            )

    with When("I insert data on the second node"):
        nodes[1].query(f"INSERT INTO {table_name} VALUES (123)")

    with And("I sync the first node"):
        sync_replica(node=nodes[0], table_name=table_name)

    with And("I get the path for the part"):
        r = nodes[1].query(
            f"SELECT path FROM system.parts where table='{table_name}' and name='all_0_0_0' FORMAT TabSeparated"
        )
        part_path = r.output
        assert part_path.startswith("/"), error("Expected absolute path!")

    with And("I delete the part's count.txt"):
        nodes[1].command(f"rm {part_path}/count.txt")

    with And("I detach the table on the second node"):
        nodes[1].query(f"DETACH TABLE {table_name} SYNC")

    with And("I reattach the table on the second node"):
        nodes[1].query(f"ATTACH TABLE {table_name}")

    with And("I check detached parts on the second node"):
        r = nodes[1].query(
            f"SELECT reason, name FROM system.detached_parts where table='{table_name}' FORMAT TabSeparated"
        )
        assert r.output == "broken-on-start	broken-on-start_all_0_0_0", error()

    with And("I drop the table on the second node"):
        nodes[1].query(f"DROP TABLE {table_name} SYNC")

    with Then("The first node should still have the data"):
        r = nodes[0].query(f"SELECT * FROM {table_name} FORMAT TabSeparated")
        assert r.output == "123", error()


@TestScenario
@Requirements(RQ_SRS_015_S3_Performance_AllowS3ZeroCopyReplication_Insert("1.0"))
def performance_insert(self):
    """Compare insert performance using S3 zero copy replication and not using
    zero copy replication.
    """

    def insert_data_time(node, number_of_mb, table_name, start=0):
        values = ",".join(
            f"({x})"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        start_time = time.time()
        node.query(f"INSERT INTO {table_name} VALUES {values}")
        end_time = time.time()
        return end_time - start_time

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have a replicated table on each node"):
        table_name = "no_zero_copy_replication_insert"
        for node in nodes:
            node.restart()
            replicated_table(node=node, table_name=table_name)

    with When("I add data to the table and save the time taken"):
        no_zero_copy_time = insert_data_time(nodes[0], 20, table_name)
        metric("no_zero_copy", units="seconds", value=str(no_zero_copy_time))

    with Given("I have a replicated 0copy table on each node"):
        table_name = "allow_zero_copy_replication_insert"
        for node in nodes:
            node.restart()
            replicated_table(
                node=node,
                table_name=table_name,
                settings=f"{self.context.zero_copy_replication_setting}=1",
            )

    with When("I add data to the table and save the time taken"):
        allow_zero_copy_time = insert_data_time(nodes[0], 20, table_name)
        metric("with_zero_copy", units="seconds", value=str(allow_zero_copy_time))

    with Finally("I print the difference in time taken"):
        metric(
            "percentage_increase",
            units="%",
            value=str(
                ((allow_zero_copy_time - no_zero_copy_time) / no_zero_copy_time) * 100
            ),
        )


@TestScenario
@Requirements(RQ_SRS_015_S3_Performance_AllowS3ZeroCopyReplication_Select("1.0"))
def performance_select(self):
    """Compare select performance using S3 zero copy replication and not using
    zero copy replication.
    """
    node = current().context.node

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    try:
        with Given("I have a replicated table on each node"):
            table_name = "no_zero_copy_replication_select"
            for node in nodes:
                node.restart()
                replicated_table(node=node, table_name=table_name)

        with When("I add 20 Mb of data to the table"):
            insert_data(node=nodes[0], name=table_name, number_of_mb=20)

        with Then("I sync the replicas"):
            retry(sync_replica, timeout=600, delay=5)(
                node=nodes[1],
                table_name=table_name,
                settings=[("receive_timeout", 600)],
            )

        with Then("I select from the table and save the time taken"):
            start_time = time.time()
            nodes[1].query(
                f"CREATE TABLE zcrSelect Engine = MergeTree() ORDER BY d AS SELECT * FROM {table_name}"
            )
            end_time = time.time()
            no_zero_copy_time = end_time - start_time
            metric("no_zero_copy", units="seconds", value=str(no_zero_copy_time))

    finally:
        with Finally("I drop the tables on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS zcrSelect SYNC")

    try:
        with Given("I have a replicated 0copy table on each node"):
            table_name = "allow_zero_copy_replication_select"
            for node in nodes:
                node.restart()
                replicated_table(
                    node=node,
                    table_name=table_name,
                    settings=f"{self.context.zero_copy_replication_setting}=1",
                )

        with When("I add 20 Mb of data to the table"):
            insert_data(node=nodes[0], name=table_name, number_of_mb=20)

        with Then("I sync the replicas"):
            retry(sync_replica, timeout=600, delay=5)(
                node=nodes[1],
                table_name=table_name,
                settings=[("receive_timeout", 600)],
                timeout=600,
            )

        with Then("I select from the table and save the time taken"):
            start_time = time.time()
            nodes[1].query(
                f"CREATE TABLE zcrSelect Engine = MergeTree() ORDER BY d AS SELECT * FROM {table_name}"
            )
            end_time = time.time()
            allow_zero_copy_time = end_time - start_time
            metric("with_zero_copy", units="seconds", value=str(allow_zero_copy_time))

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS zcrSelect SYNC")

    with Finally("I print the difference in time taken"):
        metric(
            "percentage_increase",
            units="%",
            value=str(
                ((allow_zero_copy_time - no_zero_copy_time) / no_zero_copy_time) * 100
            ),
        )


@TestScenario
@Requirements(RQ_SRS_015_S3_Performance_AllowS3ZeroCopyReplication_Alter("1.0"))
def performance_alter(self):
    """Compare alter table performance using S3 zero copy replication and not
    using zero copy replication.
    """
    node = current().context.node

    def insert_data_pair(node, number_of_mb, table_name, start=0):
        values = ",".join(
            f"({x},1)"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {table_name} VALUES {values}")

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have a replicated table on each node"):
        table_name = "no_zero_copy_replication_alter"
        for node in nodes:
            replicated_table(
                node=node, table_name=table_name, columns="d UInt64, sign Int8"
            )

    with When("I add 20 Mb of data to the table"):
        insert_data_pair(nodes[0], 20, table_name)

    with Then("I sync the replicas"):
        retry(sync_replica, timeout=1200, delay=5)(
            node=nodes[1],
            table_name=table_name,
            settings=[("receive_timeout", 600)],
        )

    with Then("I alter the table and save the time taken"):
        start_time = time.time()
        nodes[1].query(f"ALTER TABLE {table_name} UPDATE sign = -1 WHERE 1")
        end_time = time.time()
        no_zero_copy_time = end_time - start_time
        metric("no_zero_copy", units="seconds", value=str(no_zero_copy_time))

    with Given("I have a replicated 0copy table on each node"):
        table_name = "allow_zero_copy_replication_alter"
        for node in nodes:
            node.restart()
            replicated_table(
                node=node,
                table_name=table_name,
                columns="d UInt64, sign Int8",
                settings=f"{self.context.zero_copy_replication_setting}=1",
            )

    with When("I add 20 Mb of data to the table"):
        insert_data_pair(nodes[0], 20, table_name)

    with Then("I sync the replicas"):
        retry(sync_replica, timeout=600, delay=5)(
            node=nodes[1],
            table_name=table_name,
            settings=[("receive_timeout", 600)],
        )

    with Then("I alter the table and save the time taken"):
        start_time = time.time()
        nodes[1].query(f"ALTER TABLE {table_name} UPDATE sign = -1 WHERE sign = 1")
        end_time = time.time()
        allow_zero_copy_time = end_time - start_time
        metric("with_zero_copy", units="seconds", value=str(allow_zero_copy_time))

    with Finally("I print the difference in time taken"):
        metric(
            "percentage_increase",
            units="%",
            value=str(
                ((allow_zero_copy_time - no_zero_copy_time) / no_zero_copy_time) * 100
            ),
        )


@TestScenario
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Alter("1.1"),
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DataPreservedAfterMutation(
        "1.0"
    ),
)
def check_refcount_after_mutation(self):
    """Check that clickhouse correctly updates ref_count when updating metadata across replicas."""
    node = current().context.node
    table_name = "table_" + getuid()

    with Given("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    try:
        with Given("I have a table"):
            node.query(
                f"""
            CREATE TABLE IF NOT EXISTS {table_name} ON CLUSTER 'sharded_cluster' (key UInt32, value1 String, value2 String, value3 String) 
            ENGINE=ReplicatedMergeTree('/clickhouse/tables/{table_name}', '{{replica}}')
            ORDER BY key
            PARTITION BY (key % 4)
            SETTINGS storage_policy='external'
            """,
                settings=[("distributed_ddl_task_timeout ", 360)],
            )

        with And("I insert some data"):
            node.query(
                f"INSERT INTO {table_name} SELECT * FROM generateRandom('key UInt32, value1 String, value2 String, value3 String') LIMIT 1000000"
            )

        with When("I add a new column"):
            node.query(
                f"ALTER TABLE {table_name} ADD COLUMN valueX String materialized value1"
            )

        with And(f"I materialize the new column"):
            node.query(f"ALTER TABLE {table_name} MATERIALIZE COLUMN valueX")

        with Then("Check refs"):
            output = node.command(
                r"grep -A 1 r00000000000000000000 -R /var/lib/clickhouse/disks/external/store/ | grep -B 1 '\-0' | grep r00000000000000000000 | sort -k 2 | uniq -df 1"
            ).output
            assert output == "", error()

    finally:
        with Finally(f"I drop the table"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER 'sharded_cluster' "
            )


@TestScenario
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Alter("1.1"),
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DataPreservedAfterMutation(
        "1.0"
    ),
)
def consistency_during_double_mutation(self):
    """Check that clickhouse correctly handles simultaneous metadata updates on different replicas."""
    node = current().context.node
    table_name = "table_" + getuid()

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    try:
        with Given("I have a 0copy table"):
            node.query(
                f"""
            CREATE TABLE IF NOT EXISTS {table_name} ON CLUSTER 'sharded_cluster' (key UInt32, value1 String, value2 String, value3 String) 
            ENGINE=ReplicatedMergeTree('/clickhouse/tables/{table_name}', '{{replica}}')
            ORDER BY key
            PARTITION BY (key % 4)
            SETTINGS storage_policy='external', {self.context.zero_copy_replication_setting}=1
            """,
                settings=[("distributed_ddl_task_timeout ", 360)],
            )

        with And("I insert some data"):
            node.query(
                f"INSERT INTO {table_name} SELECT * FROM generateRandom('key UInt32, value1 String, value2 String, value3 String') LIMIT 1000000"
            )

        with When("I add a new column on the first node"):
            nodes[0].query(
                f"ALTER TABLE {table_name} ADD COLUMN valueX String materialized value1"
            )

        with And("I delete a column on the second node"):
            nodes[1].query(f"ALTER TABLE {table_name} DROP COLUMN value3")

        with And(f"I materialize the new column on the first node"):
            nodes[0].query(f"ALTER TABLE {table_name} MATERIALIZE COLUMN valueX")

        with When("I run DESCRIBE TABLE"):
            r = node.query(f"DESCRIBE TABLE {table_name}")

        with Then("The output should contain my new column"):
            assert "valueX" in r.output, error(r)

        with And("The output should not contain the deleted column"):
            assert "value3" not in r.output, error(r)

    finally:
        with Finally(f"I drop the table"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER 'sharded_cluster' "
            )


@TestScenario
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_Alter("1.1"),
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DataPreservedAfterMutation(
        "1.0"
    ),
)
def consistency_during_conflicting_mutation(self):
    """Check that clickhouse correctly handles simultaneous metadata updates on different replicas."""
    node = current().context.node
    table_name = "table_" + getuid()

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after(less_ok=True)

    try:
        with Given("I have a table"):
            node.query(
                f"""
            CREATE TABLE IF NOT EXISTS {table_name} ON CLUSTER 'sharded_cluster' (key UInt32, value1 String, value2 String, value3 String) 
            ENGINE=ReplicatedMergeTree('/clickhouse/tables/{table_name}', '{{replica}}')
            ORDER BY key
            PARTITION BY (key % 4)
            SETTINGS storage_policy='external', {self.context.zero_copy_replication_setting}=1
            """,
                settings=[("distributed_ddl_task_timeout ", 360)],
            )

        with And("I insert some data"):
            node.query(
                f"INSERT INTO {table_name} SELECT * FROM generateRandom('key UInt32, value1 String, value2 String, value3 String') LIMIT 1000000"
            )

        with And("I delete a column on the second node"):
            nodes[1].query(f"ALTER TABLE {table_name} DROP COLUMN value3")

        with When("I add the same column on the first node"):
            nodes[0].query(
                f"ALTER TABLE {table_name} ADD COLUMN value3 String materialized value1"
            )

        with And(f"I materialize the new column on the first node"):
            nodes[0].query(f"ALTER TABLE {table_name} MATERIALIZE COLUMN value3")

        with When("I run DESCRIBE TABLE"):
            r = node.query(f"DESCRIBE TABLE {table_name}")

        with Then("The output should contain all columns"):
            assert "value1" in r.output, error(r)
            assert "value2" in r.output, error(r)
            assert "value3" in r.output, error(r)

    finally:
        with Finally(f"I drop the table"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER 'sharded_cluster' "
            )


@TestOutline(Feature)
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication("1.0"))
def outline(self, uri, bucket_prefix):
    """Test S3 and S3 compatible storage through storage disks."""
    self.context.minio_enabled = self.context.storage == "minio"

    self.context.uri = uri

    if self.context.storage == "azure":
        with Given("I have two S3 disks configured"):
            disks = {
                "external": azure_blob_type_disk_parameters(
                    self.context.azure_storage_account_url,
                    self.context.azure_container_name,
                    self.context.azure_account_name,
                    self.context.azure_account_key,
                ),
                "external_tiered": azure_blob_type_disk_parameters(
                    self.context.azure_storage_account_url,
                    self.context.azure_container_name,
                    self.context.azure_account_name,
                    self.context.azure_account_key,
                ),
            }

    else:
        with Given("a temporary s3 path"):
            temp_s3_path = temporary_bucket_path(
                bucket_prefix=f"{bucket_prefix}/zero-copy-replication"
            )

            zero_copy_uri = f"{uri}zero-copy-replication/{temp_s3_path}/"
            self.context.bucket_path = (
                f"{bucket_prefix}/zero-copy-replication/{temp_s3_path}"
            )

        with And("I have two S3 disks configured"):
            disks = {
                "external": s3_type_disk_parameters(
                    zero_copy_uri,
                    self.context.access_key_id,
                    self.context.secret_access_key,
                ),
                "external_tiered": s3_type_disk_parameters(
                    zero_copy_uri + "tiered/",
                    self.context.access_key_id,
                    self.context.secret_access_key,
                ),
            }

    with And(
        """I have a storage policy configured to use the S3 disk and a tiered
             storage policy using both S3 disks"""
    ):
        policies = {
            "external": {"volumes": {"external": {"disk": "external"}}},
            "tiered": {
                "volumes": {
                    "default": {"disk": "external"},
                    "external": {"disk": "external_tiered"},
                }
            },
        }

    with And("I have zero copy configuration"):
        if check_clickhouse_version(">=21.8")(self):
            self.context.zero_copy_replication_setting = (
                "allow_remote_fs_zero_copy_replication"
            )
        else:
            self.context.zero_copy_replication_setting = (
                "allow_s3_zero_copy_replication"
            )

        self.context.zero_copy_replication_settings = {
            self.context.zero_copy_replication_setting: "1"
        }

    with And("I have clickhouse nodes"):
        self.context.ch_nodes = [
            self.context.cluster.node(name)
            for name in self.context.cluster.nodes["clickhouse"]
        ]

    with And("I enable the disk and policy config"):
        s3_storage(disks=disks, policies=policies, restart=True)

    with And("I know the size of the s3 bucket currently"):
        initial_bucket_size = get_bucket_size()

    for scenario in loads(current_module(), Scenario):
        scenario()

    with Finally("the size of the s3 bucket should be the same as before"):
        check_bucket_size(expected_size=initial_bucket_size, tolerance=50)


@TestFeature
@Requirements(RQ_SRS_015_S3_AWS_AllowS3ZeroCopyReplication("1.0"))
@Name("zero copy replication")
def aws_s3(self, uri, bucket_prefix):

    outline(uri=uri, bucket_prefix=bucket_prefix)


@TestFeature
@Requirements(RQ_SRS_015_S3_GCS_AllowS3ZeroCopyReplication("1.0"))
@Name("zero copy replication")
def gcs(self, uri, bucket_prefix):
    skip("GCS is not supported for zero copy replication")

    outline(uri=uri, bucket_prefix=bucket_prefix)


@TestFeature
@Name("zero copy replication")
def azure(self):
    # skip("GCS is not supported for zero copy replication")

    outline(uri=None, bucket_prefix=None)


@TestFeature
@Requirements(RQ_SRS_015_S3_MinIO_AllowS3ZeroCopyReplication("1.0"))
@Name("zero copy replication")
def minio(self, uri, bucket_prefix):

    outline(uri=uri, bucket_prefix=bucket_prefix)
