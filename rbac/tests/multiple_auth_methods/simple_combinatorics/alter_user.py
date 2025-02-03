import hashlib
from testflows.core import *

from helpers.sql.query import Query
from .create_user import Identification


class AlterUser(Query):
    """ALTER USER query constructor."""

    __slots__ = (
        "query",
        "username",
        "not_identified",
        "identification",
        "add_identification",
        "reset_auth_methods_to_new",
        "_identification",
    )

    def __init__(self):
        super().__init__()
        self.query: str = "ALTER USER"
        self.username: str = None
        self.not_identified: str = None
        self.identification: list = []
        self.add_identification: list = []
        self.reset_auth_methods_to_new: bool = False
        self._identification: list = self.identification

    def __repr__(self):
        return (
            "AlterUser("
            f"{super().__repr__()}"
            f"username={self.username}, "
            f"not_identified={self.not_identified}, "
            f"identification={self.identification}, "
            f"add_identification={self.add_identification}, "
        )

    def set_username(self, name):
        self.username = name
        self.query += f" {name}"
        return self

    def set_reset_authentication_methods_to_new(self):
        self.reset_auth_methods_to_new = True
        self.query += " RESET AUTHENTICATION METHODS TO NEW"
        return self

    def set_add_identified(self):
        self._identification = self.add_identification
        if len(self.identification) < 2:
            self.query += " ADD IDENTIFIED"
        return self

    def set_identified(self):
        self._identification = self.identification
        if len(self.identification) < 2:
            self.query += " IDENTIFIED"
        return self

    def _set_identification(self, method, value=None, extra=None):
        if len(self._identification) > 1:
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

    def set_not_identified(self):
        self.not_identified = True
        self.query += " NOT IDENTIFIED"
        return self

    def set_with_no_password(self):
        self._identification.append(Identification("no_password"))
        return self._set_identification("no_password")

    def set_with_plaintext_password(self, password):
        self._identification.append(Identification("plaintext_password", password))
        return self._set_identification("plaintext_password", password)

    def set_with_sha256_hash_with_salt(self, password, salt):
        salted_password = password.encode("utf-8") + salt.encode("utf-8")
        hash_value = hashlib.sha256(salted_password).hexdigest()
        self._identification.append(
            Identification("sha256_hash_with_salt", password, hash_value, salt=salt)
        )
        return self._set_identification(
            "sha256_hash", hash_value, extra=f" SALT '{salt}'"
        )

    def set_with_double_sha1_hash(self, password):
        hash_value = hash_value = hashlib.sha1(
            hashlib.sha1(password.encode("utf-8")).digest()
        ).hexdigest()
        self._identification.append(
            Identification("double_sha1_hash", password, hash_value)
        )
        return self._set_identification("double_sha1_hash", hash_value)

    def set_with_bcrypt_password(self, password):
        self._identification.append(Identification("bcrypt_password", password))
        return self._set_identification("bcrypt_password", password)
