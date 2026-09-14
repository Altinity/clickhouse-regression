"""Bridge helpers.cluster nodes → ca-soak CA_SOAK_* env contract.

The soak driver and scenario framework talk to replicas over host-published HTTP
ports and invoke `docker exec` / chaos against container ids. After
`create_cluster` brings the suite up, call `bind_cluster(cluster)` so those
defaults match the regression-native topology.
"""

from __future__ import annotations

import os
from typing import Iterable, Optional


# Host ports published by cas/soak/soak_env/docker-compose.yml
_DEFAULT_HOST_PORTS = {
    1: 8123,
    2: 8124,
}

# soak_env RustFS is started as the `minio` service with data root `/data` and
# bucket `warehouse` (see soak_env/minio-client.yml + storage.xml endpoint).
_SOAK_ENV_POOL_DIR = "/data/warehouse/soak_pool"


def bind_cluster(
    cluster,
    *,
    nodes: Optional[Iterable[str]] = None,
    host: str = "localhost",
    host_ports: Optional[dict] = None,
    rustfs_service: str = "minio",
) -> dict:
    """Set CA_SOAK_* from a live helpers.cluster.Cluster.

    Returns the env dict that was applied (also written into os.environ).
    """
    node_names = list(nodes) if nodes is not None else list(cluster.nodes.get("clickhouse", []))
    if not node_names:
        raise RuntimeError("bind_cluster: no clickhouse nodes on cluster")

    ports = dict(_DEFAULT_HOST_PORTS)
    if host_ports:
        ports.update(host_ports)

    env = {
        "CA_SOAK_NODE_COUNT": str(len(node_names)),
        "CA_SOAK_POOL_DIR": os.environ.get("CA_SOAK_POOL_DIR", _SOAK_ENV_POOL_DIR),
    }

    containers = []
    for i, name in enumerate(node_names, start=1):
        with cluster.lock:
            container_id = cluster.node_container_id(name)
        port = ports.get(i, 8122 + i)
        env[f"CA_SOAK_NODE{i}_HOST"] = host
        env[f"CA_SOAK_NODE{i}_PORT"] = str(port)
        env[f"CA_SOAK_NODE{i}_CONTAINER"] = container_id
        containers.append(container_id)

    env["CA_SOAK_FSCK_CONTAINER"] = containers[0]
    env["CA_SOAK_CH_CONTAINERS"] = ",".join(containers)

    try:
        with cluster.lock:
            rustfs_id = cluster.node_container_id(rustfs_service, timeout=30)
        env["CA_SOAK_RUSTFS_CONTAINER"] = rustfs_id
    except Exception:
        # Optional: chaos rustfs faults need this; scenarios may override.
        pass

    # Make PackageDownloader binary available to variant docker-compose mounts.
    binary = getattr(cluster, "clickhouse_path", None)
    if binary and os.path.isfile(binary):
        env["CLICKHOUSE_BINARY_HOST_PATH"] = os.path.abspath(binary)

    for key, value in env.items():
        os.environ[key] = value

    return env


def ensure_binary_env(clickhouse_path: str) -> str:
    """Resolve clickhouse_path into CLICKHOUSE_BINARY_HOST_PATH for compose variants."""
    from helpers.cluster import PackageDownloader

    pkg = PackageDownloader(clickhouse_path, program_name="clickhouse", binary_only=True)
    binary = pkg.binary_path
    if not binary or not os.path.isfile(binary):
        raise RuntimeError(
            f"could not resolve ClickHouse binary from {clickhouse_path!r} "
            f"(got binary_path={binary!r})"
        )
    path = os.path.abspath(binary)
    os.environ["CLICKHOUSE_BINARY_HOST_PATH"] = path
    return path
