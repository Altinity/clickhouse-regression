from testflows.core import *
from testflows.combinatorics import product, CoveringArray

from alter.table.attach_partition.common import *
from alter.table.attach_partition.partition_key import valid_partition_key_pair
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import (
    getuid,
)
from helpers.tables import *


def get_node(self, table):
    """Returns first node for non-replicated tables and returns random node for replicated tables."""
    
    if table == "source":
        if "Replicated" in self.context.source_engine:
            return random.choice(
                [self.context.node_1, self.context.node_2, self.context.node_3]
            )
        else:
            return self.context.node_1

    elif table == "destination":
        if "Replicated" in self.context.destination_engine:
            return random.choice(
                [self.context.node_1, self.context.node_2, self.context.node_3]
            )
        else:
            return self.context.node_1


def check(
    self,
    partition_ids,
    source_table_name,
    destination_table_name,
    exitcode=None,
    message=None,
):
    """Check `attach partition from` statement."""

    for partition_id in partition_ids:
        query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
        self.context.node_1.query(
            query,
            exitcode=exitcode,
            message=message,
        )


def get_valid_partition_key(self, source_partition_key):
    """Return valid partition key for destination table."""

    partition_keys = [
        "tuple()",
        "a",
        "a%2",
        "a%3",
        "intDiv(a,2)",
        "intDiv(a,3)",
        "b",
        "b%2",
        "intDiv(b,2)",
        "(a,b)",
        "(a%2,b%2)",
        "(a,intDiv(b,2))",
        "(a,b%2)",
        "(intDiv(a,2),b)",
        "(intDiv(a,2),intDiv(b,2))",
        "(b,a)",
        "(b%2,a%2)",
        "(intDiv(b,2),intDiv(a,2))",
        "(b,c)",
        "(a,c)",
        "(a,b,c)",
        "(a%2,b%2,c%2)",
        "(intDiv(a,2),intDiv(b,2),intDiv(c,2))",
        "(a,c,b)",
        "(b,a,c)",
        "(b,c,a)",
        "(c,a,b)",
        "(c,b,a)",
    ]
    random.shuffle(partition_keys)
    for i in partition_keys:
        if check_clickhouse_version(">=24.3")(self):
            if valid_partition_key_pair(source_partition_key, i)[0]:
                return i
        else:
            return source_partition_key
    return None


def get_partition_ids(self, table_name, node):
    """Return list of partition ids for specified table."""
    partition_list_query = f"SELECT partition FROM system.parts WHERE table='{table_name}' ORDER BY partition_id"
    return sorted(list(set(node.query(partition_list_query).output.split())))


@TestStep
def attach_all_partitions(self, source_table_name, destination_table_name, node):
    """Attach all partitions from source table to destination table."""
    partition_ids = get_partition_ids(self, source_table_name, node)
    check(
        self,
        partition_ids,
        source_table_name,
        destination_table_name,
    )


@TestStep
def move_all_partitions(self, source_table_name, destination_table_name, node):
    """Move all partitions from source table to destination table."""
    partition_ids = get_partition_ids(self, source_table_name, node)
    for partition_id in partition_ids:
        query = f"ALTER TABLE {source_table_name} MOVE PARTITION {partition_id} TO TABLE {destination_table_name}"
        node.query(query)
        node.query(
            f"SELECT * FROM {destination_table_name} format PrettyCompactMonoBlock"
        )


