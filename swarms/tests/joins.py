from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

from helpers.common import getuid
from swarms.requirements.requirements import *

import swarms.tests.steps.swarm_steps as swarm_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


class JoinTable:
    minio_root_user = None
    minio_root_password = None

    def __init__(
        self,
        location,
        table_type,
        database_name=None,
        namespace=None,
        table_name=None,
        cluster_name=None,
        minio_root_user=None,
        minio_root_password=None,
    ):
        self.location = location
        self.table_type = table_type
        self.cluster_name = cluster_name
        self.minio_root_user = minio_root_user or JoinTable.minio_root_user
        self.minio_root_password = minio_root_password or JoinTable.minio_root_password
        self.database_name = database_name
        self.namespace = namespace
        self.table_name = table_name

    @classmethod
    def set_default_credentials(cls, minio_root_user, minio_root_password):
        """Set default credentials for all instances."""
        cls.minio_root_user = minio_root_user
        cls.minio_root_password = minio_root_password

    @classmethod
    def create_iceberg_table_function(cls, location, **kwargs):
        """Create an iceberg table instance."""
        return cls(location, "iceberg_table_function", **kwargs)

    @classmethod
    def create_icebergS3Cluster_table_function(cls, location, cluster_name, **kwargs):
        """Create an icebergS3Cluster table instance."""
        return cls(
            location,
            "icebergS3Cluster_table_function",
            cluster_name=cluster_name,
            **kwargs,
        )

    @classmethod
    def create_s3_table_function(cls, location, **kwargs):
        """Create an s3 table instance."""
        location = location + "/data/**.parquet"
        return cls(location, "s3_table_function", **kwargs)

    @classmethod
    def create_s3Cluster_table_function(cls, location, cluster_name, **kwargs):
        """Create an s3Cluster table instance."""
        location = location + "/data/**.parquet"
        return cls(
            location, "s3Cluster_table_function", cluster_name=cluster_name, **kwargs
        )

    @classmethod
    def create_iceberg_table(cls, database_name, namespace, table_name, **kwargs):
        """Create an iceberg table instance."""
        return cls(
            None,
            "iceberg_table",
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            **kwargs,
        )

    def __str__(self):
        if self.table_type == "iceberg_table":
            return f"{self.database_name}.\\`{self.namespace}.{self.table_name}\\`"
        elif self.table_type == "iceberg_table_function":
            return f"iceberg('{self.location}', '{self.minio_root_user}', '{self.minio_root_password}')"
        elif self.table_type == "icebergS3Cluster_table_function":
            return f"icebergS3Cluster({self.cluster_name}, '{self.location}', '{self.minio_root_user}', '{self.minio_root_password}')"
        elif self.table_type == "s3_table_function":
            return f"s3('{self.location}', '{self.minio_root_user}', '{self.minio_root_password}')"
        elif self.table_type == "s3Cluster_table_function":
            return f"s3Cluster({self.cluster_name}, '{self.location}', '{self.minio_root_user}', '{self.minio_root_password}')"
        else:
            raise ValueError(f"Unknown table type: {self.table_type}")

    def __repr__(self):
        return self.__str__()


