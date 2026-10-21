#!/usr/bin/env python3
"""Recording mocks for the DataLakeCatalog token forwarding tests.

Standard library only, so it runs in a stock ``python`` image.

Ports:
    8181  Iceberg REST catalog proxy in front of ``UPSTREAM`` (the
          ``token-forwarding-rest`` fixture). Records the ``Authorization`` header of every request,
          optionally enforces per-user namespace access, injects failures and
          per-user vended storage credentials into ``loadTable`` responses.
          ``POST /v1/oauth/tokens`` answers the client credentials grant.
    8190  RFC 8693 token exchange endpoint (any path).
    8191  AWS STS ``AssumeRoleWithWebIdentity`` endpoint (any path).

Every port also serves the control API under ``/_mock/``:
    GET  /_mock/requests[?service=catalog|token|sts]
    POST /_mock/reset
    POST /_mock/configure   {"catalog": {...}, "token": {...}, "sts": {...}}
    POST /_mock/relay       {"url", "method", "headers", "body"}  -> {"status", "body"}
    GET  /_mock/health

Tokens are HS256 JWTs. User tokens are signed with ``USER_SECRET`` (the key
ClickHouse validates); tokens this mock issues are signed with
``ISSUED_SECRET`` so tests can tell a forwarded user token from an exchanged
or service token.
"""

import base64
import copy
import hashlib
import hmac
import http.client
import json
import os
import re
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

USER_SECRET = os.environ.get("USER_SECRET", "token_forwarding_user_secret")
ISSUED_SECRET = os.environ.get("ISSUED_SECRET", "token_forwarding_issued_secret")
UPSTREAM = urllib.parse.urlparse(os.environ.get("UPSTREAM", "http://rest:8181"))

DEFAULTS = {
    "catalog": {
        # Reject requests without a valid user, exchanged or service token.
        "require_token": False,
        # {sub: [namespace, ...]}; None disables namespace enforcement.
        "allowed": None,
        # Statuses returned (and consumed) for the next catalog requests.
        "fail_next": [],
        # Only consume ``fail_next`` for requests whose token kind matches.
        "fail_token_kind": None,
        # {sub: {"s3.access-key-id": ..., ...}} injected into loadTable.
        "vended": {},
        "client_id": "clickhouse",
        "client_secret": "service_secret",
    },
    "token": {
        "fail_next": [],
        # Put the subject token into error bodies to prove ClickHouse does not echo them.
        "echo_subject_on_error": False,
        # None omits ``expires_in`` from the response.
        "expires_in": 3600,
        "client_id": "clickhouse",
        "client_secret": "service_secret",
    },
    "sts": {
        "reject_subs": [],
    },
}

lock = threading.Lock()
state = {"requests": [], "config": copy.deepcopy(DEFAULTS), "issued": 0}


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(data):
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def sign(payload, secret):
    header = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = b64url(json.dumps(payload, separators=(",", ":")).encode())
    signature = hmac.new(secret.encode(), f"{header}.{body}".encode(), hashlib.sha256)
    return f"{header}.{body}.{b64url(signature.digest())}"


def verify(token, secret):
    """Return the payload of an HS256 token signed with ``secret`` or None."""
    try:
        header, body, signature = token.split(".")
        expected = hmac.new(
            secret.encode(), f"{header}.{body}".encode(), hashlib.sha256
        )
        if not hmac.compare_digest(b64url(expected.digest()), signature):
            return None
        return json.loads(b64url_decode(body))
    except Exception:
        return None


def classify(token):
    """Return ``(kind, sub)`` for a bearer token."""
    if not token:
        return "none", None
    payload = verify(token, USER_SECRET)
    if payload is not None:
        return "user", payload.get("sub")
    payload = verify(token, ISSUED_SECRET)
    if payload is not None:
        return payload.get("kind", "issued"), payload.get("sub")
    return "invalid", None


def issue(kind, sub, **claims):
    with lock:
        state["issued"] += 1
        jti = state["issued"]
    return sign(
        {"kind": kind, "sub": sub, "jti": jti, "iat": int(time.time()), **claims},
        ISSUED_SECRET,
    )


def bearer(headers):
    value = headers.get("Authorization", "")
    return value[len("Bearer ") :] if value.startswith("Bearer ") else ""


def record(entry):
    entry["time"] = time.time()
    with lock:
        state["requests"].append(entry)


def namespace_of(path):
    match = re.match(r"^/v1/(?:[^/]+/)?namespaces/([^/?]+)", path)
    return urllib.parse.unquote(match.group(1)) if match else None


