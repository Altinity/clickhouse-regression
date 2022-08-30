from testflows.core import *

from s3.tests.common import *
from s3.requirements import *


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Syntax("1.0"))
def syntax(self):
    """Check that S3 storage works correctly for both imports and exports
    when accessed using a table function.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node
    expected = "427"

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the first table {name_table1}"):
            node.query(f"INSERT INTO {name_table1} VALUES (427)")

        with When(f"I export the data to S3 using the table function"):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}syntax.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}"""
            )

        with And(f"I import the data from S3 into the second table {name_table2}"):
            node.query(
                f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}syntax.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')"""
            )

        with Then(
            f"""I check that a simple SELECT * query on the second table
                   {name_table2} returns matching data"""
        ):
            r = node.query(f"SELECT * FROM {name_table2} FORMAT CSV").output.strip()
            assert r == expected, error()

    finally:
        with Finally("I overwrite the S3 data with empty data"):
            with By(f"I drop the first table {name_table1}"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And(f"I create the table again {name_table1}"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d"""
                )

            with And(
                f"""I export the empty table {name_table1} to S3 at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}syntax.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestOutline(Scenario)
@Examples(
    "wildcard expected",
    [
        ("*", "427\n427\n427\n427", Name("star")),
        ("%3F", "427\n427\n427", Name("question")),
        ("{2..3}", "427\n427", Name("nums")),
        ("{1,3}", "427\n427", Name("strings")),
    ],
)
@Requirements(RQ_SRS_015_S3_TableFunction_Path_Wildcard("1.0"))
def wildcard(self, wildcard, expected):
    """Check that imports from S3 storage using the S3 table function work
    correctly when wildcard paths with the '{wildcard}' wildcard are provided.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node

    if self.context.storage == "minio":
        with Given("If using MinIO, clear objects on directory path to avoid error"):
            self.context.cluster.minio_client.remove_object(
                self.context.cluster.minio_bucket, "data"
            )

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the first table {name_table1}"):
            node.query(f"INSERT INTO {name_table1} VALUES (427)")

        with When("I export the data to S3 using the table function"):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}subdata', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}"""
            )

        with And("I export the data to a different path in my bucket"):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}subdata1', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}"""
            )

        with And("I export the data to a different path in my bucket"):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}subdata2', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}"""
            )

        with And("I export the data to yet another path in my bucket"):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}subdata3', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}"""
            )

        with And(
            f"""I import the data from external storage into the second
                 table {name_table2} using the wildcard '{wildcard}'"""
        ):
            node.query(
                f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}subdata{wildcard}', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')"""
            )

        with Then(
            f"""I check that a simple SELECT * query on the second table
                   {name_table2} returns expected data"""
        ):
            for retry in retries(timeout=600, delay=5):
                with retry:
                    r = node.query(f"SELECT * FROM {name_table2}").output.strip()
                    assert r == expected, error()

    finally:
        with Finally("I overwrite the S3 data with empty data"):
            with By(f"I drop the first table {name_table1}"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And(f"I create the table again {name_table1}"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d"""
                )

            with And(
                f"""I export the empty table {name_table1} to S3 at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}subdata', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

            with And(
                f"""I export the empty table {name_table1} to S3 at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}subdata1', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

            with And(
                f"""I export the empty table {name_table1} to S3 at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}subdata2', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

            with And(
                f"""I export the empty table {name_table1} to S3 at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}subdata3', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestOutline(Scenario)
