from testflows.asserts import *
from testflows.core import *

from alter.table.attach_partition.requirements.requirements import *
from helpers.common import (
    getuid,
    attach_partition,
    detach_partition,
    attach_partition_from,
    attach_part,
    detach_part,
)
from helpers.tables import create_table_partitioned_by_column

one_part = ["1_1_1_0"]
second_part = ["1_2_2_0"]
multiple_parts = ["1_1_1_0", "1_2_2_0"]
all_parts = ["1_1_1_0", "1_2_2_0", "1_3_3_0"]

after_attach = {"1_1_1_0": "1_4_4_0", "1_2_2_0": "1_5_5_0", "1_3_3_0": "1_6_6_0"}
after_attach_detached_part = {"1_1_1_0": "1_4_4_0", "1_2_2_0": "1_2_2_0"}


@TestStep(When)
def corrupt_parts_on_table_partition(self, table_name, parts, bits_to_corrupt=1500000):
    """Corrupt the selected part file."""
    node = self.context.node
    bash_tools = self.context.cluster.node("bash-tools")

    with By(
        f"executing a corrupt_file script that will flip {bits_to_corrupt} bits on the {parts} part of the {table_name} table"
    ):
        for part in parts:
            original_path = f"/var/lib/clickhouse/data/default/{table_name}/{part}/"
            temp_path = f"/share/corrupt_files/{table_name}/{part}/"

            node.command(
                f"mkdir -p {temp_path} && cp {original_path}data.bin {temp_path}"
            )
            bash_tools.command(f"corrupt_file {temp_path}data.bin {bits_to_corrupt}")
            node.command(f"cp {temp_path}data.bin {original_path}")


@TestStep(When)
def corrupt_parts_on_table_partition_detached(
    self, table_name, parts, bits_to_corrupt=1500000
):
    """Corrupt the selected part file."""
    node = self.context.node
    bash_tools = self.context.cluster.node("bash-tools")

    with By(
        f"executing a corrupt_file script that will flip {bits_to_corrupt} bits on the {parts} part of the {table_name} table"
    ):
        node.command("mkdir -p /share/corrupt_files/" + table_name)
        for part in parts:
            original_path = (
                f"/var/lib/clickhouse/data/default/{table_name}/detached/{part}/"
            )
            temp_path = f"/share/corrupt_files/{table_name}/detached/{part}/"

            node.command(
                f"mkdir -p {temp_path} && cp {original_path}data.bin {temp_path}"
            )
            bash_tools.command(f"corrupt_file {temp_path}data.bin {bits_to_corrupt}")
            node.command(f"cp {temp_path}data.bin {original_path}")