@TestStep
def attach_partition_from_table(
    self,
    source_partition_key,
    destination_partition_key,
    source_table,
    destination_table,
):
    """Check `attach partition from` with different types of source and destination tables
    and different partition keys. Return table name with newly attached partitions."""

    if check_clickhouse_version("<24.3")(self):
        if source_partition_key != destination_partition_key:
            return None

    self.context.source_engine = source_table.__name__.split("_")[-1]
    self.context.destination_engine = destination_table.__name__.split("_")[-1]

    source_table_name = "source_" + getuid()
    destination_table_name = "destination_" + getuid()

    with Given(
        "I create two tables with specified engines and partition keys",
        description=f"""
            partition keys:
            source table partition key: {source_partition_key}
            destination table partition key: {destination_partition_key}
            engines:
            source table engine: {self.context.source_engine}
            destination table engine: {self.context.destination_engine}
            """,
    ):
        source_table(
            table_name=source_table_name,
            partition_by=source_partition_key,
            node=self.context.node_1,
        )
        destination_table(
            table_name=destination_table_name,
            partition_by=destination_partition_key,
            node=self.context.node_1,
        )

    if check_clickhouse_version(">=24.3")(self):
        with And(
            "I add setting to allow alter partition with different partition keys"
        ):
            if "Replicated" in self.context.destination_engine:
                for node in self.context.nodes:
                    node.query(
                        f"ALTER TABLE {destination_table_name} MODIFY SETTING allow_experimental_alter_partition_with_different_key=1"
                    )
            else:
                get_node(self, "destination").query(
                    f"ALTER TABLE {destination_table_name} MODIFY SETTING allow_experimental_alter_partition_with_different_key=1"
                )

    with And("I get the list of partitions and validate partition keys pair"):
        partition_list_query = f"SELECT partition FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id"

        partition_ids = sorted(
            list(
                set(get_node(self, "source").query(partition_list_query).output.split())
            )
        )
        valid, _ = valid_partition_key_pair(
            source_partition_key, destination_partition_key
        )

    if valid:
        with And("I attach partition from source table to the destination table"):
            query = ""
            for partition_id in partition_ids:
                query += f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}; "
            self.context.node_1.query(query)
            self.context.node_1.query(
                f"SELECT * FROM {destination_table_name} format PrettyCompactMonoBlock"
            )

        with Then(
            f"I check that partitions were attached when source table partition_id - {source_partition_key}, destination table partition key - {destination_partition_key}, source table engine - {self.context.source_engine}, destination table engine - {self.context.destination_engine}:"
        ):
            source_partition_data = get_node(self, "source").query(
                f"SELECT * FROM {source_table_name} ORDER BY tuple(*)"
            )
            destination_partition_data = get_node(self, "destination").query(
                f"SELECT * FROM {destination_table_name} ORDER BY tuple(*)"
            )
            for attempt in retries(timeout=30, delay=2):
                with attempt:
                    assert (
                        destination_partition_data.output
                        == source_partition_data.output
                    ), error()
        return destination_table_name

    return None


@TestScenario
def check_detach_attach_partition(
    self,
    source_partition_key,
    destination_partition_key,
    source_table,
    destination_table,
):
    """Check that it is possible to detach and attach newly attached partition from another table."""

    with Given(
        "I get a table with newly attached partition, all partitions from source table are attached to destination table"
    ):
        table_name = attach_partition_from_table(
            source_partition_key=source_partition_key,
            destination_partition_key=destination_partition_key,
            source_table=source_table,
            destination_table=destination_table,
        )

    if table_name is None:
        skip("Table was not created")

    with And("I get the list of partitions and validate partition keys pair"):
        destination_partition_list_query = f"SELECT partition FROM system.parts WHERE table='{table_name}' ORDER BY partition_id"
        destination_partition_ids = sorted(
            list(
                set(
                    get_node(self, "destination")
                    .query(destination_partition_list_query)
                    .output.split()
                )
            )
        )

    with And("I detach partition from the table"):
        partition = random.choice(destination_partition_ids)
        data_before = self.context.node_1.query(
            f"SELECT * FROM {table_name} ORDER BY tuple(*)"
        ).output
        self.context.node_1.query(
            f"ALTER TABLE {table_name} DETACH PARTITION {partition}"
        )
        data_after = self.context.node_1.query(
            f"SELECT * FROM {table_name} ORDER BY tuple(*)"
        )
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                assert data_after.output != data_before, error()

    with And("I attach partition to the table"):
        self.context.node_1.query(
            f"ALTER TABLE {table_name} ATTACH PARTITION {partition}"
        )
        data_after = self.context.node_1.query(
            f"SELECT * FROM {table_name} ORDER BY tuple(*)"
        )

    with Then("I check that partitions were attached"):
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                assert data_after.output == data_before, error()


