import boto3
from testflows.core import *

from s3.tests.common import *
from s3.requirements import *
from testflows.combinatorics import product


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_S3_Syntax("1.0"))
def syntax(self):
    """Check that S3 storage works correctly for both imports and exports
    when accessed using a table function.
    """
    table1_name = "table_" + getuid()
    table2_name = "table_" + getuid()
    node = current().context.node
    expected = "427"

    with Given("I create a table"):
        simple_table(node=node, name=table1_name, policy="default")

    with And("I create a second table for comparison"):
        simple_table(node=node, name=table2_name, policy="default")

    with And(f"I store simple data in the first table {table1_name}"):
        node.query(f"INSERT INTO {table1_name} VALUES (427)")

    with When(f"I export the data to S3 using the table function"):
        insert_to_s3_function(filename="syntax.csv", table_name=table1_name)

    with And(f"I import the data from S3 into the second table {table2_name}"):
        insert_from_s3_function(filename="syntax.csv", table_name=table2_name)

    with Then(
        f"""I check that a simple SELECT * query on the second table
                {table2_name} returns matching data"""
    ):
        r = node.query(f"SELECT * FROM {table2_name} FORMAT CSV").output.strip()
        assert r == expected, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path_Glob("1.0"))
def syntax_s3Cluster(self):
    """Check that S3 storage works correctly for exports
    when accessed using an s3Cluster table function.
    """
    node = current().context.node
    expected = "427"

    for cluster_name in self.context.clusters:
        with Combination(f"cluster_name = {cluster_name}"):
            table1_name = "table_" + getuid()
            table2_name = "table_" + getuid()
            with Given("I create a table"):
                simple_table(node=node, name=table1_name, policy="default")

            with And("I create a second table for comparison"):
                distributed_table_cluster(
                    table_name=table2_name,
                    cluster_name=cluster_name,
                    columns="d UInt64",
                )

            with And(f"I store simple data in the first table {table1_name}"):
                node.query(f"INSERT INTO {table1_name} VALUES (427)")

            with When(f"I export the data to S3 using the table function"):
                insert_to_s3_function(
                    filename=f"syntax_{cluster_name}.csv", table_name=table1_name
                )

            with And(f"I import the data from S3 into the second table {table2_name}"):
                insert_from_s3_function(
                    filename=f"syntax_{cluster_name}.csv",
                    cluster_name=cluster_name,
                    table_name=table2_name,
                )

            for attempt in retries(timeout=30, delay=5):
                with attempt:
                    with Then(
                        f"""I check that a simple SELECT * query on the second table
                                {table2_name} returns matching data"""
                    ):
                        r = (
                            self.context.cluster.node("clickhouse1")
                            .query(f"SELECT * FROM {table2_name} FORMAT CSV")
                            .output.strip()
                        )
                        assert r == expected, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Path_Glob("1.0"))
