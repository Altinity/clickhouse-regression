from testflows.core import current, Given, Finally, TestStep, By
from helpers.common import getuid
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

    def full_definition(self):
        """Return full column definition (name and type) that can be used when defining a table in ClickHouse."""
        return self.name + " " + self.datatype.name

    def values(self, row_count, cardinality, seed=None):
        """Yield of values that have specified cardinality."""
        values = [
            self.datatype.max_value(),
            self.datatype.min_value(),
            self.datatype.zero_or_null_value(),
        ]

        if row_count > 3:
            values += [
                self.datatype.rand_value(seed=seed) for i in range(row_count - 3)
            ]

        values = values * cardinality
        for i in range(row_count):
            yield str(values[i])


def is_numeric(datatype, decimal=True, date=False, datetime=False):
    """Return True if data type is numeric."""
    if decimal:
        if isinstance(datatype, Decimal):
            return True
    if date:
        if isinstance(datatype, Date):
            return True
    if datetime:
        if isinstance(datatype, DateTime):
            return True
    return datatype.is_numeric


def is_string(datatype):
    """Return True if data type is String."""
    return isinstance(datatype, String)


def is_map(datatype):
    """Return True if data type is Map."""
    return isinstance(datatype, Map)


def is_unsigned_integer(datatype, decimal=True):
    """Return True if data type is unsigned integer."""
    if decimal:
        if isinstance(datatype, Decimal):
            return False
    return isinstance(datatype, UInt)


def is_integer(datatype, decimal=True):
    """Return True if data type is integer."""
    if decimal:
        if isinstance(datatype, Decimal):
            return False
    return isinstance(datatype, Int)


def generate_low_card_datatypes(datatype_list):
    """Generate a list of low cardinality datatypes based on the input list."""
    return [
        LowCardinality(datatype)
        for datatype in datatype_list
        if datatype.supports_low_cardinality
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
    Generates every combination between datatypes that are valid keys and all other provided columns."""
    map_list = []
    for key in datatype_list:
        if key.is_valid_map_key:
            map_list += [Map(key=key, value=value) for value in datatype_list]
    return map_list


low_cardinality_common_basic_datatypes = generate_low_card_datatypes(
    common_basic_datatypes
)

null_common_basic_datatypes = generate_nullable_datatypes(common_basic_datatypes)

common_complex_datatypes = [
    Array(String()),
    Map(
        key=String(),
        value=LowCardinality(Float64()),
    ),
    Tuple([String()]),
]

common_datatypes = (
    common_basic_datatypes
    + low_cardinality_common_basic_datatypes
    + null_common_basic_datatypes
    + common_complex_datatypes
)

common_columns = [Column(datatype) for datatype in common_datatypes]


def generate_all_column_types(include=None, exclude=None):
    """Generate a list of datatypes with names and ClickHouse types including arrays, maps and tuples."""

    null_datatypes = generate_nullable_datatypes(basic_datatypes)
    low_cardinality_datatypes = generate_low_card_datatypes(
        basic_datatypes + null_datatypes
    )

    array_datatypes = generate_array_datatypes(
        basic_datatypes
        + null_datatypes
        + low_cardinality_datatypes
        + common_complex_datatypes
    )

    map_datatypes = generate_map_datatypes(
        basic_datatypes
        + null_datatypes
        + low_cardinality_datatypes
        + common_complex_datatypes
    )

    tuple_datatype = [
        generate_tuple_datatype(
            basic_datatypes
            + null_datatypes
            + low_cardinality_datatypes
            + common_complex_datatypes
        )
    ]

    all_test_datatypes = (
        basic_datatypes
        + map_datatypes
        + null_datatypes
        + array_datatypes
        + low_cardinality_datatypes
        + tuple_datatype
    )

    return [Column(datatype) for datatype in all_test_datatypes]


class Table:
    def __init__(self, name, columns, engine):
        self.name = name
        self.columns = columns
        self.engine = engine

    def insert_test_data(
        self, row_count=10, cardinality=2, node=None, query_settings=None, seed=None
    ):
        """Insert data necessarily for Parquet testing into the specified table."""

        if node is None:
            node = current().context.node

        name = self.name
        columns = self.columns

        total_values = []

        for row in range(row_count):
            total_values.append(
                "("
                + ",".join(
                    [
                        next(
                            column.values(
                                row_count=row_count, cardinality=cardinality, seed=seed
                            )
                        )
                        for column in columns
                    ]
                )
                + ")"
            )

        return node.query(
            f"INSERT INTO {name} VALUES {','.join(total_values)}",
            settings=query_settings,
        )


@TestStep(Given)
def create_table(
    self, engine, columns, name=None, create="CREATE", path=None, drop_sync=False
):
    """Create or attach a table with specified name and engine."""
    node = current().context.node

    if name is None:
        name = f"table_{getuid()}"

    columns_def = "(" + ",".join([column.full_definition() for column in columns]) + ")"

    try:
        if create == "CREATE":
            with By(f"creating table {name}"):
                node.query(
                    f"""
                    CREATE TABLE {name} {columns_def}
                    Engine = {engine}
                """,
                    settings=[("allow_suspicious_low_cardinality_types", 1)],
                )
        elif create == "ATTACH":
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
