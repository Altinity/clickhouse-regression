import os
import json
import random

from parquet.requirements import *
from parquet.tests.outline import import_export
from parquet.tests.common import generate_values
from helpers.common import *
from parquet.tests.bloom_filter_steps import *
from parquet.tests.steps import select_from_parquet, parquetify


@TestStep(When)
def get_all_columns(self, table_name, database, node=None):

    if node is None:
        node = self.context.node

    node.query(
        f"SELECT arrayStringConcat(groupArray(name), ',') AS column_names FROM system.columns WHERE database = 'default' AND table = 'users';"
    )


def rows_read(json_data):
    """Get the number of rows read from the json data."""

    return int(json.loads(json_data)["statistics"]["rows_read"])


@TestStep(Given)
def total_number_of_rows(self, file_name, node=None):
    """Get the total number of rows in the parquet file."""

    if node is None:
        node = self.context.node

    with By(f"getting the total number of rows in the parquet file {file_name}"):
        r = f"SELECT COUNT(*) FROM file('{file_name}', Parquet)"
        data = node.query(r)

    return int(data.output.strip())


@TestScenario
def read_and_write_file_with_bloom(self):
    """Read all files from a bloom directory that contains parquet files with bloom filters."""
    files = [
        "binary_bloom.gz.parquet",
        "timestamp_bloom.gz.parquet",
        "double_bloom.gz.parquet",
        "integer_bloom.gz.parquet",
        "decimal_bloom.gz.parquet",
        "struct_bloom.gz.parquet",
        "long_bloom.gz.parquet",
        "date_bloom.gz.parquet",
        "boolean_bloom.gz.parquet",
        "map_bloom.gz.parquet",
        "multi_column_bloom.gz.parquet",
        "array_bloom.gz.parquet",
        "float_bloom.gz.parquet",
    ]

    for file in files:
        with Given(f"I import and export the parquet file {file}"):
            import_export(
                snapshot_name=f"{file}_structure",
                import_file=os.path.join("bloom", file),
            )


@TestCheck
def check_parquet_with_bloom(
    self, file_name, statement, condition, bloom_filter, filter_pushdown, native_reader
):
    """Check if the bloom filter is being used by ClickHouse."""

    with Given("I get the total number of rows in the parquet file"):
        initial_rows = total_number_of_rows(
            file_name="bloom/multi_column_bloom.gz.parquet"
        )

    with And(
        "I read from the parquet file",
        description=f"Bloom Filter: {bloom_filter}, Filter Pushdown: {filter_pushdown}",
    ):
        with By(
            "selecting and saving the data from a parquet file without bloom filter enabled"
        ):
            data_without_bloom = select_from_parquet(
                file_name=file_name,
                statement=statement,
                condition=condition,
                format="Json",
                settings=f"input_format_parquet_use_native_reader={native_reader}",
                order_by="tuple(*)",
            )

        with And(
            f"selecting and saving the data from a parquet file with bloom filter {bloom_filter} and filter pushdown {filter_pushdown}"
        ):
            data = select_from_parquet(
                file_name=file_name,
                statement=statement,
                condition=condition,
                format="Json",
                settings=f"input_format_parquet_bloom_filter_push_down={bloom_filter},input_format_parquet_filter_push_down={filter_pushdown},use_cache_for_count_from_files=false, input_format_parquet_use_native_reader={native_reader}",
                order_by="tuple(*)",
            )

    with Then("I check that the number of rows read is correct"):
        read_rows = rows_read(data.output.strip())
        if bloom_filter == "true":
            with By(
                "Checking that the number of rows read is lower then the total number of rows of a file"
            ):
                assert read_rows < initial_rows, error()
        else:
            with By(
                "Checking that the number of rows read is equal to the total number of rows of a file"
            ):
                assert read_rows == initial_rows, error()

    with And(
        "I check that the data is the same when reading with bloom filter and without"
    ):
        assert data.output.strip() == data_without_bloom.output.strip(), error()


