import json
import datetime
import base64
from decimal import Decimal
import re

from parquet.requirements import *
from parquet.tests.outline import import_export
from parquet.tests.common import generate_values
from helpers.common import *
from parquet.tests.steps.bloom_filter import *
from parquet.tests.steps.general import (
    select_from_parquet,
    parquetify,
    get_parquet_structure,
)


class JSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder:
        - Supports DateTime serialization.
        - Supports Date serialization.
        - Supports bytes serialization.
        - Supports Decimal serialization.
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, bytes):
            try:
                return obj.decode("utf-8")
            except UnicodeDecodeError:
                return base64.b64encode(obj).decode("ascii")
        if isinstance(obj, Decimal):
            return str(obj)  # Convert Decimal to string to avoid precision loss
        return super().default(obj)



@TestStep(When)
def get_all_columns(self, table_name, database, node=None):

    if node is None:
        node = self.context.node

    node.query(
        f"SELECT arrayStringConcat(groupArray(name), ',') AS column_names FROM system.columns WHERE database = 'default' AND table = 'users';"
    )


def rows_read(json_data):
    """Get the number of rows read from the json data."""
    data = json_data[-1]
    return data


@TestStep(Given)
def total_number_of_rows(self, file_name, node=None):
    """Get the total number of rows in the parquet file."""

    if node is None:
        node = self.context.node

    with By(f"getting the total number of rows in the parquet file {file_name}"):
        r = f"SELECT COUNT(*) FROM file('{file_name}', Parquet)"
        data = node.query(r)

    return int(data.output[0][0])


# @TestScenario
# def read_and_write_file_with_bloom(self):
#     """Read all files from a bloom directory that contains parquet files with bloom filters."""
#     files = [
#         "binary_bloom.gz.parquet",
#         "timestamp_bloom.gz.parquet",
#         "double_bloom.gz.parquet",
#         "integer_bloom.gz.parquet",
#         "decimal_bloom.gz.parquet",
#         "struct_bloom.gz.parquet",
#         "long_bloom.gz.parquet",
#         "date_bloom.gz.parquet",
#         "boolean_bloom.gz.parquet",
#         "map_bloom.gz.parquet",
#         "multi_column_bloom.gz.parquet",
#         "array_bloom.gz.parquet",
#         "float_bloom.gz.parquet",
#     ]
#
#     for file in files:
#         with Given(f"I import and export the parquet file {file}"):
#             import_export(
#                 snapshot_name=f"{file}_structure",
#                 import_file=os.path.join("bloom", file),
#             )


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


# @TestSketch(Scenario)
# def read_bloom_filter_parquet_files(self):
#     """Read all files from a bloom directory that contains parquet files with bloom filters."""
#
#     file_name = "bloom/multi_column_bloom.gz.parquet"
#     statements = [
#         "*",
#         "f32",
#         "f64",
#         "int",
#         "str",
#         "fixed_str",
#         "array",
#         "f32,f64,int,str,fixed_str,array",
#     ]
#     filter = ["true", "false"]
#     native_reader = "false"
#     conditions = [
#         "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC'",
#         "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC' OR str='KCGEY'",
#         "WHERE f32=toFloat32(-15.910733) AND fixed_str IN ('BYYC', 'DCXV') ORDER BY f32 ASC",
#         "WHERE f64 IN (toFloat64(22.89182051713945), toFloat64(68.62704389505595)) ORDER BY f32",
#         "WHERE has(array, 69778) ORDER BY f32 ASC",
#         "WHERE hasAll(array, [69778,58440,2913,64975,92300]) ORDER BY f32 ASC",
#         "WHERE has(array, toInt32(toString(69778)))",
#         "WHERE hasAny(array, [69778,58440,2913,64975,92300]) ORDER BY f32 asc",
#         "WHERE '48' NOT IN 'int' AND fixed_str='BYYC'",
#     ]
#
#     check_parquet_with_bloom(
#         file_name=file_name,
#         bloom_filter=either(*filter),
#         filter_pushdown=either(*filter),
#         condition=either(*conditions),
#         statement=either(*statements),
#         native_reader=native_reader,
#     )


# @TestSketch(Scenario)
# def read_bloom_filter_parquet_files_native_reader(self):
#     """Read all files from a bloom directory that contains parquet files with bloom filters using the ClickHouse parquet native reader."""
#
#     file_name = "bloom/bloom_no_arrays.gz.parquet"
#     statements = [
#         "*",
#         "f32",
#         "f64",
#         "int",
#         "str",
#         "fixed_str",
#         "f32,f64,int,str,fixed_str",
#     ]
#     filter = ["true", "false"]
#     native_reader = "true"
#     conditions = [
#         "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC'",
#         "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC' OR str='KCGEY'",
#         "WHERE f32=toFloat32(-15.910733) AND fixed_str IN ('BYYC', 'DCXV') ORDER BY f32 ASC",
#         "WHERE f64 IN (toFloat64(22.89182051713945), toFloat64(68.62704389505595)) ORDER BY f32",
#         "WHERE '48' NOT IN 'int' AND fixed_str='BYYC'",
#     ]
#
#     check_parquet_with_bloom(
#         file_name=file_name,
#         bloom_filter=either(*filter),
#         filter_pushdown=either(*filter),
#         condition=either(*conditions),
#         statement=either(*statements),
#         native_reader=native_reader,
#     )


