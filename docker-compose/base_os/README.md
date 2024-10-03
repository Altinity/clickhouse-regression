# Base OS Setup

These files install ClickHouse and test dependencies.

`clickhouse.Dockerfile` and `keeper.Dockerfile` are special, they are used with docker releases of ClickHouse, and thus only install test dependencies.

Adding support for a new distribution is simple, make a copy of the most closely related Dockerfile, name it accordingly, and adjust it as necessary.
