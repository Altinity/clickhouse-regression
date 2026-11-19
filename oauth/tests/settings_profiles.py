"""``<profiles_mapping>`` in the token user directory (Altinity/ClickHouse#2664).

IdP groups map to settings profiles that are assigned directly to the
auto-provisioned user, so they override ``default_profile`` and the
profiles carried by roles. Most scenarios mint HS256 tokens with an
explicit ``groups`` claim so the group set is deterministic; the Keycloak
scenarios cover the same contract end to end.
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.workload import background_workload
from jwt_authentication.tests.steps import create_static_jwt
from oauth.requirements.requirements import *
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    add_cluster_with_secret,
    apply_fatal_user_directories_config,
    check_clickhouse_is_alive,
    create_memory_table,
    create_role,
    create_settings_profile,
    group_mapping_entries,
    setting_default,
)
from oauth.tests.steps.common import (
    assert_query_rejected,
    configure_openid_token_processor,
    configure_static_key_processor,
    profiles_mapping_supported,
    provider_user,
)
from oauth.tests.steps.provider_protocol import UnsupportedByProvider

SECRET = "profiles_mapping_test_secret"
SETTINGS = ("max_block_size", "max_insert_block_size", "max_query_size")


def mint_token(user, groups):
    """HS256 token for ``user`` carrying ``groups`` in the ``groups`` claim."""
    return create_static_jwt(
        payload={"sub": user, "groups": list(groups)},
        secret=SECRET,
        algorithm="HS256",
        expiration_minutes=10,
    )


@TestStep(When)
def get_settings(self, token, names=SETTINGS, ip="clickhouse1"):
    """Return the values of ``names`` in the token user's session, in order."""
    columns = ", ".join(f"getSetting('{n}')" for n in names)
    body = access_clickhouse(
        token=token, ip=ip, query=f"SELECT {columns} FORMAT TabSeparated"
    )
    return body.strip().split("\t")


@TestStep(Given)
def profiles_and_role(self, uid, role_grants=("SELECT ON default.*",), node=None):
    """Create the profiles and role used across the scenarios, mirroring the
    upstream ``test_token_profiles_mapping`` fixture.

    Returns a dict of the created names.
    """
    names = {
        "default": f"p_default_{uid}",
        "role_profile": f"p_role_{uid}",
        "analysts": f"p_analysts_{uid}",
        "fast": f"p_fast_{uid}",
        "role": f"r_profiles_{uid}",
    }

    create_settings_profile(
        name=names["default"], settings="max_block_size = 1001", node=node
    )
    create_settings_profile(
        name=names["role_profile"], settings="max_insert_block_size = 2002", node=node
    )
    create_settings_profile(
        name=names["analysts"],
        settings="max_block_size = 1003, max_insert_block_size = 2003",
        node=node,
    )
    create_settings_profile(
        name=names["fast"],
        settings="max_block_size = 1004, max_query_size = 300004",
        node=node,
    )
    create_role(
        name=names["role"],
        settings_profile=names["role_profile"],
        grants=role_grants,
        node=node,
    )
    return names


