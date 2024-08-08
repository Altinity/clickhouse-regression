from .query import Query
from .alter_user import User


class Alter(Query):
    def __init__(self, query="ALTER"):
        super().__init__(query)

    @property
    def user(self):
        return User(self)
