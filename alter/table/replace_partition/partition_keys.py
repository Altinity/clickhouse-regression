import random

from testflows.core import *
from testflows.combinatorics import product

from alter.table.attach_partition.common import (
    partitioned_MergeTree,
    version_when_attach_partition_with_different_keys_merged,
    clean_name,
)
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, check_clickhouse_version


def get_exitcode_and_message(self, source_partition_key, destination_partition_key):
    """Get exitcode and message for different partition keys."""
    one_column_keys = [
        "a",
        "a%2",
        "a%3",
        "intDiv(a,2)",
        "intDiv(a,3)",
        "b",
        "b%2",
        "intDiv(b,2)",
    ]
    two_column_keys = [
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
    ]
    three_column_keys = [
        "(a,b,c)",
        "(a%2,b%2,c%2)",
        "(intDiv(a,2),intDiv(b,2),intDiv(c,2))",
        "(a,c,b)",
        "(b,a,c)",
        "(b,c,a)",
        "(c,a,b)",
        "(c,b,a)",
    ]

    wrong_number_of_fields = {
        "tuple()": one_column_keys + two_column_keys + three_column_keys,
        "a": two_column_keys + three_column_keys + ["tuple()"],
        "a%2": two_column_keys + three_column_keys + ["tuple()"],
        "a%3": two_column_keys + three_column_keys + ["tuple()"],
        "intDiv(a,2)": two_column_keys + three_column_keys + ["tuple()"],
        "intDiv(a,3)": two_column_keys + three_column_keys + ["tuple()"],
        "b": two_column_keys + three_column_keys + ["tuple()"],
        "b%2": two_column_keys + three_column_keys + ["tuple()"],
        "intDiv(b,2)": two_column_keys + three_column_keys + ["tuple()"],
        "(a,b)": one_column_keys + three_column_keys + ["tuple()"],
        "(a%2,b%2)": one_column_keys + three_column_keys + ["tuple()"],
        "(a,intDiv(b,2))": one_column_keys + three_column_keys + ["tuple()"],
        "(a,b%2)": one_column_keys + three_column_keys + ["tuple()"],
        "(intDiv(a,2),b)": one_column_keys + three_column_keys + ["tuple()"],
        "(intDiv(a,2),intDiv(b,2))": one_column_keys + three_column_keys + ["tuple()"],
        "(b,a)": one_column_keys + three_column_keys + ["tuple()"],
        "(b%2,a%2)": one_column_keys + three_column_keys + ["tuple()"],
        "(intDiv(b,2),intDiv(a,2))": one_column_keys + three_column_keys + ["tuple()"],
        "(b,c)": one_column_keys + three_column_keys + ["tuple()"],
        "(a,c)": one_column_keys + three_column_keys + ["tuple()"],
        "(a,b,c)": one_column_keys + two_column_keys + ["tuple()"],
        "(a%2,b%2,c%2)": one_column_keys + two_column_keys + ["tuple()"],
        "(intDiv(a,2),intDiv(b,2),intDiv(c,2))": one_column_keys
        + two_column_keys
        + ["tuple()"],
        "(a,c,b)": one_column_keys + two_column_keys + ["tuple()"],
        "(b,a,c)": one_column_keys + two_column_keys + ["tuple()"],
        "(b,c,a)": one_column_keys + two_column_keys + ["tuple()"],
        "(c,a,b)": one_column_keys + two_column_keys + ["tuple()"],
        "(c,b,a)": one_column_keys + two_column_keys + ["tuple()"],
    }

    if destination_partition_key in wrong_number_of_fields.get(
        source_partition_key, ""
    ):
        exitcode = 248
        message = "DB::Exception: Wrong number of fields"
    else:
        if check_clickhouse_version(
            f">={version_when_attach_partition_with_different_keys_merged}"
        )(self):
            exitcode = 36
            message = "DB::Exception: Cannot replace partition"
        else:
            exitcode = 36
            message = "DB::Exception: Tables have different partition key"

    return exitcode, message


@TestStep
@Flags(TE)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_Key("1.0")
)
def check_replace_partition(self, source_partition_key, destination_partition_key):
    """Check that it is not possible to replace partition on the destination table when destination table and source
    table have different partition by key."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    node = self.context.node

    with Given("I create a partitioned destination table"):
        partitioned_MergeTree(
            table_name=destination_table,
            partition_by=destination_partition_key,
            node=node,
        )
        if check_clickhouse_version(
            f">={version_when_attach_partition_with_different_keys_merged}"
        )(self):
            node.query(
                f"ALTER TABLE {destination_table} MODIFY SETTING allow_experimental_alter_partition_with_different_key=1"
            )

    with And("I have a partitioned source table with a different partition key"):
        partitioned_MergeTree(
            table_name=source_table, partition_by=source_partition_key, node=node
        )

    with And("I get the list of partitions"):
        partition_list_query = f"SELECT partition FROM system.parts WHERE table='{source_table}' ORDER BY partition_id FORMAT TabSeparated"
        partition_ids = sorted(list(node.query(partition_list_query).output.split()))

    with Then("I try to replace partition on the destination"):
        if source_partition_key == destination_partition_key:
            exitcode, message = None, None
        else:
            exitcode, message = get_exitcode_and_message(
                self, source_partition_key, destination_partition_key
            )
        partition = random.choice(partition_ids)
        node.query(
            f"ALTER TABLE {destination_table} REPLACE PARTITION {partition} FROM {source_table}",
            exitcode=exitcode,
            message=message,
        )


@TestScenario
@Flags(TE)
def replace_partition_partition_key(self):
    """Run test check with different partition keys for both source and destination tables
    to see if `replace partition` is possible."""
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

    partition_keys_pairs = product(source_partition_keys, destination_partition_keys)
    with Pool(10) as executor:
        for source_partition_key, destination_partition_key in partition_keys_pairs:
            source_partition_key_str = clean_name(source_partition_key)
            destination_partition_key_str = clean_name(destination_partition_key)

            Scenario(
                f"combination partition keys {source_partition_key_str} {destination_partition_key_str}",
                test=check_replace_partition,
                parallel=True,
                executor=executor,
            )(
                source_partition_key=source_partition_key,
                destination_partition_key=destination_partition_key,
            )
        join()


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited("1.0"))
@Name("partition keys")
def feature(self, node="clickhouse1"):
    """Check that the ClickHouse doesn't crash and outputs an error when doing replace partition with different partition keys."""
    self.context.node = self.context.cluster.node(node)
    Scenario(run=replace_partition_partition_key)