@TestStep(Given)
def token_directory_with_profiles(self, names, profiles_mapping=None, node=None):
    """Static-key processor plus a token directory granting the shared role,
    using ``default_profile`` and the analysts/fast mapping by default.
    """
    if profiles_mapping is None:
        profiles_mapping = [
            {"from": "g_analysts", "to": names["analysts"]},
            {"from": "g_fast", "to": names["fast"]},
        ]

    configure_static_key_processor(
        secret=SECRET,
        common_roles=(names["role"],),
        default_profile=names["default"],
        profiles_mapping=profiles_mapping,
        node=node,
    )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping("1.0"),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_Precedence("1.0"),
)
def without_mapped_groups(self):
    """A user with no mapped group SHALL get ``default_profile`` plus the
    profile of its role, and nothing from ``profiles_mapping``.
    """
    uid = getuid()[:8]
    default_query_size = setting_default("max_query_size")

    with Given("profiles, a role carrying a profile, and the token directory"):
        names = profiles_and_role(uid=uid)
        token_directory_with_profiles(names=names)

    with When("a user whose only group is unmapped logs in"):
        values = get_settings(token=mint_token(f"u_none_{uid}", ["g_unmapped"]))

    with Then("default_profile and the role profile apply"):
        assert values == ["1001", "2002", default_query_size], error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping("1.0"),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_Precedence("1.0"),
)
def mapped_profile_overrides_default_and_role_profiles(self):
    """A mapped profile SHALL override both ``default_profile`` and the
    profiles carried by the user's roles.
    """
    uid = getuid()[:8]
    default_query_size = setting_default("max_query_size")

    with Given("profiles, a role carrying a profile, and the token directory"):
        names = profiles_and_role(uid=uid)
        token_directory_with_profiles(names=names)

    with When("a user in 'g_analysts' logs in"):
        values = get_settings(token=mint_token(f"u_analyst_{uid}", ["g_analysts"]))

    with Then("the analysts profile wins over default_profile and the role profile"):
        assert values == ["1003", "2003", default_query_size], error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_MultipleGroups(
        "1.0"
    ),
)
def later_mapping_entry_wins(self):
    """With several mapped groups all profiles SHALL be assigned and the
    later ``profiles_mapping`` entry SHALL win, whatever the token's group order.
    """
    uid = getuid()[:8]

    with Given("profiles, a role carrying a profile, and the token directory"):
        names = profiles_and_role(uid=uid)
        token_directory_with_profiles(names=names)

    for groups in (["g_fast", "g_analysts"], ["g_analysts", "g_fast"]):
        with When(f"a user with groups {groups} logs in"):
            values = get_settings(token=mint_token(f"u_both_{uid}", groups))

        with Then("g_fast (the later entry) wins on max_block_size"):
            assert values == ["1004", "2003", "300004"], error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_GroupRemoved("1.0"),
)
def profile_removed_with_group(self):
    """A user who leaves a mapped group SHALL lose its profile on the next login."""
    uid = getuid()[:8]
    user = f"u_leaving_{uid}"
    default_query_size = setting_default("max_query_size")

    with Given("profiles, a role carrying a profile, and the token directory"):
        names = profiles_and_role(uid=uid)
        token_directory_with_profiles(names=names)

    with When("the user logs in while in 'g_analysts'"):
        values = get_settings(token=mint_token(user, ["g_analysts"]))

    with Then("the analysts profile applies"):
        assert values == ["1003", "2003", default_query_size], error()

    with When("the same user logs in again without any group"):
        values = get_settings(token=mint_token(user, []))

    with Then("the analysts profile is gone; default and role profiles remain"):
        assert values == ["1001", "2002", default_query_size], error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_RawGroupMatching(
        "1.0"
    ),
)
def matches_raw_group_not_role_pipeline(self):
    """``profiles_mapping`` SHALL match the group exactly as it is in the
    token; names produced by ``roles_mapping`` / ``roles_transform`` SHALL
    NOT match.
    """
    uid = getuid()[:8]
    default_query_size = setting_default("max_query_size")

    with Given("profiles and a role carrying a profile"):
        names = profiles_and_role(uid=uid)

    with And(
        "a token directory whose profiles_mapping keys are the names the role "
        "pipeline would produce (g_fast -> mapped_fast, g_analysts -> analysts)"
    ):
        configure_static_key_processor(
            secret=SECRET,
            common_roles=(names["role"],),
            default_profile=names["default"],
            roles_mapping=[{"from": "g_fast", "to": "mapped_fast"}],
            roles_transform="s/^g_//",
            profiles_mapping=[
                {"from": "analysts", "to": names["analysts"]},
                {"from": "mapped_fast", "to": names["fast"]},
            ],
        )

    with When("a user with groups g_analysts and g_fast logs in"):
        values = get_settings(
            token=mint_token(f"u_raw_{uid}", ["g_analysts", "g_fast"])
        )

    with Then("no mapped profile applies"):
        assert values == ["1001", "2002", default_query_size], error()

    with When("a user whose token literally carries 'analysts' logs in"):
        values = get_settings(token=mint_token(f"u_literal_{uid}", ["analysts"]))

    with Then("the entry matches the raw group and applies"):
        assert values == ["1003", "2003", default_query_size], error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_MissingProfile(
        "1.0"
    ),
)
def missing_mapped_profile_skipped(self):
    """A mapping to a non-existent profile SHALL be skipped: the user still
    authenticates and the profiles that do exist still apply.
    """
    uid = getuid()[:8]

    with Given("profiles, a role carrying a profile, and the token directory"):
        names = profiles_and_role(uid=uid)
        token_directory_with_profiles(
            names=names,
            profiles_mapping=[
                {"from": "g_fast", "to": names["fast"]},
                {"from": "g_ghost", "to": f"p_does_not_exist_{uid}"},
            ],
        )

    with When("a user in both g_fast and g_ghost logs in"):
        values = get_settings(token=mint_token(f"u_ghost_{uid}", ["g_fast", "g_ghost"]))

    with Then("authentication succeeds and the existing mapped profile applies"):
        assert values == ["1004", "2002", "300004"], error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_Enforcement("1.0"),
)
def mapped_profile_constraints_enforced(self):
    """A mapped profile's settings and constraints SHALL be enforced:
    ``readonly = 1`` rejects writes and a ``CONST`` setting cannot be changed.
    """
    uid = getuid()[:8]
    role = f"r_writer_{uid}"
    readonly_profile = f"p_viewers_{uid}"
    const_profile = f"p_const_{uid}"

    with Given("a table the token role may insert into"):
        table = create_memory_table(name=f"t_profiles_{uid}")
        insert_query = f"INSERT INTO {table} VALUES (1)"

    with And("a writer role, a readonly profile and a CONST profile"):
        create_role(name=role, grants=(f"SELECT, INSERT ON {table}",))
        create_settings_profile(name=readonly_profile, settings="readonly = 1")
        create_settings_profile(
            name=const_profile, settings="max_block_size = 1005 CONST"
        )

    with And("a token directory mapping g_viewers and g_const to those profiles"):
        configure_static_key_processor(
            secret=SECRET,
            common_roles=(role,),
            profiles_mapping=[
                {"from": "g_viewers", "to": readonly_profile},
                {"from": "g_const", "to": const_profile},
            ],
        )

    with Then("baseline: a user without mapped groups can insert"):
        access_clickhouse(token=mint_token(f"u_w_{uid}", []), query=insert_query)

    with And("a user in g_viewers cannot insert"):
        assert_query_rejected(
            token=mint_token(f"u_ro_{uid}", ["g_viewers"]),
            query=insert_query,
            markers=("READONLY", "readonly"),
        )

    with And("a user in g_const cannot override the CONST setting per query"):
        assert_query_rejected(
            token=mint_token(f"u_const_{uid}", ["g_const"]),
            query="SELECT 1 SETTINGS max_block_size = 7",
            markers=("SETTING_CONSTRAINT_VIOLATION", "should not be changed"),
        )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping("1.0"),
)
def mapped_profile_applied_under_load(self):
    """Mapped profiles SHALL be assigned correctly while the server is busy."""
    uid = getuid()[:8]
    node = self.context.node

    with Given("profiles, a role carrying a profile, and the token directory"):
        names = profiles_and_role(uid=uid)
        token_directory_with_profiles(names=names)

    with background_workload(node, intensity="medium"):
        for i in range(5):
            with When(f"user #{i} in g_fast logs in under load"):
                values = get_settings(token=mint_token(f"u_load_{i}_{uid}", ["g_fast"]))

            with Then("the fast profile applies"):
                assert values == ["1004", "2002", "300004"], error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_Distributed("1.0"),
)
def mapped_profile_settings_reach_other_nodes(self):
    """Settings from mapped profiles SHALL be sent to the other nodes of a
    distributed query, even though those nodes have neither the profiles
    nor the user's groups.
    """
    uid = getuid()[:8]
    cluster = f"oauth_profiles_{uid}"
    node1, node2 = self.context.node, self.context.node2

    with Given(
        "profiles and a REMOTE-capable role carrying a profile on clickhouse1 only"
    ):
        names = profiles_and_role(
            uid=uid, role_grants=("SELECT, REMOTE ON *.*",), node=node1
        )

    with And("the same role, without any profile, on clickhouse2"):
        create_role(name=names["role"], grants=("SELECT, REMOTE ON *.*",), node=node2)

    for node in (node1, node2):
        with And(f"a cluster with an interserver secret on {node.name}"):
            add_cluster_with_secret(
                cluster_name=cluster, secret=f"secret_{uid}", node=node
            )

        with And(f"the token directory on {node.name}"):
            token_directory_with_profiles(names=names, node=node)

    with When("a user in g_fast runs a cluster() query from clickhouse1"):
        body = access_clickhouse(
            token=mint_token(f"u_cluster_{uid}", ["g_fast"]),
            query=(
                f"SELECT name, value FROM cluster('{cluster}', system.settings) "
                "WHERE name IN ('max_block_size', 'max_query_size') "
                "ORDER BY name, value FORMAT TabSeparated"
            ),
        )

    with Then("both nodes see the mapped profile's settings"):
        assert body.strip().split("\n") == [
            "max_block_size\t1004",
            "max_block_size\t1004",
            "max_query_size\t300004",
            "max_query_size\t300004",
        ], error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_Distributed_StaleProfiles(
        "1.0"
    ),
)
def stale_profiles_on_previously_visited_node(self):
    """A node the user logged into directly SHALL keep the profiles from that
    login until the user's next direct login there, and its part of a
    distributed query SHALL use them (documented limitation).
    """
    uid = getuid()[:8]
    cluster = f"oauth_stale_{uid}"
    user = f"u_stale_{uid}"
    role = f"r_stale_{uid}"
    profile = f"p_stale_{uid}"
    node1, node2 = self.context.node, self.context.node2
    default_block_size = setting_default("max_block_size")
    query = (
        f"SELECT hostName(), value FROM cluster('{cluster}', system.settings) "
        "WHERE name = 'max_block_size' ORDER BY hostName() FORMAT TabSeparated"
    )

    with Given(
        "on both nodes: a REMOTE-capable role and a profile mapped from g_stale"
    ):
        for node in (node1, node2):
            create_role(name=role, grants=("SELECT, REMOTE ON *.*",), node=node)
            create_settings_profile(
                name=profile, settings="max_block_size = 1007", node=node
            )

    for node in (node1, node2):
        with And(f"a cluster with an interserver secret on {node.name}"):
            add_cluster_with_secret(
                cluster_name=cluster, secret=f"secret_{uid}", node=node
            )

        with And(f"the token directory on {node.name}"):
            configure_static_key_processor(
                secret=SECRET,
                common_roles=(role,),
                profiles_mapping=[{"from": "g_stale", "to": profile}],
                node=node,
            )

    with When("the user logs in directly to clickhouse2 while in g_stale"):
        values = get_settings(
            token=mint_token(user, ["g_stale"]),
            names=("max_block_size",),
            ip="clickhouse2",
        )
        assert values == ["1007"], error()

    with And("the user, no longer in g_stale, runs a cluster() query from clickhouse1"):
        body = access_clickhouse(token=mint_token(user, []), query=query)

    with Then("clickhouse2 still applies the stale profile from the direct login"):
        assert body.strip().split("\n") == [
            f"clickhouse1\t{default_block_size}",
            "clickhouse2\t1007",
        ], error()

    with When("the user logs in directly to clickhouse2 again without the group"):
        get_settings(
            token=mint_token(user, []), names=("max_block_size",), ip="clickhouse2"
        )

    with And("re-runs the cluster() query from clickhouse1"):
        body = access_clickhouse(token=mint_token(user, []), query=query)

    with Then("clickhouse2 no longer applies the stale profile"):
        assert body.strip().split("\n") == [
            f"clickhouse1\t{default_block_size}",
            f"clickhouse2\t{default_block_size}",
        ], error()


