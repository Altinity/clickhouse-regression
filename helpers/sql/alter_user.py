from .query import Query
from .create_user import IdentifiedWith


class User(Query):
    def __init__(self, query):
        super().__init__(query)
        self.query = query.query + " USER"

    def __call__(self, username):
        self.query += f" {username}"
        return AlterUser(self)


class ResetAuthenticationMethodsToNew(Query):
    def __init__(self, query):
        super().__init__(query)
        self.query = query.query + " RESET AUTHENTICATION METHODS TO NEW"


class Add(Query):
    def __init__(self, query):
        super().__init__(query)
        self.query = query.query + " ADD"
        self._next.append((self, "identified_with"))

    @property
    def identified_with(self):
        return IdentifiedWith(self)


class AlterUser(Query):
    def __init__(self, query):
        super().__init__(query)
        self._next.append((self, "reset_authentication_methods_to_new"))
        self._next.append((self, "identified_with"))
        self._next.append((self, "add"))

    @property
    def reset_authentication_methods_to_new(self):
        return ResetAuthenticationMethodsToNew(self)

    @property
    def identified_with(self):
        return IdentifiedWith(self)

    @property
    def add(self):
        return Add(self)
