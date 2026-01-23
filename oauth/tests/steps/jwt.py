from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_private_key(
    public_exponent=65537, key_size=2048, file_name="new_private_key"
):
    private_key = rsa.generate_private_key(
        public_exponent=public_exponent, key_size=key_size, backend=default_backend()
    )

    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    with open(file_name, "wb") as pem_file:
        pem_file.write(pem_private_key)
