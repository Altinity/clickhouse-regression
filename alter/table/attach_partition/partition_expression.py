import random
import string

from testflows.core import *
from testflows.asserts import error

from alter.table.attach_partition.common import (
    create_partitioned_table_with_data,
    create_empty_partitioned_table,
)
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import getuid, check_clickhouse_version


source_table = "source_" + getuid()
destination_table = "destination_" + getuid()

ascii_letters = {i for i in string.ascii_letters}
all_ascii = {i for i in string.printable}
exclude = {"`", '"', "\\"}
not_letters = (
    all_ascii.difference(exclude).difference("1", "2", "3").difference(ascii_letters)
)


def if_valid(partition, with_id):
    if with_id:
        not_exists = {"0", "4", "5", "6", "7", "8", "9", "0", "-", "!"} | ascii_letters
        invalid_format = not_letters.difference({"-", "!"})

        if partition in not_exists:
            return None, None, False
        elif partition == "!" and check_clickhouse_version(">=25.2")(current()):
            return (
                62,
                "DB::Exception: Exclamation mark can only occur in != operator: Syntax error: failed at position",
                False,
            )
        elif partition == "'":
            if check_clickhouse_version(">=25.2")(current()):
                return (
                    62,
                    "DB::Exception: Single quoted string is not closed: Syntax error: failed at position",
                    False,
                )
            return 62, "DB::Exception: Syntax error: failed at position", False
        elif partition in invalid_format:
            return 248, "DB::Exception: Invalid partition format", False
        else:
            return None, None, True
    else:
        not_exists = {"0", "4", "5", "6", "7", "8", "9"}
        invalid = not_letters | ascii_letters
        unrecognized_token = ["~", "&"]

        if partition in not_exists:
            return None, None, False
        elif partition == "!" and check_clickhouse_version(">=25.2")(current()):
            return (
                62,
                "DB::Exception: Exclamation mark can only occur in != operator: Syntax error: failed at position",
                False,
            )
        elif partition == "'" and check_clickhouse_version(">=25.2")(current()):
            return (
                62,
                "DB::Exception: Single quoted string is not closed: Syntax error: failed at position",
                False,
            )
        elif partition in unrecognized_token and check_clickhouse_version(">=25.2")(
            current()
        ):
            return (
                62,
                "DB::Exception: Unrecognized token: Syntax error: failed at position",
                False,
            )
        elif partition in invalid:
            return 62, "DB::Exception: Syntax error: failed at position", False
        else:
            return None, None, True


@TestCheck
@Flags(TE)
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom("1.0"))
def check_partition_expression(
    self,
    partition,
    with_id,
):
    """Check if partition expression is valid."""
    node = self.context.node

    with Given("I try to attach partitions from source table to the destination table"):
        if with_id:
            query = f"ALTER TABLE {destination_table} ATTACH PARTITION ID '{partition}' FROM {source_table}"
        else:
            query = f"ALTER TABLE {destination_table} ATTACH PARTITION {partition} FROM {source_table}"

        exitcode, message, valid = if_valid(partition, with_id)
        node.query(query, exitcode=exitcode, message=message)

    with Then("I check if partition was attached to the destination table or not"):
        if valid:
            result = node.query(
                f"SELECT * FROM {destination_table} FORMAT TabSeparated"
            )
            for attempt in retries(timeout=10, delay=1):
                with attempt:
                    assert len(result.output) > 0, error()

            node.query(f"ALTER TABLE {destination_table} DETACH PARTITION {partition}")

        else:
            result = node.query(
                f"SELECT * FROM {destination_table} FORMAT TabSeparated"
            )
            for attempt in retries(timeout=10, delay=1):
                with attempt:
                    assert len(result.output) == 0, error()


@TestScenario
@Flags(TE)
def partition_expression(self, with_id=False):
    """Check if partition expression is valid."""
    partitions = ascii_letters | not_letters

    for num, partition in enumerate(partitions):
        Check(name=f"#{num}", test=check_partition_expression)(
            with_id=with_id,
            partition=partition,
        )


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_TableName("1.0"))
@Name("partition expression")
def feature(self, node="clickhouse1"):
    """Check if partition expression is valid."""

    self.context.node = self.context.cluster.node(node)

    create_partitioned_table_with_data(
        table_name=source_table,
        partition_by="a",
    )
    create_empty_partitioned_table(
        table_name=destination_table,
        partition_by="a",
    )
    Scenario("check partition expression with id", test=partition_expression)(
        with_id=True
    )
    Scenario("check partition expression without id", test=partition_expression)(
        with_id=False
    )
