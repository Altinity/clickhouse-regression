ARG KEEPER_DOCKER_IMAGE
FROM $KEEPER_DOCKER_IMAGE

ENV TZ=Europe/Berlin

# Fix for 22.x
RUN mkdir -p /var/lib/clickhouse/coordination