@TestCheck
def check_attach_partition_from_with_corrupted_parts(
    self, corrupt_source, corrupt_destination=None
):
    """Attach partition from when parts on one or both of the tables are corrupted."""

    node = self.context.node
    source_table = "source_" + getuid()
    destination_table = "destination_" + getuid()
    partition = 1

    with Given(
        "I have two tables with the same structure",
        description=f"""
            source_table with: {corrupt_source.__name__}    
            destination_table with: {corrupt_destination.__name__}
        """,
    ):
        create_table_partitioned_by_column(
            table_name=destination_table,
        )
        create_table_partitioned_by_column(
            table_name=source_table,
        )

    with And(
        "I populate these tables with data to create a partition with a set number of parts",
        description="""this will create a partition with three parts [
            "1_1_1_0",
            "1_2_2_0",
            "1_3_3_0",
        ]""",
    ):
        for i in range(1, 4):
            node.query(
                f"INSERT INTO {destination_table} (p, i) SELECT {partition}, {i} FROM numbers({i});"
            )
            node.query(
                f"INSERT INTO {source_table} (p, i) SELECT {partition}, {i} FROM numbers({i});"
            )

    with When("I change some bit values of the part on one of or both tables"):
        corrupt_destination(table_name=destination_table)
        corrupt_source(table_name=source_table)

    with Then(
        "I attach partition from the source table to the destination table and validate data"
    ):
        parts_before_attach = node.query(
            f"SELECT partition, part_type, name FROM system.parts WHERE table = '{destination_table}' ORDER BY tuple(*) FORMAT TabSeparated"
        )

        attach_partition_from(
            destination_table=destination_table,
            source_table=source_table,
            partition=partition,
        )

        parts_after_attach = node.query(
            f"SELECT partition, part_type, name FROM system.parts WHERE table = '{destination_table}' ORDER BY tuple(*) FORMAT TabSeparated"
        )

    with And("I try to read data from the destination table"):
        source_name = corrupt_source.__name__
        destination_name = corrupt_destination.__name__

        if source_name == "corrupt_no_parts" and destination_name == "corrupt_no_parts":
            message = None
        else:
            message = "DB::Exception:"

        node.query(
            f"SELECT * FROM {destination_table} FORMAT TabSeparated",
            message=message,
        )

    with And(
        "I check that data was attached to the destination table",
        description="this allows us to validate that the partitions were attached by validating that the inside the "
        "system.parts table the data for destination table was updated.",
    ):

        assert parts_before_attach.output.strip() != parts_after_attach.output.strip()

    with And(
        "I detach all the corrupted parts and check that it is possible to read data from the destination table without any errors",
    ):
        if source_name != "corrupt_no_parts":
            for part in self.context.source_parts:
                node.query(
                    f"ALTER TABLE {destination_table} DETACH PART '{after_attach[part]}';"
                )

        if destination_name != "corrupt_no_parts":
            for part in self.context.destination_parts:
                node.query(f"ALTER TABLE {destination_table} DETACH PART '{part}';")

        for retry in retries(timeout=10):
            with retry:
                node.query(
                    f"SELECT * FROM {destination_table} FORMAT TabSeparated",
                )


@TestCheck
def check_attach_partition_detached_with_corrupted_parts(self, corrupt):
    """Attach partition from detached folder when parts are corrupted."""
    node = self.context.node
    table = getuid()

    self.context.parts = []

    with Given(
        "I create table",
        description=f"""
            table with: {corrupt.__name__}    
        """,
    ):
        create_table_partitioned_by_column(
            table_name=table,
        )

    with And(
        "I populate the table with data to create a partition with a set number of parts",
        description="""this will create a partition with three parts [
            "1_1_1_0",
            "1_2_2_0",
            "1_3_3_0",
        ]""",
    ):
        partition = 1
        for i in range(3):
            node.query(
                f"INSERT INTO {table} (p, i) SELECT {partition}, {i} FROM numbers({i+1});"
            )

    node.query(
        f"SELECT partition, part_type, name, active, rows FROM system.parts WHERE table = '{table}' ORDER BY tuple(*) FORMAT TabSeparated"
    )

    with And("I detach partition from table"):
        detach_partition(table=table, partition="1")
        node.query(
            f"SELECT * FROM {table} FORMAT TabSeparated",
        )
        node.query(
            f"SELECT partition, part_type, name, active, rows FROM system.parts WHERE table = '{table}' ORDER BY tuple(*) FORMAT TabSeparated"
        )

    with When("I change some bit values of the partition"):
        corrupt(table_name=table)

    with Then("I attach part from the detached folder"):
        parts_before_attach = node.query(
            f"SELECT partition, part_type, name, active, rows FROM system.parts WHERE table = '{table}' ORDER BY tuple(*) FORMAT TabSeparated"
        )

        attach_partition(
            table=table,
            partition=partition,
        )

        parts_after_attach = node.query(
            f"SELECT partition, part_type, name, active, rows FROM system.parts WHERE table = '{table}' ORDER BY tuple(*) FORMAT TabSeparated"
        )
        parts = [i.split("\t") for i in parts_after_attach.output.split("\n")]
        after_attach_detached = {}
        for part in parts:
            if part[-1].strip() == "1":
                note("here")
                after_attach_detached["1_1_1_0"] = part[2].strip()
            if part[-1].strip() == "2":
                after_attach_detached["1_2_2_0"] = part[2].strip()
            if part[-1].strip() == "3":
                after_attach_detached["1_3_3_0"] = part[2].strip()

    with And("I try to read data from the table"):
        corrupt_type = corrupt.__name__

        if corrupt_type == "corrupt_no_parts":
            message = None
        else:
            message = "DB::Exception:"

        node.query(
            f"SELECT * FROM {table} FORMAT TabSeparated",
            message=message,
        )

    with And(
        "I check that data was attached to the destination table",
        description="this allows us to validate that the partitions were attached by validating that the inside the "
        "system.parts table the data for the table was updated.",
    ):

        assert parts_before_attach.output.strip() != parts_after_attach.output.strip()

    with And(
        "I detach all the corrupted parts and check that it is possible to read data from the table without any errors",
    ):
        note("Corrupted parts:")
        note(self.context.destination_parts)
        if corrupt_type != "corrupt_no_parts":
            for part in self.context.destination_parts:
                node.query(
                    f"ALTER TABLE {table} DETACH PART '{after_attach_detached[part]}'"
                )

        for retry in retries(timeout=10):
            with retry:
                node.query(
                    f"SELECT * FROM {table} FORMAT TabSeparated",
                )


