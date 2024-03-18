#!/usr/bin/env python3
import random
from itertools import combinations, chain

from testflows.core import *
from testflows.combinatorics import CoveringArray

from vfs.tests.steps import *
from vfs.requirements import *
from vfs.tests.stress_alter import optimize_random, check_consistency
from s3.tests.common import invalid_s3_storage_config


@TestScenario
@Requirements(
    RQ_SRS038_DiskObjectStorageVFS_IncompatibleSettings_ZeroCopyReplication("1.0")
)
def incompatible_with_zero_copy(self):
    """
    Check that using zero copy replication when vfs is enabled is not allowed.
    """
    with When("I create a replicated table with both vfs and 0-copy enabled"):
        r, _ = replicated_table_cluster(
            table_name="vfs_zero_copy_replication",
            storage_policy="external_vfs",
            allow_zero_copy=True,
            exitcode=None,
        )

    with Then("I expect it to fail"):
        assert r.exitcode != 0, error()


@TestScenario
@Requirements(RQ_SRS038_DiskObjectStorageVFS_IncompatibleSettings_SendMetadata("1.0"))
def incompatible_with_send_metadata(self):
    """
    Check that using send_metadata when vfs is enabled is not allowed.
    """
    with Given("a config with both allow_vfs=1 and send_metadata=1"):
        disks = {
            "external_bad": {
                "type": "s3",
                "endpoint": f"{self.context.uri}",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
                "list_object_keys_size": "1",
                "allow_vfs": "1",
                "send_metadata": "1",
            }
        }

    with Then("the config file fails to load"):
        invalid_s3_storage_config(
            disks=disks,
            policies={},
            message="DB::Exception: VFS doesn't support send_metadata",
        )


@TestStep(When)
def create_insert_measure_replicated_table(self, storage_policy="external"):
    """Create a table, insert to it, and return the change in s3 size."""

    nodes = self.context.ch_nodes
    n_rows = 100_000
    columns = "d UInt64, m UInt64"

    with Given("an s3 bucket with a known amount of data"):
        size_before = get_bucket_size(
            name=self.context.bucket_name,
            prefix=self.context.bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )

    with When("a replicated table is created successfully"):
        _, table_name = replicated_table_cluster(
            columns=columns, exitcode=0, storage_policy=storage_policy
        )

    with And("I add data to the table"):
        insert_random(
            node=nodes[0],
            table_name=table_name,
            columns=columns,
            rows=n_rows,
        )

    with And("I wait for the replicas to sync", flags=TE):
        sync_replica(node=nodes[1], table_name=table_name, timeout=300)
        sync_replica(node=nodes[2], table_name=table_name, timeout=300)
        kwargs = dict(table_name=table_name, rows=n_rows)
        retry(assert_row_count, timeout=120, delay=1)(node=nodes[0], **kwargs)
        retry(assert_row_count, timeout=120, delay=1)(node=nodes[1], **kwargs)
        retry(assert_row_count, timeout=120, delay=1)(node=nodes[2], **kwargs)

    with And("I get the size of the data added to s3"):
        size_after = get_bucket_size(
            name=self.context.bucket_name,
            prefix=self.context.bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )
        size = size_after - size_before

    return size


@TestScenario
@Tags("sanity")
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Settings_Disk("1.0"))
def disk_setting(self):
    """
    Check that allow_vfs can be enabled per disk.
    """
    with When("I measure the disk usage after create and insert without vfs"):
        for attempt in retries(timeout=120, delay=5):
            with attempt:
                size_no_vfs = create_insert_measure_replicated_table(
                    storage_policy="external_no_vfs"
                )
                assert size_no_vfs > 0, error()

    with When(
        "I measure the disk usage after create and insert with vfs config in one file"
    ):
        size_vfs = create_insert_measure_replicated_table(storage_policy="external_vfs")

    with Then("Data usage should be less than half compared to no vfs"):
        assert size_vfs <= size_no_vfs // 2, error()

    with Given("VFS is enabled for 'external' disk"):
        enable_vfs(disk_names=["external"])

    with When(
        "I measure the disk usage after create and insert with vfs config in a separate file"
    ):
        size_vfs = create_insert_measure_replicated_table(storage_policy="external")

    with Then("Data usage should be less than half compared to no vfs"):
        assert size_vfs <= size_no_vfs // 2, error()


