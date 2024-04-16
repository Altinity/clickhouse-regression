import time
import datetime

from testflows.core import *

from helpers.queries import sync_replica

from s3.tests.common import *
from s3.requirements import *


@TestStep(Given)
def measure_buckets_before_and_after(
    self, bucket_prefix=None, bucket_name=None, tolerance=5
):
    """Return the current bucket size and assert that it is the same after cleanup."""

    with When("I get the size of the s3 bucket before adding data"):
        size_before = get_stable_bucket_size(prefix=bucket_prefix, name=bucket_name)

    yield size_before

    with Then(
        """The size of the s3 bucket should be very close to the size
                before adding any data"""
    ):
        check_stable_bucket_size(
            prefix=bucket_prefix,
            name=bucket_name,
            expected_size=size_before,
            tolerance=tolerance,
        )


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
        measure_buckets_before_and_after()

    with When("I create a replicated table on each node"):
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

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after()

    with When("I create a replicated table on each node"):
        table_name = "zero_copy_replication_drop"
        for node in nodes:
            replicated_table(node=node, table_name=table_name)

    with And("I add data to the table"):
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
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_AddReplica("1.0"))
def add_replica(self):
    """Check that additional replicas of a replicated table can be added with
    no changes to the data in the table.
    """
    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after()

    with When("I create a replicated table on the first node"):
        table_name = "zero_copy_replication_add"
        replicated_table(node=nodes[0], table_name=table_name)

    with And("I add data to the table"):
        standard_inserts(node=nodes[0], table_name=table_name)

    with And("I get the size of the s3 bucket"):
        size_after_inserts = get_bucket_size()

    with And("I create a replicated table on the second node"):
        replicated_table(node=nodes[1], table_name=table_name)

    with Then(
        """The size of the s3 bucket should be 1 byte more
                than previously because of the additional replica"""
    ):
        check_bucket_size(expected_size=size_after_inserts + 1, tolerance=0)

    with And("I check simple queries on the first node"):
        standard_selects(node=nodes[0], table_name=table_name)

    with And("I check simple queries on the second node"):
        standard_selects(node=nodes[1], table_name=table_name)


