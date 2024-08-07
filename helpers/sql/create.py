from .query import Query
from .create_user import User


class Create(Query):
    def __init__(self):
        super().__init__()
        self.query = "CREATE"
        self._next.append(partial(getattr, self, "user"))

    @property
    def user(self):
        return User(self)
