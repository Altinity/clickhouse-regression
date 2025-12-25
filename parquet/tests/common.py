import json
import uuid
import datetime
import pyarrow.parquet as pq

from testflows._core.testtype import TestSubType
from testflows.asserts import values, error, snapshot
from testflows.core.name import basename, parentname
from testflows.core import current
from helpers.common import *
from helpers.datatypes import *
from helpers.tables import *
from s3.tests.common import *


def generate_non_random_values(data_type, physical_data_type=None, only_true=False):
    """Generate a fixed value for the given data type (no randomness)."""
    data_type = data_type.upper()
    physical_type = None
    length = None
    if physical_data_type is not None:
        physical_type = physical_data_type["physicalType"]
        if physical_type == "FIXED_LEN_BYTE_ARRAY":
            length = physical_data_type["length"]

    if data_type == "INT32":
        return 42
    elif data_type == "INT64":
        return 1234567890123456789
    elif data_type == "BOOLEAN":
        # If we need to respect only_true, return True in any case
        return True if only_true else True  # Always True (you can change if needed)
    elif data_type == "FLOAT":
        return 3.14
    elif data_type == "DOUBLE":
        return 2.71828
    elif data_type == "BINARY":
        return "fixedbinary"
    elif data_type == "FIXED_LEN_BYTE_ARRAY":
        return "a" * int(length)

    elif data_type in ("UTF8", "STRING", "ENUM"):
        return "fixedstring"
    elif data_type == "DECIMAL":
        if physical_type == "BINARY":
            return "1234"
        else:
            return 1234
    elif data_type == "DATE":
        # ISO format date
        return "2020-01-01"
    elif data_type in ("TIME_MILLIS", "TIME_MICROS"):
        return "12:34:56.789"
    elif data_type in ("TIMESTAMP_MILLIS", "TIMESTAMP_MICROS"):
        return "2020-01-01 12:34:56"
    elif data_type == "NONE":
        return None
    elif data_type == "MAP":
        return {
            "key_value": [
                {"key": "map_key", "value": "map_value"},
                {"key": "map_key2", "value": "map_value2"},
                {"key": "map_key3", "value": "map_value3"},
            ]
        }
    elif data_type == "LIST":
        return [1, 2, 3, 4, 5]
    elif data_type == "MAP_KEY_VALUE":
        return {
            "key_value": [
                {"key": "mapkv_key", "value": "mapkv_value"},
                {"key": "mapkv_key2", "value": "mapkv_value2"},
                {"key": "mapkv_key3", "value": "mapkv_value3"},
            ]
        }
    elif data_type == "TIME":
        return "12:34:56.789"
    elif data_type == "INTEGER":
        return 100
    elif data_type == "JSON":
        return json.dumps({"key": "fixed_json"})
    elif data_type == "BSON":
        return json.dumps({"key": "fixed_bson"})  # Basic simulation
    elif data_type == "UUID":
        return "550e8400e29b41d4a716446655440000"
    elif data_type == "INTERVAL":
        # Placeholder for an interval representation
        return 42
    elif data_type == "FLOAT16":
        return 12.34
    elif data_type == "UINT8":
        return 255
    elif data_type == "UINT16":
        return 65535
    elif data_type == "UINT32":
        return 4294967295
    elif data_type == "UINT64":
        return 18446744073709551615
    elif data_type == "INT8":
        return 127
    elif data_type == "INT16":
        return 32767
    return None