@TestScenario
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Settings_VFSToggled("1.0"))
def disable_vfs_with_vfs_table(self):
    """
    Check that removing global allow_vfs=1 when a vfs table exists does not cause data to become inaccessible.
    """
    nodes = current().context.ch_nodes
    table_name = "my_replicated_vfs_table"

    with Check("create a table with VFS enabled"):
        with Given("I enable allow_vfs"):
            enable_vfs()

        with Given("I have a table with vfs"):
            replicated_table_cluster(
                table_name=table_name,
                storage_policy="external",
                columns="d UInt64",
            )

        with And("I insert some data"):
            insert_random(
                node=nodes[1], table_name=table_name, columns="d UInt64", rows=100
            )

        with Then("the data is accessible"):
            assert_row_count(node=nodes[1], table_name=table_name, rows=100)
            retry(assert_row_count, timeout=10, delay=1)(
                node=nodes[0], table_name=table_name, rows=100
            )

    with Check("access the table without VFS"):
        with When("VFS is no longer enabled"):
            check_vfs_state(node=nodes[0], enabled=False)

        with Then("the data remains accessible"):
            assert_row_count(node=nodes[0], table_name=table_name, rows=100)

        with When("I delete some data"):
            nodes[2].query(f"DELETE FROM {table_name} WHERE d=40")

        with Then("Not all data is deleted"):
            retry(assert_row_count, timeout=5, delay=1)(
                node=nodes[1], table_name=table_name, rows=99
            )


@TestScenario
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Settings_VFSToggled("1.0"))
def enable_vfs_with_non_vfs_table(self):
    """
    Check that globally enabling allow_vfs when a non-vfs table exists does not cause data to become inaccessible.
    """

    node = current().context.node

    with Given("VFS is not enabled"):
        check_vfs_state(enabled=False)

    with And("I have a table without vfs"):
        replicated_table_cluster(
            table_name="my_non_vfs_table",
            columns="d UInt64",
        )

    with And("I insert some data"):
        insert_random(
            node=node, table_name="my_non_vfs_table", columns="d UInt64", rows=1000000
        )
        assert_row_count(node=node, table_name="my_non_vfs_table", rows=1000000)

    with And("I enable allow_object_storage_vfs"):
        enable_vfs()

    with Then("the data remains accessible"):
        assert_row_count(node=node, table_name="my_non_vfs_table", rows=1000000)


