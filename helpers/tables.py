import random
import hashlib

from testflows.core import current, Given, Finally, TestStep, By
from helpers.common import getuid, check_clickhouse_version
from helpers.datatypes import *
from testflows.core import *


class Column:
    def __init__(self, datatype, name=None):
        self.datatype = datatype
        self.name = (
            name
            if name is not None
            else self.datatype.name.replace("(", "_")
            .replace(")", "_")
            .replace(",", "_")
            .lower()
        )
        seed = int(hashlib.sha1(self.name.encode("utf-8")).hexdigest()[:10], 16)
        self.random = random.Random(seed)

    def __eq__(self, o):
        return isinstance(o, Column) and o.name == self.name

    def __lt__(self, o):
        return isinstance(o, Column) and o.name < self.name

    def full_definition(self):
        """Return full column definition (name and type) that can be used when defining a table in ClickHouse."""
        return self.name + " " + self.datatype.name

    def values(self, row_count, cardinality, random=None, shuffle_values=False):
        """Yield of values that have specified cardinality."""
        if random is None:
            random = self.random

        values = [
            self.datatype.max_value(),
            self.datatype.min_value(),
            self.datatype.zero_or_null_value(),
        ]

        if row_count > 3:
            values += [self.datatype.rand_value(random) for i in range(row_count - 3)]

        values = values * cardinality
        if shuffle_values:
            random.shuffle(values)

        for i in range(row_count * cardinality):
            yield str(values[i])


def is_numeric(
    datatype,
    decimal=True,
    date=False,
    date32=False,
    datetime=False,
    datetime64=False,
    extended_precision=True,
):
    """Return True if data type is numeric."""
    datatype = unwrap(datatype)

    if not extended_precision:
        if datatype.is_extended_precision:
            return False

    if isinstance(datatype, Decimal):
        return decimal

    if isinstance(datatype, Date32):
        return date32

    if isinstance(datatype, DateTime64):
        return datetime64

    if isinstance(datatype, DateTime):
        return datetime

    if isinstance(datatype, Date):
        return date

    return datatype.is_numeric


def is_string(datatype):
    """Return True if data type is String."""
    return isinstance(unwrap(datatype), String)


def is_map(datatype):
    """Return True if data type is Map."""
    return isinstance(unwrap(datatype), Map)


def is_array(datatype):
    """Return True if data type is Array."""
    return isinstance(unwrap(datatype), Array)


def is_nullable(datatype):
    """Return True if data type is Nullable."""
    return isinstance(datatype, Nullable)


def is_low_cardinality(datatype):
    """Return True if data type is LowCardinality."""
    return isinstance(datatype, LowCardinality)


def is_unsigned_integer(
    datatype,
    decimal=False,
    extended_precision=True,
    date=False,
    date32=False,
    datetime=False,
    datetime64=False,
):
    """Return True if data type is unsigned integer."""
    datatype = unwrap(datatype)

    if isinstance(datatype, Decimal):
        return decimal

    if isinstance(datatype, Date32):
        return date32

    if isinstance(datatype, DateTime64):
        return datetime64

    if isinstance(datatype, DateTime):
        return datetime

    if isinstance(datatype, Date):
        return date

    if not extended_precision:
        if datatype.is_extended_precision:
            return False

    return isinstance(datatype, UInt)


def is_integer(
    datatype,
    decimal=False,
    extended_precision=True,
    date=False,
    date32=False,
    datetime=False,
    datetime64=False,
):
    """Return True if data type is integer."""
    datatype = unwrap(datatype)

    if isinstance(datatype, Decimal):
        return decimal

    if isinstance(datatype, Date32):
        return date32

    if isinstance(datatype, DateTime64):
        return datetime64

    if isinstance(datatype, DateTime):
        return datetime

    if isinstance(datatype, Date):
        return date

    if not extended_precision:
        if datatype.is_extended_precision:
            return False

    return isinstance(datatype, Int)


def generate_low_card_datatypes(datatype_list):
    """Generate a list of low cardinality datatypes based on the input list."""
    return [
        LowCardinality(datatype)
        for datatype in datatype_list
        if unwrap(datatype).supports_low_cardinality
        and (
            not isinstance(datatype, Nullable)
            if check_clickhouse_version("<22.4")(current())
            else True
        )
    ]


def generate_nullable_datatypes(datatype_list):
    """Generate a list of nullable datatypes based on the input list."""
    return [Nullable(datatype) for datatype in datatype_list]


def generate_array_datatypes(datatype_list):
    """Generate a list of array datatypes based on the input list."""
    return [Array(datatype) for datatype in datatype_list]


def generate_tuple_datatype(datatype_list):
    """Generate a tuple datatype containing all the provided datatypes inside."""
    return Tuple([datatype for datatype in datatype_list])


def generate_map_datatypes(datatype_list):
    """Generate a list of map datatypes based on the input list.
    Generates every combination between datatypes that are valid keys and all other provided columns.
    """
    map_list = []
    for key in datatype_list:
        if key.is_valid_map_key:
            map_list += [Map(key=key, value=value) for value in datatype_list]
    return map_list