def wildcard(self):
    """
    Check that imports from S3 storage using the S3 table function and s3Cluster table function
    work correctly when using wildcards in the path.
    """
    node = current().context.node

    test_values = {
        ("*", "427\n427\n427\n427"),
        ("%3F", "427\n427\n427"),
        ("{2..3}", "427\n427"),
        ("{1,3}", "427\n427"),
        ("{1,3,4}", "427\n427"),
    }

    test_clusters = {None}.union(set(self.context.clusters))

    for i, combination in enumerate(product(test_values, test_clusters)):
        with Combination(
            f"test_values = {combination[0]}, cluster_name = {combination[1]}"
        ):
            table1_name = "table_" + getuid()
            table2_name = "table_" + getuid()
            wildcard, expected = combination[0]
            cluster_name = combination[1]

            if self.context.storage == "minio":
                with Given(
                    "If using MinIO, clear objects on directory path to avoid error"
                ):
                    self.context.cluster.minio_client.remove_object(
                        self.context.cluster.minio_bucket, "data"
                    )

            with Given("I create a table"):
                simple_table(node=node, name=table1_name, policy="default")

            with And("I create a second table for comparison"):
                if cluster_name is None:
                    simple_table(node=node, name=table2_name, policy="default")
                else:
                    distributed_table_cluster(
                        table_name=table2_name,
                        cluster_name=cluster_name,
                        columns="d UInt64",
                    )

            with And(f"I store simple data in the first table {table1_name}"):
                node.query(f"INSERT INTO {table1_name} VALUES (427)")

            with When("I export the data to S3 using the table function"):
                insert_to_s3_function(filename="subdata", table_name=table1_name)

            with And("I export the data to a different path in my bucket"):
                insert_to_s3_function(filename="subdata1", table_name=table1_name)

            with And("I export the data to a different path in my bucket"):
                insert_to_s3_function(filename="subdata2", table_name=table1_name)

            with And("I export the data to yet another path in my bucket"):
                insert_to_s3_function(filename="subdata3", table_name=table1_name)

            with And(
                f"""I import the data from external storage into the second
                        table {table2_name} using the wildcard '{wildcard}'"""
            ):
                if wildcard == "{1,3,4}":
                    r = insert_from_s3_function(
                        filename=f"subdata{wildcard}",
                        table_name=table2_name,
                        cluster_name=cluster_name,
                        no_checks=True,
                    )
                else:
                    r = insert_from_s3_function(
                        filename=f"subdata{wildcard}",
                        table_name=table2_name,
                        cluster_name=cluster_name,
                    )

            if r.exitcode == 0:
                with Then(
                    f"""I check that a simple SELECT * query on the second table
                            {table2_name} returns expected data"""
                ):
                    for attempt in retries(timeout=600, delay=5):
                        with attempt:
                            if cluster_name is None:
                                r = node.query(
                                    f"SELECT * FROM {table2_name} FORMAT TabSeparated"
                                ).output.strip()
                            else:
                                r = (
                                    self.context.cluster.node("clickhouse1")
                                    .query(
                                        f"SELECT * FROM {table2_name} FORMAT TabSeparated"
                                    )
                                    .output.strip()
                                )

                            assert r == expected, error()
            else:
                assert "Failed to get object info" in r.output, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Compression("1.0"))
def compression(self):
    """Check that ClickHouse can successfully use all supported compression
    methods for the S3 and s3Cluster table functions.
    """

    node = current().context.node
    expected = "427"

    compression_methods = {
        "gzip",
        "gz",
        "deflate",
        "brotli",
        "br",
        "LZMA",
        "xz",
        "zstd",
        "zst",
    }

    test_clusters = {None}.union(set(self.context.clusters))

    for compression_method, cluster_name in product(compression_methods, test_clusters):
        with Combination(
            f"compression_method = {compression_method}, cluster_name = {cluster_name}"
        ):
            table1_name = "table_" + getuid()
            table2_name = "table_" + getuid()
            with Given("I create a table"):
                simple_table(node=node, name=table1_name, policy="default")

            with And("I create a second table for comparison"):
                if cluster_name is None:
                    simple_table(node=node, name=table2_name, policy="default")
                else:
                    distributed_table_cluster(
                        table_name=table2_name,
                        cluster_name=cluster_name,
                        columns="d UInt64",
                    )

            with And(f"I store simple data in the first table {table1_name}"):
                node.query(f"INSERT INTO {table1_name} VALUES (427)")

            with When(
                f"""I export the data to S3 using the table function with compression
                        parameter set to '{compression_method}'"""
            ):
                insert_to_s3_function(
                    filename=f"compression_{compression_method}.csv",
                    table_name=table1_name,
                    compression=compression_method,
                )

            with And(
                f"""I import the data from S3 into the second table {table2_name}
                        using the table function with compression parameter set to '{compression_method}'"""
            ):
                insert_from_s3_function(
                    filename=f"compression_{compression_method}.csv",
                    table_name=table2_name,
                    compression=compression_method,
                    cluster_name=cluster_name,
                )

            with Then(
                f"""I check that a simple SELECT * query on the second table
                        {table2_name} returns matching data"""
            ):
                if cluster_name is None:
                    r = node.query(
                        f"SELECT * FROM {table2_name} FORMAT CSV"
                    ).output.strip()
                    assert r == expected, error()
                else:
                    for attempt in retries(timeout=600, delay=5):
                        with attempt:
                            r = (
                                self.context.cluster.node("clickhouse1")
                                .query(f"SELECT * FROM {table2_name} FORMAT CSV")
                                .output.strip()
                            )
                            assert r == expected, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Compression_Auto("1.0"))
