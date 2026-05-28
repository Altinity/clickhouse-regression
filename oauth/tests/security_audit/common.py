"""Shared setups and helpers for the security_audit feature.

See ``oauth/new_audit_review/combined-issues.md`` for the audit issue
catalogue.
"""

from testflows.core import *

from oauth.tests.steps.clikhouse import change_token_processors


@TestStep(Given)
def two_processor_setup(
    self,
    strict_name="keycloak",
    lenient_name="proc_b",
    lenient_secret="shared_secret_for_tests",
    lenient_algo="hs256",
    token_cache_lifetime=60,
):
    """Configure one provider-OpenID processor and one static-key processor
    alongside it. Returns both processor names and the static-key secret.

    The OpenID processor uses the active provider's discovery endpoints
    via ``client.OAuthProvider.openid_endpoints()`` so this fixture works
    against any IdP that implements the contract.
    """
    client = self.context.provider_client
    endpoints = client.OAuthProvider.openid_endpoints()

    with By(f"configuring the '{strict_name}' provider OpenID processor"):
        change_token_processors(
            processor_name=strict_name,
            processor_type="OpenID",
            token_cache_lifetime=token_cache_lifetime,
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
        )

    with And(f"adding a '{lenient_name}' static-key processor"):
        change_token_processors(
            processor_name=lenient_name,
            processor_type="jwt_static_key",
            algo=lenient_algo,
            static_key=lenient_secret,
            token_cache_lifetime=token_cache_lifetime,
        )

    yield {
        "strict_name": strict_name,
        "lenient_name": lenient_name,
        "lenient_secret": lenient_secret,
        "lenient_algo": lenient_algo,
    }


def search_server_log(node, pattern, lines=500):
    """Grep recent ``clickhouse-server.log`` lines for a pattern.

    Returns the matching lines as a single newline-joined string (empty
    string if no matches).
    """
    cmd = (
        f"tail -n {lines} /var/log/clickhouse-server/clickhouse-server.log "
        f"| grep -F -- '{pattern}' || true"
    )
    return node.command(cmd, steps=False).output.strip()