@Examples(
    "compression_method",
    [
        ("gzip", Name("Gzip")),
        ("gz", Name("Gzip short")),
        ("deflate", Name("Zlib")),
        ("brotli", Name("Brotli")),
        ("br", Name("Brotli short")),
        ("LZMA", Name("Xz")),
        ("xz", Name("Xz short")),
        ("zstd", Name("Zstd")),
        ("zst", Name("Zstd short")),
    ],
)
@Requirements(RQ_SRS_015_S3_TableFunction_Compression("1.0"))
def compression(self, compression_method):
    """Check that ClickHouse can successfully use all supported compression
    methods for the S3 table function.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node
    expected = "427"

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the first table {name_table1}"):
            node.query(f"INSERT INTO {name_table1} VALUES (427)")

        with When(
            f"""I export the data to S3 using the table function with compression
                  parameter set to '{compression_method}'"""
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}compression.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64', '{compression_method}')
                SELECT * FROM {name_table1}"""
            )

        with And(
            f"""I import the data from S3 into the second table {name_table2}
                  using the table function with compression parameter set to '{compression_method}'"""
        ):
            node.query(
                f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}compression.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64', '{compression_method}')"""
            )

        with Then(
            f"""I check that a simple SELECT * query on the second table
                   {name_table2} returns matching data"""
        ):
            r = node.query(f"SELECT * FROM {name_table2} FORMAT CSV").output.strip()
            assert r == expected, error()

    finally:
        with Finally("I overwrite the S3 data with empty data"):
            with By(f"I drop the first table {name_table1}"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And(f"I create the table again {name_table1}"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d"""
                )

            with And(
                f"""I export the empty table {name_table1} to S3 at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}compression.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestOutline(Scenario)
@Examples(
    "compression_method",
    [
        ("gzip", Name("Gzip")),
        ("gz", Name("Gzip short")),
        ("deflate", Name("Zlib")),
        ("brotli", Name("Brotli")),
        ("br", Name("Brotli short")),
        ("LZMA", Name("Xz")),
        ("xz", Name("Xz short")),
        ("zstd", Name("Zstd")),
        ("zst", Name("Zstd short")),
    ],
)
@Requirements(RQ_SRS_015_S3_TableFunction_Compression_Auto("1.0"))
def auto(self, compression_method):
    """Check that ClickHouse can successfully use 'auto' as the input to the
    compression parameter of the S3 table function to interpret files compressed
    using the supported compression methods.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node
    expected = "427"

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the first table {name_table1}"):
            node.query(f"INSERT INTO {name_table1} VALUES (427)")

        with When(
            f"""I export the data to S3 using the table function with compression
                  parameter set to '{compression_method}'"""
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}auto.{compression_method}', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64', '{compression_method}')
                SELECT * FROM {name_table1}"""
            )

        with And(
            f"""I import the data from S3 into the second table {name_table2}
                  using the table function with compression parameter set to 'auto'"""
        ):
            node.query(
                f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}auto.{compression_method}', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64', 'auto')""",
            )

        with Then(
            f"""I check that a simple SELECT * query on the second table
                   {name_table2} returns matching data"""
        ):
            r = node.query(f"SELECT * FROM {name_table2} FORMAT CSV").output.strip()
            assert r == expected, error()

    finally:
        with Finally("I overwrite the S3 data with empty data"):
            with By(f"I drop the first table {name_table1}"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And(f"I create the table again {name_table1}"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d"""
                )

            with And(
                f"""I export the empty table {name_table1} to S3 at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}auto.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Credentials("1.0"))
def credentials(self):
    """Check that ClickHouse can import and export data from an S3 bucket
    when proper authentication credentials are provided.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node
    expected = "427"

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the first table {name_table1}"):
            for attempt in retries(timeout=600, delay=5):
                with attempt:
                    node.query(f"INSERT INTO {name_table1} VALUES (427)")

        with When("I export the data to S3 using the table function"):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}credentials.csv', '{access_key_id}', '{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}"""
            )

        with And(f"I import the data from S3 into the second table {name_table2}"):
            node.query(
                f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}credentials.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')"""
            )

        with Then(
            f"""I check that a simple SELECT * query on the second table
                   {name_table2} returns matching data"""
        ):
            r = node.query(f"SELECT * FROM {name_table2} FORMAT CSV").output.strip()
            assert r == expected, error()

    finally:
        with Finally("I overwrite the S3 data with empty data"):
            with By(f"I drop the first table {name_table1}"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And(f"I create the table again {name_table1}"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d"""
                )

            with And(
                f"""I export the empty table {name_table1} to S3 at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}credentials.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_Settings_PartitionBy("1.0"))
