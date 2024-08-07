class Query:
    def __init__(self, query=""):
        self._next = []
        if isinstance(query, Query):
            self.query = query.query
        else:
            self.query = query

    def __next__(self):
        return iter(self._next)

    def __call__(self):
        return self

    def __str__(self):
        return self.query

    @property
    def comment(self):
        return Comment(self)


class Comment(Query):
    def __init__(self, query):
        super().__init__(query)

    def __call__(self, comment):
        self.query += f" -- {comment}"
        return self
