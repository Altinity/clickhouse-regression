"""Swarm feature-support detection.

The swarm feature is exposed through the ``object_storage_cluster`` setting, so
its presence is detected by a query on a running node.
"""

from testflows.core import *

from helpers.common import get_settings_value


def object_storage_cluster_supported(test):
    """Return True if the build has the object_storage_cluster (swarm) setting.

    Checks the setting's presence (``name`` column), not its ``value``:
    object_storage_cluster defaults to an empty string.
    """
    with Then("I check whether the object_storage_cluster setting exists"):
        name = get_settings_value(
            "object_storage_cluster", node=test.context.node, column="name"
        )
    return name.strip() != ""
