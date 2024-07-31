FROM altinityinfra/clickhouse-regression-multiarch:2.0

RUN ln -s /usr/bin/clickhouse-keeper /usr/bin/clickhouse-keeper-client
RUN ln -s /usr/bin/clickhouse-keeper /usr/bin/clickhouse-keeper-converter

# Fix for 22.x
RUN mkdir -p /var/lib/clickhouse/coordination

ENTRYPOINT [ "/usr/bin/clickhouse-keeper", \
    "--config-file=/etc/clickhouse-keeper/keeper_config.xml", \
    "--log-file=/var/log/clickhouse-keeper/clickhouse-keeper.log", \
    "--errorlog-file=/var/log/clickhouse-keeper/clickhouse-keeper.err.log", \
    "--pidfile=/tmp/clickhouse-keeper.pid"]
