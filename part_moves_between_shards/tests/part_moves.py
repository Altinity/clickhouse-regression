from part_moves_between_shards.requirements import *
from part_moves_between_shards.tests.steps import *


@TestOutline
def one_part_move(
    self,
    table_engine="ReplicatedSummingMergeTree",
    graphite=False,
    collapsing=False,
    vcollapsing=False,
):
    """Check that one part of data moves from one shard to another
    correct when `MOVE PART TO SHARD` query is used.
    """
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create table"):
            create_test_table(
                table_name=table_name,
                cluster_name=cluster_name,
                table_engine=table_engine,
                graphite=graphite,
                collapsing=collapsing,
                vcollapsing=vcollapsing,
            )

        with And("I stop merges"):
            for node_name in [
                "clickhouse1",
                "clickhouse2",
                "clickhouse3",
                "clickhouse4",
            ]:
                cluster.node(node_name).query(f"SYSTEM STOP MERGES {table_name}")

        with And("I make simple insert"):
            i = 0
            for name in ["clickhouse1", "clickhouse3"]:
                i = i + 1
                if graphite == True:
                    self.context.cluster.node(name).query(
                        "insert into "
                        f"{table_name} values "
                        f"(now(),'a',1,'b',{i},'c',now(),1,1,1)"
                    )
                elif collapsing == True:
                    self.context.cluster.node(name).query(
                        "insert into " f"{table_name} values " f"(1, 1)"
                    )
                elif vcollapsing == True:
                    self.context.cluster.node(name).query(
                        "insert into " f"{table_name} values " f"(1, 1, 1)"
                    )
                else:
                    simple_insert(table_name=table_name, node_name=name, value=i)

        with And("I move part from shard 1 to shard 3"):
            if graphite == True:
                node.query(
                    f"ALTER TABLE {table_name} MOVE PART '1_0_0_0' TO SHARD '/clickhouse/tables/"
                    f"replicated/03/{table_name}'"
                )
            else:
                node.query(
                    f"ALTER TABLE {table_name} MOVE PART 'all_0_0_0' TO SHARD '/clickhouse/tables/"
                    f"replicated/03/{table_name}'"
                )

        with And("I start merges and optimize table"):
            for node_name in ["clickhouse1"]:
                cluster.node(node_name).query(f"SYSTEM START MERGES {table_name}")
                cluster.node(node_name).query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check part moved and replicated"):
            retry(node.query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name}", message="0"
            )

            for name in ["clickhouse3", "clickhouse4"]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT count() FROM {table_name}", message="2"
                )
    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards_OnePartMove("1.0"))
def one_part_move_replicatedsummingmergetree(
    self, table_engine="ReplicatedSummingMergeTree"
):
    """Check that one part of data moves from one shard to another
    correct when `MOVE PART TO SHARD` query is used with ReplicatedSummingMergeTree engine.
    """
    one_part_move(table_engine=table_engine)


@TestScenario
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SupportedTableEngines("1.0"))
def one_part_move_replicatedmergetree(self, table_engine="ReplicatedMergeTree"):
    """Check that one part of data moves from one shard to another
    correct when `MOVE PART TO SHARD` query is used with ReplicatedMergeTree engine.
    """
    one_part_move(table_engine=table_engine)


@TestScenario
def one_part_move_replicatedreplacingmergetree(
    self, table_engine="ReplicatedReplacingMergeTree"
):
    """Check that one part of data moves from one shard to another
    correct when `MOVE PART TO SHARD` query is used with ReplicatedReplacingMergeTree engine.
    """
    one_part_move(table_engine=table_engine)


@TestScenario
def one_part_move_replicatedaggregatingmergetree(
    self, table_engine="ReplicatedAggregatingMergeTree"
):
    """Check that one part of data moves from one shard to another
    correct when `MOVE PART TO SHARD` query is used with ReplicatedAggregatingMergeTree engine.
    """
    one_part_move(table_engine=table_engine)


@TestScenario
def one_part_move_replicatedcollapsingmergetree(
    self, table_engine="ReplicatedCollapsingMergeTree"
):
    """Check that one part of data moves from one shard to another
    correct when `MOVE PART TO SHARD` query is used with ReplicatedCollapsingMergeTree engine.
    """
    one_part_move(table_engine=table_engine, collapsing=True)


#
#
@TestScenario
def one_part_move_replicatedversionedcollapsingmergetree(
    self, table_engine="ReplicatedVersionedCollapsingMergeTree"
):
    """Check that one part of data moves from one shard to another
    correct when `MOVE PART TO SHARD` query is used with ReplicatedVersionedCollapsingMergeTree engine.
    """
    one_part_move(table_engine=table_engine, vcollapsing=True)


