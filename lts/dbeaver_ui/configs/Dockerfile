# DBeaver CE under a virtual X display, next to the ClickHouse server under
# test. The tests drive DBeaver through xdotool and read it back through the
# AT-SPI accessibility bus (configs/desktop.py).
ARG CLICKHOUSE_IMAGE=altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest
FROM ${CLICKHOUSE_IMAGE}

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        xvfb openbox xdotool wmctrl x11-utils xclip scrot \
        libgtk-3-0 libwebkit2gtk-4.0-37 libxtst6 \
        dbus-x11 at-spi2-core python3-gi gir1.2-atspi-2.0 \
        fonts-dejavu-core curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ARG DBEAVER_VERSION=26.2.1
RUN curl -fsSL --retry 5 -o /tmp/dbeaver.tar.gz \
        "https://github.com/dbeaver/dbeaver/releases/download/${DBEAVER_VERSION}/dbeaver-ce-${DBEAVER_VERSION}-linux-x86_64.tar.gz" \
    && tar -xzf /tmp/dbeaver.tar.gz -C /opt \
    && rm /tmp/dbeaver.tar.gz

COPY start.sh /start.sh
COPY desktop.py /desktop.py
ENTRYPOINT ["/bin/bash", "/start.sh"]
