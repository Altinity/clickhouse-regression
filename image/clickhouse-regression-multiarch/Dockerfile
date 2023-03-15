FROM ubuntu:20.04

RUN apt-get update
RUN apt-get -y upgrade
RUN env DEBIAN_FRONTEND=noninteractive apt-get install --yes \
    ca-certificates \
    bash \
    btrfs-progs \
    e2fsprogs \
    iptables \
    xfsprogs \
    tar \
    pigz \
    vim \
    wget \
    git \
    iproute2 \
    cgroupfs-mount \
    python3-pip \
    tzdata \
    libreadline-dev \
    libicu-dev \
    bsdutils \
    liblua5.1-dev \
    luajit \
    libssl-dev \
    libgcc-7-dev \
    apt-transport-https \
    dirmngr \
    gnupg \
    locales \
    curl \
    unzip \
    krb5-kdc \
    krb5-admin-server \
    && rm -rf \
        /var/lib/apt/lists/* \
        /var/cache/debconf \
        /tmp/* \
    && apt-get clean

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.0.30.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN rm -f awscliv2.zip

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install pytz
RUN pip install pytest docker-compose docker dicttoxml kazoo PyMySQL pymongo tzlocal protobuf redis pandas parquet-tools flask
RUN pip install pytest-timeout boto3 minio pyarrow

ENV DOCKER_CHANNEL stable
ENV DOCKER_VERSION 20.10.9

RUN set -eux; ARCH=$(uname -i); \
	if ! wget -O docker.tgz "https://download.docker.com/linux/static/${DOCKER_CHANNEL}/${ARCH}/docker-${DOCKER_VERSION}.tgz"; then \
		echo >&2 "error: failed to download 'docker-${DOCKER_VERSION}' from '${DOCKER_CHANNEL}' for '${ARCH}'"; \
		exit 1; \
	fi; \
	\
	tar --extract \
		--file docker.tgz \
		--strip-components 1 \
		--directory /usr/local/bin/ \
	; \
	rm docker.tgz


RUN mkdir -p /etc/apt/sources.list.d \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv E0C56BD4 \
    && apt-get update

RUN apt install -y postgresql postgresql-contrib \
    && rm -rf \
        /var/lib/apt/lists/* \
        /var/cache/debconf \
        /tmp/* \
    && apt-get clean

COPY dockerd-start.sh /usr/local/bin/
COPY *.dockerimage /var/lib/docker/
