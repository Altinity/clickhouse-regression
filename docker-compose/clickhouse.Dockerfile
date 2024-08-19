ARG CLICKHOUSE_DOCKER_IMAGE_NAME
FROM $CLICKHOUSE_DOCKER_IMAGE_NAME

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