@TestScenario
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DropReplica("1.0")
)
def drop_alter_replica(self):
    """Check that when a ClickHouse instance with a replicated table is dropped,
    the data in the table is changed, and then the instance is restarted, all
    data in its replicated table matches the updated data.
    """
    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after()

    with When("I create a replicated table on each node"):
        table_name = "zero_copy_replication_drop_alter"
        for node in nodes:
            replicated_table(node=node, table_name=table_name)

    with And("I insert 1MB of data"):
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
            f"SELECT value FROM system.merge_tree_settings WHERE name = '{self.context.zero_copy_replication_setting}'"
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

    with When("I create a replicated table on each node"):
        table_name = "zero_copy_replication_metadata"
        for node in nodes:
            node.restart()
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
            .query(f"SELECT value FROM system.events WHERE event = '{event}'")
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
            .query(f"SELECT value FROM system.events WHERE event = '{event}'")
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
    table_name = "zero_copy_replication_alter_repeat"

    def insert_data_pair(node, number_of_mb, start=0):
        values = ",".join(
            f"({x},1)"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {table_name} VALUES {values}")

    def check_query_pair(node, num, query, expected):
        with By(f"executing query {num}", description=query):
            r = node.query(query).output.strip()
            with Then(f"result should match the expected", description=expected):
                assert r == expected, error()

    def alter_table(sign):
        with Then(f"I change all signs to {sign}"):
            nodes[1].query(f"ALTER TABLE {table_name} UPDATE sign = {sign} WHERE 1")

        with And("I sync the replicas"):
            for node in nodes:
                for attempt in retries(timeout=1200, delay=5):
                    with attempt:
                        node.query(f"SYSTEM SYNC REPLICA {table_name}", timeout=600)

        with And("I check that the sign is -1 for the second table"):
            check_query_pair(
                node=nodes[1],
                num=0,
                query=f"SELECT sign FROM {table_name} LIMIT 1",
                expected=f"{sign}",
            )

        with And("I check that the sign is -1 for the first table"):
            check_query_pair(
                node=nodes[0],
                num=0,
                query=f"SELECT sign FROM {table_name} LIMIT 1",
                expected=f"{sign}",
            )

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings.copy()
        settings["old_parts_lifetime"] = "1"
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after()

    with When("I create a replicated table on each node"):
        for node in nodes:
            node.restart()
            replicated_table(
                node=node, table_name=table_name, columns="d UInt64, sign Int8"
            )

    with And("I add data to the table"):
        with By("first inserting 1MB of data"):
            insert_data_pair(nodes[0], 1)

    with And("I get the size of the s3 bucket"):
        size_after_insert = get_bucket_size()

    with Then("I check that the sign is 1 for the second table"):
        check_query_pair(
            node=nodes[1],
            num=0,
            query=f"SELECT sign FROM {table_name} LIMIT 1",
            expected="1",
        )

    with And("I alter and check the size 10 times"):
        s = 1
        for i in range(count):
            alter_table(s)

            with Then(
                """I make sure the amount of data in S3 is within
                        50% of the original amount"""
            ):
                start_time = time.time()
                while True:
                    current_size = get_bucket_size()
                    if current_size < size_after_insert * 1.5:
                        break
                    if time.time() - start_time < 60:
                        time.sleep(2)
                        continue
                    assert False, "data in S3 has grown by more than 50%"

            s *= -1


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

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        size_before = measure_buckets_before_and_after()

    with When("I create a replicated table on each node"):
        table_name = "zero_copy_replication_drop_alter"
        for node in nodes:
            node.restart()
            replicated_table(node=node, table_name=table_name)

    with And("I insert 1MB of data"):
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

    with And("I check that the data added is within 1% of expected amount"):
        current_size = get_bucket_size()
        added_size = current_size - size_before

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

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        size_before = measure_buckets_before_and_after()

    with When("I create a replicated table on each node"):
        table_name = "zero_copy_replication_delete"
        for node in nodes:
            replicated_table(node=node, table_name=table_name)

    with And("I add data to the table"):
        standard_inserts(node=nodes[0], table_name=table_name)

    with Then("I check that data was added to the s3 bucket"):
        size_after = get_bucket_size()
        assert size_after > size_before, error()

    with When("I drop the table on one node"):
        nodes[0].query(f"DROP TABLE IF EXISTS {table_name}")

    with Then("The size of the s3 bucket should be the same"):
        check_bucket_size(expected_size=size_before, tolerance=0)

    with When("I drop the table on the other node"):
        nodes[1].query(f"DROP TABLE IF EXISTS {table_name} SYNC")

    with Then(
        """The size of the s3 bucket should be very close to the size
                before adding any data"""
    ):
        check_stable_bucket_size(expected_size=size_before, tolerance=5)


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_AllowS3ZeroCopyReplication_DeleteAll("1.0"))
def delete_all(self):
    """Check that when all replicas of a table are dropped, the data is deleted
    from S3.
    """
    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with And("I get the size of the s3 bucket before adding data"):
        size_before = measure_buckets_before_and_after()

    with When("I create a replicated table on each node"):
        table_name = "zero_copy_replication_delete_all"
        for node in nodes:
            replicated_table(node=node, table_name=table_name)

    with And("I add data to the table"):
        standard_inserts(node=nodes[0], table_name=table_name)

    with Then("A nonzero amount of data should be added to S3"):
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
        measure_buckets_before_and_after()

    with And("I get the size of the other s3 bucket before adding data"):
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
                query=f"SELECT COUNT() FROM {table_name}",
                expected="1572867",
            )
            check_query_node(
                node=nodes[0],
                num=1,
                query=f"SELECT uniqExact(d) FROM {table_name} WHERE d < 10",
                expected="10",
            )
            check_query_node(
                node=nodes[0],
                num=2,
                query=f"SELECT d FROM {table_name} ORDER BY d DESC LIMIT 1",
                expected="3407872",
            )
            check_query_node(
                node=nodes[0],
                num=3,
                query=f"SELECT d FROM {table_name} ORDER BY d ASC LIMIT 1",
                expected="0",
            )
            check_query_node(
                node=nodes[1],
                num=0,
                query=f"SELECT COUNT() FROM {table_name}",
                expected="1572867",
            )
            check_query_node(
                node=nodes[1],
                num=1,
                query=f"SELECT uniqExact(d) FROM {table_name} WHERE d < 10",
                expected="10",
            )
            check_query_node(
                node=nodes[1],
                num=2,
                query=f"SELECT d FROM {table_name} ORDER BY d DESC LIMIT 1",
                expected="3407872",
            )
            check_query_node(
                node=nodes[1],
                num=3,
                query=f"SELECT d FROM {table_name} ORDER BY d ASC LIMIT 1",
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
        measure_buckets_before_and_after()

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
                query=f"SELECT COUNT() FROM {table_name}",
                expected="1310721",
            )
            check_query_node(
                node=nodes[0],
                num=1,
                query=f"SELECT uniqExact(d) FROM {table_name} WHERE d < 10",
                expected="0",
            )
            check_query_node(
                node=nodes[0],
                num=2,
                query=f"SELECT d FROM {table_name} ORDER BY d DESC LIMIT 1",
                expected="3407872",
            )
            check_query_node(
                node=nodes[0],
                num=3,
                query=f"SELECT d FROM {table_name} ORDER BY d ASC LIMIT 1",
                expected="2097152",
            )
            check_query_node(
                node=nodes[1],
                num=0,
                query=f"SELECT COUNT() FROM {table_name}",
                expected="1310721",
            )
            check_query_node(
                node=nodes[1],
                num=1,
                query=f"SELECT uniqExact(d) FROM {table_name} WHERE d < 10",
                expected="0",
            )
            check_query_node(
                node=nodes[1],
                num=2,
                query=f"SELECT d FROM {table_name} ORDER BY d DESC LIMIT 1",
                expected="3407872",
            )
            check_query_node(
                node=nodes[1],
                num=3,
                query=f"SELECT d FROM {table_name} ORDER BY d ASC LIMIT 1",
                expected="2097152",
            )

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


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

    with When("I create a replicated table on each node"):
        for node in nodes:
            node.restart()
            replicated_table(
                node=node, table_name=table_name, settings="min_bytes_for_wide_part=0"
            )

    with And("I insert data on the second node"):
        nodes[1].query(f"INSERT INTO {table_name} VALUES (123)")

    with And("I sync the first node"):
        sync_replica(node=nodes[0], table_name=table_name)

    with And("I get the path for the part"):
        r = nodes[1].query(
            f"SELECT path FROM system.parts where table='{table_name}' and name='all_0_0_0'"
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
            f"SELECT reason, name FROM system.detached_parts where table='{table_name}'"
        )
        assert r.output == "broken-on-start	broken-on-start_all_0_0_0", error()

    with And("I drop the table on the second node"):
        nodes[1].query(f"DROP TABLE {table_name} SYNC")

    with Then("The first node should still have the data"):
        r = nodes[0].query(f"SELECT * FROM {table_name}")
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

    with When("I create a replicated table on each node"):
        table_name = "no_zero_copy_replication_insert"
        for node in nodes:
            node.restart()
            replicated_table(node=node, table_name=table_name)

    with And("I add data to the table and save the time taken"):
        no_zero_copy_time = insert_data_time(nodes[0], 20, table_name)
        metric("no_zero_copy", units="seconds", value=str(no_zero_copy_time))

    with Given("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with When("I create a replicated table on each node"):
        table_name = "allow_zero_copy_replication_insert"
        for node in nodes:
            node.restart()
            replicated_table(node=node, table_name=table_name)

    with And("I add data to the table and save the time taken"):
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
        with When("I create a replicated table on each node"):
            table_name = "no_zero_copy_replication_select"
            for node in nodes:
                node.restart()
                replicated_table(node=node, table_name=table_name)

        with And("I add 20 Mb of data to the table"):
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

    with Given("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    try:
        with When("I create a replicated table on each node"):
            table_name = "allow_zero_copy_replication_select"
            for node in nodes:
                node.restart()
                replicated_table(node=node, table_name=table_name)

        with And("I add 20 Mb of data to the table"):
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

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings

    with When("I create a replicated table on each node"):
        table_name = "no_zero_copy_replication_alter"
        for node in nodes:
            node.restart()
            replicated_table(
                node=node, table_name=table_name, columns="d UInt64, sign Int8"
            )

    with And("I add 20 Mb of data to the table"):
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

    with Given("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    with When("I create a replicated table on each node"):
        table_name = "allow_zero_copy_replication_alter"
        for node in nodes:
            node.restart()
            replicated_table(
                node=node, table_name=table_name, columns="d UInt64, sign Int8"
            )

    with And("I add 20 Mb of data to the table"):
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
    try:
        with Given("I have a table"):
            node.query(
                f"""
            CREATE TABLE IF NOT EXISTS {table_name} ON CLUSTER 'sharded_cluster' (key UInt32, value1 String, value2 String, value3 String) engine=ReplicatedMergeTree('/{table_name}', '{{replica}}')
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
                "grep -A 1 r00000000000000000000 -R /var/lib/clickhouse/disks/external/store/ | grep -B 1 '\-0' | grep r00000000000000000000 | sort -k 2 | uniq -df 1"
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

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = self.context.zero_copy_replication_settings
        mergetree_config(settings=settings)

    try:
        with Given("I have a table"):
            node.query(
                f"""
            CREATE TABLE IF NOT EXISTS {table_name} ON CLUSTER 'sharded_cluster' (key UInt32, value1 String, value2 String, value3 String) engine=ReplicatedMergeTree('/{table_name}', '{{replica}}')
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

    with And("I have merge tree configuration set to use zero copy replication"):
        settings = {self.context.zero_copy_replication_setting: "1"}
        mergetree_config(settings=settings)

    try:
        with Given("I have a table"):
            node.query(
                f"""
            CREATE TABLE IF NOT EXISTS {table_name} ON CLUSTER 'sharded_cluster' (key UInt32, value1 String, value2 String, value3 String) engine=ReplicatedMergeTree('/{table_name}', '{{replica}}')
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
def outline(self):
    """Test S3 and S3 compatible storage through storage disks."""
    self.context.minio_enabled = self.context.storage == "minio"

    with Given("I have two S3 disks configured"):
        uri_tiered = self.context.uri + "tiered/"
        # /zero-copy-replication/
        disks = {
            "external": {
                "type": "s3",
                "endpoint": f"{self.context.uri}zero-copy-replication/",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
            "external_tiered": {
                "type": "s3",
                "endpoint": f"{uri_tiered}",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
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

        if self.context.object_storage_mode == "vfs":
            self.context.zero_copy_replication_settings = {}
            for disk_name in disks.keys():
                disks[disk_name]["allow_vfs"] = "1"
        else:
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

    with Check("bucket should be empty before test begins"):
        check_bucket_size(expected_size=0, tolerance=50)

    for scenario in loads(current_module(), Scenario):
        scenario()


@TestFeature
@Requirements(RQ_SRS_015_S3_AWS_AllowS3ZeroCopyReplication("1.0"))
@Name("zero copy replication")
def aws_s3(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "aws_s3"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key
    self.context.bucket_name = "altinity-qa-test"
    self.context.bucket_path = "data/zero-copy-replication"

    outline()


@TestFeature
@Requirements(RQ_SRS_015_S3_GCS_AllowS3ZeroCopyReplication("1.0"))
@Name("zero copy replication")
def gcs(self, uri, access_key, key_id, node="clickhouse1"):
    skip("GCS is not supported for zero copy replication")
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "gcs"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key
    self.context.bucket_name = None
    self.context.bucket_path = None

    outline()


@TestFeature
@Requirements(RQ_SRS_015_S3_MinIO_AllowS3ZeroCopyReplication("1.0"))
@Name("zero copy replication")
def minio(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "minio"
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret
    self.context.bucket_name = "root"
    self.context.bucket_path = "data/zero-copy-replication"

    outline()