@TestSketch(Scenario)
def read_bloom_filter_parquet_files(self):
    """Read all files from a bloom directory that contains parquet files with bloom filters."""

    file_name = "bloom/multi_column_bloom.gz.parquet"
    statements = [
        "*",
        "f32",
        "f64",
        "int",
        "str",
        "fixed_str",
        "array",
        "f32,f64,int,str,fixed_str,array",
    ]
    filter = ["true", "false"]
    native_reader = "false"
    conditions = [
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC'",
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC' OR str='KCGEY'",
        "WHERE f32=toFloat32(-15.910733) AND fixed_str IN ('BYYC', 'DCXV') ORDER BY f32 ASC",
        "WHERE f64 IN (toFloat64(22.89182051713945), toFloat64(68.62704389505595)) ORDER BY f32",
        "WHERE has(array, 69778) ORDER BY f32 ASC",
        "WHERE hasAll(array, [69778,58440,2913,64975,92300]) ORDER BY f32 ASC",
        "WHERE has(array, toInt32(toString(69778)))",
        "WHERE hasAny(array, [69778,58440,2913,64975,92300]) ORDER BY f32 asc",
        "WHERE '48' NOT IN 'int' AND fixed_str='BYYC'",
    ]

    check_parquet_with_bloom(
        file_name=file_name,
        bloom_filter=either(*filter),
        filter_pushdown=either(*filter),
        condition=either(*conditions),
        statement=either(*statements),
        native_reader=native_reader,
    )


@TestSketch(Scenario)
def read_bloom_filter_parquet_files_native_reader(self):
    """Read all files from a bloom directory that contains parquet files with bloom filters using the ClickHouse parquet native reader."""

    file_name = "bloom/bloom_no_arrays.gz.parquet"
    statements = [
        "*",
        "f32",
        "f64",
        "int",
        "str",
        "fixed_str",
        "f32,f64,int,str,fixed_str",
    ]
    filter = ["true", "false"]
    native_reader = "true"
    conditions = [
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC'",
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC' OR str='KCGEY'",
        "WHERE f32=toFloat32(-15.910733) AND fixed_str IN ('BYYC', 'DCXV') ORDER BY f32 ASC",
        "WHERE f64 IN (toFloat64(22.89182051713945), toFloat64(68.62704389505595)) ORDER BY f32",
        "WHERE '48' NOT IN 'int' AND fixed_str='BYYC'",
    ]

    check_parquet_with_bloom(
        file_name=file_name,
        bloom_filter=either(*filter),
        filter_pushdown=either(*filter),
        condition=either(*conditions),
        statement=either(*statements),
        native_reader=native_reader,
    )


@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_DataTypes_Complex("1.0")
)
@TestScenario
def native_reader_array_bloom(self):
    """Read a parquet file with bloom filter and array column using the ClickHouse parquet native reader."""
    file = "array_bloom.gz.parquet"

    select_from_parquet(
        file_name=file,
        format="Json",
        settings=f"input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=false,use_cache_for_count_from_files=false, input_format_parquet_use_native_reader=true",
    )


