ARG BASE_OS
FROM $BASE_OS

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN ln -s /usr/bin/clickhouse /usr/bin/clickhouse-keeper

RUN dnf update -y
RUN dnf install -y ca-certificates procps

ARG CLICKHOUSE_PACKAGE

# Debugging
RUN echo "CLICKHOUSE_PACKAGE: $CLICKHOUSE_PACKAGE" > /tmp/clickhouse_package
RUN test -n "$CLICKHOUSE_PACKAGE"

COPY $CLICKHOUSE_PACKAGE /tmp/clickhouse.rpm
RUN dnf install -y /tmp/clickhouse.rpm
RUN rm /tmp/clickhouse.rpm