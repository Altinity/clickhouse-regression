import uuid
import pyarrow.parquet as pq

from testflows._core.testtype import TestSubType
from testflows.core.name import basename, parentname
from testflows.core import current
from helpers.common import *
from s3.tests.common import *
from testflows.asserts import values, error, snapshot


@TestStep(Given)
def start_minio(
    self,
    uri="localhost:9001",
    access_key="minio",
    secret_key="minio123",
    timeout=30,
    secure=False,
):
    minio_client = Minio(
        uri, access_key=access_key, secret_key=secret_key, secure=secure
    )
    start = time.time()
    while time.time() - start < timeout:
        try:
            buckets_to_delete = minio_client.list_buckets()

            for bucket in buckets_to_delete:
                objects = minio_client.list_objects(bucket.name, recursive=True)
                object_names = [o.object_name for o in objects]
                for name in object_names:
                    minio_client.remove_object(bucket.name, name)

            buckets = ["root", "root2"]
            self.context.cluster.minio_bucket = "root"
            self.context.cluster.minio_bucket_2 = "root2"

            for bucket in buckets:
                if minio_client.bucket_exists(bucket):
                    objects = minio_client.list_objects(bucket, recursive=True)
                    object_names = [o.object_name for o in objects]
                    for name in object_names:
                        minio_client.remove_object(bucket, name)
                    minio_client.remove_bucket(bucket)
                minio_client.make_bucket(bucket)

            return minio_client
        except Exception as ex:
            time.sleep(1)

    raise Exception("Can't wait Minio to start")


@TestStep(Given)
def allow_experimental_map_type(self):
    """Set allow_experimental_map_type = 1"""
    setting = ("allow_experimental_map_type", 1)
    default_query_settings = None

    try:
        with By("adding allow_experimental_map_type to the default query settings"):
            default_query_settings = getsattr(
                current().context, "default_query_settings", []
            )
            default_query_settings.append(setting)
        yield
    finally:
        with Finally(
            "I remove allow_experimental_map_type from the default query settings"
        ):
            if default_query_settings:
                try:
                    default_query_settings.pop(default_query_settings.index(setting))
                except ValueError:
                    pass


@TestStep(Given)
def table(self, engine, name="table0", create="CREATE", path=None, table_def=None):
    """Create or attach a table with specified name and engine."""
    node = current().context.node

    if table_def is None:
        table_def = "(" + ",".join(generate_all_column_types()) + ")"  #

    try:
        with By("creating table"):
            if create == "CREATE":
                node.query(
                    f"""
                    CREATE TABLE {name} {table_def}
                    Engine = {engine}
                """,
                    settings=[("allow_suspicious_low_cardinality_types", 1)],
                )
            elif create == "ATTACH":

                node.query(
                    f"""
                    ATTACH TABLE {name} FROM '{path}' {table_def}
                    Engine = {engine}
                    """
                )
        yield

    finally:
        with Finally("drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


def getuid():
    if current().subtype == TestSubType.Example:
        testname = (
            f"{basename(parentname(current().name)).replace(' ', '_').replace(',','')}"
        )
    else:
        testname = f"{basename(current().name).replace(' ', '_').replace(',','')}"
    return testname + "_" + str(uuid.uuid1()).replace("-", "_")


@TestStep(Given)
def upload_file_to_s3(self, file_src, file_dest):
    """Upload specified file to s3 bucket."""

    if self.context.storage == "aws_s3":
        with By("Uploading a file"):
            self.context.client.upload_file(
                file_src,
                self.context.uri,
                file_dest,
            )

    elif self.context.storage == "minio":
        xfail("Not implemented for minio")

    return


@TestStep(Then)
def check_query_output(self, query, expected=None):
    """Check the output of the provided query against either snapshot or provided values."""

    node = current().context.node
    name = basename(parentname(current().name))

    with By("executing query", description=query):
        r = node.query(query).output.strip()

    if expected:
        with Then("result should match the expected", description=expected):
            assert r == expected, error()

    else:
        with Then("I check output against snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        "\n" + r + "\n",
                        "parquet_file",
                        name=name,
                        encoder=str,
                    )
                ), error()


