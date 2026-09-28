ARG CLICKHOUSE_IMAGE=altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest
FROM ${CLICKHOUSE_IMAGE}

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless maven ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY Smoke.java /Smoke.java
COPY runner.sh /runner.sh

ENTRYPOINT ["/bin/bash", "/runner.sh"]
