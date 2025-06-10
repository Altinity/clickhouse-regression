from testflows.core import *
from s3.tests.common import add_config, create_xml_config_content


@TestStep(Given)
def get_clusters_config_for_nodes(self, nodes):
    """Create all possible cluster configurations for given nodes."""

    entries = {"remote_servers": {}}

    for node_num in range(1, len(nodes) + 1):
        for shards_num in range(1, node_num + 1):

            def generate_partitions(n, k):
                """Generate all possible ways to partition n nodes into k shards.
                Returns list of lists, where each inner list represents shard sizes that sum to n.
                """
                partitions = []
                if k == 1:
                    return [[n]]  # Only one way to partition n nodes into 1 shard
                if n < k:
                    return []

                max_size = n - (k - 1)
                for i in range(1, min(n // k + 1, max_size + 1)):
                    # Recursively generate partitions for remaining nodes and shards
                    for rest in generate_partitions(n - i, k - 1):
                        # Only keep non-increasing partitions to avoid duplicates
                        if not rest or i <= rest[0]:
                            partitions.append([i] + rest)
                return partitions

            # Get all valid partitions for current node and shard count
            all_partitions = generate_partitions(node_num, shards_num)

            # Create cluster config for each partition
            for part_idx, partition in enumerate(all_partitions):
                # Generate unique cluster name based on configuration
                cluster_name = (
                    f"cluster_{node_num}shards_{shards_num}replicas_{part_idx}"
                )
                cluster_config = []

                current_node_idx = 0

                # Configure each shard
                for shard_size in partition:
                    shard_config = {"shard": []}

                    # Add replicas to shard
                    for i in range(shard_size):
                        replica_config = {
                            "replica": {
                                "host": nodes[current_node_idx + i],
                                "port": "9000",
                            }
                        }
                        shard_config["shard"].append(replica_config)

                    cluster_config.append(shard_config)
                    current_node_idx += shard_size

                entries["remote_servers"][cluster_name] = cluster_config

    return entries


@TestStep(Given)
def add_clusters_for_nodes(self, nodes, modify=False):
    """Create all possible cluster configurations for given nodes and add them to the clickhouse configuration.
    Generate XML config and add it to ClickHouse config files.
    """
    return add_config(
        config=create_xml_config_content(
            root="yandex",
            entries=get_clusters_config_for_nodes(nodes=nodes),
            config_file="new_remote_servers.xml",
        ),
        restart=True,
        modify=modify,
    )


@TestStep(Given)
def get_clusters_for_nodes(self, nodes):
    """Get all possible cluster configurations for given nodes.
    Returns list of cluster names.
    """

    return [
        i for i in get_clusters_config_for_nodes(nodes=nodes)["remote_servers"].keys()
    ]
