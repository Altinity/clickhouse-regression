class Query:
    __slots__ = ("query", "exception")

    def __init__(self):
        self.query = ""
        self.exception = None

    def __str__(self):
        return self.query
