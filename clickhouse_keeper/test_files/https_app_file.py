import os
import argparse
import ssl

from flask import Flask


default_ciphers = "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384"


app = Flask("flask server")
app.secret_key = bytes(os.urandom(16))


def create_context(https_protocol, ciphers):
    context = ssl.SSLContext(https_protocol)
    context.set_ciphers(ciphers)
    context.load_cert_chain("/https_server.crt", "/https_server.key")

    return context


@app.route("/")
def life_check():
    """Check flask is running"""
    return "Flask is running\n"


@app.route("/data", methods=["GET"])
def data():
    """Return data."""
    return "12345"


def parse_args():
    parser = argparse.ArgumentParser(prog="https app")
    parser.add_argument("--port", default=5001, type=int)
    parser.add_argument("--protocol", default="TLSv1.2")
    parser.add_argument("--ciphers", default=default_ciphers)

    return parser.parse_args()


def main(port: int, protocol: str, ciphers: str):
    protocol = protocol.replace(".", "_")
    https_protocol = getattr(ssl, f"PROTOCOL_{protocol}")
    ssl_context = create_context(https_protocol, ciphers)

    app.run(port=port, debug=False, ssl_context=ssl_context)


if __name__ == "__main__":
    args = parse_args()

    main(args.port, args.protocol, args.ciphers)
