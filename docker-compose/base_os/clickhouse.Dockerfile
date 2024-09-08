ARG CLICKHOUSE_DOCKER_IMAGE_NAME
FROM $CLICKHOUSE_DOCKER_IMAGE_NAME

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# install curl, base image could be alpine
RUN if [ -f /etc/alpine-release ]; then \
    apk update && \
    apk add --no-cache curl shadow; \
    else \
    apt-get update && \
    apt-get install -y curl; \
    fi
