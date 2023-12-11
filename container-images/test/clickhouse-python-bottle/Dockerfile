FROM ubuntu:20.04

RUN apt-get update --fix-missing
RUN env DEBIAN_FRONTEND=noninteractive apt-get install --yes\
    python3-pip \
    && rm -rf \
        /var/lib/apt/lists/* \
        /var/cache/debconf \
        /tmp/* \
    && apt-get clean

RUN pip install bottle