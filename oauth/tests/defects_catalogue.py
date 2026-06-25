"""Catalogue of audit defect identifiers referenced by security_audit tests.

Each constant uses the Series-A tracker ID from the canonical catalogue
as the primary identifier, with legacy F-key aliases kept for searchability.
"""

# ---------------------------------------------------------------------------
# Series A — Confirmed defects originally surfaced in audit-gist.md
# (also catalogued as F<n> / <CONTROL>-<NN> in audit-gist.md)
# ---------------------------------------------------------------------------

DEFECT_H02 = "H-02 (alias F4 / RECIP-01) — bearer token accepted on plaintext transport"
DEFECT_H03 = (
    "H-03 (alias F2 / OAUTH-06) — cache bypasses per-user processor pin "
    "when claims are empty (root cause at ExternalAuthenticators.cpp:684,708)"
)
DEFECT_H06 = (
    "H-06 (alias F16 / AUTHZ-02) — FIXED in antalya-26.3 (PR #1777). "
    "Invalid roles_filter regex now fails closed: TokenAccessStorage "
    "validates the RE2 pattern at construction and throws BAD_ARGUMENTS."
)
DEFECT_H07 = (
    "H-07 (alias F17 / AVAIL-05) — FIXED in antalya-26.3 (PR #1777). "
    "Token processor parse failures now disable ALL token auth "
    "(all-or-nothing parseTokenProcessors)."
)
DEFECT_H16 = (
    "H-16 (alias F20 / TOKEN-06) — FIXED in antalya-26.3 (PR #1777). "
    "JwksJwtProcessor::resolveAndValidate now has a whole-body try/catch "
    "mirroring StaticKeyJwtProcessor."
)
DEFECT_H19 = (
    "H-19 (alias F9+F10 / DOS-01 / AVAIL-02 / AVAIL-03) — global "
    "ExternalAuthenticators::mutex held across unbounded outbound HTTP "
    "(JWKS / userinfo / introspection); a slow IdP stalls the entire "
    "auth subsystem"
)
DEFECT_H20 = (
    "H-20 (alias F7 / LEAK-03) — Authorization header retained in "
    "client_info.http_headers and reachable via getClientHTTPHeader / "
    "checkHTTPBasicCredentials / forward_headers (supersedes M-03)"
)
DEFECT_M03 = (
    "M-03 (superseded by H-20) — Authorization header exposed via "
    "getClientHTTPHeader. Use DEFECT_H20 in new tests; this constant "
    "is retained for legacy references only."
)
DEFECT_M05 = (
    "M-05 (alias F3 / OAUTH-07) — OpenID JWT-fastpath can throw before "
    "userinfo fallback executes"
)
DEFECT_M06 = (
    "M-06 (alias F8 / TOKEN-05) — FIXED in antalya-26.3 (PR #1799). "
    "Introspection is now performed when introspection_client_id and "
    "introspection_client_secret are configured."
)

# ---------------------------------------------------------------------------
# Series A — High severity (H-XX from all-issues.md)
# ---------------------------------------------------------------------------

DEFECT_H05 = "H-05 — native TCP session survives token expiration"
DEFECT_H10 = "H-10 — opaque processor accepts wrong audience / client"
DEFECT_H14 = (
    "H-14 — cache entry written before per-user claims check; lacks processor identity"
)
DEFECT_H17 = "H-17 — rejected claim check still primes cache via const_cast"
DEFECT_H22 = "H-22 — users.xml JWT processor pin not enforced on cache hit (no SQL grammar for token_processor_name)"
DEFECT_H23 = "H-23 — cross-provider identity collision via shared sub claim"
DEFECT_H25 = "H-25 — token user directory first in chain locks out non-JWT users (LOGICAL_ERROR aborts MultipleAccessStorage chain)"

# ---------------------------------------------------------------------------
# Series A — Medium severity (M-XX from all-issues.md)
# ---------------------------------------------------------------------------

DEFECT_M01 = "M-01 — processor dispatch order non-deterministic across restarts"
DEFECT_M02 = "M-02 — enable_token_auth=0 not honored on SYSTEM RELOAD CONFIG"
DEFECT_M13 = "M-13 — invalid roles_transform regex silently passes roles through"
DEFECT_M14 = (
    "M-14 — no JWT typ / token-class enforcement; id_token accepted as access token"
)
DEFECT_M17 = "M-17 — dynamic token user created with AnyHostTag (no IP allowlist)"
DEFECT_M27 = "M-27 — empty sub claim collapses multiple tokens to one user"
DEFECT_M28 = "M-28 — active TCP session survives processor removal at reload"
DEFECT_M29 = "M-29 — newline / control chars in claim values inject forged log lines"
DEFECT_M30 = "M-30 — same client-supplied session_id shares temp tables across tokens"
DEFECT_M32 = (
    "M-32 — worked default-user impersonation chain (concrete H-14 exploitation)"
)

