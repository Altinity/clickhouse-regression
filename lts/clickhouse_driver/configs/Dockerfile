ARG CLICKHOUSE_IMAGE=altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest
FROM ${CLICKHOUSE_IMAGE}

# The clickhouse-driver tests expect the server and client in this timezone.
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        git ca-certificates python3 python3-pip python3-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# GitHub refuses git protocol v2 from Ubuntu 22.04's git 2.34 ("could not
# read Username for 'https://github.com'") and serves protocol v0.
RUN git config --system protocol.version 0

COPY patches /patches
COPY runner.sh /runner.sh

ENTRYPOINT ["/bin/bash", "/runner.sh"]
