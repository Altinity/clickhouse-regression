ARG BASE_OS
FROM ubuntu:20.04 AS glibc-donor

RUN ln -s "$(uname -i)-linux-gnu" /lib/linux-gnu

FROM $BASE_OS

COPY --from=glibc-donor /lib/linux-gnu/libc.so.6 /lib/linux-gnu/libdl.so.2 /lib/linux-gnu/libm.so.6 /lib/linux-gnu/libpthread.so.0 /lib/linux-gnu/librt.so.1 /lib/linux-gnu/libnss_dns.so.2 /lib/linux-gnu/libnss_files.so.2 /lib/linux-gnu/libresolv.so.2 /lib/linux-gnu/ld-2.31.so /lib/
COPY --from=glibc-donor /etc/nsswitch.conf /etc/

RUN case $(arch) in \
    x86_64) mkdir -p /lib64 && ln -sf /lib/ld-2.31.so /lib64/ld-linux-x86-64.so.2 ;; \
    aarch64) ln -sf /lib/ld-2.31.so /lib/ld-linux-aarch64.so.1 ;; \
    esac

# Install dependencies
# bash - tests expect it
# tzdata - for setting timezone
# curl - for testing http api
# openssl - for testing https
# shadow - for useradd
RUN apk add --no-cache ca-certificates bash tzdata curl openssl shadow

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN ln -s /usr/bin/clickhouse /usr/bin/clickhouse-server
RUN ln -s /usr/bin/clickhouse /usr/bin/clickhouse-client
RUN ln -s /usr/bin/clickhouse /usr/bin/clickhouse-keeper

ARG CLICKHOUSE_PACKAGE

# Debugging
RUN echo "CLICKHOUSE_PACKAGE: $CLICKHOUSE_PACKAGE" > /tmp/clickhouse_package
RUN test -n "$CLICKHOUSE_PACKAGE"

ARG CLICKHOUSE_PACKAGE
COPY $CLICKHOUSE_PACKAGE /tmp/
# Check if it's a tgz file
RUN if [ $(echo $CLICKHOUSE_PACKAGE | grep -c ".tgz") -eq 1 ]; then \
    tar xvzf /tmp/*.tgz --strip-components=1 -C / ; \
    rm -v /tmp/*.tgz /install -r; \
  else \
    cp /tmp/* /usr/bin/; \
    chmod +x /usr/bin/clickhouse; \
    rm -v /tmp/*; \
  fi;
