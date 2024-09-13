class Query:
    __slots__ = (
        "query",
        "errored",
        "output",
        "exitcode",
        "errorcode",
        "connection_options",
        "session_settings",
    )

    def __init__(self):
        self.query = ""
        self.errored = False
        self.output = None
        self.exitcode = None
        self.errorcode = None
        self.connection_options = None
        self.session_settings = None

    def __str__(self):
        return self.query

    def __repr__(self):
        start = "Query(" if self.__class__.__name__ == "Query" else ""
        end = ")" if self.__class__.__name__ == "Query" else ""
        return (
            f"{start}"
            f"query={repr(self.query)}, "
            f"errored={self.errored}, "
            f"output={self.output}, "
            f"exitcode={self.exitcode}, "
            f"errorcode={self.errorcode}, "
            f"connection_options={self.connection_options}, "
            f"session_settings={self.session_settings}"
            f"{end}"
        )

    def add_connection_options(self, options):
        if options:
            self.connection_options = dict(options)
        return self

    def add_session_settings(self, settings):
        if settings:
            self.session_settings = dict(settings)
        return self

    def add_result(self, r):
        if hasattr(r, "raw_output"):
            self.output = r.raw_output
        else:
            self.output = r.output
        if hasattr(r, "exitcode"):
            self.exitcode = r.exitcode
        if hasattr(r, "errorcode"):
            self.errorcode = r.errorcode
        self.errored = "DB::Exception" in r.output
