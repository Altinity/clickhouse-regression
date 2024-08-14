from collections import namedtuple

from .query import Query


Username = namedtuple("Username", "name")


class DropUser(Query):
    """
    DROP USER [IF EXISTS] name [,...] [ON CLUSTER cluster_name] [FROM access_storage_type]
    """

    __slots__ = ("if_exists", "on_cluster", "usernames", "access_storage_type")

    def __init__(self):
        super().__init__()
        self.query = "DROP USER"
        self.if_exists = False
        self.on_cluster = None
        self.usernames = []
        self.access_storage_type = None

    def __repr__(self):
        return (
            "DropUser("
            f"{super().__repr__()}"
            f"if_exists={repr(self.if_exists)}, "
            f"on_cluster={self.on_cluster}, "
            f"usernames={self.usernames}, "
            f"access_storage_type={self.access_storage_type})"
        )

    def set_if_exists(self):
        self.if_exists = True
        self.query += " IF EXISTS"
        return self

    def set_username(self, username):
        self.usernames.append(Username(username))
        if len(self.usernames) > 1:
            self.query += ","
        self.query += f" {username}"
        return self

    def set_on_cluster(self, cluster_name):
        self.on_cluster = cluster_name
        self.query += f" ON CLUSTER {cluster_name}"
        return self

    def set_access_storage_type(self, access_storage_type):
        self.access_storage_type = access_storage_type
        self.query += f" FROM {access_storage_type}"
        return self
