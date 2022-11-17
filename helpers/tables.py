from testflows.core import current, Given, Finally, TestStep, By

from helpers.common import getuid

# all basic data types and sample values
data_types_and_values = {
    "UInt8": ["0", "255", "128"],
    "Int8": ["-128", "127", "101"],
    "UInt16": ["0", "65535", "32767"],
    "Int16": ["-32768", "32767", "10101"],
    "UInt32": ["0", "4294967295", "101010101"],
    "Int32": ["-2147483648", "2147483647", "10101010"],
    "UInt64": ["0", "18446744073709551615", "1010101010101010"],
    "Int64": ["-9223372036854775808", "9223372036854775807", "1010101010101010"],
    "Float32": ["-3.4028235e+38", "3.4028235e+38", "10101010"],
    "Float64": ["-1.7976909999999999e308", "1.7976909999999999e308", "5.6e266"],
    "Decimal128(38)": [
        "-0.9999999999999999999999999999999999999",
        "0.9999999999999999999999999999999999999",
        "0.1010101",
    ],
    "Date": ["'1970-01-01'", "'2149-06-06'", "'2022-10-17'"],
    "DateTime": [
        "'1970-01-01 00:00:00'",
        "'2106-02-07 06:28:15'",
        "'2022-10-17 13:46:00'",
    ],
    "String": [
        "''",
        "'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ!@#$%^&*()_-=+[]\{\}\\|\/?<>,.:;~`'",
        "'⡌⠁⠧⠑ ⠼⠁⠒  ⡍⠜⠇⠑⠹⠰⠎ ⡣⠕⠌'",
    ],
    "FixedString(85)": [
        "''",
        "'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ!@#$%^&*()_-=+[]\{\}\\|\/?<>,.:;~`'",
        "'⡌⠁⠧⠑ ⠼⠁⠒  ⡍⠜⠇⠑⠹⠰⠎ ⡣⠕⠌'",
    ],
}


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


basic_columns = [
    "uint8 UInt8",
    "int8 Int8",
    "uint16 UInt16",
    "int16 Int16",
    "uint32 UInt32",
    "int32 Int32",
    "uint64 UInt64",
    "int64 Int64",
    "float32 Float32",
    "float64 Float64",
    "decimal Decimal128(38)",
    "date Date",
    "datetime DateTime",
    "string String",
    "fixedstring FixedString(85)",
]

common_basic_columns = [
    "string String",
    "fixedstring FixedString(85)",
    "date Date",
    "datetime DateTime",
    "uint64 UInt64",
    "int64 Int64",
    "float64 Float64",
    "float32 Float32",
    "decimal Decimal128(38)",
]

common_complex_columns = [
    "array_string Array(String)",
    "map_low_card_string_low_card_float64 Map(LowCardinality(String),LowCardinality(Float64))",
]

low_cardinality_common_basic_columns = []
null_common_basic_columns = []

for type in common_basic_columns:
    if type.split(" ", 1)[1] not in ["Decimal128(38)"]:
        low_cardinality_common_basic_columns.append(
            "low_card_"
            + type.split(" ", 1)[0]
            + f" LowCardinality({type.split(' ',1)[1]})"
        )

for type in common_basic_columns:
    null_common_basic_columns.append(
        "nullable_" + type.split(" ", 1)[0] + f" Nullable({type.split(' ',1)[1]})"
    )

common_columns = (
    common_basic_columns
    + low_cardinality_common_basic_columns
    + null_common_basic_columns
    + common_complex_columns
)

map_key_types = [
    column
    for column in basic_columns
    if column not in ["float32 Float32", "float64 Float64", "decimal Decimal128(38)"]
]

container_columns = [
    f"array Array({basic_columns[0].split(' ')[1]})",
    "tuple Tuple(" + ",".join([column.split(" ")[1] for column in basic_columns]) + ","
    f"Array({basic_columns[0].split(' ')[1]}),Tuple({basic_columns[0].split(' ')[1]}),Map({map_key_types[0].split(' ')[1]}, {basic_columns[0].split(' ')[1]}))",
    f"map Map({map_key_types[0].split(' ')[1]}, {basic_columns[0].split(' ')[1]})",
]