def generate_random_value(data_type, only_true=False):
    """Generate a random value for the given data type."""
    data_type = data_type.upper()

    if data_type == "INT32":
        return random.randint(-2147483648, 2147483647)
    elif data_type == "INT64":
        return random.randint(-9223372036854775808, 9223372036854775807)
    elif data_type == "BOOLEAN":
        if not only_true:
            return random.choice([True, False])
        else:
            return True
    elif data_type == "FLOAT":
        return random.uniform(-1e38, 1e38)
    elif data_type == "DOUBLE":
        return random.uniform(-1e308, 1e308)
    elif data_type == "BINARY":
        return "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(3, 10))
        )
    elif data_type.startswith("FIXED_LEN_BYTE_ARRAY"):
        match = re.search(r"\((\d+)\)", data_type)
        if match:
            length = max(1, int(match.group(1)))
        else:
            length = random.randint(3, 10)

        return "".join(
            random.choices(
                "abcdefghijklmnopqrstuvwxyz",
                k=length,
            )
        )
    elif data_type == "UTF8" or data_type == "STRING" or data_type == "ENUM":
        return "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(3, 10))
        )
    elif data_type == "DECIMAL":
        return random.randint(0, 42912)
    elif data_type == "DATE":
        return str(
            datetime.date.today() - datetime.timedelta(days=random.randint(0, 3650))
        )
    elif data_type == "TIME_MILLIS" or data_type == "TIME_MICROS":
        return str(datetime.datetime.now().time())
    elif data_type == "TIMESTAMP_MILLIS" or data_type == "TIMESTAMP_MICROS":
        return str(datetime.datetime.now())
    elif data_type == "NONE":
        return None
    elif data_type == "MAP":
        return {
            "key_value": [
                {
                    "key": generate_random_value("UTF8"),
                    "value": generate_random_value("UTF8"),
                }
            ]
            for _ in range(3)
        }
    elif data_type == "LIST":
        return [generate_random_value("INT32") for _ in range(5)]
    elif data_type == "MAP_KEY_VALUE":
        return {
            "key_value": [
                {
                    "key": generate_random_value("UTF8"),
                    "value": generate_random_value("UTF8"),
                }
            ]
            for _ in range(3)
        }
    elif data_type == "TIME":
        return str(datetime.datetime.now().time())
    elif data_type == "INTEGER":
        return random.randint(-1000, 1000)
    elif data_type == "JSON":
        return json.dumps({"key": generate_random_value("UTF8")})
    elif data_type == "BSON":
        return json.dumps({"key": generate_random_value("UTF8")})  # BSON simulation
    elif data_type == "UUID":
        return str(uuid.uuid4())
    elif data_type == "INTERVAL":
        return random.randint(1, 1000)  # Placeholder for interval representation
    elif data_type == "FLOAT16":
        return round(random.uniform(-1e4, 1e4), 4)
    elif data_type == "UINT8":
        return random.randint(0, 255)
    elif data_type == "UINT16":
        return random.randint(0, 65535)
    elif data_type == "UINT32":
        return random.randint(0, 4294967295)
    elif data_type == "UINT64":
        return random.randint(0, 18446744073709551615)
    elif data_type == "INT8":
        return random.randint(-128, 127)
    elif data_type == "INT16":
        return random.randint(-32768, 32767)
    return None


def generate_values(data_type, count, only_true=False):
    """Generate a list of random values for the given data type."""
    return [
        generate_random_value(data_type=data_type, only_true=only_true)
        for _ in range(count)
    ]


def generate_unique_value(data_type, existing_values, max_attempts=3000):
    """
    Generate a value for the given data type that is not in existing_values.
    For complex non-hashable structures (like dict), we do a linear membership check.
    """
    for _ in range(max_attempts):
        val = generate_random_value(data_type)

        if val not in existing_values:
            return val

    raise ValueError(
        f"Could not find a unique value for data_type {data_type} after {max_attempts} attempts."
    )


