from testflows.core import *

from alter.table.attach_partition.common import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import (
    getuid,
)
from helpers.tables import *


def valid_partition_key_pair(source_partition_key, destination_partition_key):
    """Validates if pair source partition key - destination partition key is valid
    for `attach partition from` statement."""

    not_subset = {
        "tuple()": [
            "a",
            "a%2",
            "a%3",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
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
        ],
        "a": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
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
        ],
        "a%2": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
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
        ],
        "a%3": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
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
        ],
        "intDiv(a,2)": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
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
        ],
        "intDiv(a,3)": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
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
        ],
        "b": [
            "a",
            "a%2",
            "a%3",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
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
        ],
        "b%2": [
            "a",
            "a%2",
            "a%3",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
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
        ],
        "intDiv(b,2)": [
            "a",
            "a%2",
            "a%3",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
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
        ],
        "(a,b)": [
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
        ],
        "(a,b%2)": [
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
        ],
        "(intDiv(a,2),b)": [
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
        ],
        "(a%2,b%2)": [
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
        ],
        "(intDiv(a,2),intDiv(b,2))": [
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
        ],
        "(a,intDiv(b,2))": [
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
        ],
        "(b,a)": [
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
        ],
        "(b,c)": [
            "a",
            "a%2",
            "a%3",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(a,c)",
            "(a,b,c)",
            "(a%2,b%2,c%2)",
            "(intDiv(a,2),intDiv(b,2),intDiv(c,2))",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(a,c)": [
            "b",
            "b%2",
            "intDiv(b,2)",
            "(a,b)",
            "(a,b%2)",
            "(intDiv(a,2),b)",
            "(a%2,b%2)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(b,a)",
            "(b%2,a%2)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,b,c)",
            "(a%2,b%2,c%2)",
            "(intDiv(a,2),intDiv(b,2),intDiv(c,2))",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
        "(b%2,a%2)": [
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
        ],
        "(intDiv(b,2),intDiv(a,2))": [
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
        ],
    }

    not_monotonic = {
        "a": ["a%2", "a%3"],
        "a%2": ["a%3"],
        "a%3": ["a%2"],
        "intDiv(a,2)": ["a%2", "a%3"],
        "intDiv(a,3)": ["a%2", "a%3"],
        "b": ["b%2"],
        "intDiv(b,2)": ["b%2"],
        "(a,b)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(a,b%2)": [
            "a%2",
            "a%3",
            "(a%2,b%2)",
            "(b%2,a%2)",
        ],
        "(intDiv(a,2),b)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(a%2,b%2)": ["a%3", "(a,b%2)"],
        "(intDiv(a,2),intDiv(b,2))": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
        ],
        "(a,intDiv(b,2))": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(b,a)": ["a%2", "a%3", "b%2", "(a,b%2)", "(a%2,b%2)", "(b%2,a%2)"],
        "(b%2,a%2)": ["a%3", "(a,b%2)"],
        "(b,c)": ["b%2"],
        "(a,c)": ["a%2", "a%3"],
        "(intDiv(b,2),intDiv(a,2))": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
        ],
        "(a,b,c)": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
            "(a%2,b%2,c%2)",
        ],
        "(a%2,b%2,c%2)": ["a%3", "(a,b%2)"],
        "(intDiv(a,2),intDiv(b,2),intDiv(c,2))": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
            "(a%2,b%2,c%2)",
        ],
        "(a,c,b)": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
            "(a%2,b%2,c%2)",
        ],
        "(b,a,c)": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
            "(a%2,b%2,c%2)",
        ],
        "(b,c,a)": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
            "(a%2,b%2,c%2)",
        ],
        "(c,a,b)": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
            "(a%2,b%2,c%2)",
        ],
        "(c,b,a)": [
            "a%2",
            "a%3",
            "b%2",
            "(a,b%2)",
            "(a%2,b%2)",
            "(b%2,a%2)",
            "(a%2,b%2,c%2)",
        ],
    }

    partially_different = {
        "a%2": ["a", "intDiv(a,2)", "intDiv(a,3)"],
        "a%3": ["a", "intDiv(a,3)"],
        "intDiv(a,2)": ["a", "intDiv(a,3)"],
        "intDiv(a,3)": ["a", "intDiv(a,2)"],
        "b%2": ["b", "intDiv(b,2)"],
        "intDiv(b,2)": ["b"],
        "(intDiv(a,2),intDiv(b,2))": [
            "a",
            "b",
            "(a,b)",
            "(b,a)",
            "intDiv(a,3)",
            "(a,intDiv(b,2))",
            "(intDiv(a,2),b)",
        ],
        "(a%2,b%2)": [
            "a",
            "b",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "intDiv(b,2)",
            "(a,b)",
            "(b,a)",
            "(intDiv(a,2),intDiv(b,2))",
            "(intDiv(b,2),intDiv(a,2))",
            "(a,intDiv(b,2))",
            "(intDiv(a,2),b)",
        ],
        "(intDiv(b,2),intDiv(a,2))": [
            "a",
            "b",
            "(a,b)",
            "(b,a)",
            "intDiv(a,3)",
            "(a,intDiv(b,2))",
            "(intDiv(a,2),b)",
        ],
        "(b%2,a%2)": [
            "a",
            "b",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "intDiv(b,2)",
            "(a,b)",
            "(b,a)",
            "(intDiv(a,2),intDiv(b,2))",
            "(intDiv(b,2),intDiv(a,2))",
            "(a,intDiv(b,2))",
            "(intDiv(a,2),b)",
        ],
        "(a%2,b%2,c%2)": [
            "a",
            "intDiv(a,2)",
            "intDiv(a,3)",
            "b",
            "(a,b)",
            "(a,intDiv(b,2))",
            "(intDiv(a,2),b)",
            "(intDiv(a,2),intDiv(b,2))",
            "(b,a)",
            "(intDiv(b,2),intDiv(a,2))",
            "(b,c)",
            "(a,c)",
            "intDiv(b,2)",
            "(a,b,c)",
            "(a,c,b)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
            "(intDiv(a,2),intDiv(b,2),intDiv(c,2))",
        ],
        "(intDiv(a,2),intDiv(b,2),intDiv(c,2))": [
            "a",
            "intDiv(a,3)",
            "b",
            "(a,b)",
            "(a,intDiv(b,2))",
            "(intDiv(a,2),b)",
            "(b,a)",
            "(b,c)",
            "(a,c)",
            "(a,c,b)",
            "(a,b,c)",
            "(b,a,c)",
            "(b,c,a)",
            "(c,a,b)",
            "(c,b,a)",
        ],
    }

    if (
        destination_partition_key in not_monotonic.get(source_partition_key, "")
        and destination_partition_key not in not_subset.get(source_partition_key, "")
        and destination_partition_key
        not in partially_different.get(source_partition_key, "")
    ):
        return False, "not monotonic"

    if (
        destination_partition_key in not_subset.get(source_partition_key, "")
        and destination_partition_key not in not_monotonic.get(source_partition_key, "")
        and destination_partition_key
        not in partially_different.get(source_partition_key, "")
    ):
        return False, "not subset"

    if (
        destination_partition_key in partially_different.get(source_partition_key, "")
        and destination_partition_key not in not_monotonic.get(source_partition_key, "")
        and destination_partition_key not in not_subset.get(source_partition_key, "")
    ):
        return False, "partially different"

    return True, ""


