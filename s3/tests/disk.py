from testflows.core import *

from s3.tests.common import *
from s3.requirements import *
from lightweight_delete.tests.steps import insert

import time
import datetime

import lightweight_delete.tests.basic_checks as delete_basic_checks


@TestStep(Given)
def define_s3_disk_storage_configuration(
    self,
    uri=None,
    access_key_id=None,
    secret_access_key=None,
    options=None,
    disk_name="external",
):
    """Define S3 disk storage configuration with one
    S3 external disk.
    """
    if uri is None:
        uri = self.context.uri
    if access_key_id is None:
        access_key_id = self.context.access_key_id
    if secret_access_key is None:
        secret_access_key = self.context.secret_access_key
    if options is None:
        options = {}

    try:
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            disk_name: {
                "type": "s3",
                "endpoint": f"{uri}",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

        if hasattr(self.context, "s3_options"):
            disks["external"].update(self.context.s3_options)

        if options:
            disks["external"].update(options)

        yield disks

    finally:
        pass


@TestOutline
def truncate(self, table_name, node=None):
    """Check truncating table."""
    if node is None:
        node = self.context.node

    with When("I truncate the table"):
        node.query(f"TRUNCATE TABLE {table_name} SYNC")

    with Then("I check table is empty"):
        assert node.query(f"SELECT * FROM {table_name}").output == ""


@TestOutline
def gcs_truncate_err_log(self, table_name, node=None):
    """Check the error log when truncating table on GCS."""
    if node is None:
        node = self.context.node

    with Given("I note the error log size before the test."):
        cmd = node.command(
            f"stat --format=%s {'/var/log/clickhouse-server/clickhouse-server.err.log'}"
        )
        if (
            cmd.output
            == f"stat: cannot stat '/var/log/clickhouse-server/clickhouse-server.err.log': No such file or directory"
        ):
            start_logsize = 0
        else:
            start_logsize = cmd.output.split(" ")[0].strip()

    with When("I truncate the table"):
        node.query(f"TRUNCATE TABLE {table_name} SYNC")

    with Then("I check table is empty"):
        assert node.query(f"SELECT * FROM {table_name}").output == ""

    with When("I get error log size at the end of the test"):
        cmd = node.command(
            f"stat --format=%s '/var/log/clickhouse-server/clickhouse-server.err.log'"
        )
        end_logsize = cmd.output.split(" ")[0].strip()

    with Then("I check that no errors were added to the error log"):
        assert start_logsize == end_logsize, error()


@TestScenario
@Requirements()
def delete(self, use_alter_delete=True):
    """Check that data can be deleted when stored in S3
    using ALTER DELETE or TRUNCATE.
    """
    name = "table_" + getuid()
    self.context.use_alter_delete = use_alter_delete
    self.context.table_engine = "MergeTree"
    node = self.context.node

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume()

    if self.context.storage == "gcs":
        tests = [gcs_truncate_err_log]
    else:
        tests = [truncate]

    tests += loads(delete_basic_checks, Outline)

    for outline in tests:
        with Scenario(test=outline):
            with Given(f"""I create table using S3 storage policy external"""):
                s3_table(table_name=name, policy="external")

            with And("I insert many partitions and many small parts"):
                insert(
                    table_name=name,
                    partitions=10,
                    parts_per_partition=100,
                    block_size=10,
                )

            outline(table_name=name)


@TestScenario
@Requirements(RQ_SRS_015_S3_Import("1.0"))
def imports(self):
    """Check that ClickHouse can import data from S3 storage using both S3
    storage disks and the S3 table function.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    node = current().context.node
    uri = self.context.uri
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    expected = "123456"

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume()

    try:
        with Given(f"I create table using S3 storage policy external"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='external'
            """
            )

        with And("I store simple data in S3 to check import"):
            node.query(f"INSERT INTO {name_table1} VALUES ({expected})")

        with Then("I check that a simple import from S3 returns matching data"):
            r = node.query(f"SELECT * FROM {name_table1}").output.strip()
            assert r == expected, error()

        with Given("I create a second table for table function comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I delete the data from the first table"):
            with By("I drop the first table"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And("I create the first table again"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                """
                )

        with And(f"I store simple data in the first table {name_table1}"):
            node.query(f"INSERT INTO {name_table1} VALUES ({expected})")

        if self.context.storage == "minio":
            with Given("I alter the URL for MinIO table function path restrictions"):
                uri = uri[: len(uri) - 5] + "/imports"

        with When("I export the data to S3 using the table function"):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}imports.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}"""
            )

        with And(f"I import the data from S3 into the second table {name_table2}"):
            node.query(
                f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}imports.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')"""
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
                        s3('{uri}imports.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_Export("1.0"))
def exports(self):
    """Check that ClickHouse can export data to S3 storage using both S3
    storage disks and the S3 table function.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node
    expected = "654321"

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume()

    try:
        with Given(f"I create table using S3 storage policy external"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='external'
            """
            )

        with And("I export simple data to S3 to check export functionality"):
            node.query(f"INSERT INTO {name_table1} VALUES ({expected})")

        with Then("I check that a simple SELECT * query returns matching data"):
            r = node.query(f"SELECT * FROM {name_table1}").output.strip()
            assert r == expected, error()

        with Given("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I delete the data from the first table"):
            with By("I drop the first table"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And("I create the first table again"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                """
                )

        with And(f"I store simple data in the first table {name_table1}"):
            node.query(f"INSERT INTO {name_table1} VALUES ({expected})")

        if self.context.storage == "minio":
            with Given("I alter the URL for MinIO table function path restrictions"):
                uri = uri[: len(uri) - 5] + "exports"

        with When("I export the data to S3 using the table function"):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}exports.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}"""
            )

        with And(f"I import the data from S3 into the second table {name_table2}"):
            node.query(
                f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}exports.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')"""
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
                        s3('{uri}exports.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_DataParts("1.0"))
def wide_parts(self):
    """Check that data can be stored in S3 using only wide data parts."""
    name = "table_" + getuid()
    part_types = None
    node = current().context.node
    value = "427"

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume()

    try:
        with Given(
            f"""I create table using S3 storage policy external,
                    min_bytes_for_wide_parts set to 0"""
        ):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='external',
                min_bytes_for_wide_part=0
            """
            )

        with When("I store simple data in the table"):
            node.query(f"INSERT INTO {name} VALUES ({value})")

        with And("I get the part types for the data added in this table"):
            part_types = node.query(
                f"SELECT part_type FROM system.parts WHERE table = '{name}'"
            ).output.splitlines()

        with Then("The part type should be Wide"):
            for _type in part_types:
                assert _type == "Wide", error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_DataParts("1.0"))
def compact_parts(self):
    """Check that data can be stored in S3 using only compact data parts."""
    name = "table_" + getuid()
    part_types = None
    node = current().context.node
    value = "427"

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume()

    try:
        with Given(
            f"""I create table using S3 storage policy external,
                    min_bytes_for_wide_parts set to a very large value"""
        ):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='external',
                min_bytes_for_wide_part=100000
            """
            )

        with When("I store simple data in the table, stored as compact parts"):
            node.query(f"INSERT INTO {name} VALUES ({value})")

        with And("I get the part types for the data added in this table"):
            part_types = node.query(
                f"SELECT part_type FROM system.parts WHERE table = '{name}'"
            ).output.splitlines()

        with Then("The part type should be Compact"):
            for _type in part_types:
                assert _type == "Compact", error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_Changes_NoRestart("1.0"))
def restart(self):
    """Check that S3 storage configuration changes shall be applied without
    restarting the ClickHouse server.
    """

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume(restart=False)

    with When("I check the configuration works"):
        standard_check()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Metadata("1.0"))