# @Requirements(
#     RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_DataTypes_Complex("1.0")
# )
# @TestScenario
# def native_reader_array_bloom(self):
#     """Read a parquet file with bloom filter and array column using the ClickHouse parquet native reader."""
#     file = "array_bloom.gz.parquet"
#
#     select_from_parquet(
#         file_name=file,
#         format="Json",
#         settings=f"input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=false,use_cache_for_count_from_files=false, input_format_parquet_use_native_reader=true",
#     )


@TestStep
def check_all_conversions(self):
    pass


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

    node = self.context.node
    bash_tools = self.context.cluster.node("bash-tools")
    number_of_inserts = self.context.number_of_inserts

    with Given("I prepare data required for the parquet file"):
        json_file_name = (
            f"{compression_value()['compression']}_{physical_type()['physicalType']}_"
            f"{logical_type()['logicalType']}_" + getuid() + ".json"
        )
        path = self.context.json_files_local + "/" + json_file_name
        if logical_type()["logicalType"] == "NONE":
            data = generate_values(physical_type()["physicalType"], number_of_inserts)
            column_name = physical_type()["physicalType"].lower()

        else:
            data = generate_values(logical_type()["logicalType"], number_of_inserts)
            column_name = logical_type()["logicalType"].lower()

        parquet_file = (
            f"{compression_value()['compression']}_{physical_type()['physicalType']}_"
            f"{logical_type()['logicalType']}_" + getuid() + ".parquet"
        )

    with And("I create a parquet JSON definition"):

        file_definition.update(parquet_file_name(filename=f"{parquet_file}"))
        option_list.update(writer_version())
        option_list.update(compression_value())
        option_list.update(row_group_size(size=256))
        option_list.update(page_size(size=1024))
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
    with And(f"I save the JSON definition to a file {json_file_name}"):
        snapshot_name = f"{option_list['compression']}_{physical_type()['physicalType']}_{logical_type()['logicalType']}_{schema_values['schemaType']}_{option_list['writerVersion'].replace('.', '_')}"

        with open(path, "w") as json_file:
            json.dump(file_definition, json_file, cls=JSONEncoder, indent=2)

    with And(f"generate a parquet file {parquet_file}"):
        generate_parquet = parquetify(
            json_file=self.context.json_files + "/" + json_file_name,
            output_path=self.context.parquet_output_path,
            no_checks=True,
        )

    with bash_tools.client(
        client_args={"host": node.name, "statistics": "null"}
    ) as client:
        with When("I get the total number of rows in the parquet file"):
            if generate_parquet.exitcode != 0:
                skip("Incorrect JSON file structure")

            initial_rows = total_number_of_rows(file_name=parquet_file, node=client)

            for conversion in conversions:
                condition = f"WHERE {column_name} = {conversion}('{data[-1]}')"
                with Check("I check that the bloom filter is being used by ClickHouse"):

                    with By(
                        "selecting and saving the data from a parquet file without bloom filter enabled"
                    ):
                        check_conversion = select_from_parquet(
                            file_name=parquet_file,
                            statement=statement,
                            condition=condition,
                            format="TabSeparated",
                            settings=f"input_format_parquet_use_native_reader={native_reader}",
                            order_by="tuple(*)",
                            node=client,
                            no_checks=True,
                        )

                        if check_conversion.errorcode != 0:
                            continue

                        data_without_bloom = select_from_parquet(
                            file_name=parquet_file,
                            statement=statement,
                            format="TabSeparated",
                            settings=f"input_format_parquet_use_native_reader={native_reader}",
                            order_by="tuple(*)",
                            node=client,
                            limit=10
                        )

                        data_with_bloom = select_from_parquet(
                            file_name=parquet_file,
                            statement=statement,
                            format="TabSeparated",
                            settings=f"input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down={filter_pushdown},use_cache_for_count_from_files=false, input_format_parquet_use_native_reader={native_reader}",
                            order_by="tuple(*)",
                            node=client,
                            limit=10
                        )

                        file_structure = get_parquet_structure(file_name=parquet_file)

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
                            node=client,
                        )

                    with Then("I check that the number of rows read is correct"):
                        read_rows = rows_read(read_with_bloom.output)

                        with values() as that:
                            assert that(
                                snapshot(
                                    f"{read_rows}, initial_rows: {initial_rows}, file_structure: {file_structure.output}, condition: {condition}",
                                    name=f"{snapshot_name}_{conversion}",
                                    id="bloom_filter",
                                    mode=snapshot.UPDATE,
                                )
                            ), error()

                    with And(
                        "I check that the data is the same when reading with bloom filter and without"
                    ):
                        data_with_bloom = data_with_bloom.output
                        data_without_bloom = data_without_bloom.output

                        data_with_bloom.pop(-1)
                        data_without_bloom.pop(-1)

                        assert (
                            data_with_bloom == data_without_bloom
                        ), error()


