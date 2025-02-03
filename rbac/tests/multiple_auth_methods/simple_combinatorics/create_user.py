import hashlib

from collections import namedtuple

from helpers.sql.query import Query

Identification = namedtuple(
    "Identification",
    [
        "method",
        "password",
        "hash_value",
        "salt",
    ],
    defaults=[
        None,
    ]
    * 4,
)


class CreateUser(Query):
    """CREATE USER query constructor."""

    __slots__ = (
        "username",
        "identification",
    )

    def __init__(self):
        super().__init__()
        self.query: str = "CREATE USER"
        self.username: str = None
        self.identification: list[Identification] = []

    def set_username(self, name):
        self.username = name
        self.query += f" {name}"
        return self

    def set_identified(self):
        self.query += " IDENTIFIED"
        return self

    def _set_identification(self, method, value=None, extra=None):
        if len(self.identification) > 1:
            self.query += ","
        else:
            self.query += " WITH"
        if value:
            self.query += f" {method} BY '{value}'"
        else:
            self.query += f" {method}"
        if extra:
            self.query += f" {extra}"
        return self

    def set_with_no_password(self):
        self.identification.append(Identification("no_password"))
        return self._set_identification("no_password")

    def set_with_plaintext_password(self, password):
        self.identification.append(Identification("plaintext_password", password))
        return self._set_identification("plaintext_password", password)

    def set_with_sha256_hash_with_salt(self, password, salt):
        salted_password = password.encode("utf-8") + salt.encode("utf-8")
        hash_value = hashlib.sha256(salted_password).hexdigest()
        self.identification.append(
            Identification("sha256_hash_with_salt", password, hash_value, salt=salt)
        )
        return self._set_identification(
            "sha256_hash", hash_value, extra=f" SALT '{salt}'"
        )

    def set_with_double_sha1_hash(self, password):
        hash_value = hash_value = hashlib.sha1(
            hashlib.sha1(password.encode("utf-8")).digest()
        ).hexdigest()
        self.identification.append(
            Identification("double_sha1_hash", password, hash_value)
        )
        return self._set_identification("double_sha1_hash", hash_value)

    def set_with_bcrypt_password(self, password):
        self.identification.append(Identification("bcrypt_password", password))
        return self._set_identification("bcrypt_password", password)

    def __repr__(self):
        return (
            "CreateUser("
            f"{super().__repr__()}"
            f"username={self.username}, "
            f"identification={self.identification}, "
        )
