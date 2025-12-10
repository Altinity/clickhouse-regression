#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..", "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from ldap.role_mapping.requirements import *
from helpers.common import check_clickhouse_version, experimental_analyzer


# Cross-outs of known fails
xfails = {
    "mapping/roles removed and added in parallel": [(Fail, "known bug")],
    "user dn detection/mapping/roles removed and added in parallel": [
        (Fail, "known bug")
    ],
    "cluster secret/external user directory/:/:/cluster with secret/ldap user/:mapped True/select using mapped role/with privilege on source and distributed": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/34130")
    ],
    "user dn detection/mapping/add new role not present": [
        (Error, "https://github.com/ClickHouse/ClickHouse/issues/41380",check_clickhouse_version("<=23.3")),
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/41380",check_clickhouse_version("<=23.3")),
    ],
    "user dn detection/mapping/map role when ldap user belongs to large number of groups": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/42276",
            check_clickhouse_version("<22.11"),
        )
    ],
    "mapping/add new role not present": [
        (Error, "https://github.com/ClickHouse/ClickHouse/issues/41380",check_clickhouse_version("<=23.3")),
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/41380",check_clickhouse_version("<=23.3")),
    ],
    "mapping/map role when ldap user belongs to large number of groups": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/42276")
    ],
}

# Force results without running the test
ffails = {
    "cluster secret": (
        Skip,
        "feature available on 20.10+",
        check_clickhouse_version("<20.10"),
    ),
    "/role mapping/user dn detection/mapping/role removed and readded": (
        XFail,
        "roles are not being applied to active clickhouse-client connections in 23.8: https://github.com/ClickHouse/ClickHouse/issues/56646",
        check_clickhouse_version(">=23.8"),
    ),
    "/role mapping/user dn detection/mapping/role added": (
        XFail,
        "roles are not being applied to active clickhouse-client connections in 23.8: https://github.com/ClickHouse/ClickHouse/issues/56646",
        check_clickhouse_version(">=23.8"),
    ),
    "/role mapping/mapping/role removed and readded": (
        XFail,
        "roles are not being applied to active clickhouse-client connections in 23.8: https://github.com/ClickHouse/ClickHouse/issues/56646",
        check_clickhouse_version(">=23.8"),
    ),
    "/role mapping/mapping/role added": (
        XFail,
        "roles are not being applied to active clickhouse-client connections in 23.8: https://github.com/ClickHouse/ClickHouse/issues/56646",
        check_clickhouse_version(">=23.8"),
    ),
}


@TestFeature
@Name("role mapping")
@ArgumentParser(argparser)
@Specifications(SRS_014_ClickHouse_LDAP_Role_Mapping)
@Requirements(RQ_SRS_014_LDAP_RoleMapping("1.0"))
@XFails(xfails)
@FFails(ffails)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """ClickHouse LDAP role mapping regression module."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Scenario(
        run=load("ldap.authentication.tests.sanity", "scenario"), name="ldap sanity"
    )
    Feature(run=load("ldap.role_mapping.tests.server_config", "feature"))
    Feature(run=load("ldap.role_mapping.tests.mapping", "feature"))
    Feature(run=load("ldap.role_mapping.tests.user_dn_detection", "feature"))
    Feature(run=load("ldap.role_mapping.tests.cluster_secret", "feature"))


if main():
    regression()
