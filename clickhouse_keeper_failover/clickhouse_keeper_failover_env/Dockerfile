FROM clickhouse/clickhouse-keeper:latest

# keeper throws errors if this directory doesn't exist
RUN mkdir -p /var/lib/clickhouse-keeper && \
    chown clickhouse:clickhouse /var/lib/clickhouse-keeper

# make it easy to swap out config files
RUN ln -s -f /etc/clickhouse-keeper-configs/keeper_config.xml /etc/clickhouse-keeper/keeper_config.xml
