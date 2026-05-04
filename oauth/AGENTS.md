# OAuth suite — agent guide

Living reference for anyone (human or AI) working in `oauth/`. Follows
the [AGENTS.md](https://www.agents.md/) convention: this file is the
agent-facing equivalent of `README.md`. The closest `AGENTS.md` to a
file being edited wins, so feel free to add nested ones inside
`tests/security_audit/` or `tests/client_oauth_login/` if those
sub-suites grow their own conventions.

Keep this short, accurate, and updated as the suite evolves.

---

## 1. What this suite tests

ClickHouse's OAuth/OIDC authentication path:

- **Server-side**: token-processor configuration (`<token_processors>`),
  user-directory mapping (`<user_directories>`), JWT validation, OpenID
  discovery, audience/issuer pinning, role mapping from IdP groups,
  caching/refresh, fail-closed behaviour.
- **Client-side** (`tests/client_oauth_login/`): the
  `clickhouse-client --login` flow added in Altinity PR #1606 — argument
  validation, credentials-file loading, device/browser-flow plumbing,
  refresh-token cache, segfault guards from PR #1696/#1697/#1698 and
  upstream issue #103603.

Provider used by default: **Keycloak** running in docker-compose
alongside ClickHouse. Azure and Google are pluggable but most automation
lives on Keycloak — see §4.

---

## 2. Repository layout

```
oauth/
├── regression.py                         # entry point: ./regression.py …
├── envs/keycloak/keycloak_env/           # docker-compose + realm-export.json
├── requirements/                         # SRS + Python @Requirements registry
├── tests/
│   ├── steps/
│   │   ├── provider_protocol.py          # OAuthToken, OpenIDEndpoints, contract
│   │   ├── keycloak_realm.py             # Keycloak provider (full impl)
│   │   ├── azure_application.py          # Azure provider (token-only)
│   │   ├── google_application.py         # Google provider (token-only)
│   │   └── clikhouse.py                  # access_clickhouse, change_token_processors, …
│   ├── authentication.py                 # baseline: valid/empty/tampered tokens
│   ├── tokens.py                         # processor-config (OpenID discovery, bad jwks_uri)
│   ├── jwt_manipulation.py               # JWT-mutation negatives (alg=none, exp past, …)
│   ├── parameters_and_caching.py         # username_claim, groups_claim, expected_*, cache
│   ├── access_control.py                 # cross-realm / cross-client authz negatives
│   ├── groups.py                         # role mapping, dynamic membership, disable/delete
│   ├── tls.py                            # HTTPS happy path
│   ├── configuration.py                  # processor-type validation
│   ├── sanity.py                         # 2-line sanity scenarios
│   ├── security_audit/                   # H-/M-/L- audit-finding regressions
│   └── client_oauth_login/               # `clickhouse-client --login` (PR #1606+)
├── README.md                             # how to provision Azure (manual)
└── AGENTS.md                             # this file
```

---

## 3. How to run

Standard regression pattern shared with the rest of the repo. Always
provide a `--clickhouse` package URL.

### 3.1 Keycloak (default — no extra args needed)

```bash
cd oauth
./regression.py \
  --clickhouse <ch-package-url> \
  --identity-provider keycloak
```

The compose file at `envs/keycloak/keycloak_env/docker-compose.yml`
brings up Keycloak (with `--hostname=localhost`), three ClickHouse
nodes, ZooKeeper, Grafana, and a `bash-tools` container used by the
test steps to run `curl`/`docker exec`-style commands inside the Docker
network.

### 3.2 Run a single sub-feature

```bash
./regression.py \
  --clickhouse <ch-package-url> \
  --identity-provider keycloak \
  --only "/oauth/access control/*"

./regression.py \
  --clickhouse <ch-package-url> \
  --identity-provider keycloak \
  --only "/oauth/client_oauth_login/*"
```

Path patterns mirror `@Name(...)` decorators in `feature.py` /
`tests/*.py`.

### 3.3 Azure

Pre-requisites are in `README.md` (manual app-registration steps).
Then:

```bash
./regression.py \
  --clickhouse <ch-package-url> \
  --identity-provider azure \
  --tenant-id <tenant_id> \
  --client-id <app_id> \
  --client-secret <client_secret>
```

Most Azure scenarios `Skip` because identity-management automation is
not implemented (see §4).

### 3.4 Google

Selectable but mostly skipped. Refresh token must be obtained out of
band via `tests/steps/google_application.get_refresh_token_interactive`:

```bash
./regression.py \
  --clickhouse <ch-package-url> \
  --identity-provider google \
  --client-id <client_id> \
  --client-secret <client_secret> \
  --refresh-token <refresh_token>
```

---

## 4. The provider abstraction (`provider_protocol.py`)

The same scenarios MUST run unchanged against any IdP. The contract
that makes this possible lives in `tests/steps/provider_protocol.py`.

### 4.1 What's in the contract

```110:135:oauth/tests/steps/provider_protocol.py
REQUIRED_METHODS = (
    # Core token + endpoint access — every provider must implement these.
    "get_oauth_token",
    "openid_endpoints",
    "default_idp",
    # JWT mutation (used heavily by tokens / jwt_manipulation / tls /
    # security_audit). Provider-agnostic implementation lives in
    # ``provider_protocol`` itself but providers re-export it for
    # discoverability.
    "modify_jwt_token",
)

OPTIONAL_METHODS = (
    "create_user",
    "delete_user",
    "disable_user",
    "enable_user",
    "get_user_by_username",
    ...
)
```

**Required** methods MUST be implemented. **Optional** methods MAY
raise `UnsupportedByProvider` via the `unsupported(method_name)` helper
— scenarios that depend on them will `Skip`, not fail.

### 4.2 Uniform return types

```python
@dataclass
class OAuthToken:
    access_token: str
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)
```

Tests **always** read `.access_token`. Never `["access_token"]` (the
dict-style accessor is kept only for legacy compatibility and will be
removed once the audit doc says so).

```python
@dataclass
class OpenIDEndpoints:
    issuer: str
    jwks_uri: str
    userinfo_endpoint: str
    token_introspection_endpoint: Optional[str] = None
    configuration_endpoint: Optional[str] = None
    expected_audience: Optional[str] = None
```

Tests fetch endpoints via `client.OAuthProvider.openid_endpoints()`.
Never hardcode Keycloak URLs in scenarios.

### 4.3 How tests use it

```python
# tests/parameters_and_caching.py — provider-agnostic pattern
client = self.context.provider_client

with Given("I configure the processor with provider OpenID endpoints"):
    endpoints = client.OAuthProvider.openid_endpoints()
    change_token_processors(
        processor_name="keycloak",
        processor_type="OpenID",
        userinfo_endpoint=endpoints.userinfo_endpoint,
        token_introspection_endpoint=endpoints.token_introspection_endpoint,
        jwks_uri=endpoints.jwks_uri,
    )

with And("I get a valid token"):
    token = client.OAuthProvider.get_oauth_token().access_token

with Then("ClickHouse accepts the token"):
    access_clickhouse(token=token, status_code=200)
```

For optional operations:

```python
# tests/groups.py — Skip when the provider can't do it
from oauth.tests.steps.provider_protocol import UnsupportedByProvider

with Given(f"I create user '{username}'"):
    try:
        client.OAuthProvider.create_user(username=username, password="testpass123")
    except UnsupportedByProvider as e:
        skip(str(e))
```

### 4.4 Step-wrapping discipline (don't trip on this)

`@TestStep`-decorated functions MUST be called inside
`with Given/And/When/Then(...)`. Calling them directly inside a
`@TestScenario` body causes:

```
ValueError: too many values to unpack (expected 2)
```

…because the testflows step wrapper re-shapes return values.

---

## 5. Adding a new identity provider

Worked example: hypothetical `okta` provider.

### 5.1 Add the provider module

Create `oauth/tests/steps/okta.py`:

```python
"""Okta provider implementation."""

from testflows.core import *

from oauth.tests.steps.clikhouse import (
    change_token_processors,
    change_user_directories_config,
)
from oauth.tests.steps.provider_protocol import (
    OAuthToken,
    OpenIDEndpoints,
    modify_jwt_token as _shared_modify_jwt_token,
    unsupported,
)


@TestStep(Given)
def get_oauth_token(self, username=None, password=None):
    """Acquire an Okta access token (impl: ROPC, JWT-bearer, or pre-baked)."""
    # ... real implementation ...
    return OAuthToken(
        access_token=resp["access_token"],
        refresh_token=resp.get("refresh_token"),
        id_token=resp.get("id_token"),
        token_type=resp.get("token_type"),
        expires_in=resp.get("expires_in"),
        raw=resp,
    )


@TestStep(Given)
def openid_endpoints(self):
    org = self.context.okta_org  # e.g. "altinity.okta.com"
    base = f"https://{org}/oauth2/default"
    return OpenIDEndpoints(
        issuer=base,
        jwks_uri=f"{base}/v1/keys",
        userinfo_endpoint=f"{base}/v1/userinfo",
        token_introspection_endpoint=f"{base}/v1/introspect",
        configuration_endpoint=f"{base}/.well-known/openid-configuration",
        expected_audience=self.context.client_id,
    )


@TestStep(Given)
def default_idp(self, node=None, common_roles=None, roles_filter=None):
    """Configure ClickHouse to validate against Okta."""
    endpoints = openid_endpoints()
    change_token_processors(
        processor_name="okta",
        processor_type="OpenID",
        userinfo_endpoint=endpoints.userinfo_endpoint,
        token_introspection_endpoint=endpoints.token_introspection_endpoint,
        jwks_uri=endpoints.jwks_uri,
        node=node,
    )
    change_user_directories_config(
        processor="okta",
        node=node,
        common_roles=common_roles,
        roles_filter=roles_filter,
    )


class OAuthProvider:
    """Provider implementation for Okta. Implements the contract in
    ``oauth.tests.steps.provider_protocol``."""

    get_oauth_token = get_oauth_token
    openid_endpoints = openid_endpoints
    default_idp = default_idp
    modify_jwt_token = staticmethod(_shared_modify_jwt_token)

    # Implement what the SDK supports:
    # create_user = create_okta_user
    # delete_user = delete_okta_user

    # Mark the rest unsupported so dependent scenarios Skip:
    create_user = unsupported("create_user")
    delete_user = unsupported("delete_user")
    disable_user = unsupported("disable_user")
    enable_user = unsupported("enable_user")
    get_user_by_username = unsupported("get_user_by_username")
    create_group = unsupported("create_group")
    delete_group = unsupported("delete_group")
    get_group_by_name = unsupported("get_group_by_name")
    assign_user_to_group = unsupported("assign_user_to_group")
    remove_user_from_group = unsupported("remove_user_from_group")
    disable_client = unsupported("disable_client")
    enable_client = unsupported("enable_client")
    invalidate_user_sessions = unsupported("invalidate_user_sessions")
    create_realm = unsupported("create_realm")
    delete_realm = unsupported("delete_realm")
    create_client_in_realm = unsupported("create_client_in_realm")
    get_oauth_token_for_client = unsupported("get_oauth_token_for_client")
```

### 5.2 Wire it into `regression.py`

```python
# oauth/regression.py — _load_provider_module

def _load_provider_module(identity_provider):
    if identity_provider == "keycloak":
        module = keycloak
    elif identity_provider == "azure":
        from oauth.tests.steps import azure_application as azure
        module = azure
    elif identity_provider == "google":
        from oauth.tests.steps import google_application as google
        module = google
    elif identity_provider == "okta":          # ← add here
        from oauth.tests.steps import okta
        module = okta
    else:
        raise ValueError(f"Unknown identity provider: {identity_provider}")

    assert_provider_contract(module)            # ← contract-checked at startup
    return module
```

…and bootstrap any provider-specific context the same way Keycloak/Azure
do:

```python
# oauth/regression.py — regression() body
elif identity_provider_lower == "okta":
    self.context.okta_org = okta_org           # whatever you need
    self.context.client_id = client_id
    self.context.client_secret = client_secret
```

If you need a new CLI flag (e.g. `--okta-org`), add it in `argparser`:

```python
parser.add_argument(
    "--okta-org",
    type=str, dest="okta_org",
    help="Okta org domain (e.g. altinity.okta.com)",
    default=None,
)
```

…and thread it through the `regression()` signature.

### 5.3 (If applicable) Add a docker-compose env

Mirror the Keycloak structure under `oauth/envs/okta/okta_env/` with a
matching `docker-compose.yml`. Most cloud-IdP runs won't need this —
the cluster only contains ClickHouse + `bash-tools`.

### 5.4 Verify the contract is satisfied

```bash
cd /path/to/clickhouse-regression
python -c "
import sys; sys.path.insert(0, '.')
from oauth.tests.steps.provider_protocol import assert_provider_contract
from oauth.tests.steps import okta
assert_provider_contract(okta)
print('okta: contract OK')
"
```

If a required method is missing the assertion fires immediately with a
useful message — fix and re-run.

### 5.5 Run the suite

```bash
./regression.py --identity-provider okta --okta-org altinity.okta.com …
```

Scenarios that depend on `unsupported`-marked methods will `Skip`
automatically; the rest run unchanged.

---

## 6. Code style

The repo does not run a formatter in CI for this folder, but new code
should match what's already there:

- **Python 3.10+**, four-space indent, double-quoted strings.
- **Imports**: stdlib first, then `testflows.*`, then `helpers.*`,
  then `oauth.*`. Group `oauth.tests.steps.*` together.
- **Step helpers** (`@TestStep(Given|When|Then)`) live in
  `tests/steps/*.py`. Tests never call `node.command(...)` directly —
  go through a step helper so cleanup and `Skip` semantics work.
- **Scenarios**: every helper call MUST be inside a
  `with Given/And/When/Then("…"):` block. See §7 pitfall #1 for the
  symptom when this rule is violated.
- **Provider access**: always
  `client = self.context.provider_client` →
  `client.OAuthProvider.<method>(...)`. Never import provider modules
  directly inside test files.
- **Tokens**: read `.access_token`, never `["access_token"]`. The
  dict-style accessor on `OAuthToken` exists only for backwards
  compatibility and will be removed.
- **HTTP queries**: route through `access_clickhouse(...)` — it POSTs
  the query body so quoting works. Don't hand-roll `curl` URL
  encoding.
- **Comments**: explain non-obvious intent only. Don't narrate code
  (`# Get the token`).
- **Docstrings**: short (1–3 lines) on every scenario, describing what
  ClickHouse SHALL do — these often become the assertion message.
- **No emojis** in test code, comments, or commit messages.

## 7. Security considerations

This suite *tests* an authentication subsystem. A few hard rules:

- **Never commit real OAuth tokens, refresh tokens, client secrets, or
  Azure tenant IDs.** Pass them via CLI flags (`--client-secret`,
  `--refresh-token`, `--tenant-id`) or environment, not via files
  checked into git. The `.gitignore` covers the obvious paths but
  `git diff` your changes before committing.
- **The Keycloak realm-export.json** at
  `envs/keycloak/keycloak_env/keycloak-config/realm-export.json` is
  intentionally pre-populated with weak credentials (`demo:demo`,
  `grafana-secret`). They are safe because they only exist inside the
  ephemeral docker-compose network. Do not reuse these values in any
  other environment.
- **Generated test users** must use `helpers.common.getuid()` suffixes
  to avoid colliding with the seeded `demo` user. Always clean up in
  a `Finally:` block (see `groups.py` for the pattern).
- **Negative tests assert *failure modes*.** If a scenario passes
  while swallowing exceptions (`except: note(...)`), it is a false
  positive — file it, don't ship it. `audit-suite-review.md` §2.3 /
  §3.7 describes the exact pattern to avoid.
- **`assert_no_segfault(...)`** in `tests/steps/client_login.py` is
  load-bearing: any new client-side scenario MUST call it after every
  `clickhouse-client` invocation, because half the bugs covered by
  PR #1606+ are crashes that exit non-zero with otherwise innocuous
  output.
- **Logs may contain tokens.** When adding a new step that captures
  output (`node.command(...)`), make sure it doesn't leak the
  `Authorization: Bearer …` header into the testflows log. The
  existing helpers already redact; copy them, don't reinvent.

## 8. Commits and PRs

- One concern per commit; keep diffs reviewable.
- Commit message format: imperative subject ≤ 72 chars
  (`oauth: fix dynamic_group_membership_update cache observation`),
  blank line, then a body explaining *why* (the *what* is in the
  diff). No emojis.
- A change that touches `tests/steps/provider_protocol.py` MUST update
  every concrete provider in the same commit and re-run the contract
  smoke test (§5.4).
- A change that adds a step helper used by `tests/security_audit/*`
  MUST verify imports across the package — see the
  `python -c "import oauth.tests.security_audit.feature"`
  one-liner that we use as a smoke test.
- PRs touching the suite should reference the upstream
  PR/issue number(s) being verified (e.g. `Altinity/ClickHouse#1606`,
  `ClickHouse/ClickHouse#103603`) so the test↔fix mapping stays
  searchable.
- If you change a CLI flag, update §3 of this file in the same PR.
- If you change the provider contract, update §4 of this file in the
  same PR.

---

## 9. Common pitfalls

| Symptom                                                                           | Cause                                                                                                                                        | Fix                                                                                                                                         |
|-----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| `ImportError: cannot import name X from oauth.tests.steps.clikhouse`              | Step helper referenced by tests but never added/restored.                                                                                    | Add it in `clikhouse.py`. The `keycloak_openid_processor_args`/`change_user_jwt_auth`/etc. precedent is in §3.2 of `audit-suite-review.md`. |
| `ValueError: too many values to unpack (expected 2)`                              | `@TestStep` called outside a `with` block.                                                                                                   | Wrap the call: `with When("…"): exit_code, output = run_…(…)`.                                                                              |
| `TypeError: string indices must be integers` on `token["access_token"]`           | Test still using the legacy dict accessor against a non-Keycloak provider.                                                                   | Switch to `.access_token`.                                                                                                                  |
| `UnsupportedByProvider: 'create_user' is not implemented for this OAuth provider` | Scenario hit an optional method on a provider that doesn't have it.                                                                          | Wrap in `try/except UnsupportedByProvider as e: skip(str(e))`.                                                                              |
| Scenario passes but assertion never fires                                         | Common with `try: ... except Exception: note(...)` patterns.                                                                                 | Don't swallow. If a step *should* succeed, let exceptions propagate.                                                                        |
| Wrong `iss` / `aud` mismatch on a fresh box                                       | Keycloak hostname-vs-issuer mismatch — `--hostname=localhost` puts `localhost:8080` in `iss` while ClickHouse hits `keycloak:8080` for JWKS. | Use `client.OAuthProvider.openid_endpoints().issuer` for issuer pinning, never hardcode.                                                    |

---

## 10. Where to look when changes are requested

- **"Add a test for behaviour X"** → pick the right file under `tests/`
  by topic (authn vs authz vs caching vs client-side); copy a sibling
  scenario and adapt; never reach into provider modules directly,
  always go through `client.OAuthProvider.*`.
- **"Test against a new IdP"** → §5 above.

Keep this file accurate. If you change the contract, update §4. If you
add a CLI flag, update §3. If you tear out a sub-suite, fix §2.
