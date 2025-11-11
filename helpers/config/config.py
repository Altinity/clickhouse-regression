from testflows.core import *
from helpers.common import *


@TestStep(Given)
def create_and_add(
    self,
    entries: dict,
    config_file: str,
    config_d_dir: str,
    preprocessed_name: str,
    modify: bool = False,
    restart: bool = True,
    format: str = None,
    user: str = None,
    node: Node = None,
):
    """Create and add configuration file to the server."""
    with By("converting config file content to xml"):
        config = create_xml_config_content(
            entries,
            config_file=config_file,
            config_d_dir=config_d_dir,
            preprocessed_name=preprocessed_name,
        )
        if format is not None:
            for key, value in format.items():
                config.content = config.content.replace(key, value)

    with And("adding xml config file to the server"):
        return add_config(config, restart=restart, modify=modify, user=user, node=node)