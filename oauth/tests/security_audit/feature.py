"""Security audit regression tests.

See ``oauth/new_audit_review/combined-issues.md`` for the audit issue
catalogue. Each child feature is identified only by its issue ID(s);
details intentionally not duplicated here.
"""

from testflows.core import *


@TestFeature
@Name("security audit")
def feature(self):
    """See ``oauth/new_audit_review/combined-issues.md``."""

    Feature(run=load("oauth.tests.security_audit.plaintext_transport", "feature"))
    Feature(run=load("oauth.tests.security_audit.roles_filter_fail_open", "feature"))
    Feature(run=load("oauth.tests.security_audit.processor_parse_failure", "feature"))
    Feature(run=load("oauth.tests.security_audit.openid_fallback", "feature"))
    Feature(run=load("oauth.tests.security_audit.authorization_header_leak", "feature"))
    Feature(run=load("oauth.tests.security_audit.introspection_endpoint", "feature"))
    Feature(run=load("oauth.tests.security_audit.provider_availability", "feature"))
    Feature(run=load("oauth.tests.security_audit.cache_processor_binding", "feature"))
    Feature(run=load("oauth.tests.security_audit.processor_pin_bypass", "feature"))
    Feature(run=load("oauth.tests.security_audit.cross_provider_identity", "feature"))
    Feature(run=load("oauth.tests.security_audit.token_tampering", "feature"))
    Feature(run=load("oauth.tests.security_audit.log_hygiene", "feature"))
    Feature(run=load("oauth.tests.security_audit.quota_binding", "feature"))
    Feature(run=load("oauth.tests.security_audit.long_lived_session", "feature"))
    Feature(run=load("oauth.tests.security_audit.fail_closed_config", "feature"))
    Feature(run=load("oauth.tests.security_audit.storage_chain_lockout", "feature"))
    Feature(run=load("oauth.tests.security_audit.session_sharing", "feature"))
    Feature(run=load("oauth.tests.security_audit.authz_sprawl", "feature"))
