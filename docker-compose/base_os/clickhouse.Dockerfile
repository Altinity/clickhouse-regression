ARG CLICKHOUSE_DOCKER_IMAGE_NAME
FROM $CLICKHOUSE_DOCKER_IMAGE_NAME

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Fix for 22.x keeper
RUN mkdir -p /var/lib/clickhouse/coordination

# install curl, base image could be Alpine or Ubuntu
RUN if [ -f /etc/alpine-release ]; then \
    apk update && \
    apk add --no-cache curl openssl shadow openssh-client ca-certificates; \
    else \
    apt-get update -o Acquire::Retries=5 --fix-missing && \
    apt-get install -y --no-install-recommends curl openssh-client; \
    fi