def low_cardinality_common_basic_datatypes():
    return generate_low_card_datatypes(common_basic_datatypes())


def null_common_basic_datatypes():
    return generate_nullable_datatypes(common_basic_datatypes())


def common_complex_datatypes():
    return [
        Array(String()),
        Map(
            key=String(),
            value=LowCardinality(Float64()),
        ),
        Tuple([String()]),
    ]


def common_datatypes():
    return (
        common_basic_datatypes()
        + low_cardinality_common_basic_datatypes()
        + null_common_basic_datatypes()
        + common_complex_datatypes()
    )


def common_columns():
    return [Column(datatype) for datatype in common_datatypes()]


def generate_all_basic_numeric_column_types():
    """Generate a list of datatypes with names and ClickHouse types including arrays, maps and tuples."""
    types = [
        UInt8(),
        UInt16(),
        UInt32(),
        UInt64(),
        # UInt128(),
        Int8(),
        Int16(),
        Int32(),
        Int64(),
        # Int128(),
        Float32(),
        Float64(),
        Decimal128(scale=38),
    ]

    return [Column(datatype) for datatype in types]


def generate_all_column_types(include=None, exclude=None):
    """Generate a list of datatypes with names and ClickHouse types including arrays, maps and tuples."""

    if exclude is None:
        exclude = []

    _basic_datatypes = include if include else basic_datatypes()

    null_datatypes = generate_nullable_datatypes(_basic_datatypes)
    low_cardinality_datatypes = generate_low_card_datatypes(
        _basic_datatypes + null_datatypes
    )

    array_datatypes = generate_array_datatypes(
        _basic_datatypes
        + null_datatypes
        + low_cardinality_datatypes
        + common_complex_datatypes()
    )

    map_datatypes = generate_map_datatypes(
        _basic_datatypes
        + null_datatypes
        + low_cardinality_datatypes
        + common_complex_datatypes()
    )

    tuple_datatype = [
        generate_tuple_datatype(
            _basic_datatypes
            + null_datatypes
            + low_cardinality_datatypes
            + common_complex_datatypes()
        )
    ]

    all_test_datatypes = (
        _basic_datatypes
        + map_datatypes
        + null_datatypes
        + array_datatypes
        + low_cardinality_datatypes
        + tuple_datatype
    )

    return [
        Column(datatype) for datatype in all_test_datatypes if datatype not in exclude
    ]


def generate_all_map_column_types():
    """Generate map columns with every possible datatype."""
    _basic_datatypes = basic_datatypes()

    null_datatypes = generate_nullable_datatypes(_basic_datatypes)
    low_cardinality_datatypes = generate_low_card_datatypes(
        _basic_datatypes + null_datatypes
    )

    map_datatypes = generate_map_datatypes(
        _basic_datatypes
        + null_datatypes
        + low_cardinality_datatypes
        + common_complex_datatypes()
    )

    return [Column(datatype) for datatype in map_datatypes]


class Table:
    def __init__(self, name, columns, engine):
        self.name = name
        self.columns = columns
        self.engine = engine

    def insert_test_data(
        self,
        row_count=10,
        cardinality=1,
        node=None,
        query_settings=None,
        random=None,
        get_values=False,
        shuffle_values=False,
    ):
        """Insert data that is necessary for Parquet testing into the specified table.

        :param row_count: the number of rows to insert into the table, default: `10`
        :param cardinality: the number of times to repeat the same values in the table, default: `1`
        :param node: the node object to execute the query, if not provided, it will use the current context node.
        :param query_settings: list of settings to be used for the query, default: `None`
        :param random: an optional random number generator object to control the data generation, default: `None`
        :param get_values: if True, returns the generated values in addition to the query execution result, default: `False`
        :param shuffle_values: if True, shuffles the values before inserting them into the table, default: `False`
        """
        if node is None:
            node = current().context.node

        name = self.name
        columns = self.columns
        columns_values = [
            column.values(
                row_count=row_count,
                cardinality=cardinality,
                random=random,
                shuffle_values=shuffle_values,
            )
            for column in columns
        ]

        values = []

        for row in range(row_count * cardinality):
            values.append(
                "("
                + ",".join([next(column_values) for column_values in columns_values])
                + ")"
            )

        result = node.query(
            f"INSERT INTO {name} VALUES {','.join(values)}",
            settings=query_settings,
        )

        if get_values:
            return result, values
        return result