#
#
@TestScenario
def one_part_move_replicatedgraphitemergetree(
    self, table_engine="ReplicatedGraphiteMergeTree"
):
    """Check that one part of data moves from one shard to another
    correct when `MOVE PART TO SHARD` query is used with ReplicatedGraphiteMergeTree engine.
    """
    one_part_move(table_engine=table_engine, graphite=True)


@TestScenario
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards_OnePartReturn("1.0"))
def ping_pong_move_part(self):
    """Check that one part of data moves from one shard to another and returns correct."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create table with simple data"):
            create_test_table_with_insert(
                table_name=table_name,
                cluster_name=cluster_name,
                table_engine=table_engine,
            )

        with And("I move part from shard 1 to shard 3"):
            node.query(
                f"ALTER TABLE {table_name} MOVE PART 'all_0_0_0' TO SHARD '/clickhouse/tables/"
                f"replicated/03/{table_name}'"
            )

        with Then("I check part moved"):
            for name in ["clickhouse1", "clickhouse3", "clickhouse4"]:
                cluster.node(name).query(
                    f"SELECT count() FROM {table_name}", message="1"
                )

        with And("I return this part back"):
            self.context.cluster.node("clickhouse3").query(
                f"ALTER TABLE {table_name} "
                f"MOVE PART 'all_0_0_0' TO SHARD '/clickhouse/tables/"
                f"replicated/01/{table_name}'"
            )

        with Then("I check part returned"):
            retry(node.query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name}", message="1"
            )

            for name in ["clickhouse3", "clickhouse4"]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT count() FROM {table_name}", message="1"
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestOutline
def move_part_command(self, part_name="''", shard_name="03", message="", exitcode=0):
    """Environment for some `MOVE PART BETWEEN SHARDS` query different inputs."""
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create table with simple data"):
            create_test_table_with_insert(
                table_name=table_name,
                cluster_name=cluster_name,
                table_engine=table_engine,
            )

        with And("I try to move part with empty name"):
            node.query(
                f"ALTER TABLE {table_name} MOVE PART {part_name} TO SHARD '/clickhouse/tables/"
                f"replicated/{shard_name}/{table_name}'",
                message=message,
                exitcode=exitcode,
            )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ZeroPart("1.0"))
def move_zero_part(self):
    """Check that move part query doesn't work with empty part name."""
    move_part_command(
        part_name="''",
        shard_name="03",
        message="DB::Exception: Received from localhost:9000. "
        "DB::Exception: Unexpected part name",
        exitcode=233,
    )


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_MovePartWithIncorrectName("1.0")
)
def move_incorrect_part(self):
    """Check that move part query doesn't work with incorrect part name."""
    move_part_command(
        part_name="'some_incorrect_name'",
        shard_name="03",
        message="DB::Exception: Received from "
        "localhost:9000. DB::Exception: "
        "Unexpected part name",
        exitcode=233,
    )


@TestScenario
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SameShard("1.0"))
def move_part_same_shard(self):
    """Check that move part query doesn't permit on the same shard."""
    move_part_command(
        part_name="'all_0_0_0'",
        shard_name="01",
        message="Exception: Source and destination are the " "same",
        exitcode=36,
    )


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DifferentLocalStructure("1.0")
)
def different_local_structure(self):
    """Check that option doesn't work when tables have different local column structures."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create replicated table with different columns structure"):
            for name in ["clickhouse1", "clickhouse2"]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"CREATE TABLE IF NOT EXISTS {table_name}"
                    f" (v_{name} UInt64) "
                    f"ENGINE =  {table_engine}('/clickhouse/tables"
                    "/replicated/{shard}"
                    f"/{table_name}'"
                    ", '{replica}') "
                    "ORDER BY tuple() "
                    "SETTINGS assign_part_uuids=1,"
                    " part_moves_between_shards_enable=1,"
                    " part_moves_between_shards_delay_seconds=1;",
                    steps=False,
                )

        with And("I make insert into table"):
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (1)"
            )

        with Then("I try to move part"):
            node.query(
                f"ALTER TABLE {table_name} MOVE PART 'all_0_0_0' TO SHARD '/clickhouse/tables/"
                f"replicated/02/{table_name}'",
                message="DB::Exception: Table columns structure in ZooKeeper"
                " is different from local table structure.",
                exitcode=122,
            )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DifferentLocalStructure("1.0")
)
def column_rename_local(self):
    """Check that option doesn't work when one tables column renamed."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create table with simple data"):
            create_test_table_with_insert(
                table_name=table_name,
                cluster_name=cluster_name,
                table_engine=table_engine,
            )

        with And("I start merges and optimize table"):
            for node_name in [
                "clickhouse1",
                "clickhouse2",
                "clickhouse3",
                "clickhouse4",
            ]:
                cluster.node(node_name).query(f"SYSTEM START MERGES {table_name}")

        with And("I locally rename column"):
            cluster.node("clickhouse3").query(
                f"ALTER TABLE {table_name} RENAME COLUMN v to v3"
            )

        with Then("I try to move part"):
            node.query(
                f"ALTER TABLE {table_name} MOVE PART 'all_0_0_0' TO SHARD '/clickhouse/tables/"
                f"replicated/03/{table_name}'",
                message="DB::Exception: Table columns structure in ZooKeeper"
                " is different from local table structure.",
                exitcode=122,
            )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DifferentPartitionKey("1.0"))
