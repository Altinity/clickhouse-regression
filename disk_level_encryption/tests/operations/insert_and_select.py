from testflows.asserts import snapshot, error
from testflows.stash import stashed
from testflows.asserts import values as That
from testflows.core.name import basename
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *


@TestOutline
def check_insert_and_select(
    self,
    partitions_num,
    inserts_num_1,
    inserts_num_2,
    restart_before_second_insert,
    restart_after_second_insert,
    check_encryption,
    policy=None,
    node=None,
    disk_path=None,
):
    """Check insert and select based on the specified parameters
    with optional restarts and encryption check at the end.
    """
    node = self.context.node if node is None else node
    policy = self.context.policy if policy is None else policy
    disk_path = self.context.disk_path if disk_path is None else disk_path

    with Given("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy, partition_by_id=True)

    with When("I insert data into the table first time"):
        multiple_values = []
        for j in range(1, inserts_num_1 + 1):
            values = (
                "("
                + "), (".join(
                    [
                        str(i) + f",'insert_number {j}'"
                        for i in range(1, partitions_num + 1)
                    ]
                )
                + ")"
            )
            multiple_values.append(values)
        multiple_insert_into_table(name=table_name, values=multiple_values)

    with Then("I restart and check first output"):
        if restart_before_second_insert:
            with When("I restart server"):
                node.restart()

        with Then("I expect data is successfully inserted"):
            r = node.query(
                f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
            )
            with That() as that:
                assert that(
                    snapshot(r.output, name=basename(self.name) + "first")
                ), error()

        if check_encryption:
            with Then("I expect all files has ENC header"):
                check_if_all_files_are_encrypted(disk_path=disk_path)

    with When("I insert data into the table second time"):
        multiple_values = []
        for j in range(1, inserts_num_2 + 1):
            values = (
                "("
                + "), (".join(
                    [
                        str(i) + f",'insert_number {j}'"
                        for i in range(1, partitions_num + 1)
                    ]
                )
                + ")"
            )
            multiple_values.append(values)
        multiple_insert_into_table(name=table_name, values=multiple_values)

    with Then("I restart, check encryption and second output"):
        if restart_after_second_insert:
            with When("I restart server"):
                node.restart()

        with Then("I expect data is successfully inserted"):
            r = node.query(
                f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
            )
            with That() as that:
                assert that(snapshot(r.output, name=basename(self.name))), error()

        if check_encryption:
            with Then("I expect all files has ENC header"):
                check_if_all_files_are_encrypted(disk_path=disk_path)


@TestOutline
def check_insert_with_large_parts(
    self,
    partitions_num,
    inserts_num,
    restart,
    check_encryption,
    random_string_length,
    disk_path=None,
    policy=None,
    node=None,
):
    """Check we can INSERT large part of data."""
    node = self.context.node if node is None else node
    policy = self.context.policy if policy is None else policy
    disk_path = self.context.disk_path if disk_path is None else disk_path

    with Given("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy, partition_by_id=True)

    with When("I create random string data"):
        with stashed(basename(self.name) + "random_string_of_data") as stash:
            with By("creating random string data"):
                random_data = get_random_string(
                    length=partitions_num * inserts_num * random_string_length
                )
            stash(random_data)
        random_data = stash.value

    with And("I insert data into the table"):
        multiple_values = []
        for j in range(1, inserts_num + 1):
            values = (
                "("
                + "), (".join(
                    [
                        str(i)
                        + f",'{random_data[((i - 1) * (j - 1) + (j - 1)) * random_string_length: ((i - 1) * (j - 1) + (j - 1)) * random_string_length + random_string_length]}'"
                        for i in range(1, partitions_num + 1)
                    ]
                )
                + ") "
            )
            multiple_values.append(values)
        multiple_insert_into_table(name=table_name, values=multiple_values)

    with Then("checks restart encryption and output"):
        if restart:
            with When("I restart server if it is needed"):
                node.restart()

        with Then("I expect data is successfully inserted"):
            r = node.query(
                f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
            )
            with That() as that:
                assert that(snapshot(r.output, name=basename(self.name))), error()

        if check_encryption:
            with Then("I expect all files has ENC header"):
                check_if_all_files_are_encrypted(disk_path=disk_path)


@TestScenario
def check_insert_incremental_block_size(self, policy=None, node=None, check_range=512):
    """Check encryption works with different block sizes that cross
    different AES cipher block boundaries.
    """
    node = self.context.node if node is None else node
    policy = self.context.policy if policy is None else policy

    with Given("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy, partition_by_id=True)

    with When("I insert data into the table"):
        string_data = "1" * check_range
        all_values = []
        for size in range(1, check_range + 1):
            with By(f"creating insert value with string of {size} bytes"):
                values = []
                for i in range(2):
                    values.append(f"({i},'{string_data[0:size]}')")
                values = ",".join(values)
                all_values.append(values)

        multiple_insert_into_table(name=table_name, values=all_values)

        with Then("I expect data is successfully inserted"):
            r = node.query(
                f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
            )
            expected_output = (
                "".join(
                    [
                        '{"Id":0,"Value":"' + "1" * i + '"}\n'
                        for i in range(1, check_range + 1)
                    ]
                )
                + "".join(
                    [
                        '{"Id":1,"Value":"' + "1" * i + '"}\n'
                        for i in range(1, check_range)
                    ]
                )
                + '{"Id":1,"Value":"'
                + "1" * check_range
                + '"}'
            )
            assert expected_output == r.output


@TestScenario
def check_insert_back_to_back(self, policy=None, node=None):
    """Check encryption works with back to back inserts."""
    node = self.context.node if node is None else node
    policy = self.context.policy if policy is None else policy

    with Given("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy, partition_by_id=True)

    with When("I insert data into the table back to back"):
        for i in range(10):
            values = f"({i}, " + "'" + str(i) + "')"
            insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(
            f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
        )
        with That() as that:
            assert that(snapshot(r.output, name=basename(self.name))), error()


@TestOutline
def check_insert_parallel(
    self,
    concurrent_inserts,
    number_of_inserts,
    partition_by_id,
    number_of_ids,
    number_of_values,
    policy=None,
    node=None,
):
    """Check encryption works with parallel inserts."""
    node = self.context.node if node is None else node
    policy = self.context.policy if policy is None else policy

    with Given("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy, partition_by_id=partition_by_id)

    with When("I insert data into the table in parallel mode"):
        with Pool(concurrent_inserts) as pool:
            try:
                for i in range(number_of_inserts):
                    values = ",".join(
                        [
                            f"({n % number_of_ids}, 'hello_{n}')"
                            for n in range(number_of_values)
                        ]
                    )
                    When(
                        name=f"parallel insert {i}",
                        test=insert_into_table,
                        parallel=True,
                        executor=pool,
                    )(name=table_name, values=values)
            finally:
                join()

    with Then("I expect data is successfully inserted"):
        r = node.query(
            f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
        )
        with That() as that:
            assert that(snapshot(r.output, name=basename(self.name))), error()


@TestScenario
def check_insert_and_select_ten_millions_rows(
    self, rows=10000000, policy=None, node=None, disk_path=None
):
    """Check insert and select ten millions rows with fast output comparison"""
    node = self.context.node if node is None else node
    policy = self.context.policy if policy is None else policy
    disk_path = self.context.disk_path if disk_path is None else disk_path

    with Given("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy, partition_by_id=True)

    with And("I insert data into table"):
        query = f"insert into {table_name} select number % 100  as Id, concat('hello', leftPad(toString(number), 8, '0')) as Value from numbers(1,{rows})"
        node.query(query)

    with Then("I expect data is successfully inserted"):
        expected_query = f"select number % 100  as Id, concat('hello', leftPad(toString(number), 8, '0')) as Value from numbers(1,{rows}) order by Id, Value"
        with stashed(name=stashed.hash(expected_query)) as stash:
            r = node.hash_query(expected_query)
            stash(r)

        expected_hash = stash.value
        with When("I read back all data that is in the table"):
            r = node.hash_query(f"select * from {table_name} order by Id, Value")
        with Then("I expected hash of the read data to match expected"):
            assert r == expected_hash


@TestScenario
def check_insert_and_select_one_partition_one_block(self):
    """Check insert and select when all data stored in one part
    with server restart and encryption key header check.
    """
    check_insert_and_select(
        partitions_num=1,
        inserts_num_1=1,
        inserts_num_2=1,
        restart_before_second_insert=True,
        restart_after_second_insert=True,
        check_encryption=True,
    )


@TestScenario
def check_insert_and_select_ten_partitions_one_block(self):
    """Check insert and select when data stored in ten partitions with one insert
    with server restart and encryption key header check.
    """
    check_insert_and_select(
        partitions_num=10,
        inserts_num_1=1,
        inserts_num_2=1,
        restart_before_second_insert=True,
        restart_after_second_insert=True,
        check_encryption=True,
    )


@TestScenario
def check_insert_and_select_one_partition_ten_blocks(self):
    """Check insert and select when all data stored in one partition with ten inserts
    with server restart and encryption key header check.
    """
    check_insert_and_select(
        partitions_num=1,
        inserts_num_1=10,
        inserts_num_2=10,
        restart_before_second_insert=True,
        restart_after_second_insert=True,
        check_encryption=True,
    )


@TestScenario
def check_insert_and_select_three_partitions_three_blocks(self):
    """Check insert and select when data stored in three partition with three inserts
    with server restart and encryption key header check.
    """
    check_insert_and_select(
        partitions_num=3,
        inserts_num_1=3,
        inserts_num_2=3,
        restart_before_second_insert=True,
        restart_after_second_insert=True,
        check_encryption=True,
    )


@TestScenario
def check_insert_parallel_five_inserts_one_id_two_values(self):
    """Check insert and select when all data stored in one partition with five concurrent inserts
    with server restart and encryption key header check.
    """
    check_insert_parallel(
        concurrent_inserts=5,
        number_of_inserts=100,
        partition_by_id=False,
        number_of_ids=1,
        number_of_values=2,
    )


@TestScenario
def check_insert_parallel_five_inserts_hundred_ids_hundred_values(self):
    """Check insert and select when all data stored in one partition
    five concurrent inserts with server restart and encryption key header check.
    """
    check_insert_parallel(
        concurrent_inserts=5,
        number_of_inserts=100,
        partition_by_id=False,
        number_of_ids=100,
        number_of_values=100,
    )


@TestScenario
def check_insert_parallel_five_inserts_one_id_two_values_partition_by_id(self):
    """Check insert and select when all data stored in one partition with partitioning
    five concurrent inserts with server restart and encryption key header check.
    """
    check_insert_parallel(
        concurrent_inserts=5,
        number_of_inserts=100,
        partition_by_id=True,
        number_of_ids=1,
        number_of_values=2,
    )


@TestScenario
def check_insert_parallel_five_concurrent_hundred_ids_hundred_values_partition_by_id(
    self,
):
    """Check insert and select when all data stored in hundred partitions
    five concurrent inserts with server restart and encryption key header check.
    """
    check_insert_parallel(
        concurrent_inserts=5,
        number_of_inserts=100,
        partition_by_id=True,
        number_of_ids=100,
        number_of_values=100,
    )


@TestScenario
def check_insert_with_large_parts_one_partition_one_block(self):
    """Check insert and select large block of data when all data stored in one part
    with server restart and encryption key header check.
    """
    check_insert_with_large_parts(
        partitions_num=1,
        inserts_num=1,
        restart=True,
        check_encryption=True,
        random_string_length=1024 * 1024,
    )


@TestScenario
def check_insert_with_large_parts_ten_partitions_one_block(self):
    """Check insert and select large block of data when data stored in ten parts
    with server restart and encryption key header check.
    """
    check_insert_with_large_parts(
        partitions_num=10,
        inserts_num=1,
        restart=True,
        check_encryption=True,
        random_string_length=1024 * 1024,
    )


@TestScenario
def check_insert_with_large_parts_one_partition_ten_blocks(self):
    """Check insert and select ten large blocks of data when data stored in one part
    with server restart and encryption key header check.
    """
    check_insert_with_large_parts(
        partitions_num=1,
        inserts_num=10,
        restart=True,
        check_encryption=True,
        random_string_length=1024 * 1024,
    )


@TestScenario
def check_insert_with_large_parts_three_partitions_three_blocks(self):
    """Check insert and select three large blocks of data when data stored in three parts
    with server restart and encryption key header check.
    """
    check_insert_with_large_parts(
        partitions_num=3,
        inserts_num=3,
        restart=True,
        check_encryption=True,
        random_string_length=1024 * 1024,
    )


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Restart("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_InsertAndSelect("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_FileEncryption("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_EncryptedType("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_OnTheFlyEncryption("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_OnTheFlyDecryption("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_FileEncryption_FileHeader("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_FileEncryption_Metadata("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Disk_Local("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Disk("1.0"),
)
@Name("insert and select")
def feature(self, node="clickhouse1"):
    """Check INSERT and SELECT operations on a table that uses encrypted disk."""
    self.context.node = self.context.cluster.node(node)

    with Given("I have policy that uses local encrypted disk"):
        create_policy_with_local_encrypted_disk()

    for scenario in loads(current_module(), Scenario):
        scenario()