class CreateParquetStructure:
    """Class for generating a JSON file that is required to generate a Parquet file with the parquetify tool."""

    def __init__(self):
        self.parquet_data = {
            "fileName": "",
            "options": {
                "writerVersion": "1.0",
                "compression": "SNAPPY",
                "rowGroupSize": 134217728,
                "pageSize": 1048576,
                "encodings": ["PLAIN"],
                "bloomFilter": "none",
            },
            "schema": [],
        }

    def set_file_name(self, file_name):
        """Set name that will be used for generated Parquet file."""
        self.parquet_data["fileName"] = file_name

    def set_options(
        self,
        writer_version="1.0",
        compression="SNAPPY",
        row_group_size=134217728,
        page_size=1048576,
        encodings=None,
        bloom_filter="none",
    ):
        """Set options for the Parquet file."""
        options = {
            "writerVersion": writer_version,
            "compression": compression,
            "rowGroupSize": row_group_size,
            "pageSize": page_size,
            "encodings": encodings if encodings is not None else ["PLAIN"],
            "bloomFilter": bloom_filter,
        }
        self.parquet_data["options"] = options

    def add_column(
        self,
        name,
        schema_type,
        physical_type=None,
        logical_type=None,
        precision=None,
        scale=None,
        length=None,
        fields=None,
        key_type=None,
        value_type=None,
        data=None,
    ):
        """Add a column to the Parquet file with the defined schema."""
        column = {
            "name": name,
            "schemaType": schema_type,
            "physicalType": physical_type,
        }

        if physical_type:
            column["physicalType"] = physical_type
        if logical_type:
            column["logicalType"] = logical_type
        if precision:
            column["precision"] = precision
        if scale:
            column["scale"] = scale
        if length:
            column["length"] = length
        if fields:
            column["fields"] = fields
        if key_type:
            column["keyType"] = key_type
        if value_type:
            column["valueType"] = value_type
        if data:
            column["data"] = data

        self.parquet_data["schema"].append(column)

    def generate_json(self, output_file_path):
        """Generate a JSON file with the defined schema, options and file name."""
        with open(output_file_path, "w") as json_file:
            json.dump(self.parquet_data, json_file, indent=2)


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
                    if "warehouse" in bucket.name:
                        continue
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
            self.context.s3_client = minio_client
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
def table(
    self, engine, name=None, create="CREATE", path=None, table_def=None, node=None
):
    """Create or attach a table with specified name and engine."""
    if node is None:
        node = current().context.node

    if name is None:
        name = f"table_{getuid()}"

    if table_def is None:
        table_def = "(" + ",".join(generate_all_column_types()) + ")"

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
            f"{basename(parentname(current().name)).replace(' ', '_').replace(',', '')}"
        )
    else:
        testname = f"{basename(current().name).replace(' ', '_').replace(',', '')}"
    return testname + "_" + str(uuid.uuid1()).replace("-", "_")


@TestStep(Given)
def copy_file_to_host(self, src_node, src_path, host_filename):
    """Copy a file from the src node to the host and remove after the test."""
    try:
        with By("getting the name container name of the source node"):
            x = self.context.cluster.command(
                None, f"docker ps | grep {src_node} | cut -d ' ' -f 1 | head -n 1"
            ).output

        with And("copying the file from the node to the host"):
            self.context.cluster.command(None, f"mkdir /tmp/test_files", no_checks=True)
            self.context.cluster.command(
                None, f"docker cp {x}:{src_path} /tmp/test_files/{host_filename}"
            )

        yield

    finally:
        with Finally("remove the file from the host"):
            self.context.cluster.command(None, f"rm /tmp/test_files/{host_filename}")


@TestStep(Given)
def upload_file_to_s3(self, file_src, file_dest):
    """Upload specified file to s3 bucket."""

    if self.context.storage == "aws_s3":
        with By("Uploading a file"):
            self.context.s3_client.upload_file(
                file_src,
                self.context.aws_s3_bucket,
                file_dest,
            )

    elif self.context.storage == "minio":
        with By("Uploading a file"):
            self.context.s3_client.fput_object(
                self.context.cluster.minio_bucket, file_dest, file_src
            )

    return


@TestCheck
def check_source_file(self, path, compression=None, reference_table_name=None):
    """Check the contents of a Parquet file against either snapshot or provided values."""
    node = current().context.node
    table_name = "table_" + getuid()

    with By("creating a table"):
        table = create_table(
            name=table_name,
            engine="Memory",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    if check_clickhouse_version("<23.3")(self):
        with And(
            "I select and save the data from the reference table and from the newly created table"
        ):
            if check_clickhouse_version(">23.9")(self):
                order = "ALL"
            else:
                order = "tuple(*)"

            table1 = node.query(
                f"SELECT * FROM {reference_table_name} ORDER BY {order} FORMAT TabSeparated",
                use_file=True,
                file_output=f"output_{getuid()}",
            )
            table2 = node.query(
                f"SELECT * FROM {table_name} ORDER BY {order} FORMAT TabSeparated",
                use_file=True,
                file_output=f"output_{getuid()}",
            )

        with Check(
            "I check that the in the reference table and newly created table is the same"
        ):
            assert table1.output.strip() == table2.output.strip(), error()

    else:
        with And("inserting data from the specified file"):
            node.query(
                f"INSERT INTO {table_name} FROM INFILE '{path}' {'COMPRESSION ' + compression if compression and compression != 'NONE' else ''} FORMAT Parquet"
            )

        if check_clickhouse_version(">23.9")(self):
            order = "ALL"
        else:
            order = "tuple(*)"

        with Pool(3) as executor:
            sql = "SELECT {column_name}, toTypeName({column_name}) FROM {table_name} ORDER BY {order}"
            for column in table.columns:
                if reference_table_name:
                    r = current().context.node.query(
                        sql.format(
                            column_name=column.name,
                            table_name=reference_table_name,
                            order=order,
                        )
                        + " FORMAT JSONEachRow",
                        exitcode=0,
                    )

                Check(
                    test=execute_query_step,
                    name=f"{column.datatype.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=sql.format(
                        column_name=column.name, table_name=table.name, order=order
                    ),
                    expected=r.output.strip() if reference_table_name else None,
                )
            join()

    return


