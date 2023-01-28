from flask import Flask
import ssl
import os


https_protocol = ssl.PROTOCOL_TLSv1_2
ciphers = "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384"


app = Flask("https server")
app.secret_key = bytes(os.urandom(16))


def create_context():
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


if __name__ == "__main__":
    app.run(port=5001, debug=True, ssl_context=create_context())
