ARG CLICKHOUSE_IMAGE=altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest
FROM ${CLICKHOUSE_IMAGE}

COPY runner.sh runner.sh
COPY diff.patch diff.patch

CMD ./runner.sh
