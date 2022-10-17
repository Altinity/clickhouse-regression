import uuid
import pyarrow.parquet as pq

from testflows._core.testtype import TestSubType
from testflows.core.name import basename, parentname
from testflows.core import current
from helpers.common import *
from s3.tests.common import *
from testflows.asserts import values, error, snapshot


@TestStep(When)
def insert_test_data(self, name, node=None):
    """Insert data necessarily for Parquet testing into the specified table."""

    xfail("Needs redesign")

    if node is None:
        node = self.context.node

    with By("Inserting some values"):
        node.query(
            f"INSERT INTO {name} VALUES"
            "(0,0,0,0,0,0,0,0,0,0,0,'2022-01-01','2022-01-01 00:00:00','A','B',[0,0,0],(0,0,0,0,0,0,0,0,0,0,0,'2022-01-01','2022-01-01 00:00:00','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}}), {{'a':0, 'b':0}}),"
            "(1,1,1,1,1,1,1,1,1,1,0.5,'2022-01-01','2022-01-01 00:00:00','A','B',[1,1,1],(1,1,1,1,1,1,1,1,1,1,0.5,'2022-01-01','2022-01-01 00:00:00','A','B',[1,1,1],(1,1,1), {{'a':1, 'b':1}}), {{'a':1, 'b':1}}),"
            "(0,-128,0,-32768,0,-2147483648,0,-9223372036854775808,-3.40282347e+38,-1.79769e+308,-0.9999999999999999999999999999999999999,'1970-01-01','1970-01-01 00:00:00','A','B',[0,0,0],(0,-128,0,-32768,0,-2147483648,0,-9223372036854775808,-3.40282347e+38,-1.79769e+308,-0.9999999999999999999999999999999999999,'1970-01-01','1970-01-01 00:00:00','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}}) , {{'a':0, 'b':0}}),"
            "(255,127,65535,32767,4294967295,2147483647,18446744073709551615,9223372036854775807,3.40282347e+38,1.79769e+308,0.9999999999999999999999999999999999999,'2149-06-06','2106-02-07 06:28:15','A','B',[0,0,0],(255,127,65535,32767,4294967295,2147483647,18446744073709551615,9223372036854775807,3.40282347e+38,1.79769e+308,0.9999999999999999999999999999999999999,'2149-06-06','2106-02-07 06:28:15','A','B',[0,0,0],(0,0,0), {{'a':0, 'b':0}}), {{'a':0, 'b':0}}),"
            "(Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,[Null,Null,Null],(Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,[Null,Null,Null],(Null), {{Null:Null}}), {{Null:Null}})"
        )

    return


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
def table(self, engine, name="table0", create="CREATE"):
    """Create or attach a table with specified name and engine."""
    node = current().context.node

    try:
        with By("creating table"):
            node.query(
                f"""
                {create} TABLE {name} {generate_all_column_types()}
                Engine = {engine}
            """
            )
        yield

    finally:
        with Finally("drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestStep(Given)
def create_view(self, view_type, view_name, condition, node=None):
    """Create view."""
    if node is None:
        node = self.context.node

    try:
        with Given("I create view"):
            if view_type == "LIVE":
                node.query(
                    f"CREATE {view_type} VIEW {view_name} as {condition}",
                    settings=[("allow_experimental_live_view", 1)],
                )
            elif view_type == "WINDOW":
                node.query(
                    f"CREATE {view_type} VIEW {view_name} as {condition}",
                    settings=[("allow_experimental_window_view", 1)],
                )
            else:
                node.query(f"CREATE {view_type} VIEW {view_name} as {condition}")

        yield
    finally:
        with Finally("I delete view"):
            node.query(f"DROP VIEW {view_name} SYNC")


def getuid():
    if current().subtype == TestSubType.Example:
        testname = (
            f"{basename(parentname(current().name)).replace(' ', '_').replace(',','')}"
        )
    else:
        testname = f"{basename(current().name).replace(' ', '_').replace(',','')}"
    return testname + "_" + str(uuid.uuid1()).replace("-", "_")


@TestStep(Given)
def upload_parquet_to_aws_s3(self, s3_client):
    """Upload Parquet file to aws s3 container."""

    with By("Uploading a file"):
        s3_client.upload_file(
            "/var/lib/clickhouse/user_files/data.Parquet",
            self.context.uri,
            "/s3_Table/data.Parquet",
        )


@TestStep(Then)
def check_query_output(self, query, expected=None):
    """Check the output of the provided query against either snapshot or provided values."""

    node = current().context.node
    name = basename(current().name)

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
def check_source_file(self, path, expected=None):
    """Check the contents of a Parquet file against either snapshot or provided values."""
    node = current().context.node
    name = basename(current().name)

    with By("reading the file"):
        r = node.command(
            f"python3 -c \"import pyarrow.parquet as pq; import pandas as pd;print(pq.ParquetFile('{path}').schema);print(pd.read_parquet('{path}', engine=pyarrow))\""
        ).output.strip()

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
                        name=name,
                        encoder=str,
                    )
                ), error()

    return