def metadata(self):
    """Check that ClickHouse creates metadata for S3 disks in the correct
    directory locally. Check that the disk name matches the disk used in the
    storage policy.
    """
    name = "table_" + getuid()
    disk_name = "external"
    disk_names = None
    disk_paths = None
    node = current().context.node

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume()

    with And(f"I create table using S3 storage policy external"):
        simple_table(name=name)

    with When("I add data to the table"):
        with By("first inserting 1MB of data"):
            insert_data(name=name, number_of_mb=1)

        with And("another insert of 1MB of data"):
            insert_data(name=name, number_of_mb=1, start=1024 * 1024)

        with And("then doing a large insert of 10Mb of data"):
            insert_data(name=name, number_of_mb=10, start=1024 * 1024 * 2)

    with And("I get the disk name for the parts added in this table"):
        disk_names = node.query(
            f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
        ).output.splitlines()

    with Then("The disk name should match the disk selected by the 'external' policy"):
        for _name in disk_names:
            assert _name == f"{disk_name}", error()

    with When("I get the path for the parts added in this table"):
        disk_paths = node.query(
            f"SELECT path FROM system.parts WHERE table = '{name}'"
        ).output.splitlines()

    with Then(
        f"The paths for each data part should start with /var/lib/clickhouse/disks/{disk_name}/store/"
    ):
        for path in disk_paths:
            assert path.startswith(
                f"/var/lib/clickhouse/disks/{disk_name}/store/"
            ), error()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MultipleStorageDevices("1.0"))
def multiple_storage(self):
    """Check that ClickHouse S3 disks and policies can be configured such that
    a policy can use multiple S3 disks at the same time.
    """
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    disks = None
    policies = None
    node = current().context.node

    def insert_data_time(number_of_mb, time, start=0):
        values = ",".join(
            f"({x},{time})"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {name} VALUES {values}")

    if self.context.storage == "minio":
        with Given("I edit the Minio URI to avoid path conflicts"):
            uri = uri[: len(uri) - 5] + "multiple-storage/"

    with Given("I have a disk configuration with two S3 storage disks"):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "first_external": {
                "type": "s3",
                "endpoint": f"{uri}subdata1/",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
            "second_external": {
                "type": "s3",
                "endpoint": f"{uri}subdata2/",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

        if hasattr(self.context, "s3_options"):
            disks["first_external"].update(self.context.s3_options)
            disks["second_external"].update(self.context.s3_options)

    with And("I have a storage policy configured to use both S3 disks at once"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {
                "volumes": {
                    "default": {"disk": "first_external"},
                    "external": {"disk": "second_external"},
                }
            },
        }

    with s3_storage(disks, policies, restart=True):
        try:
            with Given(f"I create table using S3 storage policy external"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        d UInt64,
                        d1 DateTime
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    TTL d1 + interval 2 day to volume 'external'
                    SETTINGS storage_policy='external'
                """
                )

            with When("I add data to the table"):
                with By("first inserting 1MB of data"):
                    tm = time.mktime(
                        (datetime.date.today() - datetime.timedelta(days=7)).timetuple()
                    )
                    insert_data_time(1, tm, 0)

                with And("another insert of 1MB of data"):
                    tm = time.mktime(
                        (datetime.date.today() - datetime.timedelta(days=7)).timetuple()
                    )
                    insert_data_time(1, tm, 1024 * 1024)

                with And("then doing a large insert of 10Mb of data"):
                    tm = time.mktime(datetime.date.today().timetuple())
                    insert_data_time(10, tm, 1024 * 1024 * 2)

            with Then(
                """I get the name of all partitions for all data parts
                      in this table"""
            ):
                disk_names = node.query(
                    f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                ).output.splitlines()

            with And("""I check the names to make sure both disks are used"""):
                assert (
                    "first_external" in disk_names and "second_external" in disk_names
                ), error()

        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MultipleStorageDevices_NoChangesForQuerying("1.0"))
def multiple_storage_query(self):
    """Check that when policies and disks are configured such that a policy uses
    multiple S3 storage disks, queries using the policy can be formatted the
    same way as queries using any other policy.
    """
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    disks = None
    policies = None
    node = current().context.node

    def insert_data_time(number_of_mb, time, start=0):
        values = ",".join(
            f"({x},{time})"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {name} VALUES {values}")

    if self.context.storage == "minio":
        with Given("I edit the Minio URI to avoid path conflicts"):
            uri = uri[: len(uri) - 5] + "multiple-storage/"

    with Given("I have a disk configuration with two S3 storage disks"):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "first_external": {
                "type": "s3",
                "endpoint": f"{uri}subdata1/",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
            "second_external": {
                "type": "s3",
                "endpoint": f"{uri}subdata2/",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

        if hasattr(self.context, "s3_options"):
            disks["first_external"].update(self.context.s3_options)
            disks["second_external"].update(self.context.s3_options)

    with And("I have a storage policy configured to use both S3 disks at once"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {
                "volumes": {
                    "default": {"disk": "first_external"},
                    "external": {"disk": "second_external"},
                }
            },
        }

    with s3_storage(disks, policies, restart=True):
        try:
            with Given(f"I create table using S3 storage policy external"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        d UInt64,
                        d1 DateTime
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    TTL d1 + interval 2 day to volume 'external'
                    SETTINGS storage_policy='external'
                """
                )

            with When("I add data to the table"):
                with By("first inserting 1MB of data"):
                    tm = time.mktime(
                        (datetime.date.today() - datetime.timedelta(days=7)).timetuple()
                    )
                    insert_data_time(1, tm, 0)

                with And("another insert of 1MB of data"):
                    tm = time.mktime(
                        (datetime.date.today() - datetime.timedelta(days=7)).timetuple()
                    )
                    insert_data_time(1, tm, 1024 * 1024)

                with And("then doing a large insert of 10Mb of data"):
                    tm = time.mktime(datetime.date.today().timetuple())
                    insert_data_time(10, tm, 1024 * 1024 * 2)

            with Then(
                """I get the name of all partitions for all data parts
                      in this table"""
            ):
                disk_names = node.query(
                    f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                ).output.splitlines()

            with And("""I check the names to make sure both disks are used"""):
                assert (
                    "first_external" in disk_names and "second_external" in disk_names
                ), error()

            with Then("I check simple queries"):
                check_query(
                    num=0, query=f"SELECT COUNT() FROM {name}", expected="1572867"
                )
                check_query(
                    num=1,
                    query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
                    expected="10",
                )
                check_query(
                    num=2,
                    query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
                    expected="3407872",
                )
                check_query(
                    num=3,
                    query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
                    expected="0",
                )

        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_AddingMoreStorageDevices("1.0"))
def add_storage(self):
    """Check that the user can add S3 storage devices to ClickHouse."""
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    disks = None
    policies = None
    node = current().context.node
    expected = "212"

    if self.context.storage == "minio":
        with Given("I edit the Minio URI to avoid path conflicts"):
            uri = uri[: len(uri) - 5] + "/add-storage/"

    with Given("I have a disk configuration with one S3 storage disk"):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "first_external": {
                "type": "s3",
                "endpoint": f"{uri}subdata1/",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

        if hasattr(self.context, "s3_options"):
            disks["first_external"].update(self.context.s3_options)

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {"volumes": {"external1": {"disk": "first_external"}}},
        }

    with s3_storage(disks, policies, restart=True):
        try:
            with Given(f"I create table using S3 storage policy external"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    SETTINGS storage_policy='external'
                """
                )

            with When("I store simple data in the table"):
                node.query(f"INSERT INTO {name} VALUES ({expected})")

            with Then("I check that a simple SELECT * query returns matching data"):
                r = node.query(f"SELECT * FROM {name}").output.strip()
                assert r == expected, error()

        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")

    with Given("I add a disk to the disk configuration"):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "first_external": {
                "type": "s3",
                "endpoint": f"{uri}subdata1/",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
            "second_external": {
                "type": "s3",
                "endpoint": f"{uri}subdata2/",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

        if hasattr(self.context, "s3_options"):
            disks["first_external"].update(self.context.s3_options)
            disks["second_external"].update(self.context.s3_options)

    with And("I have a storage policy configured to use the new S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {"volumes": {"external": {"disk": "second_external"}}},
        }

    with s3_storage(disks, policies, restart=True):
        try:
            with Given(f"I create table using S3 storage policy external"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    SETTINGS storage_policy='external'
                """
                )

            with When("I store simple data in the table"):
                node.query(f"INSERT INTO {name} VALUES ({expected})")

            with Then("I check that a simple SELECT * query returns matching data"):
                r = node.query(f"SELECT * FROM {name}").output.strip()
                assert r == expected, error()

        finally:
            with Finally("I drop the table if exists"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_RemoteHostFilter("1.0"))
def remote_host_filter(self):
    """Check that the remote host filter can be used to block access to bucket
    URLs provided in the S3 disk configuration.
    """
    urls = None

    with Given("I have a list of urls to allow access"):
        urls = {}

    with remote_host_filter_config(urls=urls, restart=True):
        with Given("I update the config to have s3 and local disks"):
            default_s3_disk_and_volume()

        with When("I check the configuration works"):
            standard_check()


@TestScenario
@Requirements(
    RQ_SRS_015_S3_Disk_Configuration_Syntax("1.0"), RQ_SRS_015_S3_Policy_Syntax("1.0")
)
def syntax(self):
    """Check that S3 disk storage configuration with valid syntax can be used
    to import and export data from ClickHouse when the storage disk is selected
    using a storage policy with valid syntax.
    """
    name = "table_" + getuid()

    with Given(
        """I have a disk configuration with a S3 storage disk, access id and key"""
    ):
        default_s3_disk_and_volume()

    with Given(f"I create table using S3 storage policy external"):
        simple_table(name=name)

    with When("I add data to the table"):
        with By("first inserting 1MB of data"):
            insert_data(name=name, number_of_mb=1)

        with And("another insert of 1MB of data"):
            insert_data(name=name, number_of_mb=1, start=1024 * 1024)

        with And("then doing a large insert of 10Mb of data"):
            insert_data(name=name, number_of_mb=10, start=1024 * 1024 * 2)

    with Then("I check simple queries"):
        check_query(num=0, query=f"SELECT COUNT() FROM {name}", expected="1572867")
        check_query(
            num=1,
            query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
            expected="10",
        )
        check_query(
            num=2,
            query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
            expected="3407872",
        )
        check_query(
            num=3,
            query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
            expected="0",
        )
        check_query(
            num=4,
            query=f"SELECT * FROM {name} WHERE d == 0 OR d == 1048578 OR d == 2097154 ORDER BY d",
            expected="0\n1048578\n2097154",
        )
        check_query(
            num=5,
            query=f"SELECT * FROM (SELECT d FROM {name} WHERE d == 1)",
            expected="1",
        )


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_Access("1.0"))
def access(self):
    """Check that ClickHouse S3 disk can be configured with the
    skip_access_check parameter set to 0 when ClickHouse has access to
    the corresponding endpoint.
    """

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume(settings={"skip_access_check": "0"})

    with When("I check the configuration works"):
        standard_check()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_Access("1.0"))
