ARG KEEPER_DOCKER_IMAGE
FROM $KEEPER_DOCKER_IMAGE

# Fix for 22.x
RUN mkdir -p /var/lib/clickhouse/coordination