@TestStep(Given)
def create_table(
    self,
    engine,
    columns,
    name=None,
    path=None,
    drop_sync=False,
    order_by=None,
    partition_by=None,
    primary_key=None,
    comment=None,
    as_select=None,
    settings=None,
    query_settings=None,
    empty=None,
    if_not_exists=False,
    node=None,
    cluster=None,
    order_by_all_columns=False,
):
    """Create a table with specified name and engine."""
    if settings is None:
        settings = [("allow_suspicious_low_cardinality_types", 1)]

    if name is None:
        name = f"table_{getuid()}"

    if node is None:
        node = current().context.node

    columns_def = "(" + ",".join([column.full_definition() for column in columns]) + ")"

    if order_by_all_columns:
        non_nullable_columns = [
            column for column in columns if "Nullable" not in column.datatype.name
        ]
        order_by = (
            "(" + ",".join([column.name for column in non_nullable_columns]) + ")"
        )

    if if_not_exists:
        if_not_exists = "IF NOT EXISTS "
    else:
        if_not_exists = ""

    if cluster is not None:
        on_cluster = f" ON CLUSTER {cluster}"
    else:
        on_cluster = ""

    try:
        with By(f"creating table {name}"):
            query = (
                f"CREATE TABLE {if_not_exists}{name}{on_cluster} {columns_def}\n"
                f"ENGINE = {engine}"
            )
            if primary_key is not None:
                query += f"\nPRIMARY KEY {primary_key}"

            if partition_by is not None:
                query += f"\nPARTITION BY {partition_by}"

            if order_by is not None:
                query += f"\nORDER BY {order_by}"

            if comment is not None:
                query += f"\nCOMMENT '{comment}'"

            if empty is not None:
                query += f"\nEMPTY AS {empty}"

            if as_select is not None:
                query += f"\nAS SELECT {as_select}"
            if query_settings is not None:
                query += f"\nSETTINGS {query_settings}"

            node.query(
                query,
                settings=settings,
            )

            yield Table(name, columns, engine)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(
                f"DROP TABLE IF EXISTS {name}{on_cluster} {' SYNC' if drop_sync else ''}"
            )


@TestStep(Given)
def create_temporary_table(
    self,
    engine,
    columns,
    name=None,
    path=None,
    drop_sync=False,
    order_by=None,
    partition_by=None,
    comment=None,
    as_select=None,
    settings=None,
    empty=None,
    node=None,
):
    """Create a table with specified name and engine."""
    if settings is None:
        settings = [("allow_suspicious_low_cardinality_types", 1)]

    if name is None:
        name = f"table_{getuid()}"

    if node is None:
        node = current().context.node

    columns_def = "(" + ",".join([column.full_definition() for column in columns]) + ")"

    try:
        with By(f"creating table {name}"):
            query = (
                f"CREATE TEMPORARY TABLE {name} {columns_def}\n" f"ENGINE = {engine}"
            )

            if partition_by is not None:
                query += f"\nPARTITION BY {partition_by}"

            if order_by is not None:
                query += f"\nORDER BY {order_by}"

            if comment is not None:
                query += f"\nCOMMENT '{comment}'"

            if empty is not None:
                query += f"\nEMPTY AS {empty}"

            if as_select is not None:
                query += f"\nAS SELECT {as_select}"

            node.query(
                query,
                settings=settings,
            )

            yield Table(name, columns, engine)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}{' SYNC' if drop_sync else ''}")


@TestStep(Given)
def create_partitioned_table_with_compact_and_wide_parts(
    self,
    table_name,
    min_rows_for_wide_part=10,
    min_bytes_for_wide_part=100,
    engine="MergeTree",
):
    """Create a partitioned table that has specific settings in order
    to get both wide and compact parts."""
    create_table(
        name=table_name,
        engine=engine,
        partition_by="p",
        order_by="tuple()",
        columns=[
            Column(name="p", datatype=UInt8()),
            Column(name="i", datatype=UInt64()),
        ],
        query_settings=f"min_rows_for_wide_part={min_rows_for_wide_part}, min_bytes_for_wide_part={min_bytes_for_wide_part}",
    )


@TestStep(Given)
def create_table_partitioned_by_column(
    self,
    table_name,
    engine="MergeTree",
    partition_by="p",
    columns=None,
    query_settings=None,
    order_by="tuple()",
    node=None,
):
    """Create a table that is partitioned by a specific column."""

    if node is None:
        node = self.context.node

    if columns is None:
        columns = [
            Column(name="p", datatype=UInt16()),
            Column(name="i", datatype=UInt64()),
            Column(name="extra", datatype=UInt8()),
        ]

    with By(f"creating a table that is partitioned by a '{partition_by}' column "):
        create_table(
            name=table_name,
            engine=engine,
            partition_by=partition_by,
            order_by=order_by,
            columns=columns,
            query_settings=query_settings,
            if_not_exists=True,
            node=node,
        )


@TestStep(Given)
def attach_table(self, engine, columns, name=None, path=None, drop_sync=False):
    """Attach a table with specified name and engine."""
    if name is None:
        name = f"table_{getuid()}"

    node = current().context.node

    columns_def = "(" + ",".join([column.full_definition() for column in columns]) + ")"
    try:
        with By(f"attaching table {name}"):
            node.query(
                f"""
                    ATTACH TABLE {name} FROM '{path}' {columns_def}
                    Engine = {engine}
                    """
            )

            yield Table(name, columns, engine)

    finally:
        with Finally(f"drop the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name}{' SYNC' if drop_sync else ''}")