def different_partition_key(self):
    """Check that option doesn't work when tables have different local partition keys."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create table"):
            for name in ["clickhouse1", "clickhouse2"]:
                if name == "clickhouse1":
                    retry(cluster.node(name).query, timeout=100, delay=1)(
                        f"CREATE TABLE IF NOT EXISTS {table_name}"
                        f" (v UInt64, date Date) "
                        f"ENGINE = {table_engine}("
                        "'/clickhouse/tables"
                        "/replicated/{shard}"
                        f"/{table_name}'"
                        ", '{replica}') "
                        "PARTITION BY (date)"
                        "ORDER BY tuple() "
                        "SETTINGS assign_part_uuids=1,"
                        " part_moves_between_shards_enable=1,"
                        " part_moves_between_shards_delay_seconds=1;",
                        steps=False,
                    )
                else:
                    retry(cluster.node(name).query, timeout=100, delay=1)(
                        f"CREATE TABLE IF NOT EXISTS {table_name}"
                        f" (v UInt64, date Date) "
                        f"ENGINE = {table_engine}("
                        "'/clickhouse/tables"
                        "/replicated/{shard}"
                        f"/{table_name}'"
                        ", '{replica}') "
                        "PARTITION BY (v)"
                        "ORDER BY tuple() "
                        "SETTINGS assign_part_uuids=1,"
                        " part_moves_between_shards_enable=1,"
                        " part_moves_between_shards_delay_seconds=1;",
                        steps=False,
                    )

        with And("I make insert into table"):
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (1, '2022-01-03')"
            )

        with Then("I try to move part"):
            node.query(
                f"ALTER TABLE {table_name} MOVE PART '20220103_0_0_0' TO SHARD '/clickhouse/tables/"
                f"replicated/02/{table_name}'",
                message=" DB::Exception: Existing table metadata in ZooKeeper"
                " differs in partition key expression.",
                exitcode=86,
            )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards_PartNotExist("1.0"))
def move_part_not_exist(self):
    """Check error message when move part that not exist."""
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create table with simple data"):
            create_test_table_with_insert(
                table_name=table_name,
                cluster_name=cluster_name,
                table_engine=table_engine,
            )

        with And("I move part that not exist"):
            node.query(
                f"ALTER TABLE {table_name} MOVE PART 'all_0_1_0' TO SHARD '/clickhouse/tables/"
                f"replicated/03/{table_name}'",
                message="DB::Exception: Part all_0_1_0 not found locally.",
                exitcode=232,
            )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves("1.0"))
def two_parts_move_concurrent(self):
    """Check 2 different parts move from 1 shard to 2 others correct."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create table with simple data"):
            create_test_table_with_insert(
                table_name=table_name,
                cluster_name=cluster_name,
                table_engine=table_engine,
            )
            retry(cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (3)"
            )

        with And("I move 2 parts to different shard concurrent"):
            When("I move all_0_0_0 part to clickhouse2", test=move_part, parallel=True)(
                table_name=table_name, shard="02", part="all_0_0_0"
            )
            When("I move all_1_1_0 part to clickhouse3", test=move_part, parallel=True)(
                table_name=table_name, shard="03", part="all_1_1_0"
            )
            join()

        with And("I start merges and optimize table"):
            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check part moved"):
            retry(node.query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name}", message="0"
            )
            retry(cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name}", message="1"
            )

            for name in ["clickhouse3", "clickhouse4"]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT count() FROM {table_name}", message="2"
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves_SamePart("1.0")
)
def part_moves_two_times_concurrent(self):
    """Check that one part doesn't move to 2 different shards."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create table with simple data"):
            create_test_table_with_insert(
                table_name=table_name,
                cluster_name=cluster_name,
                table_engine=table_engine,
            )

        with And("I try to move one part to different shard"):
            When("I move all_0_0_0 part to clickhouse2", test=move_part, parallel=True)(
                table_name=table_name, shard="02", part="all_0_0_0"
            )
            When("I move all_0_0_0 part to clickhouse3", test=move_part, parallel=True)(
                table_name=table_name,
                shard="03",
                part="all_0_0_0",
                message="DB::Exception: "
                "Received from localhost:9000."
                " DB::Exception: Part is busy, reason:"
                " Part all_0_0_0 has ",
                exitcode=128,
            )
            join()

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestOutline
def part_move_parallel_with_insert(
    self, table_name, node_name="clickhouse1", iterations=2
):
    """Check that part move work correct with insert in parallel."""
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    with Given("I create table with simple data"):
        create_test_table_with_insert(
            table_name=table_name, cluster_name=cluster_name, table_engine=table_engine
        )

    with When("I move parts and parallel make insert"):
        part_uuid = (
            self.context.cluster.node("clickhouse1")
            .query(f"SELECT uuid FROM system.parts where name = 'all_0_0_0'")
            .output.strip()
        )
        for i in range(iterations):
            with When(f"move number {i}"):
                with By("waiting for new part in system.parts table"):
                    part = ""
                    while part == "":
                        part = (
                            self.context.cluster.node("clickhouse1")
                            .query(
                                f"SELECT name FROM system.parts where uuid = '{part_uuid}'"
                            )
                            .output.strip()
                        )

                By(
                    "I move part from shard 1 to shard 3 and return it",
                    test=move_part_and_return,
                    parallel=True,
                )(
                    table_name=table_name,
                    part=part,
                    part_uuid=part_uuid,
                    shard1="01",
                    shard2="03",
                    node_name1="clickhouse1",
                    node_name2="clickhouse3",
                )

                And("I make concurrent insert", test=simple_insert, parallel=True)(
                    table_name=table_name, node_name=node_name, value=i + 7
                )

                join()

    with And("I start merges and optimize table"):
        node.query(f"SYSTEM START MERGES {table_name}")
        node.query(f"OPTIMIZE TABLE {table_name} FINAL")


@TestScenario
@Retry(5)
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves_InsertDataOnSourceNodeSamePartition(
        "1.0"
    )
)
def part_move_parallel_with_insert_to_source(self):
    """Check that `PART MOVE` work correct with insert on source node in parallel."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I make move from and insert to clickhouse1 concurrent"):
            part_move_parallel_with_insert(
                table_name=table_name, node_name="clickhouse1"
            )

        with Then("I check part moved correct"):
            retry(cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name}", message="3"
            )
            retry(cluster.node("clickhouse3").query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name}", message="1"
            )
    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Retry(5)
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves_InsertDataOnDestinationNodeSamePartition(
        "1.0"
    )
)
def part_move_parallel_with_insert_to_destination(self):
    """Check that `PART MOVE` work correct with insert on destination node in parallel."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I make move from and insert to clickhouse1 concurrent"):
            part_move_parallel_with_insert(
                table_name=table_name, node_name="clickhouse3"
            )

        with Then("I check part moved correct"):
            retry(cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name}", message="1"
            )
            retry(cluster.node("clickhouse3").query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name}", message="3"
            )
    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements()
def part_move_parallel_with_big_insert(self, iterations=1, number=100):
    """Check that `PART MOVE` work correct with insert on destination node in parallel."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        node = self.context.cluster.node("clickhouse1")
        with Given("I drop table if exists"):
            cluster_name = cluster_name
            node.query(
                f"DROP TABLE IF EXISTS zookeeper_bench ON CLUSTER {cluster_name} SYNC"
            )

        with And("I create table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
                f" (p UInt64, x UInt64) "
                f"ENGINE = {table_engine}('/clickhouse/tables/"
                "replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}') "
                "ORDER BY tuple() "
                "SETTINGS  in_memory_parts_enable_wal=0, "
                "assign_part_uuids=1,"
                " part_moves_between_shards_enable=1,"
                " part_moves_between_shards_delay_seconds=0,"
                "min_bytes_for_wide_part=104857600, "
                "min_bytes_for_wide_part=104857600, "
                "parts_to_delay_insert=1000000, "
                "parts_to_throw_insert=1000000, "
                "max_parts_in_total=1000000;",
                steps=False,
            )

            for node_name in [
                "clickhouse1",
                "clickhouse2",
                "clickhouse3",
                "clickhouse4",
            ]:
                retry(cluster.node(node_name).query, timeout=100, delay=1)(
                    f"SYSTEM STOP MERGES {table_name}"
                )

            node.query(f"insert into {table_name} values(1233445414114, 1233445414114)")

        with And("I move parts and parallel make insert"):
            for i in range(iterations):
                part_uuid = (
                    self.context.cluster.node("clickhouse1")
                    .query(f"SELECT uuid FROM system.parts where name = 'all_0_0_0'")
                    .output.strip()
                )
                part = ""
                while part == "":
                    part = (
                        self.context.cluster.node("clickhouse1")
                        .query(
                            f"SELECT name FROM system.parts where uuid = '{part_uuid}'"
                        )
                        .output.strip()
                    )
                with Given(f"LOOP STEP {i}"):
                    When(
                        "I move part from shard 1 to shard 3 and return it",
                        test=move_part_and_return,
                        parallel=True,
                    )(
                        table_name=table_name,
                        part=part,
                        part_uuid=part_uuid,
                        shard1="01",
                        shard2="03",
                        node_name1="clickhouse1",
                        node_name2="clickhouse3",
                    )
                    with Step("I make big insert into table"):
                        node.query(
                            f"insert into {table_name} select rand(1)%100,"
                            f" rand(2) from numbers({number}) "
                            f"settings max_block_size=100, "
                            f"min_insert_block_size_bytes=1, "
                            f"min_insert_block_size_rows=1, "
                            f"insert_deduplicate=0, "
                            f"max_threads=128, "
                            f"max_insert_threads=128;"
                        )
                    join()

        with Then("I check part moved correct"):
            retry(cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name}", message="101"
            )
            retry(cluster.node("clickhouse3").query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name}", message="0"
            )
    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_NotSupportedTableEngines("1.0")
)
def mergetree(self):
    """Try part moves with non replicated MergeTree engine and expected to fail."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"
            table_name_d = f"test_table_d{uid}"

        with And("I create table"):
            for name in ["clickhouse1", "clickhouse2"]:
                if name == "clickhouse1":
                    retry(cluster.node(name).query, timeout=100, delay=1)(
                        f"CREATE TABLE IF NOT EXISTS {table_name}"
                        f" (v UInt64, date Date) "
                        f"ENGINE = MergeTree() "
                        "PARTITION BY (date)"
                        "ORDER BY tuple() "
                        "SETTINGS assign_part_uuids=1,"
                        " part_moves_between_shards_enable=1,"
                        " part_moves_between_shards_delay_seconds=1;",
                        steps=False,
                    )
                else:
                    retry(cluster.node(name).query, timeout=100, delay=1)(
                        f"CREATE TABLE IF NOT EXISTS {table_name}"
                        f" (v UInt64, date Date) "
                        f"ENGINE = MergeTree() "
                        "PARTITION BY (date)"
                        "ORDER BY tuple() "
                        "SETTINGS assign_part_uuids=1,"
                        " part_moves_between_shards_enable=1,"
                        " part_moves_between_shards_delay_seconds=1;",
                        steps=False,
                    )

        with And("I create distributed table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name_d} as {table_name} "
                f"ENGINE = Distributed"
                f"({cluster_name}, currentDatabase(), {table_name})",
                steps=False,
            )

        with And("I make insert into table"):
            retry(node.query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (1, '2022-01-03')"
            )

        with Then("I try to move part"):
            node.query(
                f"ALTER TABLE {table_name} MOVE PART '20220103_0_0_0' TO SHARD '02'",
                message="DB::Exception: MOVE "
                "PARTITION TO SHARD is "
                "not supported by storage "
                "MergeTree.",
                exitcode=48,
            )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestFeature
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards("1.0"))
@Name("part_moves")
def feature(self):
    """Check part moves between shards."""
    global table_engine
    table_engine = "ReplicatedSummingMergeTree"
    cluster = self.context.cluster
    keeper_cluster_nodes = cluster.nodes["zookeeper"][0:1]
    clickhouse_cluster_nodes = cluster.nodes["clickhouse"][:4]

    with Given("I create remote config"):
        entries = {
            "cluster_1replica_3shard": [
                {"shard": [{"replica": {"host": "clickhouse1", "port": "9000"}}]},
                {"shard": [{"replica": {"host": "clickhouse2", "port": "9000"}}]},
                {
                    "shard": [
                        {"replica": {"host": "clickhouse3", "port": "9000"}},
                        {"replica": {"host": "clickhouse4", "port": "9000"}},
                    ]
                },
            ]
        }
        create_remote_configuration(entries=entries)

    with And("I create 1 zookeeper cluster configuration"):
        create_config_section(
            control_nodes=keeper_cluster_nodes, cluster_nodes=clickhouse_cluster_nodes
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