def table_of(path):
    match = re.match(r"^/v1/(?:[^/]+/)?namespaces/[^/]+/tables/([^/?]+)$", path)
    return urllib.parse.unquote(match.group(1)) if match else None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    service = None

    def log_message(self, format, *args):
        pass

    def body(self):
        if getattr(self, "_body", None) is not None:
            return self._body
        if "chunked" in self.headers.get("Transfer-Encoding", "").lower():
            chunks = []
            while True:
                size = int(self.rfile.readline().split(b";")[0].strip() or b"0", 16)
                if size == 0:
                    while self.rfile.readline() not in (b"\r\n", b"\n", b""):
                        pass
                    break
                chunks.append(self.rfile.read(size))
                self.rfile.readline()
            self._body = b"".join(chunks)
        else:
            length = int(self.headers.get("Content-Length") or 0)
            self._body = self.rfile.read(length) if length else b""
        return self._body

    def reply(self, status, payload, content_type="application/json", headers=None):
        if not isinstance(payload, (bytes, bytearray)):
            payload = (
                payload.encode()
                if isinstance(payload, str)
                else json.dumps(payload).encode()
            )
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(payload)

    def handle_any(self):
        self._body = None
        path = urllib.parse.urlparse(self.path).path
        if path.startswith("/_mock/"):
            return self.control(path)
        return getattr(self, f"serve_{self.service}")()

    do_GET = do_POST = do_DELETE = do_HEAD = do_PUT = handle_any

    def control(self, path):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if path == "/_mock/health":
            return self.reply(200, {"ok": True})
        if path == "/_mock/requests":
            service = query.get("service", [None])[0]
            with lock:
                requests = [
                    r for r in state["requests"] if service in (None, r["service"])
                ]
            return self.reply(200, requests)
        if path == "/_mock/reset":
            with lock:
                state["requests"].clear()
                state["config"] = copy.deepcopy(DEFAULTS)
            return self.reply(200, {"ok": True})
        if path == "/_mock/configure":
            changes = json.loads(self.body() or b"{}")
            with lock:
                for service, values in changes.items():
                    state["config"][service].update(values)
                config = copy.deepcopy(state["config"])
            return self.reply(200, config)
        if path == "/_mock/relay":
            return self.relay(json.loads(self.body()))
        return self.reply(404, {"error": f"unknown control path {path}"})

    def relay(self, spec):
        """Send an HTTP request on behalf of the test host (ClickHouse ports are not published)."""
        data = spec.get("body")
        request = urllib.request.Request(
            spec["url"],
            data=data.encode() if data is not None else None,
            method=spec.get("method", "POST"),
            headers=spec.get("headers", {}),
        )
        try:
            with urllib.request.urlopen(
                request, timeout=spec.get("timeout", 120)
            ) as response:
                return self.reply(
                    200,
                    {
                        "status": response.status,
                        "body": response.read().decode(errors="replace"),
                        "headers": dict(response.headers),
                    },
                )
        except urllib.error.HTTPError as e:
            return self.reply(
                200,
                {
                    "status": e.code,
                    "body": e.read().decode(errors="replace"),
                    "headers": dict(e.headers),
                },
            )
        except Exception as e:
            return self.reply(200, {"status": 0, "body": repr(e), "headers": {}})

    def serve_catalog(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self.body()
        token = bearer(self.headers)
        kind, sub = classify(token)
        with lock:
            config = copy.deepcopy(state["config"]["catalog"])

        entry = {
            "service": "catalog",
            "method": self.command,
            "path": path,
            "query": parsed.query,
            "token": token,
            "token_kind": kind,
            "sub": sub,
            "access_delegation": self.headers.get("X-Iceberg-Access-Delegation"),
        }

        if self.command == "POST" and path.rstrip("/").endswith("/oauth/tokens"):
            form = {
                k: v[0]
                for k, v in urllib.parse.parse_qs(parsed.query or body.decode()).items()
            }
            entry["form"] = form
            record(entry)
            if (
                form.get("client_id") != config["client_id"]
                or form.get("client_secret") != config["client_secret"]
            ):
                return self.reply(401, {"error": "invalid_client"})
            return self.reply(
                200,
                {
                    "access_token": issue(
                        "service", f"service:{form.get('client_id')}"
                    ),
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
                },
            )

        record(entry)

        if config["fail_next"] and config["fail_token_kind"] in (None, kind):
            with lock:
                status = state["config"]["catalog"]["fail_next"].pop(0)
            return self.reply(
                status,
                {
                    "error": {
                        "message": "injected failure",
                        "type": "MockFailure",
                        "code": status,
                    }
                },
            )

        if config["require_token"] and kind in ("none", "invalid"):
            return self.reply(
                401,
                {
                    "error": {
                        "message": "missing or invalid bearer token",
                        "type": "NotAuthorizedException",
                        "code": 401,
                    }
                },
            )

        allowed = config["allowed"]
        namespace = namespace_of(path)
        if (
            allowed is not None
            and namespace is not None
            and namespace not in allowed.get(sub or "", [])
        ):
            return self.reply(
                403,
                {
                    "error": {
                        "message": f"{sub} may not access {namespace}",
                        "type": "ForbiddenException",
                        "code": 403,
                    }
                },
            )

        status, headers, payload = self.forward(body)

        if (
            allowed is not None
            and self.command == "GET"
            and re.match(r"^/v1/(?:[^/]+/)?namespaces/?$", path)
            and status == 200
        ):
            listing = json.loads(payload)
            listing["namespaces"] = [
                ns
                for ns in listing.get("namespaces", [])
                if ".".join(ns) in allowed.get(sub or "", [])
            ]
            payload = json.dumps(listing).encode()

        if (
            self.command == "GET"
            and table_of(path)
            and status == 200
            and sub in config["vended"]
        ):
            table = json.loads(payload)
            table.setdefault("config", {}).update(config["vended"][sub])
            payload = json.dumps(table).encode()

        return self.reply(
            status, payload, headers.get("Content-Type", "application/json")
        )

    def forward(self, body):
        connection = http.client.HTTPConnection(
            UPSTREAM.hostname, UPSTREAM.port or 80, timeout=60
        )
        headers = {
            name: value
            for name, value in self.headers.items()
            if name.lower()
            not in (
                "authorization",
                "host",
                "content-length",
                "connection",
                "transfer-encoding",
            )
        }
        connection.request(self.command, self.path, body=body or None, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        connection.close()
        return response.status, dict(response.getheaders()), payload

    def serve_token(self):
        form = {k: v[0] for k, v in urllib.parse.parse_qs(self.body().decode()).items()}
        with lock:
            config = copy.deepcopy(state["config"]["token"])
        record(
            {
                "service": "token",
                "method": self.command,
                "path": self.path,
                "form": form,
                "authorization": self.headers.get("Authorization"),
                "content_type": self.headers.get("Content-Type"),
            }
        )

        if config["fail_next"]:
            with lock:
                status = state["config"]["token"]["fail_next"].pop(0)
            error = {"error": "invalid_grant", "error_description": "injected failure"}
            if config["echo_subject_on_error"]:
                error["error_description"] = (
                    f"rejected subject_token {form.get('subject_token', '')}"
                )
            return self.reply(status, error)

        if form.get("grant_type") != "urn:ietf:params:oauth:grant-type:token-exchange":
            return self.reply(400, {"error": "unsupported_grant_type"})
        if (
            form.get("client_id") != config["client_id"]
            or form.get("client_secret") != config["client_secret"]
        ):
            return self.reply(401, {"error": "invalid_client"})

        kind, sub = classify(form.get("subject_token", ""))
        if kind != "user":
            return self.reply(
                400,
                {
                    "error": "invalid_grant",
                    "error_description": "subject token is not valid",
                },
            )

        claims = {}
        if "actor_token" in form:
            actor_kind, actor_sub = classify(form["actor_token"])
            if actor_kind not in ("service", "user"):
                return self.reply(
                    400,
                    {
                        "error": "invalid_grant",
                        "error_description": "actor token is not valid",
                    },
                )
            claims["act"] = {"sub": actor_sub}

        response = {
            "access_token": issue("exchanged", sub, **claims),
            "token_type": "Bearer",
            "issued_token_type": form.get("requested_token_type")
            or "urn:ietf:params:oauth:token-type:access_token",
        }
        if config["expires_in"] is not None:
            response["expires_in"] = config["expires_in"]
        return self.reply(200, response)

    def serve_sts(self):
        parsed = urllib.parse.urlparse(self.path)
        raw = self.body().decode() or parsed.query
        params = {k: v[0] for k, v in urllib.parse.parse_qs(raw).items()}
        with lock:
            config = copy.deepcopy(state["config"]["sts"])
        token = params.get("WebIdentityToken", "")
        kind, sub = classify(token)
        record(
            {
                "service": "sts",
                "method": self.command,
                "action": params.get("Action"),
                "role_arn": params.get("RoleArn", ""),
                "role_session_name": params.get("RoleSessionName", ""),
                "web_identity_token": token,
                "token_kind": kind,
                "sub": sub,
                "authorization": self.headers.get("Authorization"),
            }
        )

        if kind != "user" or sub in config["reject_subs"]:
            return self.reply(
                400,
                '<ErrorResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/"><Error><Type>Sender</Type>'
                "<Code>InvalidIdentityToken</Code><Message>Incorrect token audience</Message></Error>"
                "<RequestId>mock</RequestId></ErrorResponse>",
                "text/xml",
            )

        expiration = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        return self.reply(
            200,
            '<AssumeRoleWithWebIdentityResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">'
            "<AssumeRoleWithWebIdentityResult><Credentials>"
            "<AccessKeyId>test</AccessKeyId><SecretAccessKey>test</SecretAccessKey>"
            f"<SessionToken>session-for-{sub}</SessionToken><Expiration>{expiration}</Expiration>"
            f"</Credentials><SubjectFromWebIdentityToken>{sub}</SubjectFromWebIdentityToken>"
            "</AssumeRoleWithWebIdentityResult>"
            "<ResponseMetadata><RequestId>mock</RequestId></ResponseMetadata>"
            "</AssumeRoleWithWebIdentityResponse>",
            "text/xml",
        )


def serve(port, service):
    handler = type(f"{service.title()}Handler", (Handler,), {"service": service})
    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    threads = [serve(8181, "catalog"), serve(8190, "token"), serve(8191, "sts")]
    for thread in threads:
        thread.join()
