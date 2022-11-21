from testflows.core import current, Given, Finally, TestStep, By
from helpers.common import getuid
from helpers.datatypes import *
from testflows.core import *


class Column:
    def __init__(self, datatype, name=None):
        self.datatype = datatype
        self.name = name if name is not None else self.datatype.name.replace("(","_").replace(")","_").lower()

    def full_definition(self):
        """Return full column definition (name and type) that can be used when defining a table in ClickHouse."""
        return self.name + " " + self.datatype.name

    def max_value(self):
        """Return the maximum value for the column in string format."""
        return str(self.datatype.max_value())

    def min_value(self):
        """Return the minimum value for the column in string format."""
        return str(self.datatype.min_value())

    def rand_value(self, seed=None):
        """Return the random value for the column in string format."""
        return str(self.datatype.rand_value(seed))

    def zero_or_null_value(self):
        """Return the null or zero value for the column in string format."""
        return str(self.datatype.zero_or_null_value())

    def values(self, row_count, cardinality, seed=None):
        """Yield of values that have specified cardinality."""
        values = [self.max_value(), self.min_value(), self.zero_or_null_value()]
        if row_count > 3:
            values += [self.rand_value(seed=seed) for i in range(row_count - 3)]
        values = values * cardinality
        for i in range(row_count):
            yield values[i]


class Tuple(Column):
    def __init__(
        self,
        columns,
    ):
        self.columns = columns
        self.name = "tuple_" + "_".join([column.name for column in self.columns])
        self.type = "Tuple(" + ",".join([column.dataype.name for column in self.columns]) + ")"

    def full_definition(self):
        """Return full column definition (name and type) that can be used when defining a table in ClickHouse."""

        return self.name + " " + self.datatype.name

    def max_value(self):
        """Return the maximum value for the column in string format."""

        return "tuple(" + ",".join([column.max_value() for column in self.columns]) + ")"

    def min_value(self):
        """Return the minimum value for the column in string format."""

        return "tuple(" + ",".join([column.min_value() for column in self.columns]) + ")"

    def rand_value(self, seed=None):
        """Return the random value for the column in string format."""

        return (
            "tuple(" + ",".join([column.rand_value(seed) for column in self.columns]) + ")"
        )

    def zero_or_null_value(self):
        """Return the null or zero value for the column in string format."""

        return (
            "tuple("
            + ",".join([column.zero_or_null_value() for column in self.columns])
            + ")"
        )


class Map(Column):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.name = "map_" + self.key.name + "_" + self.value.name
        self.type = "Map(" + self.key.datatype.name + "," + self.value.datatype.name + ")"

    def full_definition(self):
        """Return full column definition (name and type) that can be used when defining a table in ClickHouse."""

        return self.name + " " + self.type

    def max_value(self):
        """Return the maximum value for the column in string format."""

        return "map(" + self.key.max_value() + "," + self.value.max_value() + ")"

    def min_value(self):
        """Return the minimum value for the column in string format."""

        return "map(" + self.key.min_value() + "," + self.value.min_value() + ")"

    def rand_value(self, seed=None):
        """Return the random value for the column in string format."""

        return (
            "map(" + self.key.rand_value(seed) + "," + self.value.rand_value(seed) + ")"
        )

    def zero_or_null_value(self):
        """Return the null or zero value for the column in string format."""

        return (
            "map("
            + self.key.zero_or_null_value()
            + ","
            + self.value.zero_or_null_value()
            + ")"
        )


class Array(Column):
    def __init__(self, column):
        self.column = column
        self.name = "array_" + self.column.name
        self.type = "Array(" + self.column.type + ")"

    def full_definition(self):
        """Return full column definition (name and type) that can be used when defining a table in ClickHouse."""

        return self.name + " " + self.type

    def max_value(self):
        """Return the maximum value for the column in string format."""

        return "[" + self.column.max_value() + "]"

    def min_value(self):
        """Return the minimum values for the column in string format."""

        return "[" + self.column.min_value() + "]"

    def rand_value(self, seed=None):
        """Return the random values for the column in string format."""

        return "[" + self.column.rand_value(seed) + "]"

    def zero_or_null_value(self):
        """Return the null or zero value for the column in string format."""

        return "[" + self.column.zero_or_null_value() + "]"

