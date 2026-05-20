"""HTTP mock that returns an oversized OIDC discovery document.

Used to regress the bound on ``.well-known/openid-configuration``
downloads in clickhouse-client's OAuth front half: an unbounded
discovery document MUST NOT grow client memory without limit, MUST
NOT hang the client, and MUST surface as a clean failure.

The module is loaded as text by the
``start_oversized_oidc_discovery_mock`` step in ``client_login.py``
and executed inside the ``bash-tools`` container — same idiom as
``keycloak_device_flow.py``. The step appends a call to
:func:`run_oversized_oidc_discovery_mock` with the desired
``port`` / ``padding_bytes`` and writes the bundle through
``nohup python3 …``.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer


def _make_handler(padding_bytes: int):
    """Build a request handler that pads the discovery JSON to ``padding_bytes`` of x's."""

    class OversizedDiscoveryHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # noqa: ARG002 — silence stderr
            pass

        def do_GET(self):
            if ".well-known/openid-configuration" not in self.path:
                self.send_response(404)
                self.end_headers()
                return
            pad = b"x" * padding_bytes
            body = b'{"issuer":"http://bash-tools:0/x","pad":"' + pad + b'"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return OversizedDiscoveryHandler


def run_oversized_oidc_discovery_mock(port: int, padding_bytes: int) -> None:
    """Serve forever on ``0.0.0.0:port`` returning a padded discovery JSON.

    Any path containing ``.well-known/openid-configuration`` receives a
    200 with a JSON body whose ``pad`` field is exactly
    ``padding_bytes`` bytes of ``"x"``; every other path receives a
    bare 404. ``serve_forever`` blocks — the caller is expected to run
    this under ``nohup`` and kill the PID when done.
    """

    HTTPServer(("0.0.0.0", port), _make_handler(padding_bytes)).serve_forever()
