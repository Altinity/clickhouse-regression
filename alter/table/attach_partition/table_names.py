from testflows.core import *
from testflows.asserts import error
import string
import random

from alter.table.attach_partition.common import (
    create_partitioned_table_with_data,
    create_empty_partitioned_table,
)
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import getuid

part_of_unicode = []
ascii_letters = {i for i in string.ascii_letters}
all_ascii = {i for i in string.printable}
exclude = {"`", '"', "\\"}
not_letters = all_ascii.difference(ascii_letters).difference(exclude)


def valid_name(source_table_name, destination_table_name):
    invalid = ["."] + [i for i in not_letters] + part_of_unicode
    if "_" in invalid:
        invalid.remove("_")
    valid = ["a" * 10000] + [i for i in ascii_letters] + ["_"]

    if destination_table_name in invalid or source_table_name in invalid:
        return 62, "Syntax error: failed at position"
    elif destination_table_name in valid or source_table_name in valid:
        note("Could not find a table or table does not exist")
        return 60, "DB::Exception: "
    else:
        return None, None


@TestScenario
@Flags(TE)
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_TableName("1.0"))
def check_table_name(
    self,
    source_name,
    destination_name,
    with_id,
    source_table,
):
    """Check if table name is valid."""

    node = self.context.node

    with Given("I get partition ids"):
        if with_id:
            partition_list_query = f"SELECT partition_id FROM system.parts WHERE table='{source_table}' ORDER BY partition_id FORMAT TabSeparated"
        else:
            partition_list_query = f"SELECT partition FROM system.parts WHERE table='{source_table}' ORDER BY partition_id FORMAT TabSeparated"

        partition_ids = sorted(
            list(set(node.query(partition_list_query).output.split()))
        )

    with Then("I try to attach partitions from source table to the destination table"):
        if "source" in source_name and "destination" in destination_name:
            for partition_id in partition_ids:
                if with_id:
                    query = f"ALTER TABLE {destination_name} ATTACH PARTITION ID '{partition_id}' FROM {source_table}"
                else:
                    query = f"ALTER TABLE {destination_name} ATTACH PARTITION {partition_id} FROM {source_table}"
                node.query(query)
        elif "source" in destination_name and "destination" in source_name:
            pass
        else:
            exitcode, message = valid_name(source_name, destination_name)
            for partition_id in partition_ids:
                if with_id:
                    query = f"ALTER TABLE {destination_name} ATTACH PARTITION ID '{partition_id}' FROM {source_name}"
                else:
                    query = f"ALTER TABLE {destination_name} ATTACH PARTITION {partition_id} FROM {source_name}"

                result = node.query(query, no_checks=True)
                assert message in result.output, error()
                assert exitcode == result.exitcode, error()


@TestSketch(Scenario)
@Flags(TE)
def table_names(self, source_table, destination_table, with_id=False):
    """Run test check with different table names to see if `attach partition from` is possible."""

    ascii_letters = {i for i in string.ascii_letters}

    if self.context.stress:
        table_names_all = (
            {
                source_table,
                destination_table,
                "a" * 10000,
            }
            | ascii_letters
            | not_letters
            | part_of_unicode
        )
    else:
        table_names_all = (
            {
                source_table,
                destination_table,
                "a" * 10000,
            }
            | set(random.sample(sorted(ascii_letters), 5))
            | set(random.sample(list(not_letters), 10))
            | set(random.sample(part_of_unicode, 10))
        )

    check_table_name(
        source_name=either(*table_names_all),
        destination_name=either(*table_names_all),
        with_id=with_id,
        source_table=source_table,
    )


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_TableName("1.0"))
@Name("table names")
def feature(self, node="clickhouse1"):
    """Run test check with different table names to see if `attach partition from` is possible."""

    self.context.node = self.context.cluster.node(node)
    source_table = "source_" + getuid()
    destination_table = "destination_" + getuid()

    for i in range(2000, 4000, 100):
        part_of_unicode.append(chr(i))

    create_partitioned_table_with_data(
        table_name=source_table,
        partition_by="a",
    )
    create_empty_partitioned_table(
        table_name=destination_table,
        partition_by="a",
    )

    Scenario("check table names with id", test=table_names)(
        with_id=True, source_table=source_table, destination_table=destination_table
    )
    Scenario("check table names without id", test=table_names)(
        with_id=False, source_table=source_table, destination_table=destination_table
    )
