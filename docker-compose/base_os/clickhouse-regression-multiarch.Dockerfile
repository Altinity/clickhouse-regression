ARG BASE_OS
FROM $BASE_OS

RUN ln -s /usr/bin/clickhouse /usr/bin/clickhouse-keeper

ARG CLICKHOUSE_PACKAGE
COPY $CLICKHOUSE_PACKAGE /tmp/
# Check if it's a deb file
RUN if [ $(echo $CLICKHOUSE_PACKAGE | grep -c ".deb") -eq 1 ]; then \
    apt-get install -y /tmp/*.deb; \
  else \
    cp /tmp/* /usr/bin/; \
    chmod +x /usr/bin/clickhouse; \
  fi \
  && rm -v /tmp/*;