@TestCheck
def check_bloom_filter_on_parquet(
    self,
    schema_type,
    writer_version,
    physical_type,
    logical_type,
    compression_value,
    statement,
    native_reader,
    filter_pushdown,
    bloom_filter_on_clickhouse,
    conversions,
):
    """Check if the bloom filter is being used by ClickHouse."""
    file_definition = {}
    option_list = {}
    schema_values = {}

    with Given("I prepare data required for the parquet file"):
        json_file_name = (
            f"{compression_value()['compression']}_{physical_type()['physicalType']}_{logical_type()['logicalType'] if logical_type is not None else 'None'}_"
            + getuid()
            + ".json"
        )
        path = self.context.json_files_local + "/" + json_file_name

        if logical_type is None:
            data = generate_values(
                physical_type()["physicalType"], random.randint(1, 100)
            )
        else:
            data = generate_values(
                logical_type()["logicalType"], random.randint(1, 100)
            )

        column_name = logical_type()["logicalType"].lower()
        parquet_file = (
            f"{compression_value()['compression']}_{physical_type()['physicalType']}_{logical_type()['logicalType'] if logical_type is not None else 'None'}_"
            + getuid()
            + ".parquet"
        )
    with And("I create a parquet JSON definition"):

        file_definition.update(parquet_file_name(filename=f"{parquet_file}"))
        option_list.update(writer_version())
        option_list.update(compression_value())
        option_list.update(row_group_size())
        option_list.update(page_size())
        option_list.update(encodings())
        option_list.update(bloom_filter())

        file_options = options(options=option_list)

        file_definition.update(file_options)

        schema_values.update(
            schema_type(
                name=column_name,
                physical_type=physical_type(),
                logical_type=logical_type(),
                data=data,
            )
        )

        file_schema = schema(schema=schema_values)

        file_definition.update(file_schema)

    with open(path, "w") as json_file:
        json.dump(file_definition, json_file, indent=2)

    with And(f"generate a parquet file {parquet_file}"):
        parquetify(
            json_file=self.context.json_files + "/" + json_file_name,
            output_path=self.context.parquet_output_path,
        )

    with And("I get the total number of rows in the parquet file"):
        initial_rows = total_number_of_rows(file_name=parquet_file)

    with Check("I check that the bloom filter is being used by ClickHouse"):
        for conversion in conversions:
            condition = f"WHERE {column_name} = {conversion}({data[0]})"
            with By(
                "selecting and saving the data from a parquet file without bloom filter enabled"
            ):
                data_without_bloom = select_from_parquet(
                    file_name=parquet_file,
                    statement=statement,
                    condition=condition,
                    format="TabSeparated",
                    settings=f"input_format_parquet_use_native_reader={native_reader}",
                    order_by="tuple(*)",
                )

                data_with_bloom = select_from_parquet(
                    file_name=parquet_file,
                    statement=statement,
                    condition=condition,
                    format="TabSeparated",
                    settings=f"input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down={filter_pushdown},use_cache_for_count_from_files=false, input_format_parquet_use_native_reader={native_reader}",
                    order_by="tuple(*)",
                )

            with And(
                f"selecting and saving the data from a parquet file with bloom filter {bloom_filter_on_clickhouse} and filter pushdown {filter_pushdown}"
            ):
                read_with_bloom = select_from_parquet(
                    file_name=parquet_file,
                    statement=statement,
                    condition=condition,
                    format="Json",
                    settings=f"input_format_parquet_bloom_filter_push_down={bloom_filter_on_clickhouse},input_format_parquet_filter_push_down={filter_pushdown},use_cache_for_count_from_files=false, input_format_parquet_use_native_reader={native_reader}",
                    order_by="tuple(*)",
                )

            with Then("I check that the number of rows read is correct"):
                read_rows = rows_read(read_with_bloom.output.strip())
                if bloom_filter_on_clickhouse == "true":
                    with By(
                        "Checking that the number of rows read is lower then the total number of rows of a file"
                    ):
                        assert read_rows < initial_rows, error()
                else:
                    with By(
                        "Checking that the number of rows read is equal to the total number of rows of a file"
                    ):
                        assert read_rows == initial_rows, error()

            with And(
                "I check that the data is the same when reading with bloom filter and without"
            ):
                assert (
                    data_with_bloom.output.strip() == data_without_bloom.output.strip()
                ), error()