def access_skip_check(self):
    """Check that ClickHouse S3 disk can be configured with the
    skip_access_check parameter set to 1 when ClickHouse has access to
    the corresponding endpoint.
    """
    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume(settings={"skip_access_check": "1"})

    with When("I check the configuration works"):
        standard_check()


@TestOutline(Scenario)
@Examples("cache", [("0", Name("cache disabled")), ("1", Name("cache enabled"))])
@Requirements(RQ_SRS_015_S3_Disk_Configuration_CacheEnabled("1.0"))
def cache(self, cache):
    """Check that the <cache_enabled> parameter to the S3 disk configuration
    works as expected by setting the parameter to each of the allowed boolean
    values and checking the local cache location after storing data in the
    corresponding S3 disk.
    """
    name = "table_" + getuid()
    node = current().context.node

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume(settings={"data_cache_enabled": cache}, restart=True)

    with Given(f"I create table using S3 storage policy external"):
        simple_table(name=name, policy="s3_cache")

    with When("I add data to the table"):
        with By("first inserting 1MB of data"):
            insert_data(name=name, number_of_mb=1)

        with And("another insert of 1MB of data"):
            insert_data(name=name, number_of_mb=1, start=1024 * 1024)

        with And("then doing a large insert of 10Mb of data"):
            insert_data(name=name, number_of_mb=10, start=1024 * 1024 * 2)

    with When("I get the path for the parts added in this table"):
        if check_clickhouse_version(">=22.8")(self):
            disk_paths = node.query(
                f"SELECT cache_path FROM system.filesystem_cache"
            ).output.splitlines()

            with And("I select from the table to generate the cache"):
                node.query(f"SELECT * FROM {name} FORMAT Null")
        else:
            disk_paths = node.query(
                f"SELECT path FROM system.parts WHERE table = '{name}'"
            ).output.splitlines()

    with Then(
        """I check that a cache directory exists for each of the
                parts added"""
    ):
        for path in disk_paths:
            idx = path.index("/store")
            if check_clickhouse_version("=22.7")(self):
                cache_path = path[:idx] + "/cache" + path[idx:-10] + "detached/"
            elif check_clickhouse_version(">=22.8")(self):
                cache_path = "/var/lib/clickhouse/cores/" + path
            else:
                cache_path = path[:idx] + "/cache" + path[idx:]
            out = node.command(
                f'if [ -d "{cache_path}" ]; then echo 1; else echo 0; fi;'
            ).output
            assert out == f"{cache}", error()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_CacheEnabled_Default("1.0"))
def cache_default(self):
    """Check that when S3 storage disks are used, ClickHouse caches the data
    locally by default.
    """
    name = "table_" + getuid()
    node = current().context.node

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with Given(f"I create table using S3 storage policy external"):
        simple_table(name=name)

    with When("I add data to the table"):
        with By("first inserting 1MB of data"):
            insert_data(name=name, number_of_mb=1)

        with And("another insert of 1MB of data"):
            insert_data(name=name, number_of_mb=1, start=1024 * 1024)

        with And("then doing a large insert of 10Mb of data"):
            insert_data(name=name, number_of_mb=10, start=1024 * 1024 * 2)

    with When("I get the path for the parts added in this table"):
        if check_clickhouse_version(">=22.8")(self):
            disk_paths = node.query(
                f"SELECT cache_path FROM system.filesystem_cache"
            ).output.splitlines()

            with And("I select from the table to generate the cache"):
                node.query(f"SELECT * FROM {name} FORMAT Null")
        else:
            disk_paths = node.query(
                f"SELECT path FROM system.parts WHERE table = '{name}'"
            ).output.splitlines()

    with Then(
        """I check that a cache directory exists for each of the
                parts added"""
    ):
        for path in disk_paths:
            idx = path.index("/store")
            if check_clickhouse_version("=22.7")(self):
                cache_path = path[:idx] + "/cache" + path[idx:-10] + "detached/"
            elif check_clickhouse_version(">=22.8")(self):
                cache_path = "/var/lib/clickhouse/cores/" + path
            else:
                cache_path = path[:idx] + "/cache" + path[idx:]
            out = node.command(
                f'if [ -d "{cache_path}" ]; then echo 1; else echo 0; fi;'
            ).output
            assert out == "1", error()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_CachePath("1.0"))
