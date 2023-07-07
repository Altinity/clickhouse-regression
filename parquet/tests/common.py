import uuid
import pyarrow.parquet as pq

from testflows._core.testtype import TestSubType
from testflows.core.name import basename, parentname
from testflows.core import current
from helpers.common import *
from helpers.datatypes import *
from helpers.tables import *
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
            f"{basename(parentname(current().name)).replace(' ', '_').replace(',','')}"
        )
    else:
        testname = f"{basename(current().name).replace(' ', '_').replace(',','')}"
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
            self.context.cluster.command(None, f"mkdir /tmp/test_files")
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


@TestStep(Then)
def check_source_file(self, path, compression=None):
    """Check the contents of a Parquet file against either snapshot or provided values."""
    node = current().context.node
    table_name = "table_" + getuid()

    with By("creating a table"):
        table = create_table(
            name=table_name,
            engine="Memory",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with And("inserting data from the specified file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '{path}' {'COMPRESSION '+ compression if compression and compression != 'NONE' else ''} FORMAT Parquet"
        )

    with Pool(3) as executor:
        for column in table.columns:
            Check(
                test=execute_query_step,
                name=f"{column.datatype.name}",
                parallel=True,
                executor=executor,
            )(sql=f"SELECT {column.name}, toTypeName({column.name}) FROM {table.name}")
        join()

    return


@TestStep(Then)
def check_source_file_on_s3(self, file, compression_type=None):
    """Download specified file from aws s3 and check the contents."""

    if self.context.storage == "aws_s3":
        with By("Downloading the file"):
            self.context.s3_client.download_file(
                self.context.aws_s3_bucket,
                f"data/parquet/{file}",
                "/tmp/test_files/data.Parquet",
            )

    elif self.context.storage == "minio":
        with By("Downloading the file"):
            self.context.s3_client.fget_object(
                self.context.cluster.minio_bucket,
                "data/parquet/" + file,
                "/tmp/test_files/data.Parquet",
            )

    with By("copying the file to the docker node"):
        x = self.context.cluster.command(
            None, "docker ps | grep clickhouse1 | cut -d ' ' -f 1 | head -n 1"
        ).output
        self.context.cluster.command(
            None,
            f"docker cp /tmp/test_files/data.Parquet {x}:/data.Parquet",
        )

    with Then("I check the file"):
        check_source_file(path="/data.Parquet", compression=compression_type)


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
        Decimal128(38),
        Date(),
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
):
    """Wrapper to call the execute_query function using testflows Check."""
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
):
    """Execute SQL query and compare the output to the snapshot."""
    if snapshot_name is None:
        snapshot_name = current().name

    if "DateTime64" in snapshot_name:
        if check_clickhouse_version(">=22.8")(current()):
            snapshot_name += ">=22.8"

    assert "snapshot_id" in current().context, "test must set self.context.snapshot_id"

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
                    assert that(
                        snapshot(
                            "\n" + r.output.strip() + "\n",
                            id=current().context.snapshot_id,
                            name=snapshot_name,
                            encoder=str,
                        )
                    ), error()
