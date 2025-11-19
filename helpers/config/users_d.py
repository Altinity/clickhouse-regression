from testflows.core import *
import helpers.config.config as config


@TestStep(Given)
def create_and_add(
    self,
    entries: dict,
    config_file: str,
    modify: bool = False,
    restart: bool = True,
    format: str = None,
    user: str = None,
    config_d_dir: str = "/etc/clickhouse-server/users.d",
    preprocessed_name: str = "users.xml",
    node: Node = None,
):
    """Create and add users configuration file in users.d."""
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
