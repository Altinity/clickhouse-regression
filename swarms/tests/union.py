from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

from helpers.common import getuid
from helpers.tables import create_table_as_select
from swarms.requirements.requirements import *

import random
import swarms.tests.steps.swarm_steps as swarm_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

random.seed(42)


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
def check_union(
    self,
    left_table,
    right_table,
    node=None,
    object_storage_cluster_1="replicated_cluster",
    object_storage_cluster_2="replicated_cluster",
    order_by="tuple(*)",
):
    """Check union operation."""
    if node is None:
        node = self.context.node

    with Given("choose to run query with UNION ALL or UNION DISTINCT"):
        all_or_distinct = random.choice(["UNION ALL", "UNION DISTINCT"])

    with And("create merge tree tables as left and right tables"):
        left_merge_tree_table = create_table_as_select(
            as_select_from=left_table,
        )
        right_merge_tree_table = create_table_as_select(
            as_select_from=right_table,
        )

    with When("get expected result from uniting merge tree tables"):
        query = f"""
            SELECT * FROM ((
                SELECT * EXCEPT (time_col), toDateTime(time_col) as time_col
                    FROM {left_merge_tree_table} AS t1
                )
            {all_or_distinct} (
                SELECT * EXCEPT (time_col), toDateTime(time_col) as time_col
                FROM {right_merge_tree_table} AS t2
                )
            )
            ORDER BY {order_by}
            """
        expected_result = node.query(query)

    with Then("check UNION on iceberg tables and cluster functions"):
        object_storage_cluster_setting_1 = random.choice(
            ["", f"SETTINGS object_storage_cluster = '{object_storage_cluster_1}'"]
        )
        object_storage_cluster_setting_2 = random.choice(
            ["", f"SETTINGS object_storage_cluster = '{object_storage_cluster_2}'"]
        )
        query = f"""
            SELECT * FROM ((
                SELECT * EXCEPT (time_col), toDateTime(time_col) as time_col
                FROM {left_table} AS t1
                {object_storage_cluster_setting_1}
                )
            {all_or_distinct} (
                SELECT * EXCEPT (time_col), toDateTime(time_col) as time_col
                FROM {right_table} AS t2
                {object_storage_cluster_setting_2}
                )
            )
            ORDER BY {order_by}
            """

        result = node.query(query)
        assert result.output == expected_result.output, error()


@TestFeature
@Flags(TE)
def union_clause(self, minio_root_user, minio_root_password, node=None):
    """Check reading data from iceberg tables with basic union clause."""
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

    with And("define all possible left and right tables combinations for union"):
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

    with And("define object storage clusters options"):
        object_storage_clusters = [
            "replicated_cluster_three_nodes",
            "replicated_cluster_two_nodes",
            "replicated_cluster_two_nodes_version_2",
            "replicated_cluster",
            "cluster_one_observer_one_swarm",
            "cluster_one_observer_two_swarm",
        ]

    all_possible_combinations = list(
        product(
            left_tables,
            right_tables,
            object_storage_clusters,
            object_storage_clusters,
        )
    )

    if not self.context.stress:
        all_possible_combinations = random.sample(all_possible_combinations, 500)

    length = len(all_possible_combinations)

    with Pool(10) as pool:
        for num, (
            left_table,
            right_table,
            object_storage_cluster_1,
            object_storage_cluster_2,
        ) in enumerate(all_possible_combinations):
            name = f"union {num} of {length}: {left_table} with {right_table} in {object_storage_cluster_1} cluster and {object_storage_cluster_2} cluster"
            Scenario(
                name=name,
                test=check_union,
                parallel=True,
                executor=pool,
            )(
                left_table=left_table,
                right_table=right_table,
                object_storage_cluster_1=object_storage_cluster_1,
                object_storage_cluster_2=object_storage_cluster_2,
            )
        join()


@TestFeature
@Name("swarm union")
def feature(self, minio_root_user, minio_root_password):
    """Check that union cluse works with object_storage_cluster setting."""

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

    Feature(test=union_clause)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
