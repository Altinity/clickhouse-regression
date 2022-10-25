import pyarrow as pa
import pyarrow.parquet as pq

pyarrow_types = {
    "bool": pa.bool_(),
    "uint8": pa.uint8(),
    "int8": pa.int8(),
    "uint16": pa.uint16(),
    "int16": pa.int16(),
    "uint32": pa.uint32(),
    "int32": pa.int32(),
    "uint64": pa.uint64(),
    "int64": pa.int64(),
    "float": pa.float32(),
    "double": pa.float64(),
    "date64": pa.date64(),
    "date32": pa.date32(),
    "string": pa.string(),
    "binary": pa.binary(),
}

data_types_and_values = {
    "bool": [True, False, True],
    "uint8": [0, 255, 128],
    "int8": [-128, 127, 101],
    "uint16": [0, 65535, 32767],
    "int16": [-32768, 32767, 10101],
    "uint32": [0, 4294967295, 101010101],
    "int32": [-2147483648, 2147483647, 10101010],
    "uint64": [0, 18446744073709551615, 1010101010101010],
    "int64": [-9223372036854775808, 9223372036854775807, 1010101010101010],
    "float": [-3.4028235e38, 3.4028235e38, 10101010],
    "double": [-1.7976909999999999e308, 1.7976909999999999e308, 5.6e266],
    "date32": [0, 65535, 10],
    "date64": [0, 1000000, 10],
    "string": [
        "''",
        "'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ!@#$%^&*()_-=+[]\{\}\\|\/?<>,.:;~`'",
        "'hello'",
    ],
    "binary": ["1", "0", "111100111111"],
}


def chunked_array_file():
    arr = pa.array([[("a" * 2**30, 1)]], type=pa.map_(pa.string(), pa.int32()))
    arr = pa.chunked_array([arr, arr])
    tab = pa.table({"arr": arr})
    pq.write_table(tab, "chunked_array_test_file.parquet")


def generate_parquet_test_files():
    """Generate Parquet files used in ClickHouse Parquet format tests.
    Does NOT include TimeStamp and Decimal Parquet types.
    """

    value_dict = {}
    schema = []

    for type, values in data_types_and_values.items():
        value_dict[type] = values
        schema.append((type, pyarrow_types[type]))

        value_dict["list_" + type] = [[value] for value in values]
        schema.append(("list_" + type, pa.list_(pyarrow_types[type])))

        value_dict["list_struct_" + type] = [[(value,)] for value in values]
        schema.append(
            ("list_struct_" + type, pa.list_(pa.struct([("a", pyarrow_types[type])])))
        )

        if type not in ["float", "double"]:
            for inner_key, inner_values in data_types_and_values.items():
                value_dict["map_" + type + "_" + inner_key] = [
                    [(value, inner_value) for inner_value in inner_values]
                    for value in values
                ]
                schema.append(
                    (
                        "map_" + type + "_" + inner_key,
                        pa.map_(pyarrow_types[type], pyarrow_types[inner_key]),
                    )
                )

                value_dict["list_map_" + type + "_" + inner_key] = [
                    [[(value, inner_value)] for inner_value in inner_values]
                    for value in values
                ]
                schema.append(
                    (
                        "list_map_" + type + "_" + inner_key,
                        pa.list_(
                            pa.map_(pyarrow_types[type], pyarrow_types[inner_key])
                        ),
                    )
                )

                value_dict["map_" + type + "_list_" + inner_key] = [
                    [(value, [inner_value]) for inner_value in inner_values]
                    for value in values
                ]
                schema.append(
                    (
                        "map_" + type + "_list_" + inner_key,
                        pa.map_(
                            pyarrow_types[type], pa.list_(pyarrow_types[inner_key])
                        ),
                    )
                )

                value_dict["map_" + type + "_struct_" + inner_key] = [
                    [(value, (inner_value,)) for inner_value in inner_values]
                    for value in values
                ]
                schema.append(
                    (
                        "map_" + type + "_struct_" + inner_key,
                        pa.map_(
                            pyarrow_types[type],
                            pa.struct([("a", pyarrow_types[inner_key])]),
                        ),
                    )
                )

    value_dict["struct"] = [
        tuple([value[i] for value in data_types_and_values.values()]) for i in range(3)
    ]
    schema.append(
        (
            "struct",
            pa.struct([(f"{value}", value) for value in data_types_and_values.keys()]),
        )
    )

    table = pa.table(value_dict, schema=pa.schema(schema))

    for compression in ["NONE", "SNAPPY", "GZIP", "BROTLI", "LZ4", "ZSTD"]:
        pq.write_table(
            table,
            f"C:\\Users\\myros\\Altinity\\data_{compression}.Parquet",
            compression=compression,
        )

    return