def is_numeric(datatype, decimal=True, date=False, datetime=False):
    """Return True if data type is numeric."""
    if datatype.startswith("UInt") or datatype.startswith("Nullable(UInt"):
        return True
    if datatype.startswith("Int") or datatype.startswith("Nullable(Int"):
        return True
    if datatype.startswith("Float") or datatype.startswith("Nullable(Float"):
        return True
    if decimal:
        if datatype.startswith("Decimal") or datatype.startswith("Nullable(Decimal"):
            return True
    if date:
        if datatype.startswith("Date") or datatype.startswith("Nullable(Date"):
            return True
    if datetime:
        if datatype.startswith("DateTime") or datatype.startswith("Nullable(DateTime"):
            return True
    return False

def is_string(datatype):
    """Return True if data type is String."""
    if (
        datatype.startswith("String")
        or datatype.startswith("Nullable(String")
        or datatype.startswith("LowCardinality(String")
    ):
        return True


def is_map(datatype):
    """Return True if data type is Map."""
    if datatype.startswith("Map") or datatype.startswith("Nullable(Map"):
        return True


def is_unsigned_integer(datatype, decimal=True):
    """Return True if data type is unsigned integer."""
    if datatype.startswith("UInt") or datatype.startswith("Nullable(UInt"):
        return True
    return False


def is_integer(datatype, decimal=True):
    """Return True if data type is numeric."""
    if datatype.startswith("UInt") or datatype.startswith("Nullable(UInt"):
        return True
    if datatype.startswith("Int") or datatype.startswith("Nullable(Int"):
        return True
    return False


def generate_low_card_columns(column_list):
    """Generate a list of low cardinality columns based on the input list."""
    return [
        Column(LowCardinality(column.data_type))
        for column in column_list
        if column.data_type.is_low_cardinality
    ]


def generate_nullable_columns(column_list):
    """Generate a list of nullable columns based on the input list."""
    return [Column(Nullable(column.data_type)) for column in column_list]


def generate_array_columns(column_list):
    """Generate a list of array columns based on the input list."""
    return [Array(column=column) for column in column_list]


def generate_tuple_column(column_list):
    """Generate a tuple column containing all the provided column types inside."""
    return Tuple(column_list)


def generate_map_columns(column_list):
    """Generate a list of map columns based on the input list.
    Generates every combination between columns that are valid keys and all other provided columns."""
    map_list = []
    for key in column_list:
        if isinstance(key, Tuple) or isinstance(key, Array) or isinstance(key, Map):
            # The if and elif have to be done seperately because Tuple, Array, Map classes do not have 'data_type'
            continue
        elif key.data_type.is_valid_map_key:
            map_list += [Map(key=key, value=value) for value in column_list]
    return map_list


basic_columns = [Column(data_type) for data_type in basic_data_types]

common_basic_columns = [Column(data_type) for data_type in common_basic_data_types]

low_cardinality_common_basic_columns = generate_low_card_columns(common_basic_columns)

null_common_basic_columns = generate_nullable_columns(common_basic_columns)

common_complex_columns = [
    Array(column=Column(String())),
    Map(
        key=Column(String()),
        value=Column(LowCardinality(Float64())),
    ),
    Tuple([Column(String())]),
]

common_columns = (
    common_basic_columns
    + low_cardinality_common_basic_columns
    + null_common_basic_columns
    + common_complex_columns
)


def generate_all_column_types(include=None, exclude=None):
    """Generate a list of columns with names and ClickHouse types including arrays, maps and tuples."""

    null_columns = generate_nullable_columns(basic_columns)
    low_cardinality_columns = generate_low_card_columns(basic_columns + null_columns)

    array_columns = generate_array_columns(
        basic_columns + null_columns + low_cardinality_columns + common_complex_columns
    )

    map_columns = generate_map_columns(
        basic_columns + null_columns + low_cardinality_columns + common_complex_columns
    )

    tuple_column = [
        generate_tuple_column(
            basic_columns
            + null_columns
            + low_cardinality_columns
            + common_complex_columns
        )
    ]

    all_test_columns = (
        basic_columns
        + map_columns
        + null_columns
        + array_columns
        + low_cardinality_columns
        + tuple_column
    )

    return list(all_test_columns)


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