def partition(self):
    """Check that ClickHouse can export paritioned data."""
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node

    with When("I export the data to S3 using the table function"):
        sql = (
            f"INSERT INTO FUNCTION s3('{uri}_partition_export_"
            + "{_partition_id}.csv'"
            + f", '{access_key_id}','{secret_access_key}', 'CSV', 'a String') PARTITION BY a VALUES ('x'),('y'),('z')"
        )
        node.query(sql)

    for partition_id in ["x", "y", "z"]:
        with Then(f"I check the data in the {partition_id} partition"):
            output = node.query(
                f"""SELECT * FROM
                s3('{uri}_partition_export_{partition_id}.csv', '{access_key_id}','{secret_access_key}', 'CSV', 'a String')"""
            ).output
            assert output == partition_id, error()


@TestScenario
@Requirements()
def multiple_columns(self):
    """Check that storage works properly when a table with multiple columns
    is imported and exported.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64,
                    a String,
                    b Int8
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64,
                    a String,
                    b Int8
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with When("I add data to the table"):
            node.query(f"INSERT INTO {name_table1} (d,a,b) VALUES (1,'Dog',0)")
            node.query(f"INSERT INTO {name_table1} (d,a,b) VALUES (2,'Cat',7)")
            node.query(f"INSERT INTO {name_table1} (d,a,b) VALUES (3,'Horse',12)")

        with When("I export the data to external storage using the table function"):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}multiple_columns.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64, a String, b Int8')
                SELECT * FROM {name_table1}"""
            )

        with And(
            f"I import the data from external storage into the second table {name_table2}"
        ):
            node.query(
                f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}multiple_columns.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64, a String, b Int8')"""
            )

        with Then("I check a count query"):
            r = node.query(f"SELECT COUNT(*) FROM {name_table2}").output.strip()
            assert r == "3", error()

        with And("I check a select * query"):
            r = node.query(f"SELECT * FROM {name_table2}").output.strip()
            assert r == "1\tDog\t0\n2\tCat\t7\n3\tHorse\t12", error()

        with And("I check a query selecting one row"):
            r = node.query(f"SELECT d,a,b FROM {name_table2} WHERE d=3").output.strip()
            assert r == "3\tHorse\t12", error()

    finally:
        with Finally("I overwrite the data with empty data"):
            with By(f"I drop the first table {name_table1}"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And(f"I create the table again {name_table1}"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d"""
                )

            with And(
                f"""I export the empty table {name_table1} at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}multiple_columns.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestOutline(Scenario)
@Examples("fmt", [("ORC", Name("ORC")), ("PARQUET", Name("Parquet"))])
@Requirements(RQ_SRS_015_S3_TableFunction_Format("1.0"))
def data_format(self, fmt):
    """Check that ClickHouse can import and export data with ORC and Parquet
    data formats.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with When("I add data to the table"):
            with By("first inserting 1MB of data"):
                insert_data(name=name_table1, number_of_mb=1)

            with And("another insert of 1MB of data"):
                insert_data(name=name_table1, number_of_mb=1, start=1024 * 1024)

            with And("then doing a large insert of 10Mb of data"):
                insert_data(name=name_table1, number_of_mb=10, start=1024 * 1024 * 2)

        with When(
            f"I export the data to external storage using the table function with {fmt} data format"
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}data_format.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1} FORMAT {fmt}"""
            )

        with And(
            f"I import the data from external storage into the second table {name_table2} with {fmt} data format"
        ):
            node.query(
                f"""
                INSERT INTO {name_table2} SELECT * FROM
                s3('{uri}data_format.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64') FORMAT {fmt}"""
            )

        with Then("I check simple queries"):
            check_query(
                num=0, query=f"SELECT COUNT() FROM {name_table2}", expected="1572867"
            )
            check_query(
                num=1,
                query=f"SELECT uniqExact(d) FROM {name_table2} WHERE d < 10",
                expected="10",
            )
            check_query(
                num=2,
                query=f"SELECT d FROM {name_table2} ORDER BY d DESC LIMIT 1",
                expected="3407872",
            )
            check_query(
                num=3,
                query=f"SELECT d FROM {name_table2} ORDER BY d ASC LIMIT 1",
                expected="0",
            )
            check_query(
                num=4,
                query=f"SELECT * FROM {name_table2} WHERE d == 0 OR d == 1048578 OR d == 2097154 ORDER BY d",
                expected="0\n1048578\n2097154",
            )
            check_query(
                num=5,
                query=f"SELECT * FROM (SELECT d FROM {name_table2} WHERE d == 1)",
                expected="1",
            )

    finally:
        with Finally("I overwrite the data with empty data"):
            with By(f"I drop the first table {name_table1}"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And(f"I create the table again {name_table1}"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d"""
                )

            with And(
                f"""I export the empty table {name_table1} at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}data_format.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestScenario
@Requirements()
def multipart(self):
    """Check that storage works correctly when uploads and downloads use
    multiple parts.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node

    try:
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with When("I add data to the table"):
            with By("first inserting 1MB of data"):
                insert_data(name=name_table1, number_of_mb=1)

            with And("another insert of 1MB of data"):
                insert_data(name=name_table1, number_of_mb=1, start=1024 * 1024)

            with And("then doing a large insert of 10Mb of data"):
                insert_data(name=name_table1, number_of_mb=10, start=1024 * 1024 * 2)

        with change_max_single_part_upload_size(node=node, size=5):
            with When("I export the data using the table function"):
                node.query(
                    f"""
                    INSERT INTO FUNCTION
                    s3('{uri}multipart.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                    SELECT * FROM {name_table1}"""
                )

            with And(f"I import the data into the second table {name_table2}"):
                node.query(
                    f"""
                    INSERT INTO {name_table2} SELECT * FROM
                    s3('{uri}multipart.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')"""
                )

        with Then("I check simple queries"):
            check_query(
                num=0, query=f"SELECT COUNT() FROM {name_table2}", expected="1572867"
            )
            check_query(
                num=1,
                query=f"SELECT uniqExact(d) FROM {name_table2} WHERE d < 10",
                expected="10",
            )
            check_query(
                num=2,
                query=f"SELECT d FROM {name_table2} ORDER BY d DESC LIMIT 1",
                expected="3407872",
            )
            check_query(
                num=3,
                query=f"SELECT d FROM {name_table2} ORDER BY d ASC LIMIT 1",
                expected="0",
            )
            check_query(
                num=4,
                query=f"SELECT * FROM {name_table2} WHERE d == 0 OR d == 1048578 OR d == 2097154 ORDER BY d",
                expected="0\n1048578\n2097154",
            )
            check_query(
                num=5,
                query=f"SELECT * FROM (SELECT d FROM {name_table2} WHERE d == 1)",
                expected="1",
            )

    finally:
        with Finally("I overwrite the data with empty data"):
            with By(f"I drop the first table {name_table1}"):
                node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

            with And(f"I create the table again {name_table1}"):
                node.query(
                    f"""
                    CREATE TABLE {name_table1} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d"""
                )

            with And(
                f"""I export the empty table {name_table1} at the
                      location where I want to overwrite data"""
            ):
                node.query(
                    f"""
                        INSERT INTO FUNCTION
                        s3('{uri}multipart.csv', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                        SELECT * FROM {name_table1}"""
                )

        with Finally(f"I drop the first table {name_table1}"):
            node.query(f"DROP TABLE IF EXISTS {name_table1} SYNC")

        with And(f"I drop the second table {name_table2}"):
            node.query(f"DROP TABLE IF EXISTS {name_table2} SYNC")


@TestScenario
@Requirements(RQ_SRS_015_S3_RemoteHostFilter("1.0"))
def remote_host_filter(self):
    """Check that the remote host filter can be used to block access to
    bucket URLs provided in the S3 table function.
    """
    name_table1 = "table_" + getuid()
    name_table2 = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node
    expected = "427"
    urls = None

    with Given("I have a list of urls to allow access"):
        urls = {"host_regexp": "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}$"}

    with remote_host_filter_config(urls=urls, restart=True):
        with Given("I create a table"):
            node.query(
                f"""
                CREATE TABLE {name_table1} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And("I create a second table for comparison"):
            node.query(
                f"""
                CREATE TABLE {name_table2} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d"""
            )

        with And(f"I store simple data in the first table {name_table1}"):
            node.query(f"INSERT INTO {name_table1} VALUES (427)")

        with When(
            """I export the data to S3 using the table function,
                  expecting failure"""
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {name_table1}""",
                message=f'DB::Exception: URL "{uri}" is not allowed',
            )


@TestOutline(Feature)
@Requirements(RQ_SRS_015_S3_TableFunction("1.0"))
def outline(self):
    """Test S3 and S3 compatible storage through storage disks."""
    for scenario in loads(current_module(), Scenario):
        with allow_s3_truncate(self.context.node):
            scenario()


@TestFeature
def ssec_encryption_check(self):
    """Check that S3 encrypts files when SSEC option is enabled."""
    node = current().context.node
    name = f"table_{getuid()}"

    with allow_s3_truncate(self.context.node):
        with Given("I have a table"):
            simple_table(name=name, policy="default")

        with And("I insert 1MB of data"):
            node.query(f"INSERT INTO {name} VALUES (1),(2),(3),(4),(5),(6)")

        with When("I insert not encrypted data"):
            node.query(
                f"""
                    INSERT INTO FUNCTION
                    file('not_encrypted.csv', 'CSV', 'd UInt64')
                    SELECT * FROM {name} """
            )

        with Then("I define S3 SSEC option"):
            add_ssec_s3_option()

        with And("I define S3 endpoint configuration"):
            endpoints = {
                "s3-bucket": {
                    "endpoint": f"{self.context.uri}",
                    "access_key_id": f"{self.context.access_key_id}",
                    "secret_access_key": f"{self.context.secret_access_key}",
                }
            }

            endpoints["s3-bucket"].update(self.context.s3_options)

        with s3_endpoints(endpoints):
            with When("I insert encrypted data"):
                for attempt in retries(timeout=1500):
                    with attempt:
                        node.query(
                            f"""
                                INSERT INTO FUNCTION
                                s3('{self.context.uri}encrypted.csv', '{self.context.access_key_id}','{self.context.secret_access_key}', 'CSV', 'd UInt64')
                                SELECT * FROM {name}"""
                        )

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.context.access_key_id,
                aws_secret_access_key=self.context.secret_access_key,
            )
            with And("I copy the encrypted file"):
                s3_client.download_file(
                    "altinity-qa-test", "data/encrypted.csv", "encrypted.csv"
                )
                x = self.context.cluster.command(
                    None, "docker ps | grep clickhouse1 | cut -d ' ' -f 1 | head -n 1"
                ).output
                self.context.cluster.command(
                    None,
                    f"docker cp encrypted.csv {x}:/var/lib/clickhouse/user_files/encrypted.csv",
                )

            with When("I take the md5sum of the two files"):
                unencrypted_sum = node.command(
                    "md5sum /var/lib/clickhouse/user_files/not_encrypted.csv"
                ).output.split(" ")[0]
                encrypted_sum = node.command(
                    "md5sum /var/lib/clickhouse/user_files/encrypted.csv"
                ).output.split(" ")[0]

            with Then("I assert they are different"):
                assert unencrypted_sum != encrypted_sum, error()

            with And("I double check the encrypted file"):
                output = node.command(
                    "cat /var/lib/clickhouse/user_files/encrypted.csv"
                ).output
                assert "1\n2\n3\n4\n5\n6\n" not in output, error()


@TestFeature
@Requirements(
    RQ_SRS_015_S3_AWS_SSEC("1.0"),
)
@Name("ssec")
def ssec(self):
    """Check S3 table function with SSEC option enabled."""

    with Given("I define S3 SSEC option"):
        add_ssec_s3_option()

    with And("I define S3 endpoint configuration"):
        endpoints = {
            "s3-bucket": {
                "endpoint": f"{self.context.uri}",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            }
        }

        endpoints["s3-bucket"].update(self.context.s3_options)

    with s3_endpoints(endpoints):
        outline()


@TestFeature
@Requirements(RQ_SRS_015_S3_AWS_TableFunction("1.0"))
@Name("aws s3 table function")
def aws_s3(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "aws_s3"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    outline()

    Feature(run=ssec_encryption_check)
    Feature(run=ssec)


@TestFeature
@Requirements(RQ_SRS_015_S3_GCS_TableFunction("1.0"))
@Name("gcs table function")
def gcs(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "gcs"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    outline()


@TestFeature
@Requirements(RQ_SRS_015_S3_MinIO_TableFunction("1.0"))
@Name("minio table function")
def minio(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "minio"
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    outline()
