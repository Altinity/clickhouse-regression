"""Composite, provider-agnostic steps shared across the oauth test suite.

These build on the primitives in :mod:`oauth.tests.steps.clikhouse` and the
provider contract in :mod:`oauth.tests.steps.provider_protocol`. They exist to
keep scenarios readable: instead of copy-pasting a processor-configuration
block or a privilege-denied assertion into every file, a scenario calls one
named step.
"""

from testflows.core import *
from testflows.asserts import error

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
    change_user_directories_config,
    check_clickhouse_is_alive,
)
from oauth.tests.steps.provider_protocol import UnsupportedByProvider


@TestStep(Given)
def configure_openid_token_processor(
    self,
    *,
    processor_name="keycloak",
    processor_type="OpenID",
    common_roles=("general-role",),
    roles_filter=None,
    roles_transform=None,
    default_profile=None,
    token_cache_lifetime=None,
    username_claim=None,
    groups_claim=None,
    expected_issuer=None,
    expected_audience=None,
    userinfo_endpoint=None,
    token_introspection_endpoint=None,
    include_introspection=True,
    replace=True,
):
    """Configure the standard provider-backed OpenID token processor and
    point the token user-directory at it.

    Endpoints are pulled from the active provider
    (``self.context.provider_client.OAuthProvider.openid_endpoints()``) and
    the introspection client credentials are wired from context, so the
    same call works unchanged across identity providers.

    ``userinfo_endpoint`` / ``token_introspection_endpoint`` override the
    discovered endpoints (used to point at unreachable URLs in
    availability/fail-closed tests). Pass ``include_introspection=False``
    to configure a userinfo-only processor (no introspection endpoint or
    credentials).

    Optional knobs (cache lifetime, claim names, issuer/audience pinning)
    are forwarded as-is; ``change_token_processors`` ignores any that are
    ``None``. Pass ``common_roles=None`` to omit the ``common_roles``
    element entirely.
    """
    client = self.context.provider_client
    endpoints = client.OAuthProvider.openid_endpoints()

    introspection_endpoint = None
    introspection_client_id = None
    introspection_client_secret = None
    if include_introspection:
        introspection_endpoint = (
            token_introspection_endpoint
            if token_introspection_endpoint is not None
            else endpoints.token_introspection_endpoint
        )
        introspection_client_id = self.context.introspection_client_id
        introspection_client_secret = self.context.introspection_client_secret

    change_token_processors(
        processor_name=processor_name,
        processor_type=processor_type,
        userinfo_endpoint=(
            userinfo_endpoint
            if userinfo_endpoint is not None
            else endpoints.userinfo_endpoint
        ),
        token_introspection_endpoint=introspection_endpoint,
        introspection_client_id=introspection_client_id,
        introspection_client_secret=introspection_client_secret,
        token_cache_lifetime=token_cache_lifetime,
        username_claim=username_claim,
        groups_claim=groups_claim,
        expected_issuer=expected_issuer,
        expected_audience=expected_audience,
        replace=replace,
    )
    change_user_directories_config(
        processor=processor_name,
        common_roles=list(common_roles) if common_roles is not None else None,
        roles_filter=roles_filter,
        roles_transform=roles_transform,
        default_profile=default_profile,
    )


@TestStep(Given)
def configure_static_key_processor(
    self,
    *,
    secret,
    processor_name="proc_a",
    algo="HS256",
    token_cache_lifetime=0,
    allow_no_expiration=None,
    common_roles=("general-role",),
    default_profile=None,
    with_user_directory=True,
    replace_section=True,
    node=None,
):
    """Configure a single ``jwt_static_key`` token processor and (by
    default) point the token user-directory at it.

    This is the static-key counterpart to
    :func:`configure_openid_token_processor`. It keeps the very common
    "one HS256 processor + token directory" setup in one place so
    scenarios stay declarative.

    Pass ``with_user_directory=False`` when the scenario configures the
    user-directory itself (e.g. with a custom ``default_profile`` order).
    """
    change_token_processors(
        processor_name=processor_name,
        processor_type="jwt_static_key",
        algo=algo,
        static_key=secret,
        token_cache_lifetime=token_cache_lifetime,
        allow_no_expiration=allow_no_expiration,
        replace_section=replace_section,
        node=node,
    )

    if with_user_directory:
        change_user_directories_config(
            processor=processor_name,
            common_roles=list(common_roles) if common_roles is not None else None,
            default_profile=default_profile,
            node=node,
        )


@TestStep(Then)
def assert_query_denied(self, token, query, ip="clickhouse1"):
    """Assert ClickHouse authenticates the token but refuses ``query`` for
    lack of privileges.

    Expects HTTP 500 carrying ``ACCESS_DENIED`` / ``Not enough privileges``.
    Returns the response body.
    """
    body = access_clickhouse(token=token, status_code=500, query=query, ip=ip)
    assert "ACCESS_DENIED" in body or "Not enough privileges" in body, error()
    return body


@TestStep(Then)
def access_clickhouse_on_all_nodes(
    self,
    token,
    https=False,
    nodes=("clickhouse1", "clickhouse2", "clickhouse3"),
    status_code=200,
):
    """Authenticate ``token`` against every node in the cluster."""
    transport = "HTTPS" if https else "HTTP"
    for i, ip in enumerate(nodes, 1):
        with Then(f"node {i} ({ip}) accepts the token over {transport}"):
            access_clickhouse(token=token, ip=ip, https=https, status_code=status_code)


@TestStep(Then)
def assert_misconfigured_processor_rejects(self, token):
    """Assert token auth is unusable: the request fails with BAD_ARGUMENTS
    (HTTP 400) and the server stays alive.

    Returns the response body.
    """
    with By("checking ClickHouse rejects with BAD_ARGUMENTS"):
        body = access_clickhouse(token=token, status_code=400)

    with And("checking the server is still alive"):
        check_clickhouse_is_alive()

    return body


@TestStep(Given)
def provider_user(self, username, password="testpass123"):
    """Create an IdP user for the duration of the enclosing test, then
    delete it on teardown.

    Skips the scenario if the provider cannot create users. Yields the
    provider-assigned user id (or whatever ``create_user`` returns).
    Cleanup is best-effort and tolerates an already-deleted user.
    """
    client = self.context.provider_client

    try:
        user_id = client.OAuthProvider.create_user(username=username, password=password)
    except UnsupportedByProvider as e:
        skip(str(e))

    try:
        yield user_id
    finally:
        with Finally(f"I delete user {username}"):
            try:
                client.OAuthProvider.delete_user(username=username)
            except UnsupportedByProvider:
                pass
            except Exception as e:  # noqa: BLE001 -- best-effort teardown
                # The user may already be gone (e.g. a scenario that
                # deletes it as part of the test). Don't fail teardown.
                note(f"could not delete user {username}: {e}")