@TestStep(Then)
def check_aws_s3_file(self, s3_client, file, expected):
    """Download specified file from aws s3 and check the contents."""

    with By("Downloading the file"):
        s3_client.download_file(self.context.uri, file, file)

    with Then("I check the file"):
        check_source_file(file=file, expected=expected)


@TestStep(Then)
def check_mysql(self, name, mysql_node, expected):
    """NOT IMPLEMENTED. NEEDS REDESIGN."""

    xfail("Needs redesign.")

    with By("I selecting from table using mysql"):
        msql_out = mysql_node.command(
            f"mysql -D default -u default -e 'SELECT * FROM {name} FORMAT Parquet'"
        ).output
        assert msql_out == expected, error()


def generate_all_column_types():
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
        "fixedstring FixedString(16)",
    ]

    container_columns = [
        "array Array(UInt8)",
        "tuple Tuple(UInt8,Int8,UInt16,Int16,UInt32,Int32,UInt64,Int64,Float32,Float64,Decimal128(38),Date,DateTime,String,FixedString(8),"
        "Array(UInt8),Tuple(UInt8,UInt8,UInt8),Map(String, UInt64))",
        "map Map(String, UInt64)",
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
                low_cardinality_columns.append(
                    "map_low_card_"
                    + type.split(" ", 1)[0]
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
                    + value_type.split(" ", 1)[0]
                    + f" Map({type.split(' ',1)[1]}, {value_type.split(' ',1)[1]})"
                )

    for type in container_columns:
        array_columns.append(
            "array_" + type.split(" ", 1)[0] + f" Array({type.split(' ',1)[1]})"
        )

    null_columns.append(
        "tuple_nullable Tuple("
        "Nullable(UInt8),"
        "Nullable(Int8),"
        "Nullable(UInt16),"
        "Nullable(Int16),"
        "Nullable(UInt32),"
        "Nullable(Int32),"
        "Nullable(UInt64),"
        "Nullable(Int64),"
        "Nullable(Float32),"
        "Nullable(Float64),"
        "Nullable(Decimal128(38)),"
        "Nullable(Date),"
        "Nullable(DateTime),"
        "Nullable(String),"
        "Nullable(FixedString(8)),"
        "Array(Nullable(UInt8)),"
        "Tuple(Nullable(UInt8),"
        "Nullable(UInt8),"
        "Nullable(UInt8)),"
        "Map(String, Nullable(UInt64)))"
    )

    low_cardinality_columns.append(
        "tuple_low_cardinality Tuple("
        "LowCardinality(UInt8),"
        "LowCardinality(Int8),"
        "LowCardinality(UInt16),"
        "LowCardinality(Int16),"
        "LowCardinality(UInt32),"
        "LowCardinality(Int32),"
        "LowCardinality(UInt64),"
        "LowCardinality(Int64),"
        "LowCardinality(Float32),"
        "LowCardinality(Float64),"
        "LowCardinality(Decimal128(38)),"
        "LowCardinality(Date),"
        "LowCardinality(DateTime),"
        "LowCardinality(String),"
        "LowCardinality(FixedString(8)),"
        "Array(LowCardinality(UInt8)),"
        "Tuple(LowCardinality(UInt8),"
        "LowCardinality(UInt8),"
        "LowCardinality(UInt8)),"
        "Map(String, LowCardinality(UInt64)))"
    )

    low_cardinality_columns.append(
        "tuple_low_cardinality_nullable Tuple("
        "LowCardinality(Nullable(UInt8)),"
        "LowCardinality(Nullable(Int8)),"
        "LowCardinality(Nullable(UInt16)),"
        "LowCardinality(Nullable(Int16)),"
        "LowCardinality(Nullable(UInt32)),"
        "LowCardinality(Nullable(Int32)),"
        "LowCardinality(Nullable(UInt64)),"
        "LowCardinality(Nullable(Int64)),"
        "LowCardinality(Nullable(Float32)),"
        "LowCardinality(Nullable(Float64)),"
        "LowCardinality(Nullable(Decimal128(38))),"
        "LowCardinality(Nullable(Date)),"
        "LowCardinality(Nullable(DateTime)),"
        "LowCardinality(Nullable(String)),"
        "LowCardinality(Nullable(FixedString(8))),"
        "Array(LowCardinality(Nullable(UInt8))),"
        "Tuple(LowCardinality(Nullable(UInt8)),"
        "LowCardinality(Nullable(UInt8)),"
        "LowCardinality(Nullable(UInt8))),"
        "Map(String, LowCardinality(Nullable(UInt64))))"
    )

    all_test_columns = (
        basic_columns + container_columns + map_columns + array_columns + null_columns
    )  # + low_cardinality_columns
    all_test_columns = "(" + ",".join(all_test_columns) + ")"

    return all_test_columns