# ---------------------------------------------------------------------------
# Series B — M-NEW-XX from all-issues.md (logical-fuzzing + Jira passes)
# ---------------------------------------------------------------------------

DEFECT_M_NEW_01 = (
    "M-NEW-01 — missing default_profile silently auto-provisions "
    "unrestricted users (TokenAccessStorage::assignProfileNoLock)"
)

# ---------------------------------------------------------------------------
# Series A — Low severity / hardening (L-XX from all-issues.md)
# ---------------------------------------------------------------------------

DEFECT_L08 = "L-08 — attacker-controlled sub claim burns victim's failed-auth quota"
DEFECT_L09 = "L-09 — sub with control chars reaches system.users / dynamic users"
DEFECT_L11 = "L-11 — future iat claim silently accepted (no upper-bound check)"
DEFECT_L12 = "L-12 — unknown JWT crit header silently accepted"
DEFECT_L13 = "L-13 — TRACE-level logs expose username and group names (PII)"
DEFECT_L14 = "L-14 — Unicode-homograph sub collision creates indistinguishable users"
DEFECT_L16 = "L-16 — unknown kid values flood server logs (enumeration / log noise)"
DEFECT_L17 = (
    "L-17 — quota key derived from attacker-controlled sub (DoS amplification of L-08)"
)

# ---------------------------------------------------------------------------
# New findings from runtime audit-review (continue Series A per
# all-issues.md §4: H-30, M-33, L-22, ...)
# ---------------------------------------------------------------------------

DEFECT_H_NEW_30 = (
    "H-NEW-30 — JWT exp never propagated to cache TTL on the "
    "StaticKeyJwtProcessor / JwksJwtProcessor fastpaths. A JWT past "
    "its IdP-issued exp keeps authenticating for up to "
    "token_cache_lifetime (default 3600s) because resolveAndValidate "
    "never calls credentials.setExpiresAt(decoded_jwt.get_expires_at()) "
    "on the JWT codepaths. The opaque/OpenID-userinfo paths set it "
    "correctly. Violates SRS 13.1.5 'Common.Cache.Behavior' which "
    "mandates cache_entry_expires_at = min(token.exp, now + "
    "token_cache_lifetime). Code anchors: "
    "src/Access/TokenProcessorsJWT.cpp:375-563 vs "
    "TokenProcessorsOpaque.cpp:117,198,340; cache write at "
    "src/Access/ExternalAuthenticators.cpp:624-640. Logged in "
    "all-issues.md as H-NEW-30."
)

DEFECT_M33 = (
    "M-33 (alias CFG-04) — duplicate <token> entries inside "
    "<user_directories> are silently accepted: ClickHouse merges the "
    "duplicate siblings without raising and auth proceeds with whichever "
    "entry won the merge. SRS 6.2.1.1.4 says auth SHALL NOT be allowed "
    "when user_directories contains multiple duplicate entries. Same "
    "fail-open family as H-06 / H-07 — invalid config silently tolerated. "
    "Code anchor: src/Access/AccessControl.cpp / TokenAccessStorage "
    "configuration parser does not enforce uniqueness on <token> "
    "children. New finding from runtime regression testing — registered "
    "as next Series-A medium per all-issues.md §4."
)

# ---------------------------------------------------------------------------
# Backwards-compatible aliases (legacy F-key names).
# New code should reference the Series-A ID directly.
# ---------------------------------------------------------------------------

DEFECT_F2 = DEFECT_H03
DEFECT_F3 = DEFECT_M05
DEFECT_F4 = DEFECT_H02
DEFECT_F7 = DEFECT_H20
DEFECT_F8 = DEFECT_M06
DEFECT_F9 = DEFECT_H19
DEFECT_F10 = DEFECT_H19
DEFECT_F16 = DEFECT_H06
DEFECT_F17 = DEFECT_H07
DEFECT_F20 = DEFECT_H16
DEFECT_M_NEW_50 = DEFECT_M33