def cache_path(self):
    """Check that the cache path parameter to the S3 storage disk can be used
    to change the location of the cache.
    """
    name = "table_" + getuid()
    node = current().context.node

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume(
            settings={
                "cache_path": "/var/lib/clickhouse/disks/external/other_cache/subdirectory/"
            }
        )

    with Given(f"I create table using S3 storage policy external"):
        simple_table(name=name)

    with When("I add data to the table"):
        with By("first inserting 1MB of data"):
            insert_data(name=name, number_of_mb=1)

        with And("another insert of 1MB of data"):
            insert_data(name=name, number_of_mb=1, start=1024 * 1024)

        with And("then doing a large insert of 10Mb of data"):
            insert_data(name=name, number_of_mb=10, start=1024 * 1024 * 2)

    with When("I get the path for the parts added in this table"):
        if check_clickhouse_version(">=22.8")(self):
            disk_paths = node.query(
                f"SELECT cache_path FROM system.filesystem_cache"
            ).output.splitlines()

            with And("I select from the table to generate the cache"):
                node.query(f"SELECT * FROM {name} FORMAT Null")
        else:
            disk_paths = node.query(
                f"SELECT path FROM system.parts WHERE table = '{name}'"
            ).output.splitlines()

    with Then(
        """I check that a cache directory exists in the specified
                location for each of the parts added"""
    ):
        for path in disk_paths:
            idx = path.index("/store")
            if check_clickhouse_version(">=22.7")(self):
                cache_path = (
                    path[:idx]
                    + "/other_cache/subdirectory"
                    + path[idx:-10]
                    + "detached/"
                )
            elif check_clickhouse_version(">=22.8")(self):
                cache_path = "/var/lib/clickhouse/cores/" + path
            else:
                cache_path = path[:idx] + "/other_cache/subdirectory" + path[idx:]
            out = node.command(
                f'if [ -d "{cache_path}" ]; then echo 1; else echo 0; fi;'
            ).output
            assert out == "1", error()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_MinBytesForSeek_Syntax("1.0"))
def min_bytes_for_seek_syntax(self):
    """Check that S3 disk storage works correctly when <min_bytes_for_seek>
    parameter is set.
    """
    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume(settings={"min_bytes_for_seek": "4"})

    with When("I check the configuration works"):
        standard_check()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_S3MaxSinglePartUploadSize_Syntax("1.0"))
def max_single_part_upload_size_syntax(self):
    """Check that S3 disk storage works correctly when
    <s3_max_single_part_upload_size> parameter to the disk configuration is set.
    """
    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume(settings={"s3_max_single_part_upload_size": "0"})

    with When("I check the configuration works"):
        standard_check()


@TestScenario
@Requirements(
    RQ_SRS_015_S3_AWS_Disk_URL("1.0"), RQ_SRS_015_S3_AWS_Disk_URL_Generic("1.0")
)
def generic_url(self):
    """Check that AWS S3 disk storage works correctly when generic
    endpoint URL is provided in the disk configuration.
    """
    if self.context.storage != "aws_s3":
        skip("only for AWS S3")

    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    disks = None
    policies = None
    node = current().context.node
    expected = "427"

    with Given("I have a disk configuration with a S3 storage disk"):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "aws": {
                "type": "s3",
                "endpoint": "https://altinity-qa-test.s3.amazonaws.com/data/",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "aws_external": {"volumes": {"external": {"disk": "aws"}}},
        }

    with Then("Generic URL is currently treated as invalid configuration"):
        fail(
            """Generic URL is treated as invalid configuration, ClickHouse
             will not start if config is added"""
        )

    with s3_storage(disks, policies, restart=True):
        try:
            with Given(f"I create table using S3 storage policy aws_external"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    SETTINGS storage_policy='aws_external'
                """
                )

            with When("I store simple data in the table"):
                node.query(f"INSERT INTO {name} VALUES (427)")

            with Then("I check that a simple SELECT * query returns matching data"):
                r = node.query(f"SELECT * FROM {name}").output.strip()
                assert r == expected, error()

        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(
    RQ_SRS_015_S3_AWS_Disk_URL("1.0"), RQ_SRS_015_S3_AWS_Disk_URL_Specific("1.0")
)
def specific_url(self):
    """Check that AWS S3 disk storage works correctly when region-specific
    endpoint URL is provided in the disk configuration.
    """
    if self.context.storage != "aws_s3":
        skip("only for AWS S3")

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    with When("I check the configuration works"):
        standard_check()


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_S3UseEnvironmentCredentials("1.0"))
def environment_credentials(self):
    """Check that AWS S3 disk storage works correctly when server-level credentials
    are provided, and used by the disk by setting <use_environment_credentials>
    to true.
    """
    name = "table_" + getuid()
    disks = None
    policies = None
    endpoints = None
    node = current().context.node
    expected = "427"

    with Given("I have server-level environment credentials set for my endpoint"):
        endpoints = {
            "my_endpoint": {
                "endpoint": f"{self.context.uri}",
                "use_environment_credentials": "1",
            }
        }

        if hasattr(self.context, "s3_options"):
            endpoints["my_endpoint"].update(self.context.s3_options)

    with And(
        """I have a S3 storage disk with <use_environment_credentials>
             parameter set to true"""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "external": {
                "type": "s3",
                "endpoint": f"{self.context.uri}",
                "use_environment_credentials": "1",
            },
        }

        if hasattr(self.context, "s3_options"):
            disks["external"].update(self.context.s3_options)

    with And(f"I have a storage policy configured to use the S3 disk debug"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "s3_external": {"volumes": {"external": {"disk": "external"}}},
        }

    with s3_env_credentials(endpoints=endpoints, restart=True):
        with s3_storage(disks, policies, restart=True):
            try:
                with Given(f"I create table using S3 storage policy s3_external"):
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            d UInt64
                        ) ENGINE = MergeTree()
                        ORDER BY d
                        SETTINGS storage_policy='s3_external'
                    """
                    )

                with When("I store simple data in the table"):
                    node.query(f"INSERT INTO {name} VALUES ({expected})")

                with Then("I check that a simple SELECT * query returns matching data"):
                    r = node.query(f"SELECT * FROM {name}").output.strip()
                    assert r == expected, error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestOutline(Scenario)
@Examples(
    "engine",
    [
        ("MergeTree", Name("MergeTree")),
        ("ReplacingMergeTree", Name("ReplacingMergeTree")),
        ("SummingMergeTree", Name("SummingMergeTree")),
        ("AggregatingMergeTree", Name("AggregatingMergeTree")),
    ],
)
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_MergeTree("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_ReplacingMergeTree("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_SummingMergeTree("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_AggregatingMergeTree("1.0"),
)
def mergetree(self, engine):
    """Check that different MergeTree engines can be used to select S3 storage
    disks when tables are created.
    """
    name = "table_" + getuid()
    node = current().context.node

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    try:
        with Given(
            f"""I create table using the {engine} engine and S3
                    storage policy external"""
        ):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = {engine}()
                ORDER BY d
                SETTINGS storage_policy='external'
            """
            )

        with When("I add data to the table"):
            with By("first inserting 1MB of data"):
                insert_data(name=name, number_of_mb=1)

            with And("another insert of 1MB of data"):
                insert_data(name=name, number_of_mb=1, start=1024 * 1024)

            with And("then doing a large insert of 10Mb of data"):
                insert_data(name=name, number_of_mb=10, start=1024 * 1024 * 2)

        with Then("I check simple queries"):
            check_query(num=0, query=f"SELECT COUNT() FROM {name}", expected="1572867")
            check_query(
                num=1,
                query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
                expected="10",
            )
            check_query(
                num=2,
                query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
                expected="3407872",
            )
            check_query(
                num=3,
                query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
                expected="0",
            )
            check_query(
                num=4,
                query=f"SELECT * FROM {name} WHERE d == 0 OR d == 1048578 OR d == 2097154 ORDER BY d",
                expected="0\n1048578\n2097154",
            )
            check_query(
                num=5,
                query=f"SELECT * FROM (SELECT d FROM {name} WHERE d == 1)",
                expected="1",
            )

    finally:
        with Finally("I drop the table if exists"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_CollapsingMergeTree("1.0"))
def mergetree_collapsing(self):
    """Check that the CollapsingMergeTree engine can be used to select S3
    storage disks when tables are created.
    """
    name = "table_" + getuid()
    node = current().context.node

    def insert_data_mtc(number_of_mb, start=0):
        values = ",".join(
            f"({x},1)"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {name} VALUES {values}")

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    try:
        with Given(
            f"""I create table using the CollapsingMergeTree engine
                    and S3 storage policy external"""
        ):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64,
                    sign Int8
                ) ENGINE = CollapsingMergeTree(sign)
                ORDER BY d
                SETTINGS storage_policy='external'
            """
            )

        with When("I add data to the table"):
            with By("first inserting 1MB of data"):
                insert_data_mtc(number_of_mb=1)

            with And("another insert of 1MB of data"):
                insert_data_mtc(number_of_mb=1, start=1024 * 1024)

            with And("then doing a large insert of 10Mb of data"):
                insert_data_mtc(number_of_mb=10, start=1024 * 1024 * 2)

        with Then("I check simple queries"):
            check_query(num=0, query=f"SELECT COUNT() FROM {name}", expected="1572867")
            check_query(
                num=1,
                query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
                expected="10",
            )
            check_query(
                num=2,
                query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
                expected="3407872",
            )
            check_query(
                num=3,
                query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
                expected="0",
            )

    finally:
        with Finally("I drop the table if exists"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_MergeTree_VersionedCollapsingMergeTree("1.0"))
