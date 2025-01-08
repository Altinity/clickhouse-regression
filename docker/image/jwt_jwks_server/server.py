import sys
import signal
from bottle import response, route, run, request

stored_parameters = {
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS512",
            "kid": "mykid",
            "n": "0RRsKcZ5j9UckjioG4Phvav3dkg2sXP6tQ7ug0yowAo_u2HffB-1OjKuhWTpA3E3YkMKj0RrT-tuUpmZEXqCAipEV7XcfCv3o"
            "7Poa7HTq1ti_abVwT_KyfGjoNBBSJH4LTNAyo2J8ySKSDtpAEU52iL7s40Ra6I0vqp7_aRuPF5M4zcHzN3zarG5EfSVSG1-gT"
            "kaRv8XJbra0IeIINmKv0F4--ww8ZxXTR6cvI-MsArUiAPwzf7s5dMR4DNRG6YNTrPA0pTOqQE9sRPd62XsfU08plYm27naOUZ"
            "O5avIPl1YO5I6Gi4kPdTvv3WFIy-QvoKoPhPCaD6EbdBpe8BbTQ",
            "e": "AQAB",
        },
    ]
}


@route("/.well-known/jwks.json")
def server():
    response.status = 200
    response.content_type = "application/json"
    return stored_parameters


@route("/")
def ping():
    """Health check endpoint."""
    response.content_type = "text/plain"
    response.set_header("Content-Length", 2)
    return "OK"


def handle_sigterm(*args):
    """Handle SIGTERM for graceful shutdown."""
    print("SIGTERM received. Shutting down gracefully...")
    sys.exit(0)


@route("/parameters", method="POST")
def update_jwks():
    """Update JWKS parameters."""
    global stored_parameters
    try:
        payload = request.json
        if not payload:
            response.status = 400
            return {"error": "Invalid JSON payload"}

        # Store parameters in memory
        stored_parameters = payload

        response.status = 200
        return {"message": "Parameters stored successfully"}
    except Exception as e:
        response.status = 500
        return {"error": f"An error occurred: {str(e)}"}


signal.signal(signal.SIGTERM, handle_sigterm)


run(host="0.0.0.0", port=int(sys.argv[1]))
