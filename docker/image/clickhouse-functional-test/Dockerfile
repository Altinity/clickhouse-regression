FROM altinityinfra/clickhouse-regression-multiarch:3.0

ARG odbc_driver_url="https://github.com/ClickHouse/clickhouse-odbc/releases/download/v1.1.4.20200302/clickhouse-odbc-1.1.4-Linux.tar.gz"

RUN apt-get update -y \
    && env DEBIAN_FRONTEND=noninteractive \
        apt-get install --yes --no-install-recommends \
            brotli \
            expect \
            zstd \
            lsof \
            ncdu \
            netcat-openbsd \
            openssl \
            protobuf-compiler \
            python3 \
            python3-lxml \
            python3-requests \
            python3-termcolor \
            python3-pip \
            qemu-user-static \
            sudo \
            # golang version 1.13 on Ubuntu 20 is enough for tests
            golang \
            telnet \
            tree \
            unixodbc \
            wget \
            mysql-client=8.0* \
            postgresql-client \
            sqlite3 \
            awscli \
            rpm2cpio \
            cpio \
            python3-requests \
            llvm-9 \
            rpm2cpio \
            cpio          

RUN pip3 install numpy scipy pandas Jinja2

RUN mkdir -p /tmp/clickhouse-odbc-tmp \
   && wget -nv -O - ${odbc_driver_url} | tar --strip-components=1 -xz -C /tmp/clickhouse-odbc-tmp \
   && cp /tmp/clickhouse-odbc-tmp/lib64/*.so /usr/local/lib/ \
   && odbcinst -i -d -f /tmp/clickhouse-odbc-tmp/share/doc/clickhouse-odbc/config/odbcinst.ini.sample \
   && odbcinst -i -s -l -f /tmp/clickhouse-odbc-tmp/share/doc/clickhouse-odbc/config/odbc.ini.sample \
   && rm -rf /tmp/clickhouse-odbc-tmp

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV NUM_TRIES=1
ENV MAX_RUN_TIME=0

ARG TARGETARCH

RUN mkdir -p /var/lib/clickhouse
COPY ./s3downloader ./s3downloader
RUN ./s3downloader --dataset-names hits visits
