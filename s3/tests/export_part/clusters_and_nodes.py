import random
from itertools import combinations

from testflows.core import *
from testflows.asserts import error

from s3.tests.export_part.steps import *


@TestScenario
def different_nodes_same_destination(self, cluster, node1, node2):
    """Test export part from different nodes to same S3 destination in a given cluster."""
    
    with Given("I create tables on different nodes"):
        source1, shared_destination = create_source_and_destination_tables(cluster=cluster, node=node1)        
        source2, _ = create_source_and_destination_tables(cluster=cluster, node=node2)
    
    with When("I insert test data into the source tables"):
        source1.insert_test_data(random=random.Random(1), node=node1)
        source2.insert_test_data(random=random.Random(2), node=node2)
    
    with And("I export parts from both nodes"):
        parts1 = source1.get_parts(node=node1)
        parts2 = source2.get_parts(node=node2)
        events_before_node1 = export_events(node=node1)
        events_before_node2 = export_events(node=node2)
        export_part(parts=parts1, source=source1, destination=shared_destination)
        export_part(parts=parts2, source=source2, destination=shared_destination)
    
    with Then("I check system.events that all exports are successful"):
        events_after_node1 = export_events(node=node1)
        events_after_node2 = export_events(node=node2)
        total_exports_after = events_after.get("PartsExports", 0) + events_after.get("PartsExportDuplicated", 0)
        total_exports_before = events_before.get("PartsExports", 0) + events_before.get("PartsExportDuplicated", 0)
        assert total_exports_after == total_exports_before + len(parts1) + len(parts2), error()
    
    with And("I verify data from both nodes appear in S3"):
        destination_data = shared_destination.select_ordered_by_partition_and_index()
        for part in parts1:
            assert part.split("_")[0] in destination_data, error()
        for part in parts2:
            assert part.split("_")[0] in destination_data, error()


@TestScenario  
def different_nodes_different_destinations(self, cluster, node1, node2):
    """Test export part from different nodes to different S3 destinations."""
    
    with Given("I create tables on different nodes with same part names"):
        source1, destination1 = create_source_and_destination_tables(cluster=cluster, node=node1)
        source2, destination2 = create_source_and_destination_tables(cluster=cluster, node=node2)
    
    with When("I insert test data into the source tables"):
        source1.insert_test_data(random=random.Random(1))
        source2.insert_test_data(random=random.Random(2))

    with And("I export parts from both nodes to separate destinations"):
        parts1 = source1.get_parts()
        parts2 = source2.get_parts()
        events_before = export_events()
        export_part(parts=parts1, source=source1, destination=destination1)
        export_part(parts=parts2, source=source2, destination=destination2)
    
    with Then("I check system.events that all exports are successful"):
        events_after = export_events()
        total_exports_after = events_after.get("PartsExports", 0) + events_after.get("PartsExportDuplicated", 0)
        total_exports_before = events_before.get("PartsExports", 0) + events_before.get("PartsExportDuplicated", 0)
        assert total_exports_after == total_exports_before + len(parts1) + len(parts2), error()

    with And("I verify data from both nodes appear in separate destinations"):
        data1 = destination1.select_ordered_by_partition_and_index()
        data2 = destination2.select_ordered_by_partition_and_index()
    
    with By("Checking data from both nodes appear in the right destinations"):
        for part in parts1:
            assert part.split("_")[0] in data1, error()
        for part in parts2:
            assert part.split("_")[0] in data2, error()
    
    with And("Checking data from both nodes do not appear in the wrong destinations"):
        unique_parts1 = list(set(parts1) - set(parts2))
        unique_parts2 = list(set(parts2) - set(parts1))
        for part in unique_parts1:
            assert part.split("_")[0] not in data2, error()
        for part in unique_parts2:
            assert part.split("_")[0] not in data1, error()


# I need to get the nodes from a cluster; is this the right way to do it?
def get_cluster_nodes(cluster, node=None):
    """Get all nodes in a cluster."""
    
    if node is None:
        node = current().context.node
    
    result = node.query(
        f"SELECT host_name FROM system.clusters WHERE cluster = '{cluster}'",
        exitcode=0
    )
    
    nodes = [line.strip() for line in result.output.splitlines() if line.strip()]
    return nodes


@TestFeature
@Name("clusters and nodes")
def feature(self):
    """Check functionality of exporting data parts to S3 storage from different clusters and nodes."""
    
    clusters = [
        # "sharded_cluster",
        # "replicated_cluster",
        # "one_shard_cluster",
        # "sharded_cluster12",
        # "one_shard_cluster12",
        "sharded_cluster23",
        # "one_shard_cluster23",
    ]

    for cluster in clusters:
        node_names = get_cluster_nodes(cluster=cluster)
        
        for node1_name, node2_name in combinations(node_names, 2):
            node1 = self.context.cluster.node(node1_name)
            node2 = self.context.cluster.node(node2_name)
            note(f"Testing {cluster} with nodes {node1_name} and {node2_name}")
            # different_nodes_same_destination(cluster=cluster, node1=node1, node2=node2)
            # different_nodes_different_destinations(cluster=cluster, node1=node1, node2=node2)