from flask import Flask, request, send_file, Response

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/<path:file_name>", methods=["GET"])
def read_file(file_name):
    """Read binary data from specified file."""
    path = f"/var/lib/app_files/{file_name}"
    return send_file(path)


@app.route("/<path:file_name>", methods=["POST"])
def write_file(file_name):
    """Append binary data to specified file."""
    with open(f"/var/lib/app_files/{file_name}", "ab") as file:
        file.write(request.data)
    return ""


@app.route("/", methods=["GET"])
def life_check():
    """Check that the flask server is up."""
    return "1"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
