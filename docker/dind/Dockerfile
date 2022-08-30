FROM ubuntu:20.04

RUN apt-get update -y
RUN apt-get install -y apt-utils
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
    iproute2 \
    cgroupfs-mount \
    tzdata \
    libreadline-dev \
    libicu-dev \
    bsdutils \
    curl \
    apt-transport-https \
    expect \
    python3-lxml \
    python3-termcolor \

    && rm -rf \
        /var/lib/apt/lists/* \
        /var/cache/debconf \
        /tmp/* \
    && apt-get clean

RUN apt-get update -y \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:ubuntu-toolchain-r/test \
    && env DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    git \
    python3.8 \
    python3-pip

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install docker-compose docker tzlocal==2.1
RUN pip3 install testflows==1.7.54 pytz boto3 python-dateutil numpy packaging

ENV DOCKER_CHANNEL stable
ENV DOCKER_VERSION 17.09.1-ce

RUN set -eux; \
	if ! wget -O docker.tgz "https://download.docker.com/linux/static/${DOCKER_CHANNEL}/aarch64/docker-${DOCKER_VERSION}.tgz"; then \
		echo >&2 "error: failed to download 'docker-${DOCKER_VERSION}' from '${DOCKER_CHANNEL}' for '${aarch64}'"; \
		exit 1; \
	fi; \
	\
	tar --extract \
		--file docker.tgz \
		--strip-components 1 \
		--directory /usr/local/bin/ \
	; \
	rm docker.tgz

RUN apt-get update && apt-get install -y unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install

COPY dockerd-start.sh /usr/local/bin/
#COPY *.dockerimage /var/lib/docker/

