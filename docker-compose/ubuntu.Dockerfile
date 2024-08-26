ARG BASE_OS
FROM $BASE_OS

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN ln -s /usr/bin/clickhouse /usr/bin/clickhouse-keeper

RUN apt-get update
RUN apt-get install -y ca-certificates

ARG CLICKHOUSE_PACKAGE

# Debugging
RUN echo "CLICKHOUSE_PACKAGE: $CLICKHOUSE_PACKAGE" > /tmp/clickhouse_package
RUN test -n "$CLICKHOUSE_PACKAGE"

COPY $CLICKHOUSE_PACKAGE /tmp/clickhouse.deb
RUN apt-get install -y /tmp/clickhouse.deb
RUN rm /tmp/clickhouse.deb