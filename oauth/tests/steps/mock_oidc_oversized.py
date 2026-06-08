"""HTTP mock that returns an oversized OIDC discovery document.

Regresses the bound on ``.well-known/openid-configuration``
downloads — an unbounded document must not grow client memory
without limit or hang the client.

Loaded as text and executed inside the bash-tools container by the
``start_oversized_oidc_discovery_mock`` step.
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
    """Serve on ``0.0.0.0:port`` returning a padded discovery JSON.

    Blocks via ``serve_forever`` — run under ``nohup`` and kill the PID when done.
    """

    HTTPServer(("0.0.0.0", port), _make_handler(padding_bytes)).serve_forever()
