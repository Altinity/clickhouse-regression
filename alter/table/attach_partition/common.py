import platform

from testflows.asserts import values, error, snapshot
from testflows.core import *

from helpers.tables import *

version_when_attach_partition_with_different_keys_merged = "26.8"


def clean_name(name):
    return (
        name.replace("(", "_").replace(")", "_").replace(",", "_").replace("%", "mod")
    )


def current_cpu():
    """Return current cpu architecture."""
    arch = platform.processor()
    if arch not in ("x86_64", "aarch64", "arm"):
        raise TypeError(f"unsupported CPU architecture {arch}")
    return arch


@TestStep(Given)
def create_partitioned_table_with_data(
    self,
    table_name,
    engine="MergeTree",
    partition_by="tuple()",
    primary_key=None,
    columns=None,
    query_settings=None,
    order_by="tuple()",
    node=None,
    number_of_partitions=3,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
    bias=0,
    small=False,
):
    """Create a table that is partitioned by specified columns."""

    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if engine == "GraphiteMergeTree":
        engine = f"GraphiteMergeTree('{config}')"
    elif engine == "VersionedCollapsingMergeTree":
        engine = f"VersionedCollapsingMergeTree({sign},{version})"
    elif engine == "CollapsingMergeTree":
        engine = f"CollapsingMergeTree({sign})"

    params = {
        "name": table_name,
        "engine": engine,
        "partition_by": partition_by,
        "primary_key": primary_key,
        "order_by": order_by,
        "columns": columns,
        "query_settings": query_settings,
        "if_not_exists": True,
        "node": node,
    }

    not_none_params = {k: v for k, v in params.items() if v is not None}

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        create_table(**not_none_params)

    with And(f"inserting data that will create multiple partitions"):
        if small:
            node.query(
                f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT 0, 0, 0, number+1000, 1 FROM numbers({4})"
            )
            node.query(
                f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT 1, 1, 1, number+1000, 1 FROM numbers({4})"
            )
        else:
            for i in range(1, number_of_partitions + 1):
                node.query(
                    f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT {i+bias}, {i+4+bias}, {i+8+bias}, number+1000, 1 FROM numbers({4})"
                )
                node.query(
                    f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT number+10, number+{i+bias}+14, number+{i+bias}+18, number+1001, 1 FROM numbers({10})"
                )


@TestStep(Given)
def create_empty_partitioned_table(
    self,
    table_name,
    engine="MergeTree",
    partition_by="tuple()",
    primary_key=None,
    columns=None,
    query_settings=None,
    order_by="tuple()",
    node=None,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
):
    """Create a table that is partitioned by specified columns."""

    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if engine == "GraphiteMergeTree":
        engine = f"GraphiteMergeTree('{config}')"
    elif engine == "VersionedCollapsingMergeTree":
        engine = f"VersionedCollapsingMergeTree({sign},{version})"
    elif engine == "CollapsingMergeTree":
        engine = f"CollapsingMergeTree({sign})"

    params = {
        "name": table_name,
        "engine": engine,
        "partition_by": partition_by,
        "primary_key": primary_key,
        "order_by": order_by,
        "columns": columns,
        "query_settings": query_settings,
        "if_not_exists": True,
        "node": node,
    }

    not_none_params = {k: v for k, v in params.items() if v is not None}

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        create_table(**not_none_params)


