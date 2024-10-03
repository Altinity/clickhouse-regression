from flask import Flask
import os

app = Flask("flask server")
app.secret_key = bytes(os.urandom(16))


@app.route("/")
def life_check():
    """Check flask is running"""
    return "Flask is running\n"


@app.route("/data", methods=["GET"])
def data():
    """Return data."""
    return "12345"


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000, debug=True)
