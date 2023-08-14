FROM clickhouse/clickhouse-server:22.8.12.45

ARG apt_archive="http://archive.ubuntu.com"
RUN sed -i "s|http://archive.ubuntu.com|$apt_archive|g" /etc/apt/sources.list

RUN apt-get install --yes ca-certificates