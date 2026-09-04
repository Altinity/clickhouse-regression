ARG CLICKHOUSE_DOCKER_IMAGE_NAME
FROM $CLICKHOUSE_DOCKER_IMAGE_NAME

# Docker images under test can intentionally default to a non-root user. The
# regression wrapper needs root only while adding its own test dependencies and
# creating test directories; docker-compose test services also expect to manage
# their mounted configuration at runtime.
USER 0

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Fix for 22.x keeper
RUN mkdir -p /var/lib/clickhouse/coordination

# Functional tests bind compatibility wrappers over the /usr/bin command
# paths. Replace image symlinks with independent hard links first, otherwise
# Docker follows each destination symlink and mounts the wrapper over the real
# /usr/bin/clickhouse binary. Keep unshadowed links in /usr/local/bin for the
# wrappers to execute without redispatching into themselves.
RUN for command in \
        benchmark client compressor extract-from-config git-import local \
        obfuscator server; do \
        ln /usr/bin/clickhouse "/usr/local/bin/clickhouse-${command}"; \
        rm -f "/usr/bin/clickhouse-${command}"; \
        ln /usr/bin/clickhouse "/usr/bin/clickhouse-${command}"; \
    done

# Install test dependencies. Release images can be Alpine, Debian/Ubuntu, or UBI.
RUN if [ -f /etc/alpine-release ]; then \
    apk update && \
    apk add --no-cache curl openssl shadow openssh-client ca-certificates iproute2; \
    elif command -v dnf >/dev/null 2>&1; then \
    dnf install -y openssl openssh-clients ca-certificates iproute procps-ng && \
    dnf clean all; \
    else \
    apt-get update -o Acquire::Retries=5 --fix-missing && \
    apt-get install -y --no-install-recommends curl openssh-client iproute2; \
    fi
