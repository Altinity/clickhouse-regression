from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

from helpers.common import getuid
from helpers.tables import create_table_as_select
from swarms.requirements.requirements import *

import random
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

    @classmethod
    def create_merge_tree_table(cls, table_name, **kwargs):
        """Create a merge tree table instance."""

        return cls(
            None,
            "merge_tree_table",
            table_name=table_name,
            **kwargs,
        )

    def __str__(self):
        if self.table_type == "iceberg_table":
            return f"{self.database_name}.\\`{self.namespace}.{self.table_name}\\`"
        elif self.table_type == "merge_tree_table":
            return self.table_name
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
    order_by="tuple(*)",
):
    """Check join operation."""
    if node is None:
        node = self.context.node

    if join_clause == "FULL OUTER JOIN" and object_storage_cluster_join_mode == "allow":
        xfail(
            "FULL OUTER JOIN is not supported in allow mode https://github.com/ClickHouse/ClickHouse/issues/89996"
        )

    with Given("create merge tree tables as left and right tables"):
        left_merge_tree_table = create_table_as_select(
            as_select_from=left_table,
        )
        right_merge_tree_table = create_table_as_select(
            as_select_from=right_table,
        )

    with When("get expected result from joining merge tree tables"):
        query = f"""
            SELECT *
            FROM {left_merge_tree_table} AS t1
            {join_clause} {right_merge_tree_table} AS t2
            """

        # asof join has to have single inequality condition
        if join_clause == "ASOF JOIN" or join_clause == "LEFT ASOF JOIN":
            for sign in ["<=", ">=", "<", ">"]:
                if sign in join_condition:
                    query += f" ON {join_condition}"
                    break
            else:
                query += f" ON {join_condition} AND t1.long_col < t2.long_col"
        elif join_clause != "CROSS JOIN" and join_clause != "PASTE JOIN":
            query += f" ON {join_condition}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if format:
            query += f" FORMAT {format}"

        expected_result = node.query(query)

    exitcode, message = None, None

    non_stable_join_clauses = [
        "INNER JOIN",
        "INNER ANY JOIN",
        "CROSS JOIN",
        "ASOF JOIN",
        "RIGHT OUTER JOIN",
        "RIGHT SEMI JOIN",
        "RIGHT ANTI JOIN",
        "RIGHT ANY JOIN",
        "LEFT OUTER JOIN",
        "LEFT SEMI JOIN",
        "LEFT ANTI JOIN",
        "LEFT ANY JOIN",
        "LEFT ASOF JOIN",
    ]

    if (
        (
            object_storage_cluster_join_mode == "allow"
            and left_table.table_type == "iceberg_table"
            and right_table.table_type == "iceberg_table"
            and object_storage_cluster
            and join_clause != "PASTE JOIN"
        )
        or (
            object_storage_cluster_join_mode == "allow"
            and left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "iceberg_table"
            and object_storage_cluster
            and join_clause != "PASTE JOIN"
        )
        or (
            object_storage_cluster_join_mode == "allow"
            and left_table.table_type == "s3_table_function"
            and right_table.table_type == "iceberg_table"
            and object_storage_cluster
            and join_clause != "PASTE JOIN"
        )
        or (
            object_storage_cluster_join_mode == "allow"
            and left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "iceberg_table"
            and join_clause != "PASTE JOIN"
        )
        or (
            object_storage_cluster_join_mode == "allow"
            and left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "iceberg_table"
            and join_clause != "PASTE JOIN"
        )
    ):
        exitcode, message = (
            81,
            "DB::Exception:",
        )

    if (
        (
            left_table.table_type == "iceberg_table"
            and right_table.table_type == "merge_tree_table"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "merge_tree_table"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "s3_table_function"
            and right_table.table_type == "merge_tree_table"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "merge_tree_table"
            and object_storage_cluster_join_mode == "allow"
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "merge_tree_table"
            and object_storage_cluster_join_mode == "allow"
            and join_clause != "PASTE JOIN"
        )
    ):
        exitcode, message = (
            60,
            "DB::Exception:",
        )

    query = f"""
        SELECT *
        FROM {left_table} AS t1
        {join_clause} {right_table} AS t2
        """

    if join_clause == "ASOF JOIN" or join_clause == "LEFT ASOF JOIN":
        for sign in ["<=", ">=", "<", ">"]:
            if sign in join_condition:
                query += f" ON {join_condition}"
                break
        else:
            query += f" ON {join_condition} AND t1.long_col < t2.long_col"
    elif join_clause != "CROSS JOIN":
        query += f" ON {join_condition}"

    if join_clause == "PASTE JOIN":
        query = f"""
            SELECT *
            FROM
            (
                SELECT *
                FROM {left_table}
            ) AS t1
            PASTE JOIN
            (
                SELECT *
                FROM {right_table}
            ) AS t2
        """

    if order_by:
        query += f" ORDER BY {order_by}"

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
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "iceberg_table"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "iceberg_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "s3_table_function"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "s3_table_function"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "s3_table_function"
            and right_table.table_type == "iceberg_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "iceberg_table"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "iceberg_table_function"
            and object_storage_cluster_join_mode == "allow"
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "allow"
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "icebergS3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "iceberg_table_function"
            and object_storage_cluster_join_mode == "allow"
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "s3Cluster_table_function"
            and right_table.table_type == "s3_table_function"
            and object_storage_cluster_join_mode == "allow"
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "iceberg_table"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "icebergS3Cluster_table_function"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "iceberg_table_function"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
        or (
            left_table.table_type == "s3_table_function"
            and right_table.table_type == "s3Cluster_table_function"
            and object_storage_cluster_join_mode == "allow"
            and object_storage_cluster
            and join_clause in non_stable_join_clauses
        )
    ):
        # resulting rows are not stable
        assert result.exitcode == 0, error()
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

    with Given(
        "create merge tree tables from iceberg tables with same schema and data"
    ):
        merge_tree_tables = []
        for iceberg_table in iceberg_tables:
            merge_tree_table_name = f"merge_tree_table_{getuid()}"
            create_table_as_select(
                as_select_from=iceberg_table, table_name=merge_tree_table_name
            )
            merge_tree_tables.append(
                JoinTable.create_merge_tree_table(table_name=merge_tree_table_name)
            )

    left_tables = (
        iceberg_tables
        + iceberg_table_functions
        + s3_table_functions
        + iceberg_s3_cluster_table_functions
        + s3_cluster_table_functions
        + merge_tree_tables
    )
    right_tables = (
        iceberg_tables
        + iceberg_table_functions
        + s3_table_functions
        + iceberg_s3_cluster_table_functions
        + s3_cluster_table_functions
        + merge_tree_tables
    )
    modes = ["allow", "local"]
    join_conditions = [
        "t1.boolean_col = t2.boolean_col",
        "t1.boolean_col = t2.boolean_col AND t1.string_col = t2.string_col",
        "t1.string_col = t2.string_col AND t1.long_col = t2.long_col",
        "t1.long_col < t2.long_col AND t1.string_col = t2.string_col",
        "t1.integer_col = t2.integer_col",
        "t1.double_col = t2.double_col",
        "t1.float_col = t2.float_col",
        "t1.decimal_col = t2.decimal_col",
        "t1.date_col = t2.date_col",
        "t1.timestamp_col = t2.timestamp_col",
        "t1.timestamptz_col = t2.timestamptz_col",
        "t1.timestamp_col < t2.timestamp_col AND t1.string_col = t2.string_col",
    ]
    object_storage_clusters = [
        None,
        "replicated_cluster_three_nodes",
        "replicated_cluster_two_nodes",
        "replicated_cluster_two_nodes_version_2",
        "replicated_cluster",
        "cluster_one_observer_one_swarm",
        "cluster_one_observer_two_swarm",
    ]
    join_clauses = [
        "INNER JOIN",
        "INNER ANY JOIN",
        "CROSS JOIN",
        "ASOF JOIN",
        "RIGHT OUTER JOIN",
        "RIGHT SEMI JOIN",
        "RIGHT ANTI JOIN",
        "RIGHT ANY JOIN",
        "LEFT OUTER JOIN",
        "LEFT SEMI JOIN",
        "LEFT ANTI JOIN",
        "LEFT ANY JOIN",
        "LEFT ASOF JOIN",
        "PASTE JOIN",
        "FULL OUTER JOIN",
    ]

    length = len(
        list(
            product(
                left_tables,
                right_tables,
                modes,
                join_conditions,
                object_storage_clusters,
                join_clauses,
            )
        )
    )

    all_possible_combinations = list(
        product(
            left_tables,
            right_tables,
            modes,
            join_conditions,
            object_storage_clusters,
            join_clauses,
        )
    )

    if not self.context.stress:
        all_possible_combinations = random.sample(all_possible_combinations, 1000)

    pause()

    with Pool() as pool:
        for num, (
            left_table,
            right_table,
            mode,
            join_condition,
            object_storage_cluster,
            join_clause,
        ) in enumerate(all_possible_combinations):
            name = f"join {num} of {length}: {left_table} with {right_table} in {mode} mode on {object_storage_cluster} cluster with {join_clause} clause"
            Scenario(
                name=name,
                test=check_join,
                parallel=True,
                executor=pool,
            )(
                left_table=left_table,
                right_table=right_table,
                object_storage_cluster=object_storage_cluster,
                join_clause=join_clause,
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
    with Given("create cluster with observer initiator and one swarm nodes"):
        cluster_name = "cluster_one_observer_one_swarm"
        swarm_steps.add_node_to_swarm(
            node=self.context.node,
            observer=True,
            cluster_name=cluster_name,
            config_name="one_swarm_node.xml",
            path="/clickhouse/discovery/swarm1",
        )
        swarm_steps.add_node_to_swarm(
            node=self.context.node2,
            cluster_name=cluster_name,
            config_name="one_swarm_node.xml",
            path="/clickhouse/discovery/swarm1",
        )

    with And("create cluster with observer initiator and two swarm nodes"):
        cluster_name = "cluster_one_observer_two_swarm"
        swarm_steps.add_node_to_swarm(
            node=self.context.node,
            observer=True,
            cluster_name=cluster_name,
            config_name="two_swarm_nodes.xml",
            path="/clickhouse/discovery/swarm2",
        )
        swarm_steps.add_node_to_swarm(
            node=self.context.node2,
            cluster_name=cluster_name,
            config_name="two_swarm_nodes.xml",
            path="/clickhouse/discovery/swarm2",
        )
        swarm_steps.add_node_to_swarm(
            node=self.context.node3,
            cluster_name=cluster_name,
            config_name="two_swarm_nodes.xml",
            path="/clickhouse/discovery/swarm2",
        )

    Feature(test=join_clause)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
