from .query import Query


class User(Query):
    def __init__(self, query):
        super().__init__(query)
        self.query = query.query + " USER"
        self._next.append((self, "if_not_exists"))
        self._next.append((self, "or_replace"))

    @property
    def if_not_exists(self):
        self.query += " IF NOT EXISTS"
        return UserName(self)

    @property
    def or_replace(self):
        self.query += " OR REPLACE"
        return UserName(self)

    def __call__(self, username):
        return UserName(self)(username)


class IdentifiedWith(Query):
    def __init__(self, query):
        super().__init__(query)
        self.sep = ""
        self.query += " IDENTIFIED WITH"
        self._next.append((self, "no_password"))
        self._next.append((self, "plaintext_password"))
        self._next.append((self, "sha256_password"))
        self._next.append((self, "sha256_hash"))
        self._next.append((self, "sha256_hash_with_salt"))
        self._next.append((self, "double_sha1_password"))
        self._next.append((self, "double_sha1_hash"))
        self._next.append((self, "bcrypt_password"))
        self._next.append((self, "bcrypt_hash"))

    @property
    def no_password(self):
        self.query += f"{self.sep} no_password"
        self.sep = ","
        return self

    @property
    def plaintext_password(self, password):
        self.query += f"{self.sep} plaintext_password BY '{password}'"
        self.sep = ","
        return self

    @property
    def sha256_password(self, password):
        self.query += f"{self.sep} sha256_password BY '{password}'"
        self.sep = ","
        return self

    @property
    def sha256_hash(self, password):
        self.query += f"{self.sep} sha256_hash BY '{password}'"
        self.sep = ","
        return self

    @property
    def sha256_hash_with_salt(self, password, salt):
        self.query += f"{self.sep} sha256_hash BY '{password}' SALT '{salt}'"

    @property
    def double_sha1_password(self, password):
        self.query += f"{self.sep} double_sha1_password BY '{password}'"
        self.sep = ","
        return self

    @property
    def double_sha1_hash(self, password):
        self.query += f"{self.sep} double_sha1_hash BY '{password}'"
        self.sep = ","
        return self

    @property
    def bcrypt_password(self, password):
        self.query += f"{self.sep} bcrypt_password BY '{password}'"
        self.sep = ","
        return self

    @property
    def brcrypt_hash(self, password):
        self.query += f"{self.sep} bcrypt_hash BY '{password}'"
        self.sep = ","
        return self

    def __call__(self, password):
        self.query += f" '{password}'"
        return super().__call__()


class UserName(Query):
    def __init__(self, query):
        super().__init__(query)
        self._next.append((self, "identified_with"))

    @property
    def identified_with(self):
        return IdentifiedWith(self)

    def __call__(self, username):
        self.query += f" {username}"
        return self


class Create(Query):
    def __init__(self):
        super().__init__()
        self.query = "CREATE"
        self._next.append(partial(getattr, self, "user"))

    @property
    def user(self):
        return User(self)


create = (
    Create()
    .user.if_not_exists("vzakaznikov")
    .identified_with("querty")
    .comment("hello")
)
print(create)