@TestStep(Given)
def create_partitioned_table_with_datetime_data(
    self,
    table_name,
    engine="MergeTree",
    partition_by="tuple()",
    primary_key=None,
    columns=None,
    query_settings=None,
    order_by="tuple()",
    node=None,
    number_of_partitions=2,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
    bias=0,
):
    """
    Create a table with DateTite columns that is partitioned by specified columns.
    The function inserts various data points into the table with different time intervals
    (seconds, minutes, hours, days, months, years) to ensure the creation of multiple
    partitions covering a wide range of temporal resolutions.
    """

    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="time", datatype=DateTime()),
            Column(name="date", datatype=Date()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if engine == "GraphiteMergeTree":
        engine = f"GraphiteMergeTree('{config}')"
    elif engine == "VersionedCollapsingMergeTree":
        engine = f"VersionedCollapsingMergeTree({sign},{version})"
    elif engine == "CollapsingMergeTree":
        engine = f"CollapsingMergeTree({sign})"

    params = {
        "name": table_name,
        "engine": engine,
        "partition_by": partition_by,
        "primary_key": primary_key,
        "order_by": order_by,
        "columns": columns,
        "query_settings": query_settings,
        "if_not_exists": True,
        "node": node,
    }

    not_none_params = {k: v for k, v in params.items() if v is not None}

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        create_table(**not_none_params)

    with And(f"inserting various data that will create multiple partitions"):
        note("seconds")
        for i in range(1, number_of_partitions + 1):
            note("different seconds")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+{i}, toDate('2000-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("different seconds and minutes")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+number*60+{i}, toDate('2000-01-01')+1, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different seconds and hours")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+number*60*60+{i}, toDate('2000-01-01')+2, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different seconds and days")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+number*60*60*24+{i}, toDate('2000-01-01')+3, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different seconds and months")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+number*60*60*24*15+{i}, toDate('2000-01-01')+4, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different seconds and years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+number*60*60*24*15*12+{i}, toDate('2000-01-01')+5, number+1000, 1 FROM numbers(5+{i})"
            )
        note("minutes")
        for i in range(1, number_of_partitions + 1):
            note("different minutes")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60+{i}, toDate('2001-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("different minutes and hours")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60+number*60*60+{i}, toDate('2001-01-01')+1, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different minutes and days")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60+number*60*60*15+{i}, toDate('2001-01-01')+2, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different minutes and months")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60+number*60*60*24*15+{i}, toDate('2001-01-01')+3, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different minutes and years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60+number*60*60*24*15*12+{i}, toDate('2001-01-01')+4, number+1000, 1 FROM numbers(5+{i})"
            )
        note("hours")
        for i in range(1, number_of_partitions + 1):
            note("different hours")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60+{i}+number, toDate('2002-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("different hours and days")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60+number*60*60*15+{i}+number, toDate('2002-01-01')+1, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different hours and months")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60+number*60*60*24*15+{i}+number, toDate('2002-01-01')+2, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different hours and years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60+number*60*60*24*15*12+{i}+number, toDate('2002-01-01')+3, number+1000, 1 FROM numbers(5+{i})"
            )
        note("days")
        for i in range(1, number_of_partitions + 1):
            note("different days")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*15+{i}+number, toDate('2003-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("different days and months")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*15+number*60*60*24*15+{i}+number, toDate('2003-01-01')+1, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different days and years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*15+number*60*60*24*15*12+{i}+number, toDate('2003-01-01')+2, number+1000, 1 FROM numbers(5+{i})"
            )
        note("months")
        for i in range(1, number_of_partitions + 1):
            note("different months")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*24*15+{i}, toDate('2004-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("different months and years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*30+number*60*60*24*15*12+{i}, toDate('2004-01-01')+1, number+1000, 1 FROM numbers(5+{i})"
            )
        note("quarters")
        for i in range(1, number_of_partitions + 1):
            note("different quarters")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*30*12+{i}, toDate('2005-01-01'), number+1000, 1 FROM numbers(10+{i})"
            )
        note("years")
        for i in range(1, number_of_partitions + 1):
            note("different years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*3600*24*15*12+{i}, toDate('2006-01-01')+number*15*12, number+1000, 1 FROM numbers(10+{i})"
            )
        note("Insert more various data to cover all possible ranges")
        for i in range(1, number_of_partitions + 1):
            note("toMinute")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2001-01-01 00:00:00')+number+40*60+{i}+5*3600, toDate('2007-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2001-01-01 00:00:00')+number*60+40*60+{i}*60+5*3600, toDate('2008-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("toMonth")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2001-05-01 00:00:00')+number*60+40*60+{i}*60+5*3600, toDate('2008-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("toSecond")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2001-05-01 00:00:00')+number+30+40*60+{i}*60+5*3600, toDate('2009-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
        note("toQuarter")
        node.query(
            f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2011-01-01 00:00:00')+60*60*24*30*7, toDate('2010-01-01'), number+1000, 1 FROM numbers(10)"
        )
        note("toHour")
        node.query(
            f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2012-01-01 00:00:00')+60*60*24+60*60*10, toDate('2010-01-01'), number+1000, 1 FROM numbers(10)"
        )
        note("toMinute")
        node.query(
            f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2012-01-01 00:00:00')+60*60*24+60*24, toDate('2010-01-01'), number+1000, 1 FROM numbers(10)"
        )