@TestScenario
def check_move_partition(
    self,
    source_partition_key,
    destination_partition_key,
    source_table,
    destination_table,
):
    """Check that it is possible to move partition to another table from the table with newly attached partition."""

    with Given(
        "I get a table with newly attached partition, all partitions from source table are attached to destination table"
    ):
        table_name = attach_partition_from_table(
            source_partition_key=source_partition_key,
            destination_partition_key=destination_partition_key,
            source_table=source_table,
            destination_table=destination_table,
        )

    if table_name is None:
        skip("Table was not created")

    with Then("I create table where I will move partition"):
        move_table_name = "move_" + getuid()
        move_partition_key = get_valid_partition_key(self, destination_partition_key)
        destination_table(
            table_name=move_table_name,
            partition_by=move_partition_key,
            node=self.context.node_1,
        )
        if check_clickhouse_version(">=24.3")(self):
            self.context.node_1.query(
                f"ALTER TABLE {move_table_name} MODIFY SETTING allow_experimental_alter_partition_with_different_key=1"
            )

    with And("I get the list of partitions and validate partition keys pair"):
        destination_partition_list_query = f"SELECT partition FROM system.parts WHERE table='{table_name}' ORDER BY partition_id"
        destination_partition_ids = sorted(
            list(
                set(
                    get_node(self, "destination")
                    .query(destination_partition_list_query)
                    .output.split()
                )
            )
        )

    with And("I move partition to another table"):
        data_before = self.context.node_1.query(
            f"SELECT * FROM {table_name} ORDER BY tuple(*)"
        ).output
        for partition in destination_partition_ids:
            query = f"ALTER TABLE {table_name} MOVE PARTITION {partition} TO TABLE {move_table_name}"
            self.context.node_1.query(query)
            self.context.node_1.query(
                f"SELECT * FROM {move_table_name} format PrettyCompactMonoBlock"
            )

    with Then("I check that partitions were moved"):
        data_after = self.context.node_1.query(
            f"SELECT * FROM {move_table_name} ORDER BY tuple(*)"
        )
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                assert data_after.output == data_before, error()


@TestScenario
def check_multiple_attach_move_partition(
    self,
    source_partition_key,
    destination_partition_key,
    source_table,
    destination_table,
    combination,
):
    """Check specific sequence of attach/move operations (A -> B -> C -> D) with specified partition keys."""

    with Given(
        "I get a table with newly attached partition, all partitions from source table are attached to destination table",
        description=f"Combination: {combination[0].__name__} -> {combination[1].__name__} -> {combination[2].__name__}",
    ):
        table_name = attach_partition_from_table(
            source_partition_key=source_partition_key,
            destination_partition_key=destination_partition_key,
            source_table=source_table,
            destination_table=destination_table,
        )

    if table_name is None:
        skip("Combination is not valid")

    with And("I save the data from the table to compare it later"):
        data_before = self.context.node_1.query(
            f"SELECT * FROM {table_name} ORDER BY tuple(*)"
        ).output

    with Then("I perform attach/move operations from specified sequence"):
        new_source_partition_key = destination_partition_key
        new_source_table_name = table_name
        for operation_num, operation in enumerate(combination):
            new_destination_table_name = f"destination{operation_num}_" + getuid()
            new_destination_partition_key = get_valid_partition_key(
                self, new_source_partition_key
            )

            destination_table(
                table_name=new_destination_table_name,
                partition_by=new_destination_partition_key,
                node=self.context.node_1,
            )
            if check_clickhouse_version(">=24.3")(self):
                self.context.node_1.query(
                    f"ALTER TABLE {new_destination_table_name} MODIFY SETTING allow_experimental_alter_partition_with_different_key=1"
                )

            operation(
                source_table_name=new_source_table_name,
                destination_table_name=new_destination_table_name,
                node=self.context.node_1,
            )
            new_source_table_name = new_destination_table_name
            new_source_partition_key = new_destination_partition_key

            with Then("I check that all partitions were attached or moved"):
                data_after = self.context.node_1.query(
                    f"SELECT * FROM {new_destination_table_name} ORDER BY tuple(*)"
                )
                for attempt in retries(timeout=30, delay=2):
                    with attempt:
                        assert data_after.output == data_before, error()


@TestScenario
def multiple_attach_move_partition(
    self,
    source_partition_key,
    destination_partition_key,
    source_table,
    destination_table,
):
    """Check that it is possible to do multiple attach/move operations (A -> B -> C -> D) when
    source and destination tables have different partition keys. Possible 8 combinations:
    attach -> {attach/move} -> {attach/move} -> {attach/move}.
    """
    with Given("I get all possible combinations of sequence of attach/move operations"):
        operations = [attach_all_partitions, move_all_partitions]
        combinations = product(operations, operations, operations)

    with Then("I perform all possible sequence of attach/move operations"):
        with Pool(4) as executor:
            for num, combination in enumerate(combinations):
                Scenario(
                    f"Combination {num}",
                    test=check_multiple_attach_move_partition,
                    parallel=True,
                    executor=executor,
                )(
                    source_partition_key=source_partition_key,
                    destination_partition_key=destination_partition_key,
                    source_table=source_table,
                    destination_table=destination_table,
                    combination=combination,
                )
            join()