def auto(self):
    """Check that ClickHouse can successfully use 'auto' as the input to the
    compression parameter of the S3 and s3Cluster table functions to interpret files compressed
    using the supported compression methods.
    """
    node = current().context.node
    expected = "427"

    compression_methods = {
        "gzip",
        "gz",
        "deflate",
        "brotli",
        "br",
        "LZMA",
        "xz",
        "zstd",
        "zst",
    }

    test_clusters = {None}.union(set(self.context.clusters))

    for compression_method, cluster_name in product(compression_methods, test_clusters):
        with Combination(
            f"compression_method = {compression_method}, cluster_name = {cluster_name}"
        ):
            table1_name = "table_" + getuid()
            table2_name = "table_" + getuid()
            with Given("I create a table"):
                simple_table(node=node, name=table1_name, policy="default")

            with And("I create a second table for comparison"):
                if cluster_name is None:
                    simple_table(node=node, name=table2_name, policy="default")
                else:
                    distributed_table_cluster(
                        table_name=table2_name,
                        cluster_name=cluster_name,
                        columns="d UInt64",
                    )

            with And(f"I store simple data in the first table {table1_name}"):
                node.query(f"INSERT INTO {table1_name} VALUES (427)")

            with When(
                f"""I export the data to S3 using the table function with compression
                        parameter set to '{compression_method}'"""
            ):
                insert_to_s3_function(
                    filename=f"auto.{compression_method}",
                    table_name=table1_name,
                    compression=compression_method,
                )

            with And(
                f"""I import the data from S3 into the second table {table2_name}
                        using the table function with compression parameter set to 'auto'"""
            ):
                insert_from_s3_function(
                    filename=f"auto.{compression_method}",
                    table_name=table2_name,
                    compression="auto",
                    cluster_name=cluster_name,
                )

            with Then(
                f"""I check that a simple SELECT * query on the second table
                        {table2_name} returns matching data"""
            ):
                if cluster_name is None:
                    r = node.query(
                        f"SELECT * FROM {table2_name} FORMAT CSV"
                    ).output.strip()
                    assert r == expected, error()
                else:
                    for attempt in retries(timeout=600, delay=5):
                        with attempt:
                            r = (
                                self.context.cluster.node("clickhouse1")
                                .query(f"SELECT * FROM {table2_name} FORMAT CSV")
                                .output.strip()
                            )
                            assert r == expected, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Credentials("1.0"))
def credentials(self):
    """Check that ClickHouse can import and export data from an S3 bucket
    when proper authentication credentials are provided.
    """
    table1_name = "table_" + getuid()
    table2_name = "table_" + getuid()
    node = current().context.node
    expected = "427"

    with Given("I create a table"):
        simple_table(node=node, name=table1_name, policy="default")

    with And("I create a second table for comparison"):
        simple_table(node=node, name=table2_name, policy="default")

    with And(f"I store simple data in the first table {table1_name}"):
        for attempt in retries(timeout=600, delay=5):
            with attempt:
                node.query(f"INSERT INTO {table1_name} VALUES (427)")

    with When("I export the data to S3 using the table function"):
        insert_to_s3_function(filename="credentials.csv", table_name=table1_name)

    with And(f"I import the data from S3 into the second table {table2_name}"):
        insert_from_s3_function(filename="credentials.csv", table_name=table2_name)

    with Then(
        f"""I check that a simple SELECT * query on the second table
                {table2_name} returns matching data"""
    ):
        r = node.query(f"SELECT * FROM {table2_name} FORMAT CSV").output.strip()
        assert r == expected, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Credentials("1.0"))
def credentials_s3Cluster(self):
    """Check that ClickHouse can import and export data from an S3 bucket
    when proper authentication credentials are provided using s3Cluster table function.
    """
    node = current().context.node
    expected = "427"

    for cluster_name in self.context.clusters:
        with Combination(f"cluster_name = {cluster_name}"):
            table1_name = "table_" + getuid()
            table2_name = "table_" + getuid()
            with Given("I create a table"):
                simple_table(node=node, name=table1_name, policy="default")

            with And("I create a second table for comparison"):
                distributed_table_cluster(
                    table_name=table2_name,
                    cluster_name=cluster_name,
                    columns="d UInt64",
                )

            with And(f"I store simple data in the first table {table1_name}"):
                for attempt in retries(timeout=600, delay=5):
                    with attempt:
                        node.query(f"INSERT INTO {table1_name} VALUES (427)")

            with When("I export the data to S3 using the table function"):
                insert_to_s3_function(
                    filename="credentials.csv", table_name=table1_name
                )

            with And(f"I import the data from S3 into the second table {table2_name}"):
                insert_from_s3_function(
                    filename="credentials.csv",
                    table_name=table2_name,
                    cluster_name=cluster_name,
                )

            for attempt in retries(timeout=30, delay=5):
                with attempt:
                    with Then(
                        f"""I check that a simple SELECT * query on the second table
                                {table2_name} returns matching data"""
                    ):
                        r = (
                            self.context.cluster.node("clickhouse1")
                            .query(f"SELECT * FROM {table2_name} FORMAT CSV")
                            .output.strip()
                        )
                        assert r == expected, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_Settings_PartitionBy("1.0"))