@TestSketch(Scenario)
@Flags(TE)
def read_parquet_with_bloom_filter(self):
    """Read parquet files with different structure with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and integrity is kept."""

    conversions = [
        "toBool",
        "toInt8",
        "toInt8OrZero",
        "toInt8OrNull",
        "toInt8OrDefault",
        "toInt16",
        "toInt16OrZero",
        "toInt16OrNull",
        "toInt16OrDefault",
        "toInt32",
        "toInt32OrZero",
        "toInt32OrNull",
        "toInt32OrDefault",
        "toInt64",
        "toInt64OrZero",
        "toInt64OrNull",
        "toInt64OrDefault",
        "toInt128",
        "toInt128OrZero",
        "toInt128OrNull",
        "toInt128OrDefault",
        "toInt256",
        "toInt256OrZero",
        "toInt256OrNull",
        "toInt256OrDefault",
        "toUInt8",
        "toUInt8OrZero",
        "toUInt8OrNull",
        "toUInt8OrDefault",
        "toUInt16",
        "toUInt16OrZero",
        "toUInt16OrNull",
        "toUInt16OrDefault",
        "toUInt32",
        "toUInt32OrZero",
        "toUInt32OrNull",
        "toUInt32OrDefault",
        "toUInt64",
        "toUInt64OrZero",
        "toUInt64OrNull",
        "toUInt64OrDefault",
        "toUInt128",
        "toUInt128OrZero",
        "toUInt128OrNull",
        "toUInt128OrDefault",
        "toUInt256",
        "toUInt256OrZero",
        "toUInt256OrNull",
        "toUInt256OrDefault",
        "toFloat32",
        "toFloat32OrZero",
        "toFloat32OrNull",
        "toFloat32OrDefault",
        "toFloat64",
        "toFloat64OrZero",
        "toFloat64OrNull",
        "toFloat64OrDefault",
        "toDate",
        "toDateOrZero",
        "toDateOrNull",
        "toDateOrDefault",
        "toDateTime",
        "toDateTimeOrZero",
        "toDateTimeOrNull",
        "toDateTimeOrDefault",
        "toDate32",
        "toDate32OrZero",
        "toDate32OrNull",
        "toDate32OrDefault",
        "toDateTime64",
        "toDateTime64OrZero",
        "toDateTime64OrNull",
        "toDateTime64OrDefault",
        "toDecimal32",
        "toDecimal32OrZero",
        "toDecimal32OrNull",
        "toDecimal32OrDefault",
        "toDecimal64",
        "toDecimal64OrZero",
        "toDecimal64OrNull",
        "toDecimal64OrDefault",
        "toDecimal128",
        "toDecimal128OrZero",
        "toDecimal128OrNull",
        "toDecimal128OrDefault",
        "toDecimal256",
        "toDecimal256OrZero",
        "toDecimal256OrNull",
        "toDecimal256OrDefault",
        "toString",
        "toFixedString",
        "toStringCutToZero",
        "toDecimalString",
        "reinterpretAsUInt8",
        "reinterpretAsUInt16",
        "reinterpretAsUInt32",
        "reinterpretAsUInt64",
        "reinterpretAsUInt128",
        "reinterpretAsUInt256",
        "reinterpretAsInt8",
        "reinterpretAsInt16",
        "reinterpretAsInt32",
        "reinterpretAsInt64",
        "reinterpretAsInt128",
        "reinterpretAsInt256",
        "reinterpretAsFloat32",
        "reinterpretAsFloat64",
        "reinterpretAsDate",
        "reinterpretAsDateTime",
        "reinterpretAsString",
        "reinterpretAsFixedString",
        "reinterpretAsUUID",
        "reinterpret",
        "CAST",
        "accurateCast(x, T)",
        "accurateCastOrNull(x, T)",
        "accurateCastOrDefault(x, T, default_value)",
        "toIntervalYear",
        "toIntervalQuarter",
        "toIntervalMonth",
        "toIntervalWeek",
        "toIntervalDay",
        "toIntervalHour",
        "toIntervalMinute",
        "toIntervalSecond",
        "toIntervalMillisecond",
        "toIntervalMicrosecond",
        "toIntervalNanosecond",
        "parseDateTime",
        "parseDateTimeOrZero",
        "parseDateTimeOrNull",
        "parseDateTimeInJodaSyntax",
        "parseDateTimeInJodaSyntaxOrZero",
        "parseDateTimeInJodaSyntaxOrNull",
        "parseDateTimeBestEffort",
        "parseDateTime32BestEffort",
        "parseDateTimeBestEffortUS",
        "parseDateTime32BestEffortOrNull",
        "parseDateTimeBestEffortOrZero",
        "parseDateTime32BestEffortOrZero",
        "parseDateTimeBestEffortUSOrNull",
        "parseDateTimeBestEffortUSOrZero",
        "parseDateTime64BestEffort",
        "parseDateTime64BestEffortUS",
        "parseDateTime64BestEffortOrNull",
        "parseDateTime64BestEffortOrZero",
        "parseDateTime64BestEffortUSOrNull",
        "parseDateTime64BestEffortUSOrZero",
        "toLowCardinality",
        "toUnixTimestamp64Milli",
        "toUnixTimestamp64Micro",
        "toUnixTimestamp64Nano",
        "fromUnixTimestamp64Milli",
        "fromUnixTimestamp64Micro",
        "fromUnixTimestamp64Nano",
        "formatRow",
        "formatRowNoNewline",
    ]

    writer_version = [writer_version_1_0, writer_version_2_0]
    compression = [snappy_compression, gzip_compression, lzo_compression, uncompressed]
    encodings = ["DICTIONARY", "BYTE_STREAM_SPLIT", "PLAIN"]
    schema_type = [
        optional,
        required,
        repeated,
        optional_group,
        required_group,
        repeated_group,
    ]
    physical_types = [
        int32_physical,
        int64_physical,
        int96_physical,
        boolean_physical,
        float_physical,
        double_physical,
        binary_physical,
        fixed_len_byte_array_physical,
    ]
    logical_types = [
        utf8,
        decimal,
        date,
        time_millis,
        time_micros,
        timestamp_millis,
        timestamp_micros,
        enum,
        map,
        list,
        string,
        map_key_value,
        time,
        integer,
        json_type,
        bson,
        uuid,
        interval,
        float16,
        uint8,
        uint16,
        uint32,
        uint64,
        int8,
        int16,
        int32,
        int64,
        no_logical_type,
    ]
    filter = ["true", "false"]
    statements = ["*"]
    check_bloom_filter_on_parquet(
        schema_type=either(*schema_type),
        writer_version=either(*writer_version),
        physical_type=either(*physical_types),
        logical_type=either(*logical_types),
        compression_value=either(*compression),
        statement=either(*statements),
        native_reader="false",
        filter_pushdown=either(*filter),
        bloom_filter_on_clickhouse=either(*filter),
        conversions=conversions,
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter("1.0"))
@Name("bloom")
def feature(self, node="clickhouse1"):
    """Check if we can read from ap parquet file with bloom filter and validate that the bloom filter is being used
    by ClickHouse.

    The combinations used:
        - Check that ClickHouse can read and then write back the parquet files that have bloom filter applied to them.
    Combinatorics:
        statements:
            - "*",
            - "f32",
            - "f64",
            - "int",
            - "str",
            - "fixed_str",
            - "array",
            - "f32,f64,int,str,fixed_str,array",
        settings:
            - input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=true
            - input_format_parquet_bloom_filter_push_down=false,input_format_parquet_filter_push_down=false
            - input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=false
            - input_format_parquet_bloom_filter_push_down=false,input_format_parquet_filter_push_down=true
        conditions:
            - WHERE
            - OR
            - AND
            - IN
            - NOT IN
            - has()
            - hasAny()
            - hasAll()
    """
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "bloom"
    self.context.json_files_local = os.path.join(
        current_dir(), "..", "data", "json_files"
    )
    self.context.json_files = "/json_files"
    self.context.parquet_output_path = "/parquet-files"

    Scenario(run=read_bloom_filter_parquet_files)
    Scenario(run=read_bloom_filter_parquet_files_native_reader)
    Scenario(run=native_reader_array_bloom)
    Scenario(run=read_parquet_with_bloom_filter)
