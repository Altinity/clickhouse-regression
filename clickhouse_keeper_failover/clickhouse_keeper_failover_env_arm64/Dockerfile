FROM altinityinfra/clickhouse-regression-multiarch:3.0

RUN ln -s /usr/bin/clickhouse-keeper /usr/bin/clickhouse-keeper-client
RUN ln -s /usr/bin/clickhouse-keeper /usr/bin/clickhouse-keeper-converter

# make it easy to swap out config files
RUN mkdir -p /etc/clickhouse-keeper
RUN ln -s -f /etc/clickhouse-keeper-configs/keeper_config_6node.xml /etc/clickhouse-keeper/keeper_config.xml

CMD ["tail", "-f", "/dev/null"] 