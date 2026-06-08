"""Complete Keycloak OAuth 2.0 device authorization over HTTP (CI automation).

Used while ``clickhouse-client --login=device`` is polling the token endpoint so
the regression suite can approve the device code without a browser.
"""

import http.cookiejar
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Optional


def _absolute_url(realm_base: str, action: str) -> str:
    action = action.replace("&amp;", "&")
    base = realm_base.rstrip("/")
    origin_m = re.match(r"^(https?://[^/]+)", base)
    origin = origin_m.group(1) if origin_m else None
    if action.startswith("http://") or action.startswith("https://"):
        # Rewrite the host portion to match realm_base so that Keycloak
        # configured with --hostname=localhost produces usable URLs when
        # reached via a Docker network alias (e.g. keycloak:8080).
        if origin:
            path_part = re.sub(r"^https?://[^/]+", "", action)
            return origin + path_part
        return action
    if action.startswith("/"):
        if origin:
            return origin + action
        return base + action
    return f"{base}/{action}"


def _hidden_inputs(html: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for m in re.finditer(
        r'<input[^>]+type=["\']hidden["\'][^>]*>', html, flags=re.IGNORECASE
    ):
        tag = m.group(0)
        nm = re.search(r'name=["\']([^"\']+)["\']', tag)
        val = re.search(r'value=["\']([^"\']*)["\']', tag)
        if nm:
            out[nm.group(1)] = val.group(1) if val else ""
    return out


def _first_form_action(html: str) -> Optional[str]:
    m = re.search(r'<form[^>]+action=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
    return m.group(1) if m else None


def _post_form(
    opener: urllib.request.OpenerDirector,
    realm_base: str,
    html: str,
    extra_fields: Dict[str, str],
    timeout_sec: int,
) -> str:
    action = _first_form_action(html)
    if not action:
        raise RuntimeError("No HTML form found in Keycloak response")
    url = _absolute_url(realm_base, action)
    data = {**_hidden_inputs(html), **extra_fields}
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    try:
        with opener.open(req, timeout=timeout_sec) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(
            f"POST {url} -> HTTP {exc.code}\n"
            f"hidden_fields={list(_hidden_inputs(html).keys())}\n"
            f"extra_fields={list(extra_fields.keys())}\n"
            f"response_body={err_body!r}"
        ) from exc


class _RewriteHostRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow redirects, rewriting the host to the configured Keycloak origin.

    Needed because ``--hostname=localhost`` makes Keycloak emit ``Location``
    headers with ``localhost``, which is unreachable from the Docker network.
    """

    def __init__(self, origin: str) -> None:
        self._origin = origin.rstrip("/")

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        newurl = re.sub(r"^https?://[^/]+", self._origin, newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def approve_keycloak_device_user_code(
    keycloak_base_url: str,
    realm: str,
    user_code_raw: str,
    username: str,
    password: str,
    timeout_sec: int = 60,
) -> None:
    """Drive Keycloak's browser device-login pages until the device code is approved.

    Raises ``RuntimeError`` if the HTTP dance fails (unexpected HTML, HTTP errors).
    """

    base = keycloak_base_url.rstrip("/")
    realm_base = f"{base}/realms/{realm}"
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        _RewriteHostRedirectHandler(base),
    )
    opener.addheaders = [("User-Agent", "clickhouse-regression-oauth-device/1.0")]

    def get(url: str) -> str:
        req = urllib.request.Request(url, method="GET")
        with opener.open(req, timeout=timeout_sec) as resp:
            return resp.read().decode("utf-8", errors="replace")

    uc = user_code_raw.strip()
    # Keycloak 26 processes the user_code via a GET query parameter on the
    # device verification URL, which redirects to the login page with a full
    # session context.  POSTing the user_code to the bare device endpoint is
    # treated as a client device-authorization request and fails with
    # "invalid_client".
    device_url = f"{realm_base}/device"
    verify_url = f"{device_url}?user_code={urllib.parse.quote(uc)}"
    try:
        next_html = get(verify_url)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GET {verify_url} failed: HTTP {exc.code}") from exc

    for _ in range(12):
        lower = next_html.lower()
        if "invalid user code" in lower or "invalid_user_code" in lower:
            raise RuntimeError("Keycloak rejected the device user_code")
        if "login" in lower and (
            'name="username"' in lower or "name='username'" in lower
        ):
            next_html = _post_form(
                opener,
                realm_base,
                next_html,
                {"username": username, "password": password},
                timeout_sec,
            )
            continue
        if (
            "oauth grant" in lower
            or "do you approve" in lower
            or 'name="accept"' in lower
        ):
            next_html = _post_form(
                opener,
                realm_base,
                next_html,
                {"accept": "Yes", "approve": "Yes"},
                timeout_sec,
            )
            continue
        if _first_form_action(next_html) is None:
            return
        hidden = _hidden_inputs(next_html)
        if hidden:
            action = _first_form_action(next_html)
            if action:
                url = _absolute_url(realm_base, action)
                body = urllib.parse.urlencode(hidden).encode()
                req = urllib.request.Request(url, data=body, method="POST")
                with opener.open(req, timeout=timeout_sec) as resp:
                    next_html = resp.read().decode("utf-8", errors="replace")
                continue
        break

    raise RuntimeError("Keycloak device approval did not reach a terminal page")
