import bcrypt
import hashlib
from testflows.core import current

from collections import namedtuple, defaultdict

from .query import Query

Username = namedtuple(
    "Username",
    ["name"],
    defaults=[
        None,
    ],
)
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
    defaults=[None, None, None, None, None, None, None, None, None, None],
)
Grantees = namedtuple(
    "Grantees",
    ["grantees", "except_grantees"],
    defaults=[
        None,
    ],
)
Setting = namedtuple(
    "Setting",
    ["variable", "value", "min_value", "max_value", "readonly", "writable", "profile"],
    defaults=[None, None, None, None, None, None],
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

    __slots__ = (
        "if_not_exists",
        "or_replace",
        "usernames",
        "on_cluster",
        "not_identified",
        "identification",
        "hosts",
        "valid_until",
        "access_storage_type",
        "default_role",
        "default_database",
        "grantees",
        "settings",
    )

    def __init__(self):
        super().__init__()
        self.query = "CREATE USER"
        self.if_not_exists = False
        self.or_replace = False
        self.usernames: list[Username] = []
        self.on_cluster = None
        self.not_identified = None
        self.identification = defaultdict(list)
        self.hosts = None
        self.valid_until = None
        self.access_storage_type = None
        self.default_role = None
        self.default_database = None
        self.grantees = None
        self.settings = []

    def __repr__(self):
        return (
            "CreateUser("
            f"{super().__repr__()}"
            f"if_not_exists={self.if_not_exists}, "
            f"or_replace={self.or_replace}, "
            f"usernames={self.usernames}, "
            f"on_cluster={self.on_cluster}, "
            f"not_identified={self.not_identified}, "
            f"identification={dict(self.identification)}, "
            f"hosts={self.hosts}, "
            f"valid_until={self.valid_until}, "
            f"access_storage_type={self.access_storage_type}, "
            f"default_role={self.default_role}, "
            f"default_database={self.default_database}, "
            f"grantees={self.grantees}, "
            f"settings={self.settings})"
        )

    def set_if_not_exists(self):
        self.if_not_exists = True
        self.query += " IF NOT EXISTS"
        return self

    def set_or_replace(self):
        self.or_replace = True
        self.query += " OR REPLACE"
        return self

    def set_username(self, name):
        self.usernames.append(Username(name))
        user_clause = f" {name}"
        if len(self.usernames) > 1:
            self.query += ","
        self.query += user_clause
        return self

    def set_on_cluster(self, cluster_name):
        self.on_cluster = cluster_name
        self.query += f" ON CLUSTER {cluster_name}"
        return self

    def set_identified(self):
        if len(self.identification) < 2:
            self.query += " IDENTIFIED"
        return self

    def _set_identification(self, method, value=None, extra=None, node=None):
        if len(self.identification[node]) > 1:
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

    def set_by_password(self, password, node=None, on_cluster=None):
        if on_cluster:
            for node in current().context.nodes:
                self.identification[node].append(Identification("password", password))
        else:
            self.identification[node].append(Identification("password", password))

        if len(self.identification[node]) > 1:
            self.query += ","
        self.query += f" BY '{password}'"
        return self

    def set_with_no_password(self, node=None, on_cluster=None):
        if on_cluster:
            for node in current().context.nodes:
                self.identification[node].append(Identification("no_password"))
        else:
            self.identification[node].append(Identification("no_password"))
        return self._set_identification("no_password", node=node)

    def set_with_plaintext_password(self, password, node=None, on_cluster=None):
        if on_cluster:
            for node in current().context.nodes:
                self.identification[node].append(
                    Identification("plaintext_password", password)
                )
        else:
            self.identification[node].append(
                Identification("plaintext_password", password)
            )
        return self._set_identification("plaintext_password", password, node=node)

    def set_with_sha256_password(self, password, node=None, on_cluster=None):
        if on_cluster:
            for node in current().context.nodes:
                self.identification[node].append(
                    Identification("sha256_password", password)
                )
        else:
            self.identification[node].append(
                Identification("sha256_password", password)
            )
        return self._set_identification("sha256_password", password, node=node)

    def set_with_sha256_hash(self, password, node=None, on_cluster=None):
        hash_value = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if on_cluster:
            for node in current().context.nodes:
                self.identification[node].append(
                    Identification("sha256_hash", password, hash_value)
                )
        else:
            self.identification[node].append(
                Identification("sha256_hash", password, hash_value)
            )
        return self._set_identification("sha256_hash", hash_value, node=node)

    def set_with_sha256_hash_with_salt(
        self, password, salt, node=None, on_cluster=None
    ):
        salted_password = password.encode("utf-8") + salt.encode("utf-8")
        hash_value = hashlib.sha256(salted_password).hexdigest()
        if on_cluster:
            for node in current().context.nodes:
                self.identification[node].append(
                    Identification(
                        "sha256_hash_with_salt", password, hash_value, salt=salt
                    )
                )
        else:
            self.identification[node].append(
                Identification("sha256_hash_with_salt", password, hash_value, salt=salt)
            )
        return self._set_identification(
            "sha256_hash", hash_value, extra=f" SALT '{salt}'", node=node
        )

    def set_with_double_sha1_password(self, password, node=None, on_cluster=None):
        if on_cluster:
            for node in current().context.nodes:
                self.identification[node].append(
                    Identification("double_sha1_password", password)
                )
        else:
            self.identification[node].append(
                Identification("double_sha1_password", password)
            )
        return self._set_identification("double_sha1_password", password, node=node)

    def set_with_double_sha1_hash(self, password, node=None, on_cluster=None):
        hash_value = hashlib.sha1(
            hashlib.sha1(password.encode("utf-8")).digest()
        ).hexdigest()
        if on_cluster:
            for node in current().context.nodes:
                self.identification[node].append(
                    Identification("double_sha1_hash", password, hash_value)
                )
        else:
            self.identification[node].append(
                Identification("double_sha1_hash", password, hash_value)
            )
        return self._set_identification("double_sha1_hash", hash_value, node=node)

    def set_with_bcrypt_password(self, password, node=None, on_cluster=None):
        if on_cluster:
            for node in current().context.nodes:
                self.identification[node].append(
                    Identification("bcrypt_password", password)
                )
        else:
            self.identification[node].append(
                Identification("bcrypt_password", password)
            )
        return self._set_identification("bcrypt_password", password, node=node)

    def set_with_bcrypt_hash(self, password, node=None, on_cluster=None):
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash_value = (
            bcrypt.hashpw(password_bytes, salt).decode("utf-8").replace("$", "\$")
        )
        if on_cluster:
            for node in current().context.nodes:
                self.identification[node].append(
                    Identification("bcrypt_hash", password, hash_value)
                )
        else:
            self.identification[node].append(
                Identification("bcrypt_hash", password, hash_value)
            )
        return self._set_identification("bcrypt_hash", hash_value, node=node)

    def set_with_ldap_server(self, server_name):
        self.identification.append(
            Identification("ldap_server", server_name=server_name)
        )
        return self._set_identification("ldap SERVER", server_name)

    def set_with_kerberos(self, realm=None):
        self.identification.append(Identification("kerberos", realm=realm))
        return (
            self._set_identification("kerberos REALM", realm)
            if realm
            else self._set_identification("kerberos")
        )

    def set_with_ssl_certificate(self, cn=None, san=None):
        self.identification.append(Identification("ssl_certificate", cn=cn, san=san))
        if cn:
            return self._set_identification("ssl_certificate CN", cn)
        elif san:
            return self._set_identification("ssl_certificate SAN", san)
        return self

    def set_with_ssh_key(self, public_key, key_type):
        self.identification.append(
            Identification("ssh_key", public_key=public_key, key_type=key_type)
        )
        return self._set_identification(f"ssh_key BY KEY {public_key} TYPE", key_type)

    def set_with_http_server(self, server_name, scheme=None):
        self.identification.append(
            Identification("http_server", server_name=server_name, scheme=scheme)
        )
        if scheme:
            return self._set_identification(f"http SERVER {server_name} SCHEME", scheme)
        else:
            return self._set_identification("http SERVER", server_name)

    def set_host(self, hosts):
        self.hosts = hosts
        self.query += f" HOST {hosts}"
        return self

    def set_valid_until(self, datetime):
        self.valid_until = datetime
        self.query += f" VALID UNTIL {datetime}"
        return self

    def set_in_access_storage_type(self, access_storage_type):
        self.access_storage_type = access_storage_type
        self.query += f" IN {access_storage_type}"
        return self

    def set_default_role(self, roles):
        self.default_role = roles
        self.query += f" DEFAULT ROLE {','.join(roles)}"
        return self

    def set_default_database(self, database):
        self.default_database = database
        self.query += f" DEFAULT DATABASE {database}"
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