@TestOutline(Scenario)
@Examples(
    "section mapping expected_message",
    [
        (
            "profiles_mapping",
            [{"from": "g_x"}],
            "profiles_mapping entry 'map' must contain both 'from' and 'to' subelements",
        ),
        (
            "profiles_mapping",
            [{"to": "p_x"}],
            "profiles_mapping entry 'map' must contain both 'from' and 'to' subelements",
        ),
        (
            "profiles_mapping",
            [{"from": "", "to": "p_x"}],
            "profiles_mapping entry 'map': 'from' must not be empty",
        ),
        (
            "profiles_mapping",
            [{"from": "g_x", "to": ""}],
            "profiles_mapping entry 'map': 'to' must not be empty",
        ),
        (
            "profiles_mapping",
            [{"from": "g_dup", "to": "p_one"}, {"from": "g_dup", "to": "p_two"}],
            "profiles_mapping has duplicate 'from' value 'g_dup'",
        ),
        (
            "roles_mapping",
            [{"from": "g_x"}],
            "roles_mapping entry 'map' must contain both 'from' and 'to' subelements",
        ),
        (
            "roles_mapping",
            [{"from": "g_dup", "to": "r_one"}, {"from": "g_dup", "to": "r_two"}],
            "roles_mapping has duplicate 'from' value 'g_dup'",
        ),
    ],
)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_Validation("1.0"),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_RolesMapping_Validation("1.0"),
)
def invalid_mapping_rejected(self, section, mapping, expected_message):
    """A malformed ``profiles_mapping`` / ``roles_mapping`` entry SHALL make
    ClickHouse refuse to start with ``BAD_ARGUMENTS``.
    """
    with Given(f"I overlay user_directories/token with a malformed {section}"):
        apply_fatal_user_directories_config(
            entries={
                "user_directories": {
                    "token": {
                        "processor": "keycloak",
                        section: group_mapping_entries(mapping),
                    }
                }
            },
            expected_message=expected_message,
            config_file=f"user_directory_{section}_invalid.xml",
        )

    with Then("ClickHouse comes back up after the bad config is removed"):
        check_clickhouse_is_alive()