@TestCheck
def check_attach_corrupted_part(self, corrupt):
    """Check attach part from detached folder when parts are corrupted."""
    node = self.context.node
    table = getuid()

    self.context.parts = []

    with Given(
        "I create table",
        description=f"""
            table with: {corrupt.__name__}    
        """,
    ):
        create_table_partitioned_by_column(
            table_name=table,
        )

    with And(
        "I populate the table with data to create a partition with a set number of parts",
        description="""this will create a partition with three parts [
            "1_1_1_0",
            "1_2_2_0",
            "1_3_3_0",
        ]""",
    ):
        partition = 1
        for i in range(3):
            node.query(
                f"INSERT INTO {table} (p, i) SELECT {partition}, {i} FROM numbers({i+1});"
            )

    node.query(
        f"SELECT partition, part_type, name, active, rows FROM system.parts WHERE table = '{table}' ORDER BY tuple(*) FORMAT TabSeparated"
    )
    with And("I detach part from table"):
        detach_part(table=table, part="1_1_1_0")
        node.query(
            f"SELECT * FROM {table} FORMAT TabSeparated",
        )
        node.query(
            f"SELECT partition, part_type, name, active, rows FROM system.parts WHERE table = '{table}' ORDER BY tuple(*) FORMAT TabSeparated"
        )

    with When("I change some bit values of the parts"):
        corrupt(table_name=table)

    with Then("I attach part from the detached folder"):
        parts_before_attach = node.query(
            f"SELECT partition, part_type, name, active, rows FROM system.parts WHERE table = '{table}' ORDER BY tuple(*) FORMAT TabSeparated"
        )

        attach_part(
            table=table,
            part="1_1_1_0",
        )

        parts_after_attach = node.query(
            f"SELECT partition, part_type, name, active, rows FROM system.parts WHERE table = '{table}' ORDER BY tuple(*) FORMAT TabSeparated"
        )

    with And("I try to read data from the table"):
        corrupt_type = corrupt.__name__

        if corrupt_type == "corrupt_no_parts":
            message = None
        else:
            message = "DB::Exception:"

        node.query(
            f"SELECT * FROM {table} FORMAT TabSeparated",
            message=message,
        )

    with And(
        "I check that data was attached to the destination table",
        description="this allows us to validate that the part was attached by validating that the inside the "
        "system.parts table the data for the table was updated.",
    ):

        assert parts_before_attach.output.strip() != parts_after_attach.output.strip()

    with And(
        "I detach all the corrupted parts and check that it is possible to read data from the table without any errors",
    ):
        if corrupt_type != "corrupt_no_parts":
            for part in self.context.destination_parts:
                node.query(
                    f"ALTER TABLE {table} DETACH PART '{after_attach_detached_part[part]}'"
                )

        for retry in retries(timeout=10, delay=2):
            with retry:
                node.query(
                    f"SELECT * FROM {table} FORMAT TabSeparated",
                )


@TestStep(When)
def corrupt_one_part(self, table_name):
    """Corrupt a single part of the partition."""
    if "source" in table_name:
        self.context.source_parts = one_part
    else:
        self.context.destination_parts = one_part

    corrupt_parts_on_table_partition(table_name=table_name, parts=one_part)


@TestStep(When)
def corrupt_one_part_detached(self, table_name):
    """Corrupt a single part of the partition."""
    self.context.destination_parts = one_part

    corrupt_parts_on_table_partition_detached(table_name=table_name, parts=one_part)