@TestCheck
def check_source_file_on_s3(
    self, file, compression_type=None, reference_table_name=None
):
    """Download specified file from aws s3 and check the contents."""

    parquet_file = "data_" + getuid() + ".Parquet"

    if self.context.storage == "aws_s3":
        with By("Downloading the file"):
            self.context.s3_client.download_file(
                self.context.aws_s3_bucket,
                f"data/parquet/{file}",
                f"/tmp/test_files/{parquet_file}",
            )

    elif self.context.storage == "minio":
        with By("Downloading the file"):
            self.context.s3_client.fget_object(
                self.context.cluster.minio_bucket,
                "data/parquet/" + file,
                f"/tmp/test_files/{parquet_file}",
            )

    with By("copying the file to the docker node"):
        x = self.context.cluster.command(
            None, "docker ps | grep clickhouse1 | cut -d ' ' -f 1 | head -n 1"
        ).output
        self.context.cluster.command(
            None,
            f"docker cp /tmp/test_files/{parquet_file} {x}:/{parquet_file}",
        )

    with Check("I check the file"):
        check_source_file(
            path=f"/{parquet_file}",
            compression=compression_type,
            reference_table_name=reference_table_name,
        )


def parquet_test_columns():
    return [
        Boolean(),
        UInt8(),
        Int8(),
        UInt16(),
        Int16(),
        UInt32(),
        Int32(),
        UInt64(),
        Int64(),
        Float32(),
        Float64(),
        Date(),
        Decimal128(38),
        DateTime(),
        String(),
        FixedString(51),
    ]


def mysql_test_columns():
    datatypes = [
        UInt8(),
        Int8(),
        UInt16(),
        Int16(),
        UInt32(),
        Int32(),
        UInt64(),
        Int64(),
        Float32(),
        Float64(),
        Date(),
        DateTime(),
        String(),
        FixedString(51),
    ]
    return [
        Column(datatype)
        for datatype in datatypes + generate_nullable_datatypes(datatypes)
    ]


def postgresql_test_columns():
    datatypes = [
        Int16(),
        Int32(),
        Int64(),
        Float32(),
        Float64(),
        Date(),
        DateTime(),
        String(),
    ]
    nullable_datatypes = generate_nullable_datatypes(datatypes)
    array_datatypes = generate_array_datatypes(datatypes + nullable_datatypes)
    return [
        Column(datatype)
        for datatype in datatypes + nullable_datatypes + array_datatypes
    ]


def postgresql_conversion(column):
    """Convert ClickHouse datatypes to PostgreSQL datatypes."""
    array = isinstance(column.datatype, Array)
    datatype = unwrap(column.datatype.datatype) if array else unwrap(column.datatype)
    suffix = "[]" if array else ""
    suffix += "" if isinstance(column.datatype, Nullable) else " NOT NULL"

    if isinstance(datatype, Int16):
        return column.name + " SMALLINT" + suffix
    elif isinstance(datatype, Int32):
        return column.name + " INTEGER" + suffix
    elif isinstance(datatype, Int64):
        return column.name + " BIGINT" + suffix
    elif isinstance(datatype, Float32):
        return column.name + " REAL" + suffix
    elif isinstance(datatype, Float64):
        return column.name + " DOUBLE PRECISION" + suffix
    elif isinstance(datatype, DateTime):
        return column.name + " TIMESTAMP" + suffix
    elif isinstance(datatype, Date):
        return column.name + " DATE" + suffix
    elif isinstance(datatype, String):
        return column.name + " TEXT" + suffix