@TestStep(Given)
def keycloak_group(self, group_name):
    """Return the id of an existing IdP group, skipping if unsupported."""
    client = self.context.provider_client
    try:
        group = client.OAuthProvider.get_group_by_name(group_name=group_name)
    except UnsupportedByProvider as e:
        skip(str(e))
    assert group is not None, error()
    return group["id"]


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping("1.0"),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping_GroupRemoved("1.0"),
)
def provider_group_membership_drives_profile(self):
    """Adding a user to an IdP group SHALL assign the mapped profile on the
    next token, and removing the user SHALL take it away again.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"profgrp_{uid}"
    profile = f"p_can_read_{uid}"
    default_block_size = setting_default("max_block_size")

    with Given(f"I create IdP user '{username}'"):
        provider_user(username=username)

    with And("I look up the created user's id"):
        try:
            user = client.OAuthProvider.get_user_by_username(username=username)
        except UnsupportedByProvider as e:
            skip(str(e))
        assert user is not None, error()
        user_id = user["id"]

    with And("I look up the existing 'can-read' group"):
        group_id = keycloak_group(group_name="can-read")

    with And("a profile mapped from the 'can-read' group"):
        create_settings_profile(name=profile, settings="max_block_size = 1008")
        configure_openid_token_processor(
            token_cache_lifetime=0,
            profiles_mapping=[{"from": "can-read", "to": profile}],
        )

    def current_block_size():
        token = client.OAuthProvider.get_oauth_token(
            username=username, password="testpass123"
        ).access_token
        return get_settings(token=token, names=("max_block_size",))

    with When("the user logs in before joining any group"):
        values = current_block_size()

    with Then("the server default applies"):
        assert values == [default_block_size], error()

    with When(f"I add '{username}' to 'can-read' and get a fresh token"):
        client.OAuthProvider.assign_user_to_group(user_id=user_id, group_id=group_id)
        values = current_block_size()

    with Then("the mapped profile applies"):
        assert values == ["1008"], error()

    with When(f"I remove '{username}' from 'can-read' and get a fresh token"):
        client.OAuthProvider.remove_user_from_group(user_id=user_id, group_id=group_id)
        values = current_block_size()

    with Then("the mapped profile is gone"):
        assert values == [default_block_size], error()


@TestFeature
@Name("settings profiles")
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_ProfilesMapping("1.0"),
)
def feature(self):
    """Group-to-settings-profile mapping in the token user directory
    (Altinity/ClickHouse#2664, closes Altinity/ClickHouse#1032).
    """
    if not profiles_mapping_supported(self):
        skip("profiles_mapping requires Altinity/ClickHouse#2664 (antalya-26.8+)")

    Scenario(run=without_mapped_groups)
    Scenario(run=mapped_profile_overrides_default_and_role_profiles)
    Scenario(run=later_mapping_entry_wins)
    Scenario(run=profile_removed_with_group)
    Scenario(run=matches_raw_group_not_role_pipeline)
    Scenario(run=missing_mapped_profile_skipped)
    Scenario(run=mapped_profile_constraints_enforced)
    Scenario(run=mapped_profile_applied_under_load)
    Scenario(run=mapped_profile_settings_reach_other_nodes)
    Scenario(run=stale_profiles_on_previously_visited_node)
    Scenario(run=invalid_mapping_rejected)
    Scenario(run=provider_group_membership_drives_profile)
