from testflows.core import *

from helpers.common import *
from helpers.tables import Column
from helpers.datatypes import UInt64, UInt16

from alter.table.attach_partition.common import (
    create_partitioned_table_with_data,
    create_empty_partitioned_table,
)
from alter.table.attach_partition.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_Structure(
        "1.0"
    )
)
def structure(self):
    """Check that it is not possible to attach partition to the destination table when the destination and source
    table have different structure."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    columns = [
        Column(name="a", datatype=UInt16()),
        Column(name="b", datatype=UInt16()),
        Column(name="c", datatype=UInt16()),
        Column(name="extra", datatype=UInt64()),
    ]

    with Given("I have a partitioned destination table"):
        create_empty_partitioned_table(
            table_name=destination_table, columns=columns, partition_by="a"
        )

    with And(
        "I have a partitioned source table with a different structure",
        description="this table has more columns compared to the destination table",
    ):
        create_partitioned_table_with_data(table_name=source_table, partition_by="a")

    with Then(
        "I try to attach partition to the destination table from the source table with a different structure"
    ):
        exitcode, message = 122, "DB::Exception: Tables have different structure"
        attach_partition_from(
            destination_table=destination_table,
            source_table=source_table,
            exitcode=exitcode,
            message=message,
        )


@TestStep
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_Key_OrderByKey(
        "1.0"
    )
)
def check_order_by(
    self, source_table, destination_table, source_order_by_key, destination_order_by_key
):
    """Check that it is possible to attach partition to the destination table from the source table only
    when both tables have same order by key."""

    node = self.context.node
    source_table_name = "source_" + getuid()
    destination_table_name = "destination_" + getuid()

    with Given(
        "I create two tables with specified order by keys",
        description=f"""
            source table order by key: {source_order_by_key}
            destination table order by key: {destination_order_by_key}
            """,
    ):
        source_table(
            table_name=source_table_name,
            order_by=source_order_by_key,
            partition_by="a",
        )
        destination_table(
            table_name=destination_table_name,
            order_by=destination_order_by_key,
            partition_by="a",
        )

    with And(
        "I try to attach partition to the destination table from the source table"
    ):
        partition_list_query = f"SELECT partition FROM system.parts WHERE table='{source_table_name}' ORDER BY partition_id FORMAT TabSeparated"

        partition_ids = sorted(
            list(set(node.query(partition_list_query).output.split()))
        )
        if source_order_by_key == destination_order_by_key:
            exitcode, message = None, None
        else:
            exitcode, message = 36, "DB::Exception: Tables have different ordering"

        for partition_id in partition_ids:
            query = f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition_id} FROM {source_table_name}"
            node.query(query, exitcode=exitcode, message=message)


@TestSketch(Scenario)
@Flags(TE)
def order_by(self, with_id=False):
    """Run test check with different order by keys for both source and destination tables to see if `attach partition from` is possible."""

    order_by_keys = {
        "tuple()",
        "a",
        "a%2",
        "a%3",
        "b",
        "(a,b)",
        "(b,a)",
    }

    check_order_by(
        source_table=create_partitioned_table_with_data,
        destination_table=create_empty_partitioned_table,
        source_order_by_key=either(*order_by_keys),
        destination_order_by_key=either(*order_by_keys),
    )


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_Key_PrimaryKey(
        "1.0"
    )
)
def check_primary_key(self, source_primary_key, destination_primary_key):
    """Check that it is possible to attach partition to the destination table from the source when
    the destination table and source table have same primary keys."""

    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I create source and destination tables with specified primary keys",
        description=f"""
            source table primary key: {source_primary_key}
            destination table primary key: {destination_primary_key}
            """,
    ):
        create_partitioned_table_with_data(
            table_name=destination_table,
            partition_by="a",
            primary_key=destination_primary_key,
            order_by="(a,b,c)",
        )
        create_partitioned_table_with_data(
            table_name=source_table,
            partition_by="a",
            primary_key=source_primary_key,
            order_by="(a,b,c)",
        )

    with Then(
        "I try to attach partition to the destination table from the source table"
    ):
        if source_primary_key == destination_primary_key:
            exitcode, message = None, None
        else:
            exitcode, message = 36, "DB::Exception: Tables have different primary key"

        attach_partition_from(
            destination_table=destination_table,
            source_table=source_table,
            exitcode=exitcode,
            message=message,
        )


@TestSketch(Scenario)
@Flags(TE)
def primary_key(self):
    """Run test check with different primary keys for both source and destination
    tables to see if `attach partition from` is possible."""

    primary_keys = {
        "tuple()",
        "a",
        "(a,b)",
        "(a,b,c)",
    }

    check_primary_key(
        source_primary_key=either(*primary_keys),
        destination_primary_key=either(*primary_keys),
    )


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_StoragePolicy(
        "1.0"
    )
)
def check_storage_policy(self, source_storage_policy, destination_storage_policy):
    """Check that it is possible to attach partition to the destination table from the source when
    the destination table and source table have same storage policies."""

    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I create source and destination tables with specified storage policies",
        description=f"""
            source table storage policy: {source_storage_policy}
            destination table storage policy: {destination_storage_policy}
            """,
    ):
        create_partitioned_table_with_data(
            table_name=destination_table,
            query_settings=f"storage_policy = '{destination_storage_policy}'",
            partition_by="a",
        )
        create_partitioned_table_with_data(
            table_name=source_table,
            query_settings=f"storage_policy = '{source_storage_policy}'",
            partition_by="a",
        )

    with Then(
        "I try to attach partition to the destination table from the source table"
    ):
        if (
            source_storage_policy == destination_storage_policy
            or check_clickhouse_version(f">=24.6")(self)
        ):
            exitcode, message = None, None
        else:
            exitcode, message = 36, "DB::Exception: Could not clone and load part"

        attach_partition_from(
            destination_table=destination_table,
            source_table=source_table,
            exitcode=exitcode,
            message=message,
        )


@TestSketch(Scenario)
@Flags(TE)
def storage_policy(self):
    """Run test check with different storage policies for both source and destination
    tables to see if `attach partition from` is possible."""

    storage_policies = {
        "policy1",
        "policy2",
    }

    check_storage_policy(
        source_storage_policy=either(*storage_policies),
        destination_storage_policy=either(*storage_policies),
    )


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_IndicesAndProjections(
        "1.0"
    )
)
def indices(self):
    """Check that it is possible to attach partition to the destination table from the source when
    the destination table and source table have same indices."""

    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I create source and destination tables with different indices",
    ):
        create_partitioned_table_with_data(
            table_name=source_table,
            partition_by="a",
        )
        create_partitioned_table_with_data(
            table_name=destination_table,
            partition_by="a",
            bias=5,
        )

    with And("I add skipping index to source table"):
        self.context.node.query(
            f"ALTER TABLE {source_table} ADD INDEX vix b TYPE set(100) GRANULARITY 2;"
        )

    with Then(
        "I try to attach partition to the destination table from the source table"
    ):
        exitcode, message = 36, "DB::Exception: Tables have different secondary indices"
        attach_partition_from(
            destination_table=destination_table,
            source_table=source_table,
            exitcode=exitcode,
            message=message,
        )

    with And("I add the same skipping index to destination table"):
        self.context.node.query(
            f"ALTER TABLE {destination_table} ADD INDEX vix b TYPE set(100) GRANULARITY 2;"
        )

    with Then(
        "I try to attach partition to the destination table from the source table"
    ):
        attach_partition_from(
            destination_table=destination_table,
            source_table=source_table,
        )

    with And("I check that partition was attached"):
        partition_values_source = self.context.node.query(
            f"SELECT * FROM {source_table} WHERE a == 1 ORDER BY tuple(*) FORMAT TabSeparated"
        ).output
        partition_values_destination = self.context.node.query(
            f"SELECT * FROM {destination_table} WHERE a == 1 ORDER BY tuple(*) FORMAT TabSeparated"
        ).output

        assert partition_values_source == partition_values_destination


@TestScenario
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_IndicesAndProjections(
        "1.0"
    )
)
def projections(self):
    """Check that it is possible to attach partition to the destination table from the source when
    the destination table and source table have same projections."""

    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I create source and destination tables with different projections",
    ):
        create_partitioned_table_with_data(
            table_name=source_table,
            partition_by="a",
        )
        create_partitioned_table_with_data(
            table_name=destination_table,
            partition_by="a",
            bias=5,
        )

    with And("I add projection to source table"):
        self.context.node.query(
            f"ALTER TABLE {source_table} ADD PROJECTION some_projection (SELECT * ORDER BY a)"
        )

    with Then(
        "I try to attach partition to the destination table from the source table"
    ):
        exitcode, message = 36, "DB::Exception: Tables have different projections"
        attach_partition_from(
            destination_table=destination_table,
            source_table=source_table,
            exitcode=exitcode,
            message=message,
        )

    with And("I add the same projection to destination table"):
        self.context.node.query(
            f"ALTER TABLE {destination_table} ADD PROJECTION some_projection (SELECT * ORDER BY a)"
        )

    with Then(
        "I try to attach partition to the destination table from the source table"
    ):
        attach_partition_from(
            destination_table=destination_table,
            source_table=source_table,
        )

    with And("I check that partition was attached"):
        partition_values_source = self.context.node.query(
            f"SELECT * FROM {source_table} WHERE a == 1 ORDER BY tuple(*) FORMAT TabSeparated"
        ).output
        partition_values_destination = self.context.node.query(
            f"SELECT * FROM {destination_table} WHERE a == 1 ORDER BY tuple(*) FORMAT TabSeparated"
        ).output

        assert partition_values_source == partition_values_destination


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions("1.0"))
@Name("conditions")
def feature(self, node="clickhouse1"):
    """Check that it is not possible to attach the partition from the source table to the
    destination table when these two tables have different:
    * Structure
    * Order By key
    * Primary key
    * Storage Policy
    * Indices and projections
    """

    self.context.node = self.context.cluster.node(node)

    Scenario(run=structure)
    Scenario(run=order_by)
    Scenario(run=primary_key)
    Scenario(run=storage_policy)
    Scenario(run=indices)
    Scenario(run=projections)