def check(
    partition_ids,
    source_table_name,
    destination_table_name,
    node,
    exitcode=None,
    message=None,
    with_id=False,
):
    """Check `attach partition from` statement with or without `id`."""
    for partition_id in partition_ids:
        if with_id:
            query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition_id}' FROM {source_table_name}"
        else:
            query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"

        node.query(
            query,
            exitcode=exitcode,
            message=message,
        )


@TestScenario
@Flags(TE)
def check_attach_partition_from(
    self,
    source_table,
    destination_table,
    source_partition_key,
    destination_partition_key,
    source_table_engine="MergeTree",
    destination_table_engine="MergeTree",
    with_id=False,
):
    """Check `attach partition from` with different types of source and destination tables."""
    node = self.context.node

    source_table_name = "source_" + getuid()
    destination_table_name = "destination_" + getuid()

    with Given(
        "I create two tables with specified engines and partition keys",
        description=f"""
            partition keys:
            source table partition key: {source_partition_key}
            destination table partition key: {destination_partition_key}
            engines:
            source table engine: {destination_table_engine}
            destination table engine: {source_table_engine}
            """,
    ):
        source_table(
            table_name=source_table_name,
            engine=source_table_engine,
            partition_by=source_partition_key,
        )
        destination_table(
            table_name=destination_table_name,
            engine=destination_table_engine,
            partition_by=destination_partition_key,
        )

    with And("I attach partition from source table to the destination table"):
        if with_id:
            partition_list_query = f"SELECT partition_id FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id"
        else:
            partition_list_query = f"SELECT partition FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id"

        partition_ids = sorted(
            list(set(node.query(partition_list_query).output.split()))
        )
        valid, reason = valid_partition_key_pair(
            source_partition_key, destination_partition_key
        )

        if valid:
            for partition_id in partition_ids:
                if with_id:
                    query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition_id}' FROM {source_table_name}"
                else:
                    query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
                node.query(query)
        else:
            if reason == "not monotonic":
                exitcode, message = (
                    36,
                    "DB::Exception: Destination table partition expression is not monotonically increasing",
                )
                check(
                    partition_ids=partition_ids,
                    source_table_name=source_table_name,
                    destination_table_name=destination_table_name,
                    node=node,
                    exitcode=exitcode,
                    message=message,
                    with_id=with_id,
                )
            elif reason == "not subset":
                exitcode, message = (
                    36,
                    "DB::Exception: Destination table partition expression columns must be a subset of source table partition expression columns.",
                )
                check(
                    partition_ids=partition_ids,
                    source_table_name=source_table_name,
                    destination_table_name=destination_table_name,
                    node=node,
                    exitcode=exitcode,
                    message=message,
                    with_id=with_id,
                )
            elif reason == "partially different":
                exitcode, message = (
                    248,
                    "DB::Exception: Can not create the partition. A partition can not contain values that have different partition ids.",
                )
                for partition_id in partition_ids:
                    if with_id:
                        query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition_id}' FROM {source_table_name}"
                    else:
                        query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
                    try:
                        node.query(
                            query,
                            exitcode=exitcode,
                            message=message,
                        )
                    except:
                        try:
                            node.query(query)
                        except Exception as e:
                            fail(f"An unexpected exception occurred: {e}")

    with Then(
        f"I check that partitions were attached when source table partition_id - {source_partition_key}, destination table partition key - {destination_partition_key}, source table engine - {source_table_engine}, destination table engine - {destination_table_engine}:"
    ):
        if valid:
            source_partition_data = node.query(
                f"SELECT * FROM {source_table_name} ORDER BY a,b,c"
            ).output
            destination_partition_data = node.query(
                f"SELECT * FROM {destination_table_name} ORDER BY a,b,c"
            ).output

            assert source_partition_data == destination_partition_data

        elif reason == "partially different":
            execute_query(
                f"SELECT a,b,c,extra FROM {destination_table_name} ORDER BY a,b,c,extra",
                snapshot_name="/alter/table/attach_partition/partition_key/attach_partition_from/"
                + current().name.split("/")[-1],
            )