def generate_all_column_types():
    """Generate a list of every type of column necessary for Parquet tests."""
    array_columns = []
    map_columns = []
    null_columns = []
    low_cardinality_columns = []

    for type in basic_columns:
        array_columns.append(
            "array_" + type.split(" ", 1)[0] + f" Array({type.split(' ',1)[1]})"
        )
        null_columns.append(
            "nullable_" + type.split(" ", 1)[0] + f" Nullable({type.split(' ',1)[1]})"
        )
        null_columns.append(
            "array_nullable_"
            + type.split(" ", 1)[0]
            + f" Array(Nullable({type.split(' ',1)[1]}))"
        )

        if type != "decimal Decimal128(38)":
            low_cardinality_columns.append(
                "low_card_"
                + type.split(" ", 1)[0]
                + f" LowCardinality({type.split(' ',1)[1]})"
            )
            low_cardinality_columns.append(
                "array_low_card_"
                + type.split(" ", 1)[0]
                + f" Array(LowCardinality({type.split(' ',1)[1]}))"
            )
            low_cardinality_columns.append(
                "array_low_card_nullable_"
                + type.split(" ", 1)[0]
                + f" Array(LowCardinality(Nullable({type.split(' ',1)[1]})))"
            )

        if type not in ["float32 Float32", "float64 Float64", "decimal Decimal128(38)"]:
            for value_type in basic_columns:
                map_columns.append(
                    "map_"
                    + type.split(" ", 1)[0]
                    + "_"
                    + value_type.split(" ", 1)[0]
                    + f" Map({type.split(' ',1)[1]}, {value_type.split(' ',1)[1]})"
                )
                null_columns.append(
                    "map_"
                    + type.split(" ", 1)[0]
                    + "_nullable_"
                    + value_type.split(" ", 1)[0]
                    + f" Map({type.split(' ',1)[1]}, Nullable({value_type.split(' ',1)[1]}))"
                )
                if type in ["string String", "fixedstring FixedString(85)"]:
                    low_cardinality_columns.append(
                        "map_low_card_"
                        + type.split(" ", 1)[0]
                        + "_"
                        + value_type.split(" ", 1)[0]
                        + f" Map(LowCardinality({type.split(' ',1)[1]}), {value_type.split(' ',1)[1]})"
                    )
                    low_cardinality_columns.append(
                        "map_low_card_"
                        + type.split(" ", 1)[0]
                        + "_nullable_"
                        + value_type.split(" ", 1)[0]
                        + f" Map(LowCardinality({type.split(' ',1)[1]}), Nullable({value_type.split(' ',1)[1]}))"
                    )

                    if value_type != "decimal Decimal128(38)":
                        low_cardinality_columns.append(
                            "map_low_card_"
                            + type.split(" ", 1)[0]
                            + "_low_card_"
                            + value_type.split(" ", 1)[0]
                            + f" Map(LowCardinality({type.split(' ',1)[1]}), LowCardinality({value_type.split(' ',1)[1]}))"
                        )
                        low_cardinality_columns.append(
                            "map_low_card_"
                            + type.split(" ", 1)[0]
                            + "_low_card_nullable_"
                            + value_type.split(" ", 1)[0]
                            + f" Map(LowCardinality({type.split(' ',1)[1]}), LowCardinality(Nullable({value_type.split(' ',1)[1]})))"
                        )

            for value_type in container_columns:
                map_columns.append(
                    "map_"
                    + type.split(" ", 1)[0]
                    + "_"
                    + value_type.split(" ", 1)[0]
                    + f" Map({type.split(' ',1)[1]}, {value_type.split(' ',1)[1]})"
                )

    for type in container_columns:
        array_columns.append(
            "array_" + type.split(" ", 1)[0] + f" Array({type.split(' ',1)[1]})"
        )

    null_columns.append(
        "tuple_nullable Tuple("
        + ",".join(
            ["Nullable(" + column.split(" ")[1] + ")" for column in basic_columns]
        )
        + ","
        f"Array(Nullable({basic_columns[0].split(' ')[1]})),"
        f"Tuple(Nullable({basic_columns[0].split(' ')[1]})),"
        f"Map({map_key_types[0].split(' ')[1]}, Nullable({basic_columns[0].split(' ')[1]})))"
    )

    # low_cardinality_columns.append(
    #     "tuple_low_cardinality Tuple("
    #     + ",".join(
    #         [
    #             "LowCardinality(" + column.split(" ")[1] + ")"
    #             for column in basic_columns
    #             if column != "decimal Decimal128(38)"
    #         ]
    #     )
    #     + ")"
    #     + ","
    #     f"Array(LowCardinality({basic_columns[0].split(' ')[1]})),"
    #     f"Tuple(LowCardinality({basic_columns[0].split(' ')[1]})),"
    #     f"Map({map_key_types[0].split(' ')[1]}, LowCardinality({basic_columns[0].split(' ')[1]})))"
    # )

    # low_cardinality_columns.append(
    #     "tuple_low_cardinality_nullable Tuple("
    #     + ",".join(
    #         [
    #             "LowCardinality(Nullable(" + column.split(" ")[1] + "))"
    #             for column in basic_columns
    #             if column != "decimal Decimal128(38)"
    #         ]
    #     )
    #     + ","
    #     f"Array(LowCardinality(Nullable({basic_columns[0].split(' ')[1]}))),"
    #     f"Tuple(LowCardinality(Nullable({basic_columns[0].split(' ')[1]}))),"
    #     f"Map({map_key_types[0].split(' ')[1]}, LowCardinality(Nullable({basic_columns[0].split(' ')[1]}))))"
    # )

    all_test_columns = (
        basic_columns
        # FIXME: introduces duplicates
        # + container_columns
        + map_columns
        + null_columns
        + array_columns
        + low_cardinality_columns
    )

    return list(set(all_test_columns))


