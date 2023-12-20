ARG TAG=latest
FROM clickhouse/integration-tests-runner:${TAG}.base

RUN python3 -m pip install --no-cache-dir \
    docker==6.1.3 \
    pytest-reportlog==0.4.0