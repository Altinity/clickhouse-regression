from testflows.core import *
from testflows.combinatorics import product, CoveringArray

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

    monotonicity_not_implemented = {
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
        "a%3": ["a", "intDiv(a,2)", "intDiv(a,3)"],
        "intDiv(a,2)": ["a", "intDiv(a,3)"],
        "intDiv(a,3)": ["a", "intDiv(a,2)"],
        "b%2": ["b", "intDiv(b,2)"],
        "intDiv(b,2)": ["b"],
        "(a,intDiv(b,2))": ["b", "(intDiv(a,2),b)", "(a,b)", "(b,a)"],
        "(intDiv(a,2),b)": ["a", "intDiv(a,3)", "(a,b)", "(b,a)", "(a,intDiv(b,2))"],
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
        "(a,b%2)": [
            "b",
            "intDiv(b,2)",
            "(a,b)",
            "(b,a)",
            "(intDiv(a,2),b)",
            "(intDiv(a,2),intDiv(b,2))",
            "(a,intDiv(b,2))",
            "(intDiv(b,2),intDiv(a,2))",
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
        destination_partition_key
        in monotonicity_not_implemented.get(source_partition_key, "")
        and destination_partition_key not in not_subset.get(source_partition_key, "")
        and destination_partition_key
        not in partially_different.get(source_partition_key, "")
    ):
        return False, "monotonicity not implemented"

    if (
        destination_partition_key in not_subset.get(source_partition_key, "")
        and destination_partition_key
        not in monotonicity_not_implemented.get(source_partition_key, "")
        and destination_partition_key
        not in partially_different.get(source_partition_key, "")
    ):
        return False, "not subset"

    if (
        destination_partition_key in partially_different.get(source_partition_key, "")
        and destination_partition_key
        not in monotonicity_not_implemented.get(source_partition_key, "")
        and destination_partition_key not in not_subset.get(source_partition_key, "")
    ):
        return False, "partially different"

    return True, ""


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
    with_id=False,
):
    """Check `attach partition from` statement with or without `id`."""
    for partition_id in partition_ids:
        if with_id:
            query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition_id}' FROM {source_table_name}"
        else:
            query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"

        self.context.node_1.query(
            query,
            exitcode=exitcode,
            message=message,
        )