def mysql_conversion(column):
    """Convert ClickHouse datatypes to MySQL datatypes."""
    if isinstance(column.datatype, UInt8) or isinstance(unwrap(column.datatype), UInt8):
        return (
            "`"
            + column.name
            + "` TINYINT UNSIGNED "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, Int8) or isinstance(unwrap(column.datatype), Int8):
        return (
            "`"
            + column.name
            + "` TINYINT SIGNED "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, UInt16) or isinstance(
        unwrap(column.datatype), UInt16
    ):
        return (
            "`"
            + column.name
            + "` SMALLINT UNSIGNED "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, Int16) or isinstance(
        unwrap(column.datatype), Int16
    ):
        return (
            "`"
            + column.name
            + "` SMALLINT SIGNED "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, UInt32) or isinstance(
        unwrap(column.datatype), UInt32
    ):
        return (
            "`"
            + column.name
            + "` INT UNSIGNED "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, Int32) or isinstance(
        unwrap(column.datatype), Int32
    ):
        return (
            "`"
            + column.name
            + "` INT UNSIGNED "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, UInt64) or isinstance(
        unwrap(column.datatype), UInt64
    ):
        return (
            "`"
            + column.name
            + "` BIGINT UNSIGNED "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, Int64) or isinstance(
        unwrap(column.datatype), Int64
    ):
        return (
            "`"
            + column.name
            + "` BIGINT SIGNED "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, Float32) or isinstance(
        unwrap(column.datatype), Float32
    ):
        return (
            "`"
            + column.name
            + "` DOUBLE "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, Float64) or isinstance(
        unwrap(column.datatype), Float64
    ):
        return (
            "`"
            + column.name
            + "` DOUBLE "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, FixedString) or isinstance(
        unwrap(column.datatype), FixedString
    ):
        return (
            "`"
            + column.name
            + "` BLOB "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, String) or isinstance(
        unwrap(column.datatype), String
    ):
        return (
            "`"
            + column.name
            + "` BLOB "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, DateTime) or isinstance(
        unwrap(column.datatype), DateTime
    ):
        return (
            "`"
            + column.name
            + "` DATETIME "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )
    elif isinstance(column.datatype, Date) or isinstance(unwrap(column.datatype), Date):
        return (
            "`"
            + column.name
            + "` DATE "
            + f"{'NULL' if isinstance(column.datatype, Nullable) else 'NOT NULL'}"
        )

    raise Exception(f"invalid type {type(column.datatype)}")


@TestOutline
def execute_query_step(
    self,
    sql,
    expected=None,
    exitcode=None,
    message=None,
    no_checks=False,
    snapshot_name=None,
    format="JSONEachRow",
    use_file=False,
    hash_output=False,
    snapshot_id=None,
    use_version=None,
):
    """Wrapper to call the execute_query function using testflows Check."""
    if use_version is not None:
        snapshot_name = current().name + use_version

    execute_query(
        sql=sql,
        expected=expected,
        exitcode=exitcode,
        message=message,
        no_checks=no_checks,
        snapshot_name=snapshot_name,
        format=format,
        use_file=use_file,
        hash_output=hash_output,
        snapshot_id=snapshot_id,
    )


def execute_query(
    sql,
    expected=None,
    exitcode=None,
    message=None,
    no_checks=False,
    snapshot_name=None,
    format="JSONEachRow",
    use_file=False,
    hash_output=False,
    snapshot_id=None,
):
    """Execute SQL query and compare the output to the snapshot."""
    if snapshot_name is None:
        snapshot_name = current().name

    if "DateTime64" in snapshot_name:
        if check_clickhouse_version(">=22.8")(current()):
            snapshot_name += ">=22.8"

    assert "snapshot_id" in current().context, "test must set self.context.snapshot_id"

    if snapshot_id is not None:
        snapshot_id = snapshot_id
    else:
        snapshot_id = current().context.snapshot_id

    with When("I execute query", description=sql):
        if format and not "FORMAT" in sql:
            sql += " FORMAT " + format

        r = current().context.node.query(
            sql,
            exitcode=exitcode,
            message=message,
            no_checks=no_checks,
            use_file=use_file,
            hash_output=hash_output,
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
                    snapshot_result = snapshot(
                        "\n" + r.output.strip() + "\n",
                        id=snapshot_id,
                        name=snapshot_name,
                        encoder=str,
                        mode=snapshot.UPDATE,
                    )
                    assert that(snapshot_result), error()