def mergetree_versionedcollapsing(self):
    """Check that the VersionedCollapsingMergeTree engine can be used to select S3
    storage disks when tables are created.
    """
    name = "table_" + getuid()
    node = current().context.node

    def insert_data_mtvc(number_of_mb, start=0):
        values = ",".join(
            f"({x},1,1)"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {name} VALUES {values}")

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume()

    try:
        with Given(
            f"""I create table using the VersionedCollapsingMergeTree
                    engine and S3 storage policy external"""
        ):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64,
                    sign Int8,
                    version UInt64
                ) ENGINE = VersionedCollapsingMergeTree(sign, version)
                ORDER BY d
                SETTINGS storage_policy='external'
            """
            )

        with When("I add data to the table"):
            with By("first inserting 1MB of data"):
                insert_data_mtvc(number_of_mb=1)

            with And("another insert of 1MB of data"):
                insert_data_mtvc(number_of_mb=1, start=1024 * 1024)

            with And("then doing a large insert of 10Mb of data"):
                insert_data_mtvc(number_of_mb=10, start=1024 * 1024 * 2)

        with Then("I check simple queries"):
            check_query(num=0, query=f"SELECT COUNT() FROM {name}", expected="1572867")
            check_query(
                num=1,
                query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
                expected="10",
            )
            check_query(
                num=2,
                query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
                expected="3407872",
            )
            check_query(
                num=3,
                query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
                expected="0",
            )

    finally:
        with Finally("I drop the table if exists"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_Performance_PerformTTLMoveOnInsert("1.0"))
def performance_ttl_move(self):
    """Check performance of inserts to tables on S3 disks when perform ttl move
    on insert parameter is set to a positive value when comparing to the case
    when perform ttl move on insert parameter is turned off.
    """
    name = "table_" + getuid()
    disks = None
    policies = None
    ttl_time = None
    no_ttl_time = None
    node = current().context.node

    def insert_data_time(number_of_mb, start=0):
        now = time.mktime(datetime.datetime.today().timetuple())
        values = ",".join(
            f"({x},{now})"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        start_time = time.time()
        node.query(f"INSERT INTO {name} VALUES {values}")
        end_time = time.time()
        return end_time - start_time

    with Given("I have a disk configuration with a S3 storage disk"):
        disks = define_s3_disk_storage_configuration()

    with And(
        f"""I have a tiered S3 storage policy with perform_ttl_move_on_insert
             parameter set to 0 and an unchanged tiered storage policy for
             comparison"""
    ):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "tiered": {
                "volumes": {
                    "default": {"disk": "default"},
                    "external": {"disk": "external", "perform_ttl_move_on_insert": "1"},
                }
            },
            "tiered_bg": {
                "volumes": {
                    "default": {"disk": "default"},
                    "external": {"disk": "external", "perform_ttl_move_on_insert": "0"},
                }
            },
        }

    with s3_storage(disks, policies, restart=True):
        try:
            with Given(f"I create a table"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        d UInt64,
                        d1 DateTime
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    TTL d1 + interval 0 second to volume 'external'
                    SETTINGS storage_policy='tiered'
                """
                )

            with Then("I add 40 Mb of data to the table and save the time taken"):
                ttl_time = insert_data_time(40, 1024 * 1024 * 2)
                metric("export_40Mb_ttl", units="seconds", value=str(ttl_time))

            with And("I create the table again with the other policy"):
                with By("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")

                with And("I create the table again"):
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            d UInt64,
                            d1 DateTime
                        ) ENGINE = MergeTree()
                        ORDER BY d
                        TTL d1 + interval 0 second to volume 'external'
                        SETTINGS storage_policy='tiered_bg'
                    """
                    )

            with Then("I add 40 Mb of data to the table and save the time taken"):
                no_ttl_time = insert_data_time(40, 1024 * 1024 * 2)
                metric("export_40Mb_no_ttl", units="seconds", value=str(no_ttl_time))

            with And("I log the performance improvement as a percentage"):
                metric(
                    "percentage_improvement",
                    units="%",
                    value=str(100 * (ttl_time - no_ttl_time) / no_ttl_time),
                )
        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestOutline(Scenario)
@Examples("bool_value", [("0", Name("no ttl move")), ("1", Name("ttl move"))])
@Requirements(RQ_SRS_015_S3_Policy_PerformTTLMoveOnInsert("1.0"))
def perform_ttl_move_on_insert(self, bool_value):
    """Check that ClickHouse works correctly when importing and exporting data
    to/from S3 storage with a tiered storage policy with perform_ttl_move_on_insert
    parameter set. If 0, ClickHouse shall perform ttl moves to the S3 disk in the
    background, otherwise, ClickHouse shall perform ttl moves upon insert.
    """
    name = "table_" + getuid()
    disks = None
    policies = None
    node = current().context.node
    expected = "427"

    with Given("I have a disk configuration with a S3 storage disk"):
        disks = define_s3_disk_storage_configuration()

    with And(
        f"""I have a tiered S3 storage policy with perform_ttl_move_on_insert
             parameter set to {bool_value}"""
    ):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "tiered": {
                "volumes": {
                    "default": {"disk": "default"},
                    "external": {
                        "disk": "external",
                        "perform_ttl_move_on_insert": f"{bool_value}",
                    },
                }
            },
        }

    with s3_storage(disks, policies, restart=True):
        try:
            with Given(f"I create table using S3 storage policy tiered"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        d UInt64,
                        d1 DateTime
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    TTL d1 + interval 0 second to volume 'external'
                    SETTINGS storage_policy='tiered'
                """
                )

            with When("I store simple data in the table"):
                now = time.mktime(datetime.datetime.today().timetuple())
                node.query(f"INSERT INTO {name} VALUES ({expected}, {now})")

            with Then("I check that a simple SELECT * query returns matching data"):
                r = node.query(f"SELECT d FROM {name}").output.strip()
                assert r == expected, error()

        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_Policy_PerformTTLMoveOnInsert_Default("1.0"))
