FROM clickhouse/clickhouse-keeper:latest

# This directory needs to exist for configs to get merged properly
RUN mkdir -p /var/lib/clickhouse-keeper && \
    chown clickhouse:clickhouse /var/lib/clickhouse-keeper

