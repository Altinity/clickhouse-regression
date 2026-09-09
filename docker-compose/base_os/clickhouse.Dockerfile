ARG CLICKHOUSE_DOCKER_IMAGE_NAME
FROM $CLICKHOUSE_DOCKER_IMAGE_NAME

# UBI images can default to a non-root user; the dnf branch below needs root
# to install packages and to replace /usr/bin symlinks with hard links. This
# is a no-op for Alpine/Ubuntu, which already run as root by default.
USER 0

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Fix for 22.x keeper
RUN mkdir -p /var/lib/clickhouse/coordination

# Install test dependencies. Release images can be Alpine, Debian/Ubuntu, or UBI.
#
# UBI only: functional tests bind compatibility wrapper scripts over the
# /usr/bin command paths, which on UBI are symlinks to /usr/bin/clickhouse.
# Docker follows the symlink and mounts the wrapper over the real multicall
# binary itself, causing infinite self-recursion. Replace them with
# independent hard links (also kept unshadowed under /usr/local/bin) so
# wrapper scripts have a real binary to call instead of recursing into
# themselves. Alpine/Ubuntu images are untouched by this.
RUN if [ -f /etc/alpine-release ]; then \
    apk update && \
    apk add --no-cache curl openssl shadow openssh-client ca-certificates iproute2; \
    elif command -v dnf >/dev/null 2>&1; then \
    dnf install -y openssl openssh-clients ca-certificates iproute procps-ng && \
    dnf clean all && \
    for command in benchmark client compressor extract-from-config git-import local obfuscator server; do \
        ln /usr/bin/clickhouse "/usr/local/bin/clickhouse-${command}"; \
        rm -f "/usr/bin/clickhouse-${command}"; \
        ln /usr/bin/clickhouse "/usr/bin/clickhouse-${command}"; \
    done; \
    else \
    apt-get update -o Acquire::Retries=5 --fix-missing && \
    apt-get install -y --no-install-recommends curl openssh-client iproute2; \
    fi