@TestStep(Then)
def check_source_file(self, path, compression=None, expected=None, snap_name=None):
    """Check the contents of a Parquet file against either snapshot or provided values."""
    node = current().context.node
    table_name = "table_" + getuid()

    if snap_name is None:
        snap_name = basename(current().name)

    with By("creating a table"):
        table(name=table_name, engine="Memory")
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '{path}' {'COMPRESSION '+ compression if compression and compression != 'NONE' else ''} FORMAT Parquet"
        )

    with By("reading the file"):
        r = node.query(f"SELECT * FROM {table_name}").output.strip()

    if expected:
        with Then(f"result should match the expected values", description=expected):
            assert r == expected, error()

    else:
        with Then("I check output against snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        "\n" + r + "\n",
                        "parquet_file",
                        name=snap_name,
                        encoder=str,
                    )
                ), error()

    return


@TestStep(Then)
def check_source_file_on_s3(self, file, expected=None, compression_type=None):
    """Download specified file from aws s3 and check the contents."""

    if self.context.storage == "aws_s3":
        with By("Downloading the file"):
            self.context.client.download_file(
                self.context.aws_s3_bucket, f"data/parquet/{file}", "data.Parquet"
            )
            x = self.context.cluster.command(
                None, "docker ps | grep clickhouse1 | cut -d ' ' -f 1 | head -n 1"
            ).output
            self.context.cluster.command(
                None,
                f"docker cp data.Parquet {x}:/data.Parquet",
            )

    elif self.context.storage == "minio":
        xfail("not implemented yet")

    with Then("I check the file"):
        check_source_file(
            path="/data.Parquet", expected=expected, compression=compression_type
        )


@TestStep(Then)
def check_mysql(self, name, mysql_node, expected):
    """NOT IMPLEMENTED. NEEDS REDESIGN."""

    xfail("Needs redesign.")

    with By("I selecting from table using mysql"):
        msql_out = mysql_node.command(
            f"mysql -D default -u default -e 'SELECT * FROM {name} FORMAT Parquet'"
        ).output
        assert msql_out == expected, error()


def generate_all_column_types(include=None, exclude=None):
    """Generate a list of every type of column necessary for Parquet tests."""

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

    if include:
        basic_columns = [
            column for column in basic_columns if column.split(" ")[1] in include
        ]

    elif exclude:
        basic_columns = [
            column for column in basic_columns if column.split(" ")[1] not in exclude
        ]

    map_key_types = [
        column
        for column in basic_columns
        if column
        not in ["float32 Float32", "float64 Float64", "decimal Decimal128(38)"]
    ]

    container_columns = [
        f"array Array({basic_columns[0].split(' ')[1]})",
        "tuple Tuple("
        + ",".join([column.split(" ")[1] for column in basic_columns])
        + ","
        f"Array({basic_columns[0].split(' ')[1]}),Tuple({basic_columns[0].split(' ')[1]}),Map({map_key_types[0].split(' ')[1]}, {basic_columns[0].split(' ')[1]}))",
        f"map Map({map_key_types[0].split(' ')[1]}, {basic_columns[0].split(' ')[1]})",
    ]

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
        + container_columns
        + map_columns
        + null_columns
        + array_columns
        + low_cardinality_columns
    )

    return all_test_columns


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


@TestStep(When)
def insert_test_data(self, name, columns=None, node=None):
    """Insert data necessarily for Parquet testing into the specified table."""

    if node is None:
        node = self.context.node

    if columns is None:
        columns = generate_all_column_types()

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
                    zero_and_nulls.append("{" + data_types_and_values[key][0] + ":[0]}")

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
                zero_and_nulls.append("{" + data_types_and_values[key][0] + ":{0:0}}")

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

                zero_and_nulls.append("(" + ",".join(tuple_zeros) + ",[0],(0),{0:0})")

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

    with By("Inserting values into the specified destination"):
        node.query(
            f"INSERT INTO {name} VALUES {'('+','.join(min_values)+'),('+','.join(max_values)+'),('+','.join(misc_values)+'),('+','.join(zero_and_nulls) + ')'}",
            settings=[("engine_file_allow_create_multiple_files", 1)],
        )

    return
