import bcrypt
import hashlib

from collections import namedtuple

from .query import Query

User = namedtuple("User", ["name", "cluster"])
Identification = namedtuple(
    "Identification",
    [
        "method",
        "password",
        "hash_value",
        "salt",
        "server_name",
        "realm",
        "cn",
        "san",
        "public_key",
        "key_type",
        "scheme",
    ],
    defaults=[
        None,
    ]
    * 10,
)
Setting = namedtuple(
    "Setting",
    ["variable", "value", "min_value", "max_value", "readonly", "writable", "profile"],
    defaults=[
        None,
    ]
    * 6,
)


class CreateUser(Query):
    """
    CREATE USER [IF NOT EXISTS | OR REPLACE] name1 [ON CLUSTER cluster_name1]
        [, name2 [ON CLUSTER cluster_name2] ...]
    [NOT IDENTIFIED | IDENTIFIED {[WITH {no_password | plaintext_password | sha256_password | sha256_hash | double_sha1_password | double_sha1_hash}] BY {'password' | 'hash'}} | {WITH ldap SERVER 'server_name'} | {WITH kerberos [REALM 'realm']} | {WITH ssl_certificate CN 'common_name' | SAN 'TYPE:subject_alt_name'} | {WITH ssh_key BY KEY 'public_key' TYPE 'ssh-rsa|...'} | {WITH http SERVER 'server_name' [SCHEME 'Basic']}]
    [HOST {LOCAL | NAME 'name' | REGEXP 'name_regexp' | IP 'address' | LIKE 'pattern'} [,...] | ANY | NONE]
    [VALID UNTIL datetime]
    [IN access_storage_type]
    [DEFAULT ROLE role [,...]]
    [DEFAULT DATABASE database | NONE]
    [GRANTEES {user | role | ANY | NONE} [,...] [EXCEPT {user | role} [,...]]]
    [SETTINGS variable [= value] [MIN [=] min_value] [MAX [=] max_value] [READONLY | WRITABLE] | PROFILE 'profile_name'] [,...]
    """
    def __init__(self):
        super().__init__()
        self.query = "CREATE USER"
        self.if_not_exists_flag = False
        self.or_replace_flag = False
        self.users = []
        self.not_identified_flag = None
        self.identification = []
        self.hosts = None
        self.valid_until = None
        self.access_storage_type = None
        self.default_role = None
        self.default_database = None
        self.grantees = None
        self.except_grantees = None
        self.settings = []

    def __str__(self):
        return self.query

    def __repr__(self):
        return f"CreateUser(query={repr(self.query)}, if_not_exists_flag={self.if_not_exists_flag}, or_replace_flag={self.or_replace_flag}, users={self.users}, not_identified_flag={self.not_identified_flag}, identification={self.identification}, hosts={self.hosts}, valid_until={self.valid_until}, access_storage_type={self.access_storage_type}, default_role={self.default_role}, default_database={self.default_database}, grantees={self.grantees}, except_grantees={self.except_grantees}, settings={self.settings})"

    def if_not_exists(self):
        self.if_not_exists_flag = True
        self.query += " IF NOT EXISTS"
        return self

    def or_replace(self):
        self.or_replace_flag = True
        self.query += " OR REPLACE"
        return self

    def user(self, name, cluster_name=None):
        self.users.append(User(name, cluster_name))
        user_clause = f" {name}"
        if cluster_name:
            user_clause += f" ON CLUSTER {cluster_name}"
        if len(self.users) > 1:
            self.query += ","
        self.query += user_clause
        return self

    def identified(self):
        if len(self.identification) < 2:
            self.query += " IDENTIFIED"
        return self

    def _set_identification(self, method, value=None, extra=None):
        if len(self.identification) > 1:
            self.query += ","
        if value:
            self.query += f" WITH {method} BY '{value}'"
        else:
            self.query += f" WITH {method}"
        if extra:
            self.query += f" {extra}"
        return self

    def not_identified(self):
        self.not_identified_flag = True
        self.query += " NOT IDENTIFIED"

    def by_password(self, password):
        self.identification.append(Identification("password", password))
        if len(self.identification) < 2:
            self.query += " BY"
        if len(self.identification) > 1:
            self.query += ","
        self.query += f" '{password}'"

    def with_no_password(self):
        self.identification.append(Identification("no_password"))
        return self._set_identification("no_password")

    def with_plaintext_password(self, password):
        self.identification.append(Identification("plaintext_password", password))
        return self._set_identification("plaintext_password", password)

    def with_sha256_password(self, password):
        self.identification.append(Identification("sha256_password", password))
        return self._set_identification("sha256_password", password)

    def with_sha256_hash(self, password):
        hash_value = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.identification.append(Identification("sha256_hash", password, hash_value))
        return self._set_identification("sha256_hash", hash_value)

    def with_sha256_hash_with_salt(self, password, salt):
        salted_password = password.encode("utf-8") + salt.encode("utf-8")
        hash_value = hashlib.sha256(salted_password).hexdigest()
        self.identification.append(
            Identification("sha256_hash_with_salt", password, hash_value, salt=salt)
        )
        return self._set_identification(
            "sha256_hash", hash_value, extra=f" SALT '{salt}'"
        )

    def with_double_sha1_password(self, password):
        self.identification.append(Identification("double_sha1_password", password))
        return self._set_identification("double_sha1_password", password)

    def with_double_sha1_hash(self, password):
        hash_value = hash_value = hashlib.sha1(
            hashlib.sha1(password.encode("utf-8")).digest()
        ).hexdigest()
        self.identification.append(
            Identification("double_sha1_hash", password, hash_value)
        )
        return self._set_identification("double_sha1_hash", hash_value)

    def with_bcrypt_password(self, password):
        self.identification.append(Identification("bcrypt_password", password))
        return self._set_identification("bcrypt_password", password)

    def with_bcrypt_hash(self, password):
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash_value = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
        self.identification.append(Identification("bcrypt_hash", password, hash_value))
        return self._set_identification("bcrypt_hash", hash_value)

    def with_ldap_server(self, server_name):
        self.identification.append(
            Identification("ldap_server", server_name=server_name)
        )
        return self._set_identification("ldap SERVER", server_name)

    def with_kerberos(self, realm=None):
        self.identification.append(Identification("kerberos", realm=realm))
        return (
            self._set_identification("kerberos REALM", realm)
            if realm
            else self._set_identification("kerberos")
        )

    def with_ssl_certificate(self, cn=None, san=None):
        self.identification.append(Identification("ssl_certificate", cn=cn, san=san))
        if cn:
            return self._set_identification("ssl_certificate CN", cn)
        elif san:
            return self._set_identification("ssl_certificate SAN", san)
        return self

    def with_ssh_key(self, public_key, key_type):
        self.identification.append(
            Identification("ssh_key", public_key=public_key, key_type=key_type)
        )
        return self._set_identification(f"ssh_key BY KEY {public_key} TYPE", key_type)

    def with_http_server(self, server_name, scheme=None):
        self.identification.append(
            Identification("http_server", server_name=server_name, scheme=scheme)
        )
        if scheme:
            return self._set_identification(f"http SERVER {server_name} SCHEME", scheme)
        else:
            return self._set_identification("http SERVER", server_name)

    def host(self, hosts):
        self.hosts = hosts
        self.query += f" HOST {hosts}"
        return self

    def valid_until(self, datetime):
        self.valid_until = datetime
        self.query += f" VALID UNTIL {datetime}"
        return self

    def in_access_storage_type(self, access_storage_type):
        self.access_storage_type = access_storage_type
        self.query += f" IN {access_storage_type}"
        return self

    def default_role(self, roles):
        self.default_role = roles
        self.query += f" DEFAULT ROLE {','.join(roles)}"
        return self

    def default_database(self, database):
        self.default_database = database
        self.query += f" DEFAULT DATABASE {database}"
        return self

    def grantees(self, grantees, except_grantees=None):
        self.grantees = grantees
        self.except_grantees = except_grantees
        self.query += f" GRANTEES {','.join(grantees)}"
        if except_grantees:
            self.query += f" EXCEPT {','.join(except_grantees)}"
        return self

    def setting(
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