class Table:
    def __init__(self, name, columns, engine):
        self.name = name
        self.columns = columns
        self.engine = engine

    def insert_test_data(self, node=None, query_settings=None):
        """Insert data necessarily for Parquet testing into the specified table."""

        if node is None:
            node = current().context.node

        name = self.name
        columns = self.columns

        min_values = []
        max_values = []
        misc_values = []
        zero_and_nulls = []

        for column in columns:

            if "LowCardinality(" in column:
                column = ",".join(
                    [
                        i.replace("LowCardinality(", "", 1).replace(")", "", 1)
                        if "LowCardinality(" in i
                        else i
                        for i in column.split(",")
                    ]
                )

            type = column.split(" ", 1)[1]

            if type.startswith("Array"):

                type = type[6:-1]

                if type.startswith("Array"):
                    min_values.append(f"[[{data_types_and_values['UInt8'][0]}]]")
                    max_values.append(f"[[{data_types_and_values['UInt8'][1]}]]")
                    misc_values.append(f"[[{data_types_and_values['UInt8'][2]}]]")

                    if type[6:-1].startswith("Nullable"):
                        zero_and_nulls.append("[[Null]]")
                    else:
                        zero_and_nulls.append("[[0]]")

                elif type.startswith("Tuple"):
                    min_values.append(
                        "[("
                        + ",".join(
                            [
                                data_types_and_values[key][0]
                                for key in data_types_and_values.keys()
                            ]
                        )
                        + f",[{data_types_and_values['UInt8'][0]}],({data_types_and_values['UInt8'][0]}),"
                        + "{"
                        + data_types_and_values["UInt8"][0]
                        + ":"
                        + data_types_and_values["UInt8"][0]
                        + "})]"
                    )
                    max_values.append(
                        "[("
                        + ",".join(
                            [
                                data_types_and_values[key][1]
                                for key in data_types_and_values.keys()
                            ]
                        )
                        + f",[{data_types_and_values['UInt8'][1]}],({data_types_and_values['UInt8'][1]}),"
                        + "{"
                        + data_types_and_values["UInt8"][1]
                        + ":"
                        + data_types_and_values["UInt8"][1]
                        + "})]"
                    )
                    misc_values.append(
                        "[("
                        + ",".join(
                            [
                                data_types_and_values[key][2]
                                for key in data_types_and_values.keys()
                            ]
                        )
                        + f",[{data_types_and_values['UInt8'][2]}],({data_types_and_values['UInt8'][2]}),"
                        + "{"
                        + data_types_and_values["UInt8"][2]
                        + ":"
                        + data_types_and_values["UInt8"][2]
                        + "})]"
                    )

                    if type[6:-1].startswith("Nullable"):
                        zero_and_nulls.append(
                            "[("
                            + ",".join(["Null" for key in data_types_and_values.keys()])
                            + ",[Null],(Null),{0:Null})]"
                        )
                    else:
                        tuple_zeros = []
                        for key in data_types_and_values.keys():
                            if key in ["String", "FixedString(85)"]:
                                tuple_zeros.append(("'0'"))
                            elif key in ["Date", "DateTime"]:
                                tuple_zeros.append(data_types_and_values[key][0])
                            else:
                                tuple_zeros.append("0")

                        zero_and_nulls.append(
                            "[(" + ",".join(tuple_zeros) + ",[0],(0),{0:0})]"
                        )

                elif type.startswith("Map"):
                    min_values.append(
                        "[{"
                        + data_types_and_values["UInt8"][0]
                        + ":"
                        + data_types_and_values["UInt8"][0]
                        + "}]"
                    )
                    max_values.append(
                        "[{"
                        + data_types_and_values["UInt8"][1]
                        + ":"
                        + data_types_and_values["UInt8"][1]
                        + "}]"
                    )
                    misc_values.append(
                        "[{"
                        + data_types_and_values["UInt8"][2]
                        + ":"
                        + data_types_and_values["UInt8"][2]
                        + "}]"
                    )
                    zero_and_nulls.append("[{0:0}]")

                elif type.startswith("Nullable"):
                    type = type[9:-1]
                    min_values.append(f"[{data_types_and_values[type][0]}]")
                    max_values.append(f"[{data_types_and_values[type][1]}]")
                    misc_values.append(f"[{data_types_and_values[type][2]}]")
                    zero_and_nulls.append("[Null]")

                else:
                    min_values.append(f"[{data_types_and_values[type][0]}]")
                    max_values.append(f"[{data_types_and_values[type][1]}]")
                    misc_values.append(f"[{data_types_and_values[type][2]}]")

                    if type in ["String", "FixedString(85)"]:
                        zero_and_nulls.append("['0']")
                    elif type in ["Date", "DateTime"]:
                        zero_and_nulls.append(f"[{data_types_and_values[type][0]}]")
                    else:
                        zero_and_nulls.append("[0]")

            elif type.startswith("Map"):
                key, value = type[4:-1].split(", ", 1)
                if value.startswith("Array"):
                    min_values.append(
                        "{"
                        + data_types_and_values[key][0]
                        + ":["
                        + data_types_and_values["UInt8"][0]
                        + "]}"
                    )
                    max_values.append(
                        "{"
                        + data_types_and_values[key][1]
                        + ":["
                        + data_types_and_values["UInt8"][1]
                        + "]}"
                    )
                    misc_values.append(
                        "{"
                        + data_types_and_values[key][2]
                        + ":["
                        + data_types_and_values["UInt8"][2]
                        + "]}"
                    )

                    if value.startswith("Array(Nullable"):
                        zero_and_nulls.append(
                            "{" + data_types_and_values[key][0] + ":[Null]}"
                        )
                    else:
                        zero_and_nulls.append(
                            "{" + data_types_and_values[key][0] + ":[0]}"
                        )

                elif value.startswith("Tuple"):
                    min_values.append(
                        "{"
                        + data_types_and_values[key][0]
                        + ":("
                        + ",".join(
                            [
                                data_types_and_values[key][0]
                                for key in data_types_and_values.keys()
                            ]
                        )
                        + f",[{data_types_and_values['UInt8'][0]}],({data_types_and_values['UInt8'][0]}),"
                        + "{"
                        + data_types_and_values["UInt8"][0]
                        + ":"
                        + data_types_and_values["UInt8"][0]
                        + "})}"
                    )
                    max_values.append(
                        "{"
                        + data_types_and_values[key][1]
                        + ":("
                        + ",".join(
                            [
                                data_types_and_values[key][0]
                                for key in data_types_and_values.keys()
                            ]
                        )
                        + f",[{data_types_and_values['UInt8'][1]}],({data_types_and_values['UInt8'][1]}),"
                        + "{"
                        + data_types_and_values["UInt8"][1]
                        + ":"
                        + data_types_and_values["UInt8"][1]
                        + "})}"
                    )
                    misc_values.append(
                        "{"
                        + data_types_and_values[key][2]
                        + ":("
                        + ",".join(
                            [
                                data_types_and_values[key][2]
                                for key in data_types_and_values.keys()
                            ]
                        )
                        + f",[{data_types_and_values['UInt8'][2]}],({data_types_and_values['UInt8'][2]}),"
                        + "{"
                        + data_types_and_values["UInt8"][2]
                        + ":"
                        + data_types_and_values["UInt8"][2]
                        + "})}"
                    )

                    tuple_zeros = []
                    for tuple_key in data_types_and_values.keys():
                        if tuple_key in ["String", "FixedString(85)"]:
                            tuple_zeros.append(("'0'"))
                        elif tuple_key in ["Date", "DateTime"]:
                            tuple_zeros.append(data_types_and_values[tuple_key][0])
                        else:
                            tuple_zeros.append("0")

                    zero_and_nulls.append(
                        "{"
                        + data_types_and_values[key][0]
                        + ":("
                        + ",".join(tuple_zeros)
                        + ",[0],(0),{0:0})}"
                    )

                elif value.startswith("Map"):
                    min_values.append(
                        "{"
                        + data_types_and_values[key][0]
                        + ":{"
                        + data_types_and_values["UInt8"][0]
                        + ":"
                        + data_types_and_values["UInt8"][0]
                        + "}}"
                    )
                    max_values.append(
                        "{"
                        + data_types_and_values[key][1]
                        + ":{"
                        + data_types_and_values["UInt8"][1]
                        + ":"
                        + data_types_and_values["UInt8"][1]
                        + "}}"
                    )
                    misc_values.append(
                        "{"
                        + data_types_and_values[key][2]
                        + ":{"
                        + data_types_and_values["UInt8"][2]
                        + ":"
                        + data_types_and_values["UInt8"][2]
                        + "}}"
                    )
                    zero_and_nulls.append(
                        "{" + data_types_and_values[key][0] + ":{0:0}}"
                    )

                else:
                    if value.startswith("Nullable"):
                        zero_and_nulls.append(
                            "{" + data_types_and_values[key][0] + ":Null}"
                        )
                    else:
                        if value in ["String", "FixedString(85)"]:
                            zero_and_nulls.append(
                                "{" + data_types_and_values[key][0] + ":'0'}"
                            )
                        elif value in ["Date", "DateTime"]:
                            zero_and_nulls.append(
                                "{"
                                + data_types_and_values[key][0]
                                + ":"
                                + data_types_and_values[value][0]
                                + "}"
                            )
                        else:
                            zero_and_nulls.append(
                                "{" + data_types_and_values[key][0] + ":0}"
                            )

                    value = value[9:-1] if value.startswith("Nullable") else value

                    min_values.append(
                        "{"
                        + data_types_and_values[key][0]
                        + ":"
                        + data_types_and_values[value][0]
                        + "}"
                    )
                    max_values.append(
                        "{"
                        + data_types_and_values[key][1]
                        + ":"
                        + data_types_and_values[value][1]
                        + "}"
                    )
                    misc_values.append(
                        "{"
                        + data_types_and_values[key][2]
                        + ":"
                        + data_types_and_values[value][2]
                        + "}"
                    )

            elif type.startswith("Tuple"):
                min_values.append(
                    "("
                    + ",".join(
                        [
                            data_types_and_values[key][0]
                            for key in data_types_and_values.keys()
                        ]
                    )
                    + f",[{data_types_and_values['UInt8'][0]}],({data_types_and_values['UInt8'][0]}),"
                    + "{"
                    + data_types_and_values["UInt8"][0]
                    + ":"
                    + data_types_and_values["UInt8"][0]
                    + "})"
                )
                max_values.append(
                    "("
                    + ",".join(
                        [
                            data_types_and_values[key][1]
                            for key in data_types_and_values.keys()
                        ]
                    )
                    + f",[{data_types_and_values['UInt8'][1]}],({data_types_and_values['UInt8'][1]}),"
                    + "{"
                    + data_types_and_values["UInt8"][1]
                    + ":"
                    + data_types_and_values["UInt8"][1]
                    + "})"
                )
                misc_values.append(
                    "("
                    + ",".join(
                        [
                            data_types_and_values[key][2]
                            for key in data_types_and_values.keys()
                        ]
                    )
                    + f",[{data_types_and_values['UInt8'][2]}],({data_types_and_values['UInt8'][2]}),"
                    + "{"
                    + data_types_and_values["UInt8"][2]
                    + ":"
                    + data_types_and_values["UInt8"][2]
                    + "})"
                )

                if type[6:-1].startswith("Nullable"):
                    zero_and_nulls.append(
                        "("
                        + ",".join(["Null" for key in data_types_and_values.keys()])
                        + ",[Null],(Null),{0:Null})"
                    )
                else:
                    tuple_zeros = []
                    for key in data_types_and_values.keys():
                        if key in ["String", "FixedString(85)"]:
                            tuple_zeros.append(("'0'"))
                        elif key in ["Date", "DateTime"]:
                            tuple_zeros.append(data_types_and_values[key][0])
                        else:
                            tuple_zeros.append("0")

                    zero_and_nulls.append(
                        "(" + ",".join(tuple_zeros) + ",[0],(0),{0:0})"
                    )

            else:
                if type.startswith("Nullable"):
                    zero_and_nulls.append("Null")
                else:
                    if type in ["String", "FixedString(85)"]:
                        zero_and_nulls.append(("'0'"))
                    elif type in ["Date", "DateTime"]:
                        zero_and_nulls.append(data_types_and_values[type][0])
                    else:
                        zero_and_nulls.append("0")

                type = type[9:-1] if type.startswith("Nullable") else type

                min_values.append(data_types_and_values[type][0])
                max_values.append(data_types_and_values[type][1])
                misc_values.append(data_types_and_values[type][2])

        return node.query(
            f"INSERT INTO {name} VALUES {'('+','.join(min_values)+'),('+','.join(max_values)+'),('+','.join(misc_values)+'),('+','.join(zero_and_nulls) + ')'}",
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

    columns_def = "(" + ",".join(columns) + ")"  #

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
