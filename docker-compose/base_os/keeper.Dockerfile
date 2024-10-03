ARG KEEPER_DOCKER_IMAGE
FROM $KEEPER_DOCKER_IMAGE

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Fix for 22.x
RUN mkdir -p /var/lib/clickhouse/coordination