def partition(self):
    """Check that ClickHouse can export partitioned data."""
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
                s3('{uri}_partition_export_{partition_id}.csv', '{access_key_id}','{secret_access_key}', 'CSV', 'a String') FORMAT TabSeparated"""
            ).output
            assert output == partition_id, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_Settings_PartitionBy("1.0"))
def partition_s3Cluster(self):
    """Check that ClickHouse can export partitioned data using s3Cluster table function."""
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node

    for cluster_name in self.context.clusters:
        with Combination(f"cluster_name = {cluster_name}"):
            with When("I export the data to S3 using the table function"):
                sql = (
                    f"INSERT INTO FUNCTION s3('{uri}_partition_export_"
                    + "{_partition_id}.csv'"
                    + f", '{access_key_id}','{secret_access_key}', 'CSV', 'a String') PARTITION BY a VALUES ('x'),('y'),('z')"
                )
                node.query(sql)

            for partition_id in ["x", "y", "z"]:
                with Then(f"I check the data in the {partition_id} partition"):
                    for attempt in retries(timeout=30, delay=5):
                        with attempt:
                            output = (
                                self.context.cluster.node("clickhouse1")
                                .query(
                                    f"""SELECT * FROM
                                s3Cluster('{cluster_name}', '{uri}_partition_export_{partition_id}.csv', '{access_key_id}','{secret_access_key}', 'CSV', 'a String') FORMAT TabSeparated"""
                                )
                                .output
                            )
                            assert output == partition_id, error()


@TestScenario
@Requirements()
def multiple_columns(self):
    """Check that storage works properly when a table with multiple columns
    is imported and exported.
    """
    table1_name = "table_" + getuid()
    table2_name = "table_" + getuid()
    node = current().context.node

    with Given("I create a table"):
        simple_table(
            node=node,
            name=table1_name,
            policy="default",
            columns="d UInt64, a String, b Int8",
        )

    with And("I create a second table for comparison"):
        simple_table(
            node=node,
            name=table2_name,
            policy="default",
            columns="d UInt64, a String, b Int8",
        )

    with When("I add data to the table"):
        node.query(f"INSERT INTO {table1_name} (d,a,b) VALUES (1,'Dog',0)")
        node.query(f"INSERT INTO {table1_name} (d,a,b) VALUES (2,'Cat',7)")
        node.query(f"INSERT INTO {table1_name} (d,a,b) VALUES (3,'Horse',12)")

    with When("I export the data to external storage using the table function"):
        insert_to_s3_function(
            filename="multiple_columns.csv",
            table_name=table1_name,
            columns="d UInt64, a String, b Int8",
        )

    with And(
        f"I import the data from external storage into the second table {table2_name}"
    ):
        insert_from_s3_function(
            filename="multiple_columns.csv",
            table_name=table2_name,
            columns="d UInt64, a String, b Int8",
        )

    with Then("I check a count query"):
        r = node.query(
            f"SELECT COUNT(*) FROM {table2_name} FORMAT TabSeparated"
        ).output.strip()
        assert r == "3", error()

    with And("I check a select * query"):
        r = node.query(
            f"SELECT * FROM {table2_name} FORMAT TabSeparated"
        ).output.strip()
        assert r == "1\tDog\t0\n2\tCat\t7\n3\tHorse\t12", error()

    with And("I check a query selecting one row"):
        r = node.query(
            f"SELECT d,a,b FROM {table2_name} WHERE d=3 FORMAT TabSeparated"
        ).output.strip()
        assert r == "3\tHorse\t12", error()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_Format("1.0"))
def data_format(self):
    """Check that ClickHouse can import and export data with ORC and Parquet
    data formats.
    """
    node = current().context.node

    test_values = {
        "ORC",
        "PARQUET",
    }
    test_clusters = {None}.union(set(self.context.clusters))

    for fmt, cluster_name in product(test_values, test_clusters):
        with Combination(f"fmt = {fmt}, cluster_name = {cluster_name}"):
            table1_name = "table_" + getuid()
            table2_name = "table_" + getuid()
            with Given("I create a table"):
                simple_table(node=node, name=table1_name, policy="default")

            with And("I create a second table for comparison"):
                if cluster_name is None:
                    simple_table(node=node, name=table2_name, policy="default")
                else:
                    distributed_table_cluster(
                        table_name=table2_name,
                        cluster_name=cluster_name,
                        columns="d UInt64",
                    )

            with When("I add data to the table"):
                standard_inserts(node=node, table_name=table1_name)

            with When(
                f"I export the data to external storage using the table function with {fmt} data format"
            ):
                insert_to_s3_function(
                    filename="data_format.csv", table_name=table1_name, fmt=fmt
                )

            with And(
                f"I import the data from external storage into the second table {table2_name} with {fmt} data format"
            ):
                insert_from_s3_function(
                    filename="data_format.csv",
                    table_name=table2_name,
                    fmt=fmt,
                    cluster_name=cluster_name,
                )

            with Then("I check simple queries"):
                for attempt in retries(timeout=10, delay=1):
                    with attempt:
                        standard_selects(
                            node=self.context.cluster.node("clickhouse1"),
                            table_name=table2_name,
                        )


@TestScenario
@Requirements()
def multipart(self):
    """Check that storage works correctly when uploads and downloads use
    multiple parts.
    """
    table1_name = "table_" + getuid()
    table2_name = "table_" + getuid()
    node = current().context.node

    with Given("I create a table"):
        simple_table(node=node, name=table1_name, policy="default")

    with And("I create a second table for comparison"):
        simple_table(node=node, name=table2_name, policy="default")

    with When("I add data to the table"):
        standard_inserts(node=node, table_name=table1_name)

    with change_max_single_part_upload_size(node=node, size=5):
        with When("I export the data using the table function"):
            insert_to_s3_function(filename="multipart.csv", table_name=table1_name)

        with And(f"I import the data into the second table {table2_name}"):
            insert_from_s3_function(filename="multipart.csv", table_name=table2_name)

    with Then("I check simple queries"):
        standard_selects(node=node, table_name=table2_name)


@TestScenario
@Requirements(RQ_SRS_015_S3_RemoteHostFilter("1.0"))
def remote_host_filter(self):
    """Check that the remote host filter can be used to block access to
    bucket URLs provided in the S3 table function.
    """
    table1_name = "table_" + getuid()
    table2_name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    node = current().context.node
    expected = "427"
    urls = None

    with Given("I have a list of urls to allow access"):
        urls = {"host_regexp": r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}$"}

    with remote_host_filter_config(urls=urls, restart=True):
        with Given("I create a table"):
            simple_table(node=node, name=table1_name, policy="default")

        with And("I create a second table for comparison"):
            simple_table(node=node, name=table2_name, policy="default")

        with And(f"I store simple data in the first table {table1_name}"):
            node.query(f"INSERT INTO {table1_name} VALUES (427)")

        with When(
            """I export the data to S3 using the table function,
                  expecting failure"""
        ):
            node.query(
                f"""
                INSERT INTO FUNCTION
                s3('{uri}', '{access_key_id}','{secret_access_key}', 'CSVWithNames', 'd UInt64')
                SELECT * FROM {table1_name}""",
                message=f'DB::Exception: URL "{uri}" is not allowed',
            )


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_MeasureFileSize("1.0"))
def measure_file_size(self):

    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    table1_name = "table_" + getuid()
    uri = self.context.uri + "measure-file-size/"
    bucket_path = self.context.bucket_path + "/measure-file-size"

    node = current().context.node

    with Given("I get the size of the s3 bucket before adding data"):
        size_before = measure_buckets_before_and_after(bucket_prefix=bucket_path)

    with And("I create a table"):
        simple_table(node=node, name=table1_name, policy="default")

    with When("I add data to the table"):
        standard_inserts(node=node, table_name=table1_name)

    with And(f"I export the data to S3 using the table function"):
        insert_to_s3_function(
            filename="measure_me.csv",
            table_name=table1_name,
            uri=uri,
        )

    with And("I get the size of the s3 bucket after adding data"):
        size_after = get_stable_bucket_size(prefix=bucket_path, delay=20)

    with Then("I compare the size that clickhouse reports"):
        r = node.query(
            f"SELECT sum(_size) FROM s3('{uri}**', '{access_key_id}','{secret_access_key}', 'One') FORMAT TSV"
        )

        for retry in retries(timeout=30, delay=5):
            with retry:
                size_clickhouse = int(r.output.strip())
                assert size_after - size_before == size_clickhouse, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_MeasureFileSize("1.0"))
def measure_file_size_s3Cluster(self):
    """Check that ClickHouse can measure file size using s3Cluster table function."""
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    table1_name = "table_" + getuid()
    uri = self.context.uri + "measure-file-size/"
    bucket_path = self.context.bucket_path + "/measure-file-size"

    for cluster_name in self.context.clusters:
        with Combination(f"cluster_name = {cluster_name}"):
            node = current().context.node

            with Given("I get the size of the s3 bucket before adding data"):
                size_before = measure_buckets_before_and_after(
                    bucket_prefix=bucket_path
                )

            with And("I create a table"):
                simple_table(node=node, name=table1_name, policy="default")

            with When("I add data to the table"):
                standard_inserts(node=node, table_name=table1_name)

            with And(f"I export the data to S3 using the table function"):
                insert_to_s3_function(
                    filename="measure_me.csv",
                    table_name=table1_name,
                    uri=uri,
                )

            with And("I get the size of the s3 bucket after adding data"):
                size_after = get_stable_bucket_size(prefix=bucket_path, delay=20)

            with Then("I compare the size that clickhouse reports"):
                for attempt in retries(timeout=10, delay=1):
                    with attempt:
                        r = node.query(
                            f"SELECT sum(_size) FROM s3Cluster('{cluster_name}', '{uri}**', '{access_key_id}','{secret_access_key}', 'One') FORMAT TSV"
                        )
                        size_clickhouse = int(r.output.strip())
                        debug(
                            f"size_after: {size_after}, size_before: {size_before}, size_clickhouse: {size_clickhouse}"
                        )
                        assert size_after - size_before == size_clickhouse, error()


@TestOutline(Feature)
@Requirements(
    RQ_SRS_015_S3_TableFunction_S3("1.0"), RQ_SRS_015_S3_TableFunction_S3Cluster("1.0")
)
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
                    self.context.uri, "data/encrypted.csv", "encrypted.csv"
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
        outline(uri=self.context.uri)


@TestFeature
@Requirements(RQ_SRS_015_S3_AWS_TableFunction("1.0"))
@Name("table function")
def aws_s3(self, uri, bucket_prefix):

    with Given("a temporary s3 path"):
        temp_s3_path = temporary_bucket_path(
            bucket_prefix=f"{bucket_prefix}/table_function"
        )

        self.context.uri = f"{uri}table_function/{temp_s3_path}/"
        self.context.bucket_path = f"{bucket_prefix}/table_function/{temp_s3_path}"

    outline()

    Feature(run=ssec_encryption_check)
    Feature(test=ssec)


@TestFeature
@Requirements(RQ_SRS_015_S3_GCS_TableFunction("1.0"))
@Name("table function")
def gcs(self, uri, bucket_prefix):

    with Given("a temporary s3 path"):
        temp_s3_path = temporary_bucket_path(
            bucket_prefix=f"{bucket_prefix}/table_function"
        )

        self.context.uri = f"{uri}table_function/{temp_s3_path}/"
        self.context.bucket_path = f"{bucket_prefix}/table_function/{temp_s3_path}"

    outline()


@TestFeature
@Requirements(RQ_SRS_015_S3_MinIO_TableFunction("1.0"))
@Name("table function")
def minio(self, uri, bucket_prefix):

    with Given("a temporary s3 path"):
        temp_s3_path = temporary_bucket_path(
            bucket_prefix=f"{bucket_prefix}/table_function"
        )

        self.context.uri = f"{uri}table_function/{temp_s3_path}/"
        self.context.bucket_path = f"{bucket_prefix}/table_function/{temp_s3_path}"

    outline()