@TestSketch(Scenario)
@Flags(TE)
def attach_partition_from(self, with_id=False):
    """Run test check with different partition keys for both source and destination tables to see if `attach partition from` is possible."""

    partition_keys = {
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

    engines = {
        "MergeTree",
        # "ReplacingMergeTree",
        # "AggregatingMergeTree",
        # "SummingMergeTree",
        # "CollapsingMergeTree",
        # "VersionedCollapsingMergeTree",
        # "GraphiteMergeTree",
    }

    check_attach_partition_from(
        source_table=create_partitioned_table_with_data,
        destination_table=create_empty_partitioned_table,
        source_table_engine=either(*engines),
        destination_table_engine=either(*engines),
        source_partition_key=either(*partition_keys),
        destination_partition_key=either(*partition_keys),
        with_id=with_id,
    )


@TestFeature
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Key_PartitionKey(
        "1.0"
    ),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_SupportedTableEngines("1.0"),
)
@Name("partition key")
def feature(self, node="clickhouse1"):
    """Check conditions for partition key."""

    self.context.node = self.context.cluster.node(node)
    with Pool(2) as pool:
        Scenario(run=attach_partition_from, parallel=True, executor=pool)
        Scenario(test=attach_partition_from, parallel=True, executor=pool)(with_id=True)