@TestStep(Given)
def create_empty_partitioned_table_with_datetime_data(
    self,
    table_name,
    engine="MergeTree",
    partition_by="tuple()",
    primary_key=None,
    columns=None,
    query_settings=None,
    order_by="tuple()",
    node=None,
    number_of_partitions=2,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
    bias=0,
):
    """Create a table that is partitioned by specified columns."""

    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="time", datatype=DateTime()),
            Column(name="date", datatype=Date()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if engine == "GraphiteMergeTree":
        engine = f"GraphiteMergeTree('{config}')"
    elif engine == "VersionedCollapsingMergeTree":
        engine = f"VersionedCollapsingMergeTree({sign},{version})"
    elif engine == "CollapsingMergeTree":
        engine = f"CollapsingMergeTree({sign})"

    params = {
        "name": table_name,
        "engine": engine,
        "partition_by": partition_by,
        "primary_key": primary_key,
        "order_by": order_by,
        "columns": columns,
        "query_settings": query_settings,
        "if_not_exists": True,
        "node": node,
    }

    not_none_params = {k: v for k, v in params.items() if v is not None}

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        create_table(**not_none_params)


@TestStep(Given)
def create_partitioned_replicated_table_with_datetime_data(
    self,
    table_name,
    engine="ReplicatedMergeTree",
    partition_by="tuple()",
    primary_key=None,
    columns=None,
    query_settings=None,
    order_by="tuple()",
    node=None,
    number_of_partitions=2,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
    bias=0,
    nodes=None,
):
    """
    Create a table with DateTite columns that is partitioned by specified columns.
    The function inserts various data points into the table with different time intervals
    (seconds, minutes, hours, days, months, years) to ensure the creation of multiple
    partitions covering a wide range of temporal resolutions.
    """

    if columns is None:
        columns = [
            Column(name="time", datatype=DateTime()),
            Column(name="date", datatype=Date()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if "GraphiteMergeTree" in engine:
        engine = f"ReplicatedGraphiteMergeTree('{config}')"
    elif "VersionedCollapsingMergeTree" in engine:
        engine = f"ReplicatedVersionedCollapsingMergeTree({sign},{version})"
    elif "CollapsingMergeTree" in engine:
        engine = f"ReplicatedCollapsingMergeTree({sign})"

    if nodes is None:
        nodes = self.context.nodes

    if "Replicated" not in engine:
        engine = "Replicated" + engine

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        for node in nodes:
            params = {
                "name": table_name,
                "engine": engine,
                "partition_by": partition_by,
                "primary_key": primary_key,
                "order_by": order_by,
                "cluster": "replicated_cluster_secure",
                "columns": columns,
                "query_settings": query_settings,
                "if_not_exists": True,
                "node": node,
            }
            not_none_params = {k: v for k, v in params.items() if v is not None}
            create_table(**not_none_params)

    node = random.choice(nodes)
    with And(f"inserting various data that will create multiple partitions"):
        note("seconds")
        for i in range(1, number_of_partitions + 1):
            note("different seconds")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+{i}, toDate('2000-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("different seconds and minutes")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+number*60+{i}, toDate('2000-01-01')+1, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different seconds and hours")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+number*60*60+{i}, toDate('2000-01-01')+2, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different seconds and days")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+number*60*60*24+{i}, toDate('2000-01-01')+3, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different seconds and months")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+number*60*60*24*15+{i}, toDate('2000-01-01')+4, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different seconds and years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+number+number*60*60*24*15*12+{i}, toDate('2000-01-01')+5, number+1000, 1 FROM numbers(5+{i})"
            )
        note("minutes")
        for i in range(1, number_of_partitions + 1):
            note("different minutes")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60+{i}, toDate('2001-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("different minutes and hours")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60+number*60*60+{i}, toDate('2001-01-01')+1, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different minutes and days")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60+number*60*60*15+{i}, toDate('2001-01-01')+2, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different minutes and months")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60+number*60*60*24*15+{i}, toDate('2001-01-01')+3, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different minutes and years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60+number*60*60*24*15*12+{i}, toDate('2001-01-01')+4, number+1000, 1 FROM numbers(5+{i})"
            )
        note("hours")
        for i in range(1, number_of_partitions + 1):
            note("different hours")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60+{i}+number, toDate('2002-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("different hours and days")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60+number*60*60*15+{i}+number, toDate('2002-01-01')+1, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different hours and months")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60+number*60*60*24*15+{i}+number, toDate('2002-01-01')+2, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different hours and years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60+number*60*60*24*15*12+{i}+number, toDate('2002-01-01')+3, number+1000, 1 FROM numbers(5+{i})"
            )
        note("days")
        for i in range(1, number_of_partitions + 1):
            note("different days")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*15+{i}+number, toDate('2003-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("different days and months")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*15+number*60*60*24*15+{i}+number, toDate('2003-01-01')+1, number+1000, 1 FROM numbers(5+{i})"
            )
            note("different days and years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*15+number*60*60*24*15*12+{i}+number, toDate('2003-01-01')+2, number+1000, 1 FROM numbers(5+{i})"
            )
        note("months")
        for i in range(1, number_of_partitions + 1):
            note("different months")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*24*15+{i}, toDate('2004-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("different months and years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*30+number*60*60*24*15*12+{i}, toDate('2004-01-01')+1, number+1000, 1 FROM numbers(5+{i})"
            )
        note("quarters")
        for i in range(1, number_of_partitions + 1):
            note("different quarters")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*60*60*30*12+{i}, toDate('2005-01-01'), number+1000, 1 FROM numbers(10+{i})"
            )
        note("years")
        for i in range(1, number_of_partitions + 1):
            note("different years")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2000-01-01 00:00:00')+(number)*3600*24*15*12+{i}, toDate('2006-01-01')+number*15*12, number+1000, 1 FROM numbers(10+{i})"
            )
        note("Insert more various data to cover all possible ranges")
        for i in range(1, number_of_partitions + 1):
            note("toMinute")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2001-01-01 00:00:00')+number+40*60+{i}+5*3600, toDate('2007-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2001-01-01 00:00:00')+number*60+40*60+{i}*60+5*3600, toDate('2008-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("toMonth")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2001-05-01 00:00:00')+number*60+40*60+{i}*60+5*3600, toDate('2008-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
            note("toSecond")
            node.query(
                f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2001-05-01 00:00:00')+number+30+40*60+{i}*60+5*3600, toDate('2009-01-01'), number+1000, 1 FROM numbers(5+{i})"
            )
        note("toQuarter")
        node.query(
            f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2011-01-01 00:00:00')+60*60*24*30*7, toDate('2010-01-01'), number+1000, 1 FROM numbers(10)"
        )
        note("toHour")
        node.query(
            f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2012-01-01 00:00:00')+60*60*24+60*60*10, toDate('2010-01-01'), number+1000, 1 FROM numbers(10)"
        )
        note("toMinute")
        node.query(
            f"INSERT INTO {table_name} (time, date, extra, sign) SELECT toDateTime('2012-01-01 00:00:00')+60*60*24+60*24, toDate('2010-01-01'), number+1000, 1 FROM numbers(10)"
        )

    with And("wait until the data is replicated"):
        for attempt in retries(timeout=300, delay=10):
            with attempt:
                data1 = (
                    self.context.node_1.query(
                        f"SELECT * FROM {table_name} ORDER BY tuple(*)"
                    )
                ).output.strip()
                data2 = (
                    self.context.node_2.query(
                        f"SELECT * FROM {table_name} ORDER BY tuple(*)"
                    )
                ).output.strip()
                data3 = (
                    self.context.node_3.query(
                        f"SELECT * FROM {table_name} ORDER BY tuple(*)"
                    )
                ).output.strip()
                assert data1 == data2 == data3, "Data is not yet replicated"


@TestStep(Given)
def create_empty_partitioned_replicated_table_with_datetime_data(
    self,
    table_name,
    engine="ReplicatedMergeTree",
    partition_by="tuple()",
    primary_key=None,
    columns=None,
    query_settings=None,
    order_by="tuple()",
    node=None,
    number_of_partitions=2,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
    bias=0,
    nodes=None,
):
    """Create a table that is partitioned by specified columns."""

    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="time", datatype=DateTime()),
            Column(name="date", datatype=Date()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if "GraphiteMergeTree" in engine:
        engine = f"ReplicatedGraphiteMergeTree('{config}')"
    elif "VersionedCollapsingMergeTree" in engine:
        engine = f"ReplicatedVersionedCollapsingMergeTree({sign},{version})"
    elif "CollapsingMergeTree" in engine:
        engine = f"ReplicatedCollapsingMergeTree({sign})"

    if nodes is None:
        nodes = self.context.nodes

    if "Replicated" not in engine:
        engine = "Replicated" + engine

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        for node in nodes:
            params = {
                "name": table_name,
                "engine": engine,
                "partition_by": partition_by,
                "primary_key": primary_key,
                "cluster": "replicated_cluster_secure",
                "order_by": order_by,
                "columns": columns,
                "query_settings": query_settings,
                "if_not_exists": True,
                "node": node,
            }
            not_none_params = {k: v for k, v in params.items() if v is not None}
            create_table(**not_none_params)


@TestStep(Given)
def create_partitioned_replicated_table_with_data(
    self,
    table_name: str,
    columns: list[dict] = None,
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
    partition_by: str = None,
    engine="ReplicatedMergeTree",
    query_settings=None,
    nodes=None,
    node=None,
    number_of_partitions=3,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
    bias=0,
    small=False,
):
    """Create a table with the specified engine."""
    if columns is None:
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if "GraphiteMergeTree" in engine:
        engine = f"ReplicatedGraphiteMergeTree('{config}')"
    elif "VersionedCollapsingMergeTree" in engine:
        engine = f"ReplicatedVersionedCollapsingMergeTree({sign},{version})"
    elif "CollapsingMergeTree" in engine:
        engine = f"ReplicatedCollapsingMergeTree({sign})"

    if nodes is None:
        nodes = self.context.nodes

    if "Replicated" not in engine:
        engine = "Replicated" + engine

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        for node in nodes:
            create_table(
                name=table_name,
                columns=columns,
                engine=f"{engine}",
                order_by=order_by,
                primary_key=primary_key,
                comment=comment,
                partition_by=partition_by,
                cluster="replicated_cluster_secure",
                node=node,
                if_not_exists=True,
            )

    node = random.choice(nodes)
    with And(f"inserting data that will create multiple partitions"):
        if small:
            node.query(
                f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT 0, 0, 0, number+1000, 1 FROM numbers({4})"
            )
            node.query(
                f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT 1, 1, 1, number+1000, 1 FROM numbers({4})"
            )
        else:
            for i in range(1, number_of_partitions + 1):
                node.query(
                    f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT {i+bias}, {i+4+bias}, {i+8+bias}, number+1000, 1 FROM numbers({4})"
                )
                node.query(
                    f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT number+10, number+{i+bias}+14, number+{i+bias}+18, number+1001, 1 FROM numbers({10})"
                )

    with And("wait until the data is replicated"):
        for attempt in retries(timeout=300, delay=10):
            with attempt:
                data1 = (
                    self.context.node_1.query(
                        f"SELECT * FROM {table_name} ORDER BY tuple(*)"
                    )
                ).output.strip()
                data2 = (
                    self.context.node_2.query(
                        f"SELECT * FROM {table_name} ORDER BY tuple(*)"
                    )
                ).output.strip()
                data3 = (
                    self.context.node_3.query(
                        f"SELECT * FROM {table_name} ORDER BY tuple(*)"
                    )
                ).output.strip()
                assert data1 == data2 == data3, "Data is not yet replicated"


@TestStep(Given)
def create_empty_partitioned_replicated_table(
    self,
    table_name: str,
    columns: list[dict] = None,
    if_not_exists: bool = False,
    db: str = None,
    comment: str = None,
    primary_key=None,
    order_by: str = "tuple()",
    partition_by: str = None,
    engine="ReplicatedMergeTree",
    query_settings=None,
    nodes=None,
    node=None,
    number_of_partitions=2,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
    bias=0,
):
    """Create a table with the specified engine."""
    if columns is None:
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if "GraphiteMergeTree" in engine:
        engine = f"ReplicatedGraphiteMergeTree('{config}')"
    elif "VersionedCollapsingMergeTree" in engine:
        engine = f"ReplicatedVersionedCollapsingMergeTree({sign},{version})"
    elif "CollapsingMergeTree" in engine:
        engine = f"ReplicatedCollapsingMergeTree({sign})"

    if nodes is None:
        nodes = self.context.nodes

    if "Replicated" not in engine:
        engine = "Replicated" + engine

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        for node in nodes:
            create_table(
                name=table_name,
                columns=columns,
                engine=f"{engine}",
                order_by=order_by,
                primary_key=primary_key,
                comment=comment,
                partition_by=partition_by,
                cluster="replicated_cluster_secure",
                node=node,
                if_not_exists=True,
            )


@TestStep(Given)
def create_temporary_partitioned_table_with_data(
    self,
    table_name: str,
    columns: list[dict] = None,
    order_by: str = "tuple()",
    partition_by: str = None,
    engine="MergeTree",
    node=None,
    number_of_partitions=3,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
    bias=0,
):
    """Create a table with the specified engine."""
    if columns is None:
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if "GraphiteMergeTree" in engine:
        engine = f"GraphiteMergeTree('{config}')"
    elif "VersionedCollapsingMergeTree" in engine:
        engine = f"VersionedCollapsingMergeTree({sign},{version})"
    elif "CollapsingMergeTree" in engine:
        engine = f"CollapsingMergeTree({sign})"

    columns_def = "(" + ",".join([column.full_definition() for column in columns]) + ")"

    with By(f"creating a temporary table that is partitioned by '{partition_by}'"):
        node.query(
            f"CREATE TEMPORARY TABLE {table_name} {columns_def} ENGINE = {engine} PARTITION BY {partition_by} ORDER BY {order_by}"
        )

    for i in range(1, number_of_partitions + 1):
        node.query(
            f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT {i+bias}, {i+4+bias}, {i+8+bias}, number+1000, 1 FROM numbers({4})"
        )
        node.query(
            f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT number+10, number+{i+bias}+14, number+{i+bias}+18, number+1001, 1 FROM numbers({10})"
        )


@TestStep(Given)
def create_empty_temporary_partitioned_table(
    self,
    table_name: str,
    columns: list[dict] = None,
    order_by: str = "tuple()",
    partition_by: str = None,
    engine="MergeTree",
    node=None,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
):
    """Create a table with the specified engine."""
    if columns is None:
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if "GraphiteMergeTree" in engine:
        engine = f"GraphiteMergeTree('{config}')"
    elif "VersionedCollapsingMergeTree" in engine:
        engine = f"VersionedCollapsingMergeTree({sign},{version})"
    elif "CollapsingMergeTree" in engine:
        engine = f"CollapsingMergeTree({sign})"

    columns_def = "(" + ",".join([column.full_definition() for column in columns]) + ")"

    with By(f"creating a temporary table that is partitioned by '{partition_by}'"):
        node.query(
            f"CREATE TEMPORARY TABLE {table_name} {columns_def} ENGINE = {engine} PARTITION BY {partition_by} ORDER BY {order_by}"
        )


@TestStep(Given)
def create_regular_partitioned_table_with_data(
    self,
    table_name: str,
    columns: list[dict] = None,
    order_by: str = "tuple()",
    partition_by: str = None,
    engine="MergeTree",
    node=None,
    number_of_partitions=3,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
    bias=0,
):
    """Create a table with the specified engine."""
    if columns is None:
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if "GraphiteMergeTree" in engine:
        engine = f"GraphiteMergeTree('{config}')"
    elif "VersionedCollapsingMergeTree" in engine:
        engine = f"VersionedCollapsingMergeTree({sign},{version})"
    elif "CollapsingMergeTree" in engine:
        engine = f"CollapsingMergeTree({sign})"

    columns_def = "(" + ",".join([column.full_definition() for column in columns]) + ")"

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        node.query(
            f"CREATE TABLE {table_name} {columns_def} ENGINE = {engine} PARTITION BY {partition_by} ORDER BY {order_by}"
        )

    for i in range(1, number_of_partitions + 1):
        node.query(
            f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT {i+bias}, {i+4+bias}, {i+8+bias}, number+1000, 1 FROM numbers({4})"
        )
        node.query(
            f"INSERT INTO {table_name} (a, b, c, extra, sign) SELECT number+10, number+{i+bias}+14, number+{i+bias}+18, number+1001, 1 FROM numbers({10})"
        )


@TestStep(Given)
def create_empty_regular_partitioned_table(
    self,
    table_name: str,
    columns: list[dict] = None,
    order_by: str = "tuple()",
    partition_by: str = None,
    engine="MergeTree",
    node=None,
    config="graphite_rollup_example",
    sign="sign",
    version="a",
):
    """Create a table with the specified engine."""
    if columns is None:
        columns = [
            Column(name="a", datatype=UInt16()),
            Column(name="b", datatype=UInt16()),
            Column(name="c", datatype=UInt16()),
            Column(name="extra", datatype=UInt64()),
            Column(name="Path", datatype=String()),
            Column(name="Time", datatype=DateTime()),
            Column(name="Value", datatype=Float64()),
            Column(name="Timestamp", datatype=Int64()),
            Column(name="sign", datatype=Int8()),
        ]

    if "GraphiteMergeTree" in engine:
        engine = f"GraphiteMergeTree('{config}')"
    elif "VersionedCollapsingMergeTree" in engine:
        engine = f"VersionedCollapsingMergeTree({sign},{version})"
    elif "CollapsingMergeTree" in engine:
        engine = f"CollapsingMergeTree({sign})"

    columns_def = "(" + ",".join([column.full_definition() for column in columns]) + ")"

    with By(f"creating a table that is partitioned by '{partition_by}'"):
        node.query(
            f"CREATE TABLE {table_name} {columns_def} ENGINE = {engine} PARTITION BY {partition_by} ORDER BY {order_by}"
        )


@TestStep(Then)
def check_partition_was_attached(
    self,
    table,
    node=None,
    sort_column="p",
    partition=1,
    column="i",
    list=False,
):
    """Check that the partition was attached to the table."""
    if node is None:
        node = self.context.node

    with By("I check that there is no partition in detached folder"):
        partition_values = node.query(
            f"SELECT partition_id FROM system.detached_parts WHERE table = '{table}' and partition_id = '{partition}' ORDER BY tuple(*) FORMAT TabSeparated"
        ).output

        assert len(partition_values) == 0

    with And("I check that data from the partition is on the table"):
        data = node.query(
            f"SELECT partition FROM system.parts WHERE partition = '{partition}' and table = '{table}' FORMAT TabSeparated"
        ).output

        assert len(data) > 0


@TestStep(Then)
def check_part_was_attached(
    self,
    table,
    node=None,
    sort_column="p",
    part=None,
    column="i",
    list=False,
):
    """Check that the part was attached to the table."""
    if node is None:
        node = self.context.node

    with By("I check that there is no part in the detached folder"):
        part_value = node.query(
            f"SELECT name FROM system.detached_parts WHERE table = '{table}' and name = '{part}' ORDER BY tuple(*) FORMAT TabSeparated"
        ).output

        assert len(part_value) == 0


@TestStep(Then)
def check_partition_was_attached_from(
    self,
    source_table,
    destination_table,
    node=None,
    partition=1,
):
    """Check that the partition was attached to the table."""
    if node is None:
        node = self.context.node

    with By(
        "I check that data in attached partition is the same in both the source and destination tables"
    ):
        source_data = node.query(
            f"SELECT * FROM {source_table} WHERE p = {partition} ORDER BY p FORMAT TabSeparated"
        ).output
        destination_data = node.query(
            f"SELECT * FROM {destination_table} WHERE p = {partition} ORDER BY p FORMAT TabSeparated"
        ).output

        assert source_data == destination_data


@TestStep(Then)
def check_partition_was_detached(
    self,
    table,
    node=None,
    sort_column="p",
    partition=1,
    column="i",
    list=False,
):
    """Check that the partition was detached from the table."""
    if node is None:
        node = self.context.node

    with By("selecting data from the table"):
        partition_values = node.query(
            f"SELECT partition_id FROM system.detached_parts WHERE table = '{table}' and partition_id = '{partition}' ORDER BY tuple(*) FORMAT TabSeparated"
        ).output

        assert len(partition_values) > 0


@TestStep(Then)
def check_part_was_detached(
    self,
    table,
    number_of_active_parts,
    node=None,
    sort_column="p",
    part=None,
    column="i",
    list=False,
):
    """Check that the part was detached from the table."""
    if node is None:
        node = self.context.node

    with By("selecting data from the table"):
        partition_values = node.query(
            f"SELECT name FROM system.detached_parts WHERE table = '{table}' and name = '{part}' ORDER BY tuple(*) FORMAT TabSeparated"
        ).output

        assert len(partition_values) > 0

    with And("I check that data from the part is not on the table"):
        number_of_active_parts_after_detach = int(
            node.query(
                f"SELECT count(name) FROM system.parts WHERE table = '{table}' and active = 1 FORMAT TabSeparated"
            ).output.strip()
        )

        assert number_of_active_parts_after_detach == number_of_active_parts - 1


@TestStep(Given)
def insert_data(
    self,
    table_name,
    number_of_values=3,
    number_of_partitions=5,
    number_of_parts=1,
    node=None,
    bias=0,
):
    """Insert random UInt64 values into a column and create multiple partitions based on the value of number_of_partitions."""
    if node is None:
        node = self.context.node

    with By("Inserting random values into a column with uint64 datatype"):
        for i in range(1, number_of_partitions + 1):
            for _ in range(1, number_of_parts + 1):
                node.query(
                    f"INSERT INTO {table_name} (a, b, i) SELECT {i%4+bias}, {i}, rand64() FROM numbers({number_of_values})"
                )


@TestStep(Given)
def insert_date_data(
    self,
    table_name,
    number_of_partitions=5,
    node=None,
    bias=0,
):
    """Insert Date data into table."""
    if node is None:
        node = self.context.node

    with By("Inserting values into a column with Date datatype"):
        for i in range(1, number_of_partitions + 1):
            node.query(
                f"INSERT INTO {table_name} (timestamp) VALUES (toDate('2023-12-20')+{i}+{bias})"
            )


@TestStep(Given)
def create_partitions_with_random_uint64(
    self,
    table_name,
    number_of_values=3,
    number_of_partitions=5,
    number_of_parts=1,
    node=None,
    bias=0,
):
    """Insert random UInt64 values into a column and create multiple partitions based on the value of number_of_partitions."""
    if node is None:
        node = self.context.node

    with By("Inserting random values into a column with uint64 datatype"):
        for i in range(1, number_of_partitions + 1):
            for _ in range(1, number_of_parts + 1):
                node.query(
                    f"INSERT INTO {table_name} (p, i) SELECT {i+bias}, rand64() FROM numbers({number_of_values})"
                )


def execute_query(
    sql,
    expected=None,
    exitcode=None,
    message=None,
    no_checks=False,
    snapshot_name=None,
    format="TabSeparatedWithNames",
    node=None,
    path=None,
):
    """Execute SQL query and compare the output to the snapshot."""
    if snapshot_name is None:
        snapshot_name = "/alter/table/attach_partition" + current().name

    if node is None:
        node = current().context.node

    with When("I execute query", description=sql):
        r = node.query(
            sql + " FORMAT " + format,
            exitcode=exitcode,
            message=message,
            no_checks=no_checks,
        )
        if no_checks:
            return r

    if message is None:
        if expected is not None:
            with Then("I check output against expected"):
                assert r.output.strip() == expected, error()
        else:
            with Then("I check output against snapshot"):
                with values() as that:
                    for attempt in retries(timeout=30, delay=5):
                        with attempt:
                            assert that(
                                snapshot(
                                    "\n" + r.output.strip() + "\n",
                                    "tests." + current_cpu(),
                                    name=snapshot_name,
                                    path=path,
                                    encoder=str,
                                    mode=snapshot.CHECK,
                                )
                            ), error()


# MergeTree


@TestStep(Given)
def partitioned_MergeTree(self, table_name, partition_by, nodes=None, node=None):
    create_partitioned_table_with_data(
        table_name=table_name,
        engine="MergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_small_MergeTree(self, table_name, partition_by, nodes=None, node=None):
    create_partitioned_table_with_data(
        table_name=table_name,
        engine="MergeTree",
        partition_by=partition_by,
        node=node,
        small=True,
    )


@TestStep(Given)
def empty_partitioned_MergeTree(self, table_name, partition_by, nodes=None, node=None):
    create_empty_partitioned_table(
        table_name=table_name,
        engine="MergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_ReplicatedMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_data(
        table_name=table_name,
        engine="ReplicatedMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def partitioned_small_ReplicatedMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_data(
        table_name=table_name,
        engine="ReplicatedMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
        small=True,
    )


@TestStep(Given)
def empty_partitioned_ReplicatedMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table(
        table_name=table_name,
        engine="ReplicatedMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def temporary_partitioned_MergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_temporary_partitioned_table_with_data(
        table_name=table_name,
        engine="MergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_temporary_partitioned_MergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_temporary_partitioned_table(
        table_name=table_name,
        engine="MergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_MergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="MergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_MergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="MergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_ReplicatedMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_ReplicatedMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


# ReplacingMergeTree


@TestStep(Given)
def partitioned_ReplacingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_data(
        table_name=table_name,
        engine="ReplacingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_ReplacingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table(
        table_name=table_name,
        engine="ReplacingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_ReplicatedReplacingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_data(
        table_name=table_name,
        engine="ReplicatedReplacingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_ReplicatedReplacingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table(
        table_name=table_name,
        engine="ReplicatedReplacingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def temporary_partitioned_ReplacingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_temporary_partitioned_table_with_data(
        table_name=table_name,
        engine="ReplacingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_temporary_partitioned_ReplacingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_temporary_partitioned_table(
        table_name=table_name,
        engine="ReplacingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_ReplacingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="ReplacingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_ReplacingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="ReplacingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_ReplicatedReplacingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedReplacingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_ReplicatedReplacingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedReplacingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


# AggregatingMergeTree


@TestStep(Given)
def partitioned_AggregatingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_data(
        table_name=table_name,
        engine="AggregatingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_AggregatingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table(
        table_name=table_name,
        engine="AggregatingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_ReplicatedAggregatingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_data(
        table_name=table_name,
        engine="ReplicatedAggregatingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_ReplicatedAggregatingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table(
        table_name=table_name,
        engine="ReplicatedAggregatingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def temporary_partitioned_AggregatingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_temporary_partitioned_table_with_data(
        table_name=table_name,
        engine="AggregatingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_temporary_partitioned_AggregatingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_temporary_partitioned_table(
        table_name=table_name,
        engine="AggregatingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_AggregatingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="AggregatingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_AggregatingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="AggregatingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_ReplicatedAggregatingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedAggregatingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_ReplicatedAggregatingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedAggregatingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


# SummingMergeTree


@TestStep(Given)
def partitioned_SummingMergeTree(self, table_name, partition_by, nodes=None, node=None):
    create_partitioned_table_with_data(
        table_name=table_name,
        engine="SummingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_SummingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table(
        table_name=table_name,
        engine="SummingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_ReplicatedSummingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_data(
        table_name=table_name,
        engine="ReplicatedSummingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_ReplicatedSummingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table(
        table_name=table_name,
        engine="ReplicatedSummingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def temporary_partitioned_SummingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_temporary_partitioned_table_with_data(
        table_name=table_name,
        engine="SummingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_temporary_partitioned_SummingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_temporary_partitioned_table(
        table_name=table_name,
        engine="SummingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_SummingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="SummingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_SummingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="SummingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_ReplicatedSummingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedSummingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_ReplicatedSummingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedSummingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


# CollapsingMergeTree


@TestStep(Given)
def partitioned_CollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_data(
        table_name=table_name,
        engine="CollapsingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_CollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table(
        table_name=table_name,
        engine="CollapsingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_ReplicatedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_data(
        table_name=table_name,
        engine="ReplicatedCollapsingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_ReplicatedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table(
        table_name=table_name,
        engine="ReplicatedCollapsingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def temporary_partitioned_CollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_temporary_partitioned_table_with_data(
        table_name=table_name,
        engine="CollapsingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_temporary_partitioned_CollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_temporary_partitioned_table(
        table_name=table_name,
        engine="CollapsingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_CollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="CollapsingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_CollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="CollapsingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_ReplicatedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedCollapsingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_ReplicatedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedCollapsingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


# VersionedCollapsingMergeTree


@TestStep(Given)
def partitioned_VersionedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_data(
        table_name=table_name,
        engine="VersionedCollapsingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_VersionedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table(
        table_name=table_name,
        engine="VersionedCollapsingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_ReplicatedVersionedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_data(
        table_name=table_name,
        engine="ReplicatedVersionedCollapsingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_ReplicatedVersionedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table(
        table_name=table_name,
        engine="ReplicatedVersionedCollapsingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def temporary_partitioned_VersionedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_temporary_partitioned_table_with_data(
        table_name=table_name,
        engine="VersionedCollapsingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_temporary_partitioned_VersionedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_temporary_partitioned_table(
        table_name=table_name,
        engine="VersionedCollapsingMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_VersionedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="VersionedCollapsingMergeTree",
        partition_by=partition_by,
        node=node,
        version="extra",
    )


@TestStep(Given)
def empty_partitioned_datetime_VersionedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="VersionedCollapsingMergeTree",
        partition_by=partition_by,
        node=node,
        version="extra",
    )


@TestStep(Given)
def partitioned_datetime_ReplicatedVersionedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedVersionedCollapsingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
        version="extra",
    )


@TestStep(Given)
def empty_partitioned_datetime_ReplicatedVersionedCollapsingMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedVersionedCollapsingMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
        version="extra",
    )


# GraphiteMergeTree


@TestStep(Given)
def partitioned_GraphiteMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_data(
        table_name=table_name,
        engine="GraphiteMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_GraphiteMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table(
        table_name=table_name,
        engine="GraphiteMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_ReplicatedGraphiteMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_data(
        table_name=table_name,
        engine="ReplicatedGraphiteMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_ReplicatedGraphiteMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table(
        table_name=table_name,
        engine="ReplicatedGraphiteMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def temporary_partitioned_GraphiteMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_temporary_partitioned_table_with_data(
        table_name=table_name,
        engine="GraphiteMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_temporary_partitioned_GraphiteMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_temporary_partitioned_table(
        table_name=table_name,
        engine="GraphiteMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_GraphiteMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="GraphiteMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_GraphiteMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_table_with_datetime_data(
        table_name=table_name,
        engine="GraphiteMergeTree",
        partition_by=partition_by,
        node=node,
    )


@TestStep(Given)
def partitioned_datetime_ReplicatedGraphiteMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedGraphiteMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )


@TestStep(Given)
def empty_partitioned_datetime_ReplicatedGraphiteMergeTree(
    self, table_name, partition_by, nodes=None, node=None
):
    create_empty_partitioned_replicated_table_with_datetime_data(
        table_name=table_name,
        engine="ReplicatedGraphiteMergeTree",
        partition_by=partition_by,
        nodes=nodes,
        node=node,
    )