def perform_ttl_move_on_insert_default(self):
    """Check that when tiered S3 storage policies are used with TTL moves,
    ClickHouse performs TTL moves upon inserts to tables created with the
    tiered storage policies by default.
    """
    name = "table_" + getuid()
    disk_name = "external"
    disks = None
    policies = None
    node = current().context.node

    def insert_data_time(number_of_mb, start=0):
        now = time.mktime(datetime.datetime.today().timetuple())
        values = ",".join(
            f"({x},{now})"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {name} VALUES {values}")

    with Given("I have a disk configuration with a S3 storage disk"):
        disks = define_s3_disk_storage_configuration(disk_name=disk_name)

    with And("I have a tiered S3 storage policy"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "tiered": {
                "volumes": {
                    "default": {"disk": "default"},
                    "external": {"disk": f"{disk_name}"},
                }
            },
        }

    with s3_storage(disks, policies, restart=True):
        try:
            with Given(f"I create table using S3 storage policy tiered"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        d UInt64,
                        d1 DateTime
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    TTL d1 + interval 0 second to volume 'external'
                    SETTINGS storage_policy='tiered'
                """
                )

            with When("I add data to the table"):
                with By("first inserting 1MB of data"):
                    insert_data_time(1, 0)

                with And("another insert of 1MB of data"):
                    insert_data_time(1, 1024 * 1024)

                with And("then doing a large insert of 10Mb of data"):
                    insert_data_time(10, 1024 * 1024 * 2)

            with Then(
                """I get the name of all partitions for all data parts
                      in this table"""
            ):
                disk_names = node.query(
                    f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                ).output.splitlines()

            with And(
                """The disk name should match the S3 disk, indicating that
                     the data parts were moved to S3 immediately as expected"""
            ):
                for _name in disk_names:
                    assert _name == f"{disk_name}", error()

        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Examples(
    "name engine",
    [
        ("altering_mt", "MergeTree()"),
    ],
)
def alter_move(self, node="clickhouse1"):
    """Check that when data is moved from one disk to another using ALTER MOVE,
    the data path changes correctly.
    """
    cluster = self.context.cluster
    prefix = "/var/lib/clickhouse/disks"
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    disks = None
    policies = None

    with Given("cluster node"):
        node = cluster.node(node)

    with And(
        """I have a disk storage configuration with 3 jbod disks and
               an external disk"""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "jbod1": {"path": "/jbod1/"},
            "jbod2": {"path": "/jbod2/", "keep_free_space_bytes": "10485760"},
            "jbod3": {"path": "/jbod3/", "keep_free_space_ratio": "0.5"},
            "external": {
                "type": "s3",
                "endpoint": f"{uri}",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

        if hasattr(self.context, "s3_options"):
            disks["external"].update(self.context.s3_options)

    with And(
        """I have storage policies configured to use the external disk in
             tiered moves."""
    ):
        policies = {
            "small_jbod_with_external": {
                "volumes": {"main": {"disk": "jbod1"}, "external": {"disk": "external"}}
            },
            "jbods_with_external": {
                "volumes": {
                    "main": [
                        {"disk": "jbod1"},
                        {"disk": "jbod2"},
                        {"max_data_part_size_bytes": "10485760"},
                    ],
                    "external": {"disk": "external"},
                }
            },
            "moving_jbod_with_external": {
                "volumes": {
                    "main": {"disk": "jbod1"},
                    "external": {"disk": "external"},
                },
                "move_factor": "0.7",
            },
        }

    with s3_storage(disks, policies, restart=True):
        for example in self.examples:
            name, engine = example
            with When(f"for example table name='{name}', engine='{engine}'"):
                with When("I create table"):
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            EventDate Date,
                            number UInt64
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        PARTITION BY toYYYYMM(EventDate)
                        SETTINGS storage_policy='jbods_with_external'
                    """
                    )
                try:
                    with And("I stop merges to avoid conflicts"):
                        node.query(f"SYSTEM STOP MERGES {name}")

                    with And("I insert 4 values"):
                        node.query(
                            f"INSERT INTO {name} VALUES(toDate('2019-03-15'), 65)"
                        )
                        node.query(
                            f"INSERT INTO {name} VALUES(toDate('2019-03-16'), 66)"
                        )
                        node.query(
                            f"INSERT INTO {name} VALUES(toDate('2019-04-10'), 42)"
                        )
                        node.query(
                            f"INSERT INTO {name} VALUES(toDate('2019-04-11'), 43)"
                        )

                    used_disks = get_used_disks_for_table(node, name)

                    with Then("all writes should go to jbods"):
                        assert all(d.startswith("jbod") for d in used_disks), error()

                    with When("I get the first part from system.parts"):
                        first_part = node.query(
                            f"SELECT name FROM system.parts WHERE table = '{name}'"
                            " AND active = 1 ORDER BY modification_time LIMIT 1"
                        ).output.strip()

                        with And("I try to move first part to 'external' volume"):
                            time.sleep(1)
                            node.query(
                                f"ALTER TABLE {name} MOVE PART '{first_part}' TO VOLUME 'external'"
                            )
                        with And(
                            "I get disk name from system.parts for the first part"
                        ):
                            disk = node.query(
                                f"SELECT disk_name FROM system.parts WHERE table = '{name}' "
                                f" AND name = '{first_part}' and active = 1"
                            ).output.strip()

                        with Then("the disk name should be 'external'"):
                            assert disk == "external", error()
                        with And(
                            "path should start with '/var/lib/clickhouse/disks/external'"
                        ):
                            expected = prefix + "/external"
                            assert get_path_for_part_from_part_log(
                                node, name, first_part
                            ).startswith(expected), error()

                    with When("I move the first part to 'jbod1' disk"):
                        time.sleep(1)
                        node.query(
                            f"ALTER TABLE {name} MOVE PART '{first_part}' TO DISK 'jbod1'"
                        )

                        with And(
                            "I get disk name from system.parts for the first part"
                        ):
                            disk = node.query(
                                f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                                f" AND name = '{first_part}' and active = 1"
                            ).output.strip()

                        with Then("the disk name shoul dbe 'jbod1'"):
                            assert disk == "jbod1", error()
                        with And("path should start with '/jbod1'"):
                            expected = "/jbod1"
                            assert get_path_for_part_from_part_log(
                                node, name, first_part
                            ).startswith(expected), error()

                    with When("I move partition 201904 to 'external' volume"):
                        time.sleep(1)
                        node.query(
                            f"ALTER TABLE {name} MOVE PARTITION 201904 TO VOLUME 'external'"
                        )

                        with And("I get disks for this partition"):
                            disks = (
                                node.query(
                                    f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                                    " AND partition = '201904' and active = 1"
                                )
                                .output.strip()
                                .split("\n")
                            )

                        with Then("number of disks should be 2"):
                            assert len(disks) == 2, error()
                        with And("all disks should be 'external'"):
                            assert all(d == "external" for d in disks), error()
                        with And(
                            "all paths should start with '/var/lib/clickhouse/disks/external'"
                        ):
                            expected = prefix + "/external"
                            assert all(
                                path.startswith(expected)
                                for path in get_paths_for_partition_from_part_log(
                                    node, name, "201904"
                                )[:2]
                            ), error()

                    with When("I move partition 201904 to disk 'jbod2'"):
                        time.sleep(1)
                        node.query(
                            f"ALTER TABLE {name} MOVE PARTITION 201904 TO DISK 'jbod2'"
                        )

                        with And("I get disks for this partition"):
                            disks = (
                                node.query(
                                    f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                                    " AND partition = '201904' and active = 1"
                                )
                                .output.strip()
                                .split("\n")
                            )

                        with Then("number of disks should be 2"):
                            assert len(disks) == 2, error()
                        with And("all disks should be 'jbod2'"):
                            assert all(d == "jbod2" for d in disks), error()
                        with And("all paths should start with '/jbod2'"):
                            expected = "/jbod2"
                            for path in get_paths_for_partition_from_part_log(
                                node, name, "201904"
                            )[:2]:
                                assert path.startswith(expected), error()

                    with When("in the end I get number of rows in the table"):
                        count = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                        with Then("the count should be 4"):
                            assert count == "4", error()

                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements()
@Examples(
    "name engine",
    [
        ("moving_default_move_factor_mt", "MergeTree()"),
        (
            "moving_default_move_factor_replicated_mt",
            "ReplicatedMergeTree('/clickhouse/moving_replicated_mt', '1')",
        ),
    ],
)
def default_move_factor(self, node="clickhouse1"):
    """Check that once the default value of **move_factor** which is 0.1
    is reached then in the background the parts are moved to the external volume.
    """
    cluster = self.context.cluster
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    disks = None
    policies = None

    with Given("cluster"):
        node = cluster.node(node)

    with And(
        """I have a disk storage configuration with 3 jbod disks and
               an external disk"""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "jbod1": {"path": "/jbod1/"},
            "jbod2": {"path": "/jbod2/", "keep_free_space_bytes": "10485760"},
            "jbod3": {"path": "/jbod3/", "keep_free_space_ratio": "0.5"},
            "external": {
                "type": "s3",
                "endpoint": f"{uri}",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

        if hasattr(self.context, "s3_options"):
            disks["external"].update(self.context.s3_options)

    with And(
        """I have storage policies configured to use the external disk in
             tiered moves."""
    ):
        policies = {
            "small_jbod_with_external": {
                "volumes": {"main": {"disk": "jbod1"}, "external": {"disk": "external"}}
            },
            "jbods_with_external": {
                "volumes": {
                    "main": [
                        {"disk": "jbod1"},
                        {"disk": "jbod2"},
                        {"max_data_part_size_bytes": "10485760"},
                    ],
                    "external": {"disk": "external"},
                }
            },
            "moving_jbod_with_external": {
                "volumes": {
                    "main": {"disk": "jbod1"},
                    "external": {"disk": "external"},
                },
                "move_factor": "0.7",
            },
        }

    with s3_storage(disks, policies, restart=True):
        for example in self.examples:
            name, engine = example
            with When(f"for example table name='{name}', engine='{engine}'"):
                with When("I create table"):
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            s1 String
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        SETTINGS storage_policy='small_jbod_with_external'
                    """
                    )
                try:
                    with And("I stop merges to avoid conflicts"):
                        node.query(f"SYSTEM STOP MERGES {name}")

                    with And(
                        "I fill up first disk above 90%%",
                        description="small jbod size is 40MB",
                    ):
                        with By("first inserting 2MB of data with 2 rows 1MB each"):
                            data = []
                            for i in range(2):
                                data.append(
                                    get_random_string(cluster, 1024 * 1024, steps=False)
                                )
                            values = ",".join(["('" + x + "')" for x in data])
                            node.query(f"INSERT INTO {name} VALUES {values}")

                        with And(
                            "then inserting 7 times 5MB of data with 5 rows 1MB each"
                        ):
                            for i in range(7):
                                data = []
                                for i in range(5):
                                    data.append(
                                        get_random_string(
                                            cluster, 1024 * 1024, steps=False
                                        )
                                    )
                                values = ",".join(["('" + x + "')" for x in data])
                                node.query(f"INSERT INTO {name} VALUES {values}")

                    with And("poll maximum 20 times to check used disks for the table"):
                        used_disks = get_used_disks_for_table(node, name)
                        retry = 20
                        i = 0
                        while (
                            not sum(1 for x in used_disks if x == "jbod1") <= 7
                            and i < retry
                        ):
                            with And("sleep 0.5 sec"):
                                time.sleep(0.5)
                            used_disks = get_used_disks_for_table(node, name)
                            i += 1

                    with Then(
                        "check that jbod1 disk is used less than or equal to 7 times"
                    ):
                        assert sum(1 for x in used_disks if x == "jbod1") <= 7, error()

                    with And(
                        "I check that at least one part has been moved to 'external' disk"
                    ):
                        assert "external" in used_disks, error()

                    for attempt in retries(count=10, delay=1):
                        with attempt:
                            with When("I check if parts were deleted from jbod1"):
                                entries = (
                                    node.command(
                                        f"find /jbod1/store/*/*/ -name 'all_*'",
                                        exitcode=0,
                                    )
                                    .output.strip()
                                    .splitlines()
                                )
                                assert len(entries) <= 7, error()

                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements()
def download_appropriate_disk(self, nodes=None):
    """Check that insert into one node of the two-node replicated cluster
    results in data storage to the correct disk once the
    other node syncs up.
    """
    cluster = self.context.cluster
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    disks = None
    policies = None

    if nodes is None:
        nodes = cluster.nodes["clickhouse"][:2]

    with Given(f"cluster nodes {nodes}"):
        nodes = [cluster.node(name) for name in nodes]

    with And(
        """I have a disk storage configuration with 3 jbod disks and
               an external disk"""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "jbod1": {"path": "/jbod1/"},
            "jbod2": {"path": "/jbod2/", "keep_free_space_bytes": "10485760"},
            "jbod3": {"path": "/jbod3/", "keep_free_space_ratio": "0.5"},
            "external": {
                "type": "s3",
                "endpoint": f"{uri}",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

        if hasattr(self.context, "s3_options"):
            disks["external"].update(self.context.s3_options)

    with And(
        """I have storage policies configured to use the external disk in
             tiered moves."""
    ):
        policies = {
            "small_jbod_with_external": {
                "volumes": {"main": {"disk": "jbod1"}, "external": {"disk": "external"}}
            },
            "jbods_with_external": {
                "volumes": {
                    "main": [
                        {"disk": "jbod1"},
                        {"disk": "jbod2"},
                        {"max_data_part_size_bytes": "10485760"},
                    ],
                    "external": {"disk": "external"},
                }
            },
            "moving_jbod_with_external": {
                "volumes": {
                    "main": {"disk": "jbod1"},
                    "external": {"disk": "external"},
                },
                "move_factor": "0.7",
            },
        }

    with s3_storage(disks, policies, restart=True):
        try:
            with When("I create replicated table on each node"):
                for i, node in enumerate(nodes):
                    node.restart()
                    node.query(
                        f"""
                        CREATE TABLE replicated_table_for_download (
                            s1 String
                        ) ENGINE = ReplicatedMergeTree('/clickhouse/replicated_table_for_download', '{i + 1}')
                        ORDER BY tuple()
                        SETTINGS storage_policy='moving_jbod_with_external', old_parts_lifetime=1, cleanup_delay_period=1, cleanup_delay_period_random_add=2
                    """
                    )

            with When("I insert 50MB of data using 50 rows 1MB each on the first node"):
                data = []
                for i in range(50):
                    data.append(get_random_string(cluster, 1024 * 1024))
                values = ",".join(["('" + x + "')" for x in data])
                nodes[0].query(
                    f"INSERT INTO replicated_table_for_download VALUES {values}"
                )

            with And("I sync the other replica"):
                for _ in range(10):
                    try:
                        nodes[-1].query(
                            "SYSTEM SYNC REPLICA replicated_table_for_download"
                        )
                        break
                    except:
                        time.sleep(0.5)

            with When("I check the used disk on other replica"):
                disks = get_used_disks_for_table(
                    nodes[-1], "replicated_table_for_download"
                )

            expected_disks = {
                "external",
            }
            with Then(
                f"the used disk should match {expected_disks}", format_name=False
            ):
                assert set(disks) == expected_disks, error()

        finally:
            with Finally("I drop the table on each node"):
                for node in nodes:
                    node.query(
                        "DROP TABLE IF EXISTS replicated_table_for_download SYNC"
                    )


@TestScenario
def alter_on_cluster_modify_ttl(self):
    """Check that ALTER TABLE ON CLUSTER MODIFY TTL works correctly with S3 storage."""
    name = "table_" + getuid()
    disks = None
    policies = None
    node = current().context.node
    cluster = self.context.cluster
    expected = "427"

    def insert_data_time(node, number_of_mb, time, start=0):
        values = ",".join(
            f"({x},{time})"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {name} VALUES {values}")

    with Given("I have a disk configuration with a S3 storage disk"):
        disks = define_s3_disk_storage_configuration()

    with And("I have a tiered S3 storage policy"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "tiered": {
                "volumes": {
                    "default": {"disk": "default"},
                    "external": {"disk": "external"},
                }
            },
        }

    with Given("I set the node names"):
        nodes = cluster.nodes["clickhouse"][:3]

    with And(f"cluster nodes {nodes}"):
        nodes = [cluster.node(name) for name in nodes]

    with s3_storage(disks, policies, restart=True):
        try:
            with Given(
                f"I create a replicated table on each node using S3 storage policy tiered"
            ):
                for i, node in enumerate(nodes):
                    node.restart()
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            d UInt64,
                            d1 DateTime
                        ) ENGINE = ReplicatedMergeTree('/clickhouse/alter_on_cluster_modify_ttl_{self.context.storage}', '{i + 1}')
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
                        (datetime.date.today() - datetime.timedelta(days=4)).timetuple()
                    )
                    insert_data_time(nodes[0], 1, tm, 1024 * 1024)

                with And("a large insert of 10Mb of data"):
                    tm = time.mktime(datetime.date.today().timetuple())
                    insert_data_time(nodes[0], 10, tm, 1024 * 1024 * 2)

            with Then("I check simple queries on the first node"):
                check_query_node(
                    node=nodes[0],
                    num=0,
                    query=f"SELECT COUNT() FROM {name}",
                    expected="1572867",
                )
                check_query_node(
                    node=nodes[0],
                    num=1,
                    query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
                    expected="10",
                )
                check_query_node(
                    node=nodes[0],
                    num=2,
                    query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
                    expected="3407872",
                )
                check_query_node(
                    node=nodes[0],
                    num=3,
                    query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
                    expected="0",
                )

            with Then("I check simple queries on the second node"):
                check_query_node(
                    node=nodes[1],
                    num=0,
                    query=f"SELECT COUNT() FROM {name}",
                    expected="1572867",
                )
                check_query_node(
                    node=nodes[1],
                    num=1,
                    query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
                    expected="10",
                )
                check_query_node(
                    node=nodes[1],
                    num=2,
                    query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
                    expected="3407872",
                )
                check_query_node(
                    node=nodes[1],
                    num=3,
                    query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
                    expected="0",
                )

            with Then("I check simple queries on the third node"):
                check_query_node(
                    node=nodes[2],
                    num=0,
                    query=f"SELECT COUNT() FROM {name}",
                    expected="1572867",
                )
                check_query_node(
                    node=nodes[2],
                    num=1,
                    query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
                    expected="10",
                )
                check_query_node(
                    node=nodes[2],
                    num=2,
                    query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
                    expected="3407872",
                )
                check_query_node(
                    node=nodes[2],
                    num=3,
                    query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
                    expected="0",
                )

            with When("I alter TTL"):
                node.query(
                    f"""ALTER TABLE {name} ON CLUSTER cluster1 MODIFY TTL d1 + interval 5 day to volume 'external'"""
                )

            with Then("I check simple queries on the first node"):
                check_query_node(
                    node=nodes[0],
                    num=0,
                    query=f"SELECT COUNT() FROM {name}",
                    expected="1572867",
                )
                check_query_node(
                    node=nodes[0],
                    num=1,
                    query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
                    expected="10",
                )
                check_query_node(
                    node=nodes[0],
                    num=2,
                    query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
                    expected="3407872",
                )
                check_query_node(
                    node=nodes[0],
                    num=3,
                    query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
                    expected="0",
                )

            with Then("I check simple queries on the second node"):
                check_query_node(
                    node=nodes[1],
                    num=0,
                    query=f"SELECT COUNT() FROM {name}",
                    expected="1572867",
                )
                check_query_node(
                    node=nodes[1],
                    num=1,
                    query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
                    expected="10",
                )
                check_query_node(
                    node=nodes[1],
                    num=2,
                    query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
                    expected="3407872",
                )
                check_query_node(
                    node=nodes[1],
                    num=3,
                    query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
                    expected="0",
                )

            with Then("I check simple queries on the third node"):
                check_query_node(
                    node=nodes[2],
                    num=0,
                    query=f"SELECT COUNT() FROM {name}",
                    expected="1572867",
                )
                check_query_node(
                    node=nodes[2],
                    num=1,
                    query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
                    expected="10",
                )
                check_query_node(
                    node=nodes[2],
                    num=2,
                    query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
                    expected="3407872",
                )
                check_query_node(
                    node=nodes[2],
                    num=3,
                    query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
                    expected="0",
                )

        finally:
            with Finally("I drop the table on each node"):
                for node in nodes:
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements()
def config_over_restart(self):
    """Check S3 configuration over server restarts."""
    name = "table_" + getuid()
    disks = None
    policies = None
    node = current().context.node

    with Given("I have a disk configuration with a S3 storage disk, access id and key"):
        default_s3_disk_and_volume(settings={"s3_max_single_part_upload_size": "0"})

    with Given(f"I create table using S3 storage policy external"):
        simple_table(name=name)

    with And(f"I stop merges on the table"):
        node.query(f"SYSTEM STOP MERGES {name}")

    with When("I add data to the table"):
        with By("first inserting 1MB of data"):
            insert_data(name=name, number_of_mb=1)

        with And("another insert of 1MB of data"):
            insert_data(name=name, number_of_mb=1, start=1024 * 1024)

        with And("then doing a large insert of 10Mb of data"):
            insert_data(name=name, number_of_mb=10, start=1024 * 1024 * 2)

    with Then("I check simple queries"):
        check_query(num=0, query=f"SELECT COUNT() FROM {name}", expected="1572867")
        check_query(
            num=1,
            query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
            expected="10",
        )
        check_query(
            num=2,
            query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
            expected="3407872",
        )
        check_query(
            num=3,
            query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
            expected="0",
        )
        check_query(
            num=4,
            query=f"SELECT * FROM {name} WHERE d == 0 OR d == 1048578 OR d == 2097154 ORDER BY d",
            expected="0\n1048578\n2097154",
        )
        check_query(
            num=5,
            query=f"SELECT * FROM (SELECT d FROM {name} WHERE d == 1)",
            expected="1",
        )

    with When("I restart clickhouse"):
        node.restart_clickhouse()

    with And("I optimize the table"):
        node.query(f"OPTIMIZE TABLE {name} FINAL")

    with Then("I check simple queries"):
        check_query(num=0, query=f"SELECT COUNT() FROM {name}", expected="1572867")
        check_query(
            num=1,
            query=f"SELECT uniqExact(d) FROM {name} WHERE d < 10",
            expected="10",
        )
        check_query(
            num=2,
            query=f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1",
            expected="3407872",
        )
        check_query(
            num=3,
            query=f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1",
            expected="0",
        )
        check_query(
            num=4,
            query=f"SELECT * FROM {name} WHERE d == 0 OR d == 1048578 OR d == 2097154 ORDER BY d",
            expected="0\n1048578\n2097154",
        )
        check_query(
            num=5,
            query=f"SELECT * FROM (SELECT d FROM {name} WHERE d == 1)",
            expected="1",
        )


@TestFeature
@Requirements(
    RQ_SRS_015_S3_AWS_SSEC("1.0"),
)
def ssec(self):
    """Check S3 SSE-C encryption option."""
    if self.context.storage not in ["aws_s3"]:
        xfail(f"not supported on {self.context.storage}")

    with Given("I add S3 SSE-C encryption option"):
        add_ssec_s3_option()
    disk_tests()


@TestOutline(Feature)
@Requirements(
    RQ_SRS_015_S3_Disk("1.0"),
    RQ_SRS_015_S3_Disk_Configuration("1.0"),
    RQ_SRS_015_S3_Policy("1.0"),
)
def disk_tests(self):
    """Test S3 and S3 compatible storage through storage disks."""
    for scenario in loads(current_module(), Scenario):
        with allow_s3_truncate(self.context.node):
            scenario()


@TestFeature
@Requirements(RQ_SRS_015_S3_AWS("1.0"), RQ_SRS_015_S3_AWS_Disk_Configuration("1.0"))
@Name("aws s3 disk")
def aws_s3(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "aws_s3"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    disk_tests()

    Feature(run=ssec)


@TestFeature
@Requirements(RQ_SRS_015_S3_GCS("1.0"), RQ_SRS_015_S3_GCS_Disk_Configuration("1.0"))
@Name("gcs disk")
def gcs(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "gcs"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    if check_clickhouse_version(">=22.6")(self):
        with Given("I disable batch delete option"):
            add_batch_delete_option()

    disk_tests()


@TestFeature
@Requirements(RQ_SRS_015_S3_MinIO("1.0"), RQ_SRS_015_S3_MinIO_Disk_Configuration("1.0"))
@Name("minio disk")
def minio(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "minio"
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    disk_tests()
