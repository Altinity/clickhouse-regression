import bcrypt
import hashlib

from collections import namedtuple

from .query import Query
from .create_user import Identification, Grantees, Setting

Username = namedtuple(
    "Username",
    ["name", "renamed"],
    defaults=[
        None,
    ]
    * 2,
)


class AlterUser(Query):
    """
    ALTER USER [IF EXISTS] name1 [ON CLUSTER cluster_name1] [RENAME TO new_name1]
        [, name2 [ON CLUSTER cluster_name2] [RENAME TO new_name2] ...]
    [RESET AUTHENTICATION METHODS TO NEW]
    [NOT IDENTIFIED | IDENTIFIED | ADD IDENTIFIED {[WITH {no_password | plaintext_password | sha256_password | sha256_hash | double_sha1_password | double_sha1_hash}] BY {'password' | 'hash'}} | {WITH ldap SERVER 'server_name'} | {WITH kerberos [REALM 'realm']} | {WITH ssl_certificate CN 'common_name' | SAN 'TYPE:subject_alt_name'}]
    [[ADD | DROP] HOST {LOCAL | NAME 'name' | REGEXP 'name_regexp' | IP 'address' | LIKE 'pattern'} [,...] | ANY | NONE]
    [VALID UNTIL datetime]
    [DEFAULT ROLE role [,...] | ALL | ALL EXCEPT role [,...] ]
    [GRANTEES {user | role | ANY | NONE} [,...] [EXCEPT {user | role} [,...]]]
    [SETTINGS variable [= value] [MIN [=] min_value] [MAX [=] max_value] [READONLY | WRITABLE] | PROFILE 'profile_name'] [,...]
    """

    __slots__ = (
        "query",
        "if_exists",
        "usernames",
        "on_cluster",
        "not_identified",
        "identification",
        "add_identification",
        "reset_auth_methods_to_new",
        "add_hosts",
        "drop_hosts",
        "valid_until",
        "default_role",
        "all_except_default_role",
        "grantees",
        "settings",
        "_identification",
    )

    def __init__(self):
        super().__init__()
        self.query = "ALTER USER"
        self.if_exists = False
        self.usernames = []
        self.on_cluster = None
        self.not_identified = None
        self.identification = []
        self.add_identification = []
        self.reset_auth_methods_to_new = False
        self.add_hosts = None
        self.drop_hosts = None
        self.valid_until = None
        self.default_role = None
        self.all_except_default_role = None
        self.grantees = None
        self.settings = []
        self._identification = self.identification

    def __repr__(self):
        return (
            "AlterUser("
            f"{super().__repr__()}"
            f"if_exists={self.if_exists}, "
            f"usernames={self.usernames}, "
            f"on_cluster={self.on_cluster}, "
            f"not_identified={self.not_identified}, "
            f"identification={self.identification}, "
            f"add_identification={self.add_identification}, "
            f"reset_auth_methods_to_new={self.reset_auth_methods_to_new}, "
            f"add_hosts={self.add_hosts}, "
            f"drop_hosts={self.drop_hosts}, "
            f"valid_until={self.valid_until}, "
            f"default_role={self.default_role}, "
            f"all_except_default_role={self.all_except_default_role}, "
            f"grantees={self.grantees}, "
            f"settings={self.settings})"
        )

    def set_if_exists(self):
        self.if_exists = True
        self.query += " IF EXISTS"
        return self

    def set_username(self, name, rename_to=None):
        self.usernames.append(Username(name, rename_to))
        user_clause = f" {name}"
        if rename_to:
            user_clause += f" RENAME TO {rename_to}"
        if len(self.usernames) > 1:
            self.query += ","
        self.query += user_clause
        return self

    def set_on_cluster(self, cluster_name):
        self.on_cluster = cluster_name
        self.query += f" ON CLUSTER {cluster_name}"
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

    def set_by_password(self, password):
        self._identification.append(Identification("password", password))
        if len(self._identification) > 1:
            self.query += ","
        self.query += f" BY '{password}'"
        return self

    def set_with_no_password(self):
        self._identification.append(Identification("no_password"))
        return self._set_identification("no_password")

    def set_with_plaintext_password(self, password):
        self._identification.append(Identification("plaintext_password", password))
        return self._set_identification("plaintext_password", password)

    def set_with_sha256_password(self, password):
        self._identification.append(Identification("sha256_password", password))
        return self._set_identification("sha256_password", password)

    def set_with_sha256_hash(self, password):
        hash_value = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self._identification.append(Identification("sha256_hash", password, hash_value))
        return self._set_identification("sha256_hash", hash_value)

    def set_with_sha256_hash_with_salt(self, password, salt):
        salted_password = password.encode("utf-8") + salt.encode("utf-8")
        hash_value = hashlib.sha256(salted_password).hexdigest()
        self._identification.append(
            Identification("sha256_hash_with_salt", password, hash_value, salt=salt)
        )
        return self._set_identification(
            "sha256_hash", hash_value, extra=f" SALT '{salt}'"
        )

    def set_with_double_sha1_password(self, password):
        self._identification.append(Identification("double_sha1_password", password))
        return self._set_identification("double_sha1_password", password)

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

    def set_with_bcrypt_hash(self, password):
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash_value = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
        self._identification.append(Identification("bcrypt_hash", password, hash_value))
        return self._set_identification("bcrypt_hash", hash_value)

    def set_with_ldap_server(self, server_name):
        self._identification.append(
            Identification("ldap_server", server_name=server_name)
        )
        return self._set_identification("ldap SERVER", server_name)

    def set_with_kerberos(self, realm=None):
        self._identification.append(Identification("kerberos", realm=realm))
        return (
            self._set_identification("kerberos REALM", realm)
            if realm
            else self._set_identification("kerberos")
        )

    def set_with_ssl_certificate(self, cn=None, san=None):
        self._identification.append(Identification("ssl_certificate", cn=cn, san=san))
        if cn:
            return self._set_identification("ssl_certificate CN", cn)
        elif san:
            return self._set_identification("ssl_certificate SAN", san)
        return self

    def set_with_ssh_key(self, public_key, key_type):
        self._identification.append(
            Identification("ssh_key", public_key=public_key, key_type=key_type)
        )
        return self._set_identification(f"ssh_key BY KEY {public_key} TYPE", key_type)

    def set_with_http_server(self, server_name, scheme=None):
        self._identification.append(
            Identification("http_server", server_name=server_name, scheme=scheme)
        )
        if scheme:
            return self._set_identification(f"http SERVER {server_name} SCHEME", scheme)
        else:
            return self._set_identification("http SERVER", server_name)

    def set_add_host(self, hosts):
        self.add_hosts = hosts
        self.query += f" ADD HOST {hosts}"
        return self

    def set_drop_host(self, hosts):
        self.drop_hosts = hosts
        self.query += f" DROP HOST {hosts}"
        return self

    def set_valid_until(self, datetime):
        self.valid_until = datetime
        self.query += f" VALID UNTIL {datetime}"
        return self

    def set_default_role(self, roles, all_except_roles=None):
        self.default_role = roles
        self.all_except_default_role = all_except_roles
        self.query += f" DEFAULT ROLE {','.join(roles)}"
        if all_except_roles:
            self.query += f" ALL EXCEPT {','.join(all_except_roles)}"
        return self

    def set_grantees(self, grantees, except_grantees=None):
        self.grantees = Grantees(grantees, except_grantees)
        self.query += f" GRANTEES {','.join(grantees)}"
        if except_grantees:
            self.query += f" EXCEPT {','.join(except_grantees)}"
        return self

    def set_setting(
        self,
        variable,
        value=None,
        min_value=None,
        max_value=None,
        readonly=False,
        writable=False,
        profile=None,
    ):
        self.settings.append(
            Setting(variable, value, min_value, max_value, readonly, writable, profile)
        )
        setting_clause = variable
        if value is not None:
            setting_clause += f" = {value}"
        if min_value is not None:
            setting_clause += f" MIN = {min_value}"
        if max_value is not None:
            setting_clause += f" MAX = {max_value}"
        if readonly:
            setting_clause += " READONLY"
        if writable:
            setting_clause += " WRITABLE"
        if profile:
            setting_clause += f" PROFILE {profile}"
        if len(self.settings) < 2:
            self.query += " SETTINGS"
        if len(self.settings) > 1:
            self.query += ","
        self.query += f" {setting_clause}"
        return self