@TestScenario
@Flags(TE)
def attach_partition_from(self):
    """Run test check with different partition keys for both source and destination tables
    to see if it is possible to use different ALTERs on newly attached partitions."""

    source_partition_keys = {
        "tuple()",
        "a",
        "a%2",
        "a%3",
        "intDiv(a,2)",
        "intDiv(a,3)",
        "b",
        "b%2",
        "intDiv(b,2)",
        "(a,b)",
        "(a%2,b%2)",
        "(a,intDiv(b,2))",
        "(a,b%2)",
        "(intDiv(a,2),b)",
        "(intDiv(a,2),intDiv(b,2))",
        "(b,a)",
        "(b%2,a%2)",
        "(intDiv(b,2),intDiv(a,2))",
        "(b,c)",
        "(a,c)",
        "(a,b,c)",
        "(a%2,b%2,c%2)",
        "(intDiv(a,2),intDiv(b,2),intDiv(c,2))",
        "(a,c,b)",
        "(b,a,c)",
        "(b,c,a)",
        "(c,a,b)",
        "(c,b,a)",
    }

    destination_partition_keys = {
        "tuple()",
        "a",
        "a%2",
        "a%3",
        "intDiv(a,2)",
        "intDiv(a,3)",
        "b",
        "b%2",
        "intDiv(b,2)",
        "(a,b)",
        "(a%2,b%2)",
        "(a,intDiv(b,2))",
        "(a,b%2)",
        "(intDiv(a,2),b)",
        "(intDiv(a,2),intDiv(b,2))",
        "(b,a)",
        "(b%2,a%2)",
        "(intDiv(b,2),intDiv(a,2))",
        "(b,c)",
        "(a,c)",
        "(a,b,c)",
        "(a%2,b%2,c%2)",
        "(intDiv(a,2),intDiv(b,2),intDiv(c,2))",
        "(a,c,b)",
        "(b,a,c)",
        "(b,c,a)",
        "(c,a,b)",
        "(c,b,a)",
    }

    source_table_types = {
        partitioned_MergeTree,
        partitioned_small_MergeTree,
        partitioned_ReplicatedMergeTree,
        partitioned_small_ReplicatedMergeTree,
    }

    destination_table_types = {
        empty_partitioned_MergeTree,
        empty_partitioned_ReplicatedMergeTree,
    }

    partition_keys_pairs = product(source_partition_keys, destination_partition_keys)
    table_pairs = product(source_table_types, destination_table_types)
    combinations = product(partition_keys_pairs, table_pairs)

    with Pool(4) as executor:
        for partition_keys, tables in combinations:
            source_partition_key, destination_partition_key = partition_keys
            source_table, destination_table = tables

            source_partition_key_str = (
                source_partition_key.replace("(", "_")
                .replace(")", "_")
                .replace(",", "_")
                .replace("%", "mod")
            )
            destination_partition_key_str = (
                destination_partition_key.replace("(", "_")
                .replace(")", "_")
                .replace(",", "_")
                .replace("%", "mod")
            )

            Scenario(
                f"move partition combination partition keys {source_partition_key_str} {destination_partition_key_str} tables {source_table.__name__} {destination_table.__name__}",
                test=check_move_partition,
                parallel=True,
                executor=executor,
            )(
                source_table=source_table,
                destination_table=destination_table,
                source_partition_key=source_partition_key,
                destination_partition_key=destination_partition_key,
            )
            Scenario(
                f"detach attach partition combination partition keys {source_partition_key_str} {destination_partition_key_str} tables {source_table.__name__} {destination_table.__name__}",
                test=check_detach_attach_partition,
                parallel=True,
                executor=executor,
            )(
                source_table=source_table,
                destination_table=destination_table,
                source_partition_key=source_partition_key,
                destination_partition_key=destination_partition_key,
            )
            Scenario(
                f"multiple operations combination partition keys {source_partition_key_str} {destination_partition_key_str} tables {source_table.__name__} {destination_table.__name__}",
                test=multiple_attach_move_partition,
                parallel=True,
                executor=executor,
            )(
                source_table=source_table,
                destination_table=destination_table,
                source_partition_key=source_partition_key,
                destination_partition_key=destination_partition_key,
            )
        join()


@TestFeature
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Key_PartitionKey(
        "1.0"
    ),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_SupportedTableEngines("1.0"),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Replicas("1.0"),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom("1.0"),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_KeepData("1.0"),
)
@Name("operations on attached partitions")
def feature(self):
    """Check that it is possible to perform different ALTERs on newly attached partitions."""

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node("clickhouse1"),
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]

    Scenario(
        "operations on attached partition",
        run=attach_partition_from,
    )