@TestOutline(Scenario)
@Requirements(RQ_SRS038_DiskObjectStorageVFS_SharedSettings_SchemaInference("1.0"))
@Examples(
    "settings",
    [["schema_inference_use_cache_for_s3=1"], ["schema_inference_use_cache_for_s3=0"]],
)
def table_function(self, settings):
    """Check that S3 storage works correctly for both imports and exports
    when accessed using a table function and sharing a uri with a vfs disk.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri + "vfs/"
    node = current().context.node
    expected = "427"

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the first table {name_table1}"):
            node.query(f"INSERT INTO {name_table1} VALUES (427)")

        with When(f"I export the data to S3 using the table function"):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}syntax.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}  SETTINGS s3_truncate_on_insert=1"""
            )

        with And(f"I import the data from S3 into the second table {name_table2}"):
            node.query(
                f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}syntax.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64') 
                SETTINGS {settings}"""
            )

        with Then(
            f"""I check that a simple SELECT * query on the second table
                   {name_table2} returns matching data"""
        ):
            r = node.query(f"SELECT * FROM {name_table2} FORMAT CSV").output.strip()
            assert r == expected, error()

    finally:
        with Finally("I overwrite the S3 data with empty data"):
            with By(f"I drop the first table {name_table1}"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And(f"I create the table again {name_table1}"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d"""
                )

            with And(
                f"""I export the empty table {name_table1} to S3 at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}syntax.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1} SETTINGS s3_truncate_on_insert=1"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestStep
@Retry(timeout=10, delay=1)
def insert(self, table_name, settings):
    """Insert random data to a table."""
    node = random.choice(self.context.ch_nodes)
    with By(f"inserting rows to {table_name} on {node.name} with settings {settings}"):
        insert_random(node=node, table_name=table_name, settings=settings, rows=5000000)


@TestStep
@Retry(timeout=10, delay=1)
def select(self, table_name, settings=None):
    """Perform select queries on a random node."""
    node = random.choice(self.context.ch_nodes)
    if settings:
        settings = "SETTINGS " + settings
    for _ in range(random.randint(3, 10)):
        with By(f"count rows in {table_name} on {node.name}"):
            node.query(f"SELECT count() FROM {table_name} {settings}")


def combinations_all_lengths(items, min_size=1, max_size=None):
    """Get combinations for all possible combination sizes, up to a given limit."""
    if max_size is None:
        max_size = len(items)
    return chain(*[combinations(items, i) for i in range(min_size, max_size + 1)])


@TestOutline(Combination)
def check_setting_combination(
    self, table_setting, select_setting, insert_setting, storage_setting
):
    """Perform concurrent inserts and selects with a combination of settings."""

    if storage_setting is not None:
        with Given(f"storage with settings {storage_setting}"):
            storage_setting = storage_setting.split("=")
            disks = {
                "external": {
                    storage_setting[0]: storage_setting[1],
                }
            }
            s3_storage(disks=disks, restart=False, config_file="test_settings.xml")

    with Given("a replicated table"):
        _, table_name = replicated_table_cluster(
            storage_policy="external_vfs",
            exitcode=0,
            settings=table_setting,
        )

    with And("some inserted data"):
        insert(table_name=table_name, settings=insert_setting)

    When(
        f"I INSERT in parallel",
        test=insert,
        parallel=True,
        flags=TE,
    )(table_name=table_name, settings=insert_setting)
    When(
        f"I SELECT in parallel",
        test=select,
        parallel=True,
        flags=TE,
    )(table_name=table_name, settings=select_setting)
    When(
        f"I OPTIMIZE {table_name}",
        test=optimize_random,
        parallel=True,
        flags=TE,
    )(table_name=table_name)

    join()

    with Then("I check that the replicas are consistent", flags=TE):
        check_consistency(tables=[table_name])


@TestScenario
@Tags("long", "combinatoric")
@Requirements(
    RQ_SRS038_DiskObjectStorageVFS_SharedSettings_Mutation("0.0"),
    RQ_SRS038_DiskObjectStorageVFS_SharedSettings_S3("1.0"),
    RQ_SRS038_DiskObjectStorageVFS_SharedSettings_ReadBackoff("1.0"),
    RQ_SRS038_DiskObjectStorageVFS_SharedSettings_ConcurrentRead("1.0"),
)
def setting_combinations(self):
    """Perform concurrent inserts and selects with various settings."""
    settings = {
        "table_setting": (
            None,
            "remote_fs_execute_merges_on_single_replica_time_threshold=0",
            "zero_copy_concurrent_part_removal_max_split_times=2",
            "zero_copy_concurrent_part_removal_max_postpone_ratio=0.1",
            "zero_copy_merge_mutation_min_parts_size_sleep_before_lock=0",
        ),
        "select_setting": (
            None,
            "merge_tree_min_rows_for_concurrent_read_for_remote_filesystem=0",
            "merge_tree_min_bytes_for_concurrent_read_for_remote_filesystem=0",
        ),
        "insert_setting": (
            None,
            *[
                ",".join(c)
                for c in combinations_all_lengths(
                    [
                        "s3_truncate_on_insert=1",
                        "s3_create_new_file_on_insert=1",
                        "s3_skip_empty_files=1",
                        f"s3_max_single_part_upload_size={int(64*1024)}",
                    ],
                    min_size=2,
                    max_size=3,
                )
            ],
        ),
        "storage_setting": (
            None,
            "remote_fs_read_backoff_threshold=0",
            "remote_fs_read_backoff_max_tries=0",
        ),
    }

    covering_array_strength = len(settings) if self.context.stress else 2
    for config in CoveringArray(settings, strength=covering_array_strength):
        title = ",".join([f"{k}={v}" for k, v in config.items()])
        Combination(title, test=check_setting_combination)(**config)


@TestFeature
@Name("settings")
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Providers_Configuration("1.0"))
def feature(self):
    """Test interactions between VFS and other settings."""
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