@TestScenario
@Flags(TE)
def check_attach_partition_from(
    self,
    source_partition_key,
    destination_partition_key,
    source_table,
    destination_table,
    with_id=False,
):
    """Check `attach partition from` with different types of source and destination tables."""

    if check_clickhouse_version(
        f"<{version_when_attach_partition_with_different_keys_merged}"
    )(self):
        if source_partition_key != destination_partition_key:
            skip(
                f"`attach partition from` with tables that have different partition keys are not supported before {version_when_attach_partition_with_different_keys_merged}"
            )

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

    if check_clickhouse_version(
        f">={version_when_attach_partition_with_different_keys_merged}"
    )(self):
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
        if with_id:
            partition_list_query = f"SELECT partition_id FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id FORMAT TabSeparated"
        else:
            partition_list_query = f"SELECT partition FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id FORMAT TabSeparated"

        partition_ids = sorted(
            list(
                set(get_node(self, "source").query(partition_list_query).output.split())
            )
        )
        valid, reason = valid_partition_key_pair(
            source_partition_key, destination_partition_key
        )

    with And("I attach partition from source table to the destination table"):
        if valid:
            for partition_id in partition_ids:
                if with_id:
                    query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION ID '{partition_id}' FROM {source_table_name}"
                else:
                    query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"

                self.context.node_1.query(query)
                self.context.node_1.query(
                    f"SELECT * FROM {destination_table_name} format PrettyCompactMonoBlock"
                )

        else:
            if reason == "monotonicity not implemented":
                exitcode, message = (
                    36,
                    "DB::Exception: Monotonicity check not implemented or not available for partition expression",
                )
                check(
                    self,
                    partition_ids=partition_ids,
                    source_table_name=source_table_name,
                    destination_table_name=destination_table_name,
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
                    self,
                    partition_ids=partition_ids,
                    source_table_name=source_table_name,
                    destination_table_name=destination_table_name,
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
                        self.context.node_1.query(
                            query,
                            exitcode=exitcode,
                            message=message,
                        )
                    except:
                        note("Partition can be attached")

    with And(
        "I change engine names to compare replicated results with non-replicated results in snapshots"
    ):
        if "Replicated" in self.context.source_engine:
            source_engine = self.context.source_engine.replace("Replicated", "")
        else:
            source_engine = self.context.source_engine
        if "Replicated" in self.context.destination_engine:
            destination_engine = self.context.destination_engine.replace(
                "Replicated", ""
            )
        else:
            destination_engine = self.context.destination_engine

    with Then(
        f"I check that partitions were attached when source table partition_id - {source_partition_key}, destination table partition key - {destination_partition_key}, source table engine - {source_engine}, destination table engine - {destination_engine}:"
    ):
        if valid:
            for attempt in retries(timeout=600, delay=20):
                with attempt:
                    source_partition_data = get_node(self, "source").query(
                        f"SELECT * FROM {source_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
                    )
                    destination_partition_data = get_node(self, "destination").query(
                        f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
                    )
                    assert (
                        destination_partition_data.output
                        == source_partition_data.output
                    ), error()

        elif reason == "partially different":
            addition_to_snapshot_name = (
                "_small" if "small" in source_table.__name__ else ""
            )
            execute_query(
                f"SELECT a,b,c,extra FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated",
                snapshot_name=current().name.split("/")[-1] + addition_to_snapshot_name,
                node=get_node(self, "destination"),
            )

    with And(f"I check that all replicas of destination table have same data:"):
        if "Replicated" in self.context.destination_engine:
            for attempt in retries(timeout=600, delay=20):
                with attempt:
                    destination_partition_data_1 = self.context.node_1.query(
                        f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
                    )
                    destination_partition_data_2 = self.context.node_2.query(
                        f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
                    )
                    destination_partition_data_3 = self.context.node_3.query(
                        f"SELECT * FROM {destination_table_name} ORDER BY a,b,c,extra FORMAT TabSeparated"
                    )
                    assert (
                        destination_partition_data_1.output
                        == destination_partition_data_2.output
                        == destination_partition_data_3.output
                    )

    with And(
        "I check that I can use data in the destination table after detach attach"
    ):
        data_before = self.context.node_1.query(
            f"SELECT * FROM {destination_table_name} WHERE a > 1 ORDER BY a,b,c,extra FORMAT TabSeparated"
        ).output
        self.context.node_1.query(f"DETACH TABLE {destination_table_name}")
        self.context.node_1.query(f"ATTACH TABLE {destination_table_name}")
        data_after = self.context.node_1.query(
            f"SELECT * FROM {destination_table_name} WHERE a > 1 ORDER BY a,b,c,extra FORMAT TabSeparated"
        )
        for attempt in retries(timeout=300, delay=20):
            with attempt:
                assert data_after.output == data_before, error()


@TestScenario
@Flags(TE)
def attach_partition_from(self, with_id=False):
    """Run test check with different partition keys for both source and destination tables
    to see if `attach partition from` is possible."""

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
        partitioned_ReplacingMergeTree,
        partitioned_ReplicatedReplacingMergeTree,
        partitioned_AggregatingMergeTree,
        partitioned_ReplicatedAggregatingMergeTree,
        partitioned_SummingMergeTree,
        partitioned_ReplicatedSummingMergeTree,
        partitioned_CollapsingMergeTree,
        partitioned_ReplicatedCollapsingMergeTree,
        partitioned_VersionedCollapsingMergeTree,
        partitioned_ReplicatedVersionedCollapsingMergeTree,
        partitioned_GraphiteMergeTree,
        partitioned_ReplicatedGraphiteMergeTree,
    }

    destination_table_types = {
        empty_partitioned_MergeTree,
        empty_partitioned_ReplicatedMergeTree,
        empty_partitioned_ReplacingMergeTree,
        empty_partitioned_ReplicatedReplacingMergeTree,
        empty_partitioned_AggregatingMergeTree,
        empty_partitioned_ReplicatedAggregatingMergeTree,
        empty_partitioned_SummingMergeTree,
        empty_partitioned_ReplicatedSummingMergeTree,
        empty_partitioned_CollapsingMergeTree,
        empty_partitioned_ReplicatedCollapsingMergeTree,
        empty_partitioned_VersionedCollapsingMergeTree,
        empty_partitioned_ReplicatedVersionedCollapsingMergeTree,
        empty_partitioned_GraphiteMergeTree,
        empty_partitioned_ReplicatedGraphiteMergeTree,
    }

    if self.context.stress:
        source_table_types = {
            partitioned_MergeTree,
            partitioned_small_MergeTree,
            partitioned_small_ReplicatedMergeTree,
            partitioned_ReplicatedMergeTree,
        }
        destination_table_types = {
            empty_partitioned_MergeTree,
            empty_partitioned_ReplicatedMergeTree,
        }
        # since pr that allows to attach partition with different partition keys is not implemented,
        # there is no need to test all combinations

        # partition_keys_pairs = product(
        #     source_partition_keys, destination_partition_keys
        # )
        partition_keys = source_partition_keys
        table_pairs = product(source_table_types, destination_table_types)
        combinations = product(partition_keys, table_pairs)
    else:
        # combinations_dict = {
        #     "source_table": source_table_types,
        #     "destination_table": destination_table_types,
        #     "source_key": source_partition_keys,
        #     "destination_key": destination_partition_keys,
        # }
        combinations_dict = {
            "source_table": list(source_table_types),
            "destination_table": list(destination_table_types),
            "partition_key": list(source_partition_keys),
        }
        covering_array = CoveringArray(combinations_dict, strength=3)
        combinations = [
            (
                item["partition_key"],
                (item["source_table"], item["destination_table"]),
            )
            for item in covering_array
        ]

    with Pool(4) as executor:
        for partition_keys, tables in combinations:
            partition_key = partition_keys
            source_table, destination_table = tables

            partition_key_str = clean_name(partition_key)

            Scenario(
                f"combination partition keys {partition_key_str} tables {source_table.__name__} {destination_table.__name__}",
                test=check_attach_partition_from,
                parallel=True,
                executor=executor,
            )(
                source_table=source_table,
                destination_table=destination_table,
                source_partition_key=partition_key,
                destination_partition_key=partition_key,
                with_id=with_id,
            )
        join()


@TestFeature
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Key_PartitionKey_Different(
        "1.0"
    ),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Key_PartitionKey_Unpartitioned(
        "1.0"
    ),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_SupportedTableEngines("1.0"),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Replicas("1.0"),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom("1.0"),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_KeepData("1.0"),
)
@Name("partition key")
def feature(self):
    """Check conditions for partition key when using `attach partition from` statement
    with different partition keys."""

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node("clickhouse1"),
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]

    with Pool(2) as pool:
        Scenario(
            "attach partition from without id",
            test=attach_partition_from,
            parallel=True,
            executor=pool,
        )(with_id=False)
        Scenario(
            "attach partition from with id",
            test=attach_partition_from,
            parallel=True,
            executor=pool,
        )(with_id=True)
        join()
