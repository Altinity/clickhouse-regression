from testflows.core import *
import helpers.config.config as config
from helpers.common import check_clickhouse_version, check_if_antalya_build


@TestStep(Given)
def create_and_add(
    self,
    entries: dict,
    config_file: str,
    modify: bool = False,
    restart: bool = True,
    format: str = None,
    user: str = None,
    config_d_dir: str = "/etc/clickhouse-server/config.d",
    preprocessed_name: str = "config.xml",
    node: Node = None,
):
    """Create and add configuration file in config.d."""
    return config.create_and_add(
        entries=entries,
        config_file=config_file,
        config_d_dir=config_d_dir,
        preprocessed_name=preprocessed_name,
        modify=modify,
        restart=restart,
        format=format,
        user=user,
        node=node,
    )


def export_partition_setting_name():
    """Return the ``EXPORT PARTITION`` server-config flag name for this build.

    Renamed in https://github.com/Altinity/ClickHouse/pull/1618. Antalya 25.8
    still uses ``enable_experimental_export_merge_tree_partition_feature``;
    26.1+ uses ``allow_experimental_export_merge_tree_partition``.
    """
    if check_clickhouse_version("<26.1")(current()):
        return "enable_experimental_export_merge_tree_partition_feature"
    return "allow_experimental_export_merge_tree_partition"


@TestStep(Given)
def enable_export_partition(
    self,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file=None,
    restart=True,
    nodes=None,
):
    """Enable the Antalya ``EXPORT PARTITION`` server gate in ``config.d``.

    No-op on non-Antalya builds: the setting is not in upstream
    ``ServerSettings``, and ClickHouse 26.8+ (ClickHouse#100332) refuses
    unknown top-level config keys at startup and on reload.
    """
    if not check_if_antalya_build():
        return

    setting_name = export_partition_setting_name()
    if config_file is None:
        config_file = f"{setting_name}.xml"

    if nodes is None:
        nodes = getattr(self.context, "nodes", None)
        if not nodes:
            cluster = self.context.cluster
            nodes = [cluster.node(name) for name in cluster.nodes["clickhouse"]]

    for node in nodes:
        create_and_add(
            entries={setting_name: "1"},
            config_file=config_file,
            config_d_dir=config_d_dir,
            node=node,
            restart=restart,
        )
