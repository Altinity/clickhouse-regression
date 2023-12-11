FROM ubuntu:20.04

RUN apt-get update --fix-missing
RUN apt-get -y upgrade
RUN env DEBIAN_FRONTEND=noninteractive apt-get install --yes\
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
    && rm -rf \
        /var/lib/apt/lists/* \
        /var/cache/debconf \
        /tmp/* \
    && apt-get clean

RUN ARCH=$(uname -i); curl "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}-2.0.30.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN rm -f awscliv2.zip

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update && apt-get install google-cloud-cli

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV DOCKER_CHANNEL stable
ENV DOCKER_VERSION 17.09.1-ce