@TestScenario
def check_join(
    self,
    left_table,
    right_table,
    join_clause,
    join_condition,
    object_storage_cluster_join_mode,
    node=None,
    object_storage_cluster="replicated_cluster_two_nodes",
    format="Values",
):
    """Check join operation."""
    if node is None:
        node = self.context.node

    with Given("create merge tree tables as left and right tables"):
        left_merge_tree_table = f"left_merge_tree_{getuid()}"
        right_merge_tree_table = f"right_merge_tree_{getuid()}"

        node.query(
            f"CREATE TABLE {left_merge_tree_table} ENGINE = MergeTree ORDER BY tuple() AS SELECT * FROM {left_table}"
        )
        node.query(
            f"CREATE TABLE {right_merge_tree_table} ENGINE = MergeTree ORDER BY tuple() AS SELECT * FROM {right_table}"
        )

    with When("get expected result from joining merge tree tables"):
        expected_result = node.query(
            f"""
            SELECT *
            FROM {left_merge_tree_table} AS t1
            {join_clause} {right_merge_tree_table} AS t2
            ON {join_condition}
            ORDER BY tuple(*)
            FORMAT Values
            """
        )

    exitcode, message = None, None

    if (
        (
            object_storage_cluster_join_mode == "allow"
            and left_table.table_type == "iceberg_table"
            and right_table.table_type == "iceberg_table"
        )
        or (
            object_storage_cluster_join_mode == "allow"
            and left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "iceberg_table"
        )
        or (
            object_storage_cluster_join_mode == "allow"
            and left_table.table_type == "s3_table_function"
            and right_table.table_type == "iceberg_table"
        )
        or (
            object_storage_cluster_join_mode == "allow"
            and left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "iceberg_table"
        )
        or (
            object_storage_cluster_join_mode == "allow"
            and left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "iceberg_table"
        )
    ):
        exitcode, message = (
            81,
            "DB::Exception:",
        )

    if (
        (
            left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "local"
            and left_table.location == right_table.location
        )
        or (
            left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "iceberg_table_function"
            and object_storage_cluster_join_mode == "local"
            and left_table.location == right_table.location
        )
        or (
            left_table.table_type == "s3_table_function"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "local"
            and left_table.location == right_table.location
        )
        or (
            left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "local"
            and left_table.location == right_table.location
        )
    ):
        exitcode, message = (
            10,
            "DB::Exception:",
        )

    query = f"""
        SELECT *
        FROM {left_table} AS t1
        {join_clause} {right_table} AS t2
        ON {join_condition}
        ORDER BY tuple(*)
        """

    settings = {}

    if object_storage_cluster_join_mode:
        settings["object_storage_cluster_join_mode"] = (
            f"'{object_storage_cluster_join_mode}'"
        )

    if object_storage_cluster:
        settings["object_storage_cluster"] = f"'{object_storage_cluster}'"

    if settings:
        query += f" SETTINGS {', '.join([f'{key}={value}' for key, value in settings.items()])}"

    if format:
        query += f" FORMAT {format}"

    result = node.query(query, exitcode=exitcode, message=message)

    if (
        (
            left_table.table_type == "iceberg_table"
            and right_table.table_type == "iceberg_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "iceberg_table"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "iceberg_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "s3_table_function"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "s3_table_function"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "s3_table_function"
            and right_table.table_type == "iceberg_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "iceberg_table"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "iceberg_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "iceberg_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "iceberg_table"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
        or (
            left_table.table_type == "s3_table_function"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
        )
    ):
        assert result.output == "", error()
    elif not exitcode:
        assert result.output == expected_result.output, error()


@TestFeature
@Flags(TE)
def join_clause(self, minio_root_user, minio_root_password, node=None):
    """Check reading data from ClickHouse table from Iceberg database with basic join clause."""
    if node is None:
        node = self.context.node

    database_name = f"database_{getuid()}"
    number_of_iceberg_tables = 3
    locations = [
        f"s3://warehouse/data{i}" for i in range(1, number_of_iceberg_tables + 1)
    ]
    urls = [
        f"http://minio:9000/warehouse/data{i}"
        for i in range(1, number_of_iceberg_tables + 1)
    ]
    iceberg_tables = []

    with Given("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with Given("create iceberg tables in different locations"):
        for location in locations:
            _, table_name, namespace = (
                swarm_steps.iceberg_table_with_all_basic_data_types(
                    minio_root_user=minio_root_user,
                    minio_root_password=minio_root_password,
                    location=location,
                )
            )
            iceberg_tables.append(
                JoinTable.create_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                )
            )

    with When("list all possible left and right tables for joins"):
        JoinTable.set_default_credentials(minio_root_user, minio_root_password)

        s3_table_functions = [
            JoinTable.create_s3_table_function(
                url,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            for url in urls
        ]
        iceberg_table_functions = [
            JoinTable.create_iceberg_table_function(
                url,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            for url in urls
        ]
        iceberg_s3_cluster_table_functions = [
            JoinTable.create_icebergS3Cluster_table_function(url, "replicated_cluster")
            for url in urls
        ]
        s3_cluster_table_functions = [
            JoinTable.create_s3Cluster_table_function(url, "replicated_cluster")
            for url in urls
        ]

        left_tables = (
            iceberg_tables
            + iceberg_table_functions
            + s3_table_functions
            + iceberg_s3_cluster_table_functions
            + s3_cluster_table_functions
        )
        right_tables = (
            iceberg_tables
            + iceberg_table_functions
            + s3_table_functions
            + iceberg_s3_cluster_table_functions
            + s3_cluster_table_functions
        )
        modes = ["allow", "local"]
        join_conditions = [
            "t1.boolean_col = t2.boolean_col",
            "t1.boolean_col = t2.boolean_col AND t1.string_col = t2.string_col",
            "t1.string_col = t2.string_col AND t1.long_col = t2.long_col",
        ]

    length = len(list(product(left_tables, right_tables, modes, join_conditions)))

    with Pool(5) as pool:
        for num, (left_table, right_table, mode, join_condition) in enumerate(
            product(left_tables, right_tables, modes, join_conditions)
        ):

            Scenario(
                name=f"join {num} of {length}: {left_table} with {right_table} in {mode} mode",
                test=check_join,
                parallel=True,
                executor=pool,
            )(
                left_table=left_table,
                right_table=right_table,
                join_clause="JOIN",
                join_condition=join_condition,
                object_storage_cluster_join_mode=mode,
            )
        join()


@TestScenario
def s3Cluster_stability(self, minio_root_user, minio_root_password, node=None):
    """Check stability of s3Cluster table function with different joins."""
    pass


@TestFeature
@Name("swarm joins")
def feature(self, minio_root_user, minio_root_password):
    """Run swarm cluster joins checks."""

    # without object storage cluster
    # object storage cluster uses same nodes as cluster functions
    # object storage cluster join uses same nodes as cluster functions
    # object storage cluster uses differentt nodes than cluster functions

    Feature(test=join_clause)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
