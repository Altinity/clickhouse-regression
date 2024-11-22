ARG BASE_OS=altinityinfra/clickhouse-regression-multiarch:3.0
FROM $BASE_OS

RUN ln -s /usr/bin/clickhouse /usr/bin/clickhouse-keeper

ARG CLICKHOUSE_PACKAGE
COPY $CLICKHOUSE_PACKAGE /tmp/

RUN case "$CLICKHOUSE_PACKAGE" in \
  *.deb) \
    apt-get install -y /tmp/*.deb ;; \
  *.tgz) \
    tar xvzf /tmp/*.tgz --strip-components=1 -C / && \
    rm -v /install -r ;; \
  *) \
    cp /tmp/* /usr/bin/ && \
    chmod +x /usr/bin/clickhouse ;; \
  esac && \
  rm -v /tmp/*