@TestSketch(Outline)
@Flags(TE)
def read_parquet_with_bloom_filter(self, logical_type, statements=None):
    """Read parquet files with different structure with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""

    if statements is None:
        statements = ["*"]

    filter = ["true", "false"]
    check_bloom_filter_on_parquet(
        schema_type=either(*schema_type),
        writer_version=either(*writer_version),
        physical_type=either(*physical_types),
        logical_type=logical_type,
        compression_value=either(*compression),
        statement=either(*statements),
        native_reader="false",
        filter_pushdown=either(*filter),
        bloom_filter_on_clickhouse=either(*filter),
        conversions=conversions,
    )


@TestSketch(Scenario)
@Flags(TE)
def utf8_with_bloom_filter(self):
    """Read parquet files with utf-8 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=utf8)


@TestSketch(Scenario)
@Flags(TE)
def decimal_with_bloom_filter(self):
    """Read parquet files with decimal logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=decimal)


@TestSketch(Scenario)
@Flags(TE)
def date_with_bloom_filter(self):
    """Read parquet files with date logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=date)


@TestSketch(Scenario)
@Flags(TE)
def time_millis_with_bloom_filter(self):
    """Read parquet files with time-millis logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=time_millis)


@TestSketch
@Flags(TE)
def time_micros_with_bloom_filter(self):
    """Read parquet files with time-micros logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=time_micros)


@TestSketch(Scenario)
@Flags(TE)
def timestamp_millis_with_bloom_filter(self):
    """Read parquet files with timestamp-millis logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=timestamp_millis)


@TestSketch(Scenario)
@Flags(TE)
def timestamp_micros_with_bloom_filter(self):
    """Read parquet files with timestamp-micros logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=timestamp_micros)


@TestSketch(Scenario)
@Flags(TE)
def enum_with_bloom_filter(self):
    """Read parquet files with enum logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=enum)


@TestSketch(Scenario)
@Flags(TE)
def map_with_bloom_filter(self):
    """Read parquet files with map logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=map)


@TestSketch(Scenario)
@Flags(TE)
def list_with_bloom_filter(self):
    """Read parquet files with list logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=list)


@TestSketch(Scenario)
@Flags(TE)
def string_with_bloom_filter(self):
    """Read parquet files with string logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=string)


@TestSketch(Scenario)
@Flags(TE)
def map_key_value_with_bloom_filter(self):
    """Read parquet files with map key value logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=map_key_value)


@TestSketch(Scenario)
@Flags(TE)
def time_with_bloom_filter(self):
    """Read parquet files with time logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=time)


@TestSketch(Scenario)
@Flags(TE)
def integer_with_bloom_filter(self):
    """Read parquet files with integer logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=integer)


@TestSketch(Scenario)
@Flags(TE)
def json_with_bloom_filter(self):
    """Read parquet files with json logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=json_type)


@TestSketch(Scenario)
@Flags(TE)
def bson_with_bloom_filter(self):
    """Read parquet files with bson logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=bson)


@TestSketch(Scenario)
@Flags(TE)
def uuid_with_bloom_filter(self):
    """Read parquet files with uuid logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=uuid)


@TestSketch(Scenario)
@Flags(TE)
def interval_with_bloom_filter(self):
    """Read parquet files with interval logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=interval)


@TestSketch(Scenario)
@Flags(TE)
def float16_with_bloom_filter(self):
    """Read parquet files with float16 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=float16)


@TestSketch(Scenario)
@Flags(TE)
def uint8_with_bloom_filter(self):
    """Read parquet files with uint8 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=uint8)


@TestSketch(Scenario)
@Flags(TE)
def uint16_with_bloom_filter(self):
    """Read parquet files with uint16 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=uint16)


@TestSketch(Scenario)
@Flags(TE)
def uint32_with_bloom_filter(self):
    """Read parquet files with uint32 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=uint32)


@TestSketch(Scenario)
@Flags(TE)
def uint64_with_bloom_filter(self):
    """Read parquet files with uint64 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=uint64)


@TestSketch(Scenario)
@Flags(TE)
def int8_with_bloom_filter(self):
    """Read parquet files with int8 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=int8)


@TestSketch(Scenario)
@Flags(TE)
def int16_with_bloom_filter(self):
    """Read parquet files with int16 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=int16)


@TestSketch(Scenario)
@Flags(TE)
def int32_with_bloom_filter(self):
    """Read parquet files with int32 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=int32)


@TestSketch(Scenario)
@Flags(TE)
def int64_with_bloom_filter(self):
    """Read parquet files with int64 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=int64)


@TestSketch(Scenario)
@Flags(TE)
def no_logical_type_with_bloom_filter(self):
    """Read parquet files with no logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    read_parquet_with_bloom_filter(logical_type=no_logical_type)


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter("1.0"))
@Name("bloom")
def feature(self, node="clickhouse1", number_of_inserts=1500):
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
    self.context.number_of_inserts = number_of_inserts
    for scenario in loads(current_module(), Scenario):
        scenario()
