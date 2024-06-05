FROM clickhouse/clickhouse-keeper:24.3

# make it easy to swap out config files
RUN ln -s -f /etc/clickhouse-keeper-configs/keeper_config_6node.xml /etc/clickhouse-keeper/keeper_config.xml

CMD ["tail", "-f", "/dev/null"] 