@TestStep(When)
def corrupt_second_part(self, table_name):
    """Corrupt a single part of the partition."""
    self.context.destination_parts = second_part

    corrupt_parts_on_table_partition(table_name=table_name, parts=second_part)


@TestStep(When)
def corrupt_two_parts(self, table_name):
    """Corrupt a single part of the partition."""
    self.context.destination_parts = ["1_1_1_0", "1_2_2_0"]

    corrupt_parts_on_table_partition_detached(table_name=table_name, parts=["1_1_1_0"])
    corrupt_parts_on_table_partition(table_name=table_name, parts=["1_2_2_0"])


@TestStep(When)
def corrupt_multiple_parts(self, table_name):
    """Corrupt multiple parts of the partition."""
    if "source" in table_name:
        self.context.source_parts = multiple_parts
    else:
        self.context.destination_parts = multiple_parts

    corrupt_parts_on_table_partition(table_name=table_name, parts=multiple_parts)


@TestStep(When)
def corrupt_multiple_parts_detached(self, table_name):
    """Corrupt a single part of the partition."""
    self.context.destination_parts = multiple_parts

    corrupt_parts_on_table_partition_detached(
        table_name=table_name, parts=multiple_parts
    )


@TestStep(When)
def corrupt_all_parts(self, table_name):
    """Corrupt all parts of the partition."""
    if "source" in table_name:
        self.context.source_parts = all_parts
    else:
        self.context.destination_parts = all_parts

    corrupt_parts_on_table_partition(table_name=table_name, parts=all_parts)


@TestStep(When)
def corrupt_all_parts_detached(self, table_name):
    """Corrupt a single part of the partition."""
    self.context.destination_parts = all_parts

    corrupt_parts_on_table_partition_detached(table_name=table_name, parts=all_parts)


@TestStep(When)
def corrupt_no_parts(self, table_name):
    """Corrupt no parts of the partition."""
    if "source" in table_name:
        self.context.source_parts = []
    else:
        self.context.destination_parts = []
    with By(f"not corrupting a {table_name} table"):
        note(f"{table_name} is not corrupted")


@TestSketch(Scenario)
@Flags(TE)
def attach_partition_from_with_corrupted_parts(self):
    """Check attach partition with different amounts of parts being corrupted on one or both tables."""
    values = {
        corrupt_no_parts,
        corrupt_all_parts,
        corrupt_multiple_parts,
        corrupt_one_part,
    }

    check_attach_partition_from_with_corrupted_parts(
        corrupt_destination=either(*values),
        corrupt_source=either(*values),
    )


@TestSketch(Scenario)
@Flags(TE)
def attach_partition_detached_with_corrupted_parts(self):
    """Check attach partition with different amounts of parts being corrupted."""
    values = {
        corrupt_no_parts,
        corrupt_all_parts_detached,
        corrupt_multiple_parts_detached,
        corrupt_one_part_detached,
    }

    check_attach_partition_detached_with_corrupted_parts(
        corrupt=either(*values),
    )


@TestSketch(Scenario)
@Flags(TE)
def attach_corrupted_part(self):
    """
    Check attach partition with different amounts of parts being corrupted.

    Combinations:
    Attach non-corrupted to non-corrupted table
    Attach corrupted part to non-corrupted table
    Attach non-corrupted part to corrupted table
    Attach corrupted part to corrupted table
    """
    values = {
        corrupt_no_parts,
        corrupt_one_part_detached,
        corrupt_second_part,
        corrupt_two_parts,
    }

    check_attach_corrupted_part(
        corrupt=either(*values),
    )


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_CorruptedParts("1.0"))
@Name("corrupted partitions")
def feature(self, node="clickhouse1"):
    """
    Check how clickhouse behaves when attach partition with corrupted parts inside partitions.

    Combinations:
    * None of the parts are corrupted
    * One part is corrupted
    * Multiple parts are corrupted
    * All parts are corrupted
    """
    self.context.node = self.context.cluster.node(node)

    Scenario(run=attach_partition_from_with_corrupted_parts)
    Scenario(run=attach_partition_detached_with_corrupted_parts)
    Scenario(run=attach_corrupted_part)
