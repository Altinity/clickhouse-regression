ARG BASE_OS
FROM $BASE_OS

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN ln -s /usr/bin/clickhouse /usr/bin/clickhouse-keeper

RUN apt-get update && apt-get install -y ca-certificates curl openssl

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
